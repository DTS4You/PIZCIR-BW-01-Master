# main_ws2812-05.py
from array import array
import uasyncio as asyncio                                    # type: ignore
from libs.ws2812_parallel_async import WS2812ParallelAsync

import machine                                                # type: ignore
machine.freq(250_000_000)  # Verdoppelt die Rechenleistung der CPU

LEDS = 178

@micropython.viper                                            # type: ignore
def copy_pattern_fast(buf_ptr: ptr32, src_ptr: ptr32, leds: int, pattern_len: int, pos: int, bg_color: int, state: int):
    # 1. Zuerst den gesamten Puffer mit der Hintergrundfarbe füllen
    if state == 0:
        for i in range(leds):
            buf_ptr[i] = 0x000000  # Hintergrundfarbe (schwarz)
    else:
        for i in range(leds):
            buf_ptr[i] = bg_color  # Hintergrundfarbe (z.B. dunkelblau)

        for i in range(leds):
            buf_ptr[i] = bg_color
            
        # 2. Das Quell-Muster an Position 'pos' in den Puffer kopieren
        for i in range(pattern_len):
            idx = pos + i
            if idx >= leds:
                idx -= leds  # Wrap-around für den Ringpuffer (Modulo-Ersatz)
                
            buf_ptr[idx] = src_ptr[i]


async def animate_arrays(leds):
    ch_buffers = [array("I", [0] * LEDS) for _ in range(8)]
    
    # Dein Quell-Array mit den passenden Farbwerten
    source_pattern = array("I", [0x050000, 0x200000, 0x800000, 0xAA0000, 0xFF0000, 0xAA0000, 0x800000, 0x200000, 0x050000])
    pattern_len = len(source_pattern)
    bg_color = 0x000003  # Hintergrund-Farbwert
    state = 0
    pos = 0
    
    while True:
        # Für alle 8 Kanäle das Muster anwenden
        for ch in range(8):
            if ch ==2 or ch == 3:
                state = 0
            else:
                state = 1
            buf_ptr = ch_buffers[ch]  # Hier kein ptr32() nötig!
            copy_pattern_fast(buf_ptr, source_pattern, LEDS, pattern_len, pos, bg_color, state)

        leds.set_all_channels(ch_buffers)
        await leds.show(copy=False)

        pos += 1
        if pos >= LEDS:
            pos = 0
            
        await asyncio.sleep_ms(10)


async def main():
    leds = WS2812ParallelAsync(leds=LEDS, first_pin=2, brightness=255, yield_every=32, reset_us=300)
    try:
        await animate_arrays(leds)
    finally:
        await leds.deinit()

asyncio.run(main())

