# #############################################################################
# ### MyGlobal
# #############################################################################

class Global_Module:
    
    inc_ws2812          = True
    inc_decoder         = True
    inc_serial          = True
    inc_xio             = True

class Global_WS2812:

    numpix_1            = 175           # Anzahl LEDs im 1. Stripe
    numpix_2            = 175           # Anzahl LEDs im 2. Stripe
    numpix_3            = 175           # Anzahl LEDs im 3. Stripe
    numpix_4            = 175           # Anzahl LEDs im 4. Stripe
    numpix_5            = 175           # Anzahl LEDs im 5. Stripe
    numpix_6            = 175           # Anzahl LEDs im 6. Stripe
    numpix_7            = 176           # Anzahl LEDs im 7. Stripe
    numpix_8            = 176           # Anzahl LEDs im 8. Stripe
    # -------------------------------------------------------------------------
    # 1. Stripe -> 0
    seg_01_strip        = 0             #  1. Ledsegment -> Stripe      # 1. LED hinterer Teil
    seg_01_start        = 0             #  1. Ledsegment -> Start
    seg_01_count        = 175           #  1. Ledsegment -> Anzahl
    # 2. Stripe -> 1
    seg_02_strip        = 1             #  2. Ledsegment -> Stripe      # 2. LED hinterer Teil
    seg_02_start        = 0             #  2. Ledsegment -> Start
    seg_02_count        = 175           #  2. Ledsegment -> Anzahl
    # 3. Stripe -> 2
    seg_03_strip        = 2             #  3. Ledsegment -> Stripe      # 3. LED hinterer Teil
    seg_03_start        = 0             #  3. Ledsegment -> Start
    seg_03_count        = 175           #  3. Ledsegment -> Anzahl
    # 4. Stripe -> 3
    seg_04_strip        = 3             #  4. Ledsegment -> Stripe      # 4. LED hinterer Teil
    seg_04_start        = 0             #  4. Ledsegment -> Start
    seg_04_count        = 175           #  4. Ledsegment -> Anzahl
    # 5. Stripe -> 4
    seg_05_strip        = 4             #  5. Ledsegment -> Stripe      # 5. LED hinterer Teil
    seg_05_start        = 0             #  5. Ledsegment -> Start
    seg_05_count        = 175           #  5. Ledsegment -> Anzahl
    # 6. Stripe -> 5
    seg_06_strip        = 5             #  6. Ledsegment -> Stripe      # 6. LED hinterer Teil
    seg_06_start        = 0             #  6. Ledsegment -> Start
    seg_06_count        = 175           #  6. Ledsegment -> Anzahl
    # 7. Stripe -> 6
    seg_07_strip        = 6             #  7. Ledsegment -> Stripe      # 7. LED hinterer Teil
    seg_07_start        = 0             #  7. Ledsegment -> Start
    seg_07_count        = 175           #  7. Ledsegment -> Anzahl
    # 8. Stripe -> 7
    seg_08_strip        = 7             #  8. Ledsegment -> Stripe      # 8. LED hinterer Teil
    seg_08_start        = 0             #  8. Ledsegment -> Start
    seg_08_count        = 175           #  8. Ledsegment -> Anzahl
    #    
# -----------------------------------------------------------------------------

    color_def           = (  0,  0,  3)
    color_off           = (  0,  0,  0)
    color_on            = (100,100,100)
    color_dot           = ( 50, 50, 50)
    color_blink_on      = (  0,200,  0)
    color_blink_off     = (  0, 10,  0)


class Global_Default:

    blink_freq          = 3.0           # Blink Frequenz
    

def main():

    print("Start Global Init")
    mg = Global_WS2812
    print(mg.numpix_1)
    print(mg.numpix_2)
    print(mg.seg_01_strip, mg.seg_01_start, mg.seg_01_count)
    print(mg.seg_02_strip, mg.seg_02_start, mg.seg_02_count)


#------------------------------------------------------------------------------
#--- Main
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()