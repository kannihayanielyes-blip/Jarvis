"""
launcher.py — détection et exécution de commandes applicatives.
Analyse le texte pour ouvrir des apps ou des URLs sans passer par Claude.
"""

import subprocess
import webbrowser
import config


# Mots-clés → action
_COMMANDS = {
    "claude": ["ouvre claude", "lance claude", "open claude"],
    "obsidian": ["ouvre obsidian", "lance obsidian", "open obsidian"],
    "spotify": ["lance spotify", "mets de la musique", "joue de la musique", "musique"],
}


def handle_command(text: str) -> bool:
    """
    Analyse le texte et exécute une commande si reconnue.
    Retourne True si une commande a été traitée, False sinon.
    """
    text_lower = text.lower()

    if _matches(text_lower, _COMMANDS["claude"]):
        _open_app(config.CLAUDE_EXE_PATH, "Claude")
        return True

    if _matches(text_lower, _COMMANDS["obsidian"]):
        _open_app(config.OBSIDIAN_EXE_PATH, "Obsidian")
        return True

    if _matches(text_lower, _COMMANDS["spotify"]):
        _open_url(config.SPOTIFY_PLAYLIST_URL, "Spotify")
        return True

    return False


def _matches(text: str, keywords: list[str]) -> bool:
    return any(kw in text for kw in keywords)


def _open_app(path: str, name: str):
    from voice import speak
    try:
        subprocess.Popen([path])
        speak(f"{name} lancé.")
    except FileNotFoundError:
        speak(f"Je ne trouve pas {name}. Vérifie le chemin dans config.py.")
    except Exception as e:
        speak(f"Impossible de lancer {name}.")
        print(f"[launcher] Erreur : {e}")


def _open_url(url: str, name: str):
    from voice import speak
    webbrowser.open(url)
    speak(f"{name} ouvert.")
