from Bleak import BleakScanner, BleakClient 
class Mug:
    def __init__(self,unit: str,coffeeTemp=5500: int, teaTemp=5900: int):
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

    #Get the current temp
    async def getCurrentTemp(self):
        try:
            if await self.connectedClient.is_connected():
                currentTemp = await self.connectedClient.read_gatt_char(CURRENT_TEMP)
                CurrentDegree = float(int.from_bytes(currentTemp, byteorder='little', signed=False)) * 0.01
                CurrentDegree = round(CurrentDegree, 1)
                print(CurrentDegree)
                # Send UI Signal
                self.getDegree.emit(float(CurrentDegree))
            else:
                self.connectionChanged.emit(False)
                print("not connected")
        except Exception as exc:
            print('Error: {}'.format(exc))


