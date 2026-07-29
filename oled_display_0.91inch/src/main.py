# =====================================================================
#  Hallo Welt auf dem 0.91" OLED (SSD1306, 128x32) am Raspberry Pi Pico
#
#  Verkabelung:  OLED SDA -> GPIO0   |   OLED SCL -> GPIO1
#                OLED VCC -> 3V3     |   OLED GND -> GND
#
#  Text und Optionen kommen aus nachricht.txt und einstellungen.txt —
#  diese Datei musst du zum Rumspielen nicht anfassen.
# =====================================================================

from machine import Pin, I2C
import framebuf
import time
import ssd1306

WIDTH, HEIGHT = 128, 32
CHAR_W = 8  # breite eines zeichens im eingebauten 8x8-font

# ------------------- NACHRICHT + EINSTELLUNGEN LESEN -----------------


def read_file(name):
    try:
        with open(name) as f:
            return f.read()
    except OSError:
        return None


def read_message():
    raw = read_file("nachricht.txt")
    if raw:
        for line in raw.split("\n"):
            line = line.strip()
            if line:
                # ae/oe/ue zeichnen wir selbst (siehe render_line),
                # nur fuer ss gibt es keinen sinnvollen ersatz-glyph
                return line.replace("ß", "ss")
    return "Hallo Welt!"


def read_settings():
    # defaults, falls die datei fehlt oder eine zeile kaputt ist
    s = {"groesse": 2, "modus": "static", "tempo": 3,
         "invertiert": False, "helligkeit": 255, "gedreht": False}
    raw = read_file("einstellungen.txt")
    if not raw:
        return s
    for line in raw.split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip().lower()
        value = value.strip().lower()
        if key in ("groesse", "tempo", "helligkeit"):
            try:
                s[key] = int(value)
            except ValueError:
                pass
        elif key in ("invertiert", "gedreht"):
            s[key] = value in ("ja", "yes", "true", "1")
        elif key == "modus":
            if value in ("static", "scroll", "blink", "bounce"):
                s[key] = value
    # auf sinnvolle bereiche begrenzen
    s["groesse"] = min(4, max(1, s["groesse"]))
    s["tempo"] = min(10, max(1, s["tempo"]))
    s["helligkeit"] = min(255, max(0, s["helligkeit"]))
    return s


TEXT = read_message()
CFG = read_settings()
SIZE = CFG["groesse"]
SPEED = CFG["tempo"]

# ------------------------- SETUP -------------------------------------

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
oled = ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)
oled.contrast(CFG["helligkeit"])
oled.invert(CFG["invertiert"])
if CFG["gedreht"]:
    oled.rotate(0)

# ------------------------- HELFER ------------------------------------


# der eingebaute font kennt nur ascii. fuer umlaute zeichnen wir den
# grundbuchstaben eine zeile tiefer und setzen zwei punkte darueber
UMLAUT = {"ä": "a", "ö": "o", "ü": "u", "Ä": "A", "Ö": "O", "Ü": "U"}


def render_line(text):
    # text zeichenweise in einen 8 pixel hohen puffer rendern
    w = len(text) * CHAR_W
    buf = bytearray(w)  # 8 pixel hoch -> 1 byte pro spalte
    small = framebuf.FrameBuffer(buf, w, 8, framebuf.MONO_VLSB)
    for i, ch in enumerate(text):
        cx = i * CHAR_W
        base = UMLAUT.get(ch)
        if base is None:
            small.text(ch, cx, 0)
        else:
            small.text(base, cx, 1)
            small.pixel(cx + 2, 0, 1)
            small.pixel(cx + 5, 0, 1)
    return small, w


def draw_text(text, x, y, size=1):
    # erst in den kleinen puffer rendern, dann jedes gesetzte pixel als
    # size-x-size-quadrat aufs display bringen (pixel-art-scaling)
    small, w = render_line(text)
    for sx in range(w):
        for sy in range(8):
            if small.pixel(sx, sy):
                oled.fill_rect(x + sx * size, y + sy * size, size, size, 1)


def text_width(text, size):
    return len(text) * CHAR_W * size


def centered_y(size):
    return max(0, (HEIGHT - 8 * size) // 2)


def show_static():
    oled.fill(0)
    x = max(0, (WIDTH - text_width(TEXT, SIZE)) // 2)
    draw_text(TEXT, x, centered_y(SIZE), SIZE)
    oled.show()


def show_scroll():
    w = text_width(TEXT, SIZE)
    y = centered_y(SIZE)
    x = WIDTH
    while True:
        oled.fill(0)
        draw_text(TEXT, x, y, SIZE)
        oled.show()
        x -= SPEED
        if x < -w:
            x = WIDTH
        time.sleep_ms(20)


def show_blink():
    on = True
    while True:
        if on:
            show_static()
        else:
            oled.fill(0)
            oled.show()
        on = not on
        time.sleep_ms(1100 - SPEED * 100)


def show_bounce():
    w = text_width(TEXT, SIZE)
    h = 8 * SIZE
    x, y = 0, 0
    dx, dy = SPEED, 1
    while True:
        oled.fill(0)
        draw_text(TEXT, x, y, SIZE)
        oled.show()
        x += dx
        y += dy
        if x <= 0 or x + w >= WIDTH:
            dx = -dx
        if y <= 0 or y + h >= HEIGHT:
            dy = -dy
        time.sleep_ms(20)


# ------------------------- LOS GEHTS ---------------------------------

MODE = CFG["modus"]
if MODE == "scroll":
    show_scroll()
elif MODE == "blink":
    show_blink()
elif MODE == "bounce":
    show_bounce()
else:
    show_static()
