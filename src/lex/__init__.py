"""LEX stream cipher (eSTREAM Phase 3, LEX-128) bằng Python thuần. Chỉ dùng cho học tập."""
from .lex.api import LEX, decrypt, encrypt

__all__ = ["LEX", "encrypt", "decrypt"]
__version__ = "1.0.0"
