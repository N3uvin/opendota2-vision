import pytesseract
from PIL import ImageGrab
import requests
import customtkinter
import re

# ------------------ CONFIG ------------------
# Path to your Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Set dark theme for CustomTkinter
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

# OpenDota API base URL
API_URL = "https://api.opendota.com/api"

# ------------------ GUI ------------------
app = customtkinter.CTk()
app.geometry("450x250")
app.title("OpenDota Friend Stats")

# Status label
label_status = customtkinter.CTkLabel(app, text="Press 'Scan Screen' to find Friend ID", font=("Arial", 14))
label_status.pack(pady=(10,5))

# Winrate label
winrate_label = customtkinter.CTkLabel(app, text="", font=("Arial", 16))
winrate_label.pack(pady=5)

# Top hero label
hero_label = customtkinter.CTkLabel(app, text="", font=("Arial", 16))
hero_label.pack(pady=5)

# ------------------ FUNCTIONS ------------------
def scan_screen():
    """
    Takes a screenshot of the entire screen, uses OCR to detect numeric Friend ID,
    and fetches OpenDota stats if ID is found.
    """
    label_status.configure(text="Scanning screen...", text_color="white")
    app.update()
    
    # Take screenshot
    screenshot = ImageGrab.grab()
    text_result = pytesseract.image_to_string(screenshot, lang='eng')
    screenshot.close()

    # Search for numeric Friend ID (adjust regex if needed)
    match = re.search(r'\b\d{8,12}\b', text_result)
    if not match:
        label_status.configure(text="Friend ID not found on screen.", text_color="red")
        winrate_label.configure(text="")
        hero_label.configure(text="")
        return

    steam_id = match.group()
    label_status.configure(text=f"Found Friend ID: {steam_id}", text_color="green")
    app.update()
    fetch_opendota_stats(steam_id)

def fetch_opendota_stats(steam_id):
    """
    Fetches last 15 matches from OpenDota API, calculates winrate,
    and finds the most played hero.
    """
    try:
        # Get last 15 matches
        matches = requests.get(f"{API_URL}/players/{steam_id}/recentMatches").json()
        if not matches:
            label_status.configure(text="No recent matches found.", text_color="red")
            winrate_label.configure(text='Account may be private.')
            hero_label.configure(text='')
            return

        total_games = len(matches)

        # ------------------ Win calculation ------------------
        # Count wins by checking team and match outcome
        # player_slot < 128 --> Radiant, >= 128 --> Dire
        wins = sum(
            1  # Add 1 for each match where the player won
            for m in matches
            if (
                # Case 1: Player was Radiant and Radiant won
                (m['player_slot'] < 128 and m['radiant_win'])
                # Case 2: Player was Dire and Radiant lost (Dire won)
                or (m['player_slot'] >= 128 and not m['radiant_win'])
            )
        )

        winrate = wins / total_games * 100  # Winrate in percentage

        # ------------------ Top hero calculation ------------------
        # Count the number of games played on each hero
        hero_count = {}
        for m in matches:
            hero_id = m['hero_id']
            hero_count[hero_id] = hero_count.get(hero_id, 0) + 1

        # Find the hero with the most games
        max_count = 0
        top_hero_id = None
        for hero_id, count in hero_count.items():
            if count > max_count:
                max_count = count
                top_hero_id = hero_id

        # Get hero names from OpenDota
        heroes_data = requests.get(f"{API_URL}/heroes").json()
        hero_dict = {h['id']: h['localized_name'] for h in heroes_data}
        top_hero_name = hero_dict.get(top_hero_id, str(top_hero_id))

        # ------------------ Update GUI ------------------
        winrate_label.configure(text=f"Winrate (last {total_games} games): {winrate:.1f}%")
        winrate_label.configure(text_color="green" if winrate >= 50 else "red")
        hero_label.configure(text=f"Top Hero: {top_hero_name} ({hero_count[top_hero_id]} games)")
        label_status.configure(text="Data fetched successfully", text_color="white")

    except Exception as e:
        label_status.configure(text=f"Error fetching data: {e}", text_color="red")
        winrate_label.configure(text="")
        hero_label.configure(text="")

# Button to start the process
button_scan = customtkinter.CTkButton(app, text="Scan Screen", command=scan_screen)
button_scan.pack(pady=10)

app.mainloop()
