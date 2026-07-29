#!/bin/bash
# doppelklick-flasher fuer macos
cd "$(dirname "$0")"
python3 flash.py
echo ""
read -p "enter druecken zum schliessen ..."
