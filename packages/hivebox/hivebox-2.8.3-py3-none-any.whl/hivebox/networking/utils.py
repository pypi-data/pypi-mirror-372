import psutil
import socket

def get_ip(default='127.0.0.1'):
    tailscale_ip = next(map(
        lambda item: item.address,
        filter(
            lambda item: item.family == socket.AF_INET,
            psutil.net_if_addrs().get('tailscale0', [])
        )
    ), None)
    if tailscale_ip is not None:
        return tailscale_ip

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('8.8.8.8', 1))
        local_ip = s.getsockname()[0]
    except:
        local_ip = default
    finally:
        s.close()
    return local_ip