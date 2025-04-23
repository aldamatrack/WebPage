from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import paramiko
import os
import logging
from dotenv import load_dotenv
import psycopg2 as p

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# SSH Configuration for session cleaning
HOST = os.getenv("Controller_IP")
USERNAME = os.getenv("Username")
PASSWORD = os.getenv("Password")
PORT = 22

def execute_ssh_command(command):
    """Execute an SSH command and return output, error, and status code."""
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, port=PORT, username=USERNAME, password=PASSWORD)
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        client.close()
        return output, error, 0 if not error else 1
    except Exception as e:
        app.logger.error(f"SSH Error: {str(e)}")
        return "", str(e), 1

# ------------ Session Cleaner Endpoints ------------
@app.route('/run-clean-session', methods=['POST'])
def run_clean_session():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    session_id = request.json.get('session_id')
    if not session_id:
        return jsonify({'error': 'Missing session_id'}), 400
    output, error, code = execute_ssh_command(f"/opt/Nubi/utils.sh -cleanSessionId {session_id}")
    return jsonify({'output': output, 'error': error, 'returncode': code})

@app.route('/run-reset-session', methods=['POST'])
def run_reset_session():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    session_id = request.json.get('session_id')
    if not session_id:
        return jsonify({'error': 'Missing session_id'}), 400
    output, error, code = execute_ssh_command(f"/opt/Nubi/utils.sh -resetSessionId {session_id}")
    return jsonify({'output': output, 'error': error, 'returncode': code})

# ------------ Database Endpoints ------------
def get_data():
    conn = p.connect("dbname=ipaddress user=postgres password=root")
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

@app.route('/update', methods=['POST'])
def update_data():
    data = request.get_json()
    conn = p.connect("dbname=ipaddress user=postgres password=root")
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
