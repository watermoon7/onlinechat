import socket
import struct
import customtkinter
import json
import threading
import utils


def change_theme(new_theme: str):
    customtkinter.set_appearance_mode(new_theme)

def change_font_size(new_scaling: str):
    new_scaling_float = int(new_scaling.replace("%", "")) / 100 * 1.2
    customtkinter.set_widget_scaling(new_scaling_float)


class OptionsMenu(customtkinter.CTkFrame):

    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.options_label = customtkinter.CTkLabel(self, text="Options", anchor="w")
        self.options_label.grid(row=0, column=0)

        self.connect_button = customtkinter.CTkButton(self, text="Connect", command=self.master.connect)
        self.connect_button.grid(row=1, column=0, padx=10, pady=10)

        self.disconnect_button = customtkinter.CTkButton(self, text="Disconnect", command=self.master.disconnect)
        self.disconnect_button.grid(row=2, column=0, padx=10, pady=10)

        self.reset_socket = customtkinter.CTkButton(self, text="Refresh Connection", command=self.master.refresh_connection)
        self.reset_socket.grid(row=3, column=0, padx=10, pady=10)
        

        

        self.ui_label = customtkinter.CTkLabel(self, text="UI", anchor="w")
        self.ui_label.grid(row=4, column=0)

        self.theme_menu = customtkinter.CTkOptionMenu(self, values=["Light", "Dark", "System"], command=change_theme)
        self.theme_menu.grid(row=5, column=0, padx=10, pady=10)
        self.theme_menu.set("Dark")
        
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self, values=[str(i*10) + '%' for i in range(1, 21)], command=change_font_size)
        self.scaling_optionemenu.grid(row=6, column=0, padx=10, pady=10)
        self.scaling_optionemenu.set("100%")
        change_font_size("100%")


        self.advanced_options_label = customtkinter.CTkLabel(self, text="Advanced Options", anchor="w")
        self.advanced_options_label.grid(row=7, column=0)
        
        
        self.reset_socket = customtkinter.CTkButton(self, text="Reset Socket", command=self.master.reset_socket)
        self.reset_socket.grid(row=8, column=0)

        #self.port_label = customtkinter.CTkLabel(self, text="Port:", anchor="w")
        #self.port_label.grid(row=8, column=0)
        self.port_entry = customtkinter.CTkEntry(self)
        self.port_entry.grid(row=9, column=0, padx=10, pady=10)
        self.port_entry.insert(0, str(self.master.port))
        self.port_button = customtkinter.CTkButton(self, text="Set Port", command=self.master.set_port)
        self.port_button.grid(row=10, column=0, padx=10, pady=10)

        #self.ip_label = customtkinter.CTkLabel(self, text="IP:", anchor="w")
        #self.ip_label.grid(row=11, column=0)
        self.ip_entry = customtkinter.CTkEntry(self)
        self.ip_entry.grid(row=11, column=0, padx=10, pady=10)
        self.ip_entry.insert(0, str(self.master.host))
        self.ip_button = customtkinter.CTkButton(self, text="Set IP", command=self.master.set_host)
        self.ip_button.grid(row=12, column=0, padx=10, pady=10)


class ChatBox(customtkinter.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.input_box = customtkinter.CTkEntry(self)
        self.input_box.grid(column=0, row=1, padx=10, pady=10, sticky="nesw")

        self.console = customtkinter.CTkTextbox(self)
        self.console.grid(column=0, row=0, padx=10, pady=10, sticky="nesw")
        self.console.configure(state=customtkinter.DISABLED)


    def clear_text_box(self, *args):
        self.console.configure(state=customtkinter.NORMAL)
        self.console.delete("0.0", customtkinter.END)
        self.console.configure(state=customtkinter.DISABLED)


    def set_console_text(self, text):
        self.clear_text_box()
        self.console.configure(state=customtkinter.NORMAL)
        self.console.insert("0.0", text)
        self.console.configure(state=customtkinter.DISABLED)


    def clear_input_box(self, *args):
        self.input_box.delete(0, customtkinter.END)


    def pop_input_box(self, *args):
        text = self.input_box.get()
        self.clear_input_box()
        return text



class App(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        #self.host = "86.25.143.94"  # wills IP address (keep secrit) (use when server is running on different network)
        #self.host = "192.168.0.112" # use this when running the server on the same network
        self.host = "127.0.0.1"
        self.port = 7014
        self.connected = False
        self.msg_list = []
        self.address = None

        self.client_socket = socket.socket()
        self.client_socket.settimeout(3) # times out after 3 seconds of trying to connect

        self.title("effCorentin")
        self.geometry("1080x720")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.chat_box = ChatBox(self)
        self.chat_box.grid(row=0, column=0, padx=10, pady=20, sticky="nesw")
        self.chat_box.set_console_text("Not Connected To Server")

        self.options_menu = OptionsMenu(self)
        self.options_menu.grid(row=0, column=1, padx=10, pady=20, sticky="nesw")

        self.bind("<Return>", self.send_message)
        self.protocol("WM_DELETE_WINDOW", self.on_close)


    def update_chat_box(self):
        self.chat_box.set_console_text(
            "\n".join(
                [f"{i['from']} > {i['content']}" for i in self.msg_list]
            )
        )


    def reset_socket(self):
        if not self.connected:
            self.client_socket = socket.socket()


    def set_port(self):
        if not self.connected:
            new_port = self.options_menu.port_entry.get()
            if utils.is_valid_port(str(new_port)):
                self.port = int(new_port)
            else:
                self.options_menu.port_entry.delete(0, customtkinter.END)
                self.options_menu.port_entry.insert(0, self.port)

        print(self.port)

    def set_host(self):
        if not self.connected:
            new_host = self.options_menu.ip_entry.get()
            if utils.is_valid_ip(new_host):
                self.host = new_host
            else:
                self.options_menu.ip_entry.delete(0, customtkinter.END)
                self.options_menu.ip_entry.insert(0, self.host)
        
        print(self.host)

    def refresh_connection(self):
        self.reset_socket()
        self.set_port()
        self.set_host()
        

    def on_close(self):
        if self.connected:
            self.disconnect()

        self.destroy()


    def connect(self, *args):
        try:
            self.client_socket.connect((self.host, self.port))
            self.address = utils.receive(self.client_socket)

            while True:
                data = utils.receive(self.client_socket)
                if data == "END":
                    break
                
                message = json.loads(data)
                self.msg_list.append(message)

            self.connected = True
            self.update_chat_box()
        except socket.timeout as e:
            self.chat_box.set_console_text("Timed out when trying to connect to server: " + str(e))
        except Exception as e:
            if not self.connected:
                self.chat_box.set_console_text("Error when trying to connect to server: " + str(e))


    def disconnect(self, *args):
        try:
            self.client_socket.close()
            self.client_socket = socket.socket()
            
            self.connected = False
            self.msg_list = []
            self.update_chat_box()
        except Exception as e:
            print("Error when trying to disconnect from the server: " + str(e))


    def send_message(self, *args):
        if self.connected:
            message = self.chat_box.pop_input_box().strip()

            message = {
                "flag": "general_message",
                "from": self.address,
                "to": "all",
                "content": message
            }

            utils.send(self.client_socket, json.dumps(message))

            self.msg_list.append(message)
            self.update_chat_box()
        else:
            self.chat_box.set_console_text("Not connected to the server")

    def receive_message(self):
        print(1)
        while True:
            while self.connected:
                data = utils.receive(self.client_socket)
                print(data)
                if data == "KICKED":
                    self.disconnect()
                    self.connected = False
                elif data is not None:
                    try:
                        message = json.loads(data)
                        print("message recieved")
                        if message["flag"] == "general_message":
                            self.msg_list.append(message)
                            self.update_chat_box()
                    except json.decoder.JSONDecodeError as e:
                        print(f"{data}: {e}")



if __name__ == '__main__':
    app = App()
    thread = threading.Thread(target=app.receive_message)
    thread.start()
    app.mainloop()
