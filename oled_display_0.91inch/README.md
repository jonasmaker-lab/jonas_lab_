# Hallo Welt auf dem 0.91" OLED (Raspberry Pi Pico)

Deinen eigenen Text auf einem 0.91-Zoll-OLED-Display (SSD1306, 128×32 Pixel)
anzeigen — mit einem Raspberry Pi Pico oder Pico W. Funktioniert auf
**Windows und Mac**, ganz ohne Programmieren:

> **Text ändern = `nachricht.txt` bearbeiten, dann flashen. Fertig.**

## Was du brauchst

- Raspberry Pi Pico oder Pico W
  ([mit angelöteten Headers](https://amzn.to/4g1XR44) — direkt loslegen |
  [ohne Header](https://amzn.to/4x391ey) — selbst löten)
  - alternativ ein [ESP32-Board](https://amzn.to/4vUc3kk) — Hinweis: damit habe
    ich den Code hier nicht explizit getestet (andere Pins, MicroPython-Firmware
    fürs ESP32-Board nötig)
- [0.91" OLED-Display mit I2C](https://amzn.to/4bUdEiX) (4 Pins: GND, VCC, SCL, SDA)
- [4 Jumper-Kabel (Dupont-Set)](https://amzn.to/4wy5Vzs) + [Micro-USB-**Datenkabel**](https://amzn.to/4g1b9xJ) (reine Ladekabel funktionieren nicht!)

*Als Amazon-Partner verdiene ich an qualifizierten Käufen.*
- Python 3.8 oder neuer auf deinem Computer ([python.org/downloads](https://www.python.org/downloads/))
  - Windows: beim Installieren den Haken bei **"Add Python to PATH"** setzen!

## Verkabelung

| OLED-Pin | Pico-Pin              |
|----------|-----------------------|
| GND      | GND (z. B. Pin 38)    |
| VCC      | 3V3 (Pin 36)          |
| SCL      | GPIO1 (Pin 2)         |
| SDA      | GPIO0 (Pin 1)         |

Wo welcher Pin sitzt: [offizielles Pico-W-Pinout (PDF)](https://pip-assets.raspberrypi.com/categories/686-raspberry-pi-pico-w/documents/RP-008315-DS-1-PicoW-A4-Pinout.pdf)

## Schritt 1: MicroPython auf den Pico (einmalig)

Falls dein Pico noch fabrikneu ist:

1. Firmware herunterladen: [micropython.org/download/RPI_PICO_W](https://micropython.org/download/RPI_PICO_W/)
   (normaler Pico ohne W: [micropython.org/download/RPI_PICO](https://micropython.org/download/RPI_PICO/)) —
   die Datei endet auf `.uf2`
2. **BOOTSEL-Knopf gedrückt halten** und dabei den Pico per USB anstecken
3. Es erscheint ein Laufwerk namens `RPI-RP2` — die `.uf2`-Datei dort hineinziehen
4. Der Pico startet automatisch neu. Fertig, das musst du nie wieder machen

## Schritt 2: Flashen

**Windows:** Doppelklick auf `flash.bat`

**Mac:** Doppelklick auf `flash.command`
(beim allerersten Mal blockt macOS eventuell: Rechtsklick → "Öffnen" → "Öffnen")

Das war's. Das Skript installiert sich das Flash-Tool selbst, findet den
Pico automatisch und kopiert alles rüber. Danach zeigt das Display deine
Nachricht — auch nach dem Abstecken, alles bleibt auf dem Pico gespeichert.

Alternativ im Terminal: `python flash.py` (Windows notfalls `py flash.py`).

## Schritt 3: Rumspielen 🎛️

**Deinen Text ändern** → `nachricht.txt` öffnen (Doppelklick, ganz normaler
Editor), Text reinschreiben, speichern, nochmal flashen (Schritt 2).
Umlaute (ä/ö/ü) werden echt dargestellt, nur ß wird zu ss.

**Aussehen ändern** → `einstellungen.txt` öffnen:

| Einstellung  | Werte | Was sie macht |
|--------------|-------|---------------|
| `groesse`    | 1–4 | Schriftgröße. Bei 1 passen 16 Zeichen aufs Display, bei 2 nur 8 |
| `modus`      | `static` / `scroll` / `blink` / `bounce` | steht / läuft durch / blinkt / hüpft wie der DVD-Screensaver |
| `tempo`      | 1–10 | Geschwindigkeit bei scroll/blink/bounce |
| `invertiert` | `ja` / `nein` | Schwarzer Text auf weißem Grund |
| `helligkeit` | 0–255 | 0 = fast aus, 255 = volle Helligkeit |
| `gedreht`    | `ja` / `nein` | Anzeige um 180° drehen (wenn das Display kopfüber verbaut ist) |

Nach jeder Änderung: nochmal flashen. Ausprobier-Ideen: langer Text mit
`modus = scroll`, oder dein Name mit `groesse = 3` und `modus = bounce`.

Wer tiefer einsteigen will: der eigentliche Code liegt in `src/main.py` —
dort kann man mit `oled.pixel()`, `oled.line()`, `oled.rect()` auch
eigene Grafik malen.

## Probleme?

| Symptom | Lösung |
|---------|--------|
| `kein pico gefunden` | Anderes USB-Kabel probieren (Datenkabel!), Thonny schließen falls offen, MicroPython installiert? (Schritt 1) |
| Display bleibt schwarz | Verkabelung prüfen: SDA↔GPIO0, SCL↔GPIO1 vertauscht ist der Klassiker. VCC an 3V3? |
| `python` nicht gefunden (Windows) | `py flash.py` im Terminal probieren, oder Python neu installieren mit "Add to PATH"-Haken |
| macOS blockt flash.command | Rechtsklick → "Öffnen" → "Öffnen" (nur beim ersten Mal nötig) |
| Text abgeschnitten | `groesse` kleiner machen oder kürzere Nachricht — bei Größe 2 passen nur 8 Zeichen, `modus = scroll` zeigt beliebig lange Texte |

## Was liegt in diesem Ordner?

```
oled_display_0.91inch/
├── README.md            <- diese anleitung
├── nachricht.txt        <- DEIN TEXT — hier aendern!
├── einstellungen.txt    <- groesse, modus, tempo, ...
├── flash.bat            <- doppelklick-flasher (windows)
├── flash.command        <- doppelklick-flasher (mac)
├── flash.py             <- das eigentliche flash-skript
└── src/
    ├── main.py          <- der code, der auf dem pico laeuft
    └── ssd1306.py       <- display-treiber
```
