import asyncio
from sys import platform
import logging
from bleak import BleakClient, BleakScanner

UUIDS = {
    "target_temp": "fc540003-236c-4c94-8fa9-944a3e5353fa",
    "led_color": "fc540014-236c-4c94-8fa9-944a3e5353fa",
    "current_temp": "fc540002-236c-4c94-8fa9-944a3e5353fa",
    "current_bat": "fc540007-236c-4c94-8fa9-944a3e5353fa",
}

logging.basicConfig(format="%(asctime)s %(message)s ", level=logging.INFO)


class Mug:
    def __init__(self, unit: str, coffeeTemp=5500, teaTemp=5900):
        self.unit = unit
        self.coffeeTemp = coffeeTemp
        self.teaTemp = teaTemp
        self.keepConnectionAlive = True
        self.searchForDevice = True
        self.current_temp = None

    async def connectToMug(self):
        try:
            print("Searching..", end="")
            # self.connectionChanged.emit(False)
            # Search for the mug as long til we find it.
            while self.searchForDevice:
                print(".", end="")
                scanner = BleakScanner()
                # scanner.register_detection_callback(detection_callback)
                await scanner.start()
                await asyncio.sleep(5.0)
                await scanner.stop()
                devices = await scanner.get_discovered_devices()
                for device in devices:
                    if device.name == "Ember Ceramic Mug":
                        # We found the ember mug!
                        print(device.address)
                        print(device.name)
                        print(device.details)
                        # try to connect to the mug
                        async with BleakClient(device) as client:
                            self.connectedClient = client
                            self.isConnected = await client.is_connected()
                            print("Connected: {0}".format(self.isConnected))
                            if platform != "darwin":
                                # Avoid this on mac, since CoreBluetooth doesnt support pairing.
                                y = await client.pair()
                                print("Paired: {0}".format(y))
                            # Set connection parameters and use signal to send it to the UI.
                            self.keepConnectionAlive = True
                            # self.connectionChanged.emit(True)
                            # await self.fetchLEDColor(self)
                            # Auto update Temp and Battery
                            # self.timer = QTimer()

                            # Execute function every 3 seconds
                            # TO-DO: Must decouple the calling of this function from the connection
                            # while self.keepConnectionAlive:
                            # We stay in here to keep the client alive
                            # once keepConnectionAlive is set to false
                            # the client will also disconnect automatically
                            while self.keepConnectionAlive == True:
                                await asyncio.sleep(1)
                            # await asyncio.sleep(5)
                            # print(".")
                            # await asyncio.gather(
                            #     self.getCurrentBattery(),
                            #     self.getCurrentTemp(),
                            #     self.getTargetTemp(),
                            # )
                            # await asyncio.sleep(3)
                            return
        except Exception as exc:
            # self.connectionChanged.emit(False)
            print("Error: {}".format(exc))

    # # function to get the current temp from the async loop.
    # def fetchCurrentTemperature(self):
    #     if self.connectedClient is not None:
    #         asyncio.ensure_future(self.getCurrentTemp())

    # # function to get the current charge percentage from the async loop.
    # def fetchCurrentBattery(self):
    #     if self.connectedClient is not None:
    #         asyncio.ensure_future(self.getCurrentBattery())

    # Get the current temp
    async def getCurrentTemp(self):
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
            self.current_temp = CurrentDegree
            logging.info("Temp: %s", self.current_temp)
            # await asyncio.sleep(3)
            # print(CurrentDegree)
            # Send UI Signal
            # self.getDegree.emit(float(CurrentDegree))
        else:
            # self.connectionChanged.emit(False)
            print("not connected")

    async def getCurrentBattery(self):
        if await self.connectedClient.is_connected():
            currentBat = await self.connectedClient.read_gatt_char(UUIDS["current_bat"])
            logging.info("Battery: %s", float(currentBat[0]))
            # await asyncio.sleep(3)
            # Send UI Signal
            # self.getBattery.emit(float(currentBat[0]))
        else:
            # self.connectionChanged.emit(False)
            print("not connected")

    async def getTargetTemp(self):
        if await self.connectedClient.is_connected():
            currentTemp = await self.connectedClient.read_gatt_char(
                UUIDS["target_temp"]
            )
            TargetDegree = (
                float(int.from_bytes(currentTemp, byteorder="little", signed=False))
                * 0.01
            )
            if self.unit == "F":
                TargetDegree = (TargetDegree * 1.8) + 32
            TargetDegree = round(TargetDegree, 1)
            logging.info("Temp: %s", TargetDegree)
        else:
            # self.connectionChanged.emit(False)
            print("not connected")

    async def update_values(self):
        while True:
            try:
                await self.getCurrentBattery()
                await self.getCurrentTemp()
                await self.getTargetTemp()
                await asyncio.sleep(3)
            except:
                print("Not connected, trying again in 10 seconds")
                await asyncio.sleep(10)

    async def setToTemp(self, temp: float):
        while True:
            try:
                print("Trying")
                if await self.connectedClient.is_connected():
                    if self.unit == "F":
                        temp = (temp - 32) / 1.8
                    print(temp)
                    print("try setting the target temperature")
                    convert_temp = int(temp * 1000)
                    print(convert_temp)
                    newtarget = bytearray(convert_temp.to_bytes(2, "little"))
                    await self.connectedClient.write_gatt_char(
                        UUIDS["target_temp"], newtarget, False
                    )
                    return
                    # Send UI Signal
                    # self.getDegree.emit(float(temp * 0.01))

                else:
                    # self.connectionChanged.emit(False)
                    print("not connected")
            except Exception as err:
                print("sleep")
                print(err)
                await asyncio.sleep(5)
