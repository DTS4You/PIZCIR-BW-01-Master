######################################################
### Main-Program                                   ###
### Projekt: BIZCIR-BW-01-Master                   ###
### Version: 1.02          29.08.2026              ###
######################################################
from machine import UART, Pin
from libs.modul_uart_async import AsyncUART
from libs.modul_xio_bus import ParallelBus
import time, sys
import uctypes
import uasyncio as asyncio
import libs.modul_ws2812_dma as myws2812
import libs.modul_hwdebug as myhwdebug
import libs.modul_anim_obj as myanim
import libs.modul_color_index as mycolor



global hwdebug
hwdebug = myhwdebug.HWDEBUG()
global ws2812
leds = myws2812.WS2812Fast(start_pin=2, leds_per_strip=175)

mycolor.color_setup()
myanim.pattern_setup()
myanim.anim_setup()

global led_offset
led_offset = 0

#------------------------------------------------------------------------------
# Callback-Funktionen
#------------------------------------------------------------------------------
# UART -> hat Daten empfangen
def daten_empfangen_handler(nachricht):
    print(f"[RX Empfangen]: {nachricht}")
    
    # Beispiel: Auf bestimmte Befehle reagieren und direkt antworten
    if nachricht.upper() == "PING":
        uart_dev.send_line("PONG")
#------------------------------------------------------------------------------
# 4-Bit parallel-Bus
def on_string_received(text):
    print(f"\n[RX Event] Empfangener Text: '{text}' (Länge: {len(text)})")
#------------------------------------------------------------------------------
# Modul-Instanz erstellen (auf UART0, GP0/GP1)
uart_dev = AsyncUART(
    uart_id=0,
    baudrate=9600,
    tx_pin=0,
    rx_pin=1,
    on_receive=daten_empfangen_handler
)
# Modul-Bus-Instanz erstellen
bus = ParallelBus(
    data_pins=[10, 11, 12, 13], pin_strobe_high=14, pin_strobe_low=15
)
#------------------------------------------------------------------------------
# --- Hintergrund-Task simulieren ---
#------------------------------------------------------------------------------
async def background_heartbeat():
    print("Starte Background Task...")
    blink_time = 0.5
    blink_state = False
    counter = 1
    while True:
        #print("Hintergrund-Task: Status-LED blinken")
        hwdebug.write_output(blink_state)
        blink_state = not blink_state
        #uart_dev.send_line("Heartbeat -> " + str(counter))
        #----------------------------------------------------------------------
        # Beispiel: Senden über Parallel-Bus !!!
        msg = "do,anim," + str(counter)
        print(msg)
        await bus.send_text(msg)
        #----------------------------------------------------------------------
        counter = counter + 1
        if counter > 99:
            counter = 1
        await asyncio.sleep(blink_time)
#------------------------------------------------------------------------------

def inc_offset():
    global led_offset
    led_offset = led_offset + 1
    if led_offset > 20:
        led_offset = 0
    #print("LED Offset:", led_offset)

def draw_led_frame(offset):
    #print("Zeichne LED-Frame mit Offset:", offset)
    for s in range(8):
        for i in range(5):
            [r, g, b] = mycolor.color_index[2].red, mycolor.color_index[2].green, mycolor.color_index[2].blue
            leds.set_pixel_rgb(s, i + offset, r, g, b)
        

#------------------------------------------------------------------------------
# Main-Loop als asynchroner Task
#------------------------------------------------------------------------------
async def main_loop():

    frame_time = 0.02
    print("Starte WS2812-Berechnung...")
    while True:
        # Aktuelle Adressen des Ziel-Buffers holen
        #if leds.write_index == 0:
        #    addrs_ptr = uctypes.addressof(leds.addrs_set0)
        #else:
        #    addrs_ptr = uctypes.addressof(leds.addrs_set1)
        #----------------------------------------------------------------------
        leds.clear()
        leds.fill_strip_rgb(2,  0,  0, 40)
        leds.fill_strip_rgb(3,  0, 40,  0)
        leds.fill_strip_rgb(4, 40,  0,  0)
        draw_led_frame(led_offset)
        leds.show()
        inc_offset()
        await asyncio.sleep(frame_time)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# --- Alle Tasks starten ---
#-----------------------------------------------------------------------------
async def main():
    # UART-Empfangstask im Hintergrund starten
    uart_dev.start()
    print("Starte Main-Loop und Hintergrund-Task...")
    await asyncio.gather(
        main_loop(),
        background_heartbeat()
    )

#------------------------------------------------------------------------------
# --- Hardware Startbedingung -> Taste drücken ---
#-----------------------------------------------------------------------------
def wait_hardware_run():
    print("Tastenabfrage...")
    while(hwdebug.read_input()==True):      # Warten, bis die Taste gedrückt wird (LOW)
        time.sleep(0.2)                     # Kurze Pause, um die CPU nicht zu blockieren
        sys.exit()
    print("Bedingung erfüllt => Starte Programm...")

#------------------------------------------------------------------------------
#--- Ab hier startet das Programm
#-----------------------------------------------------------------------------
try:
    print("Programmstart...")
    wait_hardware_run()  # Warte auf Tastendruck
    asyncio.run(main())
except KeyboardInterrupt:
    hwdebug.write_output(0)
    print("Programm wurde durch Benutzer abgebrochen.")
    leds.clear()
    leds.show()
    leds.cleanup()
    del leds
    #--------------------------------------------------------------------------
    #--- Reset des Controllers ---
    #--------------------------------------------------------------------------
    machine.reset()
    #--------------------------------------------------------------------------
#==============================================================================
