#!/usr/bin/env python3
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import paramiko
import os
import logging
from dotenv import load_dotenv
import psycopg2 as p
import socket

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)
ssh_sessions = {}
# Configure logging
logging.basicConfig(level=logging.DEBUG)

# SSH Configuration for session cleaning
HOST = os.getenv("Controller_IP")
USERNAME = os.getenv("Username")
PASSWORD = os.getenv("Password")
SSHPORT = os.getenv("SshPort")

DBPORT = os.getenv("DBport")
DBNAME = os.getenv("DBname")
DBUSER = os.getenv("DBuser")
DBPASSWORD = os.getenv("DBpassword")
DBIP= os.getenv("DBIP")

PDUpassword = os.getenv("PDUpass")
CONTROLLERpassword = os.getenv("CONTROLLERpass")



#--------Controller clear logic----------
def start_ssh_command(session_id, command):
    """Open an interactive shell, send the command, and read until a (y/n) prompt."""
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            HOST,
            port=SSHPORT,
            username=USERNAME,
            password=PASSWORD,
            compress=True,
            look_for_keys=False,
            allow_agent=False
        )
        # Disable Nagle's algorithm for lower latency
        transport = client.get_transport()
        sock = transport.sock
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        channel = transport.open_session()
        channel.get_pty()       # Allocate a PTY so the remote will prompt interactively
        channel.invoke_shell()  # Start the shell
        channel.send(command + "\n")

        buffer = ""
        # Read until the prompt appears
        while True:
            if channel.recv_ready():
                chunk = channel.recv(1024).decode(errors='ignore')
                buffer += chunk
                if "(y/n)" in buffer.lower():
                    break
        # Store for confirmation step
        ssh_sessions[session_id] = (client, channel)
        return buffer, None
    except Exception as e:
        return None, str(e)


def confirm_ssh_command(session_id, confirmation):
    """Send confirmation ('y' or 'n') to the open shell and read final output."""
    if session_id not in ssh_sessions:
        return None, f"No active session for ID {session_id}"

    try:
        client, channel = ssh_sessions.pop(session_id)
        channel.send(confirmation.strip().lower() + "\n")

        final_output = ""
        # Read until the process ends
        while not channel.exit_status_ready():
            if channel.recv_ready():
                final_output += channel.recv(1024).decode(errors='ignore')

        client.close()
        return final_output, None
    except Exception as e:
        return None, str(e)

# ----- Flask Routes -----
@app.route('/run-clean-session', methods=['POST'])
def run_clean_session():
    session_id = request.json.get('session_id')
    if not session_id:
        return jsonify(error="Missing session_id"), 400

    cmd = f"/opt/Nubi/utils.sh -cleanSessionId {session_id}"
    output, error = start_ssh_command(session_id, cmd)
    if error:
        return jsonify(error=error), 500
    return jsonify(output=output, need_confirmation=True)


@app.route('/run-reset-session', methods=['POST'])
def run_reset_session():
    session_id = request.json.get('session_id')
    if not session_id:
        return jsonify(error="Missing session_id"), 400

    cmd = f"/opt/Nubi/utils.sh -resetSessionId {session_id}"
    output, error = start_ssh_command(session_id, cmd)
    if error:
        return jsonify(error=error), 500
    return jsonify(output=output, need_confirmation=True)


@app.route('/confirm-session', methods=['POST'])
def confirm_session():
    session_id = request.json.get('session_id')
    confirmation = request.json.get('confirmation')
    if not session_id or confirmation not in ('y', 'n'):
        return jsonify(error="Missing session_id or invalid confirmation"), 400

    output, error = confirm_ssh_command(session_id, confirmation)
    if error:
        return jsonify(error=error), 500
    return jsonify(output=output, status="done")

# ------------ Database Endpoints ------------
def get_data():
    conn = p.connect(
    dbname=DBNAME,
    user=DBUSER,  #postgress user
    password=DBPASSWORD, #postgres password
    host=DBIP,       #Database IP, need to be allow the source IP and MD5 auth
    port=DBPORT
)
    cur = conn.cursor()
    cur.execute("SELECT * FROM ipaddr ORDER BY pdu_number;")
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    data = [dict(zip(colnames, row)) for row in rows]
    cur.close()
    conn.close()
    return data

@app.route('/data', methods=['GET'])
def sent_data():
    return jsonify(get_data())

@app.route('/api/PDUauthentication')
def getAuthUsers():
    conn = p.connect(
    dbname=DBNAME,
    user=DBUSER,  #postgress user
    password=DBPASSWORD, #postgres password
    host=DBIP,       #Database IP, need to be allow the source IP and MD5 auth
    port=DBPORT
    ) 
    cur = conn.cursor()
    cur.execute("SELECT username FROM authusers;")
    authUsers = cur.fetchall()
    print(authUsers)
    return jsonify({"authUsers":authUsers, "PDUpass":PDUpassword})

@app.route('/api/Controllerauthentication')
def getControllerhUsers():
    conn = p.connect(
    dbname=DBNAME,
    user=DBUSER,  #postgress user
    password=DBPASSWORD, #postgres password
    host=DBIP,       #Database IP, need to be allow the source IP and MD5 auth
    port=DBPORT
    ) 
    cur = conn.cursor()
    cur.execute("SELECT username FROM Controllerauthusers;")
    authUsers = cur.fetchall()
    print(authUsers)
    return jsonify({"authUsers":authUsers, "Controllerpass":CONTROLLERpassword})



@app.route('/update', methods=['POST'])
def update_data():
    data = request.get_json()
    conn = p.connect(
    dbname=DBNAME,
    user=DBUSER,  #postgress user
    password=DBPASSWORD, #postgres password
    host=DBIP,       #Database IP, need to be allow the source IP and MD5 auth
    port=DBPORT
    )
    cur = conn.cursor()
    cur.execute(
        "UPDATE ipaddr SET ipaddress=%s WHERE pduname=%s",
        (data.get('ipaddress'), data.get('pduname'))
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'Data updated successfully'})

# ------------ Template Routes ------------
@app.route('/')
def main_page():
    return render_template('main.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/monthlyreport')
def monthly_report():
    return render_template('monthlyreport.html')

@app.route('/pdu')
def pdu_page():
    return render_template('pdu.html')

@app.route('/controler')
def controler_page():
    return render_template('controler.html')

# Error Handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
