import time
import cv2
from hivebox.common.cli import cli_print, PrintColors
import depthai as dai
import numpy as np


def wait_for_device(mxid, timeout=30, interval=0.1):
    start = time.time()
    while time.time() - start < timeout:
        devices = list(map(lambda info: info.getMxId(), dai.XLinkConnection.getAllConnectedDevices()))
        if mxid in devices:
            return True
        else:
            time.sleep(interval)
    else:
        cli_print(f"[Warning] Device not available again after 30 seconds! MXID: {mxid}", PrintColors.RED)
        return False


def select_device():
    infos = dai.XLinkConnection.getAllConnectedDevices()

    if len(infos) == 0:
        raise RuntimeError("No DepthAI device found!")
    else:
        print("Available devices:")
        for i, info in enumerate(infos):
            print(f"[{i}] {info.getMxId()} [{info.state.name}]")

        if len(infos) == 1:
            return infos[0]
        else:
            val = input("Which DepthAI Device you want to use: ")
            try:
                return infos[int(val)]
            except:
                raise ValueError("Incorrect value supplied: {}".format(val))


def to_planar(arr: np.ndarray, shape: tuple = None) -> np.ndarray:
    if shape:
        return cv2.resize(arr, shape).transpose(2, 0, 1).flatten()
    else:
        return arr.transpose(2, 0, 1).flatten()

def frame_norm(frame, bbox):
    normVals = np.full(len(bbox), frame.shape[0])
    normVals[::2] = frame.shape[1]
    return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)
