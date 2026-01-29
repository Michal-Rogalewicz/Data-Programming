import customtkinter as ctk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageSequence
import requests
from io import BytesIO
import os

# ------------------ PATH SETUP ------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")

# ------------------ LOAD DATA ------------------

df = pd.read_csv(os.path.join(BASE_DIR, "pokemon_data.csv"))

df.columns = (
    df.columns.str.strip().str.lower()
    .str.replace(" ", "_")
    .str.replace(".", "", regex=False)
)

df["name"] = df["name"].str.title()
df["type_2"] = df["type_2"].fillna("")

# ------------------ AVERAGE STATS ------------------

AVG_STATS = df[["hp", "attack", "defense", "sp_atk", "sp_def", "speed"]].mean()

# ------------------ TYPE COLORS ------------------

TYPE_COLORS = {
    "Fire": "#ff6b6b", "Water": "#4dabf7", "Grass": "#69db7c",
    "Electric": "#ffd43b", "Psychic": "#da77f2", "Ice": "#74c0fc",
    "Dragon": "#9775fa", "Dark": "#495057", "Fairy": "#faa2c1",
    "Fighting": "#e8590c", "Flying": "#91a7ff", "Poison": "#c77dff",
    "Ground": "#e0aaff", "Rock": "#adb5bd", "Bug": "#94d82d",
    "Steel": "#ced4da", "Ghost": "#845ef7", "Normal": "#dee2e6"
}

# ------------------ APP SETUP ------------------

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("1450x900")
app.title("NEXDEX")
app.configure(fg_color="white")

chart_mode = ctk.StringVar(value="both")

# ------------------ LOADING GIF ------------------

gif = Image.open(os.path.join(ASSETS_DIR, "Loading_screen.gif"))
gif_frames = []

for frame in ImageSequence.Iterator(gif):
    frame = frame.convert("RGBA")
    gif_frames.append(ctk.CTkImage(frame, size=(120, 120)))

gif_label = ctk.CTkLabel(app, text="", fg_color="white")
gif_label.pack_forget()

gif_index = 0
gif_running = False

def animate_gif():
    global gif_index
    if not gif_running:
        return
    gif_label.configure(image=gif_frames[gif_index])
    gif_index = (gif_index + 1) % len(gif_frames)
    app.after(100, animate_gif)

def start_loading():
    global gif_running, gif_index
    gif_running = True
    gif_index = 0
    gif_label.pack(pady=10)
    animate_gif()

def stop_loading():
    global gif_running
    gif_running = False
    gif_label.pack_forget()

# ------------------ POKEAPI HELPERS ------------------

def get_pokemon_api(name):
    try:
        r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name.lower()}", timeout=5)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def get_evolution_chain(name):
    try:
        species = requests.get(
            f"https://pokeapi.co/api/v2/pokemon-species/{name.lower()}",
            timeout=5
        ).json()

        evo_url = species["evolution_chain"]["url"]
        chain = requests.get(evo_url, timeout=5).json()["chain"]

        evo = []
        while chain:
            evo.append(chain["species"]["name"].title())
            chain = chain["evolves_to"][0] if chain["evolves_to"] else None

        return " → ".join(evo)
    except:
        return "Unavailable"

def make_type_badge(parent, t):
    if not t:
        return
    ctk.CTkLabel(
        parent,
        text=t,
        fg_color=TYPE_COLORS.get(t, "#adb5bd"),
        text_color="black",
        corner_radius=15,
        padx=12,
        pady=4
    ).pack(side="left", padx=5)

# ------------------ CORE FUNCTIONS ------------------

def load_from_list(name):
    start_loading()
    def delayed():
        pokemon = df[df["name"] == name].iloc[0]
        stop_loading()
        display_pokemon(pokemon)
    app.after(600, delayed)

def search_pokemon():
    query = search_entry.get().strip()
    if not query:
        return
    start_loading()
    def delayed():
        results = df[df["name"].str.contains(query, case=False)]
        stop_loading()
        if results.empty:
            status_label.configure(text="❌ Pokémon not found")
            return
        display_pokemon(results.iloc[0])
    app.after(800, delayed)

def display_pokemon(p):
    for w in info_container.winfo_children():
        w.destroy()

    api = get_pokemon_api(p.name)

    # SPRITE
    if api and api["sprites"]["front_default"]:
        img = Image.open(BytesIO(requests.get(api["sprites"]["front_default"]).content))
        sprite = ctk.CTkImage(img, size=(150, 150))
        ctk.CTkLabel(info_container, image=sprite, text="").pack(pady=5)

    # NAME
    ctk.CTkLabel(
        info_container,
        text=p.name,
        font=("Arial", 24, "bold"),
        text_color="black"
    ).pack(pady=5)

    # TYPES
    tf = ctk.CTkFrame(info_container, fg_color="white")
    tf.pack(pady=5)
    make_type_badge(tf, p.type_1)
    make_type_badge(tf, p.type_2)

    # ABILITIES (ONLY IF AVAILABLE)
    if api and api.get("abilities"):
        abilities = ", ".join(
            a["ability"]["name"].replace("-", " ").title()
            for a in api["abilities"]
        )
        ctk.CTkLabel(
            info_container,
            text=f"Abilities: {abilities}",
            text_color="black"
        ).pack(pady=4)

    # EVOLUTION (ONLY IF AVAILABLE)
    evo_chain = get_evolution_chain(p.name)
    if evo_chain != "Unavailable":
        ctk.CTkLabel(
            info_container,
            text=f"Evolution: {evo_chain}",
            text_color="black"
        ).pack(pady=4)

    status_label.configure(text=f"Loaded {p.name}")
    draw_graphs(p)

def draw_graphs(p):
    for w in graph_frame.winfo_children():
        w.destroy()

    labels = ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]
    stats = [p.hp, p.attack, p.defense, p.sp_atk, p.sp_def, p.speed]
    avg = AVG_STATS.tolist()
    x = np.arange(len(labels))

    if chart_mode.get() in ("bar", "both"):
        fig, ax = plt.subplots(figsize=(6.5, 4.8))
        ax.bar(x, avg, color="#dee2e6", label="Average")
        ax.bar(x, stats, color="#4dabf7", alpha=0.85, label=p.name)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_ylim(0, 200)
        ax.legend()
        FigureCanvasTkAgg(fig, graph_frame).get_tk_widget().pack(side="left", padx=25)

    if chart_mode.get() in ("radar", "both"):
        angles = np.linspace(0, 2*np.pi, len(stats), endpoint=False)
        stats_loop = stats + stats[:1]
        avg_loop = avg + avg[:1]
        angles_loop = np.append(angles, angles[0])

        fig, ax = plt.subplots(figsize=(6.5, 4.8), subplot_kw=dict(polar=True))
        ax.plot(angles_loop, avg_loop, color="#adb5bd", label="Average")
        ax.plot(angles_loop, stats_loop, color="#4dabf7", label=p.name)
        ax.fill(angles_loop, stats_loop, alpha=0.35)
        ax.set_thetagrids(angles * 180/np.pi, labels)
        ax.legend(loc="upper right")
        FigureCanvasTkAgg(fig, graph_frame).get_tk_widget().pack(side="right", padx=25)

def toggle_chart():
    modes = ["bar", "radar", "both"]
    chart_mode.set(modes[(modes.index(chart_mode.get()) + 1) % 3])
    status_label.configure(text=f"Chart mode: {chart_mode.get().upper()}")

# ------------------ UI ------------------

main_frame = ctk.CTkFrame(app, fg_color="white")
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

sidebar_visible = False
list_frame = ctk.CTkFrame(main_frame, width=260, fg_color="white")

pokemon_list = ctk.CTkScrollableFrame(list_frame, width=240, fg_color="white")
pokemon_list.pack(fill="both", expand=True)

for name in df["name"].unique():
    ctk.CTkButton(
        pokemon_list,
        text=name,
        anchor="w",
        fg_color="#f1f3f5",
        text_color="black",
        hover_color="#e9ecef",
        command=lambda n=name: load_from_list(n)
    ).pack(fill="x", pady=2)

def toggle_sidebar():
    global sidebar_visible
    if sidebar_visible:
        list_frame.pack_forget()
        sidebar_visible = False
    else:
        list_frame.pack(side="left", fill="y", padx=10)
        sidebar_visible = True

content_frame = ctk.CTkFrame(main_frame, fg_color="white")
content_frame.pack(side="right", fill="both", expand=True)

ctk.CTkButton(content_frame, text="☰ Pokédex", width=140, command=toggle_sidebar).pack(pady=(5, 10))

logo_img = ctk.CTkImage(
    Image.open(os.path.join(ASSETS_DIR, "Pokedex_Title.png")),
    size=(300, 110)
)
ctk.CTkLabel(content_frame, image=logo_img, text="", fg_color="white").pack(pady=(10, 20))

search_entry = ctk.CTkEntry(content_frame, placeholder_text="Search Pokémon", width=320)
search_entry.pack(pady=5)

ctk.CTkButton(content_frame, text="Search", command=search_pokemon).pack()
ctk.CTkButton(content_frame, text="Toggle Charts", command=toggle_chart).pack(pady=5)

info_container = ctk.CTkFrame(content_frame, fg_color="white")
info_container.pack(pady=10)

graph_frame = ctk.CTkFrame(content_frame, fg_color="white")
graph_frame.pack(pady=20)

status_label = ctk.CTkLabel(app, text="Ready", anchor="w", fg_color="white", text_color="black")
status_label.pack(fill="x", padx=10, pady=5)

app.mainloop()