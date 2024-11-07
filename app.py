from flask import Flask, render_template, request, jsonify
import os
import subprocess
import json

app = Flask(__name__)

# Load server configurations from a JSON file
SERVERS_FILE = "servers.json"

def load_servers():
    if os.path.exists(SERVERS_FILE):
        with open(SERVERS_FILE, "r") as file:
            return json.load(file)
    print("path doesnt exist")
    return []

def save_servers(servers):
    with open(SERVERS_FILE, "w") as file:
        json.dump(servers, file, indent=4)

@app.route("/")
def index():
    servers = load_servers()
    return render_template("index.html", servers=servers)

@app.route("/start", methods=["POST"])
def start_server():
    data = request.json
    servers = load_servers()
    server = next((s for s in servers if s["name"] == data.get("name")), None)
    start_info = server.get("start_info")
    file_name = start_info.get("file_name")
    directory = start_info.get("directory")
    if file_name and directory:
        start_command = f"start {directory}\\{file_name}"  # Command to start the server
        start_command = start_command.replace("/", "\\")  # Replace forward slashes with backslashes
        print(start_command)
        subprocess.Popen(start_command, cwd=directory, shell=True)  # Execute the command to start the server in its directory
        return jsonify({"status": "success", "message": f"Started: {file_name}"})
    return jsonify({"status": "error", "message": "No command provided"})

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
    return jsonify({"status": "success", "message": "Server removed"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9231, debug=True)
