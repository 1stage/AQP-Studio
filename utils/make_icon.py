import os
from PIL import Image

src_png = "assets/win-icon.png"
out_ico = os.path.join("assets", "win-icon.ico")

img = Image.open(src_png)
img = img.resize((256, 256), Image.LANCZOS)
img.save(out_ico)
print(f"Single-size ICO generated: {out_ico}")
