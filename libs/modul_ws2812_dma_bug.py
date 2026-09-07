import array
import time
import math
from machine import Pin, mem32
import rp2
import uctypes

# --- PIO ASSEMBLY (WS2812 Timing: 800 kHz) ---
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


# --- VIPER SET_LED & BRESENHAM LINIEN-DRAWING ---
@micropython.viper
def set_pixel(strip_addrs_ptr: ptr32, x: int, y: int, r: int, g: int, b: int, leds_per_strip: int):
    """Setzt ein einzelnes Pixel (x, y) direkt im aktiven Back-Buffer."""
    if y >= 0 and y <= 7 and x >= 0 and x < leds_per_strip:
        color = (g << 24) | (r << 16) | (b << 8)
        buf_ptr = ptr32(strip_addrs_ptr[y])
        buf_ptr[x] = color

@micropython.viper
def draw_line(strip_addrs_ptr: ptr32, x0: int, y0: int, x1: int, y1: int, r: int, g: int, b: int, leds_per_strip: int):
    if y0 < 0: y0 = 0
    elif y0 > 7: y0 = 7
    if y1 < 0: y1 = 0
    elif y1 > 7: y1 = 7

    color = (g << 24) | (r << 16) | (b << 8)

    dx = x1 - x0
    if dx < 0: dx = -dx
    sx = 1 if x0 < x1 else -1

    dy = y1 - y0
    if dy < 0: dy = -dy
    else: dy = -dy
    sy = 1 if y0 < y1 else -1

    err = dx + dy

    while True:
        if x0 >= 0 and x0 < leds_per_strip:
            buf_ptr = ptr32(strip_addrs_ptr[y0])
            buf_ptr[x0] = color

        if x0 == x1 and y0 == y1:
            break

        e2 = err << 1
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


# --- HOCHPERFORMANTE WS2812 PARALLEL-KLASSE ---
class WS2812Fast:
    def __init__(self, start_pin: int, leds_per_strip: int):
        self.num_strips = 8
        self.leds_per_strip = leds_per_strip
        self.DMA_BASE = 0x50000000
        
        # Double-Buffering
        self.buffer_sets = [
            [array.array("I", [0] * leds_per_strip) for _ in range(8)],
            [array.array("I", [0] * leds_per_strip) for _ in range(8)]
        ]
        
        self.addrs_set0 = array.array("I", [uctypes.addressof(b) for b in self.buffer_sets[0]])
        self.addrs_set1 = array.array("I", [uctypes.addressof(b) for b in self.buffer_sets[1]])
        
        self.write_index = 0
        self.dma_configs = array.array("I", [0] * 8)
        self.sm_list = []
        
        # 1. DMA-Kanäle vorab sicher stoppen
        DMA_ABORT = self.DMA_BASE + 0x444
        mem32[DMA_ABORT] = 0xFF
        while mem32[DMA_ABORT] != 0:
            pass

        dreq_map = [0, 1, 2, 3, 8, 9, 10, 11]

        for i in range(8):
            # Pin direkt mit initialem LOW-State definieren
            pin = Pin(start_pin + i, Pin.OUT, value=0)
            sm = rp2.StateMachine(i, ws2812_parallel, freq=8_000_000, sideset_base=pin)
            sm.active(1)
            self.sm_list.append(sm)
            
            dreq = dreq_map[i]
            self.dma_configs[i] = (dreq << 15) | (1 << 4) | (2 << 2) | 1
            dest_fifo = (0x50200010 + (i * 4)) if i < 4 else (0x50300010 + ((i - 4) * 4))
            
            base = self.DMA_BASE + (i * 0x40)
            mem32[base + 0x04] = dest_fifo

    def clear(self):
        addrs_ptr = uctypes.addressof(self.addrs_set0) if self.write_index == 0 else uctypes.addressof(self.addrs_set1)
        self._clear_viper(addrs_ptr, self.leds_per_strip)

    @staticmethod
    @micropython.viper
    def _clear_viper(strip_addrs_ptr: ptr32, leds_per_strip: int):
        for s in range(8):
            buf_ptr = ptr32(strip_addrs_ptr[s])
            for i in range(leds_per_strip):
                buf_ptr[i] = 0

    def set_led(self, x: int, y: int, r: int, g: int, b: int):
        """Setzt eine einzelne LED an Position x (Index auf Streifen) und y (Kanal 0-7)"""
        addrs_ptr = uctypes.addressof(self.addrs_set0) if self.write_index == 0 else uctypes.addressof(self.addrs_set1)
        set_pixel(addrs_ptr, x, y, r, g, b, self.leds_per_strip)

    def draw_line_global(self, x0: int, y0: int, x1: int, y1: int, r: int, g: int, b: int):
        addrs_ptr = uctypes.addressof(self.addrs_set0) if self.write_index == 0 else uctypes.addressof(self.addrs_set1)
        draw_line(addrs_ptr, x0, y0, x1, y1, r, g, b, self.leds_per_strip)

    def show(self):
        for i in range(8):
            while mem32[self.DMA_BASE + (i * 0x40) + 0x0C] & (1 << 24):
                pass
        
        # Sicherer Reset-Spreizwert für alle WS2812B-Varianten
        time.sleep_us(350)
        
        read_idx = self.write_index
        active_buffers = self.buffer_sets[read_idx]
        
        for i in range(8):
            base = self.DMA_BASE + (i * 0x40)
            mem32[base + 0x00] = uctypes.addressof(active_buffers[i])
            mem32[base + 0x08] = self.leds_per_strip
            mem32[base + 0x0C] = self.dma_configs[i]
            
        self.write_index = 1 - self.write_index

    def cleanup(self):
        DMA_ABORT = self.DMA_BASE + 0x444
        mem32[DMA_ABORT] = 0xFF
        while mem32[DMA_ABORT] != 0:
            pass

        for i in range(8):
            base = self.DMA_BASE + (i * 0x40)
            mem32[base + 0x0C] = 0
            if i < len(self.sm_list):
                self.sm_list[i].active(0)


def test_ws2812():
    leds = WS2812Fast(start_pin=2, leds_per_strip=250)

    try:
        print("Setze die ersten 5 LEDs einzeln in Weiß...")
        leds.clear()
        
        for y in range(8):
            for x in range(5):
                leds.set_led(x=x, y=y, r=0, g=40, b=40)
        
        leds.show()
        
        print("Ausgabe gesendet. Warte 10 Sekunden...")
        time.sleep(10)

    finally:
        leds.cleanup()
        print("Beendet.")

if __name__ == "__main__":
    test_ws2812()