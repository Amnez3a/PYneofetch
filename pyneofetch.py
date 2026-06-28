from pyneofetch_args import parse_args  # args
import time
import os
import subprocess
import platform
import psutil
import shutil
import sys
import getpass
from colorama import init, Fore, Back, Style

init()

WINDOWS_ASCII_ART = """\
       _.-;;-._
'-..-'|   ||   |
'-..-'|_.-;;-._|
'-..-'|   ||   |
'-..-'|_.-''-._|"""

LINUX_ASCII_ART = """\
    .---.
   /     \\
   \\.@-@./
   /`\\_/`\\
  //  _  \\\\
 | \\     )|_
/`\\_`>  <_/ \\
\\__/'---'\\__/"""


MACOS_ASCII_ART = """\
          .:'
      __ :'__
   .'`__`-'__``.
  :__________.-'
  :_________: 
  :_________:
   :_________`-;
    `.__.-.__.'"""


def get_cpu_model():
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if "model name" in line:
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "Unknown"


def get_cpu_temp():
    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            return "N/A"
        for key in ["coretemp", "k10temp", "zenith", "cpu_thermal", "acpitz"]:
            if key in temps:
                return f"{temps[key][0].current:.1f}°C"
        return f"{list(temps.values())[0][0].current:.1f}°C"
    except Exception:
        return "N/A"


def get_package_count():
    managers = {
        "pacman": ["pacman", "-Qq"],
        "apt": ["apt", "list", "--installed"],
        "dnf": ["rpm", "-qa"],
        "zypper": ["rpm", "-qa"],
        "xbps-query": ["xbps-query", "-l"],
        "apk": ["apk", "info"],
    }
    for mgr, cmd in managers.items():
        if shutil.which(mgr):
            result = subprocess.run(cmd, capture_output=True, text=True)
            lines = [line for line in result.stdout.strip().split("\n") if line]
            count = len(lines) - 1 if mgr == "apt" else len(lines)
            return f"{count} ({mgr})"
    return "Unknown"


def pc_info():
    host = os.uname().nodename.strip()

    if platform.system() == "Linux":
        try:
            os_name = platform.freedesktop_os_release().get("NAME", "Linux").strip()
        except (AttributeError, OSError):
            os_name = "Linux"
    else:
        os_name = platform.system().strip()

    cpu_model = get_cpu_model()
    cpu_temp = get_cpu_temp()
    cpu_usage = psutil.cpu_percent(interval=0.5)

    gpu_raw = (
        subprocess.run("lspci | grep VGA", shell=True, text=True, capture_output=True)
        .stdout.strip()
        .split("\n")[0]
    )
    gpu_info = gpu_raw.split(": ", 1)[1] if ": " in gpu_raw else gpu_raw

    vm = psutil.virtual_memory()
    ram_used = vm.used // (1024**3)
    ram_total = vm.total // (1024**3)

    disk = psutil.disk_usage("/")
    disk_string = f"{disk.used / (1024**3):.1f} GB / {disk.total / (1024**3):.1f} GB ({disk.percent}%)"

    kernel = subprocess.run(
        "uname -r", shell=True, text=True, capture_output=True
    ).stdout.strip()
    uptime = (time.time() - psutil.boot_time()) / 3600
    packages = get_package_count()

    return [
        f"Host:     {host}",
        f"OS:       {os_name}",
        f"Kernel:   {kernel}",
        f"CPU:      {cpu_model}",
        f"Temp:     {cpu_temp} | Usage: {cpu_usage}%",
        f"GPU:      {gpu_info}",
        f"RAM:      {ram_used} GB / {ram_total} GB",
        f"Disk:     {disk_string}",
        f"Packages: {packages}",
        f"Uptime:   {uptime:.2f}h",
    ]


def user_info():
    return [
        f"User:     {getpass.getuser().strip()} | UID: {os.getuid()}",
        f"Home:     {os.path.expanduser('~').strip()}",
    ]


def desktop_info():
    wm_de = os.environ.get("XDG_CURRENT_DESKTOP", "Unknown")
    shell = os.environ.get("SHELL", "Unknown")
    term = os.environ.get("TERM", "Unknown")
    env_path = os.environ.get("VIRTUAL_ENV")
    env_name = os.path.basename(env_path) if env_path else "not active"

    return [
        f"Shell:    {shell}",
        f"WM/DE:    {wm_de}",
        f"Term:     {term}",
        f"Env:      {env_name}",
    ]


def other_info():
    return [
        f"{Back.YELLOW}{Fore.BLACK}Python:   {sys.version.split()[0]}{Style.RESET_ALL}",
    ]


def build_info_lines():
    sections = [
        (f"{Back.WHITE}{Fore.BLACK}PC INFO{Style.RESET_ALL}", pc_info()),
        (f"{Back.WHITE}{Fore.BLACK}USER INFO{Style.RESET_ALL}", user_info()),
        (f"{Back.WHITE}{Fore.BLACK}DESKTOP INFO{Style.RESET_ALL}", desktop_info()),
        (f"{Back.WHITE}{Fore.BLACK}OTHER{Style.RESET_ALL}", other_info()),
    ]
    lines = []
    for title, content in sections:
        lines.append(f"[ {title} ]")
        lines.extend(content)
        lines.append("")
    return lines


def render(art_str, info_lines):
    if not art_str:
        for line in info_lines:
            print(line)
        return

    art_lines = art_str.split("\n")
    art_width = max(len(line) for line in art_lines) + 4

    total = max(len(art_lines), len(info_lines))
    for i in range(total):
        left = art_lines[i] if i < len(art_lines) else ""
        right = info_lines[i] if i < len(info_lines) else ""
        print(f"{left:<{art_width}}{right}")


def run_args(args):
    info_lines = build_info_lines()
    if args.logo:
        logos = {
            "windows": WINDOWS_ASCII_ART,
            "linux": LINUX_ASCII_ART,
            "macos": MACOS_ASCII_ART,
        }
        return logos.get(args.logo, ""), info_lines

    if args.only:
        valid_sections = {
            "pc": pc_info,
            "user": user_info,
            "desktop": desktop_info,
            "other": other_info,
        }
        selected = [s.strip() for s in args.only.split(",")]
        info_lines = []
        for sec in selected:
            if sec in valid_sections:
                info_lines.append(
                    f"{Back.WHITE}{Fore.BLACK}[ {sec.upper()} INFO ]{Style.RESET_ALL}"
                )
                info_lines.extend(valid_sections[sec]())
                info_lines.append("")
            else:
                print(f"Warning: Invalid section '{sec}' ignored.")

    # art
    if args.no_art:
        art = ""
    elif args.custom_art:
        art = (
            args.custom_art.read_text()
            if args.custom_art.is_file()
            else print(f"Error: Custom art file '{args.custom_art}' not found.")
        )  # я не ебу зачем в одну строчку запилил
    else:
        if platform.system() == "Linux":
            art = LINUX_ASCII_ART
        elif platform.system() == "Windows":
            art = WINDOWS_ASCII_ART
        elif platform.system() == "Darwin":  # macos
            art = MACOS_ASCII_ART
        else:
            art = ""
    return art, info_lines


def main():
    art, info_lines = run_args(parse_args())
    print("==" * 50)

    render(art, info_lines)
    print("==" * 50)


if __name__ == "__main__":
    main()
