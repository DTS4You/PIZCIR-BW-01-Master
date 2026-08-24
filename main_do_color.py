import time
import libs.modul_color_index as mycolor

def main():

    print("--- Start ---")

    mycolor.color_setup()

    print("Objekte erzeugen")

    print("Anzahl der Color_Objekte:", len(mycolor.color_index))
    for i in range(len(mycolor.color_index)):
        print(f"Index: {mycolor.color_index[i].index}, R: {mycolor.color_index[i].red}, G: {mycolor.color_index[i].green}, B: {mycolor.color_index[i].blue}, Brightness: {mycolor.color_index[i].brightness}, RGB32: {hex(mycolor.color_index[i].rgb32)}")
    
    print("\n--- Test int32_to_4bytes ---")
    for i in range(len(mycolor.color_index)):
        b0, b1, b2, b3 = mycolor.int32_to_4bytes(mycolor.color_index[i].rgb32, little_endian=True)
        print(f"Index: {mycolor.color_index[i].index}, RGB32: {hex(mycolor.color_index[i].rgb32)}, Bytes: [{b0}, {b1}, {b2}, {b3}]")
    print("--- Ende ---")
    



#------------------------------------------------------------------------------
#--- Main
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
