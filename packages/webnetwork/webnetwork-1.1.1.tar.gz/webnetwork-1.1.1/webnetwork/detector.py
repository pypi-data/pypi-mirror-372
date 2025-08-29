import os, re, time, threading, csv, socket, requests, platform, subprocess
from collections import deque, Counter
from datetime import datetime, timedelta
try: from scapy.all import sniff, conf, TCP, IP
except: pass

LOG_CHECK_INTERVAL = 1.0
WINDOW_SECONDS = 10
REQS_PER_IP_THRESHOLD = 50
TOTAL_RPS_THRESHOLD = 200
UNIQUE_IP_ENTROPY_THRESHOLD = 0.5
SYN_RATE_THRESHOLD = 100
SYN_TO_ACK_RATIO = 5.0
ALERT_CSV = "alerts.csv"

def now_ts(): return datetime.utcnow().isoformat()+"Z"
def write_alert(alert_type, details):
    row=[now_ts(), alert_type, details]
    print("[ALERT]", row)
    try: 
        with open(ALERT_CSV,"a",newline="") as f: csv.writer(f).writerow(row)
    except: pass

def block_ip(ip):
    system=platform.system().lower()
    try:
        if "linux" in system or "darwin" in system:
            subprocess.run(["sudo","iptables","-A","INPUT","-s",ip,"-j","DROP"])
        elif "windows" in system:
            subprocess.run(["netsh","advfirewall","firewall","add","rule","name=BlockIP","dir=in","action=block",f"remoteip={ip}"])
    except: pass

class LogAnalyzer:
    ip_regex=re.compile(r'^(\d{1,3}(?:\.\d{1,3}){3})\b')
    def __init__(self, logfile_path, window_seconds=WINDOW_SECONDS):
        self.logfile_path=logfile_path
        self.window=timedelta(seconds=window_seconds)
        self.events=deque()
        self.lock=threading.Lock()
        self.running=False
    def _tail_follow(self):
        with open(self.logfile_path,"r",encoding="utf-8",errors="ignore") as fh:
            fh.seek(0,2)
            while self.running:
                line=fh.readline()
                if not line: time.sleep(LOG_CHECK_INTERVAL); continue
                m=self.ip_regex.match(line)
                if m:
                    ip=m.group(1)
                    ts=datetime.utcnow()
                    with self.lock: self.events.append((ts,ip))
    def _prune_and_check(self):
        import math
        while self.running:
            time.sleep(LOG_CHECK_INTERVAL)
            cutoff=datetime.utcnow()-self.window
            with self.lock:
                while self.events and self.events[0][0]<cutoff: self.events.popleft()
                total_reqs=len(self.events)
                rps=total_reqs/max(1,self.window.total_seconds())
                ip_counts=Counter(ip for _,ip in self.events)
                top_ip, top_count = ip_counts.most_common(1)[0] if ip_counts else (None,0)
                if total_reqs<=1: entropy_norm=1.0
                else:
                    probs=[c/total_reqs for c in ip_counts.values()]
                    H=-sum(p*math.log(p+1e-12) for p in probs)
                    entropy_norm=H/(math.log(len(probs)+1e-12))
                if rps>TOTAL_RPS_THRESHOLD: write_alert("TOTAL_RPS_SPIKE",f"rps={rps:.1f}")
                if top_count>REQS_PER_IP_THRESHOLD: write_alert("HIGH_REQS_SINGLE_IP",f"ip={top_ip}"); block_ip(top_ip)
                if entropy_norm<UNIQUE_IP_ENTROPY_THRESHOLD and total_reqs>50: write_alert("LOW_IP_ENTROPY",f"H_norm={entropy_norm:.2f}"); block_ip(top_ip)
    def start(self):
        self.running=True
        threading.Thread(target=self._tail_follow,daemon=True).start()
        threading.Thread(target=self._prune_and_check,daemon=True).start()

class PacketSniffer:
    def __init__(self, iface=None, window_seconds=WINDOW_SECONDS):
        self.iface=iface
        self.window=timedelta(seconds=window_seconds)
        self.syn_events=deque()
        self.synack_events=deque()
        self.lock=threading.Lock()
        self.running=False
    def _on_packet(self,pkt):
        if IP in pkt and TCP in pkt:
            t=datetime.utcnow(); tcp=pkt[TCP]; flags=tcp.flags
            if flags==0x02: self.syn_events.append((t,pkt[IP].src))
            elif flags&0x12==0x12: self.synack_events.append((t,pkt[IP].src))
    def _sniff(self):
        sniff(iface=self.iface,filter="tcp",prn=self._on_packet,store=False,stop_filter=lambda x:not self.running)
    def _prune_and_check(self):
        while self.running:
            time.sleep(LOG_CHECK_INTERVAL)
            cutoff=datetime.utcnow()-self.window
            while self.syn_events and self.syn_events[0][0]<cutoff: self.syn_events.popleft()
            while self.synack_events and self.synack_events[0][0]<cutoff: self.synack_events.popleft()
            syn_count=len(self.syn_events)
            synack_count=len(self.synack_events)
            ratio=(syn_count/(synack_count+1e-6)) if synack_count>0 else float('inf')
            src_counts=Counter(src for _,src in self.syn_events)
            top_src,top_count=src_counts.most_common(1)[0] if src_counts else (None,0)
            if syn_count>SYN_RATE_THRESHOLD: write_alert("SYN_RATE_SPIKE",f"syn_count={syn_count}"); block_ip(top_src)
            if ratio>SYN_TO_ACK_RATIO and syn_count>(SYN_RATE_THRESHOLD/10): write_alert("HIGH_SYN_TO_ACK_RATIO",f"ratio={ratio:.2f}"); block_ip(top_src)
            if top_count>(SYN_RATE_THRESHOLD/4): write_alert("SYN_SINGLE_SOURCE_FLOOD",f"src={top_src}"); block_ip(top_src)
    def start(self):
        self.running=True
        threading.Thread(target=self._sniff,daemon=True).start()
        threading.Thread(target=self._prune_and_check,daemon=True).start()

def get_public_ip():
    try: return requests.get("https://api.ipify.org").text.strip()
    except: return socket.gethostbyname(socket.gethostname())

def find_logfile():
    paths=["/var/log/nginx/access.log","/var/log/apache2/access.log","/var/log/httpd/access_log"]
    for p in paths: 
        if os.path.exists(p): return p
    return None

def start(logfile=None, iface=None):
    ip=get_public_ip()
    print(f"Monitoring server IP : {ip}")
    if not logfile: logfile=find_logfile()
    if logfile and os.path.exists(logfile): LogAnalyzer(logfile).start()
    if iface or True: PacketSniffer(iface).start()
    while True: time.sleep(1)
