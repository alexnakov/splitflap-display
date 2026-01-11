# 🧭 User Guide – Tweaking the Digital Solari Board

This guide explains how to **modify the code and instantly see visual or behavioral changes** in the split‑flap display. It is written for developers who want to experiment, customize, or extend the project.

---

## 🧩 Project Structure (Relevant Files)

```text
main.py          # Application entry point & animation logic
constants.py     # All tunable visual + timing parameters
weather.py       # Weather + location data source
fonts/           # Display font
audio/           # Flip sound effects
```

👉 **Most customization happens in `constants.py`.**

---

## 🎨 Visual Customization

### 1. Change the Overall Style (Live Toggle)

While the app is running, press:

- **`D`** → cycle styles: `classic → matte → retro → paper`

Internally, this updates:

```python
SplitFlap.STYLE = "classic"
```

Each style affects:

- Bezel color
- Shadows
- Highlight reflections
- Hinge animation

---

### 2. Colors (constants.py)

```python
BG_COLOR = (18, 20, 24)
SLOT_COLOR = (38, 40, 44)
ACCENT = (90, 95, 100)
```

Try:

- Warmer tones for a vintage look
- Higher contrast for readability
- Darker BG for a cinema-style display

💡 **Save the file and restart the app** to see changes.

---

### 3. Font & Character Appearance

In `main.py`:

```python
self.font = pygame.font.Font("fonts/DINMittelschriftStd.otf", 64)
```

You can:

- Change font size (e.g. `48`, `72`)
- Swap fonts (ensure monospace for best alignment)

Each flap also has a vertical offset:

```python
self.v_offset = 12
```

Adjust this if characters appear too high or low.

---

## ⏱️ Animation Tuning

### Flip Speed (constants.py)

```python
FLIP_CLOSE_TIME = 0.08
FLIP_OPEN_TIME  = 0.10
INTER_FLAP_DELAY = 0.02
```

Examples:

- **Slower, cinematic** → increase times
- **Snappier, mechanical** → decrease times

---

### Ghost Flips (Ambient Motion)

Ghost flips simulate mechanical randomness.

```python
GHOST_PROBABILITY = 0.003
GHOST_TIMER = 6.0
```

Press **`G`** while running to trigger ghost flips manually.

---

## 🌍 Cities & Weather Data

Cities are defined in `weather.py`:

```python
WEATHER_LOCATIONS = [
  {"key": "LONDON", ...},
  {"key": "CHICAGO", ...},
]
```

The board cycles automatically based on:

```python
FULLBOARD_REFRESH_TIMER
```

To test without API calls:

```bash
python main.py --mock-weather
```

---

## 🕒 Time Display Logic

The local time display updates **one minute at a time** without re-flipping the entire row.

See:

```python
App.increment_minute()
```

This method:

- Reads characters directly from flaps
- Computes next minute
- Flips only changed digits

💡 You can reuse this logic for **countdowns, clocks, or timers**.

---

## ⌨️ Keyboard Controls

| Key       | Action              |
| --------- | ------------------- |
| `D`       | Cycle visual styles |
| `G`       | Trigger ghost flips |
| `C`       | Force city refresh  |
| `SPACE`   | Toggle board state  |
| `ESC / Q` | Quit                |

---

## 🔊 Sound Design

Flip sounds are loaded here:

```python
self.click_sounds = [pygame.mixer.Sound("./audio/sf-1.mp3")]
```

Volume is controlled via:

```python
self.click_sounds[0].set_volume(0.05)
```

Try layering multiple sounds for richer mechanical depth.

---

## 🧪 Safe Experiments to Try

- Change `COLS` and `ROWS` to resize the board
- Add a new city to `WEATHER_LOCATIONS`
- Increase font size and reduce rows for a departure-board look
- Disable sound for silent installations

---

## 📤 Where to Publish This Guide

Recommended options:

1. **GitHub (Best)**

   - Keep this as `USER_GUIDE.md`
   - Link it from `README.md`

2. **GitHub Wiki**

   - Ideal for future expansion
   - Supports images & diagrams

3. **Dev.to / Medium**

   - Great for storytelling & visibility
   - Title idea:

     > _Building a Digital Solari Board with Pygame_

4. **LinkedIn Article**

   - High recruiter visibility
   - Shortened version with GIFs

---

## ✅ Final Tip

If you’re experimenting:

- Make **one change at a time**
- Watch how motion, sound, and timing interact
- Mechanical UIs feel best when slightly imperfect 😉

Enjoy tweaking!
