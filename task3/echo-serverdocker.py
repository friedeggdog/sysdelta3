#!/bin/python3
import socket,os,sys,threading,re
from Cryptodome.Cipher import AES
import mysql.connector

HOST = socket.gethostbyname(socket.gethostname())
PORT = 65432
ADDR = (HOST, PORT)
STANDARD = 'utf-8'
key = b"1qaz2wsx3edc4rfv"
nonce = b"2wsx4rfv6yhn8ik,"

try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR) 
except Exception as e:
    print(f"An error has occurred:{e}, Exiting ...")
    sys.exit(1)

def client_handle(conn, addr):
    try:
        cipher = AES.new(key, AES.MODE_EAX, nonce)
        username = conn.recv(1024).decode(STANDARD)
        passw = conn.recv(1024)
        passw = cipher.decrypt(passw).decode(STANDARD)
        mydb = mysql.connector.connect(host="172.25.0.1",user="root",password="1234")
        mycursor = mydb.cursor()
        mycursor.execute("USE users")
        mycursor.execute(f"Select * from uandp where Username='{username}' and Pass='{passw}'")
        result = len(mycursor.fetchall())
        if result > 0:
            if not os.path.isdir(f"/home/files/{username}"): #if user doesnt have a directory to store his files create one
                os.makedirs(f"/home/files/{username}")
            conn.send("Connected to server".encode(STANDARD))
        else:
            conn.send("Login Failed".encode(STANDARD))
    except:
        result = 0

    try:
        while result>0:

            cipher = AES.new(key, AES.MODE_EAX, nonce)

            action = ''
            while True:
                if action[-3:] == '<!>':
                    break
                else:
                    action = action + conn.recv(1024).decode(STANDARD)       
            action = action[:-3]
            action = action.split('<|>')
            cmd = action[0]

            if cmd == 'Logout':
                break
            elif cmd == 'Upload':
                file_name = action[1]
                file_zip = action[2]
                file_zip = file_zip[2:-1].encode().decode('unicode_escape').encode("raw_unicode_escape")
                defile_zip = cipher.decrypt(file_zip)

                with open(f"/home/files/{username}/{file_name}.zip", "wb") as f:
                    f.write(defile_zip)

                conn.send(f"File uploaded as {file_name}.zip".encode(STANDARD))
            elif cmd == 'Delete':
                file_name = action[1]
                
                if os.path.isfile(f"/home/files/{username}/{file_name}"):
                    os.remove(f"/home/files/{username}/{file_name}")
                    conn.send(f"File {file_name} removed successfully".encode(STANDARD))
                else:
                    conn.send(f"File {file_name} does not exist".encode(STANDARD))
            elif cmd == "Search":
                regex = action[1]
                list_files = os.listdir(f"/home/files/{username}/")
                match = ''
                for i in list_files:
                    if re.search(f"{regex}", i):
                        match = match + '\n' + i
                conn.send(f"The list of files matching the given expression is {match}".encode(STANDARD))
            elif cmd == "Load":
                name = action[1]
                with open(f"/home/files/{username}/{name}", "rb") as f:
                    content = f.read()
                encontent = cipher.encrypt(content)
                conn.send(f"{encontent}<!>".encode(STANDARD))
                if conn.recv(1024).decode(STANDARD) == 'done':
                    conn.send(f"File received as From_{name[0:-4]}".encode(STANDARD))
            elif cmd == "Fold_Upload":
                fold_name = action[1]
                fold_zip = action[2]
                fold_zip = fold_zip[2:-1].encode().decode('unicode_escape').encode("raw_unicode_escape")
                defold_zip = cipher.decrypt(fold_zip)
                with open(f"/home/files/{username}/{fold_name}.zip", "wb") as f:
                    f.write(defold_zip)

                conn.send(f"Folder uploaded as {fold_name}.zip".encode(STANDARD))
            elif cmd == "Fold_Load":
                name = action[1]
                with open(f"/home/files/{username}/{name}", "rb") as f:
                    content = f.read()
                encontent = cipher.encrypt(content)
                conn.send(f"{encontent}<!>".encode(STANDARD))
                if conn.recv(1024).decode(STANDARD) == 'done': #if done is recieved send response message
                    conn.send(f"Folder received as From_{name[0:-4]}".encode(STANDARD))
            else:
                conn.send(f"!!Invalid command!!\nUpload <filepath>\nLoad <name>\nFold_Upload <folderpath>\nFold_Load <name>\nSearch <regex>\nDelete <name>\nLogout".encode(STANDARD))
    except Exception as e:
        print(f"An error has occurred:{e}, Disconnecting ...")
        conn.send(f"A server side error has occurred, Exiting ...".encode(STANDARD))
    print(f'Closing:{addr}')
    conn.close()

def start():
    server.listen()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=client_handle, args=(conn, addr))
        thread.start()
        print("No of connections:",threading.active_count()-1)


print("Starting Server...")
print(HOST)
start()