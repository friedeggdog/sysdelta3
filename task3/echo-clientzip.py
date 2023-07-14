#!/bin/python3  
import socket,os,pathlib,io,zipfile,sys
from Crypto.Cipher import AES

HOST = "172.25.0.2"
PORT = 65432
STANDARD = 'utf-8'
key = b"1qaz2wsx3edc4rfv"
nonce = b"2wsx4rfv6yhn8ik,"

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as e:
    print(f"Error creating socket:{e}, Exiting ...")
    sys.exit(1)

try:
    client.connect((HOST,PORT))
except socket.gaierror as e:
    print(f"Address-related error connecting to server:{e}, Exiting ...")
    sys.exit(1)
except socket.error as e:
    print(f"Error connecting:{e}, Exiting ...")
    sys.exit(1)

def main():
    try:
        cipher = AES.new(key, AES.MODE_EAX, nonce)
        username = input("Enter Username>>>")
        client.sendall(username.encode(STANDARD))
        password = input("Enter Password>>>")
        password = cipher.encrypt(password.encode(STANDARD))
        client.sendall(password)
        if len(username) == 0 or len(password) == 0:
            raise Exception("Fields Empty")
        while True:

            cipher = AES.new(key, AES.MODE_EAX, nonce)

            msg = client.recv(1024).decode(STANDARD)
            print(msg)
            if msg == 'A server side error has occurred, Exiting ...' or msg == 'Login Failed': #stop the thread if these messages are sent from server
                break
            exp = input("Enter command>>>")
            exp = exp.split(' ')
            cmd = exp[0]

            if cmd == 'Logout':
                client.send(f"{cmd}<!>".encode(STANDARD))
                break
            elif cmd == 'Upload':
                archive = io.BytesIO()
                file_path = exp[1]
                file_name = os.path.basename(file_path)

                if os.path.isdir(file_path) or not os.path.exists(file_path):
                    raise Exception("File does not exist or is Folder")

                with zipfile.ZipFile(archive,'w') as zip_archive:
                    zip_archive.write(file_path, compress_type=zipfile.ZIP_DEFLATED, arcname=file_name)

                text = archive.getvalue()
                entext = cipher.encrypt(text)
                archive.close()
                reply = f"{cmd}<|>{file_name}<|>{entext}<!>".encode(STANDARD)
                client.send(reply)
            elif cmd == "Delete":
                file_name = exp[1]
                client.send(f"{cmd}<|>{file_name}<!>".encode(STANDARD))
            elif cmd == "Search":
                regex = exp[1]
                client.send(f"{cmd}<|>{regex}<!>".encode(STANDARD))
            elif cmd == "Load":
                name =  exp[1]
                client.send(f"{cmd}<|>{name}<!>".encode(STANDARD))
                
                text = ''
                while True:
                    if text[-3:] == '<!>': #keep recieving data till <!> is reached 
                        client.send(f"done".encode(STANDARD))
                        break
                    elif text == 'A server side error has occurred, Exiting ...':
                        raise Exception()
                    else:
                        text = text + client.recv(1024).decode(STANDARD)

                text = text[2:-4].encode().decode('unicode_escape').encode("raw_unicode_escape") #converts string of bytes to actual bytes
                detext = cipher.decrypt(text)
                with zipfile.ZipFile(io.BytesIO(detext), mode="r") as z:
                    if len(z.infolist()) > 1: #if the zipfile contains more than one file exit
                        raise Exception("Not a File")
                    with open(f"/home/{os.getlogin()}/From_{name[:-4]}", "w") as f:
                        f.write(z.read(z.infolist()[0]).decode())

            elif cmd == "Fold_Upload":
                archive = io.BytesIO()
                fold_path = exp[1]
                if not os.path.exists(fold_path) or os.path.isfile(fold_path):
                    raise Exception("Folder does not exist or is File")

                if len(os.path.basename(fold_path)) == 0: ##to make the name come properly
                    fold_name = os.path.basename(fold_path[:-1])
                else:
                    fold_name = os.path.basename(fold_path)
                fold_path = pathlib.Path(fold_path)

                with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zip_archive: 
                    for fpath in fold_path.rglob("*"):
                        zip_archive.write(fpath, arcname=fpath.relative_to(fold_path))
                
                text = archive.getvalue()
                entext = cipher.encrypt(text)
                archive.close()
                reply = f"{cmd}<|>{fold_name}<|>{entext}<!>".encode(STANDARD)
                client.send(reply)
            elif cmd == "Fold_Load":
                name =  exp[1]
                client.send(f"{cmd}<|>{name}<!>".encode(STANDARD))

                text = ''
                while True:
                    if text[-3:] == '<!>':
                        client.send(f"done".encode(STANDARD))
                        break
                    elif text == 'A server side error has occurred, Exiting ...':
                        raise Exception()
                    else:
                        text = text + client.recv(1024).decode(STANDARD)

                text = text[2:-4].encode().decode('unicode_escape').encode("raw_unicode_escape")
                detext = cipher.decrypt(text)
                with zipfile.ZipFile(io.BytesIO(detext), mode="r") as z:
                    for file in z.namelist():
                            z.extract(file, f'From_{name[0:-4]}')
            else:
                client.send(f"{cmd}<!>".encode(STANDARD))
    except (Exception, KeyboardInterrupt) as e:
        print(f"An error has occurred:{e}, Disconnecting ...")
        client.send(f"Logout<!>".encode(STANDARD))


    print("Disconnected")
    client.close() 

main()