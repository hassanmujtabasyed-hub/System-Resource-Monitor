import psutil 
import matplotlib.pyplot as plt
from datetime import datetime 
import csv 
import time

log_file = "resource_log.csv"

cpu_data = []
memory_data = []
disk_read_data = []
disk_write_data = []
download_speed_data = []
upload_speed_data = []
timestamps = []

CPU_SCALE_FACTOR = 10

# headers
with open(log_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Time", "CPU Usage (%)", "Memory Usage (%)", 
                     "Disk Read (MB)", "Disk Write (MB)", 
                     "Download Speed (KB/s)", "Upload Speed (KB/s)"])

def get_disk_io():
    io_counters = psutil.disk_io_counters()
    read_mb = io_counters.read_bytes / (1024 * 1024)  
    write_mb = io_counters.write_bytes / (1024 * 1024)  
    return read_mb, write_mb

def get_network_io(previous_net):
    net_io = psutil.net_io_counters()
    download_speed = (net_io.bytes_recv - previous_net.bytes_recv) / 1024  # KB/s (download speed =(net_io.bytes_recv - previous_net.bytes_recv))/(1024*1024) #MB/s
    upload_speed = (net_io.bytes_sent - previous_net.bytes_sent) / 1024  # KB/s
    return download_speed, upload_speed, net_io

previous_net = psutil.net_io_counters()

plt.ion()
fig, ax = plt.subplots(figsize=(12, 8))

while True:
    current_time = datetime.now().strftime("%H:%M:%S")
    cpu = psutil.cpu_percent(interval=1) 
    memory = psutil.virtual_memory().percent 
    disk_read, disk_write = get_disk_io()  
    download_speed, upload_speed, previous_net = get_network_io(previous_net)  

    print(f"Time: {current_time}")
    print(f"CPU Usage: {cpu}% (Scaled: {cpu * CPU_SCALE_FACTOR}%) | Memory Usage: {memory}%")
    print(f"Disk Read: {disk_read:.2f} MB | Disk Write: {disk_write:.2f} MB")
    print(f"Download Speed: {download_speed:.2f} KB/s | Upload Speed: {upload_speed:.2f} KB/s")
    print("-" * 50)

    cpu_data.append(cpu * CPU_SCALE_FACTOR)  
    memory_data.append(memory)
    disk_read_data.append(disk_read)
    disk_write_data.append(disk_write)
    download_speed_data.append(download_speed)
    upload_speed_data.append(upload_speed)
    timestamps.append(current_time)

    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([current_time, cpu, memory, round(disk_read, 2), round(disk_write, 2), 
                         round(download_speed, 2), round(upload_speed, 2)])

    ax.clear()
    ax.plot(cpu_data, label=f"CPU Usage (Scaled x{CPU_SCALE_FACTOR})", color='r', linewidth=1.5)
    ax.plot(memory_data, label="Memory Usage (%)", color='b', linewidth=1.5)
    ax.plot(disk_read_data, label="Disk Read (MB)", color='g', linewidth=1.5)
    ax.plot(disk_write_data, label="Disk Write (MB)", color='y', linewidth=1.5)
    ax.plot(download_speed_data, label="Download Speed (KB/s)", color='c', linewidth=1.5)
    ax.plot(upload_speed_data, label="Upload Speed (KB/s)", color='m', linewidth=1.5)

    ax.set_title("Real-Time System Resource Monitoring")
    ax.set_xlabel("Time")
    ax.set_ylabel("Usage")
    ax.legend(loc="upper left")
    ax.grid()
    ax.tick_params(axis='x', rotation=45)
    ax.set_xticks(range(0, len(timestamps), max(1, len(timestamps)//10)))  # Reduce x-tick density
    ax.set_xticklabels(timestamps[::max(1, len(timestamps)//10)])

    ax.set_ylim(0, max(max(cpu_data[-10:], default=1), max(memory_data[-10:], default=1), 100 * CPU_SCALE_FACTOR))

    plt.pause(1)
