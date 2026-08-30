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
7. SPOCK        7           !_Nicht vorhanden_!
8. Galileo	    8   		2, 3 ,                   9 , 10     
# -----------------------------------------------------------------------------
Nr. HTML-Code	                    Stripe:
0	do,all,def	    Default			
1	do,obj,1,blink	H2Sat	        1, 2	            1, 2	
2	do,obj,2,blink	EnMap	        3, 4	            3, 4	
3	do,obj,3,blink	SARah	        11, 12, 15		                        3, 4, 7
4	do,obj,4,blink	SAR_Lupe	    3, 4	            3, 4	
5	do,obj,5,blink	SATCOMBw	    1, 2, 5, 6, 7, 8	1, 2, 5, 6, 7, 8	
6	do,obj,6,blink	TerraSAR-X	    13, 14		                            5, 6
7	do,obj,7,blink	SPOCK	---		
8	do,obj,8,blink	Galileo	        2, 3, 9, 10	        2, 3	            1, 2
# -----------------------------------------------------------------------------
XIO Parallel Bus:   Master -> Slave / Richtung -> Senden
Funktionen:
Serial Kommandos werden werden über die UART empfangen
und 1:1 weiter über den Bus gesendet.
# -----------------------------------------------------------------------------