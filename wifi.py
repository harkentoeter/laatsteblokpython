import scapy.all as scapy
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import datetime
import threading
from collections import deque

TARGET_IP = "127.0.0.1"
PORT_RANGE = range(1, 1025)

SYN_INTERVAL = 1  # seconds
PORT_SCAN_INTERVAL = 5  # seconds

syn_counts = deque([0]*60, maxlen=60)
time_labels = deque([datetime.datetime.utcnow().strftime("%H:%M:%S")]*60, maxlen=60)
port_status = {}
lock = threading.Lock()

def capture_syn_requests_loop():
    while True:
        count = 0
        def count_syn(packet):
            nonlocal count
            if scapy.TCP in packet and packet[scapy.TCP].flags == "S":
                count += 1
        scapy.sniff(timeout=SYN_INTERVAL, prn=count_syn, store=0)
        with lock:
            syn_counts.append(count)
            time_labels.append(datetime.datetime.utcnow().strftime("%H:%M:%S"))

def scan_ports_loop():
    while True:
        open_ports = []
        closed_ports = []
        for port in PORT_RANGE:
            pkt = scapy.IP(dst=TARGET_IP)/scapy.TCP(dport=port, flags="S")
            response = scapy.sr1(pkt, timeout=0.5, verbose=0)
            if response and scapy.TCP in response and response[scapy.TCP].flags == 18:  # SYN-ACK
                open_ports.append(port)
            else:
                closed_ports.append(port)
        with lock:
            for port in PORT_RANGE:
                if port in open_ports:
                    port_status[port] = 'open'
                else:
                    port_status[port] = 'closed'
        time.sleep(PORT_SCAN_INTERVAL)

def update(frame):
    with lock:
        # Update SYN graph
        syn_ax.clear()
        syn_ax.plot(list(time_labels), list(syn_counts), color='blue')
        syn_ax.set_title('SYN Requests per Second')
        syn_ax.set_xlabel('Time (UTC)')
        syn_ax.set_ylabel('SYN count/sec')
        syn_ax.tick_params(axis='x', rotation=45)
        syn_ax.grid(True)

        # Update port status plot
        port_ax.clear()
        ports = list(PORT_RANGE)
        status_colors = ['green' if port_status.get(p) == 'open' else 'red' for p in ports]
        x = np.arange(len(ports)) % 32
        y = np.arange(len(ports)) // 32
        port_ax.scatter(x, y, c=status_colors, s=30)
        port_ax.set_title('Port Status (Green=open, Red=closed)')
        port_ax.set_xticks([])
        port_ax.set_yticks([])
        port_ax.set_xlim(-1, 32)
        port_ax.set_ylim(-1, len(ports)//32 + 1)

syn_thread = threading.Thread(target=capture_syn_requests_loop, daemon=True)
port_thread = threading.Thread(target=scan_ports_loop, daemon=True)
syn_thread.start()
port_thread.start()

fig, (syn_ax, port_ax) = plt.subplots(2, 1, figsize=(12, 8))
ani = FuncAnimation(fig, update, interval=1000, cache_frame_data=False)
plt.tight_layout()
plt.show()

