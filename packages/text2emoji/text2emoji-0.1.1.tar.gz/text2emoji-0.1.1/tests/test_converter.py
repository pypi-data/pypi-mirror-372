from text2emoji import text_to_emoji

def test_basic_conversion():
    assert text_to_emoji("I am happy") == "I am 😊"
    assert text_to_emoji("fire and love") == "🔥 and ❤️"
