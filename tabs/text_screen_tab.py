import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk
# Ensure main_frame and editor_layout are packed first
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk

class TextScreenTab(ttk.Frame):
    def _interpolate_cells(self, start, end):
        # Bresenham's line algorithm for grid interpolation
        x0, y0 = start
        x1, y1 = end
        cells = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        if dx > dy:
            err = dx / 2.0
            while x != x1:
                cells.append((y, x))
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                cells.append((y, x))
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        cells.append((y1, x1))
        return cells
    def load_aquascii_bin(self, path, target_width, target_height):
        """Load AQUASCII characters from a BIN file as 8x8 blocks, each 8 bytes, resized to target size."""
        import os
        chars = []
        with open(path, "rb") as f:
            data = f.read()
        num_chars = len(data) // 8
        for char_idx in range(num_chars):
            char_bytes = data[char_idx*8:(char_idx+1)*8]
            img = Image.new("RGB", (8, 8), "white")
            pixels = img.load()
            for y in range(8):
                byte = char_bytes[y]
                for x in range(8):
                    if (byte >> (7-x)) & 1:
                        pixels[x, y] = (0, 0, 0)  # Foreground (black)
                    else:
                        pixels[x, y] = (255, 255, 255)  # Background (white)
            img = img.resize((target_width, target_height), Image.NEAREST)
            chars.append(ImageTk.PhotoImage(img))
        return chars

    # Removed duplicate empty __init__
    def __init__(self, parent):
        super().__init__(parent)
        self._screen_buffer_initialized = False
        self.show_grid_var = tk.BooleanVar(value=True)
        self.show_grid_var.trace_add("write", lambda *args: self.update_screen_grid())
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#808080", borderwidth=0)
        style.configure("TNotebook.Tab", background="#A0A0A0", font=("Arial", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#D0D0D0")])

        self.fg_labels = [None] * 16
        self.bg_labels = [None] * 16
        self.selected_fg_idx = 0
        self.selected_bg_idx = 7

        self.main_frame = tk.Frame(self, bg="#D0D0D0")
        self.main_frame.pack(fill=tk.X)
        self.col_mode_var = tk.StringVar(value="40")

        # Use self as parent for editor_layout
        self.editor_layout = tk.Frame(self, bg="#D0D0D0")
        self.editor_layout.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Screen panel (empty, no canvas or buffer logic)
        self.screen_frame = tk.LabelFrame(self.editor_layout, text="Screen", bg="#D0D0D0", width=736, height=496)
        self.screen_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0,8))

        # AQUASCII character selector panel
        self.aquascii_cell_width = 16
        self.aquascii_cell_height = 16
        self.char_spacing = 2
        self.active_char = 65

        aquascii_canvas_width = 8 * self.aquascii_cell_width + (8 - 1) * self.char_spacing
        aquascii_canvas_height = 32 * self.aquascii_cell_height + (32 - 1) * self.char_spacing
        aquascii_panel_width = aquascii_canvas_width + 24
        aquascii_panel = tk.LabelFrame(self.editor_layout, text="AQUASCII", bg="#D0D0D0", width=aquascii_panel_width)
        aquascii_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0,8), ipadx=8, ipady=8)

        palette_and_controls_frame = tk.Frame(self.editor_layout, bg="#D0D0D0")
        palette_and_controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0, anchor="n")

        # Palette frame with FG/BG subframes
        palette_frame = tk.LabelFrame(palette_and_controls_frame, text="Palette", bg="#D0D0D0")
        palette_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=0)

        aquarius_palette = [
            (0x11, 0x11, 0x11),
            (0xFF, 0x11, 0x11),
            (0x11, 0xFF, 0x11),
            (0xFF, 0xFF, 0x11),
            (0x22, 0x22, 0xEE),
            (0xFF, 0x11, 0xFF),
            (0x33, 0xCC, 0xCC),
            (0xFF, 0xFF, 0xFF),
            (0xCC, 0xCC, 0xCC),
            (0x33, 0xBB, 0xBB),
            (0xCC, 0x22, 0xCC),
            (0x44, 0x11, 0x99),
            (0xFF, 0xFF, 0x77),
            (0x22, 0xDD, 0x44),
            (0xBB, 0x22, 0x22),
            (0x33, 0x33, 0x33),
        ]

        fg_frame = tk.LabelFrame(palette_frame, text="FG", bg="#D0D0D0")
        fg_frame.grid(row=0, column=0, padx=2, pady=(2,8), sticky="ew")
        palette_frame.grid_columnconfigure(0, weight=1)
        for idx in range(16):
            row = idx // 4
            col = idx % 4
            rgb = aquarius_palette[idx]
            color = f'#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}'
            border_color = "#FF0000" if idx == self.selected_fg_idx else "#D0D0D0"
            lbl = tk.Label(fg_frame, text="", width=4, height=1, bg=color, highlightbackground=border_color, highlightcolor=border_color, highlightthickness=4, bd=0, borderwidth=0)
            lbl.grid(row=row, column=col, padx=8, pady=1, sticky="ew")
            lbl.bind("<Button-1>", lambda e, i=idx: self.select_fg_swatch(i))
            self.fg_labels[idx] = lbl

        bg_frame = tk.LabelFrame(palette_frame, text="BG", bg="#D0D0D0")
        bg_frame.grid(row=1, column=0, padx=2, pady=(8,2), sticky="ew")
        for idx in range(16):
            row = idx // 4
            col = idx % 4
            rgb = aquarius_palette[idx]
            color = f'#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}'
            border_color = "#FF0000" if idx == self.selected_bg_idx else "#D0D0D0"
            lbl = tk.Label(bg_frame, text="", width=4, height=1, bg=color, highlightbackground=border_color, highlightcolor=border_color, highlightthickness=4, bd=0, borderwidth=0)
            lbl.grid(row=row, column=col, padx=8, pady=1, sticky="ew")
            lbl.bind("<Button-1>", lambda e, i=idx: self.select_bg_swatch(i))
            self.bg_labels[idx] = lbl

        # Controls panel
        controls_frame = tk.LabelFrame(palette_and_controls_frame, text="Controls", bg="#D0D0D0")
        controls_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(10,4))
        screen_mode_section = tk.LabelFrame(controls_frame, text="Screen Mode", bg="#D0D0D0")
        screen_mode_section.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(8,4))
        tk.Radiobutton(screen_mode_section, text="40 Col", variable=self.col_mode_var, value="40", bg="#D0D0D0").pack(side=tk.LEFT, padx=4, pady=2)
        tk.Radiobutton(screen_mode_section, text="80 Col", variable=self.col_mode_var, value="80", bg="#D0D0D0").pack(side=tk.LEFT, padx=4, pady=2)
        self.col_mode_var.trace_add("write", self.on_col_mode_change)

        # Restore Show Grid checkbox section
        show_grid_section = tk.LabelFrame(controls_frame, text="Visual Aids", bg="#D0D0D0")
        show_grid_section.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(4,4))
        show_grid_cb = tk.Checkbutton(show_grid_section, text="Show Grid", variable=self.show_grid_var, bg="#D0D0D0")
        show_grid_cb.pack(side=tk.LEFT, padx=4, pady=2)

        self.paint_char_var = tk.BooleanVar(value=True)
        self.paint_fg_var = tk.BooleanVar(value=True)
        self.paint_bg_var = tk.BooleanVar(value=True)
        paint_panel = tk.LabelFrame(palette_and_controls_frame, text="Paint", bg="#D0D0D0")
        paint_panel.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(0,0))
        paint_panel.grid_columnconfigure(0, weight=1)
        paint_panel.grid_columnconfigure(1, weight=1)
        paint_panel.grid_columnconfigure(2, weight=1)
        char_cb = tk.Checkbutton(paint_panel, text="Char", variable=self.paint_char_var, bg="#D0D0D0")
        fg_cb = tk.Checkbutton(paint_panel, text="FG", variable=self.paint_fg_var, bg="#D0D0D0")
        bg_cb = tk.Checkbutton(paint_panel, text="BG", variable=self.paint_bg_var, bg="#D0D0D0")
        # Make sure paint_panel row 1 expands
        paint_panel.grid_rowconfigure(1, weight=1)
        paint_panel.grid_columnconfigure(0, weight=1)
        paint_panel.grid_columnconfigure(1, weight=1)
        paint_panel.grid_columnconfigure(2, weight=1)
        char_cb.grid(row=0, column=0, sticky="nsew", padx=8, pady=(8,2))
        fg_cb.grid(row=0, column=1, sticky="nsew", padx=8, pady=(8,2))
        bg_cb.grid(row=0, column=2, sticky="nsew", padx=8, pady=(8,2))
        self.char_preview_frame = tk.Frame(
            paint_panel,
            bg="#D0D0D0",
            highlightbackground="#222222",
            highlightcolor="#222222",
            highlightthickness=2,
            bd=0,
            relief="flat"
        )
        # Place preview in row 1, column 1, visually left-aligned under FG checkbox
        self.char_preview_frame.grid(row=1, column=1, sticky="nw", padx=(0,16), pady=(8,8))
        self.char_preview_canvas = tk.Canvas(self.char_preview_frame, width=64, height=64, bg="#E0E0E0", highlightthickness=0)
        # Center the canvas in the frame with minimal padding
        self.char_preview_canvas.pack(expand=False, fill=None, padx=0, pady=0)
        # Ensure initial preview is shown at startup
        self.update_char_preview()

        # Ensure aquascii_images_selector is initialized before using
        self.aquascii_images_selector = []
        images_selector = self.load_aquascii_bin("assets/aquascii.bin", 16, 16)
        self.aquascii_images_selector = images_selector
        # Restore AQUASCII character selection grid
        if hasattr(self, 'aquascii_canvas'):
            self.aquascii_canvas.pack_forget()
        self.aquascii_canvas = tk.Canvas(aquascii_panel, width=aquascii_canvas_width, height=aquascii_canvas_height, bg="#FFFFFF", highlightthickness=0, bd=0)
        self.aquascii_canvas.pack(side=tk.TOP, fill=tk.Y, padx=8, pady=8)
        self.aquascii_canvas.bind("<Button-1>", self.on_aquascii_click)
        self.aquascii_canvas_images = []
        for idx in range(32*8):
            row = idx // 8
            col = idx % 8
            x = col * (self.aquascii_cell_width + self.char_spacing)
            y = row * (self.aquascii_cell_height + self.char_spacing)
            if idx < len(self.aquascii_images_selector):
                img_id = self.aquascii_canvas.create_image(x, y, anchor="nw", image=self.aquascii_images_selector[idx])
                self.aquascii_canvas_images.append(img_id)
        self.draw_aquascii_overlay()

    # ...Screen panel is now empty, no canvas or event bindings...

        # ...existing code...

    def update_char_preview(self):
        # Determine resolution and logical pixel size
        mode = self.col_mode_var.get()
        char_code = self.active_char if hasattr(self, 'active_char') else 65
        fg_idx = getattr(self, 'selected_fg_idx', 0)
        bg_idx = getattr(self, 'selected_bg_idx', 7)
        palette = [
            (0x11, 0x11, 0x11), (0xFF, 0x11, 0x11), (0x11, 0xFF, 0x11), (0xFF, 0xFF, 0x11),
            (0x22, 0x22, 0xEE), (0xFF, 0x11, 0xFF), (0x33, 0xCC, 0xCC), (0xFF, 0xFF, 0xFF),
            (0xCC, 0xCC, 0xCC), (0x33, 0xBB, 0xBB), (0xCC, 0x22, 0xCC), (0x44, 0x11, 0x99),
            (0xFF, 0xFF, 0x77), (0x22, 0xDD, 0x44), (0xBB, 0x22, 0x22), (0x33, 0x33, 0x33)
        ]
        fg_color = f'#{palette[fg_idx][0]:02X}{palette[fg_idx][1]:02X}{palette[fg_idx][2]:02X}'
        bg_color = f'#{palette[bg_idx][0]:02X}{palette[bg_idx][1]:02X}{palette[bg_idx][2]:02X}'
        # Set preview size and logical pixel size
        if mode == "80":
            width, height = 32, 64
            logical_w, logical_h = 4, 8
        else:
            width, height = 64, 64
            logical_w, logical_h = 8, 8
        self.char_preview_canvas.config(width=width, height=height)
        # Get bitmap for character
        bitmap = self.get_char_bitmap(char_code)
        # Render preview: BG for 0 pixels, FG for 1 pixels
        from PIL import Image, ImageDraw
        # Checkerboard only if fg == bg
        if fg_idx == bg_idx:
            # FG and BG are the same: outline each logical pixel with the logical NOT color
            img = Image.new("RGB", (width, height), bg_color)
            draw = ImageDraw.Draw(img)
            # Compute logical NOT color
            fg_rgb = tuple(int(fg_color[i:i+2], 16) for i in (1, 3, 5))
            not_rgb = tuple(255 - c for c in fg_rgb)
            not_color = '#%02X%02X%02X' % not_rgb
            rows = len(bitmap)
            cols = len(bitmap[0]) if rows > 0 else 0
            for y in range(rows):
                for x in range(cols):
                    px = x * logical_w
                    py = y * logical_h
                    if bitmap[y][x]:
                        # Draw outline rectangle (1 pixel border)
                        draw.rectangle([px, py, px+logical_w-1, py+logical_h-1], outline=not_color, width=1)
                        # Fill center with FG/BG color
                        draw.rectangle([px+1, py+1, px+logical_w-2, py+logical_h-2], fill=fg_color)
        else:
            img = Image.new("RGB", (width, height), bg_color)
            draw = ImageDraw.Draw(img)
            rows = len(bitmap)
            cols = len(bitmap[0]) if rows > 0 else 0
            for y in range(rows):
                for x in range(cols):
                    color = fg_color if bitmap[y][x] else bg_color
                    px = x * logical_w
                    py = y * logical_h
                    draw.rectangle([px, py, px+logical_w-1, py+logical_h-1], fill=color)
        self.char_preview_imgtk = ImageTk.PhotoImage(img)
        self.char_preview_canvas.delete("all")
        self.char_preview_canvas.create_image(width//2, height//2, image=self.char_preview_imgtk, anchor="center")

    def _is_dark_color(self, hex_color):
        # Helper to determine if a color is dark (for checkerboard contrast)
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        # Perceived brightness
        brightness = (r*299 + g*587 + b*114) / 1000
        return brightness < 128

    def get_char_bitmap(self, char_code):
        # Returns 8x8 bitmap for character code from loaded AQUASCII binary
        # Use the binary data loaded in self.aquascii_images_selector
        try:
            # Load raw bytes from the BIN file (assume 8 bytes per char, 256 chars)
            with open("assets/aquascii.bin", "rb") as f:
                data = f.read()
            offset = char_code * 8
            char_bytes = data[offset:offset+8]
            bitmap = []
            for byte in char_bytes:
                row = [(byte >> (7-x)) & 1 for x in range(8)]
                bitmap.append(row)
            return bitmap
        except Exception:
            # Fallback: all foreground
            return [[1]*8 for _ in range(8)]

    def render_char_bitmap(self, bitmap, width, height, logical_w, logical_h, fg_color, bg_color):
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        rows = len(bitmap)
        cols = len(bitmap[0]) if rows > 0 else 0
        for y in range(rows):
            for x in range(cols):
                color = fg_color if bitmap[y][x] else bg_color
                px = x * logical_w
                py = y * logical_h
                draw.rectangle([px, py, px+logical_w-1, py+logical_h-1], fill=color)
        return img

    # ...existing code...
    def select_fg_swatch(self, idx):
        self.selected_fg_idx = idx
        for lbl in self.fg_labels:
            lbl.config(highlightbackground="#D0D0D0", highlightcolor="#D0D0D0")
        self.fg_labels[idx].config(highlightbackground="#FF0000", highlightcolor="#FF0000")
        self.update_char_preview()

    def select_bg_swatch(self, idx):
        self.selected_bg_idx = idx
        for lbl in self.bg_labels:
            lbl.config(highlightbackground="#D0D0D0", highlightcolor="#D0D0D0")
        self.bg_labels[idx].config(highlightbackground="#FF0000", highlightcolor="#FF0000")
        self.update_char_preview()

    # ...existing code...

    def on_screen_right_click(self, event):
        col = event.x // self.cell_width
        row = event.y // self.cell_height
        active_start_col = self.border_cols
        active_end_col = self.total_cols - self.border_cols
        active_start_row = self.border_rows
        active_end_row = self.total_rows - self.border_rows

        # Only pick up character/colors if in active area
        if (active_start_col <= col < active_end_col and active_start_row <= row < active_end_row):
            cell = self.screen_buffer[row][col]
            picked_char = cell["char"]
            picked_fg = cell["fg"]
            picked_bg = cell["bg"]
            if 0 <= picked_char < len(self.aquascii_images_selector):
                self.active_char = picked_char
                self.selected_fg_idx = picked_fg
                self.selected_bg_idx = picked_bg
                # Update swatch highlights
                for lbl in self.fg_labels:
                    lbl.config(highlightbackground="#D0D0D0", highlightcolor="#D0D0D0")
                self.fg_labels[picked_fg].config(highlightbackground="#FF0000", highlightcolor="#FF0000")
                for lbl in self.bg_labels:
                    lbl.config(highlightbackground="#D0D0D0", highlightcolor="#D0D0D0")
                self.bg_labels[picked_bg].config(highlightbackground="#FF0000", highlightcolor="#FF0000")
                self.draw_aquascii_overlay()
                self.update_char_preview()

    def on_aquascii_click(self, event):
        # Use fixed 16x16 cell size for selector panel
        aquascii_cell_width = 16
        aquascii_cell_height = 16
        col = event.x // (aquascii_cell_width + self.char_spacing)
        row = event.y // (aquascii_cell_height + self.char_spacing)
        idx = row * 8 + col
        if 0 <= idx < len(self.aquascii_images_selector):
            self.active_char = idx
            self.draw_aquascii_overlay()
            self.update_char_preview()

    def draw_aquascii_overlay(self):
        # Use fixed 16x16 cell size for selector panel
        aquascii_cell_width = 16
        aquascii_cell_height = 16
        self.aquascii_canvas.delete("active_overlay")
        ax = (self.active_char % 8) * (aquascii_cell_width + self.char_spacing)
        ay = (self.active_char // 8) * (aquascii_cell_height + self.char_spacing)
        self.aquascii_canvas.create_rectangle(ax, ay, ax+aquascii_cell_width, ay+aquascii_cell_height, outline="#FF0000", width=2, tags="active_overlay")

    # ...Screen grid drawing removed...

    # ...Screen draw handler removed...

    # ...Screen click handler removed...

    # ...Screen drag handler removed...


    def get_grid_params(self):
        col_mode = self.col_mode_var.get()
        if col_mode == "80":
            pixel_width = 1
            pixel_height = 2
            cols = 80
            cell_width = pixel_width * 8  # 8
            cell_height = pixel_height * 8  # 16
            border_cols = 6  # 6 character border for 80-col mode
        else:
            pixel_width = 2
            pixel_height = 2
            cols = 40
            cell_width = pixel_width * 8  # 16
            cell_height = pixel_height * 8  # 16
            border_cols = 3  # 3 character border for 40-col mode
        rows = 25
        border_rows = 3  # Always 3 rows for top/bottom border
        return cell_width, cell_height, cols, rows, border_cols, border_rows

    # ...Screen grid update removed...

    def on_col_mode_change(self, *args):
        # Only update Paint char preview width, no legacy update calls to Screen panel
        self.update_char_preview()

    # ...Screen tab activation logic removed...
