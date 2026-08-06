#!/usr/bin/env python3
import os, subprocess, time, shutil

dir_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(dir_path)

# Detach completely from parent subshell/task
pid = os.fork()
if pid > 0:
    print(f"Started daemon process PID: {pid}")
    exit(0)

os.setsid()

# Clean up old processes
subprocess.run("pkill -f 'Xvnc :21' || true", shell=True)
subprocess.run("pkill -f 'Xvfb :21' || true", shell=True)
subprocess.run("pkill -f 'x11vnc' || true", shell=True)
subprocess.run("pkill -f 'websockify.*6080' || true", shell=True)
subprocess.run("pkill -f '@codebufffreebuff-desktop' || true", shell=True)
subprocess.run("rm -f /tmp/.X21-lock", shell=True)

time.sleep(1)

# Ensure fluxbox configuration auto-maximizes Freebuff Desktop app
fluxbox_dir = os.path.expanduser("~/.fluxbox")
os.makedirs(fluxbox_dir, exist_ok=True)
apps_file = os.path.join(fluxbox_dir, "apps")
with open(apps_file, "w") as f:
    f.write("""[app] (@codebufffreebuff-desktop)
  [Maximized] {yes}
[end]
""")

# 1. Start Native TigerVNC Server (Xvnc) on Port 5921 for 10x Faster Zero-Lag Rendering
xvnc_bin = shutil.which("Xvnc") or "/usr/bin/Xvnc"

xvnc_cmd = [
    xvnc_bin,
    ":21",
    "-geometry", "1440x900",
    "-depth", "16",
    "-rfbport", "5921",
    "-SecurityTypes", "None"
]
with open(os.path.join(dir_path, "xvnc.log"), "w") as out:
    xvnc = subprocess.Popen(xvnc_cmd, stdout=out, stderr=out)

time.sleep(2)

# 2. Start window manager (fluxbox or openbox if available)
wm_path = shutil.which("fluxbox") or shutil.which("openbox")
if wm_path:
    wm = subprocess.Popen([wm_path], env={**os.environ, "DISPLAY": ":21"}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

# 3. Start websockify / noVNC on port 6080
web_bin = shutil.which("websockify") or "/usr/bin/websockify"
if web_bin:
    novnc = subprocess.Popen([web_bin, "--web=/usr/share/novnc/", "6080", "localhost:5921"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

# 4. Start Freebuff Desktop App with 2D native X11 rendering
bin_dir = os.path.join(dir_path, "bin")
custom_path = f"{bin_dir}:{os.environ.get('PATH', '')}"

with open(os.path.join(dir_path, "freebuff-app.log"), "w") as out:
    env = {
        **os.environ,
        "PATH": custom_path,
        "DISPLAY": ":21",
        "APPDIR": os.path.join(dir_path, "squashfs-root")
    }
    cmd = [
        os.path.join(dir_path, "squashfs-root/@codebufffreebuff-desktop"),
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-gpu",
        "--disable-gpu-compositing",
        "--disable-accelerated-2d-canvas",
        "--disable-software-rasterizer",
        "--disable-dev-shm-usage"
    ]
    app = subprocess.Popen(cmd, env=env, stdout=out, stderr=out)

print("Freebuff Desktop GUI running with Native TigerVNC Server Xvnc on port 5921 for Zero Lag!")
