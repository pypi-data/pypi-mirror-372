EMOJI_MAP = {
    # Emotions
    "happy": "😊",
    "sad": "😢",
    "angry": "😠",
    "love": "❤️",
    "excited": "🤩",
    "bored": "😐",
    "tired": "😴",
    "surprised": "😲",
    "confused": "😕",
    "nervous": "😬",
    "shocked": "😱",
    "cool": "😎",
    "party": "🥳",
    "cry": "😭",
    "laugh": "😂",
    "wink": "😉",
    "smile": "😃",

    # Objects
    "fire": "🔥",
    "star": "⭐",
    "sun": "☀️",
    "moon": "🌙",
    "cloud": "☁️",
    "rain": "🌧️",
    "snow": "❄️",
    "tree": "🌳",
    "flower": "🌸",
    "coffee": "☕",
    "cake": "🎂",

    # Actions
    "ok": "👌",
    "clap": "👏",
    "thumbs_up": "👍",
    "thumbs_down": "👎",
    "pray": "🙏",
    "run": "🏃",
    "walk": "🚶",
    "sleep": "😴",
    "eat": "🍽️",
    "drink": "🥤",

    # Animals
    "dog": "🐶",
    "cat": "🐱",
    "lion": "🦁",
    "tiger": "🐯",
    "monkey": "🐵",
    "rabbit": "🐰",
    "panda": "🐼",
    "bear": "🐻",

    # Misc
    "money": "💰",
    "gift": "🎁",
    "phone": "📱",
    "laptop": "💻",
    "music": "🎵",
    "camera": "📷",
    "soccer": "⚽",
    "basketball": "🏀",
}


def text_to_emoji(text: str) -> str:
    """
    Replace words in text with emojis.
    """
    words = text.split()
    new_words = [EMOJI_MAP.get(word.lower(), word) for word in words]
    return " ".join(new_words)
