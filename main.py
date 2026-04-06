"""
Jarvis — point d'entrée principal.
Lance l'écoute en boucle et orchestre les modules.
"""

from listener import wait_for_clap
from voice import listen_speech, speak
from claude_client import ask_claude
from launcher import handle_command
import config


def main():
    print("Jarvis en écoute... (double clap pour activer)")
    while True:
        # 1. Attendre le signal d'activation (clap)
        wait_for_clap()

        speak("Oui ?")

        # 2. Écouter la commande vocale
        text = listen_speech(timeout=config.SILENCE_TIMEOUT)
        if not text:
            speak("Je n'ai rien entendu.")
            continue

        print(f"[Vous] {text}")

        # 3. Vérifier si c'est une commande d'application
        handled = handle_command(text)
        if handled:
            continue

        # 4. Sinon, envoyer à Claude
        response = ask_claude(text)
        print(f"[Jarvis] {response}")
        speak(response)


if __name__ == "__main__":
    main()
