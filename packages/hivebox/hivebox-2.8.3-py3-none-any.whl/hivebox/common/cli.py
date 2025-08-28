from __future__ import annotations

import argparse
import os
import platform
import subprocess
from pathlib import Path
from typing import Union, List
import shlex
from subprocess import run, PIPE, DEVNULL, CompletedProcess
import depthai as dai


class PrintColors:
    HEADER="\033[95m"
    BLUE="\033[94m"
    GREEN="\033[92m"
    RED="\033[91m"
    WARNING="\033[1;5;31m"
    FAIL="\033[91m"
    ENDC="\033[0m"
    BOLD="\033[1m"
    UNDERLINE="\033[4m"
    BLACK_BG_RED="\033[1;31;40m"
    BLACK_BG_GREEN="\033[1;32;40m"
    BLACK_BG_BLUE="\033[1;34;40m"


def cli_print(msg, print_color=PrintColors.GREEN):
    print("{0}{1}{2}".format(print_color, msg, PrintColors.ENDC))


def cli_run(cmd: Union[str, List], stdout: bool = False, label: str = None, silent: bool = False, workdir: Union[Path, str] = None, env: dict = None) -> CompletedProcess[str]:
    if label is None:
        label = " ".join(cmd) if isinstance(cmd, list) else cmd
    cli_print(f"Executing: \"{label}\"")
    result = run(
        cmd if isinstance(cmd, list) else shlex.split(cmd),
        stdout=PIPE if stdout else DEVNULL,
        stderr=PIPE,
        universal_newlines=True,
        cwd=str(Path(workdir).absolute()) if workdir else None,
        env={**os.environ, **(env or {})},
    )
    if result.returncode != 0 and not silent:
        cli_print(f"Error while executing \"{label}\": {result.stderr}", PrintColors.FAIL)
        raise SystemExit(1)
    return result


def _check_range(min_v, max_v):
    def check(raw_value):
        value = int(raw_value)
        if min_v <= value <= max_v:
            return value
        else:
            raise argparse.ArgumentTypeError(
                "{} is an invalid int value, must be in range {}..{}".format(raw_value, min_v, max_v)
            )

    return check


class ConfigWrapper:
    def __init__(self):
        parser = argparse.ArgumentParser()

        parser.add_argument('-dd', '--disableDepth', action="store_true", help="Disable depth information")
        parser.add_argument('--sharpness', default=None, type=_check_range(0, 4),
                            help="Sets ColorCamera's sharpness")
        parser.add_argument('--lumaDenoise', default=None, type=_check_range(0, 4),
                            help="Sets ColorCamera's Luma denoise")
        parser.add_argument('--chromaDenoise', default=None, type=_check_range(0, 4),
                            help="Sets ColorCamera's Chroma denoise")
        parser.add_argument('--manualFocus', default=None, type=_check_range(0, 255),
                            help="Specify a Lens Position between 0 and 255 to use manual focus. Otherwise, auto-focus is used by default.")
        parser.add_argument("--cameraExposure", default=None, type=int, help="Specify camera saturation")
        parser.add_argument("--cameraSensitivity", default=None, type=int, help="Specify camera sensitivity")
        parser.add_argument("--cameraSaturation", default=None, type=int, help="Specify image saturation")
        parser.add_argument("--cameraContrast", default=None, type=int, help="Specify image contrast")
        parser.add_argument("--cameraBrightness", default=None, type=int, help="Specify image brightness")
        parser.add_argument("--cameraSharpness", default=None, type=int, help="Specify image sharpness")
        parser.add_argument('-dlrc', '--disableStereoLrCheck', action="store_false", dest="stereoLrCheck",
                            help="Disable stereo 'Left-Right check' feature.")
        parser.add_argument('-ext', '--extendedDisparity', action="store_true",
                            help="Enable stereo 'Extended Disparity' feature.")
        parser.add_argument('-sub', '--subpixel', action="store_true",
                            help="Enable stereo 'Subpixel' feature.")
        parser.add_argument('--debug', action="store_true",
                            help="Enables debug mode. Capability to connect to already BOOTED devices and also implicitly disables version check")

        self.args = parser.parse_args()

    @property
    def debug(self):
        return self.args.debug

    @property
    def max_disparity(self):
        max_disparity = 95
        if self.args.extendedDisparity:
            max_disparity *= 2
        if self.args.subpixel:
            max_disparity *= 32

        return max_disparity

    @staticmethod
    def ir_enabled(device):
        try:
            drivers = device.getIrDrivers()
            return len(drivers) > 0
        except RuntimeError:
            return False

    @staticmethod
    def rgb_resolution_shape(res: dai.ColorCameraProperties.SensorResolution) -> tuple[int, int]:
        if res == dai.ColorCameraProperties.SensorResolution.THE_720_P:
            return 1280, 720
        elif res == dai.ColorCameraProperties.SensorResolution.THE_800_P:
            return 1280, 800
        elif res == dai.ColorCameraProperties.SensorResolution.THE_1080_P:
            return 1920, 1080
        elif res == dai.ColorCameraProperties.SensorResolution.THE_4_K:
            return 3840, 2160
        elif res == dai.ColorCameraProperties.SensorResolution.THE_12_MP:
            return 4056, 3040
        elif res == dai.ColorCameraProperties.SensorResolution.THE_13_MP:
            return 4208, 3120
        else:
            raise Exception('Resolution not supported!')

    def get_resolution(self, device):
        cams = device.getConnectedCameras()

        sensorNames = device.getCameraSensorNames()
        if dai.CameraBoardSocket.RGB in cams:
            name = sensorNames[dai.CameraBoardSocket.RGB]
            if name == 'OV9782':
                res = dai.ColorCameraProperties.SensorResolution.THE_800_P
                cli_print(f'Camera sensor: {name}; resolution: {self.rgb_resolution_shape(res)}', PrintColors.RED)
                return res
            else:
                res = dai.ColorCameraProperties.SensorResolution.THE_1080_P
                cli_print(f'Camera sensor: {name}; resolution: {self.rgb_resolution_shape(res)}', PrintColors.RED)
                return res

    @staticmethod
    def is_usb2(device):
        device_info = device.getDeviceInfo()
        if device_info.protocol != dai.XLinkProtocol.X_LINK_USB_VSC:
            cli_print("Enabling low-bandwidth mode due to connection mode... (protocol: {})".format(device_info.protocol),
                      PrintColors.RED)
            return True
        if device.getUsbSpeed() not in [dai.UsbSpeed.SUPER, dai.UsbSpeed.SUPER_PLUS]:
            cli_print("Enabling low-bandwidth mode due to low USB speed... (speed: {})".format(device.getUsbSpeed()),
                      PrintColors.RED)
            return True

        return False

    @staticmethod
    def check_udev_rules():
        if platform.system() == 'Linux':
            ret = subprocess.call(['grep', '-irn', 'ATTRS{idVendor}=="03e7"', '/etc/udev/rules.d'],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if ret != 0:
                cli_print("WARNING: Usb rules not found", PrintColors.WARNING)
                cli_print("""
Run the following commands to set USB rules:

$ echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="03e7", MODE="0666"' | sudo tee /etc/udev/rules.d/80-movidius.rules
$ sudo udevadm control --reload-rules && sudo udevadm trigger

After executing these commands, disconnect and reconnect USB cable to your OAK device""", PrintColors.RED)
                raise SystemExit(1)

    @staticmethod
    def is_low_capabilities():
        return platform.machine().startswith("arm") or platform.machine().startswith("aarch")
