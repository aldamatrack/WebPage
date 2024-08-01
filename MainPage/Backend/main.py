import psycopg2 as p

def CreateNewDB():
    conn = p.connect("dbname=ipaddress user=postgres password=root")

    cur = conn.cursor()
    query = "INSERT INTO ipaddr VALUES(%s, %s, %s);"


    cur.execute("CREATE TABLE IF NOT EXISTS ipaddr( ipaddress VARCHAR(50) UNIQUE NOT NULL PRIMARY KEY, PDUname VARCHAR(50) UNIQUE NOT NULL, datacenter VARCHAR(50))")
    print('''TABLE PDU IP created''')

    with open('ips.txt', 'r') as ip:
        for element in ip:
            data = element.strip().split(',')
            cur.execute(query, (data[0], data[1], "RTP"))
        conn.commit()
        ip.close()

    

def DeleteTable():
    conn = p.connect("dbname=ipaddress user=postgres password=root")

    cur = conn.cursor()
    cur.execute("DELETE FROM ipaddr;")
    conn.commit()

CreateNewDB()