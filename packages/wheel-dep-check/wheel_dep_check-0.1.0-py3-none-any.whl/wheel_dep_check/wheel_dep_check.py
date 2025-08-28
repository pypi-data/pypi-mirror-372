#!/usr/bin/env python3
import os
import sys
import subprocess
import tempfile
import zipfile
from pathlib import Path

def check_lib(lib_path, checked_libs, missing_libs):
    lib_path = Path(lib_path)
    if lib_path in checked_libs or not lib_path.is_file():
        return
    checked_libs.add(lib_path)

    print(f"Checking: {lib_path}")
    try:
        output = subprocess.check_output(["ldd", str(lib_path)], text=True)
    except subprocess.CalledProcessError:
        return

    for line in output.splitlines():
        parts = line.split()
        dep = parts[0] if parts else ""
        path = parts[2] if len(parts) >= 3 else ""

        if "not found" in line:
            print(f"  MISSING: {dep}")
            missing_libs.add(dep)
        elif path and Path(path).is_file():
            check_lib(path, checked_libs, missing_libs)

def main():
    if len(sys.argv) < 2:
        print("Usage: wheel_dep_check.py <wheel-file-or-directory>")
        sys.exit(1)

    INPUT = sys.argv[1]

    checked_libs = set()
    missing_libs = set()

    # Extract wheel if input is a .whl
    if INPUT.endswith(".whl"):
        tmpdir = tempfile.TemporaryDirectory()
        print(f"Extracting wheel {INPUT} to {tmpdir.name}")
        with zipfile.ZipFile(INPUT, "r") as zip_ref:
            zip_ref.extractall(tmpdir.name)
        wheel_dir = tmpdir.name
    else:
        wheel_dir = INPUT

    # Walk through all .so files in extracted wheel or directory
    for sofile in Path(wheel_dir).rglob("*.so*"):
        check_lib(sofile, checked_libs, missing_libs)

    print("\n==== Missing Libraries ====")
    for lib in sorted(missing_libs):
        print(lib)

    print("\nTip: For each missing lib, you can run:")
    print("  dnf provides '*/<libname>.so'")

if __name__ == "__main__":
    main()

