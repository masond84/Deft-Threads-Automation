"""
Allowed symbols for Threads posts
Based on coolsymbol.top and similar sources
"""
# Bullets and list markers
BULLETS = {
    "•": "•",  # Standard bullet
    "→": "→",  # Arrow
    "➤": "➤",  # Bold arrow
    "➜": "➜",  # Arrow variant
    "➤": "➤",  # Arrow
    "▶": "▶",  # Play arrow
    "▸": "▸",  # Small arrow
    "▪": "▪",  # Square bullet
    "▫": "▫",  # Square outline
    "◦": "◦",  # Circle outline
    "○": "○",  # Circle
    "◇": "◇",  # Diamond
    "◆": "◆",  # Filled diamond
    "★": "★",  # Star
    "☆": "☆",  # Star outline
    "✧": "✧",  # Star variant
    "✦": "✦",  # Sparkle
    "✩": "✩",  # Star variant
    "✪": "✪",  # Star variant
    "✫": "✫",  # Star variant
    "✬": "✬",  # Star variant
    "✭": "✭",  # Star variant
    "✮": "✮",  # Star variant
    "✯": "✯",  # Star variant
    "✰": "✰",  # Star variant
}

# Arrows
ARROWS = {
    "→": "→",
    "←": "←",
    "↑": "↑",
    "↓": "↓",
    "⇒": "⇒",
    "⇐": "⇐",
    "⇑": "⇑",
    "⇓": "⇓",
    "➤": "➤",
    "➜": "➜",
    "➨": "➨",
    "➩": "➩",
    "➪": "➪",
    "➫": "➫",
    "➬": "➬",
    "➭": "➭",
    "➮": "➮",
    "➯": "➯",
    "➱": "➱",
    "➲": "➲",
    "➳": "➳",
    "➴": "➴",
    "➵": "➵",
    "➶": "➶",
    "➷": "➷",
    "➸": "➸",
    "➹": "➹",
    "➺": "➺",
    "➻": "➻",
    "➼": "➼",
    "➽": "➽",
    "➾": "➾",
}

# Dividers and separators
DIVIDERS = {
    "─": "─",
    "━": "━",
    "│": "│",
    "┃": "┃",
    "┄": "┄",
    "┅": "┅",
    "┆": "┆",
    "┇": "┇",
    "┈": "┈",
    "┉": "┉",
    "┊": "┊",
    "┋": "┋",
    "┌": "┌",
    "┐": "┐",
    "└": "└",
    "┘": "┘",
    "├": "├",
    "┤": "┤",
    "┬": "┬",
    "┴": "┴",
    "┼": "┼",
}

# Decorative symbols
DECORATIVE = {
    "✧": "✧",
    "✦": "✦",
    "✩": "✩",
    "✪": "✪",
    "✫": "✫",
    "✬": "✬",
    "✭": "✭",
    "✮": "✮",
    "✯": "✯",
    "✰": "✰",
    "★": "★",
    "☆": "☆",
    "♡": "♡",
    "♥": "♥",
    "♦": "♦",
    "♣": "♣",
    "♠": "♠",
    "•": "•",
    "◦": "◦",
    "▪": "▪",
    "▫": "▫",
}

# Common symbols for lists
LIST_MARKERS = ["•", "→", "➤", "▸", "▪", "★", "✧", "✦"]

# All allowed symbols combined
ALLOWED_SYMBOLS = set(BULLETS.values()) | set(ARROWS.values()) | set(DIVIDERS.values()) | set(DECORATIVE.values())

def get_list_marker(index: int = 0) -> str:
    """Get a list marker symbol"""
    return LIST_MARKERS[index % len(LIST_MARKERS)]

def get_arrow(direction: str = "right") -> str:
    """Get an arrow symbol"""
    arrow_map = {
        "right": "→",
        "left": "←",
        "up": "↑",
        "down": "↓",
    }
    return arrow_map.get(direction.lower(), "→")