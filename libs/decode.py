####################################################################
### Decoder
####################################################################

####################################################################
### Command , Sub-Command , Value 1 , Value 2                    ###
####################################################################



class Decoder:

    def __init__(self):
        
        self.data = ""
        self.array = []
        self.valid_flag = False
        self.arrary_len = 0
        self.cmd_1 = ""
        self.cmd_2 = ""
        self.value_1 = 0
        self.value_2 = 0
        self.value_3 = 0

    def res_valid_flag(self):
        self.valid_flag = False

    def get_valid_flag(self):
        return self.valid_flag

    def send_data(self, data):
        self.valid_flag = False
        self.data = data
        self.data_split()

    def data_split(self):
        self.array = self.data.split(",")
        self.arrary_len = len(self.array)
        self.cmd_decode()

    def get_data(self):
        return self.data

    def get_array(self):
        return self.array

    def cmd_decode(self):
        if self.array[0] == "set" and self.arrary_len > 1:
            if self.array[1] == "on":
                print("Parameter -> On")
            if self.array[1] == "off":
                print("Parameter -> Off")
            if self.array[1] == "def":
                print("Parameter -> Default")
            if self.array[1] == "bri":
                print("Parameter -> Brightness")
        elif self.array[0] == "do" and self.arrary_len > 2:
            self.cmd_1 = "do"
            if self.array[1] == "led" and self.arrary_len == 5:
                self.cmd_2 = "led"
                self.value_1 = int(self.array[2])
                self.value_2 = int(self.array[3])
                self.value_3 = (self.array[4])
                self.valid_flag = True

            elif self.array[1] == "obj" and self.arrary_len == 4:
                self.cmd_2 = "obj"
                self.value_1 = int(self.array[2])
                self.value_2 = self.array[3]
                self.valid_flag = True

            elif self.array[1] == "all":
                self.cmd_2 = "all"
                if self.array[2] == "on" and self.arrary_len == 3:
                    self.value_1 = 1
                    self.valid_flag = True
                    
                if self.array[2] == "off" and self.arrary_len == 3:
                    self.value_1 = 0
                    self.valid_flag = True

                if self.array[2] == "def" and self.arrary_len == 3:
                    self.value_1 = 2
                    self.valid_flag = True

            else:
                self.valid_flag = False

        elif self.array[0] == "test" and self.arrary_len == 4:
            self.cmd_1 = "test"
            if self.array[1] == "led":
                self.cmd_2 = "led"
                self.value_1 = int(self.array[2])   # Stripe (0-7)
                self.value_2 = int(self.array[3])   # LED-Position (0-1024)
                self.valid_flag = True

        else:
            self.valid_flag = False

def decode_setup():
    
    global cmd_dec
    cmd_dec = Decoder()


def decode_printout():

    if cmd_dec.valid_flag:
        print("valid command")
        for x in range(0, cmd_dec.arrary_len):
            print(cmd_dec.array[x])
    else:
        print("no valid command")


def decode_input(test_string):
        
    cmd_dec.send_data(test_string)
    
    #decode_printout()

def get_cmd_1():
    return cmd_dec.cmd_1
    
def get_cmd_2():
    return cmd_dec.cmd_2

def get_value_1():
    return cmd_dec.value_1

def get_value_2():
    return cmd_dec.value_2

def get_value_3():
    return cmd_dec.value_3

def get_valid_flag():
    return cmd_dec.valid_flag

def get_array_len():
    return cmd_dec.arrary_len
  

# ------------------------------------------------------------------------------
# --- Main Function                                                          ---
# ------------------------------------------------------------------------------
def main():

    print("Decode -> Setup")
    decode_setup()
    print("Decode -> Test")
    print("-----------------------------------")
    #decode_test("do,led,0,10,on")
    #print("-----------------------------------")
    decode_input("do,obj,4,def")
    decode_printout()
    print(get_cmd_1())
    print("-----------------------------------")
    decode_input("test,led,1,0")
    decode_printout()
    print("-----------------------------------")



# ==============================================================================

# ###############################################################################
# ### Main                                                                    ###
# ###############################################################################

if __name__ == "__main__":
    main()

    # Normal sollte das Programm hier nie ankommen !
    print("End of Programm !!!")

# ##############################################################################
