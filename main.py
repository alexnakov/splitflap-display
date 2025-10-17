import pygame
import sys
import math
import random
import numpy as np
import soundfile as sf
from london_weather import fetch_weather_update
from constants import *

class SplitFlap:
    """A single split-flap character with a two-phase flip animation."""
    STYLE = "classic"
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
        self.flip_close_time = FLIP_CLOSE_TIME + random.uniform(-0.005, -0.005)
        self.flip_open_time = FLIP_OPEN_TIME + random.uniform(-0.005, -0.005)
        self._bake_shadow()

    def set_soundbank(self, sounds):
        self.click_sounds = [pygame.mixer.Sound(f"./audio/split_flap_edited_rate_1.5.mp3")]

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

    def start_flip(self, ghost=False):
        self.ghost = ghost
        self._advance_char()

        close_time = FLIP_CLOSE_TIME
        open_time  = FLIP_OPEN_TIME
        
        if ghost:
            close_time *= 10.0   # slower for subtle ghost flips
            open_time  *= 10.0
            self.next_char = self.current

        self.flip_close_time = close_time
        self.flip_open_time  = open_time

        self.state = 'closing'
        self.timer = 0.0
        self._play_click()

    def update(self, dt):
        if self.state == 'idle':
            if self.current != self.target:
                self.start_flip()
            return

        self.timer += dt
        if self.state == 'closing' and self.timer >= self.flip_close_time:
            # Commit to next char when fully closed
            self.current = self.next_char
            self.timer = 0.0
            self.state = 'opening'
            self._play_click()
        elif self.state == 'opening' and self.timer >= self.flip_open_time:
            # Decide whether to continue flipping toward target
            self.timer = 0.0
            if self.current == self.target:
                self.state = 'idle'
                self.ghost = False
            else:
                self.start_flip()

    def draw(self, surface):
        r = self.rect
        FLAP_BORDER_RADIUS = 4

        # --- Bezel color by style ---
        if self.STYLE == "classic":
            bezel_color = tuple(max(0, c - 25) for c in SLOT_COLOR)
        elif self.STYLE == "matte":
            bezel_color = tuple(min(255, c + 10) for c in SLOT_COLOR)
        elif self.STYLE == "retro":
            bezel_color = (max(0, SLOT_COLOR[0]-40), SLOT_COLOR[1], SLOT_COLOR[2])
        elif self.STYLE == "paper":
            bezel_color = tuple(min(255, c + 40) for c in SLOT_COLOR)
        else:
            bezel_color = SLOT_COLOR

        # --- Draw slot and shadow ---
        pygame.draw.rect(surface, bezel_color, r, border_radius=FLAP_BORDER_RADIUS)
        pygame.draw.rect(surface, ACCENT, r, width=2, border_radius=FLAP_BORDER_RADIUS)
        surface.blit(self.shadow_surf, r.topleft)

        # --- Glyphs ---
        glyph_cur = self.font.render(self.current, True, TEXT_COLOR)
        glyph_next = self.font.render(self.next_char if self.next_char else self.current, True, TEXT_COLOR)
        gc_rect = glyph_cur.get_rect(center=r.center)
        gn_rect = glyph_next.get_rect(center=r.center)

        # --- Idle state ---
        if self.state == 'idle':
            surface.blit(glyph_cur, gc_rect)
            return

        # --- Motion progress ---
        if self.state == 'closing':
            p = min(1.0, self.timer / FLIP_CLOSE_TIME + random.uniform(-0.005, -0.005))
            self._draw_flip(surface, glyph_cur, glyph_next, gc_rect, gn_rect, p, phase='close')
        elif self.state == 'opening':
            p = min(1.0, self.timer / FLIP_OPEN_TIME + random.uniform(-0.005, -0.005))
            self._draw_flip(surface, glyph_cur, glyph_next, gc_rect, gn_rect, p, phase='open')

            r = self.rect
            # Slot background and bezel
            FLAP_BORDER_RADIUS = 4
            if self.STYLE == "classic":
                bezel_color = tuple(max(0, c - 25) for c in SLOT_COLOR)
            else:
                bezel_color = SLOT_COLOR

            pygame.draw.rect(surface, bezel_color, r, border_radius=FLAP_BORDER_RADIUS)
            pygame.draw.rect(surface, ACCENT, r, width=2, border_radius=FLAP_BORDER_RADIUS)
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
                p = min(1.0, self.timer / FLIP_CLOSE_TIME + random.uniform(-0.005, -0.005))
                # Top half folds down (covering current)
                self._draw_flip(surface, glyph_cur, glyph_next, gc_rect, gn_rect, p, phase='close')
            elif self.state == 'opening':
                p = min(1.0, self.timer / FLIP_OPEN_TIME + random.uniform(-0.005, -0.005))
                # Bottom half opens to reveal the (committed) current
                self._draw_flip(surface, glyph_cur, glyph_next, gc_rect, gn_rect, p, phase='open')

    def _draw_flip(self, surface, glyph_cur, glyph_next, gc_rect, gn_rect, p, phase):
        r = self.rect

        # Pre-render halves
        cell = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        cell_cur = cell.copy(); cell_next = cell.copy()
        cell_cur.blit(glyph_cur, gc_rect.move(-r.x, -r.y))
        cell_next.blit(glyph_next, gn_rect.move(-r.x, -r.y))

        # --- Easing function variations ---
        def ease_in_out(s): return 0.5 - 0.5 * math.cos(math.pi * s)
        def ease_out_back(x, overshoot=1.25): return 1 + overshoot * ((x - 1)**3 + (x - 1)**2)

        if self.STYLE == "classic" and phase == "open":
            pe = ease_out_back(p)
        elif self.STYLE == "retro":
            pe = ease_in_out(p * random.uniform(0.95, 1.05))  # slight jitter
        else:
            pe = ease_in_out(p)

        top_rect = pygame.Rect(0, 0, r.w, r.h//2)
        bot_rect = pygame.Rect(0, r.h//2, r.w, r.h - r.h//2)

        # --- Hinge shadow by style ---
        if self.STYLE == "classic":
            hinge_alpha = int(180 * (0.4 + 0.6 * pe))
        elif self.STYLE == "matte":
            hinge_alpha = int(80 * (0.2 + 0.8 * pe))
        elif self.STYLE == "retro":
            hinge_alpha = int(160 * (0.3 + 0.7 * pe))
        elif self.STYLE == "paper":
            hinge_alpha = 0
        else:
            hinge_alpha = int(120 * (0.3 + 0.7 * pe))

        hinge_line = pygame.Surface((r.w, 2), pygame.SRCALPHA)
        hinge_line.fill((0, 0, 0, hinge_alpha))

        # --- Draw static base glyph ---
        surface.blit(cell_cur, r.topleft)

        # --- Draw motion halves ---
        if phase == 'close':
            fold_h = int((r.h//2) * (1 - pe))
            if fold_h > 0:
                visible_top = cell_cur.subsurface(pygame.Rect(0, 0, r.w, fold_h))
                surface.blit(visible_top, (r.x, r.y))
            flipped = cell_next.subsurface(top_rect)
            target_h = max(1, int((r.h//2) * (0.15 + 0.85 * (1 - pe))))
            scaled = pygame.transform.smoothscale(flipped, (r.w, target_h))
            surface.blit(scaled, (r.x, r.y + (r.h//2 - target_h)))
            surface.blit(hinge_line, (r.x, r.y + r.h//2 - 1))

        else:
            fold_h = int((r.h//2) * pe)
            if fold_h < (r.h//2):
                visible_top = cell_cur.subsurface(top_rect)
                surface.blit(visible_top, (r.x, r.y))
            flipped = cell_cur.subsurface(bot_rect)
            target_h = max(1, int((r.h//2) * (0.15 + 0.85 * pe)))
            scaled = pygame.transform.smoothscale(flipped, (r.w, target_h))
            surface.blit(scaled, (r.x, r.y + r.h//2))
            surface.blit(hinge_line, (r.x, r.y + r.h//2 - 1))

        # --- Additional style effects ---
        if self.STYLE == "classic":
            # Metallic reflection during motion
            if phase == "open" and 0.2 < p < 0.8:
                ref = pygame.Surface((r.w, 2), pygame.SRCALPHA)
                alpha = int(80 * (1 - abs(0.5 - p) * 2))
                ref.fill((255, 255, 255, alpha))
                surface.blit(ref, (r.x, r.y + r.h//2 - 2))

            # Central highlight gradient
            grad = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            for y in range(r.h):
                brightness = int(30 * (1 - abs((y - r.h/2) / (r.h/2))))
                pygame.draw.line(grad, (brightness, brightness, brightness, 40), (0, y), (r.w, y))
            surface.blit(grad, r.topleft, special_flags=pygame.BLEND_RGBA_ADD)

        elif self.STYLE == "matte":
            # Soft ambient light fade
            grad = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            for y in range(r.h):
                shade = int(10 * (1 - y / r.h))
                pygame.draw.line(grad, (shade, shade, shade, 25), (0, y), (r.w, y))
            surface.blit(grad, r.topleft, special_flags=pygame.BLEND_RGBA_SUB)

        elif self.STYLE == "retro":
            # Flickering highlight
            if random.random() < 0.3 and phase == "open":
                flicker = pygame.Surface((r.w, 2), pygame.SRCALPHA)
                flicker.fill((255, 220, 180, random.randint(40, 90)))
                surface.blit(flicker, (r.x, r.y + r.h//2 - 1))

        elif self.STYLE == "paper":
            # Slight shadow offset to mimic paper layer
            paper_shadow = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            paper_shadow.fill((0, 0, 0, 15))
            surface.blit(paper_shadow, (r.x + 1, r.y + 1))


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

    def ghost_flip(self, probability=0.1):
        """Trigger a small random ghost flip on some flaps."""
        for f in self.flaps:
            if random.random() < probability and f.state == 'idle':
                f.start_flip(ghost=True)

    def update(self, dt):
        # keep existing pending handling first
        if self.pending:
            new_pending = []
            for f, c, delay in self.pending:
                delay -= dt
                if delay <= 0:
                    f.queue_target(c)
                else:
                    new_pending.append((f, c, delay))
            self.pending = new_pending if new_pending else None

        # Detect if all flaps are idle (finished flipping)
        if not self.pending and all(f.state == 'idle' for f in self.flaps):
            if hasattr(self, 'on_complete') and callable(self.on_complete):
                self.on_complete(self)
                self.on_complete = None  # only trigger once

        # existing flap updates
        for f in self.flaps:
            f.update(dt)


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Split-Flap Display – Demo")
        pygame.mixer.pre_init(44100, -16, 2, 256)
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        SCREEN_W, SCREEN_H = self.screen.get_size()
        self.clock = pygame.time.Clock()
        initial_weather = fetch_weather_update()
        self.text_a = initial_weather
        self.text_b = initial_weather

        # Fonts
        font_path = "./fonts/DepartureMono-Regular.otf"
        self.font = pygame.font.Font(font_path, 64)

        self.sounds = []

        # Build row sized to the longer of the two texts
        n_chars = COLS
        total_w = n_chars * CELL_W + (n_chars - 1) * CELL_GAP
        start_x = (SCREEN_W - total_w) // 2

        self.rows = []
        for i in range(ROWS):
            row_y = TOP_MARGIN + i * (CELL_H + CELL_GAP)
            row = FlapRow(start_x, row_y, n_chars, self.font)
            row.set_soundbank(self.sounds)
            self.rows.append(row)

        # Initialize with normalized A and schedule flip to B
        self.current_rows = self._normalize_rows(self.text_a)
        self.text_b = fetch_weather_update() # Updating new weather
        self.alt_rows = self._normalize_rows(self.text_b)
        for flap_row, text in zip(self.rows, self.current_rows):
            flap_row.set_text_immediate(text)

        self.time_since_toggle = 0.0

    def _normalize_rows(self, rows):
        normalized = []
        for row in rows:
            row = row.upper()
            row = ''.join(ch if ch in CHARSET else ' ' for ch in row)
            if len(row) < COLS:
                row += ' ' * (COLS - len(row))
            normalized.append(row[:COLS])
        return normalized

    def toggle(self):
        self.current_rows, self.alt_rows = self.alt_rows, self.current_rows
        for flap_row, text in zip(self.rows, self.current_rows):
            flap_row.flip_to(text)
        self.time_since_toggle = 0.0
    
    def refresh_board(self):
        """Force a full random refresh, then return to intended text."""
        print("Refreshing board...")
        self.is_refreshing = True
        self.random_rows = []
        for _ in range(ROWS):
            # Generate random placeholder text same width as board
            rand_text = ''.join(random.choice(CHARSET) for _ in range(COLS))
            self.random_rows.append(rand_text)

        # Flip all rows to random text first
        for flap_row, text in zip(self.rows, self.random_rows):
            flap_row.flip_to(text)

        for flap_row in self.rows:
            flap_row.on_complete = lambda row, app=self: app.on_refresh_complete()

    def refresh_random_row(self):
        """Force a random refresh on one random row."""
        print("Refreshing single row...")
        row_idx = random.randint(0, len(self.rows) - 1)
        row = self.rows[row_idx]

        # Generate random placeholder text for that row
        rand_text = ''.join(random.choice(CHARSET) for _ in range(COLS))
        row.flip_to(rand_text)

        # When done, flip back to intended text
        row.on_complete = lambda r=row, app=self, idx=row_idx: app._restore_row(idx)

    def _restore_row(self, row_idx):
        """Return a refreshed row back to its intended text."""
        row = self.rows[row_idx]
        intended_text = self.current_rows[row_idx]
        row.flip_to(intended_text)


    def on_refresh_complete(self):
        """Callback when all rows finish random pass."""
        if getattr(self, "is_refreshing", False):
            print("Random refresh complete → returning to intended text.")
            self.is_refreshing = False
            # Flip back to current intended text
            for flap_row, text in zip(self.rows, self.current_rows):
                flap_row.flip_to(text)

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
                    elif event.key == pygame.K_d:
                        styles = ["classic", "matte", "retro", "paper"]
                        idx = styles.index(SplitFlap.STYLE)
                        SplitFlap.STYLE = styles[(idx + 1) % len(styles)]

            # Auto-toggle 
            self.time_since_toggle += dt
            if self.time_since_toggle >= TOGGLE_PERIOD:
                self.toggle()

            # --- Ghost flip timer ---
            if not hasattr(self, "ghost_timer"):
                self.ghost_timer = 0.0
            self.ghost_timer += dt
            if self.ghost_timer >= GHOST_TIMER:  # every 10 seconds
                for flap_row in self.rows:
                    flap_row.ghost_flip(probability=0.1)
                self.ghost_timer = 0.0

            # --- Single-row random refresh timer ---
            if not hasattr(self, "row_refresh_timer"):
                self.row_refresh_timer = 0.0
            self.row_refresh_timer += dt

            if self.row_refresh_timer >= ROW_REFRESH_TIMER:  # every 5 minutes
                self.refresh_random_row()
                self.row_refresh_timer = 0.0

            # --- Full board random refresh timer ---
            if not hasattr(self, "refresh_timer"):
                self.refresh_timer = 0.0
            self.refresh_timer += dt

            if self.refresh_timer >= FULLBOARD_REFRESH_TIMER:  # every 60 seconds
                self.refresh_board()
                self.refresh_timer = 0.0

            for flap_row in self.rows:
                flap_row.update(dt)

            # Draw
            self.screen.fill(BG_COLOR)

            for flap_row in self.rows:
                flap_row.draw(self.screen)

            pygame.display.flip()
        pygame.quit()

if __name__ == '__main__':
    try:
        App().run()
    except Exception as e:
        print("Error:", e)
        pygame.quit()
        sys.exit(1)
