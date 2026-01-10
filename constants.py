FPS = 60
BG_COLOR = (10, 12, 14)
BOARD_COLOR = (18, 20, 24)
SLOT_COLOR = (8, 9, 10)
TEXT_COLOR = (230, 232, 235)
ACCENT = (40, 48, 56)

CHARSET = r" ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,-/'#:%°"
CHAR_INDEX = {c: i for i, c in enumerate(CHARSET)}

# --- Actual screen resolution (adjust to your monitor) ---
SCREEN_W = 1920
SCREEN_H = 1080

# --- Base layout design ---
CELL_W = 55
CELL_H = int(CELL_W * (64 / 36))
CELL_GAP = 6
TOP_MARGIN = 20
LEFT_MARGIN = 20
ROWS = 6
COLS = 22

# --- Compute scaling to fit display ---
BOARD_W = COLS * CELL_W + (COLS - 1) * CELL_GAP + LEFT_MARGIN * 2
BOARD_H = ROWS * CELL_H + (ROWS - 1) * CELL_GAP + TOP_MARGIN

# Animation timings (seconds)
FLIP_CLOSE_TIME = 0.062   # top half folding down
FLIP_OPEN_TIME = 0.052    # bottom half opening to reveal next
INTER_FLAP_DELAY = 0.039  # cascade delay between neighboring cells

TOGGLE_PERIOD = 100.0 # Keeping super high for testing

GHOST_TIMER = 60 * 1 # 1 min
FULLBOARD_REFRESH_TIMER = 60 * 5
REFRESH_DELAY = 9 # For the bottom row refreshing
MINUTE_UPDATE_TIMER = 60

GHOST_PROBABILITY = 0.017