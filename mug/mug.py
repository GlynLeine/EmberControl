import asyncio
from bleak import BleakScanner, BleakClient
from sys import platform
import log.logger as log

DEVICE_NAME = "Ember Ceramic Mug"

UUIDS = {
    "target_temp": "fc540003-236c-4c94-8fa9-944a3e5353fa", 
    "led_color": "fc540014-236c-4c94-8fa9-944a3e5353fa", 
    "current_temp": "fc540002-236c-4c94-8fa9-944a3e5353fa", 
    "current_bat": "fc540007-236c-4c94-8fa9-944a3e5353fa", 
}

class Mug: 
    def __init__(self, useCelcius: bool = True, coffeeTemp = 5500, teaTemp = 5900):
        self.useCelcius = useCelcius
        self.coffeeTemp = coffeeTemp
        self.teaTemp = teaTemp
        self.keepConnectionAlive = True
        self.searchForDevice = True
        self.current_temp = None
        self.connectedClient = BleakClient(None)
        self.scanner = None
        self.scanningComplete = asyncio.Event()
        self.connecting = asyncio.Lock()
    
    def isConnected(self) -> bool:
        return self.connectedClient is not None and self.connectedClient.is_connected and self.connectedClient.services is not None

    async def getCurrentLEDColor(self): 
        """Get the current LED color.

        The value of the current color is stored as in UUIDS["led_color"] as array.

        Returns:
            The current color as bytearray.
        """
        try:
            if  self.isConnected():
                c = await self.connectedClient.read_gatt_char(UUIDS["led_color"]) 
                return c        
            else:
                print("not connected")
        except Exception as exc:
            print("Error: {}".format(exc))

        return bytearray([0, 0, 0, 0])
            
    async def getTargetTemp(self):
        """Get the current target temperature value.

        The value of the target temperature is given as bytes and needs to be converted 
        to a unsigned integer in little endian form. Afterwards it will be converted 
        to a float value with two decimal places.

        Returns:
            the target temperature as float.
        """
        try:
            if  self.isConnected():
                currentTargetTemp = await self.connectedClient.read_gatt_char(UUIDS["target_temp"])
                targetDegree = float(int.from_bytes(currentTargetTemp, byteorder = 'little', signed = False)) * 0.01
                return targetDegree
            else:
                print("not connected")        
        except Exception as exc:
            print("Error: {}".format(exc))

        return 0.0
            
    async def getCurrentBattery(self): 
        """Get the current battery level.

        The value of the current battery level is given after requesting UUIDS["current_bat"]. 
        It will be converted to a float before returning. 

        Returns:
            the current battery level as float.
        """
        try:
            if  self.isConnected():
                curBat = await self.connectedClient.read_gatt_char(UUIDS["current_bat"])
                currentBattery = float(curBat[0])
                currentlyCharging = bool(curBat[1])
                log.printLog("Current Battery: {0}% Status: {1}".format(currentBattery, "Charging" if currentlyCharging else "Not charging"))
                return currentBattery, currentlyCharging
            else:
                print("not connected")        
        except Exception as exc:
            print("Error: {}".format(exc))

        return 0.0, bool(False)

    async def getCurrentTemp(self):
        """Get the current temperature value.

        The value of the current temperature is given as bytes and needs to be converted 
        to a unsigned integer in little endian form. Afterwards it will be converted 
        to a float value with two decimal places.

        Returns:
            the current temperature as float.
        """
        try:
            if  self.isConnected():
                currentTemp = await self.connectedClient.read_gatt_char(
                    UUIDS["current_temp"]
                )
                currentDegree = (
                    float(int.from_bytes(currentTemp, byteorder = "little", signed = False))
                    * 0.01
                )
                # Unit conversion
                if not self.useCelcius:
                    currentTemperature = (currentDegree * 1.8) + 32
                else: 
                    currentTemperature = round(currentDegree, 1)
                log.printLog("Current Temp: {0}".format(currentTemperature))
                return currentTemperature
            else:
                print("not connected")
        except Exception as exc:
            print("Error: {}".format(exc))

        return 0.0

    async def setLEDColor(self, color):
        """Sets the LED Color.

        Args:
        color (bytearray): the LED color as bytearray

        Returns:
            no value
        """
        try:
            if  self.isConnected():
                await self.connectedClient.write_gatt_char(UUIDS["led_color"], color, False)
                print("Changed Color to {0}".format(color))
            else:
                print("not connected")
        except Exception as exc:
            print("Error: {}".format(exc))
            
    async def setTargetTemp(self, temp): 
        """Sets the target temperature.

        Args:
        temp (float): the target temperature.

        Returns:
            no value
        """
        try:
            if  self.isConnected():
                newtarget = temp.to_bytes(2, 'little')
                await self.connectedClient.write_gatt_char(UUIDS["target_temp"], newtarget, False)
            else:
                print("not connected")
        except Exception as exc:
            print("Error: {}".format(exc))

    async def detectionCallback(self, device, advertisementData):
        if self.scanningComplete.is_set():
            return
        
        if advertisementData.local_name is None:
            return
            
        if device.name == DEVICE_NAME:
            # We found the ember mug!
            # try to connect to the mug
            await self.connecting.acquire()

            if self.isConnected():
                self.connecting.release()
                return
            
            log.printLog("Connecting to: \"{0}\"".format(advertisementData.local_name))
            log.nextLine()

            async with BleakClient(device) as client:
                if not client.is_connected:
                    log.prevLine()
                    log.printLog("Failed to connect.")
                    log.nextLine()
                    self.connecting.release()
                    return
                
                if platform != "darwin":
                    # Avoid this on mac, since CoreBluetooth doesnt support pairing.
                    await client.pair()
                
                log.prevLine()
                log.printLog("Connected to: \"{0}\"".format(advertisementData.local_name))
                log.nextLine()

                self.connectedClient = client                    
                # Set connection parameters and use signal to send it to the UI.
                self.keepConnectionAlive = True
                
                log.nextLine()
                self.scanningComplete.set()
                self.connecting.release()
                
                # connected, now keeping the connecting alive.
                while self.keepConnectionAlive:
                    # We stay in here to keep the client alive
                    # once keepConnectionAlive is set to false
                    # the client will also disconnect automatically
                    await asyncio.sleep(2)
                    self.keepConnectionAlive = self.isConnected()

    async def startScan(self):
        self.scanner = BleakScanner(self.detectionCallback)
        await self.scanner.start()
        
    async def connect(self):
        """Tries to connect to the first Ember Mug it finds.

        Returns:
            no value
        """
        try:
            # Search for the mug
            while self.searchForDevice:
                self.scanningComplete.clear()
                # log.clearConsole()

                asyncio.create_task(self.startScan())

                dots = 0
                while not self.scanningComplete.is_set():
                    log.printLog(("" if self.connecting.locked() else "Searching") + "." * dots)
                    
                    dots = dots + 1
                    if dots == 4:
                        dots = 0

                    await asyncio.sleep(1)
                
                await self.scanningComplete.wait()
                await self.scanner.stop()

                log.clearLine()
                while self.keepConnectionAlive:
                    await asyncio.sleep(2)

        except Exception as exc:
            # self.connectionChanged.emit(False)
            print('Error: {}'.format(exc))
