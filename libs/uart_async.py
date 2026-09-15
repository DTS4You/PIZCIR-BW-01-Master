import uasyncio as asyncio
from machine import UART, Pin

class AsyncUART:
    def __init__(self, uart_id=0, baudrate=115200, tx_pin=0, rx_pin=1, rxbuf=256, on_receive=None):
        """
        Initialisiert die asynchrone UART-Schnittstelle.
        :param on_receive: Eine Callback-Funktion, die aufgerufen wird, wenn Daten empfangen werden.
        """
        self.uart = UART(uart_id, baudrate=baudrate, tx=Pin(tx_pin), rx=Pin(rx_pin), rxbuf=rxbuf)
        self.reader = asyncio.StreamReader(self.uart)
        self.on_receive = on_receive
        self._task = None

    def start(self):
        """Startet den Empfangs-Loop im Hintergrund."""
        if self._task is None:
            self._task = asyncio.create_task(self._listen_loop())

    async def _listen_loop(self):
        """Hintergrund-Task zum Abfangen eingehender Zeilen."""
        while True:
            try:
                line = await self.reader.readline()
                if line:
                    decoded = line.decode('utf-8', 'ignore').strip()
                    if self.on_receive:
                        self.on_receive(decoded)
            except Exception as e:
                print(f"UART Fehler: {e}")

    def write(self, text):
        """Sendet einen String oder Bytes über die serielle Schnittstelle."""
        if isinstance(text, str):
            text = text.encode('utf-8')
        return self.uart.write(text)

    def send_line(self, text):
        """Hilfsfunktion: Sendet Text mit automatischem Zeilenumbruch (CRLF)."""
        if not text.endswith('\r\n'):
            text = text.rstrip('\r\n') + '\r\n'
        return self.write(text)

