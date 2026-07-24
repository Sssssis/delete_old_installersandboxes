#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime


# ==========================================
# 設定
# ==========================================

BASE = Path("/System/Volumes/Data/Library/InstallerSandboxes/.PKInstallSandboxManager")

LOGFILE = Path.home() / "Desktop" / "InstallerSandboxes_DeleteLog.txt"

start = time.time()
# ==========================================


def human_size(path):
    try:
        return subprocess.check_output(
            ["du", "-sh", str(path)],
            text=True
        ).split()[0]
    except Exception:
        return "?"


def size_to_bytes(size):

    units = {
        "K":1024,
        "M":1024**2,
        "G":1024**3,
        "T":1024**4
    }

    try:

        if size[-1].isdigit():
            return int(size)

        return float(size[:-1]) * units[size[-1]]

    except:
        return 0


def require_root():

    if os.geteuid() != 0:
        print("Please run with sudo.")
        sys.exit(1)


parser = argparse.ArgumentParser()

parser.add_argument(
    "--delete",
    action="store_true",
    help="Actually delete files."
)

parser.add_argument(
    "--year",
    type=int,
    default=2023,
    help="Delete sandboxes modified in or before this year."
)

args = parser.parse_args()

require_root()


before_size = human_size(BASE)

targets=[]

for sb in sorted(BASE.glob("*.activeSandbox")):

    try:
        year=datetime.fromtimestamp(sb.stat().st_mtime).year
    except Exception:
        continue

    if year<=args.year:

        size=human_size(sb)
        contents = []
        if (sb / "Root" / "Applications").exists():
            apps_dir = sb / "Root" / "Applications"
            contents = [p.name for p in apps_dir.iterdir() if p.is_dir()]

        if (sb/"Root/usr").exists():
            contents.append("[usr]")

        if (sb/"Root/Library").exists():
            contents.append("[Library]")

        if not contents:
            contents.append("(empty)")

        targets.append({
            "path":sb,
            "year":year,
            "size":size,
            "bytes":size_to_bytes(size),
            "appname":", ".join(contents)
        })

targets.sort(key=lambda x:x["bytes"],reverse=True)

print()
print("="*70)
print("InstallerSandboxes cleanup")
print("="*70)
print()

total=0

for t in targets:

    print(
        f'{t["year"]:<6}   '
        f'{t["size"]:>8}   '
        f'{t["path"].name:<45}'
        f'{"   "}'
        f'{t["appname"]}'
    )

    total+=t["bytes"]

print()
print("-"*70)

print(f"Directories : {len(targets)}")
print(f"Approx size : {total/1024**3:.1f} GB")

print()

if not args.delete:

    print("Dry Run only.")
    print()
    print("Nothing has been deleted.")
    print()
    print("To delete:")
    print("スキャンのみモードです。本番モードの場合は以下のようにコマンドを入れてください。")
    print("sudo python3 delete_old_installersandboxes.py --delet --year 2023")
    sys.exit(0)

print()
print("WARNING")
print("This will permanently remove the directories above.")
print()
print(f"{total/1024**3:.1f} GB will be removed.")
print()

print("本当に削除してよければ、DELETEと入力してください。")
confirm=input("Type DELETE to continue: ")

if confirm!="DELETE":

    print()
    print("Cancelled.")
    sys.exit(0)

print()

deleted=0
failed=0

after_size = human_size(BASE)
elapsed = time.time() - start

remaining = []

for t in targets:
    if t["path"].exists():
        remaining.append(t)

with open(LOGFILE,"a") as log:

    log.write("\n" + "=" * 70 + "\n")

    log.write(
        f"Cleanup started {datetime.now()}\n\n"
    )

    log.write(f"Target year : <= {args.year}\n")
    log.write(f"Directories : {len(targets)}\n")
    log.write(f"Deleted     : {deleted}\n")
    log.write(f"Failed      : {failed}\n")
    log.write(f"Remaining   : {len(remaining)}\n")
    log.write(f"Before      : {before_size}\n")
    log.write(f"After       : {after_size}\n")
    log.write(f"Elapsed     : {elapsed:.1f} sec\n")

    if remaining:
        log.write("Remaining directories:\n")
        for r in remaining:
            log.write(f'  {r["size"]:>6}  {r["path"].name}\n')
    else:
        log.write("Verification : OK (all target directories removed)\n")
    log.write("\n")

    for t in targets:

        p=t["path"]

        print("Deleting",p.name)

        log.write(f"DELETE {p}\n")

        r=subprocess.run(
            ["rm","-rf",str(p)],
            capture_output=True,
            text=True
        )

        if r.returncode==0:
            if not p.exists():
                deleted += 1

            else:
                failed += 1
                msg = "Directory still exists!"
                print(msg)
                log.write(msg + "\n")

        else:
            failed+=1
            stderr = r.stderr.strip()
            print("FAILED:due to ",stderr)
            log.write(stderr+"\n")
            if "Operation not permitted" in stderr:
                print()
                print("ERROR:")
                print("Operation not permitted")
                print()
                print("Grant Full Disk Access to Terminal.app")
                print("System Settings -> Privacy & Security -> Full Disk Access")
                print()

print()
print("処理が終了しました。サマリを表示します。")
print("=" * 70)
print("Summary")
print("=" * 70)

print(f"Target year : <= {args.year}")
print(f"Directories : {len(targets)}")
print(f"Deleted     : {deleted}")
print(f"Failed      : {failed}")
print(f"Remaining   : {len(remaining)}")
print(f"Before      : {before_size}")
print(f"After       : {after_size}")
print(f"Elapsed     : {elapsed:.1f} sec")

if remaining:
    print()
    print("Remaining directories:")
    for r in remaining:
        print(f'  {r["size"]:>6}  {r["path"].name}')
else:
    print()
    print("Verification : OK (all target directories removed)")

print()
print("Log:")
print(f"  {LOGFILE}")