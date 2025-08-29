import platform
import subprocess

def block_ip(ip):
    system = platform.system().lower()
    try:
        if "linux" in system or "darwin" in system:
            subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])
        elif "windows" in system:
            subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", "name=BlockIP", f"dir=in", f"action=block", f"remoteip={ip}"])
    except Exception as e:
        print("Firewall block failed :", e)
