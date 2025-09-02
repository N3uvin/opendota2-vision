import pytesseract
from PIL import ImageGrab
import requests
import customtkinter
import re
import os
import sys
import threading
import time
from queue import Queue

# ------------------ CONFIG ------------------
# Path to your Tesseract executable - Update this path after installing Tesseract
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Default installation path: C:\Program Files\Tesseract-OCR\tesseract.exe
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Check if Tesseract is available
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    TESSERACT_AVAILABLE = True
else:
    TESSERACT_AVAILABLE = False
    print("Warning: Tesseract not found at", TESSERACT_PATH)
    print("Please install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")
    print("Or update the TESSERACT_PATH variable in the code.")

# Set dark theme for CustomTkinter
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

# OpenDota API base URL
API_URL = "https://api.opendota.com/api"

# ------------------ RESOURCE HELPER ------------------
def resource_path(rel_path: str) -> str:
    """Get absolute path to resource, works for dev and PyInstaller onefile."""
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, rel_path)

# ------------------ GUI ------------------
app = customtkinter.CTk()
app.geometry("500x400")
app.title("OpenDota Friend Stats")

# Set the window icon
try:
    import tkinter as tk
    app.iconphoto(True, tk.PhotoImage(file=resource_path("icon.png")))
except Exception as e:
    print(f"Could not load icon: {e}")
    # Continue without icon if there's an error

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
# Global variable for auto-scan timer
auto_scan_timer = None
last_detected_id = None  # Store the last detected Friend ID
scan_queue = Queue()  # Queue for scan results
scan_thread = None  # Background scan thread

def toggle_always_on_top():
    """Toggle always on top behavior"""
    app.attributes('-topmost', always_on_top_var.get())
    if always_on_top_var.get():
        print("Window set to always on top")
    else:
        print("Window no longer always on top")

def toggle_auto_scan():
    """Toggle auto-scanning on/off"""
    global auto_scan_timer
    
    if auto_scan_var.get():
        # Start auto-scanning
        start_auto_scan()
        label_status.configure(text="Auto-scanning enabled - searching for Friend IDs...", text_color="blue")
    else:
        # Stop auto-scanning
        stop_auto_scan()
        label_status.configure(text="Auto-scanning disabled", text_color="white")

def start_auto_scan():
    """Start the auto-scan timer"""
    global auto_scan_timer
    if auto_scan_timer is None:
        auto_scan_timer = app.after(1000, auto_scan_loop)  # 1 second

def stop_auto_scan():
    """Stop the auto-scan timer"""
    global auto_scan_timer
    if auto_scan_timer is None:
        return
    app.after_cancel(auto_scan_timer)
    auto_scan_timer = None

def auto_scan_loop():
    """Main auto-scan loop - schedules scans in background thread"""
    global auto_scan_timer
    
    if auto_scan_var.get():
        # Start scan in background thread
        start_background_scan()
        # Schedule next scan
        auto_scan_timer = app.after(1000, auto_scan_loop)  # 1 second

def start_background_scan():
    """Start OCR scanning in a background thread"""
    global scan_thread
    
    # Don't start new thread if one is already running
    if scan_thread and scan_thread.is_alive():
        return
    
    scan_thread = threading.Thread(target=background_scan_worker, daemon=True)
    scan_thread.start()

def background_scan_worker():
    """Background thread worker for OCR scanning"""
    if not TESSERACT_AVAILABLE:
        return
        
    try:
        # Take screenshot
        screenshot = ImageGrab.grab()
        
        # Try multiple OCR configurations for better accuracy
        configs = [
            '--oem 3 --psm 6',  # Assume uniform block of text
            '--oem 3 --psm 8',  # Single word
            '--oem 3 --psm 11', # Sparse text
            '--oem 1 --psm 6',  # Legacy engine
        ]
        
        steam_id = None
        
        for config in configs:
            try:
                text_result = pytesseract.image_to_string(screenshot, lang='eng', config=config)
                
                # Try multiple regex patterns for Friend ID
                patterns = [
                    r'FRIEND ID:\s*(\d{8,12})',  # "FRIEND ID: 12345678"
                    r'ID:\s*(\d{8,12})',  # "ID: 12345678"
                    r'Steam.*?(\d{8,12})',  # Near "Steam" text
                    r'\b(\d{8,12})\b',  # 8-12 digit numbers with word boundaries
                    r'(\d{8,12})',  # Just the numbers (fallback)
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text_result, re.IGNORECASE)
                    if match:
                        # Extract the actual ID number
                        if len(match.groups()) > 0:
                            steam_id = match.group(1)
                        else:
                            steam_id = match.group(0)
                        
                        # Validate the ID
                        if len(steam_id) >= 8 and len(steam_id) <= 12 and steam_id.isdigit():
                            print(f"Background scan found ID '{steam_id}' with config '{config}' and pattern '{pattern}'")
                            break
                
                if steam_id:
                    break
                    
            except Exception as e:
                print(f"Background scan error with config {config}: {e}")
                continue
        
        screenshot.close()
        
        if steam_id:
            scan_queue.put(('found_id', steam_id))
        else:
            scan_queue.put(('no_id', None))
        
    except Exception as e:
        print(f"Background scan error: {e}")
        scan_queue.put(('error', str(e)))

def process_scan_results():
    """Process scan results from background thread (called from main thread)"""
    global last_detected_id
    
    try:
        while not scan_queue.empty():
            result_type, data = scan_queue.get_nowait()
            
            if result_type == 'found_id':
                steam_id = data
                if steam_id != last_detected_id:
                    last_detected_id = steam_id
                    label_status.configure(text=f"Auto-scan found new Friend ID: {steam_id}", text_color="green")
                    fetch_opendota_stats(steam_id)
                else:
                    label_status.configure(text=f"Auto-scan: Friend ID {steam_id} still visible", text_color="blue")
            
            elif result_type == 'manual_found':
                steam_id = data
                label_status.configure(text=f"Found Friend ID: {steam_id}", text_color="green")
                fetch_opendota_stats(steam_id)
            
            elif result_type == 'manual_not_found':
                label_status.configure(text="Friend ID not found. Try adjusting screen or check if ID is visible.", text_color="red")
                winrate_label.configure(text="")
                hero_label.configure(text="")
            
            elif result_type == 'no_id':
                label_status.configure(text="No Friend ID found on screen", text_color="orange")
                winrate_label.configure(text="")
                hero_label.configure(text="")
                last_detected_id = None
            
            elif result_type in ('error', 'manual_error'):
                error_msg = data
                print(f"Scan error: {error_msg}")
                if result_type == 'manual_error':
                    label_status.configure(text=f"OCR Error: {error_msg}", text_color="red")
                    winrate_label.configure(text="")
                    hero_label.configure(text="")
        
        app.after(100, process_scan_results)
        
    except Exception as e:
        print(f"Error processing scan results: {e}")
        app.after(100, process_scan_results)

def auto_scan_screen():
    pass

def scan_screen():
    if not TESSERACT_AVAILABLE:
        label_status.configure(text="Tesseract not available. Please install it first.", text_color="red")
        return
        
    label_status.configure(text="Scanning screen...", text_color="white")
    app.update()
    
    manual_scan_thread = threading.Thread(target=manual_scan_worker, daemon=True)
    manual_scan_thread.start()

def manual_scan_worker():
    try:
        screenshot = ImageGrab.grab()
        
        configs = [
            '--oem 3 --psm 6',
            '--oem 3 --psm 8',
            '--oem 3 --psm 11',
            '--oem 1 --psm 6',
        ]
        
        steam_id = None
        
        for config in configs:
            try:
                text_result = pytesseract.image_to_string(screenshot, lang='eng', config=config)
                
                patterns = [
                    r'FRIEND ID:\s*(\d{8,12})',
                    r'ID:\s*(\d{8,12})',
                    r'Steam.*?(\d{8,12})',
                    r'\b(\d{8,12})\b',
                    r'(\d{8,12})',
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text_result, re.IGNORECASE)
                    if match:
                        if len(match.groups()) > 0:
                            steam_id = match.group(1)
                        else:
                            steam_id = match.group(0)
                        
                        if len(steam_id) >= 8 and len(steam_id) <= 12 and steam_id.isdigit():
                            print(f"Manual scan found ID '{steam_id}' with config '{config}' and pattern '{pattern}'")
                            break
                
                if steam_id:
                    break
                    
            except Exception as e:
                print(f"Manual scan error with config {config}: {e}")
                continue
        
        screenshot.close()
        
        if steam_id:
            scan_queue.put(('manual_found', steam_id))
        else:
            scan_queue.put(('manual_not_found', None))
        
    except Exception as e:
        print(f"Manual scan error: {e}")
        scan_queue.put(('manual_error', str(e)))

def fetch_opendota_stats(steam_id):
    try:
        matches = requests.get(f"{API_URL}/players/{steam_id}/recentMatches").json()
        if not matches:
            label_status.configure(text="No recent matches found.", text_color="red")
            winrate_label.configure(text="")
            hero_label.configure(text="")
            return

        total_games = len(matches)
        wins = sum(
            1
            for m in matches
            if ((m['player_slot'] < 128 and m['radiant_win'])
                or (m['player_slot'] >= 128 and not m['radiant_win']))
        )
        winrate = wins / total_games * 100

        hero_count = {}
        for m in matches:
            hero_id = m['hero_id']
            hero_count[hero_id] = hero_count.get(hero_id, 0) + 1

        top_hero_id = max(hero_count, key=hero_count.get)
        heroes_data = requests.get(f"{API_URL}/heroes").json()
        hero_dict = {h['id']: h['localized_name'] for h in heroes_data}
        top_hero_name = hero_dict.get(top_hero_id, str(top_hero_id))

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

# Auto-scan toggle
auto_scan_var = customtkinter.BooleanVar()
auto_scan_checkbox = customtkinter.CTkCheckBox(app, text="Auto-scan every 1 second", variable=auto_scan_var, command=toggle_auto_scan)
auto_scan_checkbox.pack(pady=5)

# Always on top toggle
always_on_top_var = customtkinter.BooleanVar(value=True)
always_on_top_checkbox = customtkinter.CTkCheckBox(app, text="Always on top", variable=always_on_top_var, command=toggle_always_on_top)
always_on_top_checkbox.pack(pady=2)

# Manual input section
manual_frame = customtkinter.CTkFrame(app)
manual_frame.pack(pady=10, padx=20, fill="x")

manual_label = customtkinter.CTkLabel(manual_frame, text="Or enter Friend ID manually:", font=("Arial", 12))
manual_label.pack(pady=(5,2))

manual_input = customtkinter.CTkEntry(manual_frame, placeholder_text="Enter 8-12 digit Friend ID")
manual_input.pack(pady=2, padx=20, fill="x")

def manual_submit():
    steam_id = manual_input.get().strip()
    if not steam_id:
        label_status.configure(text="Please enter a Friend ID", text_color="red")
        return
    if not steam_id.isdigit() or len(steam_id) < 8 or len(steam_id) > 12:
        label_status.configure(text="Invalid Friend ID format (8-12 digits)", text_color="red")
        return
    label_status.configure(text=f"Using manual Friend ID: {steam_id}", text_color="green")
    manual_input.delete(0, 'end')
    fetch_opendota_stats(steam_id)

manual_button = customtkinter.CTkButton(manual_frame, text="Submit", command=manual_submit, width=100)
manual_button.pack(pady=5)

# Status bar at bottom
status_bar = customtkinter.CTkFrame(app, height=25)
status_bar.pack(side="bottom", fill="x", padx=5, pady=2)

if TESSERACT_AVAILABLE:
    status_text = "✓ Tesseract OCR Ready"
    status_color = "green"
else:
    status_text = "✗ Tesseract OCR Not Found - Please install Tesseract"
    status_color = "red"

status_label = customtkinter.CTkLabel(status_bar, text=status_text, font=("Arial", 10), text_color=status_color)
status_label.pack(side="left", padx=10, pady=2)

# Cleanup function for auto-scan timer
def on_closing():
    stop_auto_scan()
    app.destroy()

app.protocol("WM_DELETE_WINDOW", on_closing)

# Start the result processing system
process_scan_results()

# Set initial always on top state
app.attributes('-topmost', True)

app.mainloop()
