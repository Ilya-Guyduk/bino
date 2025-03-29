# B!NO

![screenshot](docs/Снимок%20экрана%202025-03-26%20214345.png)

**B!NO** is a simple Python application for executing local scripts on remote hosts via SSH. It provides an easy-to-use interface for managing connections and running scripts without manual SSH access.

## Features
- **Run Scripts Remotely**: Execute Bash or Python scripts on remote servers.
- **Manage Endpoints**: Save multiple SSH connections for quick access.
- **Real-time Output**: View script execution results in real-time.
- **User-Friendly UI**: Simple and minimalistic interface for quick script execution.

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/bino.git
   cd bino
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the application:
   ```sh
   python main.py
   ```

## Usage
1. **Add a Connection**:
   - Define a new SSH endpoint with hostname, port, login, and password.
2. **Write or Load a Script**:
   - Enter a Bash or Python script in the editor.
3. **Select an Endpoint**:
   - Choose a saved SSH connection.
4. **Execute the Script**:
   - Click "Run" and see the output in real-time.

## License
This project is open-source and available under the GPL3 License.

---

_Developed with ❤️ by ILya Guyduk_

