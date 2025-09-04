import tkinter as tk
from tkinter import ttk

class BMP4Tab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        # BMP4 tab UI setup
        preview_frame = tk.Frame(self, bg="#D0D0D0")
        preview_frame.pack(pady=10, padx=20)

        preview_img_width = 480
        preview_img_height = 300

        import_btn_frame = tk.Frame(preview_frame, bg="#D0D0D0")
        import_btn_frame.pack(side=tk.LEFT, padx=(10, 10))
        import_icon = app.image_icon("assets/import_image.png")
        self.import_btn = tk.Button(
            import_btn_frame,
            image=import_icon,
            width=64,
            height=64,
            relief=tk.RAISED,
            bd=4,
            command=app.import_image
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
        export_icon = app.image_icon("assets/export_image.png")
        self.export_btn = tk.Button(
            export_btn_frame,
            image=export_icon,
            width=64,
            height=64,
            relief=tk.RAISED,
            bd=4,
            state=tk.DISABLED,
            command=app.export_image
        )
        self.export_btn.pack()
        tk.Label(export_btn_frame, text="Export Image", bg="#D0D0D0", font=("Arial", 10)).pack(pady=(2,0))
        export_format_frame = tk.LabelFrame(export_btn_frame, bg="#D0D0D0", text="Export Format")
        export_format_frame.pack(pady=(8,0))
        for fmt in ["BMP4", "PNG"]:
            tk.Radiobutton(export_format_frame, bg="#D0D0D0", text=fmt, variable=app.export_format_var, value=fmt, command=app.update_preview).pack(side=tk.LEFT)

        palette_section_frame = tk.Frame(self, bg="#D0D0D0")
        palette_section_frame.pack(pady=10, fill=tk.X)
        palette_section_frame.grid_columnconfigure(0, weight=1)
        palette_section_frame.grid_columnconfigure(1, weight=1)

        app.image_controls_frame = tk.LabelFrame(palette_section_frame, bg="#D0D0D0", padx="12", pady="4", text="Image Controls")
        app.image_controls_frame.grid(row=0, column=0, padx=(20,10), sticky="nsew")
        scaling_frame = tk.LabelFrame(app.image_controls_frame, bg="#D0D0D0", padx="6", borderwidth="0", text="Scaling")
        scaling_frame.pack(fill=tk.X, pady=(4,2))
        for mode in ["letterbox", "stretch", "fill"]:
            tk.Radiobutton(scaling_frame, bg="#D0D0D0", text=mode.title(), variable=app.scaling_var, value=mode, command=app.update_preview).pack(side=tk.LEFT)
        sampling_frame = tk.LabelFrame(app.image_controls_frame, bg="#D0D0D0", padx="6", borderwidth="0", text="Sampling")
        sampling_frame.pack(fill=tk.X, pady=(2,4))
        sampling_methods = ["bicubic", "bilinear", "lanczos", "nearest"]
        app.sampling_var.set("bicubic")
        for method in sampling_methods:
            tk.Radiobutton(sampling_frame, bg="#D0D0D0", text=method.title(), variable=app.sampling_var, value=method, command=app.update_preview).pack(side=tk.LEFT)
        app.dither_var = tk.StringVar(value="floyd")
        dither_frame = tk.LabelFrame(app.image_controls_frame, bg="#D0D0D0", padx="6", borderwidth="0", text="Dithering")
        dither_frame.pack(fill=tk.X, pady=(2,4))
        for dither, label in [("floyd", "Floyd-Steinberg"), ("none", "None")]:
            tk.Radiobutton(dither_frame, bg="#D0D0D0", text=label, variable=app.dither_var, value=dither, command=app.update_preview).pack(side=tk.LEFT)

        palette_frame = tk.LabelFrame(palette_section_frame, bg="#D0D0D0", padx="12", pady="4", text="Palette Options")
        palette_frame.grid(row=0, column=1, padx=10, sticky="nsew")
        btn_frame = tk.Frame(palette_frame, bg="#D0D0D0",)
        btn_frame.pack(pady=(4, 8))
        tk.Button(btn_frame, bg="#D0D0D0", text="Load Palette...", command=app.load_palette).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, bg="#D0D0D0", text="Save Palette...", command=app.save_palette).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(palette_frame, padx="54", bg="#D0D0D0", text="Use imported palette", variable=app.force_palette_var, command=app.update_preview).pack(anchor="w")

        app.palette_preview_frame = tk.LabelFrame(palette_section_frame, bg="#D0D0D0", text="Current Palette Preview")
        app.palette_preview_frame.grid(row=0, column=2, padx=(10, 30), sticky="nsew")
        app.palette_preview_frame.config(width=160)
        swatch_height = 1
        swatch_width = 3
        app.palette_preview_labels = []
        for i in range(16):
            swatch = tk.Label(app.palette_preview_frame, width=swatch_width, height=swatch_height, relief=tk.RAISED)
            swatch.grid(row=i, column=0, padx=2, pady=2)
            label = tk.Label(app.palette_preview_frame, text="", font=("Consolas", 9), anchor="w", width=16)
            label.grid(row=i, column=1, sticky="w", padx=2)
            app.palette_preview_labels.append((swatch, label))
        app.update_palette_preview()

        controls_frame = tk.Frame(self, bg="#D0D0D0")
        controls_frame.pack(pady=10)
