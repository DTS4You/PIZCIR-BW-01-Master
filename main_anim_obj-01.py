###############################################################################
### Name    : main_anim_obj-01
### Version : 0.99
###############################################################################
import time
import uasyncio as asyncio             # type: ignore # MicroPython RP2040
#import asyncio                        # Python 3.x

import libs.anim_obj as myanim

TIME_BACKGROUND_TASK    = 1
TIME_MAIN_LOOP          = 0.3

#------------------------------------------------------------------------------
# --- Hintergrund-Task simulieren ---
#------------------------------------------------------------------------------
async def background_heartbeat():
    """Simuliert eine parallele Hardware-Aufgabe (z.B. Status-LED blinken)"""
    print("Starte Hintergrund-Task: Status-LED blinken...")
    debug_counter = 0
    while True:
        print(f"Loop: {debug_counter:04d} Hintergrund-Task läuft...")
        debug_counter += 1
        await asyncio.sleep(TIME_BACKGROUND_TASK)    # Kurze Pause, um die CPU nicht zu blockieren

#------------------------------------------------------------------------------
# Main-Loop als asynchroner Task
#------------------------------------------------------------------------------
async def main_loop():

    while True:
        #if hwdebug.read_input():
        #    hwdebug.write_output(1)            # Nur bei MicroPython auf dem RP2040 aktivieren, um die Status-LED einzuschalten
        #else:
        #    #hwdebug.write_output(0)           # Nur bei MicroPython auf dem RP2040 aktivieren, um die Status-LED auszuschalten
        pass

        await asyncio.sleep(TIME_MAIN_LOOP)       # Kurze Pause, um die CPU nicht zu blockieren
#------------------------------------------------------------------------------

def anim_setup():

    debug_anim  = True
    debug_color = True
    debug_fill  = False

    print("--- Start Color Test ---")
    color_file = "cfg_colors.json"
    color_index = myanim.load_or_create_colors(color_file)
    print("Farbenindex erzeugt")
    if debug_color:
        print("\n--- Test COLOR_OBJ ---")
        for obj in color_index:
            print(f"Index: {obj.id:2d}, R: {obj.red:3d}, G: {obj.green:3d}, B: {obj.blue:3d}, Brightness: {obj.brightness}, RGB32: {hex(obj.rgb32)}")
        print("\n--- Test int32_to_4bytes ---")
        for obj in color_index:
            b0, b1, b2, b3 = myanim.int32_to_4bytes(obj.rgb32, little_endian=True)
            print(f"Index: {obj.id:2d}, RGB32: {hex(obj.rgb32)}, Bytes: [{b0:3d}, {b1:3d}, {b2:3d}, {b3:3d}]")
        print("Farbenindex 2 ist Farbe: ", color_index[2].rgb32)
    print("--- Ende Color Test ---")

    #--------------------------------------------------------------------------
    print("--- Start Animation Test ---")
    print("-> Config-Dateien setzen")
    patterns_file = "cfg_patterns.json"                         # Pattern-Datei, die eingelsen wird.
    objects_file = "cfg_anim_objects.json"                      # Objekt-Datei, die eingelesen wird.
    anim_pattern = myanim.load_or_create_patterns(patterns_file)
    print("--> Patterns erzeugt")
    anim_obj = myanim.load_or_create_objects(objects_file, anim_pattern, color_index)
    print("--> Objekte erzeugt")
    #--------------------------------------------------------------------------
    print("Anzahl der LED-Objekte: ", len(anim_obj))


    anim_number     = 0
    anim_steps      = 50
    anim_delay      = 0.3
    anim_test_start = 5
    anim_test_stop  = 40

    anim_obj[anim_number].toggle_dir = False

    #--------------------------------------------------------------------------
    if debug_anim:
        print("Pattern Länge:", anim_obj[anim_number].pattern.length)
        print("Array Länge Gesamt:", anim_obj[anim_number].arr_length)
        print("Board Port:", anim_obj[anim_number].stripe)
        print("Startposition:", anim_obj[anim_number].start)
        print("Objekt Länge:", anim_obj[anim_number].length)
        print("Toggle Enabled:", anim_obj[anim_number].toggle_en)

        for anim_step in range(anim_steps):
            if anim_step == anim_test_start:
                anim_obj[anim_number].set_anim_state(True)
            if anim_step == anim_test_stop:
                anim_obj[anim_number].set_anim_state(False)
            
            #print(f"State: {anim_obj[anim_number].run_state:1d} | Pos: {anim_obj[anim_number].position:02d} | Array: {anim_obj[anim_number].do_anim_update()}")
            print(f"Step: {anim_step:2d} | State: {anim_obj[anim_number].run_state:1d} | Pos: {myanim.format_with_sign(anim_obj[anim_number].position, width=3)} | Array: ", end="")
            print(", ".join([f"0x{x:06X}" for x in anim_obj[anim_number].do_anim_update()]))
            time.sleep(anim_delay)
    print("--- Ende Animation Test ---")

    #--------------------------------------------------------------------------
    if debug_fill:
        print("--- Start Fill Array Test ---")
        test_array = [0, 1, 2, 3, 2, 1, 0]
        myanim.fill_array_with_color(test_array, color_index)
        print("Testarray gefüllt:", test_array)
        print("Array als Hex32 Werte : ", end="")
        for i in range(len(test_array)):
            print(f"{test_array[i]:06X}", end=" ")
        print()
        print("--- Ende Fill Array Test ---")


#------------------------------------------------------------------------------
# --- Alle Tasks starten ---
#-----------------------------------------------------------------------------
async def main():
    anim_setup()
    print("Starte Main-Loop und Hintergrund-Task...")
    await asyncio.gather(
        main_loop(),
        background_heartbeat()
    )
#------------------------------------------------------------------------------
#--- Ab hier startet das Programm
#-----------------------------------------------------------------------------
def pre_main():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        #hwdebug.write_output(0)    # Nur bei MicroPython auf dem RP2040 aktivieren, um die Status-LED auszuschalten
        print("Programm wurde durch Benutzer abgebrochen.")
        #machine.reset()            # Nur bei MicroPython auf dem RP2040 aktivieren, um den Controller neu zu starten
#------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# --- Start bei Main-Aufruf
# ------------------------------------------------------------------------------

if __name__ == "__main__":

    pre_main()      # Start der Pre-Main-Funktion

# =============================================================================