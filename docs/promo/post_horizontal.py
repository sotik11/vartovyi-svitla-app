from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np

HERE = Path(__file__).resolve().parent

SHOTS = str(HERE.parent / "screenshots" / "dark" / "{}.jpg")
HERO = HERE.parent / "hero.webp"
OUT = HERE / "post-horizontal.png"
W, H = 1600, 900
BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
REG = r"C:\Windows\Fonts\segoeui.ttf"
GOLD = (240, 184, 64)

# Night-blue ground with a warm glow where the owl sits.
yy, xx = np.mgrid[0:H, 0:W]
base = np.zeros((H, W, 3), float)
base[:] = (8, 14, 30)
glow = np.exp(-(((xx - 290) / 420) ** 2 + ((yy - 330) / 360) ** 2))
base += glow[..., None] * np.array([40, 34, 18])
cold = np.exp(-(((xx - 1150) / 700) ** 2 + ((yy - 450) / 500) ** 2))
base += cold[..., None] * np.array([10, 22, 48])
canvas = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")

def rounded(img, radius):
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, img.width - 1, img.height - 1), radius, fill=255)
    img = img.convert("RGBA")
    img.putalpha(mask)
    return img

def place(img, x, y, radius, shadow=28):
    img = rounded(img, radius)
    pad = shadow * 2
    sh = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 14, pad + img.width, pad + img.height + 14), radius,
                                         fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(shadow))
    canvas.alpha_composite(sh, (x - pad, y - pad))
    canvas.alpha_composite(img, (x, y))
    ImageDraw.Draw(canvas).rounded_rectangle((x, y, x + img.width - 1, y + img.height - 1), radius,
                                             outline=(70, 86, 120, 255), width=2)

# The owl.
hero = Image.open(HERO).convert("RGB")
hero = hero.crop((70, 60, hero.width - 70, hero.height - 70)).resize((300, 300), Image.LANCZOS)
place(hero, 140, 120, 56, shadow=34)

draw = ImageDraw.Draw(canvas)
title = ImageFont.truetype(BOLD, 54)
sub = ImageFont.truetype(REG, 27)
small = ImageFont.truetype(REG, 23)
draw.text((90, 476), "Вартовий Світла", font=title, fill=GOLD)
draw.text((92, 555), "Твій персональний контроль", font=sub, fill=(225, 230, 240))
draw.text((92, 591), "електропостачання", font=sub, fill=(225, 230, 240))
y = 660
for line in ["⚡ Завжди свіжий графік ДТЕК", "🔔 Сповіщення про зміни й відключення",
             "📊 Статистика: за графіком і фактично", "🧩 Віджети на головний екран"]:
    # Segoe has no colour emoji: a gold bullet instead.
    words = line.split(" ", 1)[1]
    draw.ellipse((96, y + 11, 106, y + 21), fill=GOLD)
    draw.text((120, y), words, font=small, fill=(190, 198, 215))
    y += 38
draw.text((92, 836), "Android · безкоштовно · без реклами", font=ImageFont.truetype(REG, 19), fill=(120, 132, 158))

# Four screens, the middle two a little higher.
shots = ["shot_home.jpg", SHOTS.replace("dark", "light").format("08"), "shot_summary.jpg", "mixed_09.jpg"]
height = 600
xs = [625, 850, 1075, 1300]
ys = [185, 125, 125, 185]
for name, x, y in zip(shots, xs, ys):
    shot = Image.open(HERE / "shots" / name if name.startswith(("shot_", "mixed_")) else name if name.endswith(".jpg") else SHOTS.format(name)).convert("RGB")
    width = round(shot.width * height / shot.height)
    place(shot.resize((width, height), Image.LANCZOS), x - 30, y, 26)

canvas.convert("RGB").save(OUT, optimize=True)
print(OUT, canvas.size)
