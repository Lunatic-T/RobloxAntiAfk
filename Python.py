import subprocess
import sys

def install_if_missing(import_name, pip_name=None):
    pip_name = pip_name or import_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"[INFO] Installing missing package: {pip_name}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

# Required packages
install_if_missing("pygetwindow")
install_if_missing("pyautogui")
install_if_missing("psutil")
install_if_missing("inputs")

# pywin32 covers both win32gui and win32process
try:
    import win32gui, win32process
except ImportError:
    print("[INFO] Installing pywin32 for win32gui and win32process")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])

# tkinter is built-in; warn if not found
try:
    import tkinter as tk
except ImportError:
    print("[WARNING] tkinter is not installed. You may need to reinstall Python with the Tcl/Tk option.")

# Rest of your imports (safe now)
import pygetwindow as gw
import win32gui
import time
import threading
import pyautogui
import subprocess
import sys
import psutil
import win32process
import tkinter as tk
import inputs

previous_window = None              # Variable to store the previously focused window
focus_enabled = False               # Whether the focus action is enabled
go = False                          # loop breaker if it cant find roblox, it only works when clicking stop 
transparencyshift = 0               # transparency mode 

def get_process_name_from_hwnd(hwnd):
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if not psutil.pid_exists(pid):
            return None
        return psutil.Process(pid).name()
    except Exception as e:
        print(f"Error fetching process name: {e}")
        return None
        
def is_target_window(process_names):
    hwnd = win32gui.GetForegroundWindow()
    process_name = get_process_name_from_hwnd(hwnd)
    return process_name in process_names
    
def antiafk(process_names):
    global previous_window
    try:
        previous_window = win32gui.GetForegroundWindow()
        
        def is_valid_window(w):
            return w.title and not w.isMinimized 
            
        all_windows = [w for w in gw.getAllWindows() if is_valid_window(w)]
        windows = [w for w in all_windows if get_process_name_from_hwnd(w._hWnd) in process_names]
        
        for w in gw.getAllWindows():
            if not w.isMinimized and w.title:
                proc_name = get_process_name_from_hwnd(w._hWnd)
                print(f"{w.title} => {proc_name}")
        
        if not windows:
            print("No active Roblox windows found.")
            return

        for window in windows:
            try:
                Rr = 0
                window.activate()
                while True:    
                    global go
                    Rr += 1 
                    if win32gui.GetForegroundWindow() == window._hWnd and go:
                        pyautogui.press('b')
                        pyautogui.keyUp('b')
                        print(f"prevented {window.title} from being kicked")
                        break
                    else: 
                        if not go:
                            break
                        print(f"Waiting For Roblox attempt {Rr}")
                        
            except Exception as e:
                print(f"Could not activate window: {e}")
        
        if previous_window and win32gui.IsWindow(previous_window):
            win32gui.SetForegroundWindow(previous_window)
            print("Set to Previous Window")
        else:
            print("Previous window was not valid, cannot refocus.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

def start():
    global focus_enabled
    global go 
    go = True 
    focus_enabled = True
    while focus_enabled:
        antiafk(["RobloxPlayerBeta.exe", "ApplicationFrameHost.exe"])

        time.sleep(300)  # Wait for 5 minutes (300 seconds)

def stop():
    global focus_enabled
    global go 
    focus_enabled = False
    go = False
    print("Stop")
    

def toggle():
    if focus_enabled:
        stop()
        toggle_button.config(text="AntiAfk: Off")
    else:
        threading.Thread(target=start, daemon=True).start()
        toggle_button.config(text="stop")

def start_move(event):
    root._drag_start_x = event.x_root
    root._drag_start_y = event.y_root

def do_move(event):
    dx = event.x_root - root._drag_start_x
    dy = event.y_root - root._drag_start_y
    x = root.winfo_x() + dx
    y = root.winfo_y() + dy
    root.geometry(f"+{x}+{y}")
    root._drag_start_x = event.x_root
    root._drag_start_y = event.y_root

def toggle_transparency():
    global transparencyshift
    transparency_levels = [1, 0.75, 0.5, 0.25]
    
    transparencyshift = (transparencyshift + 1) % len(transparency_levels)
    root.attributes('-alpha', transparency_levels[transparencyshift])


# ---------- Tkinter GUI setup ---------- 
root = tk.Tk()
root.geometry('247x24+50+50')
root.resizable(False, False)
root.attributes('-topmost', 1)
root.overrideredirect(True)
root.title("AntiIdle")

frame = tk.Frame(root, bg="gray20", height=30)
frame.pack(fill=tk.BOTH, expand=True)
frame.bind("<Button-1>", start_move)
frame.bind("<B1-Motion>", do_move)

close_btn = tk.Button(frame, text="X", command=root.destroy, bg="#222", fg="white", bd=0, font=("Segoe UI", 10, "bold"), takefocus=0, highlightthickness=0)
close_btn.place(x=203, y=2, width=20, height=20)

toggle_button = tk.Button(
    frame,
    text="start",
    command=toggle,
    bg="#222",           
    fg="white",          
    activebackground="#00b06f",  
    activeforeground="white",
    highlightthickness=0,
    bd=0,
    takefocus=0,              
    font=("Segoe UI", 10, "bold"),
    relief="flat",       
    cursor="hand2"
)
toggle_button.place(x=2, y=2,width=177, height=20)

# Transparency toggle button
transparency_button = tk.Button(
    frame,
    text="I",
    command=toggle_transparency,
    width=20,
    height=2,
    bg="#222",           
    fg="white",          
    activebackground="#00b06f",  
    activeforeground="white",
    highlightthickness=0,
    bd=0,
    takefocus=0,             
    font=("Segoe UI", 10, "bold"),
    relief="flat",       
    cursor="hand2"
)
transparency_button.place(x=181, y=2, width=20, height=20)

def on_transparency_button_enter(e):
    transparency_button.config(bg="#00b06f", fg="white")

def on_transparency_button_leave(e):
    transparency_button.config(bg="#222", fg="white")

# Hover effects for the toggle button
def on_toggle_button_enter(e):
    toggle_button.config(bg="#00b06f", fg="white")

def on_toggle_button_leave(e):
    toggle_button.config(bg="#222", fg="white")

# Hover effects for the close button
def on_close_button_enter(e):
    close_btn.config(bg="#00b06f", fg="white")

def on_close_button_leave(e):
    close_btn.config(bg="#222", fg="white")

# Bind hover effects to buttons
transparency_button.bind("<Enter>", on_transparency_button_enter)
transparency_button.bind("<Leave>", on_transparency_button_leave)

toggle_button.bind("<Enter>", on_toggle_button_enter)
toggle_button.bind("<Leave>", on_toggle_button_leave)

close_btn.bind("<Enter>", on_close_button_enter)
close_btn.bind("<Leave>", on_close_button_leave)


# Run the GUI
root.mainloop()
