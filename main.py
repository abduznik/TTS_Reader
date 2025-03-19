import pyautogui as pya
import pyperclip
import time
import keyboard
import pyttsx3
import threading
import queue
import pystray
from PIL import Image
from pystray import MenuItem, Icon
import tkinter as tk
from tkinter import ttk
import os
import sys
import json

# Global variables
last_saved_file = ""
tts_speed = 150  # Default TTS speed
selected_voice = None
voices = []
tts_queue = queue.Queue()  # Queue for text-to-speech requests
tts_thread_running = False  # Flag to indicate TTS thread status
settings_file_path = os.path.join(os.getenv("LOCALAPPDATA"), "Voice_settings.txt")  # File path for settings

# Initialize the TTS engine
engine = pyttsx3.init()

# Function to load settings
def load_settings():
    global tts_speed, selected_voice
    if os.path.exists(settings_file_path):
        try:
            with open(settings_file_path, "r") as file:
                settings = json.load(file)
                tts_speed = settings.get("speed", 150)
                selected_voice = settings.get("voice", None)
                if selected_voice:
                    engine.setProperty('voice', selected_voice)
        except Exception as e:
            print(f"Error loading settings: {e}")

# Function to save settings
def save_settings():
    global tts_speed, selected_voice
    settings = {
        "speed": tts_speed,
        "voice": selected_voice
    }
    try:
        with open(settings_file_path, "w") as file:
            json.dump(settings, file)
    except Exception as e:
        print(f"Error saving settings: {e}")

def tts_worker():
    """Thread worker function to process TTS requests sequentially."""
    global tts_thread_running
    tts_thread_running = True
    while tts_thread_running:
        try:
            text = tts_queue.get(timeout=0.1)  # Wait for text to process
            if text is None:  # Sentinel value to stop the thread
                break
            engine.setProperty('rate', tts_speed)
            if selected_voice:
                engine.setProperty('voice', selected_voice)
            engine.say(text)
            engine.runAndWait()
        except queue.Empty:
            continue
        except Exception as e:
            print(f"TTS Error: {e}")

def start_tts_thread():
    """Start the dedicated TTS thread."""
    threading.Thread(target=tts_worker, daemon=True).start()

def stop_tts_thread():
    """Stop the TTS thread."""
    global tts_thread_running
    tts_thread_running = False
    tts_queue.put(None)  # Add sentinel value to stop the thread

def speak_text(text):
    """Queue text for speaking."""
    tts_queue.put(text)

def copy_clipboard():
    """Copy selected text to the clipboard."""
    pyperclip.copy("")  # Clear the clipboard to ensure proper copying
    pya.hotkey('ctrl', 'c')
    time.sleep(0.1)  # Allow time for the copy operation
    return pyperclip.paste()

def copy_selected_text():
    """Copy selected text and queue it for TTS."""
    copied_text = copy_clipboard()
    if copied_text:
        global last_saved_file
        # Save the copied text to a file
        last_saved_file = os.path.join(os.path.expanduser("~"), "last_copied_text.txt")
        with open(last_saved_file, "w") as f:
            f.write(copied_text)  # Save copied text to a txt file
        speak_text(copied_text)  # Add text to TTS queue

def on_ctrl_insert():
    """Handler for the Ctrl + Insert hotkey."""
    copy_selected_text()

def on_ctrl_end():
    stop_tts_thread()
    time.sleep(0.1)
    start_tts_thread()

def open_last_saved_txt():
    """Open the last saved text file."""
    if last_saved_file and os.path.exists(last_saved_file):
        os.startfile(last_saved_file)
    else:
        print("No last saved text file found.")

def update_speed(speed):
    """Update TTS speed."""
    global tts_speed
    tts_speed = speed
    save_settings()  # Save updated speed to settings
    speak_text("TTS speed updated.")

def change_voice(voice):
    """Change the TTS voice."""
    global selected_voice
    selected_voice = voice
    save_settings()  # Save updated voice to settings
    speak_text("Voice changed.")

def open_settings():
    """Open settings window."""
    global voices
    voices = engine.getProperty('voices')

    settings_window = tk.Tk()
    settings_window.title("Settings")
    settings_window.geometry("400x400")
    settings_window.configure(bg="#2E2E2E")

    tk.Label(settings_window, text="Instructions:\n"
                                    "1. Select text and press Ctrl + Insert to copy and read aloud\n Ctrl + End to stop\n"
                                    "2. Adjust TTS speed or select voice in the options below.",
             bg="#2E2E2E", fg="white").pack(pady=20)

    tk.Label(settings_window, text="Select TTS Speed", bg="#2E2E2E", fg="white").pack(pady=10)
    speed_var = tk.StringVar(value=str(tts_speed))
    speed_options = [100, 150, 200, 250]
    for speed in speed_options:
        rb = tk.Radiobutton(settings_window, text=f"{speed} WPM", variable=speed_var, value=str(speed),
                            bg="#2E2E2E", fg="white", selectcolor="#3E3E3E",
                            command=lambda s=int(speed_var.get()): update_speed(s))
        rb.pack(anchor='w', padx=20)

    tk.Label(settings_window, text="Select Voice", bg="#2E2E2E", fg="white").pack(pady=20)
    voice_combobox = ttk.Combobox(settings_window, values=[voice.name for voice in voices])
    if selected_voice:
        voice_names = [voice.id for voice in voices]
        if selected_voice in voice_names:
            voice_combobox.current(voice_names.index(selected_voice))
    voice_combobox.pack(pady=10)
    voice_combobox.bind("<<ComboboxSelected>>", lambda event: change_voice(voices[voice_combobox.current()].id))

    tk.Button(settings_window, text="Close", command=settings_window.destroy).pack(pady=20)
    settings_window.mainloop()

def restart_app(icon, item):
    """Restart the application."""
    icon.stop()
    os.execv(sys.executable, ['python'] + sys.argv)

def quit_app(icon, item):
    """Quit the application."""
    stop_tts_thread()
    icon.stop()
#Important for icon_path and loading the icon
def resource(relative_path):
    base_path = getattr(
        sys,
        '_MEIPASS',
        os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
    
# Check for icon
icon_path = resource("icon.png")
icon_image = Image.open(icon_path) if os.path.exists(icon_path) else Image.new('RGBA', (64, 64), (255, 255, 255, 0))

# Create tray menu
menu = (
    MenuItem('Open Last Saved Text File', open_last_saved_txt),
    MenuItem('Settings', open_settings),
    MenuItem('Restart', restart_app),
    MenuItem('Quit', quit_app)
)
icon = Icon("TextToSpeech", icon_image, "Text to Speech App", menu)

# Load settings
load_settings()

# Start the TTS thread and tray icon
start_tts_thread()
keyboard.add_hotkey('ctrl + insert', on_ctrl_insert)
keyboard.add_hotkey('ctrl + end', on_ctrl_end)
icon.run()
