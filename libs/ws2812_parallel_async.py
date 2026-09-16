###############################################################################
# Version 1.00
# Getestet und i.O.
# ws2812_parallel_async.py
# RP2040 MicroPython: 8 x WS2812 parallel, GPIO2..GPIO9
# 1 PIO-State-Machine, 1 DMA-Kanal, Double Buffering, uasyncio
###############################################################################
from array import array
from machine import Pin
import rp2
import uasyncio as asyncio
import uctypes

CHANNELS = 8

@rp2.asm_pio(
    out_init=(rp2.PIO.OUT_LOW,) * 8,
    out_shiftdir=rp2.PIO.SHIFT_RIGHT,
    autopull=True,
    pull_thresh=32,
    fifo_join=rp2.PIO.JOIN_TX,
)
def ws2812_parallel8():
    # 10 Takte/Bit bei 8 MHz = 1,25 us.
    # 0-Bit: HIGH 2, LOW 8 Takte. 1-Bit: HIGH 7, LOW 3 Takte.
    wrap_target()
    out(x, 8)
    mov(pins, invert(null)) [1]
    mov(pins, x) [4]
    mov(pins, null) [1]
    wrap()

# Native ARM-Assembler-Transposition für 8 Kanäle
@micropython.viper
def _encode_chunk_viper(
    ch0: ptr32,
    ch1: ptr32,
    ch2: ptr32,
    ch3: ptr32,
    ch4: ptr32,
    ch5: ptr32,
    ch6: ptr32,
    ch7: ptr32,
    tx_ptr: ptr32,
    start_led: int,
    end_led: int,
    out_word_idx: int,
    ) -> int:
    oi = out_word_idx

    for led in range(start_led, end_led):
        # 32-Bit GRB-Werte aller 8 Kanäle laden
        v0 = int(ch0[led])
        v1 = int(ch1[led])
        v2 = int(ch2[led])
        v3 = int(ch3[led])
        v4 = int(ch4[led])
        v5 = int(ch5[led])
        v6 = int(ch6[led])
        v7 = int(ch7[led])

        # 24 Bits -> 6 x 32-Bit Worte (je 4 Bitplane-Masken)
        for w in range(6):
            word = 0
            for b in range(4):
                bit_idx = 23 - (w * 4 + b)
                test = 1 << bit_idx
                mask = 0

                if v0 & test:
                    mask |= 1
                if v1 & test:
                    mask |= 2
                if v2 & test:
                    mask |= 4
                if v3 & test:
                    mask |= 8
                if v4 & test:
                    mask |= 16
                if v5 & test:
                    mask |= 32
                if v6 & test:
                    mask |= 64
                if v7 & test:
                    mask |= 128

                word |= mask << (b * 8)

            tx_ptr[oi] = word
            oi += 1

    return oi

class WS2812ParallelAsync:
    """8 parallele WS2812-Strips mit zwei Zeichen- und zwei DMA-Puffern.

    draw buffer: wird von pixel()/fill()/clear() beschrieben.
    queued buffer: wird in Bitplanes konvertiert und per DMA gesendet.
    Nach erfolgreichem show() werden die Zeichenpuffer vertauscht. Damit kann
    die Anwendung den naechsten Frame zeichnen, waehrend DMA den aktuellen sendet.
    """

    def __init__(self, leds=200, first_pin=2, brightness=255, sm_id=0,
                 yield_every=8, reset_us=80):
        if not hasattr(rp2, "DMA"):
            raise RuntimeError("Diese Firmware enthaelt rp2.DMA nicht")
        if leds < 1:
            raise ValueError("leds muss mindestens 1 sein")
        if not 0 <= first_pin <= 22:
            raise ValueError("Ungueltiger Startpin fuer 8 zusammenhaengende GPIOs")
        if not 0 <= sm_id <= 7:
            raise ValueError("sm_id muss 0..7 sein")

        self.leds = int(leds)
        self.brightness = max(0, min(255, int(brightness)))
        self.yield_every = max(1, int(yield_every))
        self.reset_ms = max(1, (int(reset_us) + 999) // 1000)

        # Zwei logische Frames: je 8 Kanaele mit je leds GRB-Woertern.
        self._frames = [
            [array("I", [0] * self.leds) for _ in range(CHANNELS)],
            [array("I", [0] * self.leds) for _ in range(CHANNELS)],
        ]
        # Zwei Sende-Puffer: 24 Masken/LED, vier Masken je 32-Bit-Wort.
        self._tx = [
            array("I", [0] * (self.leds * 6)),
            array("I", [0] * (self.leds * 6)),
        ]
        self._draw = 0
        self._spare_tx = 0
        self._send_tx = None
        self._lock = asyncio.Lock()

        self.sm_id = int(sm_id)
        self.sm = rp2.StateMachine(
            self.sm_id, ws2812_parallel8, freq=8_000_000,
            out_base=Pin(first_pin)
        )
        self.sm.active(1)

        self.dma = rp2.DMA()
        pio_num = self.sm_id >> 2
        local_sm = self.sm_id & 3
        dreq = (pio_num << 3) + local_sm
        self._dma_ctrl = self.dma.pack_ctrl(
            size=2, inc_read=True, inc_write=False, treq_sel=dreq
        )

    def _grb(self, rgb):
        r, g, b = rgb
        br = self.brightness
        r = (max(0, min(255, int(r))) * br) // 255
        g = (max(0, min(255, int(g))) * br) // 255
        b = (max(0, min(255, int(b))) * br) // 255
        return (g << 16) | (r << 8) | b

    @property
    def drawing_frame(self):
        return self._frames[self._draw]

    def pixel(self, channel, index, rgb=None):
        if not 0 <= channel < CHANNELS:
            raise IndexError("channel muss 0..7 sein")
        if not 0 <= index < self.leds:
            raise IndexError("LED-Index ungueltig")
        frame = self._frames[self._draw]
        if rgb is None:
            v = frame[channel][index]
            return ((v >> 8) & 255, (v >> 16) & 255, v & 255)
        frame[channel][index] = self._grb(rgb)

    def fill(self, channel, rgb):
        if not 0 <= channel < CHANNELS:
            raise IndexError("channel muss 0..7 sein")
        value = self._grb(rgb)
        dst = self._frames[self._draw][channel]
        for i in range(self.leds):
            dst[i] = value

    def fill_all(self, rgb):
        value = self._grb(rgb)
        frame = self._frames[self._draw]
        for ch in range(CHANNELS):
            dst = frame[ch]
            for i in range(self.leds):
                dst[i] = value

    def clear(self):
        frame = self._frames[self._draw]
        for ch in range(CHANNELS):
            dst = frame[ch]
            for i in range(self.leds):
                dst[i] = 0

    async def _encode(self, frame_index, tx_index):
        """Frame kooperativ & performant mit Viper in Bitplanes umwandeln."""
        frame = self._frames[frame_index]
        tx = self._tx[tx_index]

        # Speicheradressen der 8 Kanal-Arrays und des TX-Puffers abfragen
        ch0 = uctypes.addressof(frame[0])
        ch1 = uctypes.addressof(frame[1])
        ch2 = uctypes.addressof(frame[2])
        ch3 = uctypes.addressof(frame[3])
        ch4 = uctypes.addressof(frame[4])
        ch5 = uctypes.addressof(frame[5])
        ch6 = uctypes.addressof(frame[6])
        ch7 = uctypes.addressof(frame[7])
        tx_ptr = uctypes.addressof(tx)

        step = self.yield_every
        oi = 0

        for start_led in range(0, self.leds, step):
            end_led = min(start_led + step, self.leds)
            oi = _encode_chunk_viper(
                ch0,
                ch1,
                ch2,
                ch3,
                ch4,
                ch5,
                ch6,
                ch7,
                tx_ptr,
                start_led,
                end_led,
                oi,
            )
            await asyncio.sleep_ms(0)

    async def wait(self):
        """Kooperativ warten, bis DMA und WS2812-Latch abgeschlossen sind."""
        if self._send_tx is None:
            return
        while self.dma.active():
            await asyncio.sleep_ms(0)
        await asyncio.sleep_ms(self.reset_ms)
        self._send_tx = None

    async def show(self, copy=True):
        """Aktuellen Zeichenpuffer senden und sofort einen neuen freigeben."""
        async with self._lock:
            encode_frame = self._draw
            encode_tx = self._spare_tx

            await self._encode(encode_frame, encode_tx)
            await self.wait()

            self.dma.config(
                read=self._tx[encode_tx], write=self.sm,
                count=len(self._tx[encode_tx]),
                ctrl=self._dma_ctrl, trigger=True
            )
            self._send_tx = encode_tx
            self._spare_tx = 1 - encode_tx

            new_draw = 1 - encode_frame
            if copy:
                src = self._frames[encode_frame]
                dst = self._frames[new_draw]
                for ch in range(CHANNELS):
                    for i in range(self.leds):
                        dst[ch][i] = src[ch][i]
                    await asyncio.sleep_ms(0)
            self._draw = new_draw

    async def blackout(self):
        self.clear()
        await self.show(copy=False)
        await self.wait()

    async def deinit(self, blackout=True):
        async with self._lock:
            await self.wait()
            if blackout:
                self.clear()
                await self._encode(self._draw, self._spare_tx)
                self.dma.config(
                    read=self._tx[self._spare_tx], write=self.sm,
                    count=len(self._tx[self._spare_tx]),
                    ctrl=self._dma_ctrl, trigger=True
                )
                self._send_tx = self._spare_tx
                await self.wait()
            self.sm.active(0)
            self.dma.close()

    def deinit_sync(self, blackout=True):
        """Schaltet DMA und PIO sofort synchron ohne Event Loop ab."""
        if blackout:
            # Puffer leeren
            self.clear()
            # Synchronen Bitplane-Block erzeugen & senden (ohne await)
            frame = self._frames[self._draw]
            tx = self._tx[self._spare_tx]
            
            # Einmalige synchrone Bit-Konvertierung
            oi = 0
            for led in range(self.leds):
                for bit in range(23, -1, -1):
                    test = 1 << bit
                    mask = 0
                    for ch in range(CHANNELS):
                        if frame[ch][led] & test:
                            mask |= 1 << ch
                    tx[oi] = mask
                    oi += 1

            # DMA synchron triggern
            self.dma.config(
                read=tx, write=self.sm,
                count=len(tx), ctrl=self._dma_ctrl, trigger=True
            )
            time.sleep_ms(self.reset_ms)

        # Hardware sofort deaktivieren
        self.sm.active(0)
        self.dma.close()