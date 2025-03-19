# Text-to-Speech App

## Overview
This is a lightweight and efficient text-to-speech (TTS) desktop application that allows you to read any selected text aloud with just a hotkey. It's designed for ease of use, offering quick access via a system tray and customizable settings for TTS speed and voice.

---

## Features
- **Quick TTS Access**: Select any text and press `Ctrl + Insert` to hear it read aloud, press `Ctrl + End` to stop
- **Customizable Settings**: 
  - Adjust words per minute (WPM) for TTS playback.
  - Choose from available system voices.
- **File Saving**: Automatically saves the last spoken text into a `.txt` file for easy reference.
- **System Tray Integration**: 
  - Access settings, restart the app, or quit directly from the tray menu.
- **Lightweight and Non-Intrusive**: Runs quietly in the background.
  
---

## Requirements
- Python 3.7 or later
- Libraries: 
  - `pyautogui`
  - `pyperclip`
  - `keyboard`
  - `pyttsx3`
  - `pystray`
  - `Pillow`
  - `tkinter`

Install required libraries with:
```bash
pip install pyautogui pyperclip keyboard pyttsx3 pystray pillow
