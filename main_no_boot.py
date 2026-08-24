######################################################
### Main-Program                                   ###
### Projekt: BIZCIR-BW-01-Master                   ###
### Version: 1.01          24.08.2026              ###
######################################################
from machine import Pin
import time
import uctypes
import uasyncio as asyncio
import libs.module_ws2812_dma as myws2812
import libs.module_hwdebug as myhwdebug

global hwdebug
hwdebug = myhwdebug.HWDEBUG()
global ws2812
leds = myws2812.WS2812Fast(start_pin=2, leds_per_strip=175)

global led_offset
led_offset = 0

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
            leds.set_pixel_rgb(s, i + offset, 10, 150, 10)
        

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
