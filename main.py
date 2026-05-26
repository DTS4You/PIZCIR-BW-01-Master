######################################################
### Main-Program                                   ###
### Projekt: Heinrich-Hertz-SAT                    ###
### Version: 1.05          11.05.2026              ###
######################################################
from machine import Pin, Timer      # type: ignore
from libs.module_init import Global_Module as MyModule
import time                         # type: ignore

#------------------------------------------------------------------------------
# 01 -> Next OBP              -> 1/12                         -> 11
# 02 -> Fraunhofer OBP        -> 1/11                         -> 10
# 03 -> GeReLEO Smart         -> 1/07                         -> 06
#-----
# 04 -> Flex INET             -> 1/04 , 1/05                  -> 03 , 04
#------
# 05 -> Flex OMUX             -> 1/03 , 1/06                  -> 02 , 05
#-----
# 06 -> 300W FPM              -> 1/01 , 1/02                  -> 00 , 01
#------
# 07 -> 250W FPM              -> 1/08 , 1/09                  -> 07 , 08
# 08 -> PLIU                  -> 1/10                         -> 09
# 09 -> H2KAR Reflektor       -> 2/05 , 3/05                  -> 16 , 24
# 10 -> HEMPT                 -> 2/08 , 3/08                  -> 19 , 27
# 11 -> Reaktionsräder        -> 2/06 , 3/06                  -> 17 , 25
# 12 -> Batterie              -> 4/02 , 4/03                  -> 29 , 30
# 13 -> Apogäums-Triebwerk    -> 4/01                         -> 28
# 14 -> Tank (Xe)             -> 2/03 , 3/03                  -> 14 , 22
# 15 -> Tank (MMH/MON)        -> 2/01 , 2/02 , 3/01 , 3/02    -> 12 , 13 , 20 , 21
# 16 -> Sternsensor           -> 5/01 , 6/01                  -> 31 , 32
# 17 -> Tank (He)             -> ???
# 18 -> SADM                  -> 7/01                         -> 34
# 19 -> 10 N Triebwerke       -> 8/01 , 8/02                  -> 35
# 20 -> HET                   -> ???
#------------------------------------------------------------------------------
pix_array_01 = [11]
pix_array_02 = [10]
pix_array_03 = [ 6]
pix_array_06 = [ 3, 4]
pix_array_04 = [ 2 ,5]
pix_array_05 = [ 0, 1]
pix_array_07 = [ 7, 8]
pix_array_08 = [ 9]
pix_array_09 = [16, 24]
pix_array_10 = [19]
pix_array_11 = [17, 25]
pix_array_12 = [29, 30]
pix_array_13 = [28]
pix_array_14 = [14, 22]
pix_array_15 = [12, 13, 20, 21]
pix_array_16 = [31, 32]
pix_array_17 = [11]     # ???
pix_array_18 = [34]
pix_array_19 = [35]
pix_array_20 = [11]      # ???
#------------------------------------------------------------------------------

obj_offset = 0          # Offset bei Zählung ab 1 = -1

def blink_func():
    MyWS2812.do_blink()


# ------------------------------------------------------------------------------
# --- Main Function                                                          ---
# ------------------------------------------------------------------------------
def main():

    print("=== Start Main ===")
    
    blink_couter = 0
    
    MyWS2812.do_all_def()	# Alle Leds auf Default-Wert
       
    while MySerial.sercon_read_flag():

        if blink_couter > 50:
            blink_couter = 0
            blink_func()
        
        MySerial.sercon_read_line()
        if MySerial.get_ready_flag():       # Zeichenkette empfangen
            print(MySerial.get_string())
            MyDecode.decode_input(str(MySerial.get_string()))
            #MyDecode.decode_printout()
            if MyDecode.get_valid_flag() == True:
                #print("Valid Command")
                if MyDecode.get_cmd_1() == "do":
                    #print("do")
                    if MyDecode.get_cmd_2() == "all":
                        #print("all")
                        if MyDecode.get_value_1() == 0:
                            #print("off")
                            MyWS2812.do_all_off()
                        if MyDecode.get_value_1() == 1:
                            #print("on")
                            MyWS2812.do_all_on()
                        if MyDecode.get_value_1() == 2:
                            #print("def")
                            MyWS2812.do_all_def()
                    if MyDecode.get_cmd_2() == "obj":
                        #print("obj")
                        #print(MyDecode.get_value_1())
                        #print(segment_map[MyDecode.get_value_1()])
                        MyWS2812.do_all_off()
                        if MyDecode.get_value_1() == 1:
                            for i in pix_array_01:
                                MyWS2812.set_led_obj(i + obj_offset, MyDecode.get_value_2())
                        if MyDecode.get_value_1() == 2:
                            for i in pix_array_02:
                                MyWS2812.set_led_obj(i + obj_offset, MyDecode.get_value_2())
                        if MyDecode.get_value_1() == 3:
                            for i in pix_array_03:
                                MyWS2812.set_led_obj(i + obj_offset, MyDecode.get_value_2())
                        if MyDecode.get_value_1() == 4:
                            for i in pix_array_04:
                                MyWS2812.set_led_obj(i + obj_offset, MyDecode.get_value_2())
                        if MyDecode.get_value_1() == 5:
                            for i in pix_array_05:
                                MyWS2812.set_led_obj(i + obj_offset, MyDecode.get_value_2())
                        if MyDecode.get_value_1() == 6:
                            for i in pix_array_06:
                                MyWS2812.set_led_obj(i + obj_offset, MyDecode.get_value_2())
                        if MyDecode.get_value_1() == 7:
                            for i in pix_array_07:
                                MyWS2812.set_led_obj(i + obj_offset, MyDecode.get_value_2())
                        if MyDecode.get_value_1() == 8:
                            for i in pix_array_08:
                                MyWS2812.set_led_obj(i + obj_offset, MyDecode.get_value_2())
                        if MyDecode.get_value_1() == 9:
                            for i in pix_array_09:
                                MyWS2812.set_led_obj(i + obj_offset, MyDecode.get_value_2())
                        if MyDecode.get_value_1() == 10:
                            for i in pix_array_10:
                                MyWS2812.set_led_obj(i + obj_offset, MyDecode.get_value_2())
                        if MyDecode.get_value_1() == 11:
                            for i in pix_array_11:
                                MyWS2812.set_led_obj(i + obj_offset, MyDecode.get_value_2())
                        if MyDecode.get_value_1() == 12:
                            for i in pix_array_12:
                                MyWS2812.set_led_obj(i + obj_offset, MyDecode.get_value_2())
                        if MyDecode.get_value_1() == 13:
                            for i in pix_array_13:
                                MyWS2812.set_led_obj(i + obj_offset, MyDecode.get_value_2())
                        if MyDecode.get_value_1() == 14:
                            for i in pix_array_14:
                                MyWS2812.set_led_obj(i + obj_offset, MyDecode.get_value_2())
                        if MyDecode.get_value_1() == 15:
                            for i in pix_array_15:
                                MyWS2812.set_led_obj(i + obj_offset, MyDecode.get_value_2())
                        if MyDecode.get_value_1() == 16:
                            for i in pix_array_16:
                                MyWS2812.set_led_obj(i + obj_offset, MyDecode.get_value_2())
                        if MyDecode.get_value_1() == 17:
                            for i in pix_array_17:
                                MyWS2812.set_led_obj(i + obj_offset, MyDecode.get_value_2())
                        if MyDecode.get_value_1() == 18:
                            for i in pix_array_18:
                                MyWS2812.set_led_obj(i + obj_offset, MyDecode.get_value_2())
                        if MyDecode.get_value_1() == 19:
                            for i in pix_array_19:
                                MyWS2812.set_led_obj(i + obj_offset, MyDecode.get_value_2())
                        if MyDecode.get_value_1() == 20:
                            for i in pix_array_20:
                                MyWS2812.set_led_obj(i + obj_offset, MyDecode.get_value_2())
                        #=======================================================================

                if MyDecode.get_cmd_1() == "test":
                    #print("Test")
                    if MyDecode.get_cmd_2() == "led":
                        #print("LED")
                        MyWS2812.test_led(MyDecode.get_value_1(), MyDecode.get_value_2())
                

        blink_couter = blink_couter + 1
        # Loop-Delay !!!
        time.sleep(0.01)        # 10ms
        


    print("=== End of Main ===")

# ==============================================================================
# ==============================================================================
    
# ###############################################################################
# ### Main                                                                    ###
# ###############################################################################


if __name__ == "__main__":

    if MyModule.inc_ws2812:
        #print("WS2812 -> Load-Module")
        import libs.module_ws2812_v2 as MyWS2812         # Modul WS2812  -> WS2812-Ansteuerung
        #print("WS2812 -> Setup")
        MyWS2812.setup_ws2812()
        ### Test ###
        #print("WS2812 -> Run self test")
        MyWS2812.self_test()
        #print("WS2812 -> Blink Test")
        #MyWS2812.do_blink_test()
        #print("WS2812 -> Dot-Test")
        #MyWS2812.do_dot_test()

    if MyModule.inc_decoder:
        #print("Decode -> Load-Module")
        import libs.module_decode as MyDecode
        #print("Decode -> Setup")
        MyDecode.decode_setup()
        ### Test ###
        #print("Decode -> Test")
        #MyDecode.decode_input("Test")

    if MyModule.inc_serial:
        #print("Serial-COM -> Load-Module")
        import libs.module_serial as MySerial
        #print("Serial-Con -> Setup")
        MySerial.sercon_setup()
        ### Test ###
        #print("Serial-Con -> Test")
        #MySerial.sercon_write_out("Start Test")

    main()      # Start Main $$$

# Normal sollte das Programm hier nie ankommen !
print("___End of Programm___ !!!")

# ##############################################################################
