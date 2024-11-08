from flask import Flask, render_template, request, jsonify
import os
import subprocess
import json
from dotenv import load_dotenv
import psutil

load_dotenv()

user = os.getenv("USER")
password = os.getenv("PASSWORD")

app = Flask(__name__)

# Load server configurations from a JSON file
SERVERS_FILE = "servers.json"
PID_FOLDER = "pid"

if not os.path.exists(PID_FOLDER):
    os.makedirs(PID_FOLDER)

def load_servers():
    try:
        if os.path.exists(SERVERS_FILE):
            with open(SERVERS_FILE, "r") as file:
                return json.load(file)
    except Exception as e:
        print(f"Error loading servers: {e}")
    return []

def save_servers(servers):
    try:
        with open(SERVERS_FILE, "w") as file:
            json.dump(servers, file, indent=4)
    except Exception as e:
        print(f"Error saving servers: {e}")

def get_server_status(server):
    pid_file = os.path.join(PID_FOLDER, f"{server['name']}.pid")
    if os.path.exists(pid_file):
        try:
            with open(pid_file, "r") as file:
                pid = int(file.read().strip())
                if psutil.pid_exists(pid):
                    return "running"
        except Exception as e:
            print(f"Error reading PID file: {e}")
    return "stopped"

@app.route("/")
def index():
    servers = load_servers()
    for server in servers:
        server["status"] = get_server_status(server)
    return render_template("index.html", servers=servers)

@app.route("/start", methods=["POST"])
def start_server():
    data = request.json
    servers = load_servers()
    server = next((s for s in servers if s["name"] == data.get("name")), None)
    if server:
        start_info = server.get("start_info")
        file_name = start_info.get("file_name")
        directory = start_info.get("directory")
        if file_name and directory:
            start_command = os.path.join(directory, file_name)
            try:
                process = subprocess.Popen(['psexec.exe', '-u', user, '-p', password, start_command], shell=True) # using psexec to run command as admin
                pid_file = os.path.join(PID_FOLDER, f"{server['name']}.pid")
                with open(pid_file, "w") as file:
                    file.write(str(process.pid))
                return jsonify({"status": "success", "message": f"Started: {server['name']}"})
            except Exception as e:
                return jsonify({"status": "error", "message": f"Failed to start server: {e}"})
    return jsonify({"status": "error", "message": "Server not found"})

@app.route("/stop", methods=["POST"])
def stop_server():
    data = request.json
    servers = load_servers()
    server = next((s for s in servers if s["name"] == data.get("name")), None)
    if server:
        pid_file = os.path.join(PID_FOLDER, f"{server['name']}.pid")
        if os.path.exists(pid_file):
            try:
                with open(pid_file, "r") as file:
                    pid = int(file.read().strip())
                    if psutil.pid_exists(pid):
                        process = psutil.Process(pid)
                        for child in process.children(recursive=True):
                            child.terminate()
                        process.terminate()
                        return jsonify({"status": "success", "message": f"Stopped: {server['name']}"})
            except Exception as e:
                return jsonify({"status": "error", "message": f"Failed to stop server: {e}"})
    return jsonify({"status": "error", "message": "Server not running or PID file not found"})

@app.route("/edit", methods=["POST"])
def edit_server():
    data = request.json
    servers = load_servers()
    server = next((s for s in servers if s["name"] == data.get("name")), None)
    if server:
        newName = data.get("newName")
        newStartInfo = data.get("newStart_info")
        if newName:
            server["name"] = newName
        if newStartInfo:
            server["start_info"] = newStartInfo
        save_servers(servers)
        return jsonify({"status": "success", "message": "Server updated"})
    return jsonify({"status": "error", "message": "Server not found"})

@app.route("/add", methods=["POST"])
def add_server():
    data = request.json
    servers = load_servers()
    servers.append(data)
    save_servers(servers)
    return jsonify({"status": "success", "message": "Server added"})

@app.route("/remove", methods=["POST"])
def remove_server():
    data = request.json
    servers = load_servers()
    servers = [s for s in servers if s["name"] != data.get("name")]
    save_servers(servers)
    pid_file = os.path.join(PID_FOLDER, f"{data.get('name')}.pid")
    if os.path.exists(pid_file):
        try:
            os.remove(pid_file)
        except Exception as e:
            return jsonify({"status": "error", "message": f"Failed to remove PID file: {e}"})
    return jsonify({"status": "success", "message": "Server removed"})

@app.route("/servers", methods=["GET"])
def get_servers():
    servers = load_servers()
    for server in servers:
        server["status"] = get_server_status(server)
    return jsonify(servers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9231, debug=True)
