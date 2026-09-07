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
    def __init__(self, stripe, start, length, pattern, default_color_index=0, direction=True):
        self.stripe         = stripe                        # Stripe Nummmer zählt von 1 bis N -> muss zum Board mit 0 starten
        self.start          = start                         # Startposition im Stripe Start bei 1
        self.led_length     = length
        self.color_def      = default_color_index
        self.pattern        = pattern
        self.position       = 0
        self.direction      = direction                     # True = rechts -> links / False = links -> rechts
        self.modulo         = 0
        self.modified       = False
        self.led_array      = self.pattern.led_pattern + [self.color_def] * self.led_length
        self.arr_length     = self.led_length + self.pattern.length
        self.act_array      = self.led_array

    def get_modulo(self):
        self.modulo = self.position % len(self.led_array)
        return self.modulo

    def get_led_array(self):
        return self.led_array

    def do_anim_step(self):
        arr_len = len(self.led_array)
        n = self.position % arr_len

        # Rotation ausführen
        if self.direction:
            # Rechts-Rotation
            self.act_array = self.led_array[-n:] + self.led_array[:-n]
        else:
            # Links-Rotation
            self.act_array = self.led_array[n:] + self.led_array[:n]

        # Position hochzählen/zurücksetzen
        if self.position >= self.arr_length:
            self.position = 0
        else:
            self.position += 1

        return self.act_array[self.pattern.length :]
#------------------------------------------------------------------------------
# Klasse für Farbobjekte
#------------------------------------------------------------------------------
class COLOR_OBJ:
    def __init__(self, index, red, green, blue, brightness=1):
        self.index      = index
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
                self.red
                | (self.green << 8)
                | (self.blue << 16)
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
    {"stripe":  1, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  2, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  3, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  4, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  5, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  6, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  7, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  8, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe":  9, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 10, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 11, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 11, "start": 20, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 12, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 12, "start": 20, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 13, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 14, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
    {"stripe": 15, "start":  1, "length": 10, "pattern_index": 0, "default_color_index": 1, "direction": True},
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
    {"index":  0, "r":   0, "g":   0, "b":   0, "brightness": 1},
    {"index":  1, "r":   0, "g":   0, "b":   3, "brightness": 1},
    {"index":  2, "r": 100, "g": 100, "b": 100, "brightness": 1},
    {"index":  3, "r":  50, "g":  50, "b":  50, "brightness": 1},
    {"index":  4, "r":   0, "g": 200, "b":   0, "brightness": 1},
    {"index":  5, "r":   0, "g":  10, "b":   0, "brightness": 1},
    {"index":  6, "r":  10, "g":  10, "b":  10, "brightness": 1},
    {"index":  7, "r":  10, "g":  10, "b":  10, "brightness": 1},
    {"index":  8, "r":   0, "g":  20, "b":   0, "brightness": 1},
    {"index":  9, "r":   0, "g":  50, "b":   0, "brightness": 1},
    {"index": 10, "r":   0, "g": 150, "b":   0, "brightness": 1},
    {"index": 11, "r":   0, "g":   0, "b":  20, "brightness": 1},
    {"index": 12, "r":   0, "g":   0, "b":  50, "brightness": 1},
    {"index": 13, "r":   0, "g":   0, "b": 150, "brightness": 1},
    {"index": 14, "r":  20, "g":   0, "b":   0, "brightness": 1},
    {"index": 15, "r":  70, "g":   0, "b":   0, "brightness": 1},
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
            f'    {{ "stripe": {item["stripe"]:2d}, "start": {item["start"]:2d}, "length": {item["length"]:2d}, "pattern_index": {item["pattern_index"]}, "default_color_index": {item["default_color_index"]}, "direction": {str(item["direction"]).lower()} }}{comma}'
        )
    lines.append("]")

    with open(filepath, "w") as file:
        file.write("\n".join(lines))

def load_or_create_objects(filepath, anim_patterns):
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
        pat_idx = item["pattern_index"]
        obj = ANIM_OBJ(
            stripe=item["stripe"],
            start=item["start"],
            length=item["length"],
            pattern=anim_patterns[pat_idx],
            default_color_index=item["default_color_index"],
            direction=item["direction"]
        )
        anim_objects.append(obj)

    return anim_objects

def save_colors_to_json(filepath, color_index):
    """Speichert die Liste formatiert in einer JSON-Datei."""
    lines = ["["]
    for i, obj in enumerate(color_index):
        comma = "," if i < len(color_index) - 1 else ""
        line = (
            f'    {{ "index": {obj.index:2d}, '
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
                item["index"],
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
            index=item["index"],
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

def fill_array_with_color(array, color_index):
    """Füllt ein Array mit den RGB32-Werten aus dem Farbindex."""
    for i in range(len(array)):
        array[i] = color_index[array[i]].rgb32
    return array
#------------------------------------------------------------------------------
# Main-Funktion für Modultests
#------------------------------------------------------------------------------
def main():

    debug_anim  = False
    debug_color = False
    debug_fill  = False

    print("--- Start Color Test ---")
    color_file = "cfg_colors.json"
    color_index = load_or_create_colors(color_file)
    print("Farbenindex erzeugt")
    if debug_color:
        print("\n--- Test COLOR_OBJ ---")
        for obj in color_index:
            print(f"Index: {obj.index:2d}, R: {obj.red:3d}, G: {obj.green:3d}, B: {obj.blue:3d}, Brightness: {obj.brightness}, RGB32: {hex(obj.rgb32)}")
        print("\n--- Test int32_to_4bytes ---")
        for obj in color_index:
            b0, b1, b2, b3 = int32_to_4bytes(obj.rgb32, little_endian=True)
            print(f"Index: {obj.index:2d}, RGB32: {hex(obj.rgb32)}, Bytes: [{b0:3d}, {b1:3d}, {b2:3d}, {b3:3d}]")
        print("Farbenindex 2 ist Farbe: ", color_index[2].rgb32)
    print("--- Ende Color Test ---")

    print("--- Start Animation Test ---")
    patterns_file = "cfg_patterns.json"
    objects_file = "cfg_anim_objects.json"
    anim_pattern = load_or_create_patterns(patterns_file)
    anim_obj = load_or_create_objects(objects_file, anim_pattern)
    print("Objekte erzeugt")

    print("Anzahl der LED-Objekte: ", len(anim_obj))

    if debug_anim:
        print("Pattern 0 Länge:", anim_obj[0].pattern.length)
        print("Array Länge Gesamt:", anim_obj[0].arr_length)

        for _ in range(20):
            print(
                f"Objekt Pos: {anim_obj[0].position:02d} | Array: {anim_obj[0].do_anim_step()}"
            )
            time.sleep(0.2)
    print("--- Ende Animation Test ---")

    if debug_fill:
        print("--- Start Fill Array Test ---")
        test_array = [0, 1, 2, 3, 2, 1, 0]
        fill_array_with_color(test_array, color_index)
        print("Testarray gefüllt:", test_array)
        print("--- Ende Fill Array Test ---")


#==============================================================================
if __name__ == "__main__":
    main()
#==============================================================================