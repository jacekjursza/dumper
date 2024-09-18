# config.py

import os

# Definiowanie katalogu bazowego dla projektów
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "projects")

# Upewnienie się, że katalog istnieje
os.makedirs(BASE_DIR, exist_ok=True)
