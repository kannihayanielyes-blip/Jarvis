import os
from dotenv import load_dotenv

load_dotenv()

# --- API ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# --- Détection clap ---
CLAP_THRESHOLD = 0.05      # sensibilité : 0.0 (tout capte) → 1.0 (très strict)
SILENCE_TIMEOUT = 10       # secondes d'inactivité avant de clore la conversation

# --- Chemins applicatifs Windows ---
CLAUDE_EXE_PATH = r"C:\Users\elyes\AppData\Local\AnthropicClaude\claude.exe"
OBSIDIAN_EXE_PATH = r"C:\Users\elyes\AppData\Local\Obsidian\Obsidian.exe"

# --- Spotify ---
SPOTIFY_PLAYLIST_URL = "https://open.spotify.com/playlist/[ton-id]"

# --- Modèle Claude ---
CLAUDE_MODEL = "claude-opus-4-6"
MAX_TOKENS = 1024
