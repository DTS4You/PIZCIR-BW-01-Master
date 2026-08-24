######################################################
### Main-Program                                   ###
### Projekt: BIZCIR-BW-01-Master                   ###
### Version: 1.01          24.08.2026              ###
######################################################
from machine import UART, Pin
import time, sys
import uctypes
import uasyncio as asyncio
import libs.module_ws2812_dma as myws2812
import libs.module_hwdebug as myhwdebug
import libs.modul_anim_obj as myanim
import libs.modul_color_index as mycolor

# UART wie gewohnt initialisieren
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1), rxbuf=256)

global hwdebug
hwdebug = myhwdebug.HWDEBUG()
global ws2812
leds = myws2812.WS2812Fast(start_pin=2, leds_per_strip=175)

mycolor.color_setup()
myanim.pattern_setup()
myanim.anim_setup()

global led_offset
led_offset = 0

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
        text = value + "\n"
        uart.write(text.encode('utf-8'))


#------------------------------------------------------------------------------
# --- Hintergrund-Task simulieren ---
#------------------------------------------------------------------------------
async def background_heartbeat():
    print("Starte Background Task...")
    blink_time = 0.5
    blink_state = False

    while True:
        #print("Hintergrund-Task: Status-LED blinken")
        hwdebug.write_output(blink_state)
        blink_state = not blink_state
        uart_sender("Heartbeat")
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

    frame_time = 0.05
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
        #await asyncio.sleep(frame_time)
        #leds.clear()
        #leds.show()
        await asyncio.sleep(frame_time)
        #await asyncio.sleep(0.05)  # Kurze Pause, um die CPU nicht zu blockieren
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# --- Alle Tasks starten ---
#-----------------------------------------------------------------------------
async def main():
    print("Starte Main-Loop und Hintergrund-Task...")
    await asyncio.gather(
        uart_receiver(),
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
