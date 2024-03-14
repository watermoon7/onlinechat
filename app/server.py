import socket
import threading
import json
import time
import utils

"""
- The server is responsible for sending and receiving messages
- Needs Python 3.11 (doesn't work on 3.12 but probably does work on older versions)


Message format:

message = {
    "flag": "chat_history" | "general_message",
    "from": user_name,
    "to": "all" | user_name,
    "content": content 
}
"""

class Client:

    def __init__(self, master, conn, address):
        self.master = master
        self.conn = conn
        self.address = address
        self.running = True

        # temporary
        self.name = self.address


    def onstart(self):
        utils.send(self.conn, self.address)
        for message in self.master.msg_history:
            if message["to"] in ["all", self.address]:
                data = (
                    json.dumps({
                        "flag": "chat_history",
                        "from": message["from"],
                        "to": message["to"],
                        "content": message["content"]
                    })
                )
                utils.send(self.conn, data.encode("utf-8"))

        # indicates the end of the chat history
        utils.send(self.conn, "END")

    def onstop(self):
        self.running = False
        time.sleep(0.5)
        try:
            self.conn.close()
            self.master.clients.remove(self)
        except Exception as e:
            print("Client disconnected: " + str(e))


    def execute(self):
        while self.running:
            data = utils.receive(self.conn)
            if not data:
                break
            try:
                msg = json.loads(data)
                self.master.msg_history.append(msg)
                print(f"{msg['from']} > {msg['content']}")
                for client in self.master.clients:
                    if client != self:
                        if msg["to"] in ["all", client.address]:
                            utils.send(client.conn, json.dumps(msg))
            except Exception as e:
                print(e)

        print("::User disconnected::")
        self.onstop()



class Server:

    def __init__(self, port, host):
        self.port = port
        self.host = host

        self.socket = socket.socket()
        self.socket.bind((self.host, self.port))

        self.clients = []
        self.msg_history = []


    def save_msg_history(self):
        with open("msg_history.json", "a+") as f:
            data = json.load(f)
            data.extend(self.msg_history)
            json.dump(data, f)


    def load_msg_history(self):
        with open("msg_history.json", "r") as f:
            self.msg_history = json.load(f)


    def listen(self):
        print("[SERVER STARTED]")
        while True:
            self.socket.listen(1)
            conn, address = self.socket.accept()
            print("=------------------------------------------=")
            print("<> New connection from: " + str(address) + " <>")
            print("=------------------------------------------=")

            new_client = Client(self, conn, address)
            self.clients.append(new_client)
            new_client.onstart()
            
            new_thread = threading.Thread(target=new_client.execute)
            new_thread.start()


    def server_interface(self):
        while True:
            msg = input()
            if msg == "stop":
                for client in self.clients:
                    utils.send(client.conn, "KICKED")
                    client.onstop()
            elif msg in ["commands", "help"]:
                print("Available commands:")
                print("stop, info, msglist, list, connected, help, commands, kick")
            elif msg == "info":
                print("Server Stats:")
                print(f"    Port:{self.port}")
                print(f"    IP:{self.host}")
                print(f"    Socket:{self.socket}")
                print(f"    Connections:{len(self.clients)}")
                print(f"    Num Messages:{len(self.msg_history)}")
            elif msg == "msglist":
                print("/---------------\\")
                for msg in self.msg_history:
                    print(f"{msg['from']} > {msg['content']}")
                print("\\---------------/")
            elif msg in ["list", "connected"]:
                for client in self.clients:
                    print(client.name)
            elif msg.split()[0] == "kick":
                for client in self.clients:
                    if str(msg.split(maxsplit=1)[-1].strip()) == str(client.name):
                        utils.send(client.conn, "KICKED")
                        client.onstop()
            else:
                message = {
                    "flag": "general_message",
                    "from": "SERVER",
                    "to": "all",
                    "content": msg
                }
                for client in self.clients:
                    utils.send(client.conn, json.dumps(message))
                self.msg_history.append(message)



if __name__ == '__main__':
    server = Server(
        port=7015,
        host="0.0.0.0"
    )
    thread1 = threading.Thread(target=server.listen)
    thread2 = threading.Thread(target=server.server_interface)
    thread1.start()
    thread2.start()

