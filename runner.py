#!/usr/bin/env python3
import os, subprocess, time, shutil, sys, argparse, threading

dir_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(dir_path)

# Parse port options
parser = argparse.ArgumentParser(description="Freebuff Desktop VNC Runner")
parser.add_argument("--vnc", type=int, default=5921, help="VNC Port (default: 5921)")
parser.add_argument("--web", type=int, default=6080, help="Web Port (default: 6080)")
args = parser.parse_args()

vnc_port = args.vnc
web_port = args.web

# Calculate dynamic X11 display number from vnc_port (e.g. 5921 -> :21, 5922 -> :22)
display_num = vnc_port - 5900
if display_num < 1 or display_num > 99:
    display_num = 21

display_str = f":{display_num}"

# Detach completely from parent subshell/task
pid = os.fork()
if pid > 0:
    print(f"Started daemon process PID: {pid}")
    sys.exit(0)

os.setsid()

# Ensure AppImage is extracted if missing on a new environment
squash_dir = os.path.join(dir_path, "squashfs-root")
appimage = os.path.join(dir_path, "Freebuff-Desktop.AppImage")

if not os.path.exists(squash_dir):
    if not os.path.exists(appimage):
        subprocess.run(f"curl -fsSL -L 'https://freebuff.com/api/desktop/download/linux' -o '{appimage}'", shell=True)
        subprocess.run(f"chmod +x '{appimage}'", shell=True)
    subprocess.run(f"'{appimage}' --appimage-extract >/dev/null 2>&1", shell=True)

# Clean up old display locks and processes
subprocess.run(f"pkill -f 'Xvnc {display_str}' || true", shell=True)
subprocess.run(f"pkill -f 'Xvfb {display_str}' || true", shell=True)
subprocess.run(f"pkill -f 'x11vnc.*{vnc_port}' || true", shell=True)
subprocess.run(f"pkill -f 'websockify.*{web_port}' || true", shell=True)
subprocess.run("pkill -f '@codebufffreebuff-desktop' || true", shell=True)
subprocess.run(f"rm -f /tmp/.X{display_num}-lock /tmp/.X11-unix/X{display_num}", shell=True)

time.sleep(1)

# Configure Fluxbox auto-maximize
fluxbox_dir = os.path.expanduser("~/.fluxbox")
os.makedirs(fluxbox_dir, exist_ok=True)
with open(os.path.join(fluxbox_dir, "apps"), "w") as f:
    f.write("""[app] (@codebufffreebuff-desktop)
  [Maximized] {yes}
  [Focus] {yes}
[end]
""")

# Configure Openbox auto-maximize
openbox_dir = os.path.expanduser("~/.config/openbox")
os.makedirs(openbox_dir, exist_ok=True)
with open(os.path.join(openbox_dir, "rc.xml"), "w") as f:
    f.write("""<?xml version="1.0" encoding="UTF-8"?>
<openbox_config xmlns="http://openbox.org/3.4/rc">
  <applications>
    <application name="@codebufffreebuff-desktop">
      <maximized>yes</maximized>
      <focus>yes</focus>
    </application>
  </applications>
</openbox_config>
""")

# 1. Locate or auto-install Xvnc / Xvfb
xvnc_bin = shutil.which("Xvnc") or ("/usr/bin/Xvnc" if os.path.exists("/usr/bin/Xvnc") else None)

if not xvnc_bin:
    subprocess.run("sudo apt-get update -qq && sudo apt-get install -y -qq tigervnc-standalone-server xvfb x11vnc fluxbox openbox wmctrl xdotool >/dev/null 2>&1 || true", shell=True)
    xvnc_bin = shutil.which("Xvnc") or ("/usr/bin/Xvnc" if os.path.exists("/usr/bin/Xvnc") else None)

if xvnc_bin and os.path.exists(xvnc_bin):
    xvnc_cmd = [
        xvnc_bin,
        display_str,
        "-geometry", "1440x900",
        "-depth", "16",
        "-rfbport", str(vnc_port),
        "-SecurityTypes", "None"
    ]
    with open(os.path.join(dir_path, "xvnc.log"), "w") as out:
        xvnc = subprocess.Popen(xvnc_cmd, stdout=out, stderr=out)
    time.sleep(2)
else:
    xvfb_bin = shutil.which("Xvfb") or "/usr/bin/Xvfb"
    subprocess.Popen([xvfb_bin, display_str, "-screen", "0", "1440x900x16"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    
    vnc_bin = shutil.which("x11vnc") or "/usr/bin/x11vnc"
    vnc_cmd = [
        vnc_bin,
        "-display", display_str,
        "-rfbport", str(vnc_port),
        "-forever",
        "-shared",
        "-nopw",
        "-noxdamage",
        "-repeat",
        "-wait", "5",
        "-defer", "5",
        "-nap",
        "-wireframe"
    ]
    with open(os.path.join(dir_path, "x11vnc.log"), "w") as out:
        x11vnc = subprocess.Popen(vnc_cmd, stdout=out, stderr=out)
    time.sleep(2)

# 2. Start window manager
wm_path = shutil.which("fluxbox") or shutil.which("openbox")
if wm_path:
    wm = subprocess.Popen([wm_path], env={**os.environ, "DISPLAY": display_str}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

# 3. Start websockify / noVNC on specified web port
web_bin = shutil.which("websockify") or "/usr/bin/websockify"
if web_bin and os.path.exists(web_bin):
    novnc = subprocess.Popen([web_bin, "--web=/usr/share/novnc/", str(web_port), f"localhost:{vnc_port}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

# 4. Start Freebuff Desktop App with 2D native X11 rendering
bin_dir = os.path.join(dir_path, "bin")
custom_path = f"{bin_dir}:{os.environ.get('PATH', '')}"

with open(os.path.join(dir_path, "freebuff-app.log"), "w") as out:
    env = {
        **os.environ,
        "PATH": custom_path,
        "DISPLAY": display_str,
        "APPDIR": squash_dir
    }
    cmd = [
        os.path.join(squash_dir, "@codebufffreebuff-desktop"),
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-gpu",
        "--disable-gpu-compositing",
        "--disable-accelerated-2d-canvas",
        "--disable-software-rasterizer",
        "--disable-dev-shm-usage"
    ]
    app = subprocess.Popen(cmd, env=env, stdout=out, stderr=out)

# 5. Background Auto-Raiser / Auto-Maximizer to guarantee NO black screen
def auto_raise_window():
    time.sleep(3)
    env = {**os.environ, "DISPLAY": display_str}
    for _ in range(10):
        try:
            subprocess.run("wmctrl -r '@codebufffreebuff-desktop' -b add,maximized_vert,maximized_horz 2>/dev/null || true", shell=True, env=env)
            subprocess.run("xdotool search --onlyvisible --class '@codebufffreebuff-desktop' windowactivate 2>/dev/null || true", shell=True, env=env)
        except Exception: pass
        time.sleep(2)

t = threading.Thread(target=auto_raise_window, daemon=True)
t.start()

print(f"Freebuff Desktop GUI running on VNC port {vnc_port} (Display {display_str}) & Web port {web_port}!")
