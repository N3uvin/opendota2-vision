OPENDOTA2-VISION
I’m open to feedback, feature suggestions, or any ideas to improve the script!

Python script for analyzing Dota 2 player stats and detecting potential smurfs.

Features
Detects potential smurfs by analyzing recent matches
Tracks most played heroes
Calculates winrate for last matches
Simple GUI to display results
⚠️ Important Note
This script works only in BORDERLESS WINDOW MODE in Dota 2.

⚙️ Note: This script requires Python to run. If there’s enough interest, I plan to release a standalone .exe version for easier use.

SHOWCASE
<img width="1153" height="672" alt="Снимок экрана 2025-09-01 182734" src="https://github.com/user-attachments/assets/c97ccfdf-367a-48e0-8794-9a3a7052f127" />


Example: OCR Limitations
Sometimes the script cannot detect Friend ID correctly if the background is too busy or the text is not visible. 222
<img width="1103" height="580" alt="Снимок экрана 2025-09-01 183045" src="https://github.com/user-attachments/assets/b5a1b13b-c4c0-4ae1-abcc-9125eae75916" />

Dependencies
1: Install dependencies:

pip install -r requirements.txt

2: Install Tesseract-OCR:

https://github.com/UB-Mannheim/tesseract/wiki

3: Set the path to Tesseract in dota2.py if needed:

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

USAGE
python dota2.py
