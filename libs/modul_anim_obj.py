###############################################################################
### Module  : module_anim_obj.py
### Version : 0.99
### Datum   : 24.08.2026
###############################################################################
import time

def pattern_setup():

    global anim_pattern
    anim_pattern = []
    anim_pattern.append(ANIM_PATTERN([8,9,10,9,8]))     # Anim Pattern Grün
    anim_pattern.append(ANIM_PATTERN([14,15,14]))       # Anim Pattern Rot
    anim_pattern.append(ANIM_PATTERN([11,12,13,12,11])) # Anim Pattern Blau


def anim_setup():

    global anim_obj
    anim_obj = []
    anim_obj.append(ANIM_OBJ(1, 1,10,anim_pattern[0],1,True))          #  1. Anim / 1. Stripe
    anim_obj.append(ANIM_OBJ(2, 1,10,anim_pattern[0],1,True))          #  2. Anim / 2. Stripe
    anim_obj.append(ANIM_OBJ(3, 1,10,anim_pattern[0],1,True))          #  3. Anim / 3. Stripe
    anim_obj.append(ANIM_OBJ(4, 1,10,anim_pattern[0],1,True))          #  4. Anim / 4. Stripe
    anim_obj.append(ANIM_OBJ(5, 1,10,anim_pattern[0],1,True))          #  5. Anim / 5. Stripe
    anim_obj.append(ANIM_OBJ(6, 1,10,anim_pattern[0],1,True))          #  6. Anim / 6. Stripe
    anim_obj.append(ANIM_OBJ(7, 1,10,anim_pattern[0],1,True))          #  7. Anim / 7. Stripe
    anim_obj.append(ANIM_OBJ(8, 1,10,anim_pattern[0],1,True))          #  8. Anim / 8. Stripe
    anim_obj.append(ANIM_OBJ(9, 1,10,anim_pattern[0],1,True))          #  9. Anim / 9. Stripe
    anim_obj.append(ANIM_OBJ(10, 1,10,anim_pattern[0],1,True))         # 10. Anim / 10. Stripe
    anim_obj.append(ANIM_OBJ(11, 1,10,anim_pattern[0],1,True))         # 11. Anim / 11a. Stripe
    anim_obj.append(ANIM_OBJ(11,20,10,anim_pattern[0],1,True))         # 12. Anim / 11b. Stripe
    anim_obj.append(ANIM_OBJ(12, 1,10,anim_pattern[0],1,True))         # 13. Anim / 12a. Stripe
    anim_obj.append(ANIM_OBJ(12,20,10,anim_pattern[0],1,True))         # 14. Anim / 12b. Stripe
    anim_obj.append(ANIM_OBJ(13, 1,10,anim_pattern[0],1,True))         # 15. Anim / 13. Stripe
    anim_obj.append(ANIM_OBJ(14, 1,10,anim_pattern[0],1,True))         # 16. Anim / 14. Stripe
    anim_obj.append(ANIM_OBJ(15, 1,10,anim_pattern[0],1,True))         # 17. Anim / 15. Stripe

class ANIM_OBJ:
    def __init__(self, stripe, start, lenght, pattern, default_color_index=0, direction=True):
        self.stripe     = stripe
        self.start      = start
        self.led_lenght = lenght
        self.color_def  = default_color_index
        self.pattern    = pattern
        self.position   = 0
        self.direction  = direction         # True = rechts -> links / False = links -> rechts
        self.modulo     = 0
        self.modifyed   = False
        self.led_array  = self.pattern.led_pattern + [self.color_def] * self.led_lenght
        self.arr_lenght = self.led_lenght + self.pattern.lenght
        self.act_array  = self.led_array

    def get_modulo(self):
        self.modulo = self.position % len(self.led_array)

    def get_led_array(self):
        return self.led_array

    def rotate_right(self, n):
        n = n % len(self.led_array)
        return self.led_array[-n:] + self.led_array[:-n]

    def rotate_left(self, n):
        n = n % len(self.led_array)
        return self.led_array[n:] + self.led_array[:n]

    def do_anim_step(self):
        if self.direction:
            self.act_array = self.rotate_right(self.position)
        else:
            self.act_array = self.rotate_left(self.position)

        if self.position >= self.arr_lenght:
            self.position = 0
        else:
            self.position = self.position + 1
        
        return self.act_array[self.pattern.lenght:]                 # Auf echte Anzahl LEDs kürzen -> Pattern vorne entfernen

class ANIM_PATTERN:
    def __init__(self, led_pattern):
        self.led_pattern    = led_pattern
        self.lenght         = len(self.led_pattern)


def main():

    print("--- Start ---")

    pattern_setup()
    anim_setup()

    print("Objekte erzeugen")
    
    anim_obj[1].modifyed = True

    print("Anzahl der Anim_Objekte:", len(anim_obj))
    print(anim_obj[0].pattern.lenght)
    print(anim_obj[1].pattern.lenght)

    #for i in range(len(anim_obj)):
    #    print("Objekt:", i ,"Array:", anim_obj[i].led_array)

    print(anim_obj[0].arr_lenght)

    for i in range(20):
        
        print(f"Objekt: {anim_obj[0].position:02d} Array: {anim_obj[0].do_anim_step()}")
        #print(f"Objekt: {anim_obj[1].position:02d} Array: {anim_obj[1].do_anim_step()}")

        time.sleep(0.2)
    

    print("--- Ende ---")


#------------------------------------------------------------------------------
#--- Main
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
