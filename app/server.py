import socket
import threading 

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
	
	
