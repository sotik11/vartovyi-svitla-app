from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np

HERE = Path(__file__).resolve().parent

SHOTS = str(HERE.parent / "screenshots" / "dark" / "{}.jpg")
HERO = HERE.parent / "hero.webp"
OUT = HERE / "post-vertical.png"
W, H = 1226, 1440
BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
REG = r"C:\Windows\Fonts\segoeui.ttf"
GOLD = (240, 184, 64)

# Night-blue ground: a warm glow behind the owl, a cold one behind the screens.
yy, xx = np.mgrid[0:H, 0:W]
base = np.zeros((H, W, 3), float)
base[:] = (8, 14, 30)
glow = np.exp(-(((xx - 230) / 380) ** 2 + ((yy - 230) / 300) ** 2))
base += glow[..., None] * np.array([40, 34, 18])
cold = np.exp(-(((xx - 600) / 700) ** 2 + ((yy - 1000) / 450) ** 2))
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

# The owl, and the words beside it.
hero = Image.open(HERO).convert("RGB")
hero = hero.crop((70, 60, hero.width - 70, hero.height - 70)).resize((300, 300), Image.LANCZOS)
place(hero, 80, 80, 56, shadow=34)

draw = ImageDraw.Draw(canvas)
draw.text((430, 82), "Вартовий Світла", font=ImageFont.truetype(BOLD, 62), fill=GOLD)
sub = ImageFont.truetype(REG, 30)
draw.text((433, 172), "Твій персональний контроль", font=sub, fill=(225, 230, 240))
draw.text((433, 212), "електропостачання", font=sub, fill=(225, 230, 240))
small = ImageFont.truetype(REG, 25)
y = 278
for words in ["Завжди свіжий графік ДТЕК", "Сповіщення про зміни й відключення",
              "Статистика: за графіком і фактично", "Віджети на головний екран"]:
    draw.ellipse((437, y + 12, 448, y + 23), fill=GOLD)
    draw.text((462, y), words, font=small, fill=(190, 198, 215))
    y += 40
note = "Android · безкоштовно · без реклами"
note_font = ImageFont.truetype(REG, 22)
draw.text(((W - draw.textlength(note, font=note_font)) / 2, 470), note, font=note_font, fill=(120, 132, 158))

# Four screens in a row under it, the middle two a little higher.
shots = ["shot_home.jpg", SHOTS.replace("dark", "light").format("08"), "shot_summary.jpg", "mixed_09.jpg"]
height = 760
xs = [24, 286, 548, 810]
ys = [600, 555, 555, 600]
for name, x, y in zip(shots, xs, ys):
    shot = Image.open(HERE / "shots" / name if name.startswith(("shot_", "mixed_")) else name if name.endswith(".jpg") else SHOTS.format(name)).convert("RGB")
    width = round(shot.width * height / shot.height)
    place(shot.resize((width, height), Image.LANCZOS), x, y, 28)

canvas.convert("RGB").save(OUT, optimize=True)
print(OUT, canvas.size)
