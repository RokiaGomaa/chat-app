import socket
import tkinter as tk
from tkinter import *
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image
import os
import threading

Screen = tk.Tk()
# ---------------- SERVER ----------------
SERVER_IP = 'mainline.proxy.rlwy.net'
SERVER_PORT = 50000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# ---------------- CONNECT ----------------
def connect():
    try:
        client_socket.connect((SERVER_IP, SERVER_PORT))
        threading.Thread(target=receive, daemon=True).start()
    except:
        messagebox.showerror("Error", "Connection Failed")
        Screen.destroy()

def receive():
    while True:
        try:
            data = client_socket.recv(4096)
            if not data:
                break

            chat_box.config(state='normal')
            chat_box.insert(END, data.decode(errors='ignore') + "\n", "left")
            entry.delete(0,END)
            chat_box.see(END)
            chat_box.config(state='disabled')
            
            

        except:
            break

# ---------------- TEXT ----------------
def send_text(event=None):
    message = text_var.get()
    if not message:
        return

    client_socket.sendall(f"TEXT|{message}".encode())

    chat_box.config(state='normal')
    chat_box.insert(END,  message + "\n", "right")
    entry.delete(0,END)
    chat_box.see(END)
    chat_box.config(state='disabled')
  
    

# ---------------- HD ----------------
isHD = False

def toggle_hd():
    global isHD
    isHD = not isHD

    hd_button.config(
        text="HD ✓" if isHD else "HD "
    )

# ---------------- FILE ----------------
def send_file(event=None):
    file_path = filedialog.askopenfilename()

    if not file_path:
        return

    file_name = os.path.basename(file_path)
    text_var.set(" " + file_name)

    ext = file_path.split(".")[-1].lower()

    try:
        # IMAGE
        if ext in ["jpg", "jpeg", "png"]:
            if not isHD:
                img = Image.open(file_path)
                if img.mode != "RGB":
                    img = img.convert("RGB")

                temp = "temp.jpg"
                img.save(temp, "JPEG", quality=40)
                file_path = temp

                f=open(file_path, "rb") 
                data = f.read()
                size = str(len(data)).encode()
                client_socket.sendall(b"IMAGE|" + size + b"|" + data)
                f.close()

        # VIDEO
        elif ext in ["mp4", "avi", "mov"]:
            if not isHD:
                temp = "temp.mp4"
                os.system(f'ffmpeg -i "{file_path}" -vcodec libx264 -crf 28 "{temp}"')
                file_path = temp

                f=open(file_path, "rb") 
                data = f.read()
                size = str(len(data)).encode()
                client_socket.sendall(b"VIDEO|" + size + b"|" + data)
                f.close()

        # FILE
        else:
                f= open(file_path, "rb")  
                data = f.read()
                size = str(len(data)).encode()
                client_socket.sendall(b"FILE|" + size + b"|" + data)
                f.close()

    except Exception as e:
        messagebox.showerror("Error", str(e))

# ---------------- UI ----------------

Screen.title("Chat App")
Screen.geometry("450x600")

# ---------------- CHAT BOX ----------------
chat_box = scrolledtext.ScrolledText(Screen,wrap=tk.WORD,font=("Helvetica", 12), bg="#e5ddd5",fg="#111b21",state=tk.DISABLED,bd=0,highlightthickness=0,insertbackground="black")
chat_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# رسائل WhatsApp-style
chat_box.tag_config("right",justify="right",background="#dcf8c6",lmargin2=80,rmargin=10)
chat_box.tag_config("left",justify="left",background="#ffffff",lmargin1=10,lmargin2=10,rmargin=80)

# ---------------- INPUT AREA ----------------
bottom_frame = tk.Frame(Screen, bg="#f0f0f0")
bottom_frame.pack(fill=tk.X, padx=8, pady=8)

text_var = tk.StringVar()

entry = tk.Entry(bottom_frame,textvariable=text_var,font=("Helvetica", 13), bg="white", fg="#111b21",highlightthickness=1,highlightbackground="#ccc",highlightcolor="#25d366")
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, ipady=6)
entry.bind("<Return>", send_text())

# ---------------- BUTTONS ----------------
send_btn = tk.Button(bottom_frame,text="Send",command=send_text,bg="#25d366",  fg="white",activebackground="#1ebe5d")
send_btn.pack(side=tk.RIGHT, padx=5)

file_btn = tk.Button(bottom_frame,text="Files",command=send_file,bg="#128c7e",fg="white",activebackground="#0e6f64")
file_btn.pack(side=tk.RIGHT, padx=5)

hd_button = tk.Button(bottom_frame,text="HD",command=toggle_hd,bg="#34b7f1",fg="white",activebackground="#1da1d2")
hd_button.pack(side=tk.RIGHT, padx=5)

# ---------------- START ----------------
connect()
Screen.mainloop()