import tkinter as tk
from tkinter import messagebox
import socket
import json
from client_utils import open_trailer, display_info, generate_reviews_html
import platform


def connect_to_server():
    """Partea de socket"""
    
    global client_socket
    host = "127.0.0.1"
    port = 65432
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        label_status.config(text="Conectat la server.")
    except Exception as e:
        messagebox.showerror("Eroare", f"Nu se poate conecta la server: {e}")
        root.quit()


def send_request():
    """Partea de comunicare cu serverul"""
    
    global client_socket
    search_type = search_var.get()
    search_text = entry_search.get()
    
    if not search_text:
        messagebox.showwarning("Atentie", "Introduceti un nume de film sau actor!")
        return
    
    if search_type == "trailer":
        message = f"trailer:{search_text}"
    else:
        message = f"{search_type}:{search_text}"
    
    try:
        client_socket.sendall(message.encode('utf-8'))
        
        data = client_socket.recv(65536)
        response = json.loads(data.decode('utf-8'))
        
        if response["status"] == "found":
            results = response["data"]
            print(results)
            result_text = ""
            what_to_display = "---Filme gasite in baza de date---\n"
        
            for entry in results:
                result_text += (f"Titlu: {entry['title']}, Data lansarii: {entry['release_date']}, "
                                f"Rating: {entry['rating']}\n")
                
            what_to_display += display_info(result_text, search_type)
            label_response.config(text=what_to_display)
            
        elif response["status"] == "not_found":
            label_response.config(text=f"Eroare: {response['message']}")
            
        elif response["status"] == "found_in_api":
            results = response["data"]
            result_text = ""
            what_to_display = "---Filme gasite in (TMDB) API---\n"
            
            for movie in results:
                result_text += (f"Titlu: {movie['title']}, Data lansarii: {movie['release_date']}, "
                            f"Rating: {movie['rating']}\n")
            
            what_to_display += display_info(result_text, search_type)
            label_response.config(text=what_to_display)
            
        elif response["status"] == "trailer":
            trailer_url = response["url"]
            print(trailer_url)
            if "youtube.com" in trailer_url:
                open_trailer(trailer_url)
            else:
                messagebox.showinfo("Info", trailer_url)
                
        elif response["status"] == "reviews_found":
            reviews = response["data"]
            if reviews:
                generate_reviews_html(reviews, title="Recenzii pentru Film")
                label_response.config(text="Recenziile au fost deschise intr o pagina HTML")
            else:
                label_response.config(text="Nu s au gasit recenzii.")

        elif response["status"] == "inexistent_movie_to_review":
            message = response["message"]
            label_response.config(text=message)
        
        elif response["status"] == "no_reviews":
            message = response["message"]
            label_response.config(text=message)

        else:
            label_response.config(text="Raspuns necunoscut de la server.")

    except Exception as e:
        messagebox.showerror("Eroare", f"A aparut o problema in client: {e}")

  
def search_trailer():
    search_var.set("trailer")
    send_request()
    
def clear_search():
    """Pentru a goli campul de search."""
    entry_search.delete(0, tk.END)

def quit_client():
    """Deconectarea de la server"""
    global client_socket
    try:
        client_socket.sendall(b"quit")
        client_socket.close()
        label_status.config(text="Deconectat de la server.")
        root.quit()
    except Exception as e:
        messagebox.showerror("Eroare", f"Nu se poate inchide conexiunea: {e}")
        root.quit()
        
               
"""Partea de GUI"""

root = tk.Tk()
root.title("Client GUI - Search for Movies")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

root.geometry(f"{screen_width}x{screen_height}")
print(f"Platforma este: {platform.system()}")
if platform.system() == 'Windows' or platform.system() == 'Linux':
    root.attributes('-zoomed', True)
elif platform.system() == 'Darwin':
    root.attributes('-fullscreen', False)

label_status = tk.Label(root, text="Conectare...")
label_status.pack(pady=5)

label_instruction = tk.Label(root, text="")
label_instruction.pack(pady=5)

search_var = tk.StringVar(value="title") 
radio_title = tk.Radiobutton(root, text="Titlu film", variable=search_var, value="title")
radio_title.pack()
radio_actor = tk.Radiobutton(root, text="Nume actor", variable=search_var, value="actor")
radio_actor.pack()

radio_reviews = tk.Radiobutton(root, text="Recenzii", variable=search_var, value="reviews")
radio_reviews.pack()

frame_search = tk.Frame(root)
frame_search.pack(pady=5)

entry_search = tk.Entry(frame_search, width=50)
entry_search.pack(side=tk.LEFT, pady=5)

button_clear = tk.Button(frame_search, text="Del", command=clear_search)
button_clear.pack(side=tk.RIGHT)

frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=10)

button_search = tk.Button(frame_buttons, text="Cauta", command=send_request)
button_search.pack(side=tk.LEFT, padx=5)

button_trailer = tk.Button(frame_buttons, text="Vezi Trailer", command=search_trailer)
button_trailer.pack(side=tk.LEFT, padx=5)

button_quit = tk.Button(root, text="Quit", command=quit_client)
button_quit.pack(pady=10)

label_response = tk.Label(root, text="")
label_response.pack(pady=10)

connect_to_server()
root.mainloop()