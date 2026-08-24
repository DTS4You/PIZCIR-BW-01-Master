from time import time
from libs.modul_anim_obj import myanim

def main():

    print("--- Start ---")

    myanim.pattern_setup()
    myanim.anim_setup()

    print("Objekte erzeugen")
    
    myanim.anim_obj[1].modifyed = True

    print("Anzahl der Anim_Objekte:", len(myanim.anim_obj))
    print(myanim.anim_obj[0].pattern.lenght)
    print(myanim.anim_obj[1].pattern.lenght)

    #for i in range(len(myanim.anim_obj)):
    #    print("Objekt:", i ,"Array:", myanim.anim_obj[i].led_array)

    print(myanim.anim_obj[0].arr_lenght)

    for i in range(20):
        
        print(f"Objekt: {myanim.anim_obj[0].position:02d} Array: {myanim.anim_obj[0].do_anim_step()}")
        #print(f"Objekt: {myanim.anim_obj[1].position:02d} Array: {myanim.anim_obj[1].do_anim_step()}")

        time.sleep(0.2)
    

    print("--- Ende ---")


#------------------------------------------------------------------------------
#--- Main
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
