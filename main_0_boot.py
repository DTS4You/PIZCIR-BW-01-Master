######################################################
### Main-Program                                   ###
### Projekt: BIZCIR-BW-01-Master                   ###
### Version: 1.02          29.08.2026              ###
######################################################
from machine import UART, Pin
from libs.uart_async import AsyncUART
from libs.xio_bus import ParallelBus
from libs.ws2812_parallel_async import WS2812ParallelAsync
import time, sys
import uctypes
import uasyncio as asyncio
import json


global led_offset
led_offset = 0

#==============================================================================
# Globales Dictionary für die Konfigurationswerte
CONFIG = {}

def load_global_config(filepath="config.json"):

    global CONFIG
    
    # Standardwerte (Fallbacks), falls die JSON-Datei fehlt oder unvollständig ist
    defaults = {
        "leds_per_stripe": 178,
        "leds_brightness": 64,
        "frame_time": 20,
        "blink_time": 500,
        "debug_time": 1000,
        "board_modus": "Master",
        "load_modul_hwdebug": True,
        "load_modul_anim_obj": True,
        "load_modul_fcode": True,
        "offset_led": 1,
        "offset_obj": 1,
        "offset_pattern": 1
    }
    
    try:
        with open(filepath, "r") as f:
            loaded_data = json.load(f)
            defaults.update(loaded_data)
            print(f"[CONFIG] '{filepath}' erfolgreich geladen.")
    except (OSError, ValueError) as e:
        print(f"[CONFIG] Fehler beim Laden von '{filepath}': {e}. Nutze Standardwerte.")
    
    CONFIG = defaults
#==============================================================================

# --- 1. KONFIGURATION BEIM START LADEN ---
load_global_config("cfg_global.json")

# --- 2. OPTIONALE MODUL-STEUERUNG ---
if CONFIG["load_modul_hwdebug"]:
    print("[INIT] -> Modul Hardware-Debug wird geladen...")
    global hwdebug
    import libs.hwdebug as myhwdebug
    hwdebug = myhwdebug.HWDEBUG()
else:
    print("[INIT] ## Modul Hardware-Debug wird nicht geladen ##")

if CONFIG["load_modul_anim_obj"]:
    print("[INIT] -> Modul Animationsobjekte wird geladen...")
    global anim_obj
    import libs.anim_obj as myanim
    color_file = "cfg_colors.json"
    mycolor = myanim.load_or_create_colors(color_file)
    patterns_file   = "cfg_patterns.json"
    objects_file    = "cfg_anim_objects.json"
    # 1. Zuerst Patterns laden
    anim_pattern = myanim.load_or_create_patterns(patterns_file)
    # 2. Dann Animationsobjekte laden und mit den loaded Patterns verknüpfen
    anim_obj = myanim.load_or_create_objects(objects_file, anim_pattern)
else:
    print("[INIT] ## Modul Animationsobjekte wird nicht geladen ##")

if CONFIG["load_modul_fcode"]:
    print("[INIT] -> Modul F-Code wird geladen...")
    global fcode_array
    import libs.fcode as myfcode
    filepath = "cfg_fcode_array.json"
    fcode_array = myfcode.load_or_create_json(filepath)
else:
    print("[INIT] ## Modul F-Code wird nicht geladen ##")

print("[Board-Modus]:", CONFIG["board_modus"])
print("[LEDs per Stripe]:", CONFIG["leds_per_stripe"])
print("[LEDs Helligkeit]:", CONFIG["leds_brightness"])
print("[INIT] -> Alle Module geladen. Starte Hauptprogramm...")


#------------------------------------------------------------------------------
# Callback-Funktionen
#------------------------------------------------------------------------------
# Callback-Funktion: Wird automatisch aufgerufen, wenn Daten eintreffen
def daten_empfangen_handler(nachricht):
    global rx_string
    print(f"[RX Empfangen]: {nachricht}")
    
    # Beispiel: Auf bestimmte Befehle reagieren und direkt antworten
    if nachricht.upper() == "PING":
        uart_dev.send_line("PONG")
    rx_string = nachricht
    #print(f"[RX] Empfangene Nachricht: '{rx_string}' (Länge: {len(rx_string)})")
    do_go_out(rx_string)

#------------------------------------------------------------------------------
def do_go_out(string):
    print(f"[RX-String] {string}")
    new_input_action(string)
#------------------------------------------------------------------------------

# 4-Bit parallel-Bus
def on_string_received(text):
    print(f"\n[RX Event] Empfangener Text: '{text}' (Länge: {len(text)})")
#------------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# WS2812-Instanz erstellen (auf Pin 2, 175 LEDs pro Strip)
#-----------------------------------------------------------------------------
global leds
leds = WS2812ParallelAsync(
        leds=200,
        first_pin=2,
        brightness=64,
        sm_id=0,
        yield_every=8,
        reset_us=300,
    )
#-----------------------------------------------------------------------------
# Instanz erstellen (auf UART0, GP0/GP1)
#------------------------------------------------------------------------------
uart_dev = AsyncUART(
    uart_id=0,
    baudrate=9600,
    tx_pin=0,
    rx_pin=1,
    on_receive=daten_empfangen_handler
)
#------------------------------------------------------------------------------
# Instanz erstellen parallel Bus über XIO-Pins
#------------------------------------------------------------------------------
bus = ParallelBus(
    data_pins=[10, 11, 12, 13], pin_strobe_high=14, pin_strobe_low=15
)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Neue Eingabe erfassen und verarbeiten
#------------------------------------------------------------------------------
def new_input_action(action_input):
    print(f"[INPUT] Neue Eingabe: '{action_input}'")
    treffer_werte = []
    obj_value = None
    
    if action_input.startswith("do,obj,"):
        parts = action_input.split(",")
        if len(parts) == 4 and parts[2].isdigit():
            obj_value = int(parts[2])
            print(f"Objekt-Wert erkannt: {obj_value}")
        else:
            print(f"[INPUT-FEHLER] Ungültiges Format: {action_input}")
            return
    elif action_input == "do,all,def":
        print("[INPUT] Befehl 'do,all,def' erkannt. Setze alle Animationen auf Default.")
        func_all_def()
        return
    else:
        print(f"[INPUT] Befehl wird nicht von 'do,obj,x,y' oder 'do,all,def' behandelt.")
        return

    # Prüfen, ob das Modul fcode überhaupt geladen wurde
    if fcode_array is None or not CONFIG["load_modul_fcode"]:
        print("[INPUT-FEHLER] Modul F-Code ist nicht geladen.")
        return

    # Abfangen von Bereichsfehlern beim Zugriff auf das Array
    idx = obj_value - CONFIG["offset_obj"]
    if 0 <= idx < len(fcode_array):
        treffer_werte = myfcode.get_array_from_obj(fcode_array, idx)
        print(f"Treffer-Werte: {treffer_werte}")
    else:
        print(f"[INPUT-FEHLER] Index {idx} außerhalb des F-Code-Bereichs.")
        return

    # Animationen schalten
    if anim_obj is not None:
        for i in range(len(anim_obj)):
            z = i + CONFIG["offset_obj"]
            if z in treffer_werte:
                #print(f"Treffer: Objekt {z} -> Animation starten")
                do_start_anim(z)
            else:
                #print(f"Objekt {z} -> auf Default setzen")
                do_stop_anim(z)

#-----------------------------------------------------------------------------

def do_start_anim(value):
    global anim_obj
    print(f"[DO] START Animation für Objekt {value}")
    anim_obj[value - CONFIG["offset_obj"]].modified = True

def do_stop_anim(value):
    print(f"[DO] STOP  Animation für Objekt {value}")
    anim_obj[value - CONFIG["offset_obj"]].modified = False

def func_all_def():
    print("[DO] Alle Animationen auf Default setzen.")
    if anim_obj is not None:
        for i in range(len(anim_obj)):
            z = i + CONFIG["offset_obj"]
            #print(f"Objekt {z} -> auf Default setzen")
            do_stop_anim(z)

#------------------------------------------------------------------------------
# --- Hintergrund-Task simulieren ---
#------------------------------------------------------------------------------
async def background_heartbeat():
    print("Starte Background Task...")
    # UART-Empfangstask im Hintergrund starten
    uart_dev.start()
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
        msg = "do," + str(counter)
        #print(msg)
        await bus.send_text(msg)
        #----------------------------------------------------------------------
        counter = counter + 1
        if counter > 99:
            counter = 1
        await asyncio.sleep(blink_time)
#------------------------------------------------------------------------------

def inc_offset():
    global led_offset
    led_offset = led_offset + 2
    if led_offset > 170:
        led_offset = 0
    #print("LED Offset:", led_offset)

def draw_led_frame(offset):
    dummy = 0
    #print("Zeichne LED-Frame mit Offset:", offset)
    for s in range(8):
        if anim_obj[s].modified:
            for i in range(5):
                [r, g, b] = myanim.int32_to_rgb(mycolor[2].rgb32, little_endian=True)
                #leds.set_pixel_rgb(s, i + offset, r, g, b)
                #leds.set_led(x=i + offset, y=s, r=0, g=40, b=40)
        else:
            for i in range(5):
                [r, g, b] = myanim.int32_to_rgb(mycolor[1].rgb32, little_endian=True)
                #leds.set_pixel_rgb(s, i + offset, r, g, b)
                #leds.set_led(x=i + offset, y=s, r=0, g=0, b=0)

#------------------------------------------------------------------------------
# Main-Loop als asynchroner Task
#------------------------------------------------------------------------------
async def main_loop():

    frame_time = 20  # Standardwert, kann später aus CONFIG geladen werden
    print("Starte WS2812-Berechnung...")
    while True:
        leds.clear()
        #draw_led_frame(led_offset)
        leds.fill_all((20,20,20))
        await leds.show(copy=False)
        inc_offset()
        await asyncio.sleep_ms(frame_time)
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
    main_loop.cancel()
    background_heartbeat.cancel()
finally:
    leds.clear()
    asyncio.run(leds.show(copy=False))
    time.sleep(0.1)
    asyncio.run(leds.deinit(blackout=True))
    print("Hardware sauber heruntergefahren...")
    #--------------------------------------------------------------------------
    #--- Reset des Controllers ---
    #--------------------------------------------------------------------------
    print("===RESET===")
    time.sleep(0.3)
    machine.reset()
    #___Go_Home___
    #--------------------------------------------------------------------------
#==============================================================================
