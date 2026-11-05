"""Isolated visual test: nix develop --command python verify.py.

All writable test state is in .work/. No live display, D-Bus session,
configuration, or settings are used. Cleanup targets only this run's UUID.
"""
import os
from pathlib import Path
import signal
import subprocess
import time
import uuid

root = Path(__file__).resolve().parent
work = root / ".work"
work.mkdir(exist_ok=True)
env = dict(os.environ)
for key in ("DISPLAY", "WAYLAND_DISPLAY", "DBUS_SESSION_BUS_ADDRESS", "DBUS_STARTER_ADDRESS", "DBUS_STARTER_BUS_TYPE", "SESSION_MANAGER", "HYPRLAND_INSTANCE_SIGNATURE", "SWAYSOCK"):
    env.pop(key, None)
for key, directory in {
    "HOME": "home", "XDG_CONFIG_HOME": "config", "XDG_CACHE_HOME": "cache",
    "XDG_DATA_HOME": "data", "XDG_STATE_HOME": "state", "XDG_RUNTIME_DIR": "runtime", "TMPDIR": "tmp",
}.items():
    path = work / directory
    path.mkdir(exist_ok=True, mode=0o700)
    env[key] = str(path)
token = f"IRIXIUM_TEST_TOKEN={uuid.uuid4()}"
env.update({
    "IRIXIUM_TEST_TOKEN": token.split("=", 1)[1],
    "IRIXIUM_WORK": str(work),
    "GDK_BACKEND": "x11", "GTK_THEME": "Irixium", "GSETTINGS_BACKEND": "memory",
    "GTK_MODULES": "", "NO_AT_BRIDGE": "1", "GIO_USE_VFS": "local",
    "GTK_USE_PORTAL": "0", "XDG_CURRENT_DESKTOP": "XFCE",
    "GDK_SCALE": "1", "GDK_DPI_SCALE": "1",
    "DBUS_SYSTEM_BUS_ADDRESS": f"unix:path={work}/runtime/no-system-bus",
    "XDG_DATA_DIRS": f"{root}/result/share:{env.get('IRIXIUM_TEST_DATA_DIRS', '')}:{env.get('XDG_DATA_DIRS', '/usr/local/share:/usr/share')}",
})
script = r'''
set -euo pipefail
widget=""
filemanager=""
cleanup() {
  if [ -n "$filemanager" ]; then
    thunar --quit || true
    kill "$filemanager" 2>/dev/null || true
    wait "$filemanager" 2>/dev/null || true
  fi
  if [ -n "$widget" ]; then
    kill "$widget" 2>/dev/null || true
    wait "$widget" 2>/dev/null || true
  fi
}
trap cleanup EXIT
gtk3-widget-factory > "$IRIXIUM_WORK/widget-factory.log" 2>&1 &
widget=$!
sleep 4
kill -0 "$widget"
xwininfo -root -tree > "$IRIXIUM_WORK/widget-windows.txt"
magick import -window root "$IRIXIUM_WORK/irixium-widget-factory.png"
kill "$widget"
wait "$widget" 2>/dev/null || true
widget=""
thunar /tmp > "$IRIXIUM_WORK/thunar.log" 2>&1 &
filemanager=$!
sleep 4
kill -0 "$filemanager"
xwininfo -root -tree > "$IRIXIUM_WORK/thunar-windows.txt"
magick import -window root "$IRIXIUM_WORK/irixium-thunar.png"
'''

def marked_processes():
    found = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit() or int(entry.name) == os.getpid():
            continue
        try:
            if token.encode() in (entry / "environ").read_bytes().split(b"\0"):
                found.append(int(entry.name))
        except (OSError, PermissionError):
            pass
    return found

try:
    with (work / "session.log").open("w") as log:
        subprocess.run(["xvfb-run", "-a", "-s", "-screen 0 1600x900x24 -nolisten tcp", "dbus-run-session", "--", "bash", "-c", script], env=env, cwd=root, stdout=log, stderr=subprocess.STDOUT, timeout=45, check=True)
finally:
    # Also catch D-Bus-activated helpers that detached from the process tree.
    for sig in (signal.SIGTERM, signal.SIGKILL):
        for pid in marked_processes():
            try:
                os.kill(pid, sig)
            except ProcessLookupError:
                pass
        time.sleep(0.5)
    assert not marked_processes(), "private test processes remain"
for name in ("irixium-widget-factory.png", "irixium-thunar.png"):
    assert (work / name).stat().st_size > 1000
    print(work / name)
for name in ("widget-factory.log", "thunar.log"):
    lines = (work / name).read_text().splitlines()
    warnings = [line for line in lines if "Theme parsing error" in line or "Gtk-WARNING" in line]
    print(f"{name}: {len(warnings)} GTK/CSS warnings (see log)")
print("All private test processes cleaned up.")
