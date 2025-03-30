import hashlib
from urllib.parse import urlparse


class TextProcessor:
    """Text processing utilities."""

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        text = " ".join(text.split())
        text = "".join(char for char in text if char.isprintable())
        return text.strip()

    @staticmethod
    def hash_text(text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()

    @staticmethod
    def validate_url(url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
