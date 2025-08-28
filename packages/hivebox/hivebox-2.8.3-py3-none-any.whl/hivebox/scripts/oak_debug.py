import time


def main():
    import depthai as dai
    checked = set()

    while True:
        infos = []

        while len(infos) == 0:
            infos = list(filter(
                lambda info: info.getMxId() not in checked,
                dai.XLinkConnection.getAllConnectedDevices()
            ))

            if len(infos) == 0:
                print("No new devices found, retrying in 2 seconds...")
                time.sleep(2)

        print("Available new devices:")
        for i, info in enumerate(infos):
            print(f"[{i}] {info.getMxId()} [{info.state.name}]")

        for i, info in enumerate(infos):
            print(f"Connecting to #{i}: {info.getMxId()}")
            with dai.Device(info) as device:
                print('Connected cameras:')
                for camera in device.getConnectedCameraFeatures():
                    print("-", camera)
                print('Usb speed:', device.getUsbSpeed().name)
                if device.getBootloaderVersion() is not None:
                    print('Bootloader version:', device.getBootloaderVersion())
                print('Device name:', device.getDeviceName())
                print('Product name:', device.getProductName())
                print('MXID:', device.getMxId())
                checked.add(info.getMxId())


if __name__ == '__main__':
    main()