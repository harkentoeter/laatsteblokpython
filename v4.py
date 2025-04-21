import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from PIL import Image, ImageTk
import requests
from bs4 import BeautifulSoup
import urllib.request
import json
import io

# ---------- USER-AGENTS ---------- #
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 13_5 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36"
]

# ---------- FUNCTIONS ---------- #
def get_response_with_user_agents(url):
    for agent in USER_AGENTS:
        try:
            headers = {"User-Agent": agent}
            if not url.startswith("http"):
                url = "https://" + url
            return requests.get(url, headers=headers, timeout=5)
        except Exception:
            continue
    raise Exception("Alle user agents zijn gefaald of de site is onbereikbaar.")

def scrape_website_title():
    url = entry_url.get()
    try:
        response = get_response_with_user_agents(url)
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find("title")
        output_text.insert(tk.END, f"\nTitel van de pagina: {title.text if title else 'Niet gevonden'}\n")
    except Exception as e:
        output_text.insert(tk.END, f"\nVerbindingsfout: {e}\n")

def zoek_bol_prijs():
    search = entry_bol.get()
    try:
        url = f"https://www.bol.com/nl/nl/s/?searchtext={search}"
        response = get_response_with_user_agents(url)
        soup = BeautifulSoup(response.content, "html.parser")
        prijs = soup.find("span", class_="promo-price")
        cent = soup.find("sup", class_="promo-price__fraction")

        if prijs and cent:
            euro = prijs.contents[0].strip()
            centen = cent.contents[0].strip()
            output_text.insert(tk.END, f"\nPrijs van '{search}' op bol.com: {euro},{centen}\n")
        else:
            output_text.insert(tk.END, f"\nGeen prijs gevonden voor '{search}'.\n")
    except Exception as e:
        output_text.insert(tk.END, f"\nFout bij het zoeken: {e}\n")

def getjson(url):
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())

def haal_rassen_op():
    data = getjson("https://dog.ceo/api/breeds/list/all")
    rassen = data.get("message", {})
    output_text.insert(tk.END, "\nAlle hondenrassen:\n")
    for ras in rassen:
        output_text.insert(tk.END, f"- {ras}\n")

def willekeurige_hond():
    data = getjson("https://dog.ceo/api/breeds/image/random")
    foto = data.get("message", "")
    toon_foto(foto)
    output_text.insert(tk.END, f"\nLink: {foto}\n")

ras_foto_lijst = []
ras_foto_index = 0
huidig_ras = ""

def foto_van_ras():
    global ras_foto_lijst, ras_foto_index, huidig_ras

    ras = entry_ras.get().lower()
    if ras != huidig_ras:
        huidig_ras = ras
        ras_foto_lijst = []
        ras_foto_index = 0

    if not ras_foto_lijst:
        try:
            url = f"https://dog.ceo/api/breed/{ras}/images"
            data = getjson(url)
            ras_foto_lijst = data.get("message", [])
            ras_foto_index = 0
        except Exception as e:
            output_text.insert(tk.END, f"\nKon foto's niet ophalen voor {ras}: {e}\n")
            return

    if not ras_foto_lijst:
        output_text.insert(tk.END, f"\nGeen foto's gevonden voor {ras}\n")
        return

    foto_url = ras_foto_lijst[ras_foto_index]
    toon_foto(foto_url)
    output_text.insert(tk.END, f"\n({ras}) Foto {ras_foto_index+1}/{len(ras_foto_lijst)}\nLink: {foto_url}\n")

    ras_foto_index = (ras_foto_index + 1) % len(ras_foto_lijst)

def toon_foto(foto_url):
    try:
        with urllib.request.urlopen(foto_url) as u:
            raw_data = u.read()
        im = Image.open(io.BytesIO(raw_data))
        im = im.resize((300, 300))
        photo = ImageTk.PhotoImage(im)

        image_label.configure(image=photo)
        image_label.image = photo
    except Exception as e:
        output_text.insert(tk.END, f"\nKon afbeelding niet tonen: {e}\n")

# ---------- COOLBLUE SCRAPER ---------- #
def scrape_coolblue(search_query, max_results=10):
    base_url = "https://www.coolblue.nl"
    search_url = f"{base_url}/en/search?query={search_query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        products = []
        product_cards = soup.select('a.link[title]')
        seen_titles = set()

        for product in product_cards:
            title = product.get("title")
            link = base_url + product.get("href")
            if title in seen_titles:
                continue
            seen_titles.add(title)
            parent = product.find_parent("div")
            price_tag = parent.find_next("strong", class_="sales-price__current") if parent else None
            price = price_tag.text.strip() if price_tag else "Not available"
            products.append({"title": title, "price": price, "link": link})
            if len(products) >= max_results:
                break

        output_text.insert(tk.END, f"\nCoolblue resultaten voor '{search_query}':\n")
        for i, p in enumerate(products, 1):
            output_text.insert(tk.END, f"{i}. {p['title']}\n   Prijs: {p['price']}\n   Link: {p['link']}\n\n")
    except Exception as e:
        output_text.insert(tk.END, f"\nFout bij Coolblue scraping: {e}\n")

# ---------- GUI ---------- #
root = tk.Tk()
root.title("Footprinting Tool")
root.geometry("900x700")
root.configure(bg="#1e1e1e")

style = ttk.Style()
style.theme_use("default")
style.configure("TButton", foreground="white", background="#3e3e3e", font=("Arial", 10), padding=6)
style.configure("TLabel", foreground="white", background="#1e1e1e", font=("Arial", 10))
style.configure("TEntry", fieldbackground="#2e2e2e", foreground="white")

main_frame = ttk.Frame(root)
main_frame.pack(pady=10)

label_url = ttk.Label(main_frame, text="Website URL")
label_url.grid(row=0, column=0, sticky="w", padx=5)
entry_url = ttk.Entry(main_frame, width=50)
entry_url.grid(row=0, column=1, padx=5, pady=2)

label_bol = ttk.Label(main_frame, text="Bol.com / Coolblue product")
label_bol.grid(row=1, column=0, sticky="w", padx=5)
entry_bol = ttk.Entry(main_frame, width=50)
entry_bol.grid(row=1, column=1, padx=5, pady=2)

label_ras = ttk.Label(main_frame, text="Hondenras")
label_ras.grid(row=2, column=0, sticky="w", padx=5)
entry_ras = ttk.Entry(main_frame, width=50)
entry_ras.grid(row=2, column=1, padx=5, pady=2)

button_width = 30
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

tt = ttk.Button(button_frame, text="Scrape Titel", command=scrape_website_title, width=button_width)
tt.grid(row=0, column=0, padx=5, pady=2)

bp = ttk.Button(button_frame, text="Zoek Prijs op Bol.com", command=zoek_bol_prijs, width=button_width)
bp.grid(row=0, column=1, padx=5, pady=2)

cb = ttk.Button(button_frame, text="Zoek op Coolblue", command=lambda: scrape_coolblue(entry_bol.get()), width=button_width)
cb.grid(row=1, column=0, padx=5, pady=2)

rf = ttk.Button(button_frame, text="Foto van Ras", command=foto_van_ras, width=button_width)
rf.grid(row=1, column=1, padx=5, pady=2)

wr = ttk.Button(button_frame, text="Alle Hondenrassen", command=haal_rassen_op, width=button_width)
wr.grid(row=2, column=0, padx=5, pady=2)

rd = ttk.Button(button_frame, text="Willekeurige Hond", command=willekeurige_hond, width=button_width)
rd.grid(row=2, column=1, padx=5, pady=2)

output_text = scrolledtext.ScrolledText(root, width=100, height=15, bg="#2e2e2e", fg="white")
output_text.pack(padx=10, pady=10)

image_label = tk.Label(root, bg="#1e1e1e")
image_label.pack(pady=10)

footer = ttk.Label(root, text="Versie 2.1 – Propagandalf", font=("Arial", 9, "italic"), foreground="#888888", background="#1e1e1e")
footer.pack(pady=5)

root.mainloop()

