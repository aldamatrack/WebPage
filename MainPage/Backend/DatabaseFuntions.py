import psycopg2 as p


def CreateNewDB():
    conn = p.connect(
    dbname="pduips",
    user="postgres",  #postgress user
    password="postgres", #postgres password
    host="192.168.1.102",       #Database IP, need to be allow the source IP and MD5 auth
    port="5432"
)
    cur = conn.cursor()
    # Create table with pdu_number
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ipaddr (
        pdu_number SERIAL PRIMARY KEY,
        PDUname VARCHAR(50) UNIQUE NOT NULL,
        ipaddress VARCHAR(50) UNIQUE NOT NULL,
        datacenter VARCHAR(50),
        owner VARCHAR(50),
        description VARCHAR(50),
        status VARCHAR(50)
    );""")
    print('''TABLE PDU IP created''')

    query = "INSERT INTO ipaddr (ipaddress, PDUname, datacenter, owner, description, status) VALUES (%s, %s, %s, %s, %s, %s);"
    with open('ips.txt', 'r') as ip:
        for element in ip:
            data1 = element.strip().split(',')
            print(data1)
            cur.execute(query, (data1[0], data1[1], data1[2], data1[3], data1[4], data1[5]))
        conn.commit()
        ip.close()

def DeleteTableData():
    conn = p.connect(
    dbname="pduips",
    user="postgres",  #postgress user
    password="postgres", #postgres password
    host="192.168.1.102",       #Database IP, need to be allow the source IP and MD5 auth
    port="5432"
)
    cur = conn.cursor()
    cur.execute("DELETE FROM ipaddr;")
    conn.commit()

def DeleteTable():
    conn = p.connect(
    dbname="pduips",
    user="postgres",  #postgress user
    password="postgres", #postgres password
    host="192.168.1.102",       #Database IP, need to be allow the source IP and MD5 auth
    port="5432"
)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS ipaddr;")
    conn.commit()

DeleteTable()
CreateNewDB()
