import os, sys, json, ctypes
import tkinter as tk
from tkinter import messagebox

VERSION = "v0.1.1"

config = {}
admin = False
run_wdin_as_admin = True

network_interface = ""
network_interface_friendly_name = ""
capture_device_local_ip_address = ""
stop_sniffing = None
capture_is_on = False
monitor_ip_change = None

log_current_event_to_file = True

wd_active_window = False
wd_hwnd = None
last_checked_hwnd = None
first_window_check = True

overlay_custom_font = "Arial"
overlay_font_size = 20
overlay_left_offset = 4
overlay_top_offset = 4
overlay_background_opacity = 70
in_game_overlay = None

is_a_recent_ip_for_event = {}
pinged_events = {}
timers = {'pinged': {}}
ip_address_for_current_event = None
last_event_activity_time = 0
wd_event_thread_active = False
SECS_TO_DISPLAY_CURRENT_EVENT_FOR = 9

add_contract_audio_option = False
add_invading_audio_option = False
display_disconnect_button_on_gui = True
display_online_toggle_button_on_gui = True
display_reveal_the_invader_button_on_gui = False
display_anti_afk_button_on_gui = False
display_ntfy_button_on_gui = False
shrink_gui_at_startup_to_hide_network_option = False
shrink_gui_at_startup_to_hide_audio_options = False

audio_labels = {}
audio_buttons = {}
audio_files = {}
audio_events = {}
volume_settings = {}
wd_event_types_dic = ["invaded!", "scanned!"]

reveal_the_invader_enabled = False
reloading_last_autosave = False
reloading_last_autosave_delay = 0

anti_afk_enabled = False
anti_afk_timeout = False
keyboard_listener = None
stop_anti_afk_timeout = None
last_keyboard_activity_time = 0
kbd_controller = None
AFK_INACTIVITY_THRESHOLD = 285
last_afk_key_pressed = "s"

ntfy_enabled = False
ntfy_mytopic = ""
ntfy_priority = "4"

autohotkeys = {}
disconnect_hotkey = ""
toggle_online_hotkey = ""
reload_last_autosave_hotkey = ""
quit_invasion_hotkey = ""
open_online_menu_hotkey = ""
quit_invasion_then_open_online_menu_hotkey = ""
reload_last_autosave_ahk_script = ""
quit_invasion_ahk_script = ""
open_online_menu_ahk_script = ""
quit_invasion_then_open_online_menu_ahk_script = ""
hotkeys_started = False

ICON_PATH = None
ANSI_ESCAPE = None
firewall_block = False
allow_vpn_server_switching = False

root = None
wmi_client = None
interface_window = None
selected_interface_label = None
ahk = None
wdin_button = None
wdin_label = None
disconnect_button = None
online_toggle_button = None
online_toggle_status_label = None
reveal_button = None
reveal_label = None
anti_afk_button = None
anti_afk_label = None
ntfy_button = None
ntfy_label = None
    
def check_for_windows_os():
    current_platform = sys.platform
    if not current_platform == "win32":
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Unsupported Platform", "This program can only run on Windows.")
        sys.exit()

def check_for_npcap_installation():
    npcap_driver_path = os.path.join(os.getenv('windir'), 'system32', 'drivers', 'npcap.sys')
    if not os.path.exists(npcap_driver_path):
        root = tk.Tk()
        root.withdraw()
        if messagebox.askyesno("Npcap Required", "Npcap is required to use this program.\n\nWould you like to download it now?"):
            messagebox.showinfo("Exiting", "WDIN will now exit and open the Npcap download webpage.")
            import webbrowser
            webbrowser.open("https://npcap.com/#download")
        else: 
            messagebox.showinfo("Exiting", "WDIN will now exit.")
        sys.exit()

def load_config_file():
    global config
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                try:
                    config = json.load(f)
                except json.JSONDecodeError:
                    root = tk.Tk()
                    root.withdraw()
                    choice = messagebox.askquestion(
                        "CORRUPTED CONFIG",
                        f"Your {CONFIG_FILE} file is corrupted. Would you like to continue?\n\n"
                        "[YES] = Create NEW config\n"
                        "[NO] = Exit now",
                        icon='error',
                        type='yesno'
                    )
                    if choice == 'yes':
                        with open("wdin_create_new_config_on_restart", "w"):
                            pass
                        run_as_admin()
                    else:
                        sys.exit()
        except (OSError, IOError) as e:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                f"CONFIG ERROR",
                f"Unable to open the {CONFIG_FILE} file: {e}\n\n"
                "This program will now exit."
            )
            sys.exit()

def get_config_value(config, keys, default):
    for key in keys:
        if not isinstance(config, dict):
            return default
        config = config.get(key, default)
    return config if isinstance(config, type(default)) else default

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    import sys, os, ctypes
    # Try to use pythonw.exe for GUI
    pythonw = sys.executable.replace("python.exe", "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable  # fallback
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", pythonw, params, None, 1
    )

def check_if_restarted_from_corrupted_config():
    if os.path.exists("wdin_create_new_config_on_restart"):
        os.remove("wdin_create_new_config_on_restart")
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)

check_for_windows_os()
check_for_npcap_installation()

# Define APPDATA directory for WDIN
APPDATA = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
    "WDIN"
)
os.makedirs(APPDATA, exist_ok=True)

# Ensure logs directory exists
LOGS_DIR = os.path.join(APPDATA, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Use APPDATA for config and other persistent files
CONFIG_FILE = os.path.join(APPDATA, "config.json")
CURRENT_EVENT_FILE = os.path.join(APPDATA, "current_event.txt")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DEFAULT_CONFIG = os.path.join(DATA_DIR, "config.json")

import shutil
# Ensure config.json exists in APPDATA
if not os.path.exists(CONFIG_FILE) and os.path.exists(DEFAULT_CONFIG):
    shutil.copy2(DEFAULT_CONFIG, CONFIG_FILE)

DATA_SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "data", "sounds")
DEFAULT_SOUNDS = [
    ("mgs-alert.mp3", os.path.join(APPDATA, "sounds", "mgs-alert.mp3")),
    ("inception.mp3", os.path.join(APPDATA, "sounds", "inception.mp3")),
]

# Ensure sounds exist in APPDATA
for src_name, dest_path in DEFAULT_SOUNDS:
    src_path = os.path.join(DATA_SOUNDS_DIR, src_name)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if not os.path.exists(dest_path) and os.path.exists(src_path):
        shutil.copy2(src_path, dest_path)
        
check_if_restarted_from_corrupted_config()
config = {}
load_config_file()
admin = False
run_wdin_as_admin = get_config_value(config, ['run_wdin_as_admin'], True)
if run_wdin_as_admin:
    admin = is_admin()
    if not admin:
        run_as_admin()
        sys.exit()

import logging
debug_logging = get_config_value(config, ['logging', 'debug'], False)

if debug_logging:
    logging.basicConfig(
        filename=os.path.join(LOGS_DIR, 'debug.log'),
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def log_if_enabled(msg):
    if debug_logging:
        logging.error(msg)

# Python libraries
import re, time, subprocess, warnings
from typing import Optional
from threading import Thread, Event, Timer

# Third-party libraries
from tkinter import Toplevel, filedialog, Label, font
import requests, wmi
from scapy.all import sniff, UDP, IP, get_if_list
warnings.filterwarnings("ignore", module="ahk")
from ahk import AHK
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
from pygame import mixer
mixer.init()
from pynput import keyboard
from pynput.keyboard import Controller
import win32gui, win32api, win32con, win32process

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base_path, relative_path)

def check_window_state_periodically():
    is_watch_dogs_the_active_window()
    root.after(100, check_window_state_periodically)

def is_watch_dogs_the_active_window():
    global wd_active_window, stop_anti_afk_timeout, last_checked_hwnd, hotkeys_started, wd_hwnd, first_window_check
    try:
        hwnd = win32gui.GetForegroundWindow()
        if hwnd == last_checked_hwnd:
            return
        else:
            window_title = win32gui.GetWindowText(hwnd).strip().lower()
            if window_title != "watch_dogs" or not window_title:
                current_window_check = False
            else:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)
                try:
                    exe_path = win32process.GetModuleFileNameEx(handle, 0).lower()
                    current_window_check = exe_path.endswith("watch_dogs.exe")
                    if current_window_check:
                        wd_hwnd = hwnd
                finally:
                    win32api.CloseHandle(handle)

        if (current_window_check != wd_active_window) or first_window_check:
            wd_active_window = current_window_check

            if current_window_check:
                in_game_overlay.toggle_visibility(True)
                if should_enable_ahk() and not hotkeys_started:
                    ahk.start_hotkeys()
                    hotkeys_started = True
                if anti_afk_enabled and stop_anti_afk_timeout.is_set():
                    start_anti_afk()
            else:
                in_game_overlay.toggle_visibility(False)
                if hotkeys_started:
                    ahk.stop_hotkeys()
                    hotkeys_started = False
                if not stop_anti_afk_timeout.is_set():
                    stop_anti_afk()

        last_checked_hwnd = hwnd
        first_window_check = False
        return

    except Exception as e:
        log_if_enabled(f"ERROR checking window state: {e}")
        last_checked_hwnd = None
        wd_active_window = False
        return

class InGameOverlay:
    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.label = None
        self.current_content = ""
        self.last_rect = None
        self.setup_overlay()

    def setup_overlay(self):
        self.window = Toplevel(self.parent)
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', overlay_background_opacity / 100)
        self.window.configure(bg='black')

        custom_font = font.Font(family=overlay_custom_font, weight="bold", size=overlay_font_size)
        self.label = Label(
            self.window,
            text="",
            fg='white',
            bg='black',
            font=custom_font,
            justify='left'
        )
        self.label.pack(padx=7, pady=7)
        if wd_active_window: 
            self.toggle_visibility(True)

    def update_position(self):
        try:
            rect = win32gui.GetWindowRect(wd_hwnd)
            if rect != self.last_rect:
                self.last_rect = rect
                x = rect[0] + overlay_left_offset
                y = rect[1] + overlay_top_offset
                self.window.geometry(f"+{x}+{y}")
        except Exception as e:
          log_if_enabled(f"Position update failed: {e}")
          pass

    def toggle_visibility(self, enable: bool):
        if enable and self.current_content.strip():
            self.update_position()
            self.window.deiconify()
        else:
            self.window.withdraw()

    def update_content(self, new_content):
        self.current_content = new_content
        self.label.config(text=self.current_content)
        self.toggle_visibility(wd_active_window)

def send_ntfy_notification(data, title):
    try:
        response = requests.post(f"https://ntfy.sh/{ntfy_mytopic}",
            data=data.encode(encoding='utf-8'),
            headers={
                "Title": title,
                "Priority": ntfy_priority,
                "Tags": "eye"
            })
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        error_type = type(e).__name__ 
        log_if_enabled(f"NTFY {error_type} occurred: {e}")

def reload_last_autosave(ping_time: float | None = None):
    global reloading_last_autosave
    if not wd_active_window: return
    reloading_last_autosave = True

    if ping_time is not None:
        ping_time = float(ping_time)
        sleep_time = 0.8 + (ping_time / 100)
        sleep_time += reloading_last_autosave_delay
        time.sleep(sleep_time)

    ahk.run_script(reload_last_autosave_ahk_script)
    reloading_last_autosave = False

def quit_invasion():  # added redundant if check for extra safety
    if wd_active_window: ahk.run_script(quit_invasion_ahk_script)

def open_online_menu():  # added redundant if check for extra safety
    if wd_active_window: ahk.run_script(open_online_menu_ahk_script)

def quit_invasion_then_open_online_menu():
    if wd_active_window: ahk.run_script(quit_invasion_then_open_online_menu_ahk_script)

def press_anti_afk_keys():
    global last_afk_key_pressed
    last_afk_key_pressed = "s" if last_afk_key_pressed == "w" else "w"
    anti_afk_ahk_script = f"""
        Send, {{{last_afk_key_pressed} down}}
        Sleep, 5
        Send, {{{last_afk_key_pressed} up}}
        Sleep, 5
    """
    ahk.run_script(anti_afk_ahk_script)

def on_activity(key):
    global last_keyboard_activity_time
    last_keyboard_activity_time = time.time()

def anti_afk_timeout_main(stop_event):
    while not stop_event.is_set():
        time_since_last_activity = time.time() - last_keyboard_activity_time
        if time_since_last_activity > AFK_INACTIVITY_THRESHOLD:
            if not reloading_last_autosave:
                press_anti_afk_keys()
            else:
                time.sleep(AFK_INACTIVITY_THRESHOLD)
        else:
            time.sleep(AFK_INACTIVITY_THRESHOLD - time_since_last_activity)

def start_anti_afk():
    global stop_anti_afk_timeout, last_keyboard_activity_time, keyboard_listener
    stop_anti_afk_timeout.clear()
    last_keyboard_activity_time = time.time()
    anti_afk_timeout_thread = Thread(target=anti_afk_timeout_main, args=(stop_anti_afk_timeout,))
    anti_afk_timeout_thread.daemon = True
    anti_afk_timeout_thread.start()
    if keyboard_listener is None or not keyboard_listener.running:
        keyboard_listener = keyboard.Listener(on_press=on_activity, on_release=on_activity)
        keyboard_listener.start()

def stop_anti_afk():
    global stop_anti_afk_timeout, last_keyboard_activity_time, keyboard_listener
    stop_anti_afk_timeout.set()
    last_keyboard_activity_time = None
    if keyboard_listener:
        keyboard_listener.stop()
        keyboard_listener = None

def toggle_anti_afk():
    global anti_afk_enabled
    if 'anti_afk_button' in globals() and anti_afk_button.winfo_exists():
        anti_afk_button.config(state=tk.DISABLED)
    anti_afk_enabled = not anti_afk_enabled
    if anti_afk_enabled:
        anti_afk_label.config(text="✔️", fg="green")
    else:
        anti_afk_label.config(text="❌", fg="red")
        stop_anti_afk()
    save_config()
    if 'anti_afk_button' in globals() and anti_afk_button.winfo_exists():
        root.after(90, lambda: anti_afk_button.config(state=tk.NORMAL))

def toggle_auto_reveal_the_invader():
    global reveal_the_invader_enabled
    if 'reveal_button' in globals() and reveal_button.winfo_exists():
        reveal_button.config(state=tk.DISABLED)
    reveal_the_invader_enabled = not reveal_the_invader_enabled
    if reveal_the_invader_enabled:
        reveal_label.config(text="✔️", fg="green")
    else:
        reveal_label.config(text="❌", fg="red")
    save_config()
    if 'reveal_button' in globals() and reveal_button.winfo_exists():
        root.after(90, lambda: reveal_button.config(state=tk.NORMAL))

def toggle_ntfy_notification():
    global ntfy_enabled
    if 'ntfy_button' in globals() and ntfy_button.winfo_exists():
        ntfy_button.config(state=tk.DISABLED)
    ntfy_enabled = not ntfy_enabled
    if ntfy_enabled:
        ntfy_label.config(text="✔️", fg="green")
    else:
        ntfy_label.config(text="❌", fg="red")
    save_config()
    if 'ntfy_button' in globals() and ntfy_button.winfo_exists():
        root.after(90, lambda: ntfy_button.config(state=tk.NORMAL))

class IP_Address_Change_Detector:
    def __init__(self):
        self._running = False
        self._thread = None
        self.poll_interval = 60

    def _update_ip_address_if_required(self):
        global capture_device_local_ip_address
        fresh_ip_address_from_ipconfig = self._get_local_ip_address()
        if fresh_ip_address_from_ipconfig != capture_device_local_ip_address and fresh_ip_address_from_ipconfig is not None:
            capture_device_local_ip_address = fresh_ip_address_from_ipconfig

    def _get_local_ip_address(self) -> Optional[str]:
        try:
            result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True)
            interface_section = None
            for line in result.stdout.split('\n'):
                if network_interface_friendly_name in line:
                    interface_section = []
                    continue
                if interface_section is not None:
                    if line.strip() == '':
                        break
                    interface_section.append(line.strip())
            
            if interface_section:
                for line in interface_section:
                    if 'IPv4 Address' in line:
                        ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                        if ip_match:
                            return ip_match.group(1)
            return None
        except Exception as e:
            log_if_enabled(f"Error getting Local IP: {str(e)}")
            return None

    def _monitor_loop(self):
        while self._running:
            self._update_ip_address_if_required()  
            time.sleep(self.poll_interval)

    def start(self):
        if not self._running:
            self._running = True
            self._thread = Thread(target=self._monitor_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)

def verify_that_all_audio_files_exist_and_remove_those_that_do_not():
    for event, event_details in list(audio_events.items()):
        if not isinstance(event_details, dict):
            log_if_enabled(f"Invalid entry for {event}: {event_details}. Removing it.")
            clear_audio(event)
            continue
        if 'enabled' in event_details and isinstance(event_details['enabled'], bool):
            event_details['enabled'] = tk.BooleanVar(value=event_details['enabled'])
        file_path = event_details.get('file')
        if file_path and not os.path.exists(file_path):
            log_if_enabled(f"Audio file for {event} not found: {file_path}. Removing it.")
            clear_audio(event)

def save_config():
    config = {
        'network_interface': network_interface,
        'display_current_event_in_game': {
            'font': overlay_custom_font,
            'font_size': overlay_font_size,
            'left_offset': overlay_left_offset,
            'top_offset': overlay_top_offset,
            'background_opacity_percent': overlay_background_opacity
        },
        'logging': {
            'log_current_event_to_current_event_txt_file': log_current_event_to_file
        },
        'extra_gui_options': {
            'disconnect_from_online_session_gui_button': display_disconnect_button_on_gui,
            'online_toggle_gui_button': display_online_toggle_button_on_gui,
            'add_audio_option_for_your_own_hacking_contracts': add_contract_audio_option,
            'add_audio_option_for_when_you_are_the_invader': add_invading_audio_option,
            'automatically_reveal_the_invader': {
                'gui_button': display_reveal_the_invader_button_on_gui,
                'enabled_state': reveal_the_invader_enabled,
                'added_delay_in_seconds_before_starting': reloading_last_autosave_delay
            },
            'anti_afk_timeout': {
                'gui_button': display_anti_afk_button_on_gui,
                'enabled_state': anti_afk_enabled
            },
            'send_invaded_notification_to_ntfy': {
                'gui_button': display_ntfy_button_on_gui,
                'enabled_state': ntfy_enabled,
                'mytopic': ntfy_mytopic,
                'priority': ntfy_priority
            },
            'shrink_gui_at_startup_to_hide_network_option': shrink_gui_at_startup_to_hide_network_option,
            'or_shrink_gui_at_startup_to_hide_audio_and_network_options': shrink_gui_at_startup_to_hide_audio_options
        },
        'in_game_ahk_style_hotkeys': {
            'disconnect_from_online_session': disconnect_hotkey,
            'toggle_online_services': toggle_online_hotkey,
            'reload_last_autosave_keypresses': reload_last_autosave_hotkey,
            'quit_invasion_keypresses': quit_invasion_hotkey,
            'open_online_menu_keypresses': open_online_menu_hotkey,
            'quit_invasion_then_open_online_menu_keypresses': quit_invasion_then_open_online_menu_hotkey

        },
        'allow_vpn_server_switching': allow_vpn_server_switching,
        'run_wdin_as_admin': run_wdin_as_admin
    }

    if audio_events:
        config['audio_events'] = {
            event_type: {
                'file': details['file'],
                'volume': details['volume'],
                'enabled': details['enabled'].get()
            }
            for event_type, details in audio_events.items()
            if event_type in wd_event_types_dic and isinstance(details, dict)
        }

    # Try to read existing config to preserve special settings
    try:
        with open(CONFIG_FILE, 'r') as f:
            temp_config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        temp_config = {}

    if 'logging' in temp_config:
        if 'debug' in temp_config['logging']:
            config['logging']['debug'] = temp_config['logging'].get('debug', False)
        if 'scapy' in temp_config['logging']:
            config['logging']['scapy'] = temp_config['logging'].get('scapy', False)

    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except PermissionError:
        messagebox.showerror("Permission Error", "Failed to save config - permission denied.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save config: {str(e)}")

def get_local_ip_address_by_friendly_name(friendly_name):
    c = wmi.WMI()
    for nic in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
        if friendly_name in nic.Description or friendly_name in nic.Caption:
            return nic.IPAddress[0] if nic.IPAddress else None
    return None

def network_interface_is_still_valid():
    if network_interface not in get_if_list():
        messagebox.showerror("Error", "Selected Network Interface was not found.")
        return False
    return True

def cancel_ping_timer(event_type):
    if event_type in timers['pinged']:
        timers['pinged'][event_type].cancel()

def expire_ping_for_event(event_type):
    global timers, pinged_events
    if event_type in pinged_events:
        del pinged_events[event_type]
    if event_type in timers['pinged']:
        del timers['pinged'][event_type]

def get_ping_from_event(event_type, ip_address):
    get_ping_time_asap = time.time()
    global timers, pinged_events

    cancel_ping_timer(event_type)
    expire_ping_for_event(event_type)

    if event_type not in pinged_events: pinged_events[event_type] = {}
    pinged_events[event_type]["ping_time"] = get_ping_time_asap
    pinged_events[event_type]["ip_address"] = ip_address

    expire_timer = Timer(5, expire_ping_for_event, args=[event_type])
    timers['pinged'][event_type] = expire_timer
    expire_timer.start()

def get_ping_time_from_ping_and_pong(event_type, ip_address):
    pong_time = time.time()
    global timers, pinged_events
    event_data = pinged_events.get(event_type, {})

    if not event_data:
        return False
    if event_data.get("ip_address") != ip_address:
        return False
    if "ping_time" not in event_data:
        return False
    
    ping_time = pong_time - pinged_events[event_type]["ping_time"]
    cancel_ping_timer(event_type)
    expire_ping_for_event(event_type)
    ping_time = ping_time * 1000
    ping_time = round(ping_time)
    return ping_time

def expire_event(event, ip_address):
    for d in (is_a_recent_ip_for_event, timers):
        if event in d and ip_address in d[event]:
            del d[event][ip_address]
            if not d[event]:
                del d[event]

def event_spam_protection(event, ip_address):
    if event in timers:
        if ip_address in timers[event]:
            timers[event][ip_address].cancel()
    else:
        timers[event] = {}
    if event not in is_a_recent_ip_for_event:
        is_a_recent_ip_for_event[event] = {}
    is_a_recent_ip_for_event[event][ip_address] = True
    timer = Timer(5, expire_event, args=[event, ip_address])
    timers[event][ip_address] = timer
    timer.start()

def toggle_disconnect_button(enable: bool):
    if 'disconnect_button' in globals() and disconnect_button.winfo_exists():
        current_state = disconnect_button.cget("state")
        desired_state = tk.NORMAL if enable else tk.DISABLED
        if current_state != desired_state:
            disconnect_button.config(state=desired_state)

def wait_for_end_of_wd_event():
    global ip_address_for_current_event, wd_event_thread_active
    while True:
        current_time = time.time()
        time_since_last_activity = current_time - last_event_activity_time
        remaining_time = SECS_TO_DISPLAY_CURRENT_EVENT_FOR - time_since_last_activity
        if current_time - last_event_activity_time > SECS_TO_DISPLAY_CURRENT_EVENT_FOR:
            ip_address_for_current_event = None
            in_game_overlay.update_content("")
            if log_current_event_to_file:
                with open(CURRENT_EVENT_FILE, "w"):
                     pass
            toggle_disconnect_button(False)
            wd_event_thread_active = False
            break
        time.sleep(min(remaining_time, 1))

def active_wd_event(ip_address):
    global ip_address_for_current_event, last_event_activity_time, wd_event_thread_active
    last_event_activity_time = time.time()
    ip_address_for_current_event = ip_address
    if not wd_event_thread_active:
        wd_event_thread_active = True
        wait_for_end_of_wd_event_thread = Thread(target=wait_for_end_of_wd_event)
        wait_for_end_of_wd_event_thread.daemon = True
        wait_for_end_of_wd_event_thread.start()

def handle_packet(event, ip_address):
    if is_a_recent_ip_for_event.get(event, {}).get(ip_address, False):
        event_spam_protection(event, ip_address)
        return
    event_spam_protection(event, ip_address)

    if event == "contract_send":
        wd_event_type = "contract"
        get_ping_from_event(wd_event_type, ip_address)
        return
    
    elif event == "contract_receive":
        wd_event_type = "contract"
        ping_time = get_ping_time_from_ping_and_pong(wd_event_type, ip_address)
        if not ping_time:
            return
        active_wd_event(ip_address)
        overlay_content = "Contract"

    elif event == "invasion_send":
        wd_event_type = "invading"
        get_ping_from_event(wd_event_type, ip_address)
        return
    
    elif event == "invasion_receive":
        wd_event_type = "invading"
        ping_time = get_ping_time_from_ping_and_pong(wd_event_type, ip_address)
        if not ping_time:
            return
        active_wd_event(ip_address)
        overlay_content = "Invading"

    elif event == "invaded_send":
        wd_event_type = "invaded!"
        get_ping_from_event(wd_event_type, ip_address)
        return
    
    elif event == "invaded_receive":
        wd_event_type = "invaded!"
        ping_time = get_ping_time_from_ping_and_pong(wd_event_type, ip_address)
        if not ping_time:
            return
        active_wd_event(ip_address)
        overlay_content = "INVADED!"
        if reveal_the_invader_enabled:
            reload_thread = Thread(target=reload_last_autosave, args=(ping_time,))
            reload_thread.start()
        if ntfy_enabled:
            ntfy_title = "INVADED!"
            ntfy_data = f"{ping_time}"
            notification_thread = Thread(target=send_ntfy_notification, args=(ntfy_data, ntfy_title))
            notification_thread.start()

    elif event == "scanned":
        wd_event_type = "scanned!"
        active_wd_event(ip_address)
        overlay_content = "SCANNED!"

    if audio_events.get(wd_event_type, {}).get('file') and audio_events.get(wd_event_type, {}).get('enabled', tk.BooleanVar()).get():
        play_audio_file(wd_event_type)

    if wd_event_type != "scanned!":
        overlay_content += f"\nPing: {ping_time}"

    in_game_overlay.update_content(overlay_content)
    if log_current_event_to_file:
        with open(CURRENT_EVENT_FILE, "w", encoding="utf-8") as logfile:
            logfile.write(overlay_content)

    toggle_disconnect_button(event in ["invaded_receive", "invasion_receive"])

def main_packet_handler(packet):
    global last_event_activity_time
    try:
        if stop_sniffing.is_set():
            return
        payload = bytes(packet[UDP].payload)
        if packet[IP].src == capture_device_local_ip_address:
            if b'\x90\x00\x00\x00\x00\x10c0\x00\x00\x00\x08\xbb~ \xe0' in payload:
                handle_packet("contract_send", packet[IP].dst)
            elif b'\x00\x00\x10c0\x00\x00\x00\x08\xbb~ \xe0G' in payload:
                handle_packet("invasion_send", packet[IP].dst)
            elif b'\x10c0\x00\x00\x00\x08\xbb~ \xe0G' in payload:
                handle_packet("invaded_send", packet[IP].dst)
            elif ip_address_for_current_event == packet[IP].dst:
                last_event_activity_time = time.time()
        elif packet[IP].dst == capture_device_local_ip_address:
            if b'\x90\x00\x00\x00\x00\x10c0\x00\x00\x00\x08\xbb~ \xe0' in payload:
                handle_packet("scanned", packet[IP].src)
            elif b'\xa0\x00\x00\x00\x00\x10c0\x00\x00\x00\x08\xbb~ \xe0' in payload:
                handle_packet("contract_receive", packet[IP].src)
            elif b'\x00\x00\x10c0\x00\x00\x00\x08\xbb~ \xe0G' in payload:
                pass
            elif b'\x10c0\x00\x00\x00\x08\xbb~ \xe0G' in payload:
                handle_packet("invasion_receive", packet[IP].src)
            elif b'\x0f\xff\xff\xff\xf8\x00\x00\x04\x80' in payload:
                handle_packet("invaded_receive", packet[IP].src)
            elif ip_address_for_current_event == packet[IP].src:
                last_event_activity_time = time.time()
    except Exception as e:
        log_if_enabled(f"An error occurred in main_packet_handler: {e}")

def capture_packets():
    stop_sniffing.clear()
    packet_handler = main_packet_handler
    while not stop_sniffing.is_set():
        try:
            sniff(
                iface=network_interface, 
                prn=packet_handler, 
                filter=f"udp port 9000 and not net 203.132.26.0/24", 
                store=0, 
                timeout=1
            )
        except OSError as e:
            log_if_enabled(f"An OSError occurred during packet sniffing. {e}")
    root.after(90, lambda: wdin_button.config(state=tk.NORMAL))

def toggle_capture_on():
    if allow_vpn_server_switching:
        global monitor_ip_change
        monitor_ip_change = IP_Address_Change_Detector()
        monitor_ip_change.start()
    wdin_button.config(state=tk.DISABLED)
    global capture_is_on
    capture_is_on = True
    if display_reveal_the_invader_button_on_gui or display_anti_afk_button_on_gui or display_ntfy_button_on_gui:
        wdin_label.config(text="✔️", fg="green")
    else:
        wdin_label.config(text="WDIN ENABLED", fg="green")
    capture_thread = Thread(target=capture_packets)
    capture_thread.daemon = True
    capture_thread.start()
    root.after(90, lambda: wdin_button.config(state=tk.NORMAL))

def toggle_capture_off():
    if allow_vpn_server_switching:
        global monitor_ip_change
        if monitor_ip_change:
            monitor_ip_change.stop()
    wdin_button.config(state=tk.DISABLED)
    global capture_is_on
    capture_is_on = False
    if display_reveal_the_invader_button_on_gui or display_anti_afk_button_on_gui:
        wdin_label.config(text="❌", fg="red")
    else:
        wdin_label.config(text="WDIN DISABLED", fg="red")
    stop_sniffing.set()  # wdin_button is re-enabled with stop_sniffing.set()

def toggle_capture_button():
    if not capture_is_on:
        verify_that_all_audio_files_exist_and_remove_those_that_do_not()
        if not network_interface:
            messagebox.showerror("Error", "You must specify a network interface to use.")
            return
        elif not network_interface_is_still_valid():
            return
        else:
            toggle_capture_on()
    else:
        toggle_capture_off()

def select_audio(event):
    filename = filedialog.askopenfilename(filetypes=[("Audio files", "*.mp3 *.wav *.ogg")])
    if filename:
        if hasattr(sys, 'frozen'):
            script_dir = os.path.dirname(sys.executable)
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
        
        relative_path = os.path.relpath(filename, script_dir)
        if not relative_path.startswith(".."):
            filename = relative_path

        if event not in audio_events:
            audio_events[event] = {'file': filename, 'volume': 0.5, 'enabled': tk.BooleanVar(value=True)}
        
        audio_events[event]['file'] = filename
        audio_events[event]['volume'] = audio_events[event].get('volume', 0.5)
        
        if audio_events[event]['enabled'] is None or not isinstance(audio_events[event]['enabled'], tk.BooleanVar): 
            audio_events[event]['enabled'] = tk.BooleanVar(value=True)
        
        update_audio_button(event)
        save_config()

def get_friendly_names():
    interfaces = get_if_list()
    friendly_names = []
    for iface in interfaces:
        try:
            wmi_query = f"SELECT * FROM Win32_NetworkAdapter WHERE NetConnectionID != NULL"
            for nic in wmi_client.query(wmi_query):
                if nic.GUID and iface.endswith(nic.GUID):
                    friendly_name = f"{nic.Name}"
                    friendly_names.append((iface, friendly_name))
                    break
        except Exception as e:
            friendly_name = iface
            friendly_names.append((iface, friendly_name))
    return friendly_names

def show_network_interface_window():
    global interface_window
    if interface_window is not None and interface_window.winfo_exists():
        interface_window.lift()
        return
    interface_window = Toplevel(root)
    interface_window.title("Select Network Interface")
    interface_window.geometry("600x250")
    interface_label = tk.Label(interface_window, text="Available Network Interfaces:")
    interface_label.pack(pady=5)
    frame = tk.Frame(interface_window)
    frame.pack(fill=tk.BOTH, expand=True)
    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
    interface_listbox = tk.Listbox(frame, height=10, width=60, yscrollcommand=scrollbar.set)
    scrollbar.config(command=interface_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    interface_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    friendly_names = get_friendly_names()
    for iface, friendly_name in friendly_names:
        display_name = f"{iface} ({friendly_name})"
        interface_listbox.insert(tk.END, display_name)

    def select_interface():
        global network_interface, capture_device_local_ip_address
        selected_index = interface_listbox.curselection()
        network_interface = friendly_names[selected_index[0]][0]
        selected_interface_label.config(text=friendly_names[selected_index[0]][1])
        interface_window.destroy()
        save_config()
        capture_device_local_ip_address = get_local_ip_address_by_friendly_name(friendly_names[selected_index[0]][1])

    select_interface_button = tk.Button(interface_window, text="Select Interface", command=select_interface)
    select_interface_button.pack(pady=5)

def play_audio_file(event):
    if audio_events.get(event, {}).get('file'):
        file_path = audio_events[event]['file']
        if not os.path.exists(file_path): 
            clear_audio(event)
            return
        sound = mixer.Sound(file_path)
        sound.set_volume(audio_events[event].get('volume', 0.5))
        sound.play()

def set_volume(event):
    current_volume = int(audio_events.get(event, {}).get('volume', 0.5) * 100)
    volume = tk.simpledialog.askinteger(
        "Volume",
        f"Set volume for {event} SFX (1 to 100):",
        initialvalue=current_volume,
        minvalue=1,
        maxvalue=100
    )
    if volume is not None:
        audio_events[event]['volume'] = volume / 100.0
        save_config()

def show_info(event):
    if event == "invaded!":
        info_message = "This sound effect will play when another player has invaded your game via Online Hacking or Online Tailing."
    elif event == "scanned!":
        info_message = "This sound effect will play when another player has your name appear as they are searching for players to begin an Online Hacking invasion on -or- they just started an Online Tailing on you. If Online Hacking, it does not mean that they have accepted the Online Hacking contract (that is what the \"invaded!\" sound effect is for)."
    elif event == "contract":
        info_message = "This sound effect will play when a players name appears on your Online Hacking player search -or- your game has just found an Online Tailing target."
    elif event == "invading":
        info_message = "This sound effect will play when you invade another players game via Online Hacking -or- Online Tailing."

    messagebox.showinfo(f"{event.capitalize()} Sound Notification", info_message)

def update_audio_button(event):
    frame = audio_labels[event].master

    destroy_audio_frame(frame)
    
    filename = os.path.basename(audio_events[event]['file'])
    final_filename_for_gui = (filename[:18] + '...') if len(filename) > 21 else filename
    audio_labels[event].config(text=final_filename_for_gui)
    
    if audio_events[event]['enabled'] is None:
        audio_events[event]['enabled'] = tk.BooleanVar(value=True)

    play_button = tk.Button(
        frame,
        text="▶",
        command=lambda t=event: play_audio_file(t)
    )
    play_button.pack(side='left', padx=1, before=audio_labels[event])
    
    volume_button = tk.Button(
        frame,
        text="🔊",
        command=lambda t=event: set_volume(t)
    )
    volume_button.pack(side='left', padx=1, before=audio_labels[event])
    
    clear_button = tk.Button(
        frame,
        text="X",
        command=lambda t=event: clear_audio(t)
    )
    clear_button.pack(side='left', padx=(0, 3), after=audio_labels[event])
    
    checkbox = tk.Checkbutton(
        frame,
        variable=audio_events[event]['enabled'],
        onvalue=True,
        offvalue=False,
        command=save_config
    )
    checkbox.pack(side='left', padx=1, after=audio_labels[event])

def destroy_audio_frame(frame):
    for widget in frame.winfo_children():
        if isinstance(widget, tk.Button) and widget.cget("text") in ["▶", "🔊", "X"]:
            widget.destroy()
        elif isinstance(widget, tk.Checkbutton):
            widget.destroy()

def clear_audio(event):
    if event in audio_events:
        del audio_events[event]
    audio_labels[event].config(text="No file selected")
    destroy_audio_frame(audio_labels[event].master)
    save_config()

toggle_firewall_on_cmd = (
            'netsh advfirewall firewall add rule name="WDIN - Block Watch Dogs Online" dir=in action=block protocol=UDP localport=9000 enable=yes & '
            'netsh advfirewall firewall add rule name="WDIN - Block Watch Dogs Online" dir=out action=block protocol=UDP localport=9000 enable=yes'
        )
toggle_firewall_off_cmd = (
            'netsh advfirewall firewall delete rule name="WDIN - Block Watch Dogs Online"'
        )

def toggle_firewall_rules():
    global firewall_block
    firewall_block = not firewall_block
    
    if 'online_toggle_status_label' in globals() and online_toggle_status_label.winfo_exists():
        root.after(0, lambda: (
            online_toggle_status_label.config(
                text="OFFLINE" if firewall_block else "✔️",
                fg="red" if firewall_block else "green"
            ),
        ))
    if firewall_block:
        cmd = toggle_firewall_on_cmd
        in_game_overlay.update_content("OFFLINE")
        if log_current_event_to_file:
            with open(CURRENT_EVENT_FILE, "w", encoding="utf-8") as logfile:
                logfile.write("OFFLINE")
    else:
        cmd = toggle_firewall_off_cmd
        in_game_overlay.update_content("")
        if log_current_event_to_file:
            with open(CURRENT_EVENT_FILE, "w"):
                 pass
    return run_elevated_command(cmd)

def toggle_online_status_button():
    def worker():
        if 'online_toggle_button' in globals() and online_toggle_button.winfo_exists():
            online_toggle_button.config(state=tk.DISABLED)

        toggle_firewall_rules()

        if 'online_toggle_button' in globals() and online_toggle_button.winfo_exists():
            root.after(90, lambda: online_toggle_button.config(state=tk.NORMAL))

    Thread(target=worker, daemon=True).start()

def disconnect_from_online_session_cmd(ip_address):
    cmd = (
        f'netsh advfirewall firewall add rule name="WDIN - Block Watch Dogs Online" dir=in action=block protocol=UDP localport=9000 remoteip={ip_address} enable=yes & '
        f'netsh advfirewall firewall add rule name="WDIN - Block Watch Dogs Online" dir=out action=block protocol=UDP localport=9000 remoteip={ip_address} enable=yes & '
        'timeout /t 7 /nobreak & '
        'netsh advfirewall firewall delete rule name="WDIN - Block Watch Dogs Online"'
    )
    return run_elevated_command(cmd)

def disconnect_from_online_session():
    if firewall_block or ip_address_for_current_event == None:
        return
    
    def worker():
        global firewall_block
        firewall_block = True

        if 'disconnect_button' in globals() and disconnect_button.winfo_exists():
            disconnect_button.config(state=tk.DISABLED)
        if 'online_toggle_button' in globals() and online_toggle_button.winfo_exists():
            online_toggle_button.config(state=tk.DISABLED)
        if 'online_toggle_status_label' in globals() and online_toggle_status_label.winfo_exists():
            root.after(0, lambda: online_toggle_status_label.config(text="DISCONNECT", fg="red"))

        current_content = in_game_overlay.current_content
        new_content = f"{current_content}\n_CONNECTION_INTERRUPTED"
        in_game_overlay.update_content(new_content)

        disconnect_from_online_session_cmd(ip_address_for_current_event)

        if 'online_toggle_status_label' in globals() and online_toggle_status_label.winfo_exists():
            root.after(0, lambda: online_toggle_status_label.config(text="✔️", fg="green"))
        if 'online_toggle_button' in globals() and online_toggle_button.winfo_exists():
            online_toggle_button.config(state=tk.NORMAL)
        
        firewall_block = False

    Thread(target=worker, daemon=True).start()

def run_elevated_command(cmd):
    try:
        if admin:
            subprocess.run(cmd, shell=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", "cmd.exe", f'/c "{cmd}"', None, 0
            )
        return True
    except subprocess.CalledProcessError as e:
        log_if_enabled(f"Command failed with return code {e.returncode}: {e.output}")
        return False
    except Exception as e:
        log_if_enabled(f"Command execution failed: {e}")
        return False

def get_safe_font(master_window, font_name='Arial'):
    if not isinstance(font_name, str):
        return 'Arial'
    
    available_fonts = font.families(master_window)
    if font_name in available_fonts:
        return font_name
    else:
         messagebox.showerror(
            "Error",
            f"Could not find the font \"{font_name}\". Using \"Arial\" for the in-game overlay instead.",
            parent=root
         )    
         return 'Arial'
    
# Enable AHK if anything requires it
def should_enable_ahk():
    return (
        disconnect_hotkey or toggle_online_hotkey or reload_last_autosave_hotkey or
        quit_invasion_hotkey or open_online_menu_hotkey or quit_invasion_then_open_online_menu_hotkey or
        display_reveal_the_invader_button_on_gui or reveal_the_invader_enabled or
        display_anti_afk_button_on_gui or anti_afk_enabled
    )
###############################################################################
############## MAIN SCRIPT START ##############################################
###############################################################################

def main():
    global network_interface, network_interface_friendly_name, capture_device_local_ip_address
    global stop_sniffing, capture_is_on, monitor_ip_change
    global log_current_event_to_file
    global wd_active_window, wd_hwnd, last_checked_hwnd, first_window_check
    global overlay_custom_font, overlay_font_size, overlay_left_offset, overlay_top_offset, overlay_background_opacity, in_game_overlay
    global is_a_recent_ip_for_event, pinged_events, timers, ip_address_for_current_event, last_event_activity_time, wd_event_thread_active, SECS_TO_DISPLAY_CURRENT_EVENT_FOR, CURRENT_EVENT_FILE
    global add_contract_audio_option, add_invading_audio_option, display_disconnect_button_on_gui, display_online_toggle_button_on_gui, display_reveal_the_invader_button_on_gui, display_anti_afk_button_on_gui, display_ntfy_button_on_gui, shrink_gui_at_startup_to_hide_network_option, shrink_gui_at_startup_to_hide_audio_options
    global audio_labels, audio_buttons, audio_files, audio_events, volume_settings, wd_event_types_dic
    global reveal_the_invader_enabled, reloading_last_autosave, reloading_last_autosave_delay
    global anti_afk_enabled, anti_afk_timeout, keyboard_listener, stop_anti_afk_timeout, last_keyboard_activity_time, kbd_controller, AFK_INACTIVITY_THRESHOLD, last_afk_key_pressed
    global ntfy_enabled, ntfy_mytopic, ntfy_priority
    global autohotkeys, disconnect_hotkey, toggle_online_hotkey, reload_last_autosave_hotkey, quit_invasion_hotkey, open_online_menu_hotkey, quit_invasion_then_open_online_menu_hotkey, reload_last_autosave_ahk_script, quit_invasion_ahk_script, open_online_menu_ahk_script, quit_invasion_then_open_online_menu_ahk_script, hotkeys_started
    global ICON_PATH, ANSI_ESCAPE, firewall_block, allow_vpn_server_switching
    global root, wmi_client, interface_window, selected_interface_label, ahk, wdin_button, wdin_label, disconnect_button, online_toggle_button, online_toggle_status_label, reveal_button, reveal_label, anti_afk_button, anti_afk_label, ntfy_button, ntfy_label
    
    # Miscellaneous
    ICON_PATH = resource_path(os.path.join('bin', 'icon.ico'))
    ANSI_ESCAPE = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    stop_sniffing = Event()
    stop_anti_afk_timeout = Event()
    
    ###############################################################################
    ############## LOAD MOST CONFIG_FILE SETTINGS #################################
    ###############################################################################
    
    # Network settings
    network_interface = get_config_value(config, ['network_interface'], "")
    
    # Logging settings
    log_current_event_to_file = get_config_value(config, ['logging', 'log_current_event_to_current_event_txt_file'], True)
    
    # In game overlay settings
    overlay_custom_font = get_config_value(config, ['display_current_event_in_game', 'font'], "Arial")
    overlay_font_size = get_config_value(config, ['display_current_event_in_game', 'font_size'], 20)
    overlay_left_offset = get_config_value(config, ['display_current_event_in_game', 'left_offset'], 4)
    overlay_top_offset = get_config_value(config, ['display_current_event_in_game', 'top_offset'], 4)
    overlay_background_opacity = get_config_value(config, ['display_current_event_in_game', 'background_opacity_percent'], 70)
    
    # GUI settings
    add_contract_audio_option = get_config_value(config, ['extra_gui_options', 'add_audio_option_for_your_own_hacking_contracts'], False)
    add_invading_audio_option = get_config_value(config, ['extra_gui_options', 'add_audio_option_for_when_you_are_the_invader'], False)
    display_disconnect_button_on_gui = get_config_value(config, ['extra_gui_options', 'disconnect_from_online_session_gui_button'], True)
    display_online_toggle_button_on_gui = get_config_value(config, ['extra_gui_options', 'online_toggle_gui_button'], True)
    display_reveal_the_invader_button_on_gui = get_config_value(config, ['extra_gui_options', 'automatically_reveal_the_invader', 'gui_button'], False)
    display_anti_afk_button_on_gui = get_config_value(config, ['extra_gui_options', 'anti_afk_timeout', 'gui_button'], False)
    display_ntfy_button_on_gui = get_config_value(config, ['extra_gui_options', 'send_invaded_notification_to_ntfy', 'gui_button'], False)
    shrink_gui_at_startup_to_hide_network_option = get_config_value(config, ['extra_gui_options', 'shrink_gui_at_startup_to_hide_network_option'], False)
    shrink_gui_at_startup_to_hide_audio_options = get_config_value(config, ['extra_gui_options', 'or_shrink_gui_at_startup_to_hide_audio_and_network_options'], False)
    if shrink_gui_at_startup_to_hide_audio_options:
        shrink_gui_at_startup_to_hide_network_option = True
    
    # Invader reveal settings
    reveal_the_invader_enabled = get_config_value(config, ['extra_gui_options', 'automatically_reveal_the_invader', 'enabled_state'], False)
    reloading_last_autosave_delay = get_config_value(config, ['extra_gui_options', 'automatically_reveal_the_invader', 'added_delay_in_seconds_before_starting'], 0)
    
    # Anti-AFK settings
    anti_afk_enabled = get_config_value(config, ['extra_gui_options', 'anti_afk_timeout', 'enabled_state'], False)
    
    # NTFY settings
    ntfy_enabled = get_config_value(config, ['extra_gui_options', 'send_invaded_notification_to_ntfy', 'enabled_state'], False)
    ntfy_mytopic = get_config_value(config, ['extra_gui_options', 'send_invaded_notification_to_ntfy', 'mytopic'], "")
    ntfy_priority = get_config_value(config, ['extra_gui_options', 'send_invaded_notification_to_ntfy', 'priority'], "4")
    
    # Hotkeys
    disconnect_hotkey = get_config_value(config, ['in_game_ahk_style_hotkeys', 'disconnect_from_online_session'], "")
    toggle_online_hotkey = get_config_value(config, ['in_game_ahk_style_hotkeys', 'toggle_online_services'], "")
    reload_last_autosave_hotkey = get_config_value(config, ['in_game_ahk_style_hotkeys', 'reload_last_autosave_keypresses'], "")
    quit_invasion_hotkey = get_config_value(config, ['in_game_ahk_style_hotkeys', 'quit_invasion_keypresses'], "")
    open_online_menu_hotkey = get_config_value(config, ['in_game_ahk_style_hotkeys', 'open_online_menu_keypresses'], "")
    quit_invasion_then_open_online_menu_hotkey = get_config_value(config, ['in_game_ahk_style_hotkeys', 'quit_invasion_then_open_online_menu_keypresses'], "")
    
    if reload_last_autosave_hotkey:
        reload_last_autosave_ahk_script = """
            Send, {Esc}
            Sleep, 160
            Loop, 3 {
                Send, {Down down}
                Sleep, 5
                Send, {Down up}
                Sleep, 5
            }
            Send, {Enter}
            Sleep, 5
            Send, {Enter}
            Sleep, 5
        """
    
    if quit_invasion_hotkey:
        quit_invasion_ahk_script = """
            Send, {Esc}
            Sleep, 160
            Send, {Down down}
            Sleep, 5
            Send, {Down up}
            Sleep, 5
            Send, {Enter}
            Sleep, 5
            Send, {Enter}
            Sleep, 5
        """
    
    if open_online_menu_hotkey:
        open_online_menu_ahk_script = """
            Send, {MButton}
            Sleep, 160
            Send, {Down down}
            Sleep, 5
            Send, {Down up}
            Sleep, 5
            Send, {Enter}
            Sleep, 5
        """
    
    if quit_invasion_then_open_online_menu_hotkey:
        quit_invasion_then_open_online_menu_ahk_script = """
            Send, {Esc}
            Sleep, 160
            Send, {Down down}
            Sleep, 5
            Send, {Down up}
            Sleep, 5
            Send, {Enter}
            Sleep, 5
            Send, {Enter}
            Sleep, 100
            Send, {MButton}
            Sleep, 160
            Send, {Down down}
            Sleep, 5
            Send, {Down up}
            Sleep, 5
            Send, {Enter}
            Sleep, 5
        """
    
    autohotkeys = {
        "disconnect": (disconnect_hotkey, disconnect_from_online_session) if admin and disconnect_hotkey else None,
        "toggle_online": (toggle_online_hotkey, toggle_firewall_rules) if admin and toggle_online_hotkey else None,
        "reload_autosave": (reload_last_autosave_hotkey, reload_last_autosave) if reload_last_autosave_hotkey else None,
        "quit_invasion": (quit_invasion_hotkey, quit_invasion) if quit_invasion_hotkey else None,
        "open_online_menu": (open_online_menu_hotkey, open_online_menu) if open_online_menu_hotkey else None,
        "quit_invasion_then_open_online_menu": (quit_invasion_then_open_online_menu_hotkey, quit_invasion_then_open_online_menu) if quit_invasion_then_open_online_menu_hotkey else None
    }
    
    autohotkeys = {name: value for name, value in autohotkeys.items() if value is not None}

  # autohotkeys = {}
    if admin and disconnect_hotkey:
        autohotkeys["disconnect"] = (disconnect_hotkey, disconnect_from_online_session)
    if admin and toggle_online_hotkey:
        autohotkeys["toggle_online"] = (toggle_online_hotkey, toggle_firewall_rules)
    if reload_last_autosave_hotkey:
        autohotkeys["reload_autosave"] = (reload_last_autosave_hotkey, reload_last_autosave)
    if quit_invasion_hotkey:
        autohotkeys["quit_invasion"] = (quit_invasion_hotkey, quit_invasion)
    if open_online_menu_hotkey:
        autohotkeys["open_online_menu"] = (open_online_menu_hotkey, open_online_menu)
    if quit_invasion_then_open_online_menu_hotkey:
        autohotkeys["quit_invasion_then_open_online_menu"] = (quit_invasion_then_open_online_menu_hotkey, quit_invasion_then_open_online_menu)

    if should_enable_ahk():
        ahk_path = resource_path(os.path.join('bin', 'AutoHotkey.exe'))
        ahk = AHK(executable_path=ahk_path)
        for name, (key, callback) in autohotkeys.items():
            if key:
                ahk.add_hotkey(key, callback=callback)
    
    # Other settings
    allow_vpn_server_switching = get_config_value(config, ['allow_vpn_server_switching'], False)
    
    # Audio events setting
    wd_event_types_dic = ["scanned!", "invaded!"]
    if add_contract_audio_option:
        wd_event_types_dic.append("contract")
    if add_invading_audio_option:
        wd_event_types_dic.append("invading")
    
    if 'audio_events' not in config:
        config['audio_events'] = {}
    
    def populate_audio_settings(event_name):
        if event_name in get_config_value(config, ['audio_events'], {}):
            audio_files[event_name] = get_config_value(config, ['audio_events', event_name, 'file'], "")
            volume_settings[event_name] = get_config_value(config, ['audio_events', event_name, 'volume'], 0.5)
            audio_events[event_name] = get_config_value(config, ['audio_events', event_name, 'enabled'], False)
    
    for event_name in wd_event_types_dic:
        populate_audio_settings(event_name)
    
    default_audio_files = {
        "scanned!": "mgs-alert.mp3",
        "invaded!": "inception.mp3"
    }
    
    def get_default_sound_path(filename):
        sound_dir = os.path.join(APPDATA, "sounds")
        os.makedirs(sound_dir, exist_ok=True)
        return os.path.join(sound_dir, filename)

    for event_name, default_file in default_audio_files.items():
        if not audio_files.get(event_name):
            default_sound_path = get_default_sound_path(default_file)
            if os.path.exists(default_sound_path):
                config['audio_events'][event_name] = {
                    'file': default_sound_path,
                    'volume': 0.5,
                    'enabled': True
                }
                populate_audio_settings(event_name)
    
    if display_anti_afk_button_on_gui or anti_afk_enabled:
        stop_anti_afk_timeout = Event()
        kbd_controller = Controller()
        last_keyboard_activity_time = time.time()
    
    if display_ntfy_button_on_gui or ntfy_enabled:
        if not isinstance(ntfy_mytopic, str):
            print("Invalid 'mytopic' value for 'send_invaded_notification_to_ntfy'. Disabling NTFY.")
            display_ntfy_button_on_gui = False
            ntfy_enabled = False
        else:
            if not isinstance(ntfy_priority, str):
                ntfy_priority = str(ntfy_priority)
            if ntfy_priority not in ["1", "2", "3", "4", "5"]:
                ntfy_priority = "4"
    
    root = tk.Tk()
    root.title(f"WDIN {VERSION}")
    root.iconbitmap(ICON_PATH)
    
    overlay_custom_font = get_safe_font(root, get_config_value(config, ['display_current_event_in_game', 'font'], 'Arial'))
    
    default_width = 320
    default_height = 152
    
    if shrink_gui_at_startup_to_hide_audio_options:
        default_height -= 72
    else:
        if add_contract_audio_option: default_height += 35
        if add_invading_audio_option: default_height += 35
    if shrink_gui_at_startup_to_hide_network_option: default_height -= 35
    if display_reveal_the_invader_button_on_gui or display_anti_afk_button_on_gui or display_ntfy_button_on_gui: default_height -= 8
    if admin and (display_online_toggle_button_on_gui or display_disconnect_button_on_gui): default_height += 40
    
    root.geometry(f"{default_width}x{default_height}")
    
    start_frame = tk.Frame(root)
    start_frame.pack(pady=5, anchor='w')
    
    wdin_frame = tk.Frame(start_frame)
    wdin_frame.pack(side='left', padx=5)
    
    wdin_button = tk.Button(wdin_frame, text="WDIN", command=toggle_capture_button)
    wdin_button.pack(side='left')
    
    if display_reveal_the_invader_button_on_gui or display_anti_afk_button_on_gui or display_ntfy_button_on_gui:
        wdin_label = tk.Label(wdin_frame, text="❌", font=("Arial", 13), fg="red")
        wdin_label.pack(side='left', padx=0)
    else:
        wdin_label = tk.Label(wdin_frame, text="WDIN DISABLED", font=("Arial", 18, "bold"), fg="red")
        wdin_label.pack(side='left', padx=10)
    
    def create_button_with_label(frame, button_text, button_command, label_text, label_font=("Arial", 13), label_fg="red"):
        button_frame = tk.Frame(frame)
        button_frame.pack(side='left', padx=5)
        button = tk.Button(button_frame, text=button_text, command=button_command)
        button.pack(side='left')
        label = tk.Label(button_frame, text=label_text, font=label_font, fg=label_fg)
        label.pack(side='left', padx=1)
        return button, label
    
    if display_reveal_the_invader_button_on_gui:
        reveal_label_text = "✔️" if reveal_the_invader_enabled else "❌"
        reveal_label_fg = "green" if reveal_the_invader_enabled else "red"
        reveal_button, reveal_label = create_button_with_label(
            start_frame, "REVL", toggle_auto_reveal_the_invader, reveal_label_text, label_fg=reveal_label_fg
        )
    
    if display_anti_afk_button_on_gui:
        anti_afk_label_text = "✔️" if anti_afk_enabled else "❌"
        anti_afk_label_fg = "green" if anti_afk_enabled else "red"
        anti_afk_button, anti_afk_label = create_button_with_label(
            start_frame, "AAFK", toggle_anti_afk, anti_afk_label_text, label_fg=anti_afk_label_fg
        )
    
    if display_ntfy_button_on_gui:
        ntfy_label_text = "✔️" if ntfy_enabled else "❌"
        ntfy_label_fg = "green" if ntfy_enabled else "red"
        ntfy_button, ntfy_label = create_button_with_label(
            start_frame, "NTFY", toggle_ntfy_notification, ntfy_label_text, label_fg=ntfy_label_fg
        )
    
    if admin and (display_online_toggle_button_on_gui or display_disconnect_button_on_gui):
        online_toggle_frame = tk.Frame(root)
        online_toggle_frame.pack(pady=5, anchor='w')
        
        if display_disconnect_button_on_gui:
            disconnect_button = tk.Button(
                online_toggle_frame,
                text="DISCONNECT",
                command=disconnect_from_online_session,
                state=tk.DISABLED
            )
            disconnect_button.pack(side='left', padx=5)
    
        if display_online_toggle_button_on_gui:
            online_toggle_button = tk.Button(
                online_toggle_frame,
                text="WD ONLINE",
                command=toggle_online_status_button
            )
            online_toggle_button.pack(side='left', padx=5)
            online_toggle_status_label = tk.Label(
                online_toggle_frame,
                text="✔️",
                fg="green",
                font=('Arial', 14, 'bold')
            )
            online_toggle_status_label.pack(side=tk.LEFT)
    
    def setup_audio_event(frame, event, config):
        audio_buttons[event] = tk.Button(
            frame,
            text=f"{event.capitalize()}",
            command=lambda t=event: select_audio(t)
        )
        audio_buttons[event].pack(side='left', padx=(5, 0))
        audio_labels[event] = tk.Label(frame, text="No file selected", wraplength=350)
        audio_labels[event].pack(side='left', padx=5)
        info_button = tk.Button(
            frame,
            text="?",
            command=lambda t=event: show_info(t)
        )
        info_button.pack(side='left', padx=3)
        filepath = config.get('audio_events', {}).get(event, {}).get('file')
        if filepath:
            audio_events[event] = {'file': filepath, 'volume': 0.5, 'enabled': True}
            if os.path.exists(filepath):
                event_config = config.get('audio_events', {}).get(event, {})
                audio_events[event]['volume'] = event_config.get('volume', 0.5)
                enabled_value = event_config.get('enabled', True)
                audio_events[event]['enabled'] = tk.BooleanVar(value=enabled_value)
                update_audio_button(event)
            else:
                clear_audio(event)
        else:
            audio_labels[event].config(text="No file selected")
    
    for event in wd_event_types_dic:
        frame = tk.Frame(root)
        frame.pack(pady=5, anchor='w')
        setup_audio_event(frame, event, config)
    
    interface_frame = tk.Frame(root)
    interface_frame.pack(pady=5, anchor='w')
    interface_button = tk.Button(interface_frame, text="Network", command=show_network_interface_window)
    interface_button.pack(side='left', padx=5)
    selected_interface_label = tk.Label(interface_frame, text="No interface selected")
    selected_interface_label.pack(side='left', padx=0)
    interface_window = None
    
    wmi_client = wmi.WMI()
    for iface, friendly_name in get_friendly_names():
        if network_interface == iface:
            network_interface_friendly_name = friendly_name
            selected_interface_label.config(text=network_interface_friendly_name)
            capture_device_local_ip_address = get_local_ip_address_by_friendly_name(network_interface_friendly_name)
    
    if network_interface:
        toggle_capture_button()
    
    if log_current_event_to_file:
        try:
            with open(CURRENT_EVENT_FILE, "w"):
                pass
        except PermissionError:
            try:
                os.remove(CURRENT_EVENT_FILE)
                with open(CURRENT_EVENT_FILE, "w"):
                    pass
            except PermissionError as e:
                log_if_enabled(f"[ERROR] Could not modify '{CURRENT_EVENT_FILE}' (read-only?): {e}")
    
    in_game_overlay = InGameOverlay(root)
    
    check_window_state_periodically()
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Detected Ctrl+C. Exiting.")
    finally:
        if firewall_block:
            run_elevated_command(toggle_firewall_off_cmd)