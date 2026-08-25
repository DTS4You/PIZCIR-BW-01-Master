# #############################################################################
# ### Modul XIO_2 -> Extendet Version mit 6 Bit IO
# ### V1.00
# #############################################################################
from machine import Pin             # type: ignore
from utime import sleep             # type: ignore

class XIO:

    def __init__(self, dir):
        self.dir = dir
        self.value = 0x00
        self.io = [False, False, False, False, False, False]
        self.pin = []
        if dir == "OUTPUT":
            self.set_xio_out()
        else:
            self.set_xio_in()

    def set_xio_out(self):
        self.pin.append(Pin(10, mode=Pin.OUT))
        self.pin.append(Pin(11, mode=Pin.OUT))
        self.pin.append(Pin(12, mode=Pin.OUT))
        self.pin.append(Pin(13, mode=Pin.OUT))
        self.pin.append(Pin(14, mode=Pin.OUT))
        self.pin.append(Pin(15, mode=Pin.OUT))

    def set_xio_in(self):
        self.pin.append(Pin(10, mode=Pin.IN, pull=Pin.PULL_UP))
        self.pin.append(Pin(11, mode=Pin.IN, pull=Pin.PULL_UP))
        self.pin.append(Pin(12, mode=Pin.IN, pull=Pin.PULL_UP))
        self.pin.append(Pin(13, mode=Pin.IN, pull=Pin.PULL_UP))
        self.pin.append(Pin(14, mode=Pin.IN, pull=Pin.PULL_UP))
        self.pin.append(Pin(15, mode=Pin.IN, pull=Pin.PULL_UP))
    
    def read_input(self):
        for i in range(6):
            self.io[i] = self.pin[i].value()

    def write_output(self):
        for i in range(6):
            self.pin[i].value(self.io[i])
    
    def read_io(self):
        self.read_input()
        return self.get_byte()
    
    def write_io(self, value):
        self.set_byte(value)
        self.write_output()

    def set_bit(self, bit, value=True):
        self.io[bit] = value
        return self.io[bit]
    
    def get_bit(self, bit):
        return self.io[bit]
    
    def set_byte(self, value):
        self.value = value
        for i in range(6):
            if (self.value & 1 << i ):
                self.io[i] = True
            else:
                self.io[i] = False

    def get_byte(self):
        self.value = 0x00
        for i in range(6):
            if self.io[i] == True:
                self.value = self.value | 1 << i
        return self.value
    
# -----------------------------------------------------------------------------
def main():

    print("=== Start Main -> Module_XIO ===")

    try:
        print("Start")

        debug = "INPUT"

        if debug == "OUTPUT":
            print("Write Output")
            xio = XIO("OUTPUT")

            xio.write_output()

            sleep(1)
        
            xio.set_bit(0, True)
            xio.set_bit(1, False)
            xio.set_bit(2, True)
            xio.set_bit(3, False)
            xio.set_bit(4, True)
            xio.set_bit(5, False)

            xio.write_output()

            sleep(1)

            xio.set_byte(0x01)
            xio.write_output()
            print(hex(xio.get_byte()))

            sleep(1)

            xio.set_byte(0x02)
            xio.write_output()
            print(hex(xio.get_byte()))
    
            sleep(1)

            xio.set_byte(0x04)
            xio.write_output()
            print(hex(xio.get_byte()))

            sleep(1)

            xio.set_byte(0x08)
            xio.write_output()
            print(hex(xio.get_byte()))

            sleep(1)

            xio.set_byte(0x10)
            xio.write_output()
            print(hex(xio.get_byte()))

            sleep(1)            

            xio.set_byte(0x20)
            xio.write_output()
            print(hex(xio.get_byte()))

            sleep(1)
        
            xio.set_byte(0x55)
            xio.write_output()
            print(hex(xio.get_byte()))

            sleep(1)
            xio.write_io(0xAA)
            print(hex(xio.get_byte()))

            sleep(1)
            xio.write_io(0x55)
            print(hex(xio.get_byte()))

            sleep(1)
            xio.write_io(0x00)
            print("Delete Object")
            del xio
        
        else:
            print("Read Input")
            xio = XIO("INPUT")
            xio.read_input()
            print(hex(xio.get_byte()))

            sleep(1)

            while(True):
                xio.read_io()
                print("Bit 5 = " + str(xio.get_bit(5)) + " | Bit 4 = " + str(xio.get_bit(4)) + " | Bit 3 = " + str(xio.get_bit(3)) + " | Bit 2 = " + str(xio.get_bit(2)) + " | Bit 1 = " + str(xio.get_bit(1)) + " | Bit 0 = " + str(xio.get_bit(0)))
                sleep(0.3)
            
            
      

    except KeyboardInterrupt:
        print("Keyboard Interrupt")
    finally:
        print("Exiting the program")
        print("Delete Object")
        del xio
    print("=== End Main ===")

# ------------------------------------------------------------------------------
# --- Main
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

# =============================================================================
