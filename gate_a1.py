# Copyright 2026 MV2, Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in MV2's name.
"""Job gate for AMENDMENT-1: compute nothing until the amendment plan and code on GitHub main equal
the job's own copies (CRLF normalised). Waits at most 60 minutes. Then installs the RData reader
(rdata 1.0.0), which the amendment needs for the authors' Figure 4 file."""
import hashlib
import subprocess
import sys
import time
import urllib.request

RAW = "https://raw.githubusercontent.com/munimtechnologies/whale-clan-marking-test/main/"
FILES = ["AMENDMENT-1.md", "marking_a1.py", "test_marking_a1.py"]


def md5(blob):
    return hashlib.md5(blob.replace(b"\r\n", b"\n")).hexdigest()


def check():
    ok, lines = True, []
    for name in FILES:
        with open(name, "rb") as fh:
            lm = md5(fh.read())
        try:
            with urllib.request.urlopen(RAW + name + "?t=%d" % int(time.time()), timeout=60) as r:
                rm = md5(r.read())
        except Exception as exc:  # noqa: BLE001
            lines.append("%s local %s remote fetch failed: %s" % (name, lm, exc))
            ok = False
            continue
        lines.append("%s local %s remote %s %s" % (name, lm, rm, "same" if lm == rm else "DIFFERENT"))
        ok = ok and lm == rm
    return ok, lines


def main():
    deadline = time.time() + 60 * 60
    while True:
        ok, lines = check()
        print("\n".join(lines), flush=True)
        if ok:
            print("amendment plan and code are public and identical", flush=True)
            break
        if time.time() > deadline:
            print("gate failed: public copies missing or different after 60 min; nothing computed",
                  flush=True)
            return 1
        time.sleep(300)
    rc = subprocess.run([sys.executable, "-m", "pip", "install", "--no-cache-dir", "rdata==1.0.0"],
                        check=False).returncode
    print("rdata==1.0.0 install exit code %d" % rc, flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
