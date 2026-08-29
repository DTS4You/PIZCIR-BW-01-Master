###############################################################################
### Programm    : WS2812 Fast DMA + Viper
### Version     : 1.00
### Autor       : Norbert Schwarz
### Datum       : 2026-07-31
###############################################################################
#import sys
import array
import time
from machine import Pin, mem32
import rp2
import uctypes
import uasyncio as asyncio

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, 
             autopull=True, pull_thresh=24)
def ws2812_parallel():
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0) [2]
    jmp(not_x, "do_zero")   .side(1) [1]
    jmp("bitloop")          .side(1) [4]
    label("do_zero")
    nop()                   .side(0) [4]
    wrap()

class WS2812Fast:
    def __init__(self, start_pin, leds_per_strip):
        self.num_strips = 8
        self.leds_per_strip = leds_per_strip
        self.DMA_BASE = 0x50000000
        
        # Sätze von Buffern
        self.buffer_sets = [
            [array.array("I", [0] * leds_per_strip) for _ in range(8)],
            [array.array("I", [0] * leds_per_strip) for _ in range(8)]
        ]
        
        # Zeiger (Memory-Adressen) auf die einzelnen Arrays für superschnellen Viper-Zugriff
        self.addrs_set0 = array.array("I", [uctypes.addressof(b) for b in self.buffer_sets[0]])
        self.addrs_set1 = array.array("I", [uctypes.addressof(b) for b in self.buffer_sets[1]])
        
        self.write_index = 0
        self.dma_configs = array.array("I", [0] * 8)
        
        for i in range(8):
            pin = Pin(start_pin + i)
            sm = rp2.StateMachine(i, ws2812_parallel, freq=8_000_000, sideset_base=pin)
            sm.active(1)
            
            dreq = i if i < 4 else 8 + (i - 4)
            self.dma_configs[i] = (dreq << 15) | (1 << 4) | (2 << 2) | 1
            
            dest_fifo = (0x50200010 + (i * 4)) if i < 4 else (0x50300010 + ((i - 4) * 4))
            mem32[self.DMA_BASE + (i * 0x40) + 0x04] = dest_fifo



    def clear(self):
        addrs_ptr = uctypes.addressof(self.addrs_set0) if self.write_index == 0 else uctypes.addressof(self.addrs_set1)
        self._clear_viper(addrs_ptr, self.leds_per_strip)

    def fill(self):
        addrs_ptr = uctypes.addressof(self.addrs_set0) if self.write_index == 0 else uctypes.addressof(self.addrs_set1)
        self._fill_viper(addrs_ptr, self.leds_per_strip)

    def fill_strip_rgb(self, stripe, r, g, b):
        addrs_ptr = uctypes.addressof(self.addrs_set0) if self.write_index == 0 else uctypes.addressof(self.addrs_set1)
        self._fill_viper_stripe_rgb(addrs_ptr, self.leds_per_strip, stripe, r, g, b)

    def set_pixel(self, stripe, index):
        addrs_ptr = uctypes.addressof(self.addrs_set0) if self.write_index == 0 else uctypes.addressof(self.addrs_set1)
        self._pixel_viper(addrs_ptr, self.leds_per_strip, stripe, index)

    def set_pixel_rgb(self, stripe, index, r, g, b):
        addrs_ptr = uctypes.addressof(self.addrs_set0) if self.write_index == 0 else uctypes.addressof(self.addrs_set1)
        self._pixel_viper_rgb(addrs_ptr, self.leds_per_strip, stripe, index, r, g, b)

    #--------------------------------------------------------------------------
    @staticmethod
    @micropython.viper
    def _pixel_viper_rgb(strip_addrs_ptr: ptr32, leds_per_strip: int, stripe: int, index: int, r: int, g: int, b: int):
        buf_ptr = ptr32(strip_addrs_ptr[stripe])
        buf_ptr[index] = (g << 24) | (r << 16) | (b << 8)

    #--------------------------------------------------------------------------
    @staticmethod
    @micropython.viper
    def _pixel_viper(strip_addrs_ptr: ptr32, leds_per_strip: int, stripe: int, index: int):
        buf_ptr = ptr32(strip_addrs_ptr[stripe])
        r = 0
        g = 0
        b = 10
        buf_ptr[index] = (g << 24) | (r << 16) | (b << 8)
    #--------------------------------------------------------------------------
    @staticmethod
    @micropython.viper
    def _fill_viper(strip_addrs_ptr: ptr32, leds_per_strip: int):
        for s in range(8):
            buf_ptr = ptr32(strip_addrs_ptr[s])
            for i in range(leds_per_strip):
                r = 10
                g = 10
                b = 10
                buf_ptr[i] = (g << 24) | (r << 16) | (b << 8)
    #--------------------------------------------------------------------------
    @staticmethod
    @micropython.viper
    def _fill_viper_stripe_rgb(strip_addrs_ptr: ptr32, leds_per_strip: int, stripe: int, r: int, g: int, b: int):
        buf_ptr = ptr32(strip_addrs_ptr[stripe])
        for i in range(leds_per_strip):
            buf_ptr[i] = (g << 24) | (r << 16) | (b << 8)
    #--------------------------------------------------------------------------
    @staticmethod
    @micropython.viper
    def _clear_viper(strip_addrs_ptr: ptr32, leds_per_strip: int):
        for s in range(8):
            buf_ptr = ptr32(strip_addrs_ptr[s])
            for i in range(leds_per_strip):
                buf_ptr[i] = 0
    #--------------------------------------------------------------------------

    def show(self):
        # Warten, falls DMA noch liest
        for i in range(8):
            while mem32[self.DMA_BASE + (i * 0x40) + 0x0C] & (1 << 24):
                pass
        
        time.sleep_us(300) # Reset Pause
        
        read_idx = self.write_index
        active_buffers = self.buffer_sets[read_idx]
        
        # Trigger DMA
        for i in range(8):
            base = self.DMA_BASE + (i * 0x40)
            mem32[base + 0x00] = uctypes.addressof(active_buffers[i])
            mem32[base + 0x08] = self.leds_per_strip
            mem32[base + 0x0C] = self.dma_configs[i]
            
        self.write_index = 1 - self.write_index

    def cleanup(self):
        """ Stoppt alle DMA-Kanäle und PIO State Machines sauber. """
        
        # 1. Alle DMA-Kanäle stoppen (Abort Bit setzen)
        # Für jeden Kanal (0 bis 7) das ABORT Register (Offset 0x444 im DMA-Block) ansprechen
        DMA_ABORT = self.DMA_BASE + 0x444
        mem32[DMA_ABORT] = 0xFF  # Bit 0-7 = Maske für DMA Kanäle 0 bis 7
        
        # Warten, bis der Abort verarbeitet wurde (Bit wird von der Hardware wieder genullt)
        while mem32[DMA_ABORT] != 0:
            pass

        # 2. DMA-Kanäle zurücksetzen/deaktivieren (CTRL_TRIG nullen)
        for i in range(8):
            ctrl_reg = self.DMA_BASE + (i * 0x40) + 0x0C
            mem32[ctrl_reg] = 0

        # 3. PIO State Machines stoppen & LEDs ausschalten
        # Wir setzen zuerst alle LEDs auf Schwarz, bevor wir abschalten
        self.clear()
        self.show()
        time.sleep_ms(1)  # Kurze Zeit geben zum Ausgeben
        
        for i in range(8):
            # State Machine i über die rp2.StateMachine API stoppen
            rp2.StateMachine(i).active(0)
            
            # Optional: PIO FIFO leeren
            pio_base = 0x50200000 if i < 4 else 0x50300000
            mem32[pio_base + 0x010 + ((i % 4) * 4)] = 0
        

# --- DER TURBO-RENDERER (VIPER) ---
@micropython.viper
def render_viper(strip_addrs_ptr: ptr32, sin_tab_ptr: ptr8, t_int: int, leds_per_strip: int):
    # In Viper greifen wir direkt per RAW-32-Bit-Pointer auf den RAM zu
    for s in range(8):
        # Hole die Basisadresse für den aktuellen Streifen
        buf_ptr = ptr32(strip_addrs_ptr[s])
        s_off = s * 20
        
        for i in range(leds_per_strip):
            # Schnelle Math-Indices
            idx1 = (i * 3 + t_int) & 255
            idx2 = (s_off + t_int * 2) & 255
            
            val1 = int(sin_tab_ptr[idx1])
            val2 = int(sin_tab_ptr[idx2])
            
            plasma = (val1 + val2 + 254) >> 1
            
            # RGB Werte berechnen
            r = (int(sin_tab_ptr[(plasma + t_int) & 255]) + 128) >> 4
            g = (int(sin_tab_ptr[(plasma * 2) & 255]) + 128) >> 5
            b = (int(sin_tab_ptr[(plasma + s_off) & 255]) + 128) >> 4
            
            # WS2812 GRB Format als 32-Bit Integer zusammensetzen
            # Schreibt DIREKT in den RAM ohne Methodenaufruf!
            buf_ptr[i] = (g << 24) | (r << 16) | (b << 8)



def main():

    frame_time = 0.5
    time.sleep(0.3)

    print("Starte Viper-beschleunigte Berechnung...")

    # --- Hauptschleife ---
    leds = WS2812Fast(start_pin=2, leds_per_strip=175)

    try:
        while True:
            # Aktuelle Adressen des Ziel-Buffers holen
            if leds.write_index == 0:
                addrs_ptr = uctypes.addressof(leds.addrs_set0)
            else:
                addrs_ptr = uctypes.addressof(leds.addrs_set1)
                
            leds.set_pixel(4,5)
            leds.show()
            time.sleep(frame_time)
            leds.clear()
            leds.show()
            time.sleep(frame_time)
            
    except KeyboardInterrupt:
        leds.clear()
        leds.show()
        leds.cleanup()
        del leds
        print("ENDE")
        machine.reset()

# ###############################################################################
# ### Main                                                                    ###
# ###############################################################################

if __name__ == "__main__":

    main()
