import socket
import customtkinter


def change_theme(new_theme: str):
    customtkinter.set_appearance_mode(new_theme)

def change_font_size(new_scaling: str):
    new_scaling_float = int(new_scaling.replace("%", "")) / 100
    customtkinter.set_widget_scaling(new_scaling_float)


class OptionsMenu(customtkinter.CTkFrame):

    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.appearance_mode_label = customtkinter.CTkLabel(self, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=0, column=0, padx=10, pady=10)
        self.theme_menu = customtkinter.CTkOptionMenu(self, values=["Light", "Dark", "System"], command=change_theme)
        self.theme_menu.grid(row=1, column=0, padx=10, pady=10)
        self.theme_menu.set("Dark")

        self.scaling_label = customtkinter.CTkLabel(self, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=2, column=0, padx=10, pady=10)
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self, values=[str(i*10) + '%' for i in range(1, 21)], command=change_font_size)
        self.scaling_optionemenu.grid(row=3, column=0, padx=10, pady=10)
        self.scaling_optionemenu.set("120%")
        change_font_size("120%")

        self.connect_button = customtkinter.CTkButton(self, text="Connect", command=self.master.connect)
        self.connect_button.grid(row=4, column=0, padx=10, pady=10)

        self.disconnect_button = customtkinter.CTkButton(self, text="Disconnect", command=self.master.disconnect)
        self.disconnect_button.grid(row=5, column=0, padx=10, pady=10)


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
        print(text)
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
        self.host = "192.168.0.112" # use this when running the server on the same network
        self.port = 7013
        self.connected = False
        self.msg_list = ["---Start---"]

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
        self.chat_box.set_console_text("\n".join(self.msg_list))


    def on_close(self):
        if self.connected:
            self.disconnect()

        self.destroy()


    def connect(self, *args):
        try:
            self.client_socket.connect((self.host, self.port))
            self.connected = True
            self.update_chat_box()
        except socket.timeout as e:
            self.chat_box.set_console_text("Timed out when trying to connect to server: " + str(e))
        except Exception as e:
            self.chat_box.set_console_text("Error when trying to connect to server: " + str(e))


    def disconnect(self, *args):
        try:
            self.client_socket.close()
            self.client_socket = socket.socket()

            self.connected = False
            self.msg_list.append("Disconnected from server")
            self.update_chat_box()
        except Exception as e:
            self.chat_box.set_console_text("Error when trying to disconnect from the server: " + str(e))


    def send_message(self, *args):
        if self.connected:
            message = self.chat_box.pop_input_box().strip()

            self.msg_list.append(f"User > {message}")
            if message.lower().strip() == "stop":
                self.disconnect()
            else:
                try:
                    self.client_socket.send(message.encode())
                    response = self.client_socket.recv(1024).decode()
                    print(response)
                    self.update_chat_box()
                except Exception as e:
                    print("Error when trying to send message: " + str(e))
                    self.disconnect()
        else:
            self.chat_box.set_console_text("Not connected to the server")



if __name__ == '__main__':
    app = App()
    app.mainloop()
