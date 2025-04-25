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




def start_ssh_command(session_id, command):
    """Starts an SSH command that expects interactive confirmation."""
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, port=SSHPORT, username=USERNAME, password=PASSWORD)

        stdin, stdout, stderr = client.exec_command(command)

        output = ""
        while not stdout.channel.recv_ready():
            pass  # wait for output

        while stdout.channel.recv_ready():
            output += stdout.channel.recv(1024).decode()

        # Store session for later confirmation
        ssh_sessions[session_id] = {
            'stdin': stdin,
            'stdout': stdout,
            'stderr': stderr,
            'client': client
        }

        return output.strip(), None
    except Exception as e:
        return None, str(e)


def confirm_ssh_command(session_id, confirmation):
    """Sends confirmation to an open SSH session."""
    if session_id not in ssh_sessions:
        return None, f"No active SSH session found for session_id: {session_id}"

    try:
        session = ssh_sessions.pop(session_id)  
        stdin = session['stdin']
        stdout = session['stdout']
        client = session['client']

        stdin.write(confirmation + '\n')
        stdin.flush()

        final_output = ""
        while not stdout.channel.exit_status_ready():
            while stdout.channel.recv_ready():
                final_output += stdout.channel.recv(1024).decode()

        client.close()
        return final_output.strip(), None
    except Exception as e:
        return None, str(e)


@app.route('/run-clean-session', methods=['POST'])
def run_clean_session():
    session_id = request.json.get('session_id')
    if not session_id:
        return jsonify({'error': 'Missing session_id'}), 400

    command = f"/opt/Nubi/utils.sh -cleanSessionId {session_id}"
    output, error = start_ssh_command(session_id, command)

    if error:
        return jsonify({'error': error}), 500

    return jsonify({
        'output': output,
        'message': 'Confirmation required'
    })


@app.route('/run-reset-session', methods=['POST'])
def run_reset_session():
    session_id = request.json.get('session_id')
    if not session_id:
        return jsonify({'error': 'Missing session_id'}), 400

    command = f"/opt/Nubi/utils.sh -resetSessionId {session_id}"
    output, error = start_ssh_command(session_id, command)

    if error:
        return jsonify({'error': error}), 500

    return jsonify({
        'output': output,
        'message': 'Confirmation required'
    })


@app.route('/confirm-session', methods=['POST'])
def confirm_session():
    session_id = request.json.get('session_id')
    confirmation = request.json.get('confirmation')

    if not session_id or not confirmation:
        return jsonify({'error': 'Missing session_id or confirmation'}), 400

    output, error = confirm_ssh_command(session_id, confirmation)

    if error:
        return jsonify({'error': error}), 500

    return jsonify({
        'result': output,
        'status': 'Command completed'
    })
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
