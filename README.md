# PIZCIR-Bundeswehr-Weltall
Bundeswehr-Weltall-Modell-Master
https://github.com/DTS4You/PIZCIR-Bundeswehr-Weltall/blob/main/README.md
# -----------------------------------------------------------------------------
Funktionszuordnung:

Funktion:	    HTML-Code	Stripe:
# -----------------------------------------------------------------------------

1. SATCOMBw     1		    1, 2, 5, 6, 7, 8

2. Galileo	    2   		2, 3 ,9 , 10

3. SARah	    3   		3, 4, 11, 12, 15

4. TerraSAR-X	4	    	3, 4, 13, 14

5. H2SAT	    5   		1, 2

6. EnMAP	    6   		3, 4

7. SAR-Lupe	    7   		3, 4

# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------

XIO_2 Bus:

Richtung -> Senden

Funktionen:
0         -> Keine Funktion 
1 - 63    -> Funktion 1 - 63

# -----------------------------------------------------------------------------

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

# -----------------------------------------------------------------------------