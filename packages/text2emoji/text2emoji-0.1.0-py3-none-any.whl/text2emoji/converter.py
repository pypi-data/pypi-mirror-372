EMOJI_MAP = {
    "happy": "😊",
    "sad": "😢",
    "love": "❤️",
    "fire": "🔥",
    "star": "⭐",
    "ok": "👌",
    "laugh": "😂",
    "angry": "😠",
}

def text_to_emoji(text: str) -> str:
    """
    Replace words in text with emojis.
    """
    words = text.split()
    new_words = [EMOJI_MAP.get(word.lower(), word) for word in words]
    return " ".join(new_words)
