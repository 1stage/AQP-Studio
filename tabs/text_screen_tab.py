import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk

class TextScreenTab(ttk.Frame):
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
        # Add grid toggle variable
        self.show_grid_var = tk.BooleanVar(value=True)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#808080", borderwidth=0)
        style.configure("TNotebook.Tab", background="#A0A0A0", font=("Arial", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#D0D0D0")])

        # Top controls: mode toggles
        mode_frame = tk.Frame(self, bg="#D0D0D0")
        mode_frame.pack(fill=tk.X, pady=(10,4))
        self.col_mode_var = tk.StringVar(value="40")
        tk.Label(mode_frame, text="Screen Mode:", bg="#D0D0D0", font=("Arial", 10)).pack(side=tk.LEFT, padx=(10,2))
        tk.Radiobutton(mode_frame, text="40 Col", variable=self.col_mode_var, value="40", bg="#D0D0D0").pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="80 Col", variable=self.col_mode_var, value="80", bg="#D0D0D0").pack(side=tk.LEFT)
        # Paint mode toggles
        self.paint_char_var = tk.BooleanVar(value=True)
        self.paint_fg_var = tk.BooleanVar(value=True)
        self.paint_bg_var = tk.BooleanVar(value=True)
        tk.Label(mode_frame, text="Paint:", bg="#D0D0D0", font=("Arial", 10)).pack(side=tk.LEFT, padx=(20,2))
        tk.Checkbutton(mode_frame, text="Char", variable=self.paint_char_var, bg="#D0D0D0").pack(side=tk.LEFT)
        tk.Checkbutton(mode_frame, text="FG", variable=self.paint_fg_var, bg="#D0D0D0").pack(side=tk.LEFT)
        tk.Checkbutton(mode_frame, text="BG", variable=self.paint_bg_var, bg="#D0D0D0").pack(side=tk.LEFT)
        tk.Checkbutton(mode_frame, text="Show Grid", variable=self.show_grid_var, bg="#D0D0D0", command=self.update_screen_grid).pack(side=tk.LEFT, padx=(20,2))

        # Main layout: left = AQUASCII selector, center = screen grid, right = palette selector
        editor_layout = tk.Frame(self, bg="#D0D0D0")
        editor_layout.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Calculate cell size and grid params before AQUASCII panel
        self.border_pixels = 48  # Fixed border size in actual pixels
        self.active_width = 640  # Active screen width in pixels
        self.active_height = 400 # Active screen height in pixels
        self.border_chars = 3    # Border size in characters
        self.cell_width, self.cell_height, self.cols, self.rows = self.get_grid_params()
        self.total_cols = self.cols + 2 * self.border_chars
        self.total_rows = self.rows + 2 * self.border_chars

        # AQUASCII character selector panel with label and spacing
        self.char_spacing = 2  # Space between characters in pixels
        self.active_char = 65  # Default to capital A (ninth row, second column)
            # AQUASCII character selector panel with label and spacing
        aquascii_canvas_width = 8 * self.cell_width + (8 - 1) * self.char_spacing
        aquascii_canvas_height = 32 * self.cell_height + (32 - 1) * self.char_spacing
        aquascii_panel_width = aquascii_canvas_width + 24  # Add extra width for label and padding
        aquascii_panel = tk.LabelFrame(editor_layout, text="AQUASCII", bg="#D0D0D0", width=aquascii_panel_width)
        aquascii_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0,16), ipadx=8, ipady=8)
        self.aquascii_canvas = tk.Canvas(aquascii_panel, width=aquascii_canvas_width, height=aquascii_canvas_height, bg="#FFFFFF", highlightthickness=0, bd=0)
        self.aquascii_canvas.pack(side=tk.TOP, fill=tk.Y, padx=8, pady=8)
        self.aquascii_canvas.bind("<Button-1>", self.on_aquascii_click)

        # Palette selector (16x2 grid placeholder)
        palette_frame = tk.LabelFrame(editor_layout, text="Palette", bg="#D0D0D0", width=80)
        palette_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
        self.palette_labels = []
        for row in range(2):
            row_labels = []
            for col in range(16):
                lbl = tk.Label(palette_frame, text="", width=2, height=1, bg="#C0C0C0", relief=tk.RIDGE)
                lbl.grid(row=row, column=col, padx=1, pady=1)
                row_labels.append(lbl)
            self.palette_labels.append(row_labels)

            # Load AQUASCII character images (choose PNG or BIN)
            self.aquascii_images = []
            try:
                target_width = self.cell_width
                target_height = self.cell_height
                # Uncomment one of the following lines to choose source:
                # images = self.load_aquascii_png("assets/aquascii.png", target_width, target_height)
                images = self.load_aquascii_bin("assets/aquascii.bin", target_width, target_height)
                self.aquascii_images = images  # Store as attribute to prevent GC
            except Exception as err:
                print("Failed to load AQUASCII character set:", err)
        # Draw all character images with spacing
        self.aquascii_canvas_images = []
        for idx in range(32*8):
            row = idx // 8
            col = idx % 8
            x = col * (self.cell_width + self.char_spacing)
            y = row * (self.cell_height + self.char_spacing)
            if idx < len(self.aquascii_images):
                img_id = self.aquascii_canvas.create_image(x, y, anchor="nw", image=self.aquascii_images[idx])
                self.aquascii_canvas_images.append(img_id)
        self.draw_aquascii_overlay()

        # Main screen grid (contiguous pixel field)
        screen_frame = tk.LabelFrame(editor_layout, text="Screen", bg="#D0D0D0", width=736, height=496)
        screen_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
        self.screen_canvas = tk.Canvas(screen_frame, width=736, height=496, bg="#E0E0E0", highlightthickness=0)
        self.screen_canvas.pack(side=tk.TOP, anchor="n", padx=16, pady=16)
        # Initialize screen buffer (all space character, code 32)
        self.screen_buffer = [[32 for _ in range(self.total_cols)] for _ in range(self.total_rows)]
        # Bind events and register callbacks after creating screen_canvas and screen_buffer
        self.screen_canvas.bind("<Button-1>", self.on_screen_click)
        self.screen_canvas.bind("<B1-Motion>", self.on_screen_drag)
        # Ensure grid is visible at launch
        self.update_screen_grid()
        self.col_mode_var.trace_add("write", self.on_col_mode_change)

    def on_aquascii_click(self, event):
        # Determine which character cell was clicked
        col = event.x // (self.cell_width + self.char_spacing)
        row = event.y // (self.cell_height + self.char_spacing)
        idx = row * 8 + col
        if 0 <= idx < len(self.aquascii_images):
            self.active_char = idx
            self.draw_aquascii_overlay()

    def draw_aquascii_overlay(self):
        # Remove previous overlay
        self.aquascii_canvas.delete("active_overlay")
        ax = (self.active_char % 8) * (self.cell_width + self.char_spacing)
        ay = (self.active_char // 8) * (self.cell_height + self.char_spacing)
        self.aquascii_canvas.create_rectangle(ax, ay, ax+self.cell_width, ay+self.cell_height, outline="#FF0000", width=2, tags="active_overlay")
    def draw_screen_grid(self):
        # Draw AQUASCII characters in each cell according to self.screen_buffer
        self.screen_canvas.delete("charimg")
        for row in range(self.total_rows):
            for col in range(self.total_cols):
                char_code = self.screen_buffer[row][col]
                if 0 <= char_code < len(self.aquascii_images):
                    x = col * self.cell_width
                    y = row * self.cell_height
                    self.screen_canvas.create_image(x, y, anchor="nw", image=self.aquascii_images[char_code], tags="charimg")


    def handle_screen_draw(self, event):
        col = event.x // self.cell_width
        row = event.y // self.cell_height
        active_start_col = self.border_chars
        active_end_col = self.total_cols - self.border_chars
        active_start_row = self.border_chars
        active_end_row = self.total_rows - self.border_chars

        # Border logic
        if (row < self.border_chars or row >= self.total_rows - self.border_chars or
            col < self.border_chars or col >= self.total_cols - self.border_chars):
            for r in range(self.total_rows):
                for c in range(self.total_cols):
                    if (r < self.border_chars or r >= self.total_rows - self.border_chars or
                        c < self.border_chars or c >= self.total_cols - self.border_chars):
                        self.screen_buffer[r][c] = self.active_char
            self.screen_buffer[self.border_chars][self.border_chars] = self.active_char
            self.update_screen_grid()
            return

        # First cell of active area
        if row == active_start_row and col == active_start_col:
            for r in range(self.total_rows):
                for c in range(self.total_cols):
                    if (r < self.border_chars or r >= self.total_rows - self.border_chars or
                        c < self.border_chars or c >= self.total_cols - self.border_chars):
                        self.screen_buffer[r][c] = self.active_char
            self.screen_buffer[self.border_chars][self.border_chars] = self.active_char
            self.update_screen_grid()
            return

        # Other active area cell
        if (active_start_col <= col < active_end_col and active_start_row <= row < active_end_row):
            self.screen_buffer[row][col] = self.active_char
            self.update_screen_grid()

    def on_screen_click(self, event):
        self.handle_screen_draw(event)

    def on_screen_drag(self, event):
        self.handle_screen_draw(event)


    def get_grid_params(self):
        col_mode = self.col_mode_var.get()
        if col_mode == "80":
            pixel_width = 1
            pixel_height = 2
            cols = 80
            cell_width = pixel_width * 8  # 8
            cell_height = pixel_height * 8  # 16
        else:
            pixel_width = 2
            pixel_height = 2
            cols = 40
            cell_width = pixel_width * 8  # 16
            cell_height = pixel_height * 8  # 16
        rows = 25
        return cell_width, cell_height, cols, rows

    def update_screen_grid(self):
        self.screen_canvas.delete("gridline")
        self.draw_screen_grid()  # Always draw characters first
        if self.show_grid_var.get():
            # Only grid the active area, not the border
            start_col = self.border_chars
            end_col = self.total_cols - self.border_chars
            start_row = self.border_chars
            end_row = self.total_rows - self.border_chars
            # Draw vertical grid lines for active area
            for col in range(start_col, end_col + 1):
                x = col * self.cell_width
                self.screen_canvas.create_line(x, start_row * self.cell_height, x, end_row * self.cell_height, fill="#A0A0A0", tags="gridline")
            # Draw horizontal grid lines for active area
            for row in range(start_row, end_row + 1):
                y = row * self.cell_height
                self.screen_canvas.create_line(start_col * self.cell_width, y, end_col * self.cell_width, y, fill="#A0A0A0", tags="gridline")

    def on_col_mode_change(self, *args):
        # Redraw grid with new pixel size and dimensions
        self.cell_width, self.cell_height, self.cols, self.rows = self.get_grid_params()
        self.total_cols = self.cols + 2 * self.border_chars
        self.total_rows = self.rows + 2 * self.border_chars
        canvas_width = self.border_pixels * 2 + self.cols * self.cell_width  # 736
        canvas_height = self.border_pixels * 2 + self.rows * self.cell_height  # 496
        self.screen_canvas.config(width=canvas_width, height=canvas_height)
        # Remove all rectangles and redraw
        self.screen_canvas.delete("all")
        self.cell_rects = []
        for row in range(self.total_rows):
            row_rects = []
            for col in range(self.total_cols):
                x0 = col * self.cell_width
                y0 = row * self.cell_height
                x1 = x0 + self.cell_width
                y1 = y0 + self.cell_height
                # Clamp right/bottom edge to canvas size
                if col == self.total_cols - 1:
                    x1 = canvas_width
                if row == self.total_rows - 1:
                    y1 = canvas_height
                # Fill border and active area with cyan BG and black FG
                if (row < self.border_chars or row >= self.total_rows - self.border_chars or
                    col < self.border_chars or col >= self.total_cols - self.border_chars):
                    # Border cell
                    rect = self.screen_canvas.create_rectangle(x0, y0, x1, y1, outline="", fill="#00FFFF")
                    fg_margin_x = self.cell_width // 4
                    fg_margin_y = self.cell_height // 4
                    fg_x0 = x0 + fg_margin_x
                    fg_y0 = y0 + fg_margin_y
                    fg_x1 = x1 - fg_margin_x
                    fg_y1 = y1 - fg_margin_y
                    self.screen_canvas.create_rectangle(fg_x0, fg_y0, fg_x1, fg_y1, outline="", fill="#000000")
                else:
                    # Active cell
                    rect = self.screen_canvas.create_rectangle(x0, y0, x1, y1, outline="", fill="#00FFFF")
                    fg_margin_x = self.cell_width // 4
                    fg_margin_y = self.cell_height // 4
                    fg_x0 = x0 + fg_margin_x
                    fg_y0 = y0 + fg_margin_y
                    fg_x1 = x1 - fg_margin_x
                    fg_y1 = y1 - fg_margin_y
                    self.screen_canvas.create_rectangle(fg_x0, fg_y0, fg_x1, fg_y1, outline="", fill="#000000")
                row_rects.append(rect)
            self.cell_rects.append(row_rects)

    def on_tab_active(self):
        # Call this when the tab becomes active to sync grid overlay
        self.update_screen_grid()
