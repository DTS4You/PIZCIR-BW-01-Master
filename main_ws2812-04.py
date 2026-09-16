###############################################################################
# Version 1.00
# Getestet und i.O.
###############################################################################
import uasyncio as asyncio
from libs.ws2812_parallel_async import WS2812ParallelAsync

COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
    (0, 255, 255), (255, 0, 255), (255, 128, 0), (255, 255, 255),
]


async def main():
    leds = WS2812ParallelAsync(
        leds=200,
        first_pin=2,
        brightness=32,
        sm_id=0,
        yield_every=8,
        reset_us=300,
    )

    pos = 0

    while(True):
        leds.clear()

        for s in range(8):
            for i in range(8):
                leds.pixel(s,pos + i,COLORS[s])
        
        await leds.show(copy=False)

        if pos < 20:
            pos = pos + 1
        else:
            pos = 0

        await asyncio.sleep_ms(20)



asyncio.run(main())
