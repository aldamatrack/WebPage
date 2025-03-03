from flask import Flask, request, jsonify
import paramiko
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Configure the SSH connection to the CentOS VM
HOST = os.getenv("Controller_IP")
USERNAME = os.getenv("Username")
PASSWORD = os.getenv("Password")
PORT = 22



def execute_clean_session(session_id):
    """
    Executes the clean session command on the remote CentOS VM using SSH.
    """
    command = f"/opt/Nubi/utils.sh -cleanSessionId {session_id}"
    try:
        # Create an SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the remote server
        client.connect(HOST, port=PORT, username=USERNAME, password=PASSWORD)

        # Execute the command
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()

        # Close the connection
        client.close()

        return output, error, 0 if not error else 1

    except Exception as e:
        return "", str(e), 1

def execute_reset_session(session_id):
    """
    Executes the reset session command on the remote CentOS VM using SSH.
    """
    command = f"/opt/Nubi/utils.sh -resetSessionId {session_id}"
    try:
        # Create an SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the remote server
        client.connect(HOST, port=PORT, username=USERNAME, password=PASSWORD)

        # Execute the command
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()

        # Close the connection
        client.close()

        return output, error, 0 if not error else 1

    except Exception as e:
        return "", str(e), 1

@app.route('/run-clean-session', methods=['POST'])
def run_clean_session():
    try:
        # Get the session ID from the request
        session_id = request.json.get('session_id')
        if not session_id:
            return jsonify({'error': 'No session ID provided'}), 400

        # Execute the clean session command on the CentOS VM
        output, error, returncode = execute_clean_session(session_id)

        return jsonify({
            'output': output,
            'error': error,
            'returncode': returncode
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/run-reset-session', methods=['POST'])
def run_reset_session():
    try:
        # Get the session ID from the request
        session_id = request.json.get('session_id')
        if not session_id:
            return jsonify({'error': 'No session ID provided'}), 400

        # Execute the reset session command on the CentOS VM
        output, error, returncode = execute_reset_session(session_id)

        return jsonify({
            'output': output,
            'error': error,
            'returncode': returncode
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
