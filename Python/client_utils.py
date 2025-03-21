import webbrowser
from tkinter import messagebox
import os

def convert_to_embed_url(youtube_url):
    """Transforma un URL yt intr un URL embed"""
    
    if "watch?v=" in youtube_url:
        video_id = youtube_url.split("watch?v=")[-1]
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        return embed_url
    return youtube_url

def open_trailer(url):
    """Deschide trailerul intr un browser web."""
    try:
        embed_url = convert_to_embed_url(url)
        if "https://" in embed_url:
            webbrowser.open(embed_url, new=2)
        else:
            messagebox.showinfo("Info", "Linkul primit nu contine un URL valid.")
    except Exception as e:
        messagebox.showerror("Eroare", f"Nu se poate deschide linkul: {e}")
        
        
def display_info(data, search_type):
    """Pentru cum sa afiseze cautarea"""
    
    lines = data.split('\n')
    if len(lines) == 0:
        return "Nu s au gasit rezultate."
    
    if search_type == 'actor':
        display_data = "Top 10 filme in care joaca in functie de rating (highest)\n"
        for line in lines:
            display_data += f"- {line}\n"
    else:
        display_data = ""
        display_data += f"Cea mai populara cautare:\n {lines[0]}\n"
        
        if len(lines) > 2:
            display_data += "Poate cautati alt film:\n"
            for line in lines[1:]:
                display_data += f"- {line}\n"
        
    
    return display_data

def generate_reviews_html(reviews, title="Recenzii"):
    """Creeaza un fis HTML pentru recenzii si il deschide in browser"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ro">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                padding: 20px;
                background-color: #f4f4f9;
                color: #333;
            }}
            h1 {{
                text-align: center;
                color: #444;
            }}
            .review {{
                margin-bottom: 20px;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background: #fff;
            }}
            .review h3 {{
                margin: 0 0 10px;
                color: #555;
            }}
            .review p {{
                margin: 10px 0;
                line-height: 1.6;
            }}
            .review a {{
                color: #1e90ff;
                text-decoration: none;
            }}
            .review a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
    """

    for review in reviews:
        author = review.get("author", "Anonim")
        content = review.get("content", "Fara continut disponibil.")
        url = review.get("url", "#")

        html_content += f"""
        <div class="review">
            <h3>Autor: {author}</h3>
            <p>{content}</p>
            <a href="{url}" target="_blank">Citeste recenzia completa</a>
        </div>
        """

    html_content += """
    </body>
    </html>
    """

    html_file = "reviews.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    webbrowser.open(f"file://{os.path.abspath(html_file)}")