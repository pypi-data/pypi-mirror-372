FPS=30
import time
from datetime import timedelta
import math
# Timestamp threshold (in miliseconds) under which frames will be considered synced.
# Lower number means frames will have less delay between them, which can potentially
# lead to dropped frames.
MS_THRESHOL=math.ceil(1000 / FPS)

def check_sync(queues, timestamp):
    matching_frames = []
    for name, list in queues.items(): # Go through each available stream
        # node.warn(f"List {name}, len {str(len(list))}")
        for i, msg in enumerate(list): # Go through each frame of this stream
            time_diff = abs(msg.getTimestamp() - timestamp)
            if time_diff <= timedelta(milliseconds=MS_THRESHOL): # If time diff is below threshold, this frame is considered in-sync
                matching_frames.append(i) # Append the position of the synced frame, so we can later remove all older frames
                break

    if len(matching_frames) == len(queues):
        # We have all frames synced. Remove the excess ones
        i = 0
        for name, list in queues.items():
            queues[name] = queues[name][matching_frames[i]:] # Remove older (excess) frames
            i+=1
        return True
    else:
        return False # We don't have synced frames yet

names = ['disp', 'rgb']
frames = dict() # Dict where we store all received frames
for name in names:
    frames[name] = []

while True:
    for name in names:
        f = node.io[name+"_in"].tryGet()
        if f is not None:
            frames[name].append(f) # Save received frame

            if check_sync(frames, f.getTimestamp()): # Check if we have any synced frames
                # Frames synced!
                node.info(f"Synced frame!")
                # node.warn(f"Queue size. Disp: {len(frames['disp'])}, rgb: {len(frames['rgb'])}")
                for name, list in frames.items():
                    syncedF = list.pop(0) # We have removed older (excess) frames, so at positions 0 in dict we have synced frames
                    node.info(f"{name}, ts: {str(syncedF.getTimestamp())}, seq {str(syncedF.getSequenceNum())}")
                    node.io[name+'_out'].send(syncedF) # Send synced frames to the host


    time.sleep(0.001)  # Avoid lazy looping