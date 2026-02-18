from DeviceGateway import DeviceGateway
from time import sleep
from random import randrange as rand

if __name__ == "__main__":
    gateway = DeviceGateway("config.json")
    gateway.Start()
    while True:
        try:
            reading = {
                "db": rand(40, 100)
            }
            print("Sending reading: ", reading)
            gateway.send_reading(reading)
            sleep(30)
        except Exception as e:
            print("Error while sending reading: ", e)
            sleep(30)
            gateway.Stop()