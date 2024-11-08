# Server Controller

Server Controller is a web-based application that allows you to manage multiple servers from a single control panel. You can start, stop, add, edit, and remove servers using a user-friendly interface.

## Features

- Start and stop servers
- Add new servers
- Edit existing servers
- Remove servers
- View server status (running, starting, stopped)

## Prerequisites

- Python 3.x
- Flask
- psutil
- psexec (for running commands as admin)
- dotenv

## Installation

1. Clone the repository:

```sh
git clone https://github.com/yourusername/server-controller.git
cd server-controller
```

2. Install the required Python packages:

```sh
pip install -r requirements.txt
```

3. Create a .env file in the project root directory and add your user and password:
```python
USER=your_username
PASSWORD=your_password
```

## Usage
1. Run the flask application:
```sh
python app.py
```

2. Open your web browser and go to http://localhost:9231.

3. Use the control panel to manage your servers.

## License
This project is licensed under the MIT License. See the LICENSE file for details.