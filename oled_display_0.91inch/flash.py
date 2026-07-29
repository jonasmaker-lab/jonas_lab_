#!/usr/bin/env python3
# ---------------------------------------------------------------------
#  flash.py — kopiert den OLED-Code auf den Raspberry Pi Pico (W)
#
#  funktioniert auf windows, macos und linux. einzige voraussetzung:
#  python 3.8+ ist installiert und der pico laeuft mit micropython.
#
#  benutzung:   python flash.py          (windows: evtl. "py flash.py")
# ---------------------------------------------------------------------

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
# (lokale datei, name auf dem pico)
FILES = [
    (HERE / "src" / "ssd1306.py", "ssd1306.py"),
    (HERE / "src" / "main.py", "main.py"),
    (HERE / "nachricht.txt", "nachricht.txt"),
    (HERE / "einstellungen.txt", "einstellungen.txt"),
]

MPREMOTE = None  # wird in find_mpremote() gesetzt


def run(args):
    return subprocess.run(MPREMOTE + args, capture_output=True, text=True)


def resolve_mpremote():
    # 1. mpremote schon als kommando installiert? (z. b. via pipx oder pip)
    path = shutil.which("mpremote")
    if path:
        return [path]
    # 2. als python-modul installiert?
    try:
        import mpremote  # noqa: F401
        return [sys.executable, "-m", "mpremote"]
    except ImportError:
        return None


def install_mpremote():
    print("mpremote (das flash-tool) fehlt noch, installiere es kurz ...")
    # erst normal versuchen, dann mit --break-system-packages
    # (noetig auf macos mit homebrew-python und manchen linuxen, pep 668)
    for extra in ([], ["--break-system-packages"]):
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--user", "mpremote"] + extra,
            capture_output=True, text=True)
        if result.returncode == 0:
            print("mpremote installiert.")
            return True
    print("konnte mpremote nicht automatisch installieren.")
    print("bitte einmal manuell ausfuehren und flash.py dann erneut starten:")
    print(f"  {sys.executable} -m pip install --user mpremote")
    return False


def main():
    print("=" * 55)
    print("  OLED Hallo Welt  ->  Raspberry Pi Pico")
    print("=" * 55)

    # schritt 1: flash-tool sicherstellen
    global MPREMOTE
    MPREMOTE = resolve_mpremote()
    if MPREMOTE is None:
        if not install_mpremote():
            return 1
        MPREMOTE = resolve_mpremote()
        if MPREMOTE is None:
            print("mpremote installiert, aber nicht auffindbar. bitte terminal")
            print("neu oeffnen und flash.py nochmal starten.")
            return 1

    # schritt 2: quelldateien pruefen
    for src, _ in FILES:
        if not src.exists():
            print(f"FEHLER: {src.name} fehlt. bitte den ganzen ordner herunterladen.")
            return 1

    # zeigen, was geflasht wird
    try:
        message = next(
            line.strip()
            for line in (HERE / "nachricht.txt").read_text(encoding="utf-8").split("\n")
            if line.strip())
    except StopIteration:
        print("FEHLER: nachricht.txt ist leer. bitte eine zeile text reinschreiben.")
        return 1
    print(f'deine nachricht: "{message}"')

    # schritt 3: pico suchen (mpremote findet ihn automatisch)
    print("suche den pico am usb-port ...")
    probe = run(["exec", "print('ok')"])
    if probe.returncode != 0 or "ok" not in probe.stdout:
        print()
        print("kein pico gefunden. checkliste:")
        print("  1. usb-kabel eingesteckt? (manche kabel koennen nur laden,")
        print("     kein datentransfer -> anderes kabel probieren)")
        print("  2. micropython-firmware installiert? siehe README schritt 1")
        print("  3. thonny oder ein anderes programm offen, das den port")
        print("     blockiert? -> schliessen und nochmal probieren")
        return 1
    print("pico gefunden!")

    # schritt 4: dateien kopieren
    for src, remote in FILES:
        print(f"kopiere {remote} ...")
        result = run(["cp", str(src), f":{remote}"])
        if result.returncode != 0:
            print(f"FEHLER beim kopieren von {remote}:")
            print(result.stderr or result.stdout)
            return 1

    # schritt 5: neustart, damit main.py sofort laeuft
    run(["reset"])
    print()
    print("fertig! das display zeigt jetzt deine nachricht.")
    print("zum aendern: nachricht.txt oder einstellungen.txt bearbeiten")
    print("und nochmal flashen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
