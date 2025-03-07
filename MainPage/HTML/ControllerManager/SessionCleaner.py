from flask import Flask, request, jsonify
from flask_cors import CORS
import paramiko
import os
import logging
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

# Configuración SSH
HOST = os.getenv("Controller_IP")
USERNAME = os.getenv("Username")
PASSWORD = os.getenv("Password")
PORT = 22

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

def execute_ssh_command(command):
    """Ejecuta comandos SSH genéricos con manejo de errores"""
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

@app.errorhandler(404)
def not_found(e):
    return jsonify(error="Endpoint not found"), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify(error="Internal server error"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)