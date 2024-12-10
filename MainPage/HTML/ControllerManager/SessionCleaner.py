import psycopg2 as p
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Function to get data from the database
def GetData():
    conn = p.connect("dbname=ipaddress user=postgres password=root")
    cur = conn.cursor()
    cur.execute("SELECT * FROM ipaddr ORDER BY pdu_number;")
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    data = [dict(zip(colnames, row)) for row in rows]
    cur.close()
    conn.close()
    return data



# Send data to the frontend
@app.route("/data", methods=["GET"])
def sentComand():
    

    return jsonify(GetData())

# Update data in the database
@app.route("/update", methods=["POST"])
def sent_command():
    data = request.get_json()
    
    return jsonify({'message': 'Data updated successfully'})

if __name__ == '__main__':
    app.run(debug=True)




def ControllerComman():
    print("backend test")

