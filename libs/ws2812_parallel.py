# libs/ws2812_parallel.py
# High-Performance Parallel WS2812 DMA Driver for RP2040

from array import array
from machine import Pin
import time
import rp2
import machine

machine.freq(250_000_000)

CHANNELS = 8
LEDS_PER_CHANNEL = 200
FIRST_PIN = 2
RESET_US = 80


@rp2.asm_pio(
    out_init=(
        rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW,
        rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW,
        rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW,
        rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW,
    ),
    out_shiftdir=rp2.PIO.SHIFT_RIGHT,
    autopull=True,
    pull_thresh=32,
    fifo_join=rp2.PIO.JOIN_TX,
)
def _ws2812_parallel8():
    wrap_target()
    out(x, 8)
    mov(pins, invert(null)) [1]
    mov(pins, x) [4]
    mov(pins, null) [1]
    wrap()


class WS2812DirectDMA:
    """8-Kanal Parallel-Triebwerk mit DMA und Double-Buffering."""

    def __init__(self, leds=LEDS_PER_CHANNEL, first_pin=FIRST_PIN, brightness=255, sm_id=0):
        if not hasattr(rp2, "DMA"):
            raise RuntimeError("MicroPython-Firmware enthält rp2.DMA nicht")

        self.leds = int(leds)
        self.first_pin = int(first_pin)
        self.brightness = max(0, min(255, int(brightness)))
        self.sm_id = int(sm_id)

        self.words_per_buffer = self.leds * 6
        self.tx_buf0 = array("I", bytearray(self.words_per_buffer * 4))
        self.tx_buf1 = array("I", bytearray(self.words_per_buffer * 4))
        self.active_write = 0

        self.sm = rp2.StateMachine(
            self.sm_id,
            _ws2812_parallel8,
            freq=8_000_000,
            out_base=Pin(self.first_pin),
        )
        self.sm.active(1)

        self.dma = rp2.DMA()
        pio_num = self.sm_id >> 2
        local_sm = self.sm_id & 3
        dreq = (pio_num << 3) + local_sm
        self.dma_ctrl = self.dma.pack_ctrl(
            size=2,
            inc_read=True,
            inc_write=False,
            treq_sel=dreq,
        )

        self.clear(show=True)

    @micropython.viper
    def _set_pixel_fast(self, buf: object, channel: int, index: int, grb: int):
        buf_ptr = ptr32(buf)
        base_word = index * 6
        ch_mask = 1 << channel

        for bit in range(23, -1, -1):
            bit_idx = 23 - bit
            word_offset = bit_idx >> 2
            byte_pos = bit_idx & 3
            shift = byte_pos << 3

            target_word_idx = base_word + word_offset
            current_val = buf_ptr[target_word_idx]

            if (grb >> bit) & 1:
                current_val |= (ch_mask << shift)
            else:
                current_val &= ~(ch_mask << shift)

            buf_ptr[target_word_idx] = current_val

    def _pack_grb(self, rgb):
        r, g, b = rgb
        br = self.brightness
        r = (max(0, min(255, int(r))) * br) >> 8
        g = (max(0, min(255, int(g))) * br) >> 8
        b = (max(0, min(255, int(b))) * br) >> 8
        return (g << 16) | (r << 8) | b

    def pixel(self, channel, index, rgb):
        if 0 <= channel < CHANNELS and 0 <= index < self.leds:
            grb = self._pack_grb(rgb)
            buf = self.tx_buf0 if self.active_write == 0 else self.tx_buf1
            self._set_pixel_fast(buf, channel, index, grb)

    def fill(self, channel, rgb):
        if 0 <= channel < CHANNELS:
            grb = self._pack_grb(rgb)
            buf = self.tx_buf0 if self.active_write == 0 else self.tx_buf1
            for i in range(self.leds):
                self._set_pixel_fast(buf, channel, i, grb)

    def fill_all(self, rgb):
        grb = self._pack_grb(rgb)
        buf = self.tx_buf0 if self.active_write == 0 else self.tx_buf1
        for ch in range(CHANNELS):
            for i in range(self.leds):
                self._set_pixel_fast(buf, ch, i, grb)

    def clear(self, show=False):
        buf = self.tx_buf0 if self.active_write == 0 else self.tx_buf1
        for i in range(len(buf)):
            buf[i] = 0

        if show:
            self.show()

    def busy(self):
        return bool(self.dma.active())

    def wait(self):
        while self.dma.active():
            pass
        time.sleep_us(RESET_US)

    def show(self, wait=False):
        self.wait()

        read_buf = self.tx_buf0 if self.active_write == 0 else self.tx_buf1
        write_buf = self.tx_buf1 if self.active_write == 0 else self.tx_buf0

        self.dma.config(
            read=read_buf,
            write=self.sm,
            count=len(read_buf),
            ctrl=self.dma_ctrl,
            trigger=True,
        )

        write_buf[:] = read_buf[:]
        self.active_write = 1 if self.active_write == 0 else 0

        if wait:
            self.wait()

    def deinit(self):
        self.wait()
        self.clear(show=True)
        self.sm.active(0)
        self.dma.close()

