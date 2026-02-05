import tkinter as tk
import pandas as pd
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import os
import requests
from io import BytesIO

# Create images directory if it doesn't exist
if not os.path.exists("images"):
    os.makedirs("images")
    print("Created 'images' folder for caching Pokémon sprites")

# Load pokemon data
pokemon_df = pd.read_csv("Assets/pokemon_data.csv")

# --- Navy theme ---
NAVY_BG = "#06162f"
NAVY_PANEL = "#0b2347"
NAVY_CARD = "#0f2f5e"
NAVY_BTN = "#123a73"
NAVY_BTN_ACTIVE = "#184a91"
TEXT = "#ffffff"

# Type colors dictionary
TYPE_COLORS = {
    "Fire": "#F08030", "Water": "#6890F0", "Grass": "#78C850",
    "Electric": "#F8D030", "Psychic": "#F85888", "Ice": "#98D8D8",
    "Dragon": "#7038F8", "Dark": "#705848", "Fairy": "#EE99AC",
    "Normal": "#A8A878", "Fighting": "#C03028", "Flying": "#A890F0",
    "Poison": "#A040A0", "Ground": "#E0C068", "Rock": "#B8A038",
    "Bug": "#A8B820", "Ghost": "#705898", "Steel": "#B8B8D0"
}

STAT_FIELDS = ["HP", "Attack", "Defense", "Speed"]

# Store current pokemon for charts
current_pokemon = None


def fetch_pokemon_image(pokemon_id, pokemon_name):
    """
    Fetch Pokémon image from PokéAPI and cache it locally.
    Returns the PIL Image object or None if failed.
    """
    # Check if image already exists locally
    local_paths = [
        f"images/{pokemon_id}.png",
        f"images/{pokemon_name.lower()}.png"
    ]

    for path in local_paths:
        if os.path.exists(path):
            try:
                return Image.open(path)
            except:
                continue

    # If not cached, fetch from PokéAPI
    try:
        # PokéAPI uses numeric IDs
        url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            # Get the official artwork (high quality)
            image_url = data['sprites']['other']['official-artwork']['front_default']

            if image_url:
                img_response = requests.get(image_url, timeout=5)
                if img_response.status_code == 200:
                    img = Image.open(BytesIO(img_response.content))

                    # Save to cache
                    cache_path = f"images/{pokemon_id}.png"
                    img.save(cache_path)
                    print(f"Downloaded and cached: {pokemon_name} (ID: {pokemon_id})")

                    return img
    except Exception as e:
        print(f"Failed to fetch image for {pokemon_name}: {e}")

    return None


# Create main window
window = tk.Tk()
window.title("Pokédex")
window.geometry("1400x900")
window.configure(bg=NAVY_BG)

# Load pokeball gif for animation
gif = Image.open("Assets/pokeball.gif")
frames = []
try:
    while True:
        frame = ImageTk.PhotoImage(gif.copy().resize((200, 200)))
        frames.append(frame)
        gif.seek(len(frames))
except EOFError:
    pass

# Main container
main_frame = tk.Frame(window, bg=NAVY_BG)
main_frame.pack(fill="both", expand=True)

# Top section - logo and search
top_section = tk.Frame(main_frame, bg=NAVY_BG)
top_section.pack(fill="x", pady=10)

# Logo
window.pokedex_img = tk.PhotoImage(file="Assets/Pokedex.png")
logo_label = tk.Label(top_section, image=window.pokedex_img, bg=NAVY_BG)
logo_label.pack(pady=10)

# Search area
search_frame = tk.Frame(top_section, bg=NAVY_BG)
search_frame.pack(pady=10)

search_title = tk.Label(search_frame, text="Search Pokémon",
                        font=("Helvetica", 16, "bold"),
                        bg=NAVY_BG, fg=TEXT)
search_title.pack(pady=(0, 10))

entry = tk.Entry(search_frame, font=("Helvetica", 22, "bold"),
                 justify="center", width=20, bd=0, relief="flat",
                 bg=NAVY_PANEL, fg=TEXT, insertbackground=TEXT)
entry.pack(pady=10, ipady=8)
entry.focus()

status_label = tk.Label(search_frame, text="",
                        font=("Helvetica", 12, "bold"),
                        bg=NAVY_BG, fg="#ffcc00")
status_label.pack()

# Content area
content_area = tk.Frame(main_frame, bg=NAVY_BG)
content_area.pack(fill="both", expand=True, padx=20, pady=10)

# Loading screen
loading_frame = tk.Frame(content_area, bg=NAVY_BG)

gif_label = tk.Label(loading_frame, bg=NAVY_BG)
gif_label.pack(pady=50)

loading_text = tk.Label(loading_frame, text="Searching for Pokémon...",
                        font=("Helvetica", 18, "bold"),
                        bg=NAVY_BG, fg=TEXT)
loading_text.pack(pady=10)

current_frame_index = [0]


def animate_gif():
    if loading_frame.winfo_viewable():
        gif_label.config(image=frames[current_frame_index[0]])
        current_frame_index[0] = (current_frame_index[0] + 1) % len(frames)
    window.after(60, animate_gif)


animate_gif()

# Results screen
results_frame = tk.Frame(content_area, bg=NAVY_BG)

# Left side - Pokemon stats
left_side = tk.Frame(results_frame, bg=NAVY_BG, width=600)
left_side.pack(side="left", fill="both", expand=False, padx=(0, 10))
left_side.pack_propagate(False)

stats_card = tk.Frame(left_side, bg=NAVY_CARD, bd=0)
stats_card.pack(fill="both", expand=True, padx=5, pady=5)

stats_canvas = tk.Canvas(stats_card, bg=NAVY_PANEL, highlightthickness=0)
stats_scrollbar = tk.Scrollbar(stats_card, orient="vertical", command=stats_canvas.yview)

stats_content = tk.Frame(stats_canvas, bg=NAVY_PANEL)

stats_content.bind("<Configure>", lambda e: stats_canvas.configure(scrollregion=stats_canvas.bbox("all")))
stats_canvas.create_window((0, 0), window=stats_content, anchor="nw", width=580)
stats_canvas.configure(yscrollcommand=stats_scrollbar.set)

stats_canvas.pack(side="left", fill="both", expand=True, padx=3, pady=3)
stats_scrollbar.pack(side="right", fill="y")

# Pokemon info labels
pokemon_image_label = tk.Label(stats_content, bg=NAVY_PANEL)
pokemon_image_label.pack(pady=20)

pokemon_name_label = tk.Label(stats_content, text="",
                              font=("Helvetica", 32, "bold"),
                              bg=NAVY_PANEL, fg=TEXT)
pokemon_name_label.pack(pady=10)

legendary_label = tk.Label(stats_content, text="",
                           font=("Helvetica", 18, "bold"),
                           bg=NAVY_PANEL, fg="#ffcc00")
legendary_label.pack(pady=5)

type_label = tk.Label(stats_content, text="",
                      font=("Helvetica", 18, "bold"),
                      padx=30, pady=12, fg="white")
type_label.pack(pady=15)

stats_text_label = tk.Label(stats_content, text="",
                            bg=NAVY_PANEL, fg=TEXT,
                            font=("Helvetica", 18, "bold"),
                            justify="center")
stats_text_label.pack(pady=30, padx=20)

# Right side - Chart buttons
right_side = tk.Frame(results_frame, bg=NAVY_BG)
right_side.pack(side="right", fill="both", expand=True, padx=(10, 0))

chart_title = tk.Label(right_side, text="View Charts",
                       font=("Helvetica", 24, "bold"),
                       bg=NAVY_BG, fg=TEXT)
chart_title.pack(pady=30)

buttons_container = tk.Frame(right_side, bg=NAVY_BG)
buttons_container.pack(expand=True)


def themed_button(parent, text, command):
    return tk.Button(parent, text=text,
                     font=("Helvetica", 14, "bold"),
                     bg=NAVY_BTN, fg=TEXT, width=20, pady=15,
                     relief="flat", cursor="hand2",
                     activebackground=NAVY_BTN_ACTIVE,
                     command=command)


# Chart functions
def show_bar_chart():
    if current_pokemon is None:
        return

    chart_window = tk.Toplevel(window)
    chart_window.title(f"{current_pokemon['Name']} - Bar Chart")
    chart_window.geometry("800x600")
    chart_window.configure(bg=NAVY_BG)

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor(NAVY_BG)
    ax.set_facecolor(NAVY_PANEL)

    stats_names = STAT_FIELDS
    stats_values = [current_pokemon[s] for s in stats_names]
    color = TYPE_COLORS.get(current_pokemon["Type 1"], "gray")

    ax.bar(stats_names, stats_values, color=color, edgecolor='white', linewidth=2)
    ax.set_title(f"{current_pokemon['Name']} Stats - Bar Chart",
                 fontsize=16, fontweight='bold', color='white', pad=20)
    ax.set_ylabel("Value", fontsize=12, color='white')
    ax.set_ylim(0, max(stats_values) * 1.2)
    ax.grid(axis='y', alpha=0.3, linestyle='--', color='gray')
    ax.tick_params(colors='white')

    canvas = FigureCanvasTkAgg(fig, chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def show_line_graph():
    if current_pokemon is None:
        return

    chart_window = tk.Toplevel(window)
    chart_window.title(f"{current_pokemon['Name']} - Line Graph")
    chart_window.geometry("800x600")
    chart_window.configure(bg=NAVY_BG)

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor(NAVY_BG)
    ax.set_facecolor(NAVY_PANEL)

    stats_names = STAT_FIELDS
    stats_values = [current_pokemon[s] for s in stats_names]
    color = TYPE_COLORS.get(current_pokemon["Type 1"], "gray")

    ax.plot(stats_names, stats_values, marker="o", color=color,
            linewidth=3, markersize=12, markeredgecolor='white', markeredgewidth=2)
    ax.fill_between(range(len(stats_names)), stats_values, alpha=0.3, color=color)
    ax.set_title(f"{current_pokemon['Name']} Stats - Line Graph",
                 fontsize=16, fontweight='bold', color='white', pad=20)
    ax.set_ylabel("Value", fontsize=12, color='white')
    ax.set_ylim(0, max(stats_values) * 1.2)
    ax.grid(True, alpha=0.3, linestyle='--', color='gray')
    ax.tick_params(colors='white')

    canvas = FigureCanvasTkAgg(fig, chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def show_horizontal_bar():
    if current_pokemon is None:
        return

    chart_window = tk.Toplevel(window)
    chart_window.title(f"{current_pokemon['Name']} - Horizontal Bar")
    chart_window.geometry("800x600")
    chart_window.configure(bg=NAVY_BG)

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor(NAVY_BG)
    ax.set_facecolor(NAVY_PANEL)

    stats_names = STAT_FIELDS
    stats_values = [current_pokemon[s] for s in stats_names]
    color = TYPE_COLORS.get(current_pokemon["Type 1"], "gray")

    ax.barh(stats_names, stats_values, color=color, edgecolor='white', linewidth=2)
    ax.set_title(f"{current_pokemon['Name']} Stats - Horizontal Bar",
                 fontsize=16, fontweight='bold', color='white', pad=20)
    ax.set_xlabel("Value", fontsize=12, color='white')
    ax.set_xlim(0, max(stats_values) * 1.2)
    ax.grid(axis='x', alpha=0.3, linestyle='--', color='gray')
    ax.tick_params(colors='white')

    canvas = FigureCanvasTkAgg(fig, chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def show_radar_chart():
    if current_pokemon is None:
        return

    chart_window = tk.Toplevel(window)
    chart_window.title(f"{current_pokemon['Name']} - Radar Chart")
    chart_window.geometry("800x600")
    chart_window.configure(bg=NAVY_BG)

    fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(projection='polar'))
    fig.patch.set_facecolor(NAVY_BG)
    ax.set_facecolor(NAVY_PANEL)

    stats_names = STAT_FIELDS
    stats_values = [current_pokemon[s] for s in stats_names]

    num_vars = len(stats_names)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    stats_values = stats_values + stats_values[:1]
    angles = angles + angles[:1]

    color = TYPE_COLORS.get(current_pokemon["Type 1"], "gray")

    ax.plot(angles, stats_values, 'o-', linewidth=2, color=color)
    ax.fill(angles, stats_values, alpha=0.25, color=color)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(stats_names, color='white', size=11)
    ax.set_ylim(0, max(stats_values) * 1.2)
    ax.set_title(f"{current_pokemon['Name']} Stats - Radar Chart",
                 fontsize=16, fontweight='bold', color='white', pad=20)
    ax.tick_params(colors='white')
    ax.grid(color='gray', alpha=0.3)

    canvas = FigureCanvasTkAgg(fig, chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


# Create chart buttons
themed_button(buttons_container, "Bar Chart", show_bar_chart).pack(pady=10)
themed_button(buttons_container, "Line Graph", show_line_graph).pack(pady=10)
themed_button(buttons_container, "Horizontal Bar Chart", show_horizontal_bar).pack(pady=10)
themed_button(buttons_container, "Radar Chart", show_radar_chart).pack(pady=10)


# Main functions
def show_loading():
    results_frame.pack_forget()
    loading_frame.pack(fill="both", expand=True)


def show_results():
    loading_frame.pack_forget()
    results_frame.pack(fill="both", expand=True)

    def on_mousewheel(event):
        stats_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    stats_canvas.bind_all("<MouseWheel>", on_mousewheel)


def display_pokemon(pokemon):
    global current_pokemon
    current_pokemon = pokemon

    # Fetch and display pokemon image
    try:
        pokemon_id = str(int(pokemon.get("#", 0)))
        pokemon_name = pokemon["Name"]

        # Fetch image (will use cache if available)
        img = fetch_pokemon_image(pokemon_id, pokemon_name)

        if img:
            # Resize and display
            img = img.resize((250, 250), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            pokemon_image_label.config(image=photo)
            pokemon_image_label.image = photo
        else:
            # Show placeholder text if image fetch failed
            pokemon_image_label.config(image="", text="Image not available",
                                       font=("Helvetica", 12), fg="#888888")
    except Exception as e:
        print(f"Error displaying image: {e}")
        pokemon_image_label.config(image="", text="Image not available",
                                   font=("Helvetica", 12), fg="#888888")

    # Update labels
    pokemon_name_label.config(text=pokemon["Name"])
    legendary_label.config(text="LEGENDARY POKÉMON" if pokemon["Legendary"] else "")
    type_label.config(text=f"Type: {pokemon['Type 1']}",
                      bg=TYPE_COLORS.get(pokemon["Type 1"], "gray"))

    total = sum(pokemon[s] for s in STAT_FIELDS)

    stats_text = (
        f"HP: {pokemon['HP']}\n\n"
        f"Attack: {pokemon['Attack']}\n\n"
        f"Defense: {pokemon['Defense']}\n\n"
        f"Speed: {pokemon['Speed']}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"Total Stats: {total}\n\n"
        f"Generation: {pokemon['Generation']}"
    )
    stats_text_label.config(text=stats_text)
    stats_canvas.yview_moveto(0)


def finish_loading(pokemon):
    display_pokemon(pokemon)
    show_results()
    status_label.config(text="")


def submit():
    search_name = entry.get().strip().lower()
    if not search_name:
        status_label.config(text="Please enter a Pokémon name", fg="#ffcc00")
        return

    # Partial match, take first result
    result = pokemon_df[pokemon_df["Name"].str.lower().str.contains(search_name, na=False)]

    if not result.empty:
        pokemon = result.iloc[0]
        show_loading()
        window.after(2000, lambda: finish_loading(pokemon))
    else:
        status_label.config(text="Pokémon not found", fg="#ff4444")


# Search button
search_button = tk.Button(search_frame, text="Search",
                          font=("Helvetica", 14, "bold"),
                          bg=NAVY_BTN, fg=TEXT, padx=30, pady=10,
                          relief="flat", cursor="hand2",
                          activebackground=NAVY_BTN_ACTIVE,
                          command=submit)
search_button.pack(pady=10)

# Bind enter key to search
window.bind("<Return>", lambda e: submit())

# Start the app
window.mainloop()