
SCREEN_W, SCREEN_H = 1200, 720
FPS = 60
BG_COLOR = (10, 12, 14)
BOARD_COLOR = (18, 20, 24)
SLOT_COLOR = (8, 9, 10)
TEXT_COLOR = (230, 232, 235)
ACCENT = (40, 48, 56)

# Character set typical of split-flap boards
CHARSET = " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-/'#:"
CHAR_INDEX = {c: i for i, c in enumerate(CHARSET)}

SOUND_PATH = "./audio/single-flap.mp3"

# Demo texts (must be same length for best effect; will be padded)
TEXT_A = [
    "NEW YORK  JFK  AA123 ",
    "BOSTON     BOS  DL987",
    "CHICAGO    ORD  UA452",
    "LOS ANGELES LAX SW330",
    "SEATTLE    SEA  AS808",
    "MIAMI      MIA  AA455",
]
TEXT_B = [
    "SAN DIEGO  SAN UA987 ",
    "ATLANTA    ATL DL204",
    "DALLAS     DFW AA540",
    "DENVER     DEN UA311",
    "PHOENIX    PHX SW209",
    "LAS VEGAS  LAS NK701",
]

# Board / cell sizing
CELL_W = 36
CELL_H = 64
CELL_GAP = 6
TOP_MARGIN = 80
LEFT_MARGIN = 40

ROWS = 6
COLS = 22

# Animation timings (seconds)
FLIP_CLOSE_TIME = 0.035   # top half folding down
FLIP_OPEN_TIME = 0.045    # bottom half opening to reveal next
INTER_FLAP_DELAY = 0.027  # cascade delay between neighboring cells

TOGGLE_PERIOD = 100.0 # Keeping super high for testing
GHOST_TIMER = 15
WAVE_TIMER = 100000
REFRESH_TIMER = 60 * 7 # 7 mins