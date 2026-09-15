###############################################################################
### Programm    : Funktions-Codes in Array umwandeln (MicroPython RP2040)
###############################################################################
import json

class OBJECT:
    def __init__(self, name, array):
        self.name = name
        self.array = array

#==============================================================================
# Standarddaten, die geschrieben werden, falls die Datei fehlt
DEFAULT_DATA = [
    {"name": "H2Sat",       "array": [1, 2]},
    {"name": "EnMap",       "array": [3, 4]},
    {"name": "SARah",       "array": [11, 12, 15]},
    {"name": "SAR_Lupe",    "array": [3, 4]},
    {"name": "SATCOMBw",    "array": [1, 2, 5, 6, 7, 8]},
    {"name": "TerraSAR-X",  "array": [13, 14]},
    {"name": "SPOCK",       "array": None},
    {"name": "Galileo",     "array": [2, 3, 9, 10]},
    {"name": "Dummy_1",     "array": 45}
]
#==============================================================================

def load_or_create_json(filepath):
    data = None

    # 1. Versuchen die Datei zu öffnen
    try:
        with open(filepath, "r") as file:
            data = json.load(file)
            print(f"Datei '{filepath}' geladen.")
    except (OSError, ValueError):
        print(f"Datei '{filepath}' nicht gefunden oder leer. Erzeuge neu aus Standarddaten...")

    # 2. Wenn Datei fehlte oder defekt war: Neu anlegen
    if data is None:
        try:
            with open(filepath, "w") as file:
                json.dump(DEFAULT_DATA, file)
            print(f"Datei '{filepath}' wurde auf dem RP2040 gespeichert.")
        except OSError as e:
            print(f"Fehler beim Schreiben auf das Dateisystem: {e}")
        
        data = DEFAULT_DATA

    # 3. In Objekt-Liste konvertieren
    return [OBJECT(item["name"], item["array"]) for item in data]


def get_list_from_array(object_value):
    if isinstance(object_value, list):
        return object_value
    if isinstance(object_value, tuple):
        return list(object_value)
    if isinstance(object_value, int):
        return [object_value]
    return []

def get_array_from_obj(obj_list, index):
    return get_list_from_array(obj_list[index].array)

#------------------------------------------------------------------------------
# Main-Funktion für Modultests
#------------------------------------------------------------------------------
def main():
    print("Modultest: Funktions-Codes in Array umwandeln")
    filepath = "cfg_fcode_array.json"
    fcode_array = load_or_create_json(filepath)

    for obj in fcode_array:
        print(f"{obj.name}: Länge: {len(get_list_from_array(obj.array))} -> {get_list_from_array(obj.array)}")

    print("\nTest: Zugriff auf das erste Objekt im Array")
    print("Array -> ", fcode_array[0].name, ":", get_list_from_array(fcode_array[0].array))

    print("\nTest: get_array_from_obj für Index 6 (SPOCK):")
    for i in get_array_from_obj(fcode_array, 6):
        print(i)

    print("\nModultest abgeschlossen.")

#==============================================================================
if __name__ == "__main__":
    main()
#==============================================================================
