import bluetooth
import struct
import time
from micropython import const

# BLE advertising parameters
_ADV_TYPE_FLAGS = const(0x01)
_ADV_TYPE_NAME = const(0x09)


def advertise_ble(name):
    ble = bluetooth.BLE()
    ble.active(True)

    # Our BLE advertising data must be a bytes object. We combine flags and the device name.
    adv_data = bytes()

    # Adding Flags to Advertising Data
    adv_data += struct.pack("BB", 2, _ADV_TYPE_FLAGS)
    adv_data += struct.pack("B", 0x06)  # General discovery, BR/EDR not supported

    # Adding Device Name to Advertising Data
    name_bytes = name.encode('utf-8')
    adv_data += struct.pack("BB", len(name_bytes) + 1, _ADV_TYPE_NAME)
    adv_data += name_bytes

    # Start advertising
    ble.gap_advertise(150000, adv_data)  # Advertising interval: 15 ms, meaning 150,000 microseconds
    print("advertising...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Stop advertising when the script is interrupted
        ble.gap_advertise(None)
        print("stopped advertising")


if __name__ == "__main__":
    device_name = "ESP32_BLE"
    advertise_ble(device_name)

