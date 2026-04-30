"""Terminal color and styling utilities."""


class Style:
    """ANSI escape codes for styling."""
    # Colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    
    # Reset
    RESET = "\033[0m"


def color(text: str, *codes: str) -> str:
    """Apply color codes to text."""
    return "".join(codes) + text + Style.RESET


def success(text: str) -> str:
    """Green success text."""
    return color(text, Style.GREEN)


def error(text: str) -> str:
    """Red error text."""
    return color(text, Style.RED, Style.BOLD)


def warning(text: str) -> str:
    """Yellow warning text."""
    return color(text, Style.YELLOW)


def info(text: str) -> str:
    """Blue info text."""
    return color(text, Style.CYAN)


def muted(text: str) -> str:
    """Dimmed text for secondary info."""
    return color(text, Style.DIM)


def bold(text: str) -> str:
    """Bold text."""
    return color(text, Style.BOLD)


# Icons
ICON_CHECK = color("✓", Style.GREEN, Style.BOLD)
ICON_CROSS = color("✗", Style.RED, Style.BOLD)
ICON_WARNING = color("⚠", Style.YELLOW, Style.BOLD)
ICON_ARROW = color("→", Style.CYAN)
ICON_BOLT = color("⚡", Style.BRIGHT_YELLOW, Style.BOLD)
ICON_GEAR = color("⚙", Style.BLUE)
