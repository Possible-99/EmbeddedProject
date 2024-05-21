from views.GamesView import GamesView
from blinker import signal
import subprocess
import shutil
from utils.roms import get_names_in_folder
from usb_monitor import monitor_usb, mount_usb, unmount_usb, copy_roms
from startup import play_startup_image_and_sound

def execute_game_in_mednafen(game_path):
    mednafen_executable = '/usr/games/mednafen'
    
    if not shutil.which(mednafen_executable):
        print(f"Mednafen executable '{mednafen_executable}' not found. Please ensure it is installed and in your PATH.")
        return

    try:
        return subprocess.Popen(['sudo', mednafen_executable, game_path])
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while trying to run the game: {e}")
        return None

def update_state(sender, **kwargs):
    game_name = kwargs.get('gameClicked')
    context["state"] = "ExecuteGame"
    context["gameName"] = game_name

def handle_usb_event(sender, **kwargs):
    device = kwargs.get('device')
    if 'mednafen_process' in globals() and mednafen_process:
        mednafen_process.terminate()
    gamesView.stop_view()
    mount_point = mount_usb(device)
    if mount_point:
        print(mount_point)
        copy_roms(mount_point, "./roms")
        unmount_usb(mount_point)
        context["state"] = "Setup"
        gamesView.initialize_pygame()  # Reinitialize resources after handling USB event

play_startup_image_and_sound("./splash.jpg" , "./splash.wav")
context = {"state": "Setup", "gameName": ""}
mednafen_process = None

game_clicked = signal('gameClicked')
game_clicked.connect(update_state)

usb_event_signal = signal('usb_event')
usb_event_signal.connect(handle_usb_event)

# Initialize GamesView once
gamesView = GamesView(game_clicked)

# Start USB monitor in a separate thread
import threading
usb_thread = threading.Thread(target=monitor_usb, daemon=True)
usb_thread.start()

while True:
    state = context["state"]
    print(state)
    if state == "Setup":
        gamesView.show(get_names_in_folder("./roms"))
        context["state"] = "ExecuteGame"
    if state == "ExecuteGame":
        print("Executing game:", context["gameName"])
        game_path = f"./roms/{context['gameName']}"  # Assuming the ROMs are in the 'roms' directory
        gamesView.cleanup()  # Clean up resources before executing the game
        mednafen_process = execute_game_in_mednafen(game_path)
        if mednafen_process:
            mednafen_process.wait()  # Wait for the game process to complete
        gamesView.initialize_pygame()  # Reinitialize resources after executing the game
        context["state"] = "Setup"
    if state == "USBEvent":
        # Handle USB event logic here, if necessary
        print("Handling USB event...")
        context["state"] = "Setup"