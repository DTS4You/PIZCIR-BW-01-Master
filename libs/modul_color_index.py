###############################################################################
### Module: module_color_index.py
###############################################################################
import time

def color_setup():

    global color_index
    color_index = []
    #-------------
    color_index.append(COLOR_OBJ( 0,  0,  0,  0))           # Color_Off
    color_index.append(COLOR_OBJ( 1,  0,  0,  3))           # Color_Def
    color_index.append(COLOR_OBJ( 2,100,100,100))           # Color_On
    color_index.append(COLOR_OBJ( 3, 50, 50, 50))           # Color_Dot
    color_index.append(COLOR_OBJ( 4,  0,200,  0))           # Color_Blink_On
    color_index.append(COLOR_OBJ( 5,  0, 10,  0))           # Color_Blink_Off
    color_index.append(COLOR_OBJ( 6, 10, 10, 10))           # Reserve_1
    color_index.append(COLOR_OBJ( 7, 10, 10, 10))           # Reserve_2
    color_index.append(COLOR_OBJ( 8,  0, 20,  0))           # Color_Anim_1  Grün 20%
    color_index.append(COLOR_OBJ( 9,  0, 50,  0))           # Color_Anim_2  Grün 50%
    color_index.append(COLOR_OBJ(10,  0,150,  0))           # Color_Anim_3  Grün 100%
    color_index.append(COLOR_OBJ(11,  0,  0, 20))           # Color_Anim_4  Blau 20%
    color_index.append(COLOR_OBJ(12,  0,  0, 50))           # Color_Anim_5  Blau 50%
    color_index.append(COLOR_OBJ(13,  0,  0,150))           # Color_Anim_6  Blau 100%
    color_index.append(COLOR_OBJ(14, 20,  0,  0))           # Color_Anim_7  Rot 20%
    color_index.append(COLOR_OBJ(15, 70,  0,  0))           # Color_Anim_8  Rot 70%


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
            self.rgb32 = self.red | (self.green << 8) | (self.blue << 16) | (self.dummy << 24)
        else:
            # MSB zuerst
            self.rgb32 = (self.dummy << 24) | (self.blue << 16) | (self.green << 8) | self.red

        return self.rgb32

 


def int32_to_4bytes(val, little_endian=True):
    
    b0 = val & 0xFF
    b1 = (val >> 8) & 0xFF
    b2 = (val >> 16) & 0xFF
    b3 = (val >> 24) & 0xFF

    if little_endian:
        return b0, b1, b2, b3  # LSB -> MSB
    else:
        return b3, b2, b1, b0  # MSB -> LSB



def main():

    print("--- Start ---")

    color_setup()
    print("\n--- Test COLOR_OBJ ---")
    for i in range(len(color_index)):
        print(f"Index: {color_index[i].index}, R: {color_index[i].red}, G: {color_index[i].green}, B: {color_index[i].blue}, Brightness: {color_index[i].brightness}, RGB32: {hex(color_index[i].rgb32)}")
    
    print("\n--- Test int32_to_4bytes ---")
    for i in range(len(color_index)):
        b0, b1, b2, b3 = int32_to_4bytes(color_index[i].rgb32, little_endian=True)
        print(f"Index: {color_index[i].index}, RGB32: {hex(color_index[i].rgb32)}, Bytes: [{b0}, {b1}, {b2}, {b3}]")
    print("--- Ende ---")


#------------------------------------------------------------------------------
#--- Main
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

