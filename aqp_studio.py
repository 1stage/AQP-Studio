import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class AQPStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("AQP Studio")
        self.root.configure(bg="#D0D0D0")  # 20% grey background
        self.image = None
        self.img_preview = None
        self.loaded_palette = None  # List of (R,G,B) tuples
        self.palette_var = tk.BooleanVar(value=True)
        self.force_palette_var = tk.BooleanVar(value=False)
        self.scaling_var = tk.StringVar(value="letterbox")
        self.sampling_var = tk.StringVar(value="bicubic")
        self.export_format_var = tk.StringVar(value="BMP4")
        self.setup_gui()

    def save_palette(self):
        # Get current palette (forced or preview)
        if self.force_palette_var.get() and self.loaded_palette:
            palette = list(self.loaded_palette)[:16]
            while len(palette) < 16:
                palette.append((0,0,0))
        else:
            palette = getattr(self, '_export_palette', [(0,0,0)]*16)
            palette = list(palette)[:16]
            while len(palette) < 16:
                palette.append((0,0,0))
        file_path = filedialog.asksaveasfilename(defaultextension=".pal", filetypes=[("Palette Files", "*.pal")])
        if not file_path:
            return
        try:
            with open(file_path, "w") as f:
                f.write("JASC-PAL\n0100\n16\n")
                for r, g, b in palette:
                    f.write(f"{r} {g} {b}\n")
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            with open("error_log.txt", "w") as ef:
                ef.write(f"Failed to save palette: {e}\n\n{tb}")
            messagebox.showerror("Error", f"Failed to save palette: {e}\nSee error_log.txt for details.")
    def set_export_image(self, img, palette):
        self._export_img = img
        self._export_palette = palette
    def get_padded_palette(self, img):
        pal = img.getpalette() if img.mode == "P" else None
        if pal is None:
            pal = [0] * 48
        else:
            pal = list(pal[:48])
            if len(pal) < 48:
                pal += [0] * (48 - len(pal))
        return [(pal[i*3], pal[i*3+1], pal[i*3+2]) for i in range(16)]
    def load_palette(self):
        file_path = filedialog.askopenfilename(filetypes=[("Palette Files", "*.pal")])
        if not file_path:
            return
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
            # JASC-PAL format: skip header
            if lines[0].strip() != "JASC-PAL":
                raise ValueError("Not a JASC-PAL file")
            count = int(lines[2].strip())
            palette = []
            for line in lines[3:3+count]:
                r, g, b = map(int, line.strip().split())
                palette.append((r, g, b))
            if len(palette) != 16:
                raise ValueError("Palette must have 16 colors")
            self.loaded_palette = palette
            # After loading palette, set Force palette on image checkbox
            self.force_palette_var.set(True)
            self.update_preview()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load palette: {e}")
    # Duplicate __init__ removed

    def setup_gui(self):
        from tkinter import ttk
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#808080", borderwidth=0)
        style.configure("TNotebook.Tab", background="#A0A0A0", font=("Arial", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#D0D0D0")])  # Matches frame background for selected tab

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # BMP4 tab
        bmp4_frame = tk.Frame(notebook, bg="#D0D0D0")
        notebook.add(bmp4_frame, text="BMP4 Images")

        # BMP1 tab (blank)
        bmp1_frame = tk.Frame(notebook, bg="#D0D0D0")
        notebook.add(bmp1_frame, text="BMP1 Images")
        tk.Label(bmp1_frame, text="BMP1 tools coming soon...", bg="#D0D0D0", font=("Arial", 14)).pack(pady=40)

        # All previous widget creation now goes inside bmp4_frame
        preview_frame = tk.Frame(bmp4_frame, bg="#D0D0D0")
        preview_frame.pack(pady=10, padx=20)

        preview_img_width = 480
        preview_img_height = 300

        import_btn_frame = tk.Frame(preview_frame, bg="#D0D0D0")
        import_btn_frame.pack(side=tk.LEFT, padx=(10, 10))
        import_icon = Image.open("assets/import_image.png")
        import_icon = import_icon.resize((64, 64), Image.NEAREST)
        self.import_icon_imgtk = ImageTk.PhotoImage(import_icon)
        self.import_btn = tk.Button(
            import_btn_frame,
            image=self.import_icon_imgtk,
            width=64,
            height=64,
            relief=tk.RAISED,
            bd=4,
            command=self.import_image
        )
        self.import_btn.pack()
        tk.Label(import_btn_frame, bg="#D0D0D0", text="Import Image", font=("Arial", 10)).pack(pady=(2,0))

        self.orig_img_box = tk.LabelFrame(preview_frame, bg="#D0D0D0", text=" Original Image ", width=preview_img_width+20, height=preview_img_height+36)
        self.orig_img_box.pack_propagate(False)
        self.orig_img_box.pack(side=tk.LEFT, padx=10)
        self.orig_img_label = tk.Label(self.orig_img_box, bg="#D0D0D0", text="Imported Image", fg="#B0B0B0", font=("Arial", 18))
        self.orig_img_label.pack(expand=True, fill=tk.BOTH)

        self.proc_img_box = tk.LabelFrame(preview_frame, bg="#D0D0D0", text=" Export Preview ", width=preview_img_width+20, height=preview_img_height+36)
        self.proc_img_box.pack_propagate(False)
        self.proc_img_box.pack(side=tk.LEFT, padx=10)
        self.proc_img_label = tk.Label(self.proc_img_box, bg="#D0D0D0", text="Exported Image", fg="#B0B0B0", font=("Arial", 18))
        self.proc_img_label.pack(expand=True, fill=tk.BOTH)

        export_btn_frame = tk.Frame(preview_frame, bg="#D0D0D0")
        export_btn_frame.pack(side=tk.LEFT, padx=(10, 10))
        export_icon = Image.open("assets/export_image.png")
        export_icon = export_icon.resize((64, 64), Image.NEAREST)
        self.export_icon_imgtk = ImageTk.PhotoImage(export_icon)
        self.export_btn = tk.Button(
            export_btn_frame,
            image=self.export_icon_imgtk,
            width=64,
            height=64,
            relief=tk.RAISED,
            bd=4,
            state=tk.DISABLED,
            command=self.export_image
        )
        self.export_btn.pack()
        tk.Label(export_btn_frame, text="Export Image", bg="#D0D0D0", font=("Arial", 10)).pack(pady=(2,0))
        export_format_frame = tk.LabelFrame(export_btn_frame, bg="#D0D0D0", text="Export Format")
        export_format_frame.pack(pady=(8,0))
        for fmt in ["BMP4", "PNG"]:
            tk.Radiobutton(export_format_frame, bg="#D0D0D0", text=fmt, variable=self.export_format_var, value=fmt, command=self.update_preview).pack(side=tk.LEFT)

        palette_section_frame = tk.Frame(bmp4_frame, bg="#D0D0D0")
        palette_section_frame.pack(pady=10, fill=tk.X)
        palette_section_frame.grid_columnconfigure(0, weight=1)
        palette_section_frame.grid_columnconfigure(1, weight=1)

        self.image_controls_frame = tk.LabelFrame(palette_section_frame, bg="#D0D0D0", padx="12", pady="4", text="Image Controls")
        self.image_controls_frame.grid(row=0, column=0, padx=(20,10), sticky="nsew")
        scaling_frame = tk.LabelFrame(self.image_controls_frame, bg="#D0D0D0", padx="6", borderwidth="0", text="Scaling")
        scaling_frame.pack(fill=tk.X, pady=(4,2))
        for mode in ["letterbox", "stretch", "fill"]:
            tk.Radiobutton(scaling_frame, bg="#D0D0D0", text=mode.title(), variable=self.scaling_var, value=mode, command=self.update_preview).pack(side=tk.LEFT)
        sampling_frame = tk.LabelFrame(self.image_controls_frame, bg="#D0D0D0", padx="6", borderwidth="0", text="Sampling")
        sampling_frame.pack(fill=tk.X, pady=(2,4))
        sampling_methods = ["bicubic", "bilinear", "lanczos", "nearest"]
        self.sampling_var.set("bicubic")  # Set Bicubic as default selection
        for method in sampling_methods:
            tk.Radiobutton(sampling_frame, bg="#D0D0D0", text=method.title(), variable=self.sampling_var, value=method, command=self.update_preview).pack(side=tk.LEFT)
        self.dither_var = tk.StringVar(value="floyd")
        dither_frame = tk.LabelFrame(self.image_controls_frame, bg="#D0D0D0", padx="6", borderwidth="0", text="Dithering")
        dither_frame.pack(fill=tk.X, pady=(2,4))
        for dither, label in [("floyd", "Floyd-Steinberg"), ("none", "None")]:
            tk.Radiobutton(dither_frame, bg="#D0D0D0", text=label, variable=self.dither_var, value=dither, command=self.update_preview).pack(side=tk.LEFT)

        palette_frame = tk.LabelFrame(palette_section_frame, bg="#D0D0D0", padx="12", pady="4", text="Palette Options")
        palette_frame.grid(row=0, column=1, padx=10, sticky="nsew")
        btn_frame = tk.Frame(palette_frame, bg="#D0D0D0",)
        btn_frame.pack(pady=(4, 8))
        tk.Button(btn_frame, bg="#D0D0D0", text="Load Palette...", command=self.load_palette).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, bg="#D0D0D0", text="Save Palette...", command=self.save_palette).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(palette_frame, padx="54", bg="#D0D0D0", text="Use imported palette", variable=self.force_palette_var, command=self.update_preview).pack(anchor="w")

        self.palette_preview_frame = tk.LabelFrame(palette_section_frame, bg="#D0D0D0", text="Current Palette Preview")
        self.palette_preview_frame.grid(row=0, column=2, padx=(10, 30), sticky="nsew")  # Add more right padding
        self.palette_preview_frame.config(width=160)  # Make preview area a bit narrower
        swatch_height = 1  # Smaller swatch height
        swatch_width = 3   # Smaller swatch width
        self.palette_preview_labels = []
        for i in range(16):
            swatch = tk.Label(self.palette_preview_frame, width=swatch_width, height=swatch_height, relief=tk.RAISED)
            swatch.grid(row=i, column=0, padx=2, pady=2)
            label = tk.Label(self.palette_preview_frame, text="", font=("Consolas", 9), anchor="w", width=16)
            label.grid(row=i, column=1, sticky="w", padx=2)
            self.palette_preview_labels.append((swatch, label))
        self.update_palette_preview()

        controls_frame = tk.Frame(bmp4_frame, bg="#D0D0D0")
        controls_frame.pack(pady=10)

    def set_image_controls_state(self, state):
        # Helper to enable/disable all controls in Image Controls section
        for child in self.image_controls_frame.winfo_children():
            try:
                child.config(state=state)
            except:
                for subchild in child.winfo_children():
                    try:
                        subchild.config(state=state)
                    except:
                        pass

    def import_image(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.bmp4;*.bm4;*.gif;*.tiff;*.tif;*.webp;*.ico")
        ])
        if not file_path:
            return
        ext = os.path.splitext(file_path)[1].lower()
        if ext in [".bmp4", ".bm4"]:
            self.import_bmp4(file_path)
            return
        try:
            self.image = Image.open(file_path)
            self.show_original(self.image)
            self.update_preview()
            self.export_btn.config(state=tk.NORMAL)
            self.set_image_controls_state("normal")
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            with open("error_log.txt", "w") as f:
                f.write(f"Failed to load image: {e}\n\n{tb}")
            messagebox.showerror("Error", f"Failed to load image: {e}\nSee error_log.txt for details.")

    def import_bmp4(self, file_path):
        if not file_path:
            return
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            if len(data) < 16000 + 32:
                raise ValueError("File too small to be valid BMP4/BM4")
            pixel_bytes = data[:16000]
            palette_bytes = data[-32:]
            # Decode palette: 16 colors, 2 bytes each (G4B4, R4)
            palette = []
            for i in range(16):
                g_b = palette_bytes[i*2]
                r = palette_bytes[i*2+1] & 0x0F
                g = (g_b >> 4) & 0x0F
                b = g_b & 0x0F
                # Convert 4-bit to 8-bit
                r8 = r << 4
                g8 = g << 4
                b8 = b << 4
                palette.append((r8, g8, b8))
            # Decode pixel data
            img = Image.new("P", (160, 200))
            img.putpalette([v for rgb in palette for v in rgb] + [0]*(768-3*len(palette)))
            pixels = []
            for byte in pixel_bytes:
                p1 = (byte >> 4) & 0x0F
                p2 = byte & 0x0F
                pixels.append(p1)
                pixels.append(p2)
            if len(pixels) > 160*200:
                pixels = pixels[:160*200]
            img.putdata(pixels)
            self.image = img
            self.loaded_palette = palette
            self.show_original(img)
            self.update_preview()
            self.export_btn.config(state=tk.NORMAL)
            self.set_image_controls_state("normal")
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            with open("error_log.txt", "w") as f:
                f.write(f"Failed to load BMP4/BM4: {e}\n\n{tb}")
            messagebox.showerror("Error", f"Failed to load BMP4/BM4: {e}\nSee error_log.txt for details.")

    def update_preview(self):
        if self.image is None:
            return
        img = self.image.copy()
        export_fmt = self.export_format_var.get()
        if export_fmt == "BMP4":
            target_size = (160, 200)
        else:
            target_size = (320, 200)
        # Scaling
        scaling = self.scaling_var.get()
        sampling = self.sampling_var.get()
        resample_map = {"nearest": Image.NEAREST, "bilinear": Image.BILINEAR, "bicubic": Image.BICUBIC, "lanczos": Image.LANCZOS}
        resample = resample_map.get(sampling, Image.NEAREST)
        if scaling == "stretch":
            img = img.resize(target_size, resample)
        elif scaling == "fill":
            img = self.scale_to_fill(img, target_size, resample)
        else:  # letterbox
            img = self.scale_letterbox(img, target_size, resample)
        # Palette reduction logic
        palette = None
        dither_map = {"floyd": Image.FLOYDSTEINBERG, "none": Image.NONE}
        dither = dither_map.get(getattr(self, 'dither_var', tk.StringVar(value="floyd")).get(), Image.FLOYDSTEINBERG)
        if self.force_palette_var.get() and self.loaded_palette:
            # Use loaded palette, force remap
            palette = list(self.loaded_palette)[:16]
            while len(palette) < 16:
                palette.append((0,0,0))
            img = self.remap_to_palette(img, palette)
        elif self.palette_var.get():
            # Use median cut (ADAPTIVE) palette
            img = img.convert("P", palette=Image.ADAPTIVE, colors=16, dither=dither)
            palette = self.get_padded_palette(img)
            img = self.remap_to_palette(img, palette)
        else:
            # Use image's own palette if <=16 colors, otherwise reduce
            if img.mode == "P" and len(img.getcolors(maxcolors=256) or []) <= 16:
                palette = self.get_padded_palette(img)
            else:
                img = img.convert("P", palette=Image.ADAPTIVE, colors=16, dither=dither)
                palette = self.get_padded_palette(img)
            img = self.remap_to_palette(img, palette)
        self.set_export_image(img, palette)
        # Show processed image in export preview
        preview = img.copy()
        preview = preview.resize((480, 300), Image.NEAREST)
        self.proc_img_preview = ImageTk.PhotoImage(preview)
        self.proc_img_label.config(image=self.proc_img_preview, text="")
        self.update_palette_preview()

    def scale_letterbox(self, img, target_size, resample):
        img_ratio = img.width / img.height
        target_ratio = target_size[0] / target_size[1]
        if img_ratio > target_ratio:
            new_width = target_size[0]
            new_height = int(new_width / img_ratio)
        else:
            new_height = target_size[1]
            new_width = int(new_height * img_ratio)
        img = img.resize((new_width, new_height), resample)
        result = Image.new("RGB", target_size, (0, 0, 0))
        x = (target_size[0] - new_width) // 2
        y = (target_size[1] - new_height) // 2
        result.paste(img, (x, y))
        return result

    def scale_to_fill(self, img, target_size, resample):
        img_ratio = img.width / img.height
        target_ratio = target_size[0] / target_size[1]
        if img_ratio < target_ratio:
            scale = target_size[0] / img.width
        else:
            scale = target_size[1] / img.height
        new_size = (int(img.width * scale), int(img.height * scale))
        img = img.resize(new_size, resample)
        x = (new_size[0] - target_size[0]) // 2
        y = (new_size[1] - target_size[1]) // 2
        img = img.crop((x, y, x + target_size[0], y + target_size[1]))
        return img

    def show_preview(self, img):
        preview = img.copy()
        preview = preview.resize((480, 300), Image.NEAREST)
        self.img_preview = ImageTk.PhotoImage(preview)
        self.img_label.config(image=self.img_preview)

    def show_original(self, img):
        preview = img.copy()
        preview = preview.resize((480, 300), Image.NEAREST)
        self.orig_img_preview = ImageTk.PhotoImage(preview)
        self.orig_img_label.config(image=self.orig_img_preview, text="")

    def export_image(self):
        if self.image is None:
            messagebox.showerror("Error", "No image loaded.")
            return
        export_type = self.export_format_var.get()
        if export_type == "BMP4":
            self.export_bmp4()
        elif export_type == "PNG":
            self.export_png()
        else:
            messagebox.showerror("Error", "Unknown export type.")

    def export_png(self):
        # Export the processed image as PNG
        img = getattr(self, '_export_img', None)
        if img is None:
            messagebox.showerror("Error", "No export image available. Please preview first.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
        if not file_path:
            return
        try:
            img.save(file_path, format="PNG")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PNG: {e}")

    def export_bmp1(self):
        # Prepare image: 320x200, 1BPP, 8x8 cells, 2 colors per cell from 16-color palette
        img = self.image.copy()
        img = self.scale_letterbox(img, (320, 200), Image.NEAREST)
        if self.force_palette_var.get() and self.loaded_palette:
            img = self.remap_to_palette(img, self.loaded_palette)
            # Set image palette to loaded palette
            flat_palette = []
            for rgb in self.loaded_palette:
                flat_palette.extend(rgb)
            img.putpalette(flat_palette + [0]*(768-len(flat_palette)))
            # Aquarius+ palette: 16 colors, 3 bytes each (RGB) from loaded palette
            palette_bytes = bytearray()
            for rgb in self.loaded_palette:
                palette_bytes.extend(rgb)
        else:
            img = img.convert("P", palette=Image.ADAPTIVE, colors=16)
            palette = img.getpalette()[:48]
            while len(palette) < 48:
                palette.extend([0, 0, 0])
            palette_bytes = bytearray()
            for i in range(16):
                r = palette[i*3]
                g = palette[i*3+1]
                b = palette[i*3+2]
                palette_bytes.extend([r, g, b])
        # Cell color info: 8x8 cells, each cell has 2 color indices (foreground/background)
        cell_colors = []
        pixels = img.load()
        for cell_y in range(0, 200, 8):
            for cell_x in range(0, 320, 8):
                # Get all pixel color indices in cell
                cell_indices = [pixels[x, y] for y in range(cell_y, cell_y+8) for x in range(cell_x, cell_x+8)]
                # Find two most common colors in cell
                from collections import Counter
                common = Counter(cell_indices).most_common(2)
                fg = common[0][0] if len(common) > 0 else 0
                bg = common[1][0] if len(common) > 1 else fg
                cell_colors.append((fg, bg))
        # Store cell color info: each cell 1 byte (high nibble fg, low nibble bg)
        cell_bytes = bytearray()
        for fg, bg in cell_colors:
            cell_bytes.append((fg << 4) | (bg & 0x0F))
        # Pixel data: 320x200, 1BPP, each bit is fg/bg for cell
        pixel_bytes = bytearray()
        cell_idx = 0
        for cell_y in range(0, 200, 8):
            for cell_x in range(0, 320, 8):
                fg, bg = cell_colors[cell_idx]
                for y in range(cell_y, cell_y+8):
                    for x in range(cell_x, cell_x+8, 8):
                        byte = 0
                        for bit in range(8):
                            color = pixels[x+bit, y]
                            byte = (byte << 1) | (1 if color == fg else 0)
                        pixel_bytes.append(byte)
                cell_idx += 1
        # Combine palette, cell color info, and pixel data
        out_bytes = palette_bytes + cell_bytes + pixel_bytes
        # Save file
        file_path = filedialog.asksaveasfilename(defaultextension=".bmp1", filetypes=[("Aquarius+ BMP1", "*.bmp1;*.bm1")])
        if not file_path:
            return
        try:
            with open(file_path, "wb") as f:
                f.write(out_bytes)
            messagebox.showinfo("Export", f"BMP1 file saved: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save BMP1: {e}")
        else:
            messagebox.showerror("Error", "Unknown export type.")

    def export_bmp4(self):
        # Prepare image: 160x200, 16 colors, double-wide pixels
        img = getattr(self, '_export_img', None)
        palette = getattr(self, '_export_palette', None)
        if img is None or palette is None:
            messagebox.showerror("Error", "No export image available. Please preview first.")
            return
        pal_bytes = []
        for rgb in palette:
            pal_bytes.extend(rgb)
        img.putpalette(pal_bytes + [0]*(768-len(pal_bytes)))
        palette_bytes = bytearray()
        for rgb in palette:
            r = (rgb[0] >> 4) & 0x0F
            g = (rgb[1] >> 4) & 0x0F
            b = (rgb[2] >> 4) & 0x0F
            palette_bytes.extend([ (g << 4) | b, (0 << 4) | r ])
        # Pixel data: 160x200, each pixel is 4 bits (nybble)
        pixel_bytes = bytearray()
        pixels = img.load()
        for y in range(200):
            for x in range(0, 160, 2):
                p1 = pixels[x, y] & 0x0F
                p2 = pixels[x+1, y] & 0x0F
                byte = (p1 << 4) | p2
                pixel_bytes.append(byte)
        # Ensure pixel data is exactly 16,000 bytes
        if len(pixel_bytes) > 16000:
            pixel_bytes = pixel_bytes[:16000]
        elif len(pixel_bytes) < 16000:
            pixel_bytes += bytearray([0] * (16000 - len(pixel_bytes)))
        # Combine pixel data and palette
        out_bytes = pixel_bytes + palette_bytes
        # Save file
        file_path = filedialog.asksaveasfilename(defaultextension=".bmp4", filetypes=[("Aquarius+ BMP4", "*.bmp4;*.bm4")])
        if not file_path:
            return
        try:
            with open(file_path, "wb") as f:
                f.write(out_bytes)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save BMP4: {e}")

    def update_palette_preview(self):
        # Determine which palette to show
        if self.force_palette_var.get() and self.loaded_palette:
            palette = list(self.loaded_palette)[:16]
            while len(palette) < 16:
                palette.append((0,0,0))
        else:
            palette = getattr(self, '_export_palette', [(0,0,0)]*16)
            palette = list(palette)[:16]
            while len(palette) < 16:
                palette.append((0,0,0))
        # Update swatches and labels
        swatch_height = 3  # tkinter Label height is in text lines, not pixels
        swatch_width = 6   # tkinter Label width is in text characters
        for i, (swatch, label) in enumerate(self.palette_preview_labels):
            r, g, b = palette[i]
            r4, g4, b4 = r >> 4, g >> 4, b >> 4
            hex_color = f'#{r:02x}{g:02x}{b:02x}'
            hex_nybble = f'{r4:X}{g4:X}{b4:X}'
            swatch.config(bg=hex_color, width=swatch_width, height=swatch_height)
            label.config(text=f'IDX: {i}\nHEX: {hex_nybble}\nRGB: {r4},{g4},{b4}', justify='left', anchor='w')
        # Palette preview layout: 4 columns x 4 rows, vertically center swatch and label
        for i, (swatch, label) in enumerate(self.palette_preview_labels):
            row, col = i // 4, i % 4
            swatch.grid(row=row, column=col, padx=(4,0), pady=4, sticky='nsw')
            label.grid(row=row, column=col, padx=(swatch_width*8,4), pady=4, sticky='nsw')

    def remap_to_palette(self, img, palette):
        # Remap image colors to the given palette (list of 16 RGB tuples)
        import numpy as np
        img = img.convert('RGB')
        arr = np.array(img)
        h, w, _ = arr.shape
        pal_arr = np.array(palette)
        # Flatten image array for fast processing
        arr_flat = arr.reshape(-1, 3)
        # Find closest palette color for each pixel
        def closest_color(pixel):
            diffs = pal_arr - pixel
            dist = np.sum(diffs * diffs, axis=1)
            return np.argmin(dist)
        idxs = np.array([closest_color(px) for px in arr_flat], dtype=np.uint8)
        pal_img = Image.new('P', (w, h))
        pal_img.putpalette([v for rgb in palette for v in rgb] + [0]*(768-3*len(palette)))
        pal_img.putdata(idxs.reshape(-1))
        return pal_img

if __name__ == "__main__":
    root = tk.Tk()
    app = AQPStudio(root)
    root.mainloop()

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class AQPStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("AQP Studio")
        self.root.configure(bg="#D0D0D0")  # 20% grey background
        self.image = None
        self.img_preview = None
        self.loaded_palette = None  # List of (R,G,B) tuples
        self.palette_var = tk.BooleanVar(value=True)
        self.force_palette_var = tk.BooleanVar(value=False)
        self.scaling_var = tk.StringVar(value="letterbox")
        self.sampling_var = tk.StringVar(value="bicubic")
        self.export_format_var = tk.StringVar(value="BMP4")
        self.setup_gui()

    def save_palette(self):
        # Get current palette (forced or preview)
        if self.force_palette_var.get() and self.loaded_palette:
            palette = list(self.loaded_palette)[:16]
            while len(palette) < 16:
                palette.append((0,0,0))
        else:
            palette = getattr(self, '_export_palette', [(0,0,0)]*16)
            palette = list(palette)[:16]
            while len(palette) < 16:
                palette.append((0,0,0))
        file_path = filedialog.asksaveasfilename(defaultextension=".pal", filetypes=[("Palette Files", "*.pal")])
        if not file_path:
            return
        try:
            with open(file_path, "w") as f:
                f.write("JASC-PAL\n0100\n16\n")
                for r, g, b in palette:
                    f.write(f"{r} {g} {b}\n")
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            with open("error_log.txt", "w") as ef:
                ef.write(f"Failed to save palette: {e}\n\n{tb}")
            messagebox.showerror("Error", f"Failed to save palette: {e}\nSee error_log.txt for details.")
    def set_export_image(self, img, palette):
        self._export_img = img
        self._export_palette = palette
    def get_padded_palette(self, img):
        pal = img.getpalette() if img.mode == "P" else None
        if pal is None:
            pal = [0] * 48
        else:
            pal = list(pal[:48])
            if len(pal) < 48:
                pal += [0] * (48 - len(pal))
        return [(pal[i*3], pal[i*3+1], pal[i*3+2]) for i in range(16)]
    def load_palette(self):
        file_path = filedialog.askopenfilename(filetypes=[("Palette Files", "*.pal")])
        if not file_path:
            return
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
            # JASC-PAL format: skip header
            if lines[0].strip() != "JASC-PAL":
                raise ValueError("Not a JASC-PAL file")
            count = int(lines[2].strip())
            palette = []
            for line in lines[3:3+count]:
                r, g, b = map(int, line.strip().split())
                palette.append((r, g, b))
            if len(palette) != 16:
                raise ValueError("Palette must have 16 colors")
            self.loaded_palette = palette
            # After loading palette, set Force palette on image checkbox
            self.force_palette_var.set(True)
            self.update_preview()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load palette: {e}")
    # Duplicate __init__ removed

    def setup_gui(self):
        from tkinter import ttk
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#808080", borderwidth=0)
        style.configure("TNotebook.Tab", background="#A0A0A0", font=("Arial", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#D0D0D0")])  # Matches frame background for selected tab

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # BMP4 tab
        bmp4_frame = tk.Frame(notebook, bg="#D0D0D0")
        notebook.add(bmp4_frame, text="BMP4 Images")

        # BMP1 tab (blank)
        bmp1_frame = tk.Frame(notebook, bg="#D0D0D0")
        notebook.add(bmp1_frame, text="BMP1 Images")
        tk.Label(bmp1_frame, text="BMP1 tools coming soon...", bg="#D0D0D0", font=("Arial", 14)).pack(pady=40)

        # All previous widget creation now goes inside bmp4_frame
        preview_frame = tk.Frame(bmp4_frame, bg="#D0D0D0")
        preview_frame.pack(pady=10, padx=20)

        preview_img_width = 480
        preview_img_height = 300

        import_btn_frame = tk.Frame(preview_frame, bg="#D0D0D0")
        import_btn_frame.pack(side=tk.LEFT, padx=(10, 10))
        import_icon = Image.open("assets/import_image.png")
        import_icon = import_icon.resize((64, 64), Image.NEAREST)
        self.import_icon_imgtk = ImageTk.PhotoImage(import_icon)
        self.import_btn = tk.Button(
            import_btn_frame,
            image=self.import_icon_imgtk,
            width=64,
            height=64,
            relief=tk.RAISED,
            bd=4,
            command=self.import_image
        )
        self.import_btn.pack()
        tk.Label(import_btn_frame, bg="#D0D0D0", text="Import Image", font=("Arial", 10)).pack(pady=(2,0))

        self.orig_img_box = tk.LabelFrame(preview_frame, bg="#D0D0D0", text=" Original Image ", width=preview_img_width+20, height=preview_img_height+36)
        self.orig_img_box.pack_propagate(False)
        self.orig_img_box.pack(side=tk.LEFT, padx=10)
        self.orig_img_label = tk.Label(self.orig_img_box, bg="#D0D0D0", text="Imported Image", fg="#B0B0B0", font=("Arial", 18))
        self.orig_img_label.pack(expand=True, fill=tk.BOTH)

        self.proc_img_box = tk.LabelFrame(preview_frame, bg="#D0D0D0", text=" Export Preview ", width=preview_img_width+20, height=preview_img_height+36)
        self.proc_img_box.pack_propagate(False)
        self.proc_img_box.pack(side=tk.LEFT, padx=10)
        self.proc_img_label = tk.Label(self.proc_img_box, bg="#D0D0D0", text="Exported Image", fg="#B0B0B0", font=("Arial", 18))
        self.proc_img_label.pack(expand=True, fill=tk.BOTH)

        export_btn_frame = tk.Frame(preview_frame, bg="#D0D0D0")
        export_btn_frame.pack(side=tk.LEFT, padx=(10, 10))
        export_icon = Image.open("assets/export_image.png")
        export_icon = export_icon.resize((64, 64), Image.NEAREST)
        self.export_icon_imgtk = ImageTk.PhotoImage(export_icon)
        self.export_btn = tk.Button(
            export_btn_frame,
            image=self.export_icon_imgtk,
            width=64,
            height=64,
            relief=tk.RAISED,
            bd=4,
            state=tk.DISABLED,
            command=self.export_image
        )
        self.export_btn.pack()
        tk.Label(export_btn_frame, text="Export Image", bg="#D0D0D0", font=("Arial", 10)).pack(pady=(2,0))
        export_format_frame = tk.LabelFrame(export_btn_frame, bg="#D0D0D0", text="Export Format")
        export_format_frame.pack(pady=(8,0))
        for fmt in ["BMP4", "PNG"]:
            tk.Radiobutton(export_format_frame, bg="#D0D0D0", text=fmt, variable=self.export_format_var, value=fmt, command=self.update_preview).pack(side=tk.LEFT)

        palette_section_frame = tk.Frame(bmp4_frame, bg="#D0D0D0")
        palette_section_frame.pack(pady=10, fill=tk.X)
        palette_section_frame.grid_columnconfigure(0, weight=1)
        palette_section_frame.grid_columnconfigure(1, weight=1)

        self.image_controls_frame = tk.LabelFrame(palette_section_frame, bg="#D0D0D0", padx="12", pady="4", text="Image Controls")
        self.image_controls_frame.grid(row=0, column=0, padx=(20,10), sticky="nsew")
        scaling_frame = tk.LabelFrame(self.image_controls_frame, bg="#D0D0D0", padx="6", borderwidth="0", text="Scaling")
        scaling_frame.pack(fill=tk.X, pady=(4,2))
        for mode in ["letterbox", "stretch", "fill"]:
            tk.Radiobutton(scaling_frame, bg="#D0D0D0", text=mode.title(), variable=self.scaling_var, value=mode, command=self.update_preview).pack(side=tk.LEFT)
        sampling_frame = tk.LabelFrame(self.image_controls_frame, bg="#D0D0D0", padx="6", borderwidth="0", text="Sampling")
        sampling_frame.pack(fill=tk.X, pady=(2,4))
        sampling_methods = ["bicubic", "bilinear", "lanczos", "nearest"]
        self.sampling_var.set("bicubic")  # Set Bicubic as default selection
        for method in sampling_methods:
            tk.Radiobutton(sampling_frame, bg="#D0D0D0", text=method.title(), variable=self.sampling_var, value=method, command=self.update_preview).pack(side=tk.LEFT)
        self.dither_var = tk.StringVar(value="floyd")
        dither_frame = tk.LabelFrame(self.image_controls_frame, bg="#D0D0D0", padx="6", borderwidth="0", text="Dithering")
        dither_frame.pack(fill=tk.X, pady=(2,4))
        for dither, label in [("floyd", "Floyd-Steinberg"), ("none", "None")]:
            tk.Radiobutton(dither_frame, bg="#D0D0D0", text=label, variable=self.dither_var, value=dither, command=self.update_preview).pack(side=tk.LEFT)

        palette_frame = tk.LabelFrame(palette_section_frame, bg="#D0D0D0", padx="12", pady="4", text="Palette Options")
        palette_frame.grid(row=0, column=1, padx=10, sticky="nsew")
        btn_frame = tk.Frame(palette_frame, bg="#D0D0D0",)
        btn_frame.pack(pady=(4, 8))
        tk.Button(btn_frame, bg="#D0D0D0", text="Load Palette...", command=self.load_palette).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, bg="#D0D0D0", text="Save Palette...", command=self.save_palette).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(palette_frame, padx="54", bg="#D0D0D0", text="Use imported palette", variable=self.force_palette_var, command=self.update_preview).pack(anchor="w")

        self.palette_preview_frame = tk.LabelFrame(palette_section_frame, bg="#D0D0D0", text="Current Palette Preview")
        self.palette_preview_frame.grid(row=0, column=2, padx=(10, 30), sticky="nsew")  # Add more right padding
        self.palette_preview_frame.config(width=160)  # Make preview area a bit narrower
        swatch_height = 1  # Smaller swatch height
        swatch_width = 3   # Smaller swatch width
        self.palette_preview_labels = []
        for i in range(16):
            swatch = tk.Label(self.palette_preview_frame, width=swatch_width, height=swatch_height, relief=tk.RAISED)
            swatch.grid(row=i, column=0, padx=2, pady=2)
            label = tk.Label(self.palette_preview_frame, text="", font=("Consolas", 9), anchor="w", width=16)
            label.grid(row=i, column=1, sticky="w", padx=2)
            self.palette_preview_labels.append((swatch, label))
        self.update_palette_preview()

        controls_frame = tk.Frame(bmp4_frame, bg="#D0D0D0")
        controls_frame.pack(pady=10)

    def set_image_controls_state(self, state):
        # Helper to enable/disable all controls in Image Controls section
        for child in self.image_controls_frame.winfo_children():
            try:
                child.config(state=state)
            except:
                for subchild in child.winfo_children():
                    try:
                        subchild.config(state=state)
                    except:
                        pass

    def import_image(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.bmp4;*.bm4;*.gif;*.tiff;*.tif;*.webp;*.ico")
        ])
        if not file_path:
            return
        ext = os.path.splitext(file_path)[1].lower()
        if ext in [".bmp4", ".bm4"]:
            self.import_bmp4(file_path)
            return
        try:
            self.image = Image.open(file_path)
            self.show_original(self.image)
            self.update_preview()
            self.export_btn.config(state=tk.NORMAL)
            self.set_image_controls_state("normal")
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            with open("error_log.txt", "w") as f:
                f.write(f"Failed to load image: {e}\n\n{tb}")
            messagebox.showerror("Error", f"Failed to load image: {e}\nSee error_log.txt for details.")

    def import_bmp4(self, file_path):
        if not file_path:
            return
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            if len(data) < 16000 + 32:
                raise ValueError("File too small to be valid BMP4/BM4")
            pixel_bytes = data[:16000]
            palette_bytes = data[-32:]
            # Decode palette: 16 colors, 2 bytes each (G4B4, R4)
            palette = []
            for i in range(16):
                g_b = palette_bytes[i*2]
                r = palette_bytes[i*2+1] & 0x0F
                g = (g_b >> 4) & 0x0F
                b = g_b & 0x0F
                # Convert 4-bit to 8-bit
                r8 = r << 4
                g8 = g << 4
                b8 = b << 4
                palette.append((r8, g8, b8))
            # Decode pixel data
            img = Image.new("P", (160, 200))
            img.putpalette([v for rgb in palette for v in rgb] + [0]*(768-3*len(palette)))
            pixels = []
            for byte in pixel_bytes:
                p1 = (byte >> 4) & 0x0F
                p2 = byte & 0x0F
                pixels.append(p1)
                pixels.append(p2)
            if len(pixels) > 160*200:
                pixels = pixels[:160*200]
            img.putdata(pixels)
            self.image = img
            self.loaded_palette = palette
            self.show_original(img)
            self.update_preview()
            self.export_btn.config(state=tk.NORMAL)
            self.set_image_controls_state("normal")
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            with open("error_log.txt", "w") as f:
                f.write(f"Failed to load BMP4/BM4: {e}\n\n{tb}")
            messagebox.showerror("Error", f"Failed to load BMP4/BM4: {e}\nSee error_log.txt for details.")

    def update_preview(self):
        if self.image is None:
            return
        img = self.image.copy()
        export_fmt = self.export_format_var.get()
        if export_fmt == "BMP4":
            target_size = (160, 200)
        else:
            target_size = (320, 200)
        # Scaling
        scaling = self.scaling_var.get()
        sampling = self.sampling_var.get()
        resample_map = {"nearest": Image.NEAREST, "bilinear": Image.BILINEAR, "bicubic": Image.BICUBIC, "lanczos": Image.LANCZOS}
        resample = resample_map.get(sampling, Image.NEAREST)
        if scaling == "stretch":
            img = img.resize(target_size, resample)
        elif scaling == "fill":
            img = self.scale_to_fill(img, target_size, resample)
        else:  # letterbox
            img = self.scale_letterbox(img, target_size, resample)
        # Palette reduction logic
        palette = None
        dither_map = {"floyd": Image.FLOYDSTEINBERG, "none": Image.NONE}
        dither = dither_map.get(getattr(self, 'dither_var', tk.StringVar(value="floyd")).get(), Image.FLOYDSTEINBERG)
        if self.force_palette_var.get() and self.loaded_palette:
            # Use loaded palette, force remap
            palette = list(self.loaded_palette)[:16]
            while len(palette) < 16:
                palette.append((0,0,0))
            img = self.remap_to_palette(img, palette)
        elif self.palette_var.get():
            # Use median cut (ADAPTIVE) palette
            img = img.convert("P", palette=Image.ADAPTIVE, colors=16, dither=dither)
            palette = self.get_padded_palette(img)
            img = self.remap_to_palette(img, palette)
        else:
            # Use image's own palette if <=16 colors, otherwise reduce
            if img.mode == "P" and len(img.getcolors(maxcolors=256) or []) <= 16:
                palette = self.get_padded_palette(img)
            else:
                img = img.convert("P", palette=Image.ADAPTIVE, colors=16, dither=dither)
                palette = self.get_padded_palette(img)
            img = self.remap_to_palette(img, palette)
        self.set_export_image(img, palette)
        # Show processed image in export preview
        preview = img.copy()
        preview = preview.resize((480, 300), Image.NEAREST)
        self.proc_img_preview = ImageTk.PhotoImage(preview)
        self.proc_img_label.config(image=self.proc_img_preview, text="")
        self.update_palette_preview()

    def scale_letterbox(self, img, target_size, resample):
        img_ratio = img.width / img.height
        target_ratio = target_size[0] / target_size[1]
        if img_ratio > target_ratio:
            new_width = target_size[0]
            new_height = int(new_width / img_ratio)
        else:
            new_height = target_size[1]
            new_width = int(new_height * img_ratio)
        img = img.resize((new_width, new_height), resample)
        result = Image.new("RGB", target_size, (0, 0, 0))
        x = (target_size[0] - new_width) // 2
        y = (target_size[1] - new_height) // 2
        result.paste(img, (x, y))
        return result

    def scale_to_fill(self, img, target_size, resample):
        img_ratio = img.width / img.height
        target_ratio = target_size[0] / target_size[1]
        if img_ratio < target_ratio:
            scale = target_size[0] / img.width
        else:
            scale = target_size[1] / img.height
        new_size = (int(img.width * scale), int(img.height * scale))
        img = img.resize(new_size, resample)
        x = (new_size[0] - target_size[0]) // 2
        y = (new_size[1] - target_size[1]) // 2
        img = img.crop((x, y, x + target_size[0], y + target_size[1]))
        return img

    def show_preview(self, img):
        preview = img.copy()
        preview = preview.resize((480, 300), Image.NEAREST)
        self.img_preview = ImageTk.PhotoImage(preview)
        self.img_label.config(image=self.img_preview)

    def show_original(self, img):
        preview = img.copy()
        preview = preview.resize((480, 300), Image.NEAREST)
        self.orig_img_preview = ImageTk.PhotoImage(preview)
        self.orig_img_label.config(image=self.orig_img_preview, text="")

    def export_image(self):
        if self.image is None:
            messagebox.showerror("Error", "No image loaded.")
            return
        export_type = self.export_format_var.get()
        if export_type == "BMP4":
            self.export_bmp4()
        elif export_type == "PNG":
            self.export_png()
        else:
            messagebox.showerror("Error", "Unknown export type.")

    def export_png(self):
        # Export the processed image as PNG
        img = getattr(self, '_export_img', None)
        if img is None:
            messagebox.showerror("Error", "No export image available. Please preview first.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
        if not file_path:
            return
        try:
            img.save(file_path, format="PNG")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PNG: {e}")

    def export_bmp1(self):
        # Prepare image: 320x200, 1BPP, 8x8 cells, 2 colors per cell from 16-color palette
        img = self.image.copy()
        img = self.scale_letterbox(img, (320, 200), Image.NEAREST)
        if self.force_palette_var.get() and self.loaded_palette:
            img = self.remap_to_palette(img, self.loaded_palette)
            # Set image palette to loaded palette
            flat_palette = []
            for rgb in self.loaded_palette:
                flat_palette.extend(rgb)
            img.putpalette(flat_palette + [0]*(768-len(flat_palette)))
            # Aquarius+ palette: 16 colors, 3 bytes each (RGB) from loaded palette
            palette_bytes = bytearray()
            for rgb in self.loaded_palette:
                palette_bytes.extend(rgb)
        else:
            img = img.convert("P", palette=Image.ADAPTIVE, colors=16)
            palette = img.getpalette()[:48]
            while len(palette) < 48:
                palette.extend([0, 0, 0])
            palette_bytes = bytearray()
            for i in range(16):
                r = palette[i*3]
                g = palette[i*3+1]
                b = palette[i*3+2]
                palette_bytes.extend([r, g, b])
        # Cell color info: 8x8 cells, each cell has 2 color indices (foreground/background)
        cell_colors = []
        pixels = img.load()
        for cell_y in range(0, 200, 8):
            for cell_x in range(0, 320, 8):
                # Get all pixel color indices in cell
                cell_indices = [pixels[x, y] for y in range(cell_y, cell_y+8) for x in range(cell_x, cell_x+8)]
                # Find two most common colors in cell
                from collections import Counter
                common = Counter(cell_indices).most_common(2)
                fg = common[0][0] if len(common) > 0 else 0
                bg = common[1][0] if len(common) > 1 else fg
                cell_colors.append((fg, bg))
        # Store cell color info: each cell 1 byte (high nibble fg, low nibble bg)
        cell_bytes = bytearray()
        for fg, bg in cell_colors:
            cell_bytes.append((fg << 4) | (bg & 0x0F))
        # Pixel data: 320x200, 1BPP, each bit is fg/bg for cell
        pixel_bytes = bytearray()
        cell_idx = 0
        for cell_y in range(0, 200, 8):
            for cell_x in range(0, 320, 8):
                fg, bg = cell_colors[cell_idx]
                for y in range(cell_y, cell_y+8):
                    for x in range(cell_x, cell_x+8, 8):
                        byte = 0
                        for bit in range(8):
                            color = pixels[x+bit, y]
                            byte = (byte << 1) | (1 if color == fg else 0)
                        pixel_bytes.append(byte)
                cell_idx += 1
        # Combine palette, cell color info, and pixel data
        out_bytes = palette_bytes + cell_bytes + pixel_bytes
        # Save file
        file_path = filedialog.asksaveasfilename(defaultextension=".bmp1", filetypes=[("Aquarius+ BMP1", "*.bmp1;*.bm1")])
        if not file_path:
            return
        try:
            with open(file_path, "wb") as f:
                f.write(out_bytes)
            messagebox.showinfo("Export", f"BMP1 file saved: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save BMP1: {e}")
        else:
            messagebox.showerror("Error", "Unknown export type.")

    def export_bmp4(self):
        # Prepare image: 160x200, 16 colors, double-wide pixels
        img = getattr(self, '_export_img', None)
        palette = getattr(self, '_export_palette', None)
        if img is None or palette is None:
            messagebox.showerror("Error", "No export image available. Please preview first.")
            return
        pal_bytes = []
        for rgb in palette:
            pal_bytes.extend(rgb)
        img.putpalette(pal_bytes + [0]*(768-len(pal_bytes)))
        palette_bytes = bytearray()
        for rgb in palette:
            r = (rgb[0] >> 4) & 0x0F
            g = (rgb[1] >> 4) & 0x0F
            b = (rgb[2] >> 4) & 0x0F
            palette_bytes.extend([ (g << 4) | b, (0 << 4) | r ])
        # Pixel data: 160x200, each pixel is 4 bits (nybble)
        pixel_bytes = bytearray()
        pixels = img.load()
        for y in range(200):
            for x in range(0, 160, 2):
                p1 = pixels[x, y] & 0x0F
                p2 = pixels[x+1, y] & 0x0F
                byte = (p1 << 4) | p2
                pixel_bytes.append(byte)
        # Ensure pixel data is exactly 16,000 bytes
        if len(pixel_bytes) > 16000:
            pixel_bytes = pixel_bytes[:16000]
        elif len(pixel_bytes) < 16000:
            pixel_bytes += bytearray([0] * (16000 - len(pixel_bytes)))
        # Combine pixel data and palette
        out_bytes = pixel_bytes + palette_bytes
        # Save file
        file_path = filedialog.asksaveasfilename(defaultextension=".bmp4", filetypes=[("Aquarius+ BMP4", "*.bmp4;*.bm4")])
        if not file_path:
            return
        try:
            with open(file_path, "wb") as f:
                f.write(out_bytes)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save BMP4: {e}")

    def update_palette_preview(self):
        # Determine which palette to show
        if self.force_palette_var.get() and self.loaded_palette:
            palette = list(self.loaded_palette)[:16]
            while len(palette) < 16:
                palette.append((0,0,0))
        else:
            palette = getattr(self, '_export_palette', [(0,0,0)]*16)
            palette = list(palette)[:16]
            while len(palette) < 16:
                palette.append((0,0,0))
        # Update swatches and labels
        swatch_height = 3  # tkinter Label height is in text lines, not pixels
        swatch_width = 6   # tkinter Label width is in text characters
        for i, (swatch, label) in enumerate(self.palette_preview_labels):
            r, g, b = palette[i]
            r4, g4, b4 = r >> 4, g >> 4, b >> 4
            hex_color = f'#{r:02x}{g:02x}{b:02x}'
            hex_nybble = f'{r4:X}{g4:X}{b4:X}'
            swatch.config(bg=hex_color, width=swatch_width, height=swatch_height)
            label.config(text=f'IDX: {i}\nHEX: {hex_nybble}\nRGB: {r4},{g4},{b4}', justify='left', anchor='w')
        # Palette preview layout: 4 columns x 4 rows, vertically center swatch and label
        for i, (swatch, label) in enumerate(self.palette_preview_labels):
            row, col = i // 4, i % 4
            swatch.grid(row=row, column=col, padx=(4,0), pady=4, sticky='nsw')
            label.grid(row=row, column=col, padx=(swatch_width*8,4), pady=4, sticky='nsw')

    def remap_to_palette(self, img, palette):
        # Remap image colors to the given palette (list of 16 RGB tuples)
        import numpy as np
        img = img.convert('RGB')
        arr = np.array(img)
        h, w, _ = arr.shape
        pal_arr = np.array(palette)
        # Flatten image array for fast processing
        arr_flat = arr.reshape(-1, 3)
        # Find closest palette color for each pixel
        def closest_color(pixel):
            diffs = pal_arr - pixel
            dist = np.sum(diffs * diffs, axis=1)
            return np.argmin(dist)
        idxs = np.array([closest_color(px) for px in arr_flat], dtype=np.uint8)
        pal_img = Image.new('P', (w, h))
        pal_img.putpalette([v for rgb in palette for v in rgb] + [0]*(768-3*len(palette)))
        pal_img.putdata(idxs.reshape(-1))
        return pal_img

if __name__ == "__main__":
    root = tk.Tk()
    app = AQPStudio(root)
    root.mainloop()
