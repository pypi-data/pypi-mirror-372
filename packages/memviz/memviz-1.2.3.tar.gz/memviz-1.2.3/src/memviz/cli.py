import argparse
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path

def choose_color(green_limit: float, red_limit: float, num: float) -> str:
    RED, GREEN, YELLOW = 31, 32, 33
    if num > red_limit:
        color = RED
    elif num < green_limit:
        color = GREEN
    else:
        color = YELLOW
    return f"\033[{color}m{round(num, 2)}%\033[0m"

def _read_magic(path: Path) -> bytes:
    with path.open("rb") as f:
        return f.read(8)

def is_elf(path: Path) -> bool:
    magic = _read_magic(path)
    return magic.startswith(b"\x7fELF")

def is_macho_or_universal(path: Path) -> bool:
    magic = _read_magic(path)
    # Mach-O (32/64, endianness variants) and universal/fat (CAFEBABE/CAFED00D)
    MACHO_MAGICS = {
        b"\xfe\xed\xfa\xce", b"\xce\xfa\xed\xfe",  # 32-bit
        b"\xfe\xed\xfa\xcf", b"\xcf\xfa\xed\xfe",  # 64-bit
    }
    if magic[:4] in MACHO_MAGICS:
        return True
    return magic.startswith(b"\xca\xfe\xba\xbe") or magic.startswith(b"\xca\xfe\xd0\x0d")  # fat

def _ensure_executable(path: Path) -> None:
    try:
        st = path.stat()
        path.chmod(st.st_mode | stat.S_IXUSR)
    except Exception:
        pass  # best-effort

def _run_local_valgrind(target_abs: Path, out_txt: Path) -> int:
    print("[memviz] Running valgrind locally...")
    if is_macho_or_universal(target_abs):
        print("[memviz] ERROR: Local Valgrind on macOS cannot execute this Mach-O binary reliably.")
        print("         Either install a macOS Valgrind build that works on your OS, or run via Docker with a Linux ELF binary.")
        return 1
    _ensure_executable(target_abs)
    with out_txt.open("w") as f:
        # cachegrind writes its report to stderr → redirect there
        proc = subprocess.run(
            ["valgrind", "--tool=cachegrind", str(target_abs)],
            stdout=subprocess.DEVNULL,
            stderr=f,
        )
    # Clean cachegrind artifacts if any
    for p in target_abs.parent.glob("cachegrind.out.*"):
        try: p.unlink()
        except Exception: pass
    return proc.returncode

def _run_docker_valgrind(target_abs: Path, mount_root: Path, image: str, out_txt: Path) -> int:
    if shutil.which("docker") is None:
        print("Unable to run valgrind, please either:")
        print("  1. Install valgrind: https://valgrind.org/downloads/current.html")
        print("  2. Or install Docker: https://www.docker.com/")
        return 1

    # Ensure target is inside mount_root
    try:
        target_abs.relative_to(mount_root)
    except ValueError:
        print("[memviz] ERROR: Target must be inside the current directory so Docker can see it.")
        print(f"          Current dir: {mount_root}")
        print(f"          Target path: {target_abs}")
        return 1

    rel_path = target_abs.relative_to(mount_root)
    container_out = out_txt.relative_to(mount_root)

    # Inside the container we write to /workspace/<container_out>
    # Also ensure executable bit inside container (best-effort).
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{mount_root}:/workspace",
        "-w", "/workspace",
        image,
        "bash", "-lc",
        (
            f"test -x '{rel_path}' || chmod +x '{rel_path}' || true; "
            f"valgrind --tool=cachegrind '{rel_path}' > /dev/null 2> '{container_out}'; "
            f"rm -f cachegrind.out.*"
        ),
    ]

    print("[memviz] Running inside Docker...")
    proc = subprocess.run(cmd)
    return proc.returncode

def run_cachegrind(executable_arg: str):
    # Resolve paths
    mount_root = Path.cwd().resolve()           # this is what we mount to /workspace
    target_abs = Path(executable_arg).expanduser().resolve()
    exe_name = target_abs.name
    out_txt = mount_root / f"{exe_name}.txt"    # always write into current dir

    # Basic existence check
    if not target_abs.exists():
        print(f"[memviz] ERROR: Target not found: {target_abs}")
        return None

    # Decide local vs docker
    valgrind = shutil.which("valgrind")
    if valgrind is not None:
        rc = _run_local_valgrind(target_abs, out_txt)
        return out_txt if rc == 0 else None

    # Fallback to Docker
    image = os.environ.get("IMAGE", "memviz-env")
    # Quick format hint: if Mach-O, warn before starting container
    if is_macho_or_universal(target_abs):
        print("[memviz] WARNING: Target appears to be a macOS Mach-O binary.")
        print("         A Linux container will not be able to execute it. Build an ELF binary (compile inside Docker or cross-compile).")
        return None

    rc = _run_docker_valgrind(target_abs, mount_root, image, out_txt)
    return out_txt if rc == 0 else None

def parse_and_report(text_path: Path) -> None:
    patterns = {
        "I refs": r"I\s+refs:\s+([\d,]+)",
        "I1 misses": r"I1\s+misses:\s+([\d,]+)",
        "LLi misses": r"LLi\s+misses:\s+([\d,]+)",

        "D refs": r"D\s+refs:\s+([\d,]+)",
        "D read refs":   r"D\s+refs:\s*[\d,]+\s*\(\s*([\d,]+)\s*rd",
        "D write refs":  r"D\s+refs:\s*[\d,]+\s*\(.*\+\s*([\d,]+)\s*wr",

        "D1 misses": r"D1\s+misses:\s+([\d,]+)",
        "D1 read misses":  r"D1\s+misses:\s*[\d,]+\s*\(\s*([\d,]+)\s*rd",
        "D1 write misses": r"D1\s+misses:\s*[\d,]+\s*\(\s*[\d,]+\s*rd\s*\+\s*([\d,]+)\s*wr",

        "LLd misses": r"LLd\s+misses:\s+([\d,]+)",
        "LLd read misses": r"LLd\s+misses:\s+[\d,]+\s+\(\s*([\d,]+)\s+rd",
        "LLd write misses": r"LLd\s+misses:\s+[\d,]+\s+\(\s*[\d,]+\s+rd\s*\+\s*([\d,]+)\s+wr",

        "LL refs": r"LL\s+refs:\s+([\d,]+)",
        "LL misses": r"LL\s+misses:\s+([\d,]+)",
    }

    try:
        text = text_path.read_text()
    except FileNotFoundError:
        print("ERROR: Unable to run, please either:")
        print("\t1. Install valgrind: https://valgrind.org/downloads/current.html")
        print("\t2. Or install Docker: https://www.docker.com/")
        sys.exit(1)

    results = {}
    for key, pat in patterns.items():
        m = re.search(pat, text)
        if m:
            results[key] = int(m.group(1).replace(",", ""))

    if not results:
        print("ERROR: cannot execute binary file")
        sys.exit(1)

    print("=======================  SUMMARY   =======================")
    print("INSTRUCTIONS MISS RATE: ")
    l1_icache_miss = results["I1 misses"] / results["I refs"] * 100
    last_lvl_i_miss = results["LLi misses"] / results["I refs"] * 100
    print("\t1. L1 I-cache miss rate: " + choose_color(1, 5, l1_icache_miss))
    print("\t2. Last-level instruction miss rate: " + choose_color(1, 5, last_lvl_i_miss))

    print("\nDATA MISS RATE: ")
    d1_miss = results["D1 misses"] /  results["D refs"] * 100
    last_lvl_d_miss =  results["LLd misses"] /  results["D refs"] * 100
    print("\t1. L1 D-cache miss rate: " + choose_color(2, 10, d1_miss))
    print("\t2. Last-level D-cache miss rate: "+ choose_color(2, 10, last_lvl_d_miss))

    ll_miss_rate = results["LL misses"] / results["LL refs"] * 100
    print("\nOVERALL LAST LEVEL MISS RATE: " + choose_color(1, 5, ll_miss_rate))

    print(f'\n{"READ":<10} vs \t {"WRITE":<10}')
    read_miss = (results["LLd read misses"] + results["D1 read misses"]) /  results["D read refs"] * 100
    write_miss =  (results["LLd write misses"] + results["D1 write misses"]) /  results["D write refs"] * 100
    print("-" * 25)
    print(f"{round(read_miss, 2):<10} \t {round(write_miss, 2):<15}")
    print("(in terms of miss rate (percentage))")

    LEARN_MORE_URL = "https://yyc.solvcon.net/en/latest/nsd/05cache/cache.html"
    print("\n📖 Learn more about caches:")
    print(f"  {LEARN_MORE_URL}")

    # Cleanup
    try:
        text_path.unlink()
    except Exception:
        pass

def main():
    logo = r"""
    ======================================================.
    S |             |     |     |   |     |             | |
    | '=. ========. |== | '==== | | | | ==' | .=======. | |
    |   |     |   | |   |       | |   |     | |       | | |
    |=. '=. | | .=' | | |====== | '=========' | ======' | |
    | |   | | | |   | | |   |   |   |     |   |     |   | |
    | '=. '=' | | .=' '=' | '====== '=. .=' .====== | .=' |
    |   | #######################################   | |   |
    | | |=#                               _     #===' | ==|
    | | | # _ __ ___   ___ _ __ _____   _(_)____#     |   |
    | | | #| '_ ` _ \ / _ \ '_ ` _ \ \ / / |_  /#======== |
    | |   #| | | | | |  __/ | | | | \ V /| |/ / # |       |
    | |===#|_| |_| |_|\___|_| |_| |_|\_/ |_/___|# | | ==. |
    | |   #######################################   |   | |
    |=' .== | ==| '=. | | '=======| ==| .== |=. '=====. | |
    |   |   |   |   | | |     |   |   | |   | |       | | |
    | ====. |== |== | | |===. | | '=. |=' .=' '====== | | |
    |     | |   |   | | |   | | |   | |   |     |     | | |
    | ==. '=' ======' | | | | | | ==' | .=' | ==' ====' | |
    |   |             |   | |   |       |   |           | E
    '======================================================
    """

    parser = argparse.ArgumentParser(
                        prog='memviz',
                        description='Embedded Low-Level Memory Visualization for C++')

    subparsers = parser.add_subparsers(dest="command")

    cachegrind = subparsers.add_parser('cachegrind', help = 'visualize the cache layout of a program')
    cachegrind.add_argument('executable', help='the executable to run cachegrind on')

    args = parser.parse_args()

    if len(sys.argv) == 1:
        print(logo)
        parser.print_help()
        sys.exit(0)

    if args.command == "cachegrind":
        run_cachegrind(args.executable)

if __name__ == "__main__":
    main()