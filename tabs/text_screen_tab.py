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
        try:
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
        except Exception as e:
            print("Failed to load AQUASCII BIN:", e)
        return chars
    def load_aquascii_png(self, path, target_width, target_height):
        """Load AQUASCII characters from a PNG image as 8x8 blocks, left-to-right, top-to-bottom, resized to target size."""
        img = Image.open(path)
        char_width, char_height = 8, 8
        img_width, img_height = img.size
        blocks_per_row = img_width // char_width
        blocks_per_col = img_height // char_height
        chars = []
        for block_idx in range(blocks_per_row * blocks_per_col):
            row = block_idx // blocks_per_row
            col = block_idx % blocks_per_row
            left = col * char_width
            upper = row * char_height
            right = left + char_width
            lower = upper + char_height
            char_img = img.crop((left, upper, right, lower))
            char_img = char_img.resize((target_width, target_height), Image.NEAREST)
            chars.append(ImageTk.PhotoImage(char_img))
        return chars
    def __init__(self, parent):
        super().__init__(parent)
        # ...existing code...
        self.show_grid_var = tk.BooleanVar(value=True)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#808080", borderwidth=0)
        style.configure("TNotebook.Tab", background="#A0A0A0", font=("Arial", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#D0D0D0")])

        self.main_frame = tk.Frame(self, bg="#D0D0D0")
        self.main_frame.pack(fill=tk.X)
        self.col_mode_var = tk.StringVar(value="40")

        editor_layout = tk.Frame(self, bg="#D0D0D0")
        editor_layout.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.border_pixels = 48
        self.cell_width, self.cell_height, self.cols, self.rows, self.border_cols, self.border_rows = self.get_grid_params()
        self.total_cols = self.cols + 2 * self.border_cols
        self.total_rows = self.rows + 2 * self.border_rows

        # AQUASCII character selector panel
        aquascii_cell_width = 16
        aquascii_cell_height = 16
        self.char_spacing = 2
        self.active_char = 65
        aquascii_canvas_width = 8 * aquascii_cell_width + (8 - 1) * self.char_spacing
        aquascii_canvas_height = 32 * aquascii_cell_height + (32 - 1) * self.char_spacing
        aquascii_panel_width = aquascii_canvas_width + 24
        aquascii_panel = tk.LabelFrame(editor_layout, text="AQUASCII", bg="#D0D0D0", width=aquascii_panel_width)
        aquascii_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0,16), ipadx=8, ipady=8)
        self.aquascii_canvas = tk.Canvas(aquascii_panel, width=aquascii_canvas_width, height=aquascii_canvas_height, bg="#FFFFFF", highlightthickness=0, bd=0)
        self.aquascii_canvas.pack(side=tk.TOP, fill=tk.Y, padx=8, pady=8)
        self.aquascii_canvas.bind("<Button-1>", self.on_aquascii_click)

        palette_and_controls_frame = tk.Frame(editor_layout, bg="#D0D0D0", width=260)
        palette_and_controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)

        palette_frame = tk.LabelFrame(palette_and_controls_frame, text="Palette", bg="#D0D0D0")
        palette_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=0)
        self.fg_labels = []
        self.bg_labels = []
        self.selected_fg_idx = 0
        self.selected_bg_idx = 7

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
        for col in range(4):
            fg_frame.grid_columnconfigure(col, weight=1)
        for row in range(4):
            row_labels = []
            for col in range(4):
                idx = row * 4 + col
                rgb = aquarius_palette[idx]
                color = f'#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}'
                border_color = "#FF0000" if idx == self.selected_fg_idx else "#D0D0D0"
                lbl = tk.Label(fg_frame, text="", width=4, height=1, bg=color, highlightbackground=border_color, highlightcolor=border_color, highlightthickness=4, bd=0, borderwidth=0)
                lbl.grid(row=row, column=col, padx=8, pady=1, sticky="ew")
                lbl.bind("<Button-1>", lambda e, i=idx: self.select_fg_swatch(i))
                row_labels.append(lbl)
            self.fg_labels.append(row_labels)

        bg_frame = tk.LabelFrame(palette_frame, text="BG", bg="#D0D0D0")
        bg_frame.grid(row=1, column=0, padx=2, pady=(8,2), sticky="ew")
        for col in range(4):
            bg_frame.grid_columnconfigure(col, weight=1)
        for row in range(4):
            row_labels = []
            for col in range(4):
                idx = row * 4 + col
                rgb = aquarius_palette[idx]
                color = f'#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}'
                border_color = "#FF0000" if idx == self.selected_bg_idx else "#D0D0D0"
                lbl = tk.Label(bg_frame, text="", width=4, height=1, bg=color, highlightbackground=border_color, highlightcolor=border_color, highlightthickness=4, bd=0, borderwidth=0)
                lbl.grid(row=row, column=col, padx=8, pady=1, sticky="ew")
                lbl.bind("<Button-1>", lambda e, i=idx: self.select_bg_swatch(i))
                row_labels.append(lbl)
            self.bg_labels.append(row_labels)

        # Controls: mode toggles
        mode_frame = tk.LabelFrame(palette_and_controls_frame, text="Controls", bg="#D0D0D0")
        mode_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(10,4))

        # Screen Mode sub-section
        screen_mode_section = tk.LabelFrame(mode_frame, text="Screen Mode", bg="#D0D0D0")
        screen_mode_section.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(8,4))
        tk.Radiobutton(screen_mode_section, text="40 Col", variable=self.col_mode_var, value="40", bg="#D0D0D0").pack(side=tk.LEFT, padx=4, pady=2)
        tk.Radiobutton(screen_mode_section, text="80 Col", variable=self.col_mode_var, value="80", bg="#D0D0D0").pack(side=tk.LEFT, padx=4, pady=2)
        self.col_mode_var.trace_add("write", self.on_col_mode_change)

        # Paint sub-section
        self.paint_char_var = tk.BooleanVar(value=True)
        self.paint_fg_var = tk.BooleanVar(value=True)
        self.paint_bg_var = tk.BooleanVar(value=True)
        paint_section = tk.LabelFrame(mode_frame, text="Paint", bg="#D0D0D0")
        paint_section.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(4,4))
        tk.Checkbutton(paint_section, text="Char", variable=self.paint_char_var, bg="#D0D0D0").pack(side=tk.LEFT, padx=4, pady=2)
        tk.Checkbutton(paint_section, text="FG", variable=self.paint_fg_var, bg="#D0D0D0").pack(side=tk.LEFT, padx=4, pady=2)
        tk.Checkbutton(paint_section, text="BG", variable=self.paint_bg_var, bg="#D0D0D0").pack(side=tk.LEFT, padx=4, pady=2)

        # Show Grid sub-section
        show_grid_section = tk.LabelFrame(mode_frame, text="Visual Aids", bg="#D0D0D0")
        show_grid_section.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(4,8))
        tk.Checkbutton(show_grid_section, text="Show Grid", variable=self.show_grid_var, bg="#D0D0D0", command=self.update_screen_grid).pack(side=tk.LEFT, padx=4, pady=2)

        # Load AQUASCII character images (choose PNG or BIN)
        self.aquascii_images = []
        try:
            target_width = self.cell_width
            target_height = self.cell_height
            if self.cols == 80:
                target_width = 8
                target_height = 16
            else:
                target_width = 16
                target_height = 16
            images = self.load_aquascii_bin("assets/aquascii.bin", target_width, target_height)
            self.aquascii_images = images
        except Exception as err:
            print("Failed to load AQUASCII character set:", err)

        self.aquascii_images_selector = []
        try:
            images_selector = self.load_aquascii_bin("assets/aquascii.bin", 16, 16)
            self.aquascii_images_selector = images_selector
        except Exception as err:
            print("Failed to load AQUASCII character set for selector:", err)
        self.aquascii_canvas_images = []
        for idx in range(32*8):
            row = idx // 8
            col = idx % 8
            x = col * (aquascii_cell_width + self.char_spacing)
            y = row * (aquascii_cell_height + self.char_spacing)
            if idx < len(self.aquascii_images_selector):
                img_id = self.aquascii_canvas.create_image(x, y, anchor="nw", image=self.aquascii_images_selector[idx])
                self.aquascii_canvas_images.append(img_id)
        self.draw_aquascii_overlay()

        self.aquascii_images_grid = []
        try:
            if self.cols == 80:
                images_grid = self.load_aquascii_bin("assets/aquascii.bin", 8, 16)
            else:
                images_grid = self.load_aquascii_bin("assets/aquascii.bin", 16, 16)
            self.aquascii_images_grid = images_grid
        except Exception as err:
            print("Failed to load AQUASCII character set for grid:", err)

        self.screen_frame = tk.LabelFrame(editor_layout, text="Screen", bg="#D0D0D0", width=736, height=496)
        self.screen_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
        self.screen_canvas = tk.Canvas(self.screen_frame, width=736, height=496, bg="#E0E0E0", highlightthickness=0)
        self.screen_canvas.pack(side=tk.TOP, anchor="n", padx=16, pady=16)
        self.screen_buffer = [[32 for _ in range(self.total_cols)] for _ in range(self.total_rows)]
        self.right_80_buffer = None
        self.screen_canvas.bind("<Button-1>", self.on_screen_click)
        self.screen_canvas.bind("<B1-Motion>", self.on_screen_drag)
        self.screen_canvas.bind("<Button-3>", self.on_screen_right_click)
        self.update_screen_grid()
    def select_fg_swatch(self, idx):
        self.selected_fg_idx = idx
        for row in self.fg_labels:
            for lbl in row:
                lbl.config(highlightbackground="#D0D0D0", highlightcolor="#D0D0D0")
        fg_row = idx // 4
        fg_col = idx % 4
        self.fg_labels[fg_row][fg_col].config(highlightbackground="#FF0000", highlightcolor="#FF0000")

    def select_bg_swatch(self, idx):
        self.selected_bg_idx = idx
        for row in self.bg_labels:
            for lbl in row:
                lbl.config(highlightbackground="#D0D0D0", highlightcolor="#D0D0D0")
        bg_row = idx // 4
        bg_col = idx % 4
        self.bg_labels[bg_row][bg_col].config(highlightbackground="#FF0000", highlightcolor="#FF0000")
    def select_fg_swatch(self, idx):
        self.selected_fg_idx = idx
        for row in self.fg_labels:
            for lbl in row:
                lbl.config(highlightbackground="#D0D0D0", highlightcolor="#D0D0D0")
        fg_row = idx // 4
        fg_col = idx % 4
        self.fg_labels[fg_row][fg_col].config(highlightbackground="#FF0000", highlightcolor="#FF0000")

    def select_bg_swatch(self, idx):
        self.selected_bg_idx = idx
        for row in self.bg_labels:
            for lbl in row:
                lbl.config(highlightbackground="#D0D0D0", highlightcolor="#D0D0D0")
        bg_row = idx // 4
        bg_col = idx % 4
        self.bg_labels[bg_row][bg_col].config(highlightbackground="#FF0000", highlightcolor="#FF0000")

        # Controls: mode toggles
        mode_frame = tk.LabelFrame(palette_and_controls_frame, text="Controls", bg="#D0D0D0")
        mode_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(10,4))

        # Screen Mode sub-section
        screen_mode_section = tk.LabelFrame(mode_frame, text="Screen Mode", bg="#D0D0D0")
        screen_mode_section.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(8,4))
        tk.Radiobutton(screen_mode_section, text="40 Col", variable=self.col_mode_var, value="40", bg="#D0D0D0").pack(side=tk.LEFT, padx=4, pady=2)
        tk.Radiobutton(screen_mode_section, text="80 Col", variable=self.col_mode_var, value="80", bg="#D0D0D0").pack(side=tk.LEFT, padx=4, pady=2)
        self.col_mode_var.trace_add("write", self.on_col_mode_change)

        # Paint sub-section
        self.paint_char_var = tk.BooleanVar(value=True)
        self.paint_fg_var = tk.BooleanVar(value=True)
        self.paint_bg_var = tk.BooleanVar(value=True)
        paint_section = tk.LabelFrame(mode_frame, text="Paint", bg="#D0D0D0")
        paint_section.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(4,4))
        tk.Checkbutton(paint_section, text="Char", variable=self.paint_char_var, bg="#D0D0D0").pack(side=tk.LEFT, padx=4, pady=2)
        tk.Checkbutton(paint_section, text="FG", variable=self.paint_fg_var, bg="#D0D0D0").pack(side=tk.LEFT, padx=4, pady=2)
        tk.Checkbutton(paint_section, text="BG", variable=self.paint_bg_var, bg="#D0D0D0").pack(side=tk.LEFT, padx=4, pady=2)

        # Show Grid sub-section
        show_grid_section = tk.LabelFrame(mode_frame, text="Visual Aids", bg="#D0D0D0")
        show_grid_section.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(4,8))
        tk.Checkbutton(show_grid_section, text="Show Grid", variable=self.show_grid_var, bg="#D0D0D0", command=self.update_screen_grid).pack(side=tk.LEFT, padx=4, pady=2)

        # Load AQUASCII character images (choose PNG or BIN)
        self.aquascii_images = []
        try:
            # For screen grid, use cell_width/cell_height
            target_width = self.cell_width
            target_height = self.cell_height
            # For 80-col mode, use 8x16; for 40-col, use 16x16
            if self.cols == 80:
                target_width = 8
                target_height = 16
            else:
                target_width = 16
                target_height = 16
            # images = self.load_aquascii_png("assets/aquascii.png", target_width, target_height)
            images = self.load_aquascii_bin("assets/aquascii.bin", target_width, target_height)
            self.aquascii_images = images  # Store as attribute to prevent GC
        except Exception as err:
            print("Failed to load AQUASCII character set:", err)

        # Load AQUASCII character images for selector panel (always 16x16)
        self.aquascii_images_selector = []
        try:
            images_selector = self.load_aquascii_bin("assets/aquascii.bin", 16, 16)
            self.aquascii_images_selector = images_selector
        except Exception as err:
            print("Failed to load AQUASCII character set for selector:", err)
        # Draw all character images with spacing (selector panel)
        self.aquascii_canvas_images = []
        for idx in range(32*8):
            row = idx // 8
            col = idx % 8
            x = col * (aquascii_cell_width + self.char_spacing)
            y = row * (aquascii_cell_height + self.char_spacing)
            if idx < len(self.aquascii_images_selector):
                img_id = self.aquascii_canvas.create_image(x, y, anchor="nw", image=self.aquascii_images_selector[idx])
                self.aquascii_canvas_images.append(img_id)
        self.draw_aquascii_overlay()
        # Load AQUASCII character images for screen grid (correct pixel scaling)
        self.aquascii_images_grid = []
        try:
            if self.cols == 80:
                # 80-column: 8x16, each logical pixel is 1x2
                images_grid = self.load_aquascii_bin("assets/aquascii.bin", 8, 16)
            else:
                # 40-column: 16x16, each logical pixel is 2x2
                images_grid = self.load_aquascii_bin("assets/aquascii.bin", 16, 16)
            self.aquascii_images_grid = images_grid
        except Exception as err:
            print("Failed to load AQUASCII character set for grid:", err)

        # Main screen grid (contiguous pixel field)
        self.screen_frame = tk.LabelFrame(editor_layout, text="Screen", bg="#D0D0D0", width=736, height=496)
        self.screen_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
        self.screen_canvas = tk.Canvas(self.screen_frame, width=736, height=496, bg="#E0E0E0", highlightthickness=0)
        self.screen_canvas.pack(side=tk.TOP, anchor="n", padx=16, pady=16)
        # Initialize screen buffer (all space character, code 32)
        self.screen_buffer = [[32 for _ in range(self.total_cols)] for _ in range(self.total_rows)]
        # Add buffer for right half of 80-column screen
        self.right_80_buffer = None
        # Bind events and register callbacks after creating screen_canvas and screen_buffer
        self.screen_canvas.bind("<Button-1>", self.on_screen_click)
        self.screen_canvas.bind("<B1-Motion>", self.on_screen_drag)
        self.screen_canvas.bind("<Button-3>", self.on_screen_right_click)
        # Ensure grid and background are visible at launch
        self.update_screen_grid()

    def on_screen_right_click(self, event):
        col = event.x // self.cell_width
        row = event.y // self.cell_height
        active_start_col = self.border_cols
        active_end_col = self.total_cols - self.border_cols
        active_start_row = self.border_rows
        active_end_row = self.total_rows - self.border_rows

        # Only pick up character if in active area
        if (active_start_col <= col < active_end_col and active_start_row <= row < active_end_row):
            picked_char = self.screen_buffer[row][col]
            if 0 <= picked_char < len(self.aquascii_images):
                self.active_char = picked_char
                self.draw_aquascii_overlay()

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

    def draw_aquascii_overlay(self):
        # Use fixed 16x16 cell size for selector panel
        aquascii_cell_width = 16
        aquascii_cell_height = 16
        self.aquascii_canvas.delete("active_overlay")
        ax = (self.active_char % 8) * (aquascii_cell_width + self.char_spacing)
        ay = (self.active_char // 8) * (aquascii_cell_height + self.char_spacing)
        self.aquascii_canvas.create_rectangle(ax, ay, ax+aquascii_cell_width, ay+aquascii_cell_height, outline="#FF0000", width=2, tags="active_overlay")

    def draw_screen_grid(self):
        # Draw AQUASCII characters in each cell according to self.screen_buffer
        self.screen_canvas.delete("charimg")
        for row in range(self.total_rows):
            for col in range(self.total_cols):
                char_code = self.screen_buffer[row][col]
                if 0 <= char_code < len(self.aquascii_images_grid):
                    x = col * self.cell_width
                    y = row * self.cell_height
                    self.screen_canvas.create_image(x, y, anchor="nw", image=self.aquascii_images_grid[char_code], tags="charimg")

    def handle_screen_draw(self, event):
        col = event.x // self.cell_width
        row = event.y // self.cell_height
        active_start_col = self.border_cols
        active_end_col = self.total_cols - self.border_cols
        active_start_row = self.border_rows
        active_end_row = self.total_rows - self.border_rows

        # Border logic
        if (row < self.border_rows or row >= self.total_rows - self.border_rows or
            col < self.border_cols or col >= self.total_cols - self.border_cols):
            for r in range(self.total_rows):
                for c in range(self.total_cols):
                    if (r < self.border_rows or r >= self.total_rows - self.border_rows or
                        c < self.border_cols or c >= self.total_cols - self.border_cols):
                        self.screen_buffer[r][c] = self.active_char
            self.screen_buffer[self.border_rows][self.border_cols] = self.active_char
            self.update_screen_grid()
            return

        # First cell of active area
        if row == active_start_row and col == active_start_col:
            for r in range(self.total_rows):
                for c in range(self.total_cols):
                    if (r < self.border_rows or r >= self.total_rows - self.border_rows or
                        c < self.border_cols or c >= self.total_cols - self.border_cols):
                        self.screen_buffer[r][c] = self.active_char
            self.screen_buffer[self.border_rows][self.border_cols] = self.active_char
            self.update_screen_grid()
            return

        # Other active area cell
        if (active_start_col <= col < active_end_col and active_start_row <= row < active_end_row):
            self.screen_buffer[row][col] = self.active_char
            self.update_screen_grid()

    def on_screen_click(self, event):
        col = event.x // self.cell_width
        row = event.y // self.cell_height
        self._prev_draw_cell = (col, row)
        self.handle_screen_draw(event)

    def on_screen_drag(self, event):
        col = event.x // self.cell_width
        row = event.y // self.cell_height
        prev = getattr(self, '_prev_draw_cell', None)
        curr = (col, row)
        if prev is not None and prev != curr:
            for y, x in self._interpolate_cells(prev, curr):
                # Only draw in active area
                active_start_col = self.border_cols
                active_end_col = self.total_cols - self.border_cols
                active_start_row = self.border_rows
                active_end_row = self.total_rows - self.border_rows
                if (active_start_col <= x < active_end_col and active_start_row <= y < active_end_row):
                    self.screen_buffer[y][x] = self.active_char
            self.update_screen_grid()
        self._prev_draw_cell = curr


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

    def update_screen_grid(self):
        self.screen_canvas.delete("gridline")
        self.draw_screen_grid()  # Always draw characters first
        if self.show_grid_var.get():
            # Only grid the active area, not the border
            start_col = self.border_cols
            end_col = self.total_cols - self.border_cols
            start_row = self.border_rows
            end_row = self.total_rows - self.border_rows
            # Draw vertical grid lines for active area
            for col in range(start_col, end_col + 1):
                x = col * self.cell_width
                self.screen_canvas.create_line(x, start_row * self.cell_height, x, end_row * self.cell_height, fill="#A0A0A0", tags="gridline")
            # Draw horizontal grid lines for active area
            for row in range(start_row, end_row + 1):
                y = row * self.cell_height
                self.screen_canvas.create_line(start_col * self.cell_width, y, end_col * self.cell_width, y, fill="#A0A0A0", tags="gridline")

    def on_col_mode_change(self, *args):
        prev_cols = self.cols
        prev_rows = self.rows
        prev_total_cols = self.total_cols
        prev_total_rows = self.total_rows
        prev_buffer = self.screen_buffer
        prev_mode = "80" if self.cell_width == 8 else "40"
        # Update grid parameters and buffer for new mode
        self.cell_width, self.cell_height, self.cols, self.rows, self.border_cols, self.border_rows = self.get_grid_params()
        self.total_cols = self.cols + 2 * self.border_cols
        self.total_rows = self.rows + 2 * self.border_rows
        canvas_width = self.border_pixels * 2 + self.cols * self.cell_width
        canvas_height = self.border_pixels * 2 + self.rows * self.cell_height
        self.screen_canvas.config(width=canvas_width, height=canvas_height)
        # Recreate screen buffer for new grid size
        new_buffer = [[32 for _ in range(self.total_cols)] for _ in range(self.total_rows)]
        # Preserve right half of 80-column screen
        if prev_cols == 80:
            self.right_80_buffer = []
            for r in range(prev_total_rows):
                row_right = prev_buffer[r][self.border_cols+40:self.border_cols+80]
                self.right_80_buffer.append(row_right)
        # Map previous buffer to new buffer
        if self.cols == 80 and prev_cols == 40:
            # 40→80: Copy left 40 columns, restore right 40 if available
            for r in range(min(self.total_rows, prev_total_rows)):
                for c in range(40):
                    new_buffer[r][c+self.border_cols] = prev_buffer[r][c+3]  # 3 is previous border_cols
                # Restore right half if available
                if self.right_80_buffer and r < len(self.right_80_buffer):
                    for c in range(40):
                        new_buffer[r][c+self.border_cols+40] = self.right_80_buffer[r][c]
        elif self.cols == 40 and prev_cols == 80:
            # 80→40: Copy left 40 columns, preserve right half
            for r in range(min(self.total_rows, prev_total_rows)):
                for c in range(40):
                    new_buffer[r][c+3] = prev_buffer[r][c+6]  # 6 is previous border_cols
            # Save right half (already handled above)
        else:
            # Same mode, just copy
            for r in range(min(self.total_rows, prev_total_rows)):
                for c in range(min(self.total_cols, prev_total_cols)):
                    new_buffer[r][c] = prev_buffer[r][c]
        # Set border cells to match active area (0,0)
        border_char = new_buffer[self.border_rows][self.border_cols]
        for r in range(self.total_rows):
            for c in range(self.total_cols):
                if (r < self.border_rows or r >= self.total_rows - self.border_rows or
                    c < self.border_cols or c >= self.total_cols - self.border_cols):
                    new_buffer[r][c] = border_char
        self.screen_buffer = new_buffer
        # Reload AQUASCII images for grid with correct pixel scaling
        if self.cols == 80:
            self.aquascii_images_grid = self.load_aquascii_bin("assets/aquascii.bin", 8, 16)
        else:
            self.aquascii_images_grid = self.load_aquascii_bin("assets/aquascii.bin", 16, 16)
        # Redraw everything
        self.update_screen_grid()

    def on_tab_active(self):
        # Call this when the tab becomes active to sync grid overlay
        self.update_screen_grid()
