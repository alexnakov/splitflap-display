import pygame
import sys
import math
import random
import numpy as np

"""
Split-Flap Display (Pygame)

- Mimics the visual flip of split-flap modules using a two-phase hinge animation (close then open).
- Plays a short mechanical "clack" sound on each flap using procedurally generated audio (no external files).
- Demo toggles between two texts every few seconds.

Controls:
  - ESC or Q: quit
  - SPACE: manually toggle between the two demo texts

Requirements:
  - pygame
  - numpy (for procedural sound). If numpy/mixer fails, app runs silently.
"""

# ------------------------------
# Configuration
# ------------------------------
SCREEN_W, SCREEN_H = 1200, 280
FPS = 60
BG_COLOR = (10, 12, 14)
BOARD_COLOR = (18, 20, 24)
SLOT_COLOR = (8, 9, 10)
TEXT_COLOR = (230, 232, 235)
ACCENT = (40, 48, 56)

# Character set typical of split-flap boards
CHARSET = " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-/'#:"
CHAR_INDEX = {c: i for i, c in enumerate(CHARSET)}

# Demo texts (must be same length for best effect; will be padded)
TEXT_A = "NEW YORK  JFK  AA123  14:05  ON TIME"
TEXT_B = "SAN DIEGO SAN  UA987  15:40  BOARD  "

# Board / cell sizing
CELL_W = 36
CELL_H = 64
CELL_GAP = 6
TOP_MARGIN = 80
LEFT_MARGIN = 40

# Animation timings (seconds)
FLIP_CLOSE_TIME = 0.07   # top half folding down
FLIP_OPEN_TIME = 0.09    # bottom half opening to reveal next
INTER_FLAP_DELAY = 0.06  # cascade delay between neighboring cells

# Auto-toggle between A/B every N seconds
TOGGLE_PERIOD = 6.0

# Sound configuration
ENABLE_SOUND = True
CLICK_VARIANTS = 5

# ------------------------------
# Audio: procedural click generator
# ------------------------------

def generate_click_sounds(variants=5, rate=44100):
    """Generate a handful of slightly different mechanical click sounds."""
    sounds = []
    try:
        for _ in range(variants):
            dur = random.uniform(0.018, 0.028)  # seconds
            n = int(rate * dur)
            # Start with short burst noise + decaying high-pass character
            t = np.linspace(0, dur, n, endpoint=False)
            # Base: filtered noise envelope
            noise = np.random.randn(n) * 0.35
            # Add a resonant tap (brief sine) for bite
            freq = random.uniform(2000, 3200)
            tap = 0.6 * np.sin(2 * np.pi * freq * t) * np.exp(-t * random.uniform(20, 40))
            sig = noise * np.exp(-t * random.uniform(35, 55)) + tap
            # Clip and convert to int16 stereo
            sig = np.clip(sig, -1.0, 1.0)
            audio = (sig * 32767).astype(np.int16)
            stereo = np.stack([audio, audio], axis=-1)
            snd = pygame.mixer.Sound(buffer=stereo)
            sounds.append(snd)
        return sounds
    except Exception:
        return []

# ------------------------------
# Split-flap module
# ------------------------------
class SplitFlap:
    """A single split-flap character with a two-phase flip animation."""
    def __init__(self, x, y, w, h, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.current = ' '
        self.target = ' '
        self.next_char = ' '
        self.state = 'idle'  # 'idle', 'closing', 'opening'
        self.timer = 0.0
        self.click_sounds = []
        self.shadow_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        # Precompute a subtle inner shadow for depth
        self._bake_shadow()

    def set_soundbank(self, sounds):
        self.click_sounds = sounds

    def _bake_shadow(self):
        surf = self.shadow_surf
        surf.fill((0,0,0,0))
        # Soft inner shadow
        border = 6
        darkness = 70
        for i in range(border):
            alpha = int(darkness * (1 - i / border))
            pygame.draw.rect(surf, (0,0,0,alpha),
                             (i, i, self.rect.w - 2*i, self.rect.h - 2*i), 1, border_radius=6)

    def set_char_immediate(self, c):
        self.current = c if c in CHARSET else ' '
        self.target = self.current
        self.state = 'idle'
        self.timer = 0

    def queue_target(self, c):
        self.target = c if c in CHARSET else ' '

    def _play_click(self):
        if self.click_sounds:
            random.choice(self.click_sounds).play()

    def _advance_char(self):
        ci = CHAR_INDEX.get(self.current, 0)
        ni = (ci + 1) % len(CHARSET)
        self.next_char = CHARSET[ni]

    def start_flip(self):
        self._advance_char()
        self.state = 'closing'
        self.timer = 0.0
        self._play_click()

    def update(self, dt):
        if self.state == 'idle':
            if self.current != self.target:
                self.start_flip()
            return

        self.timer += dt
        if self.state == 'closing' and self.timer >= FLIP_CLOSE_TIME:
            # Commit to next char when fully closed
            self.current = self.next_char
            self.timer = 0.0
            self.state = 'opening'
            self._play_click()
        elif self.state == 'opening' and self.timer >= FLIP_OPEN_TIME:
            # Decide whether to continue flipping toward target
            self.timer = 0.0
            if self.current == self.target:
                self.state = 'idle'
            else:
                self.start_flip()

    def draw(self, surface):
        r = self.rect
        # Slot background and bezel
        pygame.draw.rect(surface, SLOT_COLOR, r, border_radius=8)
        pygame.draw.rect(surface, ACCENT, r, width=2, border_radius=8)
        surface.blit(self.shadow_surf, r.topleft)

        # Prepare glyph surfaces for current and next
        glyph_cur = self.font.render(self.current, True, TEXT_COLOR)
        glyph_next = self.font.render(self.next_char if self.next_char else self.current, True, TEXT_COLOR)

        # Center glyphs
        gc_rect = glyph_cur.get_rect(center=r.center)
        gn_rect = glyph_next.get_rect(center=r.center)

        # Draw depending on state
        if self.state == 'idle':
            surface.blit(glyph_cur, gc_rect)
            return

        # Compute hinge animation progress 0..1
        if self.state == 'closing':
            p = min(1.0, self.timer / FLIP_CLOSE_TIME)
            # Top half folds down (covering current)
            self._draw_flip(surface, glyph_cur, glyph_next, gc_rect, gn_rect, p, phase='close')
        elif self.state == 'opening':
            p = min(1.0, self.timer / FLIP_OPEN_TIME)
            # Bottom half opens to reveal the (committed) current
            self._draw_flip(surface, glyph_cur, glyph_next, gc_rect, gn_rect, p, phase='open')

    def _draw_flip(self, surface, glyph_cur, glyph_next, gc_rect, gn_rect, p, phase):
        r = self.rect
        cx, cy = r.center

        # Pre-render halves for current and next
        # Surfaces matching cell size
        cell = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        cell_cur = cell.copy(); cell_next = cell.copy()
        cell_cur.blit(glyph_cur, gc_rect.move(-r.x, -r.y))
        cell_next.blit(glyph_next, gn_rect.move(-r.x, -r.y))

        # Compute fold amount
        # Map progress to a smooth easing for nicer motion
        def ease_in_out(s):
            return 0.5 - 0.5 * math.cos(math.pi * s)
        pe = ease_in_out(p)

        top_rect = pygame.Rect(0, 0, r.w, r.h//2)
        bot_rect = pygame.Rect(0, r.h//2, r.w, r.h - r.h//2)

        # Masks for shading hinge line
        hinge_alpha = int(120 * (0.3 + 0.7 * pe))
        hinge_line = pygame.Surface((r.w, 2), pygame.SRCALPHA)
        hinge_line.fill((0,0,0, hinge_alpha))

        # Base: draw current glyph fully, then overlay animated flap
        surface.blit(cell_cur, r.topleft)

        if phase == 'close':
            # Top half folds down over the current
            fold_h = int((r.h//2) * (1 - pe))
            if fold_h > 0:
                # Visible remaining top of current
                visible_top = cell_cur.subsurface(pygame.Rect(0, 0, r.w, fold_h))
                surface.blit(visible_top, (r.x, r.y))
            # Draw flipping top from next glyph to simulate the blur of numbers cycling
            flipped = cell_next.subsurface(top_rect)
            # Scale top half vertically toward zero around hinge
            target_h = max(1, int((r.h//2) * (0.15 + 0.85 * (1 - pe))))
            scaled = pygame.transform.smoothscale(flipped, (r.w, target_h))
            surface.blit(scaled, (r.x, r.y + (r.h//2 - target_h)))
            surface.blit(hinge_line, (r.x, r.y + r.h//2 - 1))
        else:
            # Opening phase: bottom half of the new current unfolds
            fold_h = int((r.h//2) * pe)
            if fold_h < (r.h//2):
                # Keep top half visible
                visible_top = cell_cur.subsurface(top_rect)
                surface.blit(visible_top, (r.x, r.y))
            # Bottom unfolding
            flipped = cell_cur.subsurface(bot_rect)
            target_h = max(1, int((r.h//2) * (0.15 + 0.85 * pe)))
            scaled = pygame.transform.smoothscale(flipped, (r.w, target_h))
            surface.blit(scaled, (r.x, r.y + r.h//2))
            surface.blit(hinge_line, (r.x, r.y + r.h//2 - 1))

# ------------------------------
# Row of split-flaps
# ------------------------------
class FlapRow:
    def __init__(self, x, y, n_chars, font):
        self.flaps = []
        for i in range(n_chars):
            cx = x + i * (CELL_W + CELL_GAP)
            self.flaps.append(SplitFlap(cx, y, CELL_W, CELL_H, font))
        self.pending = None

    def set_soundbank(self, sounds):
        for f in self.flaps:
            f.set_soundbank(sounds)

    def set_text_immediate(self, text):
        text = self._normalize(text)
        for f, c in zip(self.flaps, text):
            f.set_char_immediate(c)

    def flip_to(self, text):
        """Queue a flip to the given text with a cascading delay."""
        text = self._normalize(text)
        self.pending = []
        t = 0.0
        for f, c in zip(self.flaps, text):
            self.pending.append((f, c, t))
            t += INTER_FLAP_DELAY

    def _normalize(self, text):
        text = text.upper()
        # Replace unsupported characters with space
        text = ''.join(ch if ch in CHARSET else ' ' for ch in text)
        # Pad or trim to row length
        if len(text) < len(self.flaps):
            text += ' ' * (len(self.flaps) - len(text))
        else:
            text = text[:len(self.flaps)]
        return text

    def update(self, dt):
        # Dispatch pending char targets based on their cascade delay
        if self.pending:
            new_pending = []
            for f, c, delay in self.pending:
                delay -= dt
                if delay <= 0:
                    f.queue_target(c)
                else:
                    new_pending.append((f, c, delay))
            self.pending = new_pending if new_pending else None
        # Update flaps
        for f in self.flaps:
            f.update(dt)

    def draw(self, surface):
        for f in self.flaps:
            f.draw(surface)

# ------------------------------
# Main application
# ------------------------------
class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Split-Flap Display – Demo")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()

        # Background board surface
        self.board = pygame.Surface((SCREEN_W - 2*LEFT_MARGIN, CELL_H + 40))
        self.board.fill(BOARD_COLOR)
        pygame.draw.rect(self.board, ACCENT, self.board.get_rect(), width=2, border_radius=12)

        # Fonts
        self.font = pygame.font.SysFont("DejaVu Sans Mono", 44, bold=True)
        self.ui_font = pygame.font.SysFont("DejaVu Sans", 18)
        self.title_font = pygame.font.SysFont("DejaVu Sans", 22, bold=True)

        # Audio
        self.sounds = []
        if ENABLE_SOUND:
            try:
                pygame.mixer.pre_init(44100, -16, 2, 256)
            except Exception:
                pass
        try:
            pygame.mixer.init()
            self.sounds = generate_click_sounds(CLICK_VARIANTS)
        except Exception:
            self.sounds = []

        # Build row sized to the longer of the two texts
        max_len = max(len(TEXT_A), len(TEXT_B))
        n_chars = max_len
        # Center the row horizontally
        total_w = n_chars * CELL_W + (n_chars - 1) * CELL_GAP
        start_x = (SCREEN_W - total_w) // 2
        self.rows_list = []
        self.row = FlapRow(start_x, TOP_MARGIN, n_chars, self.font)
        self.row2 = FlapRow(start_x, TOP_MARGIN, n_chars, self.font)
        self.row.set_soundbank(self.sounds)

        # Initialize with normalized A and schedule flip to B
        self.current_text = self._normalize_len(TEXT_A, n_chars)
        self.alt_text = self._normalize_len(TEXT_B, n_chars)
        self.row.set_text_immediate(self.current_text)

        self.time_since_toggle = 0.0

    def _normalize_len(self, text, L):
        text = text.upper()
        text = ''.join(ch if ch in CHARSET else ' ' for ch in text)
        if len(text) < L:
            text += ' ' * (L - len(text))
        return text[:L]

    def toggle(self):
        self.current_text, self.alt_text = self.alt_text, self.current_text
        self.row.flip_to(self.current_text)
        self.time_since_toggle = 0.0

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.toggle()

            # Auto-toggle every TOGGLE_PERIOD seconds
            self.time_since_toggle += dt

            self.row.update(dt)

            # Draw
            self.screen.fill(BG_COLOR)
            # Center board
            board_x = (SCREEN_W - self.board.get_width()) // 2
            self.screen.blit(self.board, (board_x, TOP_MARGIN - 20))

            self.row.draw(self.screen)

            # UI overlay
            hint1 = self.ui_font.render("SPACE to toggle  •  ESC to quit", True, (180, 185, 190))
            self.screen.blit(hint1, (20, SCREEN_H - 32))
            title = self.title_font.render("Split-Flap Display (demo)", True, (210, 215, 220))
            self.screen.blit(title, (20, 16))

            pygame.display.flip()
        pygame.quit()

if __name__ == '__main__':
    try:
        App().run()
    except Exception as e:
        print("Error:", e)
        pygame.quit()
        sys.exit(1)
