# main.py
from array import array
import uasyncio as asyncio
from libs.ws2812_parallel_async import WS2812ParallelAsync

import machine
machine.freq(250_000_000)  # Verdoppelt die Rechenleistung der CPU


LEDS = 178

@micropython.viper
def update_buffers_fast(buffers: object, leds: int, pos: int):
    # buffers ist eine Liste von Arrays
    for ch in range(8):
        buf_ptr = ptr32(buffers[ch])
        
        # Farbe berechnen
        color_val = 0x550000
        
        for i in range(leds):
            idx = (pos + i)
            if idx >= leds:
                idx -= leds  # Ersatz für teures Modulo (%)
                
            if i < 3:
                buf_ptr[idx] = color_val
            else:
                buf_ptr[idx] = 0x000003


async def animate_arrays(leds):
    ch_buffers = [array("I", [0] * LEDS) for _ in range(8)]
    pos = 0
    
    while True:
        # Puffer blitzschnell in C-Speed füllen
        update_buffers_fast(ch_buffers, LEDS, pos)

        leds.set_all_channels(ch_buffers)
        await leds.show(copy=False)

        if pos < 170:
            pos = pos + 1
        else:
            pos = 0
        await asyncio.sleep_ms(10)


async def main():
    leds = WS2812ParallelAsync(leds=LEDS, first_pin=2, brightness=255, yield_every=LEDS, reset_us=300)
    try:
        await animate_arrays(leds)
    finally:
        await leds.deinit()

asyncio.run(main())
