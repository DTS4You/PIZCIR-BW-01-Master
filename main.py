######################################################
### Main-Program                                   ###
### Projekt: BIZCIR-BW-01-Master                   ###
### Version: 1.04          14.10.2026              ###
######################################################
from machine import UART, Pin   # type: ignore
from libs.uart_async import AsyncUART
from libs.xio_bus import ParallelBus
from libs.ws2812_parallel_async import WS2812ParallelAsync
import time, sys
import uctypes                  # type: ignore
import uasyncio as asyncio      # type: ignore
import json

#------------------------------------------------------------------------------
machine.freq(250_000_000)       # type: ignore      # Anpassung CPU Clock
#------------------------------------------------------------------------------
# Master/Slave-Konfiguration setzen
CONFIG_FILE = "cfg_global_master.json"
#CONFIG_FILE = "cfg_global_slave.json"

global led_offset
led_offset = 0

#==============================================================================
# Globales Dictionary für die Konfigurationswerte
CONFIG = {}

def load_global_config(filepath=CONFIG_FILE):

    global CONFIG
    
    # Standardwerte (Fallbacks), falls die JSON-Datei fehlt oder unvollständig ist
    defaults = {
        "leds_per_stripe": 178,
        "leds_brightness": 64,
        "frame_time": 20,
        "blink_time": 500,
        "debug_time": 1000,
        "board_modus": "Master",
        "stripe_list": [0, 1, 2, 3, 4, 5, 6, 7],
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
load_global_config(CONFIG_FILE)

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
    color_index = myanim.load_or_create_colors(color_file)
    patterns_file   = "cfg_patterns.json"
    objects_file    = "cfg_anim_objects.json"
    # 1. Zuerst Patterns laden
    anim_pattern = myanim.load_or_create_patterns(patterns_file)
    # 2. Dann Animationsobjekte laden und mit den loaded Patterns verknüpfen
    anim_obj = myanim.load_or_create_objects(objects_file, anim_pattern, color_index)
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
print("[Stripe-Liste]:", CONFIG["stripe_list"])
print("[LEDs per Stripe]:", CONFIG["leds_per_stripe"])
print("[LEDs Helligkeit]:", CONFIG["leds_brightness"])
print("[Anzahl der Objekte]:", len(CONFIG["stripe_list"]))
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
# WS2812-Instanz erstellen (auf Pin 2-9, 178 LEDs pro Strip)
#-----------------------------------------------------------------------------
global leds
leds = WS2812ParallelAsync(
        leds=CONFIG["leds_per_stripe"],
        first_pin=2,
        brightness=CONFIG["leds_brightness"],
        sm_id=0,
        yield_every=32,
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
            asyncio.create_task(do_send_msg_bus(str(obj_value)))
        else:
            print(f"[INPUT-FEHLER] Ungültiges Format: {action_input}")
            return
    elif action_input == "do,all,def":
        print("[INPUT] Befehl 'do,all,def' erkannt. Setze alle Animationen auf Default.")
        asyncio.create_task(do_send_msg_bus())
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
                print(f"Treffer: Objekt {z} -> Animation starten")
                do_start_anim(z)
            else:
                #print(f"Objekt {z} -> auf Default setzen")
                do_stop_anim(z)

#-----------------------------------------------------------------------------

def do_start_anim(value):
    global anim_obj
    print(f"[DO] START Animation für Objekt {value}")
    anim_obj[value - CONFIG["offset_obj"]].set_anim_state(True)

def do_stop_anim(value):
    print(f"[DO] STOP  Animation für Objekt {value}")
    anim_obj[value - CONFIG["offset_obj"]].set_default_state(False)
    anim_obj[value - CONFIG["offset_obj"]].set_anim_state(False)

def do_default_anim(value):
    print(f"[DO] DEFAULT Animation für Objekt {value}")
    anim_obj[value - CONFIG["offset_obj"]].set_default_state(True)

def func_all_def():
    print("[DO] Alle Animationen auf Default setzen.")
    if anim_obj is not None:
        for i in range(len(anim_obj)):
            z = i + CONFIG["offset_obj"]
            #print(f"Objekt {z} -> auf Default setzen")
            do_default_anim(z)

#-----------------------------------------------------------------------------
#--- Async Funktion zum Senden einer Testnachricht über den Bus ---
#-----------------------------------------------------------------------------
async def do_send_msg_bus(msg=None):
    if msg is None:
        msg = "0"
    print(f"[TX] Sende Nachricht: '{msg}'")
    await bus.send_text(msg)

#------------------------------------------------------------------------------
#--- Hintergrund-Task simulieren ---
#------------------------------------------------------------------------------
async def background_heartbeat():
    print("Starte Background Task...")
    # UART-Empfangstask im Hintergrund starten
    uart_dev.start()
    blink_time = 300        # Blinkzeit in Millisekunden
    blink_state = False
    while True:
        #print("Hintergrund-Task: Status-LED blinken")
        hwdebug.write_output(blink_state)
        blink_state = not blink_state
        #uart_dev.send_line("Heartbeat -> " + str(counter))
        #----------------------------------------------------------------------
        #asyncio.create_task(do_send_msg_bus())
        #----------------------------------------------------------------------
        await asyncio.sleep_ms(blink_time)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Main-Loop als asynchroner Task
#------------------------------------------------------------------------------
async def main_loop():

    frame_time = CONFIG["frame_time"]
    offset = 0
    print("Starte WS2812-Berechnung...")
    while True:
        leds.clear()
        for s in CONFIG["stripe_list"]:
            #anim_obj[s].do_anim_update()
            anim_obj[s].do_anim_update()
            led_array = anim_obj[s].do_anim_update()
            for led_index, led_color in enumerate(led_array):
                pos = anim_obj[s].start + led_index - 1
                leds.pixel_hex(anim_obj[s].stripe, pos, led_color)
        await leds.show(copy=False)
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
    machine.reset()                 # type: ignore
    #___Go_Home___
    #--------------------------------------------------------------------------
#==============================================================================
