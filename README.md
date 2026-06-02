# PIZCIR-Bundeswehr-Weltall
Bundeswehr-Weltall-Modell-Master
https://github.com/DTS4You/PIZCIR-Bundeswehr-Weltall/blob/main/README.md
# -----------------------------------------------------------------------------
Funktionszuordnung:

Funktion:	    HTML-Code	Stripe:
# -----------------------------------------------------------------------------

1. H2SAT	    1   		1, 2

2. EnMAP	    2   		3, 4

3. SARah	    3   		3, 4,                   11, 12, 15   

4. SAR-Lupe	    4   		3, 4

5. SATCOMBw     5		    1, 2, 5, 6, 7, 8

6. TerraSAR-X	6	    	3, 4,                   13, 14

7. SPOCK        7           Wird nicht dargestellt !!!

8. Galileo	    8   		2, 3 ,                   9 , 10     

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