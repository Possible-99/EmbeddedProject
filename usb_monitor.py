# usb_monitor.py
import pyudev
import os
import shutil
import subprocess
from blinker import signal

usb_event_signal = signal('usb_event')

def monitor_usb():
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='block', device_type='partition')

    observer = pyudev.MonitorObserver(monitor, lambda action, device: handle_device_event(action, device))
    observer.start()

def handle_device_event(action, device):
    if action == "add":
        usb_event_signal.send('usb_event', device=device)

def mount_usb(device):
    mount_point = f"/mnt/{device.device_node.split('/')[-1]}"
    os.makedirs(mount_point, exist_ok=True)
    try:
        subprocess.run(['sudo', 'mount', device.device_node, mount_point], check=True)
        return mount_point
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while trying to mount the device: {e}")
        return None

def unmount_usb(mount_point):
    try:
        subprocess.run(['sudo', 'umount', mount_point], check=True)
        os.rmdir(mount_point)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while trying to unmount the device: {e}")

def copy_roms(source_directory, destination_directory):
    print("Copying ROMs")
    for file in os.listdir(source_directory):
        if (file.endswith(".rom") or file.endswith(".nes")) and not file.startswith("._"):  # Skip files starting with ._
            source_file = os.path.join(source_directory, file)
            destination_file = os.path.join(destination_directory, file)
            shutil.copy(source_file, destination_file)
            print(f"Copied {file} to {destination_file}")
