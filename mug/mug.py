from Bleak import BleakScanner, BleakClient

UUIDS = {
    "target_temp": "fc540003-236c-4c94-8fa9-944a3e5353fa",
    "led_color": "fc540014-236c-4c94-8fa9-944a3e5353fa",
    "current_temp": "fc540002-236c-4c94-8fa9-944a3e5353fa",
    "current_bat": "fc540007-236c-4c94-8fa9-944a3e5353fa",
}


class Mug:
    def __init__(self, unit: str, coffeeTemp=5500, teaTemp=5900):
        self.unit = unit
        self.coffeeTemp = coffeeTemp
        self.teaTemp = teaTemp
        self.keepConnectionAlive = True
        self.searchForDevice = True
        self.connectedClient = BleakClient(None)

    # function to get the current temp from the async loop.
    def fetchCurrentTemperature(self):
        if self.connectedClient is not None:
            asyncio.ensure_future(self.getCurrentTemp(self))

    # Get the current temp
    async def getCurrentTemp(self):
        try:
            if await self.connectedClient.is_connected():
                currentTemp = await self.connectedClient.read_gatt_char(
                    UUIDS["current_temp"]
                )
                CurrentDegree = (
                    float(int.from_bytes(currentTemp, byteorder="little", signed=False))
                    * 0.01
                )
                # Unit conversion
                if self.unit == "F":
                    CurrentDegree = (CurrentDegree * 1.8) + 32
                CurrentDegree = round(CurrentDegree, 1)
                print(CurrentDegree)
                # Send UI Signal
                self.getDegree.emit(float(CurrentDegree))
            else:
                self.connectionChanged.emit(False)
                print("not connected")
        except Exception as exc:
            print("Error: {}".format(exc))

    @staticmethod
    async def setLEDColor(self, color):
        if await self.connectedClient.is_connected():
            await self.connectedClient.write_gatt_char(UUIDS["led_color"], color, False)
            print("Changed Color to {0}".format(color))
        else:
            self.connectionChanged.emit(False)
            print("not connected")
