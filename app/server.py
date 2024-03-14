import socket
import threading
import json


class Client:
    def __init__(self, master, conn, address):
        self.master = master
        self.conn = conn
        self.address = address
        self.running = False

    def send(self, data):
        self.conn.send(data.encode())

    def recieve(self):
        data = self.conn.recv(1024).decode()
        """
        Data format:
        
        message = {
            "flag": "chat_history" | "general_message",
            "type": "single" | "multi",
            "from": user_name,
            "to": ["all" | user_name | user_name1, user_name1],
            "content": content 
        }
        """
        message = json.loads(data)
        return message


    def onstart(self):
        for message in self.master.msg_history:
            self.send(
                {
                    "flag":                     
                }
            )


    def onstop(self):
        ...

    def execute(self):
        ...

class Server:
    def __init__(self, port, host):
        self.port = port
        self.host = host

        self.socket = socket.socket()
        self.socket.bind((self.port, self.host))

        self.clients = []
        self.msg_history = []

    def save_msg_history():
        with open("msg_history.json", "a+") as f:
            data = json.load(f)
            data.extend(self.msg_history)
            json.dump(data)

    def load_msg_history():
        with open("msg_history.json", "r") as f:
            msg_history = json.load(f)
            
    
    def run():
        while True:
            print("Listening...")
            server_socket.listen(1)
            conn, address = server_socket.accept()

            new_client = Client(self, conn, address)
            self.clients.append(Client)
            new_client.onstart()
            
            new_thread = threading.Thread(target=client_connection, args=[conn,])
            new_thread.start()


def client_connection(conn):
    while True:
	data = conn.recv(1024).decode()
	if not data:
	    break
	print("Message from user: " + str(data))
	conn.send(data.encode())
    conn.close()


def server_program():
    PORT = 7013
    SERVER = "0.0.0.0"
    ADDR = (SERVER, PORT)

    server_socket = socket.socket()
    server_socket.bind(ADDR)
    
    while True:
        print("Listening...")
        server_socket.listen(1)
        conn, address = server_socket.accept()
            
        new_thread = threading.Thread(target=client_connection, args=[conn,])
        new_thread.start()
        print("Connection from: " + str(address))
		
	
if __name__ == '__main__':
    server_program()
	
	
