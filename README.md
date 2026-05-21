# PIZCIR-Bundeswehr-Weltall
Bundeswehr-Weltall-Modell
https://github.com/DTS4You/PIZCIR-Bundeswehr-Weltall/blob/main/README.md
# -----------------------------------------------------------------------------
Zuordnung:

Code    Funktion
01      xyz

Modbus:

Adresse:    Funktion:
0           Status
1           Funktionscode
2           Wert


Status:
0   ->      Run / Normal
1   ->      Stop / Normal
2   ->      Reset
3   ->      Befehl

Funktionscode:
0   ->      do all

Wert:
0   ->      "off"   -> Aus
1   ->      "def"   -> Default
2   ->      "on"    -> Ein
3   ->      "blink" -> Blinken