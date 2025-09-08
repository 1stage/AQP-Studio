import tkinter as tk
from tkinter import ttk

class TextScreenTab(ttk.Frame):
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

        # AQUASCII character selector (8x32 grid)
        char_selector_frame = tk.LabelFrame(editor_layout, text="AQUASCII", bg="#D0D0D0", width=80)
        char_selector_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
        self.char_labels = []
        for row in range(32):
            row_labels = []
            for col in range(8):
                lbl = tk.Label(char_selector_frame, text="", width=2, height=1, bg="#E0E0E0", relief=tk.RIDGE)
                lbl.grid(row=row, column=col, padx=1, pady=1)
                row_labels.append(lbl)
            self.char_labels.append(row_labels)

        # Main screen grid (contiguous pixel field)
        screen_frame = tk.LabelFrame(editor_layout, text="Screen", bg="#D0D0D0")
        screen_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))
        self.screen_canvas = tk.Canvas(screen_frame, width=320, height=200, bg="#FFFFFF", highlightthickness=0)
        self.screen_canvas.pack(expand=True, fill=tk.BOTH)
        # Border size in characters
        self.border_pixels = 48  # Fixed border size in actual pixels
        # Set pixel size and grid size based on column mode
        self.cell_width, self.cell_height, self.cols, self.rows = self.get_grid_params()
        # Total grid size (active area)
        self.total_cols = self.cols
        self.total_rows = self.rows
        canvas_width = self.total_cols * self.cell_width + 2 * self.border_pixels
        canvas_height = self.total_rows * self.cell_height + 2 * self.border_pixels
        self.screen_canvas.config(width=canvas_width, height=canvas_height)

        # Draw grid with border
        self.cell_rects = []
        for row in range(self.total_rows):
            row_rects = []
            for col in range(self.total_cols):
                x0 = self.border_pixels + col * self.cell_width
                y0 = self.border_pixels + row * self.cell_height
                x1 = x0 + self.cell_width
                y1 = y0 + self.cell_height
                # Border cells: fill with different color for now
                fill = "#F8F8F8"
                rect = self.screen_canvas.create_rectangle(x0, y0, x1, y1, outline="", fill=fill)
                row_rects.append(rect)
            self.cell_rects.append(row_rects)

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

        # Register callback only once
        self.col_mode_var.trace_add("write", self.on_col_mode_change)
        # Ensure grid overlay matches control on launch
        self.update_screen_grid()

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
        if self.show_grid_var.get():
            # Draw vertical grid lines
            for col in range(self.total_cols + 1):
                x = self.border_pixels + col * self.cell_width
                self.screen_canvas.create_line(x, self.border_pixels, x, self.border_pixels + self.total_rows * self.cell_height, fill="#A0A0A0", tags="gridline")
            # Draw horizontal grid lines
            for row in range(self.total_rows + 1):
                y = self.border_pixels + row * self.cell_height
                self.screen_canvas.create_line(self.border_pixels, y, self.border_pixels + self.total_cols * self.cell_width, y, fill="#A0A0A0", tags="gridline")

    def on_col_mode_change(self, *args):
        # Redraw grid with new pixel size and dimensions
        self.cell_width, self.cell_height, self.cols, self.rows = self.get_grid_params()
        self.total_cols = self.cols
        self.total_rows = self.rows
        canvas_width = self.total_cols * self.cell_width + 2 * self.border_pixels
        canvas_height = self.total_rows * self.cell_height + 2 * self.border_pixels
        self.screen_canvas.config(width=canvas_width, height=canvas_height)
        # Remove all rectangles and redraw
        self.screen_canvas.delete("all")
        self.cell_rects = []
        for row in range(self.total_rows):
            row_rects = []
            for col in range(self.total_cols):
                x0 = self.border_pixels + col * self.cell_width
                y0 = self.border_pixels + row * self.cell_height
                x1 = x0 + self.cell_width
                y1 = y0 + self.cell_height
                fill = "#F8F8F8"
                rect = self.screen_canvas.create_rectangle(x0, y0, x1, y1, outline="", fill=fill)
                row_rects.append(rect)
            self.cell_rects.append(row_rects)
        self.update_screen_grid()

    def on_tab_active(self):
        # Call this when the tab becomes active to sync grid overlay
        self.update_screen_grid()
