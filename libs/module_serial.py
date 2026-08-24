import uasyncio as asyncio
from machine import UART, Pin

# UART wie gewohnt initialisieren
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1), rxbuf=256)

# Das entspricht funktional deiner Interrupt-Service-Routine
async def uart_receiver():
    # StreamReader macht aus dem UART ein asynchrones Event
    reader = asyncio.StreamReader(uart)
    
    print("Async-UART-Empfänger gestartet...")
    while True:
        # Hier "schläft" die Funktion völlig ohne CPU-Last,
        # bis exakt in dem Moment Daten am RX-Pin eintreffen!
        line = await reader.readline()
        
        # Sobald Daten da sind, geht es sofort hier weiter:
        print("Empfangen:", line.decode('utf-8').strip())

def uart_sender(value):
        text = f"Hallo RP2040! {value} \n"
        uart.write(text.encode('utf-8'))

async def haupt_programm():
    # Starte den UART-Lauscher im Hintergrund
    asyncio.create_task(uart_receiver())
    
    # Deine normale Hauptschleife
    counter = 0
    while True:
        print(f"Hauptschleife arbeitet ungestört... ({counter})")
        uart_sender(counter)
        counter += 1
        await asyncio.sleep(2) # Nicht-blockierendes Warten!

# Programm starten
try:
    asyncio.run(haupt_programm())
except KeyboardInterrupt:
    print("Beendet")

