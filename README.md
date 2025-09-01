# OPENDOTA2-VISION

Python script for analyzing Dota 2 player stats and detecting potential smurfs.

---

## Features
- Detects potential smurfs by analyzing recent matches
- Tracks most played heroes
- Calculates winrate for last matches
- Simple GUI to display results

---


## ⚠️ Important Note
This script **works only in BORDERLESS WINDOW MODE** in Dota 2.

# SHOWCASE
<img width="1153" height="672" alt="123" src="https://github.com/user-attachments/assets/477ce8e5-2156-4588-b118-f088456bfe55" />

## Example: OCR Limitations

Sometimes the script cannot detect Friend ID correctly if the background is too busy or the text is not visible.
<img width="1103" height="644" alt="222" src="https://github.com/user-attachments/assets/1e88b3a0-70cc-4b37-a4af-e64ef8aeace8" />

# Dependencies

1: Install dependencies:

`pip install -r requirements.txt`

2: Install Tesseract-OCR:

https://github.com/UB-Mannheim/tesseract/wiki


3: Set the path to Tesseract in dota2.py **if needed**:

`pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'`


# USAGE
`python dota2.py`
