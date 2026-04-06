"""
claude_client.py — interface avec l'API Anthropic (Claude).
Maintient un historique de conversation pour le contexte.
"""

import anthropic
import config


_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

# Historique de la conversation courante (réinitialisé au redémarrage)
_history: list[dict] = []

SYSTEM_PROMPT = (
    "Tu es Jarvis, un assistant vocal personnel. "
    "Tu réponds en français, de façon concise et directe (2-3 phrases max). "
    "Pas de markdown, pas de listes — tu parles, pas tu écris."
)


def ask_claude(user_message: str) -> str:
    """Envoie un message à Claude et retourne la réponse texte."""
    _history.append({"role": "user", "content": user_message})

    response = _client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=config.MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=_history,
    )

    reply = response.content[0].text
    _history.append({"role": "assistant", "content": reply})
    return reply


def reset_conversation():
    """Efface l'historique pour démarrer une nouvelle conversation."""
    _history.clear()
