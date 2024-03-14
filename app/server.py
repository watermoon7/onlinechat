import socket
import threading
import json

class Client:
	def __init__(self, conn, address):
		self.conn = conn
		self.address = address

	def send(self, data):
		self.conn.send(data.encode())

	def handle_incoming_traffic(self):
		data = self.conn.recv(1024).decode()
		"""
		Message format:
		
		message = {
			"type": "general_message" | "chat_history",
			"from": user_name,
			"to": ["all" | user_name | user_name1, user_name1],
			"content": content 
		}
		"""
		message = json.loads(data)


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
	
	
