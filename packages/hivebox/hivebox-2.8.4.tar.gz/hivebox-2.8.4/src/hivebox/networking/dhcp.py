from pathlib import Path
import re
from hivebox.common.cli import cli_print, cli_run, PrintColors

interfaces_config = """auto {interface_name}
iface {interface_name} inet static
        address 192.168.192.1
        netmask 255.255.255.0
        dns-nameservers 8.8.8.8"""

networkmanager_config = """[main]
plugins=ifupdown,keyfile

[ifupdown]
managed=true

[device]
wifi.scan-rand-mac-address=no"""

dnsmasq_config = """domain=hivecv.local
no-resolv
no-poll
dhcp-range=192.168.192.101,192.168.192.120,255.255.255.0,12h
dhcp-option=3,192.168.192.1
dhcp-option=6,8.8.8.8
log-queries
log-dhcp"""

class DHCPSetup:
    @staticmethod
    def _ensure_installed(pkg_name):
        result = cli_run(f"dpkg -s {pkg_name}", stdout=True, silent=True)
        if result.returncode == 0:
            m = re.search("Status:.*", result.stdout)
            if m:
                installation_status = m.group()[len("Status:"):].strip().split()
                if 'installed' in installation_status and 'ok' in installation_status:
                    cli_print(f"{pkg_name} already installed")
                    return

        cli_print(f"Installing {pkg_name}...", PrintColors.BLUE)
        cli_run(f"apt-get install -y {pkg_name}")
        cli_print(f"{pkg_name} successfully installed")

    @staticmethod
    def install_rpi5():
        cli_print("Starting DHCP installation...")
        DHCPSetup._ensure_installed("dnsmasq")

        cli_print("Configuring Static IP...")
        with Path("/etc/network/interfaces").open(mode="w") as f:
            f.write(interfaces_config.format(interface_name="eth0"))
        cli_print("Configuring Network Manager...")
        with Path("/etc/NetworkManager/NetworkManager.conf").open(mode="w") as f:
            f.write(networkmanager_config)
        cli_print("Configuring DHCP Server...")
        with Path("/etc/dnsmasq.conf").open(mode="w") as f:
            f.write(dnsmasq_config)

        cli_run("systemctl restart NetworkManager", label="NetworkManager restart")
        cli_run("systemctl restart dnsmasq", label="dnsmasq restart")

        cli_print("Finished DHCP installation!")

    @staticmethod
    def install_orangepi5b():
        cli_print("Starting DHCP installation...")
        DHCPSetup._ensure_installed("dnsmasq")

        cli_print("Configuring Static IP...")
        with Path("/etc/network/interfaces").open(mode="w") as f:
            f.write(interfaces_config.format(interface_name="end1"))
        cli_print("Configuring DHCP Server...")
        with Path("/etc/dnsmasq.conf").open(mode="w") as f:
            f.write(dnsmasq_config)

        cli_run("ip addr flush dev end1", label="Previous IP config removal")
        cli_run("systemctl restart networking", label="networking restart")
        cli_run("systemctl restart dnsmasq", label="dnsmasq restart")

        cli_print("Finished DHCP installation!")



