#!/usr/bin/env python3
import os, subprocess, time, shutil, sys, argparse

dir_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(dir_path)

# Parse port options
parser = argparse.ArgumentParser(description="Freebuff Desktop VNC Runner")
parser.add_argument("--vnc", type=int, default=5921, help="VNC Port (default: 5921)")
parser.add_argument("--web", type=int, default=6080, help="Web Port (default: 6080)")
args = parser.parse_args()

vnc_port = args.vnc
web_port = args.web

# Detach completely from parent subshell/task
pid = os.fork()
if pid > 0:
    print(f"Started daemon process PID: {pid}")
    sys.exit(0)

os.setsid()

# Clean up old processes
subprocess.run(f"pkill -f 'Xvnc :21' || true", shell=True)
subprocess.run(f"pkill -f 'Xvfb :21' || true", shell=True)
subprocess.run(f"pkill -f 'x11vnc.*{vnc_port}' || true", shell=True)
subprocess.run(f"pkill -f 'websockify.*{web_port}' || true", shell=True)
subprocess.run(f"pkill -f '@codebufffreebuff-desktop' || true", shell=True)
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

# 1. Locate or install Xvnc (TigerVNC Server)
xvnc_bin = shutil.which("Xvnc")
if not xvnc_bin and os.path.exists("/usr/bin/Xvnc"):
    xvnc_bin = "/usr/bin/Xvnc"

if not xvnc_bin:
    # Auto-attempt apt installation of tigervnc-standalone-server if missing
    subprocess.run("sudo apt-get update -qq && sudo apt-get install -y -qq tigervnc-standalone-server >/dev/null 2>&1 || true", shell=True)
    xvnc_bin = shutil.which("Xvnc") or ("/usr/bin/Xvnc" if os.path.exists("/usr/bin/Xvnc") else None)

if xvnc_bin and os.path.exists(xvnc_bin):
    xvnc_cmd = [
        xvnc_bin,
        ":21",
        "-geometry", "1440x900",
        "-depth", "16",
        "-rfbport", str(vnc_port),
        "-SecurityTypes", "None"
    ]
    with open(os.path.join(dir_path, "xvnc.log"), "w") as out:
        xvnc = subprocess.Popen(xvnc_cmd, stdout=out, stderr=out)
    time.sleep(2)
else:
    # Fallback seamlessly to Xvfb + x11vnc if Xvnc is unavailable
    xvfb_bin = shutil.which("Xvfb") or "/usr/bin/Xvfb"
    subprocess.Popen([xvfb_bin, ":21", "-screen", "0", "1440x900x16"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    
    vnc_bin = shutil.which("x11vnc") or "/usr/bin/x11vnc"
    vnc_cmd = [
        vnc_bin,
        "-display", ":21",
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

# 2. Start window manager (fluxbox or openbox if available)
wm_path = shutil.which("fluxbox") or shutil.which("openbox")
if wm_path:
    wm = subprocess.Popen([wm_path], env={**os.environ, "DISPLAY": ":21"}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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

print(f"Freebuff Desktop GUI running on VNC port {vnc_port} & Web port {web_port}!")
