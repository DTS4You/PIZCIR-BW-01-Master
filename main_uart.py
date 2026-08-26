import uasyncio as asyncio
from libs.modul_uart_async import AsyncUART

# Callback-Funktion: Wird automatisch aufgerufen, wenn Daten eintreffen
def daten_empfangen_handler(nachricht):
    print(f"[RX Empfangen]: {nachricht}")
    
    # Beispiel: Auf bestimmte Befehle reagieren und direkt antworten
    if nachricht.upper() == "PING":
        uart_dev.send_line("PONG")

# Modul-Instanz erstellen (auf UART0, GP0/GP1)
uart_dev = AsyncUART(
    uart_id=0,
    baudrate=9600,
    tx_pin=0,
    rx_pin=1,
    on_receive=daten_empfangen_handler
)

async def haupt_schleife():
    # UART-Empfangstask im Hintergrund starten
    uart_dev.start()
    
    counter = 0
    while True:
        # Periodisch Daten senden
        uart_dev.send_line(f"Statusmeldung #{counter}")
        counter += 1
        
        # Unabhängige Hauptschleife läuft weiter
        print("Hauptprogramm arbeitet...")
        await asyncio.sleep(5)

# Event-Loop starten
try:
    asyncio.run(haupt_schleife())
except KeyboardInterrupt:
    print("Programm beendet.")

