import asyncio
import time
from machine import Pin


class ParallelBus:

    def __init__(
        self, data_pins=[10, 11, 12, 13], pin_strobe_high=14, pin_strobe_low=15
    ):
        self.data_pin_nums = data_pins
        self.pin_num_strobe_high = pin_strobe_high
        self.pin_num_strobe_low = pin_strobe_low

        # Pins initialisieren (standardmäßig Empfangsmodus mit Pull-Up)
        self._init_rx_pins()

    def _init_rx_pins(self):
        """Schaltet alle Pins als Eingänge mit Pull-Up (Ruhezustand: HIGH / 1)."""
        self.pins_data = [Pin(p, Pin.IN, Pin.PULL_UP) for p in self.data_pin_nums]
        self.strobe_high = Pin(self.pin_num_strobe_high, Pin.IN, Pin.PULL_UP)
        self.strobe_low = Pin(self.pin_num_strobe_low, Pin.IN, Pin.PULL_UP)

    def _init_tx_pins(self):
        """Schaltet Pins auf Ausgang für das Senden."""
        for p in self.pins_data:
            p.init(Pin.OUT)
        self.strobe_high.init(Pin.OUT, value=1)
        self.strobe_low.init(Pin.OUT, value=1)

    def _read_nibble(self):
        """Liest 4 Bit von den Datenleitungen."""
        val = 0
        for i in range(4):
            val |= self.pins_data[i].value() << i
        return val

    async def _wait_strobe(self, pin, timeout_ms=100):
        """Wartet auf einen LOW-Puls (0) mit Timeout."""
        start = time.ticks_ms()
        while pin.value() == 1:
            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                return False
            await asyncio.sleep_ms(2)
        return True

    async def read_byte_non_blocking(self):
        """Liest ein Byte über LOW-Strobe-Pulse ein. Gibt None bei Timeout zurück."""
        # 1. High-Nibble (Warten auf LOW an GP14)
        if not await self._wait_strobe(self.strobe_high, timeout_ms=100):
            return None
        high = self._read_nibble()
        while self.strobe_high.value() == 0:
            await asyncio.sleep_ms(1)

        # 2. Low-Nibble (Warten auf LOW an GP15)
        if not await self._wait_strobe(self.strobe_low, timeout_ms=100):
            return None
        low = self._read_nibble()
        while self.strobe_low.value() == 0:
            await asyncio.sleep_ms(1)

        return (high << 4) | low

    async def listen_loop(self, on_message_callback):
        """Laufender Hintergrund-Task zum Empfangen von Texten (Ende bei '\\r')."""
        buffer = bytearray()
        while True:
            byte = await self.read_byte_non_blocking()
            if byte is not None:
                if byte == 13:  # ASCII 13 = '\r' (Carriage Return)
                    try:
                        text = buffer.decode("utf-8")
                    except (UnicodeError, ValueError):
                        # Fallback für fehlerhafte Bytes: ASCII-Interpretation / Ersetzen ungültiger Zeichen
                        text = "".join(chr(b) if 32 <= b <= 126 else "?" for b in buffer)

                    buffer = bytearray()
                    on_message_callback(text)
                else:
                    buffer.append(byte)
            await asyncio.sleep_ms(5)

    async def _send_nibble(self, nibble, strobe_pin):
        """Sendet 4 Bit mit 2 ms LOW-Puls."""
        for i in range(4):
            self.pins_data[i].value((nibble >> i) & 1)

        strobe_pin.value(0)
        await asyncio.sleep_ms(5)  # Impulsdauer
        strobe_pin.value(1)
        await asyncio.sleep_ms(8)  # Pause vor nächstem Nibble

    async def send_text(self, text):
        """Sendet einen String inkl. '\\r' am Ende."""
        self._init_tx_pins()

        data = text.encode("utf-8") + b"\r"
        for byte in data:
            await self._send_nibble((byte >> 4) & 0x0F, self.strobe_high)
            await self._send_nibble(byte & 0x0F, self.strobe_low)

        self._init_rx_pins()

