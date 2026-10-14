###############################################################################
### Modul   : Animationsobjekte
### Version : 1.00
### Datum   : 2026-10-14
################################################################################

import json
import os
import time

#------------------------------------------------------------------------------
# Klasse für Animationsmuster
#------------------------------------------------------------------------------
class ANIM_PATTERN:
    def __init__(self, led_pattern):
        self.led_pattern = led_pattern
        self.length = len(self.led_pattern)
#-----------------------------------------------------------------------------
# Klasse für Animationsobjekte
#-----------------------------------------------------------------------------
class ANIM_OBJ:
    def __init__(self, id, stripe, start, length, pregap, pattern, color_index, color_def=1, color_off=0, direction=True, toggle_en=False):
        self.id             = id
        self.stripe         = stripe                        # Stripe Nummmer zählt von 1 bis N -> muss zum Board mit 0 starten
        self.start          = start                         # Startposition im Stripe Start bei 1
        self.length         = length                        # Länge des Objektes    
        self.color_def      = color_def                     # Color Index für "Vorgabe"
        self.color_off      = color_off                     # Color Index für "Aus"
        self.pattern        = pattern                       # Animations Muster als Array aus Index-Farbwerten
        self.color_index    = color_index                   # Color Index Objekt
        self.position       = pregap                        # 0 oder Offset als Positionsvorgabe -> negative Werte verzögern den Start                              
        self.direction      = direction                     # True = rechts -> links / False = links -> rechts
        self.toggle_en      = toggle_en                     # Toggle der Richtung nach jedem Durchlauf
        self.run_state      = False                         # True = Animation läuft / False = Animation gestoppt
        self.default_state  = False                         # True = Animation läuft / False = Animation gestoppt
        self.modulo         = 0
        self.modified       = False
        self.arr_length     = self.length + self.pattern.length
        self.led_array      = self.pattern.led_pattern + [self.color_def] * self.length
        self.color_fill()
        self.act_array      = self.led_array
        self.led_output     = [self.color_index[self.color_off].rgb32] * self.length

    def color_fill(self):
        for i, wert in enumerate(self.led_array):
            #print(self.id, i , wert, self.color_index[wert].rgb32)
            self.led_array[i] = self.color_index[wert].rgb32

    def get_modulo(self):
        self.modulo = self.position % len(self.led_array)
        return self.modulo

    def get_led_array(self):
        return self.led_array

    def get_led_output(self):
        return self.led_output

    def set_anim_state(self, state=False):
        if state:
            self.run_state      = True
            self.default_state  = False
        else:
            self.run_state = False
            self.position  = 0

    def set_default_state(self, state=False):
        if state:
            self.default_state = True
            self.run_state     = False
            self.position      = 0
        else:
            self.default_state = False

    def do_anim_update(self):

        if self.run_state:
            arr_len = len(self.led_array)
            n = self.position % arr_len

            # Rotation ausführen
            if self.direction:
                # Rechts-Rotation
                self.act_array = self.led_array[-n:] + self.led_array[:-n]
            else:
                # Links-Rotation
                self.act_array = self.led_array[n:] + self.led_array[:n]

            if self.position < 0:
                # Wenn Position kleiner 0 dann nur Array-Default zurückgeben und Position hochzählen
                self.position += 1
                self.led_output = [self.color_index[self.color_def].rgb32] * self.length       # Array mit RGB32 Wert aus Color-Index[Default] zurückgeben
                return self.led_output
            else:
                # Position hochzählen/zurücksetzen bei direction / toggle_en -> Richtung immer wieder umdrehen am Ende
                if self.position >= self.arr_length:
                    self.position = 0
                    if self.toggle_en:
                        self.direction = not self.direction
                else:
                    self.position += 1

            self.led_output = self.act_array[self.pattern.length :]
            return self.led_output
        else:
            if self.default_state:
                self.led_output = [self.color_index[self.color_def].rgb32] * self.length       # Array mit RGB32 Wert aus Color-Index[Default] zurückgeben
                return self.led_output
            else:
                self.led_output = [self.color_index[self.color_off].rgb32] * self.length           # Array mit RGB32 Wert aus Color-Index[Off] zurückgeben
                return self.led_output
#------------------------------------------------------------------------------
# Klasse für Farbobjekte
#------------------------------------------------------------------------------
class COLOR_OBJ:
    def __init__(self, id, red, green, blue, brightness=1):
        self.id         = id
        self.red        = red
        self.green      = green
        self.blue       = blue
        self.dummy      = 0
        self.brightness = brightness
        self.rgb32      = 0
        self.bytes_to_int32()

    def bytes_to_int32(self, little_endian=True):
        if little_endian:
            # LSB zuerst
            self.rgb32 = (
                self.blue
                | (self.red << 8)
                | (self.green << 16)
                | (self.dummy << 24)
            )
        else:
            # MSB zuerst
            self.rgb32 = (
                (self.dummy << 24)
                | (self.blue << 16)
                | (self.green << 8)
                | self.red
            )

        return self.rgb32
#-----------------------------------------------------------------------------
# Standarddaten für die Animationsobjekte
#-----------------------------------------------------------------------------
DEFAULT_OBJECTS = [
    {"id":  1, "stripe":  3, "start":  1, "length": 10, "pregap": -15, "pattern": 1, "color_def": 1, "color_off": 0, "direction": True, "toggle_en": False},
    {"id":  2, "stripe":  4, "start":  1, "length": 10, "pregap":   0, "pattern": 0, "color_def": 1, "color_off": 0, "direction": True, "toggle_en": False},
    {"id":  3, "stripe":  5, "start":  1, "length": 10, "pregap":   0, "pattern": 0, "color_def": 1, "color_off": 0, "direction": True, "toggle_en": False},
    {"id":  4, "stripe":  6, "start":  1, "length": 10, "pregap":   0, "pattern": 0, "color_def": 1, "color_off": 0, "direction": True, "toggle_en": False},
    {"id":  5, "stripe":  7, "start":  1, "length": 10, "pregap":   0, "pattern": 0, "color_def": 1, "color_off": 0, "direction": True, "toggle_en": False},
    {"id":  6, "stripe":  8, "start":  1, "length": 10, "pregap":   0, "pattern": 0, "color_def": 1, "color_off": 0, "direction": True, "toggle_en": False},
    {"id":  7, "stripe": 10, "start":  1, "length": 10, "pregap":   0, "pattern": 0, "color_def": 1, "color_off": 0, "direction": True, "toggle_en": False},
    {"id":  8, "stripe": 11, "start":  1, "length": 10, "pregap":   0, "pattern": 0, "color_def": 1, "color_off": 0, "direction": True, "toggle_en": False},
    {"id":  9, "stripe": 12, "start":  1, "length": 10, "pregap":   0, "pattern": 0, "color_def": 1, "color_off": 0, "direction": True, "toggle_en": False},
    {"id": 10, "stripe": 13, "start":  1, "length": 10, "pregap":   0, "pattern": 0, "color_def": 1, "color_off": 0, "direction": True, "toggle_en": False},
    {"id": 11, "stripe": 13, "start": 20, "length": 10, "pregap":   0, "pattern": 0, "color_def": 1, "color_off": 0, "direction": True, "toggle_en": False},
    {"id": 12, "stripe": 14, "start":  1, "length": 10, "pregap":   0, "pattern": 0, "color_def": 1, "color_off": 0, "direction": True, "toggle_en": False},
    {"id": 13, "stripe": 14, "start": 20, "length": 10, "pregap":   0, "pattern": 0, "color_def": 1, "color_off": 0, "direction": True, "toggle_en": False},
    {"id": 14, "stripe": 15, "start":  1, "length": 10, "pregap":   0, "pattern": 0, "color_def": 1, "color_off": 0, "direction": True, "toggle_en": False},
    {"id": 15, "stripe": 16, "start": 20, "length": 10, "pregap":   0, "pattern": 0, "color_def": 1, "color_off": 0, "direction": True, "toggle_en": False}
]
#-----------------------------------------------------------------------------
# Standarddaten für die Patterns
#-----------------------------------------------------------------------------
DEFAULT_PATTERNS = [
    [8, 9, 10, 9, 8],               # Index 0 (Grün)
    [14, 15, 14],                   # Index 1 (Rot)
    [11, 12, 13, 12, 11],           # Index 2 (Blau)
]
#-----------------------------------------------------------------------------
# Standarddaten für die Farben
#-----------------------------------------------------------------------------
DEFAULT_COLOR_DATA = [
    {"id":  0, "r":   0, "g":   0, "b":   0, "brightness": 1},
    {"id":  1, "r":   0, "g":   0, "b":   3, "brightness": 1},
    {"id":  2, "r": 100, "g": 100, "b": 100, "brightness": 1},
    {"id":  3, "r":  50, "g":  50, "b":  50, "brightness": 1},
    {"id":  4, "r":   0, "g": 200, "b":   0, "brightness": 1},
    {"id":  5, "r":   0, "g":  10, "b":   0, "brightness": 1},
    {"id":  6, "r":  10, "g":  10, "b":  10, "brightness": 1},
    {"id":  7, "r":  10, "g":  10, "b":  10, "brightness": 1},
    {"id":  8, "r":   0, "g":  20, "b":   0, "brightness": 1},
    {"id":  9, "r":   0, "g":  50, "b":   0, "brightness": 1},
    {"id": 10, "r":   0, "g": 150, "b":   0, "brightness": 1},
    {"id": 11, "r":   0, "g":   0, "b":  20, "brightness": 1},
    {"id": 12, "r":   0, "g":   0, "b":  50, "brightness": 1},
    {"id": 13, "r":   0, "g":   0, "b": 150, "brightness": 1},
    {"id": 14, "r":  20, "g":   0, "b":   0, "brightness": 1},
    {"id": 15, "r":  70, "g":   0, "b":   0, "brightness": 1},
]

def load_or_create_patterns(filepath):
    """Lädt Patterns aus JSON oder erstellt Standarddatei."""
    is_empty_or_missing = True
    try:
        if os.stat(filepath)[6] > 0:
            is_empty_or_missing = False
    except OSError:
        is_empty_or_missing = True

    if is_empty_or_missing:
        print(f"Datei '{filepath}' fehlt/leer. Erstelle mit Standarddaten...")
        with open(filepath, "w") as file:
            json.dump(DEFAULT_PATTERNS, file)

    try:
        with open(filepath, "r") as file:
            data = json.load(file)
    except (ValueError, OSError):
        print(f"Warnung: '{filepath}' ungültig. Verwende Standarddaten.")
        data = DEFAULT_PATTERNS

    return [ANIM_PATTERN(pat) for pat in data]

def save_objects_to_json(filepath, objects_data):
    """Speichert Objekte in einzeiliger Form ab."""
    lines = ["["]
    count = len(objects_data)
    for i, item in enumerate(objects_data):
        comma = "," if i < count - 1 else ""
        lines.append(
            f'    {{ "id": {item["id"]:2d},"stripe": {item["stripe"]:2d}, "start": {item["start"]:2d}, "length": {item["length"]:2d}, "pregap": {item["pregap"]:4d}, "pattern": {item["pattern"]}, "color_def": {item["color_def"]}, "color_off": {item["color_off"]}, "direction": {str(item["direction"]).lower()}, "toggle_en": {str(item["toggle_en"]).lower()} }}{comma}'
        )
    lines.append("]")

    with open(filepath, "w") as file:
        file.write("\n".join(lines))

def load_or_create_objects(filepath, anim_patterns, color_index):
    """Lädt Objekt-Konfigurationen aus JSON oder erstellt Standarddatei."""
    is_empty_or_missing = True
    try:
        if os.stat(filepath)[6] > 0:
            is_empty_or_missing = False
    except OSError:
        is_empty_or_missing = True

    if is_empty_or_missing:
        print(f"Datei '{filepath}' fehlt/leer. Erstelle mit Standarddaten...")
        save_objects_to_json(filepath, DEFAULT_OBJECTS)

    try:
        with open(filepath, "r") as file:
            data = json.load(file)
    except (ValueError, OSError):
        print(f"Warnung: '{filepath}' ungültig. Verwende Standarddaten.")
        data = DEFAULT_OBJECTS

    anim_objects = []
    for item in data:
        pat_idx = item["pattern"]
        obj = ANIM_OBJ(
            id=item["id"],
            stripe=item["stripe"],
            start=item["start"],
            length=item["length"],
            pregap=item["pregap"],
            pattern=anim_patterns[pat_idx],
            color_index=color_index,
            color_def=item["color_def"],
            color_off=item["color_off"],
            direction=item["direction"],
            toggle_en=item["toggle_en"]
        )
        anim_objects.append(obj)

    return anim_objects

def save_colors_to_json(filepath, color_index):
    """Speichert die Liste formatiert in einer JSON-Datei."""
    lines = ["["]
    for i, obj in enumerate(color_index):
        comma = "," if i < len(color_index) - 1 else ""
        line = (
            f'    {{ "id": {obj.id:2d}, '
            f'"r": {obj.red:3d}, '
            f'"g": {obj.green:3d}, '
            f'"b": {obj.blue:3d}, '
            f'"brightness": {obj.brightness} }}{comma}'
        )
        lines.append(line)
    lines.append("]")

    formatted_json = "\n".join(lines)

    with open(filepath, "w") as file:
        file.write(formatted_json)


def load_or_create_colors(filepath):
    # 1. Prüfen, ob die Datei existiert und nicht leer (0 Bytes) ist
    is_empty_or_missing = True
    try:
        stat_info = os.stat(filepath)
        if stat_info[6] > 0:  # stat_info[6] entspricht der Dateigröße in Bytes
            is_empty_or_missing = False
    except OSError:
        is_empty_or_missing = True

    # Falls Datei fehlt oder leer ist: Standarddaten schreiben
    if is_empty_or_missing:
        print(
            f"Datei '{filepath}' fehlt oder ist leer. Erstelle mit Standarddaten..."
        )
        # Erstelle temporäre Liste aus Obj für formatierte Speicherung
        default_objs = [
            COLOR_OBJ(
                item["id"],
                item["r"],
                item["g"],
                item["b"],
                item.get("brightness", 1),
            )
            for item in DEFAULT_COLOR_DATA
        ]
        save_colors_to_json(filepath, default_objs)

    # 2. JSON einlesen (inklusive Fehlerabfang bei ungültigem JSON)
    try:
        with open(filepath, "r") as file:
            data = json.load(file)
    except (ValueError, OSError):
        print(
            f"Warnung: '{filepath}' ist ungültig oder beschädigt. Verwende Standarddaten."
        )
        data = DEFAULT_COLOR_DATA

    # 3. Liste mit COLOR_OBJ Objekten erzeugen
    color_index = []
    for item in data:
        obj = COLOR_OBJ(
            id=item["id"],
            red=item["r"],
            green=item["g"],
            blue=item["b"],
            brightness=item.get("brightness", 1),
        )
        color_index.append(obj)

    return color_index

def int32_to_4bytes(val, little_endian=True):
    b0 = val & 0xFF
    b1 = (val >> 8) & 0xFF
    b2 = (val >> 16) & 0xFF
    b3 = (val >> 24) & 0xFF

    if little_endian:
        return b0, b1, b2, b3  # LSB -> MSB
    else:
        return b3, b2, b1, b0  # MSB -> LSB

def int32_to_rgb(val, little_endian=True):
    b0 = val & 0xFF
    b1 = (val >> 8) & 0xFF
    b2 = (val >> 16) & 0xFF

    if little_endian:
        return b0, b1, b2  # LSB -> MSB
    else:
        return b2, b1, b0  # MSB -> LSB

def fill_array_with_color(array, color_index):
    """Füllt ein Array mit den RGB32-Werten aus dem Farbindex."""
    for i in range(len(array)):
        array[i] = color_index[array[i]].rgb32
    return array

#-----------------------------------------------------------------------------
def format_with_sign(wert, width=4):
    # Vorzeichen und Betrag trennen
    if wert >= 0:
        # Bei positiv: '+' erzwingen und mit Nullen auffüllen (Breite minus 1 für das Vorzeichen)
        return f"+{wert:0{width-1}d}"
    else:
        # Bei negativ: '-' setzen und den Betrag mit Nullen auffüllen
        return f"-{abs(wert):0{width-1}d}"

#------------------------------------------------------------------------------
# Main-Funktion für Modultests
#------------------------------------------------------------------------------
def main():

    debug_anim  = False
    debug_color = True
    debug_fill  = True
    debug_obj   = True

    print("--- Start Color Test ---")
    color_file = "cfg_colors.json"
    color_index = load_or_create_colors(color_file)
    print("Farbenindex erzeugt")
    if debug_color:
        print("\n--- Test COLOR_OBJ ---")
        for obj in color_index:
            print(f"Index: {obj.id:2d}, R: {obj.red:3d}, G: {obj.green:3d}, B: {obj.blue:3d}, Brightness: {obj.brightness}, RGB32: {hex(obj.rgb32)}")
        print("\n--- Test int32_to_4bytes ---")
        for obj in color_index:
            b0, b1, b2, b3 = int32_to_4bytes(obj.rgb32, little_endian=True)
            print(f"Index: {obj.id:2d}, RGB32: {hex(obj.rgb32)}, Bytes: [{b0:3d}, {b1:3d}, {b2:3d}, {b3:3d}]")
        print("Farbenindex 2 ist Farbe: ", color_index[2].rgb32)
    print("--- Ende Color Test ---")

    #--------------------------------------------------------------------------
    print("--- Start Animation Test ---")
    print("-> Config-Dateien setzen")
    patterns_file = "cfg_patterns.json"                         # Pattern-Datei, die eingelsen wird.
    objects_file = "cfg_anim_objects.json"                      # Objekt-Datei, die eingelesen wird.
    anim_pattern = load_or_create_patterns(patterns_file)
    print("--> Patterns erzeugt")
    anim_obj = load_or_create_objects(objects_file, anim_pattern, color_index)
    print("--> Objekte erzeugt")
    #--------------------------------------------------------------------------
    print("Anzahl der LED-Objekte: ", len(anim_obj))

    anim_number     = 0
    anim_steps      = 50
    anim_delay      = 0.4
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
            print(f"Step: {anim_step:2d} | State: {anim_obj[anim_number].run_state:1d} | Pos: {format_with_sign(anim_obj[anim_number].position, width=3)} | Array: ", end="")
            print(", ".join([f"0x{x:06X}" for x in anim_obj[anim_number].do_anim_update()]))
            time.sleep(anim_delay)
    print("--- Ende Animation Test ---")

#--------------------------------------------------------------------------
    if debug_fill:
        print("--- Start Fill Array Test ---")
        test_array = [0, 1, 2, 3, 2, 1, 0]
        fill_array_with_color(test_array, color_index)
        print("Testarray gefüllt:", test_array)
        print("Array als Hex32 Werte : ", end="")
        for i in range(len(test_array)):
            print(f"{test_array[i]:06X}", end=" ")
        print()
        print("--- Ende Fill Array Test ---")

#--------------------------------------------------------------------------
    if debug_obj:
        print("--- Start Object Test ---")
        object_array =[0, 1, 2, 3, 4, 5, 6, 7]
        for i in object_array:
            print(f"Obj: {i:02d} | Stripe: {anim_obj[i].stripe:02d} | Led_Output: {anim_obj[i].get_led_output()}")

        anim_obj[0].set_anim_state(True)

        anim_number = 0

        for anim_step in range(anim_steps):
            print(f"Obj: {anim_number:02d} | Stripe: {anim_obj[anim_number].stripe:02d} | Pos: {format_with_sign(anim_obj[anim_number].position, width=3)} | Array: ", end="")
            print(", ".join([f"0x{x:06X}" for x in anim_obj[anim_number].get_led_output()]))
            anim_obj[anim_number].do_anim_update()
        print("--- Ende Object Test ---")

#==============================================================================
if __name__ == "__main__":
    main()
#==============================================================================