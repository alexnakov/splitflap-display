FPS = 60
BG_COLOR = (10, 12, 14)
BOARD_COLOR = (18, 20, 24)
SLOT_COLOR = (8, 9, 10)
TEXT_COLOR = (230, 232, 235)
ACCENT = (40, 48, 56)

# Character set typical of split-flap boards
CHARSET = r" ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,-/'#:%°"
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
# --- Physical monitor dimensions (mm) ---
MONITOR_WIDTH_MM  = 612.3
MONITOR_HEIGHT_MM = 366.5

# --- Actual screen resolution (adjust to your monitor) ---
SCREEN_W = 1920
SCREEN_H = 1080

# --- Derived pixel density ---
PX_PER_MM = SCREEN_W / MONITOR_WIDTH_MM

# --- Base layout design ---
CELL_W = 20
CELL_H = int(CELL_W * (64 / 36))
CELL_GAP = 3
TOP_MARGIN = 40
LEFT_MARGIN = 20
ROWS = 6
COLS = 22

# --- Compute scaling to fit display ---
BOARD_W = COLS * CELL_W + (COLS - 1) * CELL_GAP + LEFT_MARGIN * 2
BOARD_H = ROWS * CELL_H + (ROWS - 1) * CELL_GAP + TOP_MARGIN

SCALE_W = SCREEN_W / BOARD_W
SCALE_H = SCREEN_H / BOARD_H
SCALE = min(SCALE_W, SCALE_H)

# --- Apply scaling ---
CELL_W = int(CELL_W * SCALE)
CELL_H = int(CELL_H * SCALE)
CELL_GAP = int(CELL_GAP * SCALE)
TOP_MARGIN = int(TOP_MARGIN * SCALE)
LEFT_MARGIN = int(LEFT_MARGIN * SCALE)


# Animation timings (seconds)
FLIP_CLOSE_TIME = 0.062   # top half folding down
FLIP_OPEN_TIME = 0.052    # bottom half opening to reveal next
INTER_FLAP_DELAY = 0.039  # cascade delay between neighboring cells

TOGGLE_PERIOD = 100.0 # Keeping super high for testing

GHOST_TIMER = 60 * 1 # 1 min
FULLBOARD_REFRESH_TIMER = 60 * 12 # 8 mins
REFRESH_DELAY = 9
MINUTE_UPDATE_TIMER = 60

GHOST_PROBABILITY = 0.017