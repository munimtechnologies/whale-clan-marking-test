# Copyright 2026 MV2, Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in MV2's name.
"""Job gate: compute nothing until the plan and code on GitHub main equal the job's own copies
(CRLF normalised). Waits at most 45 minutes. Then tries to install the optional RData reader
(rdata 1.0.0); if that fails, clan_marking.py falls back to the CSV route fixed in the plan."""
import hashlib
import subprocess
import sys
import time
import urllib.request

RAW = "https://raw.githubusercontent.com/munimtechnologies/whale-clan-marking-test/main/"
FILES = ["MARKING-PREREG.md", "clan_marking.py", "test_clan_marking.py"]


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
    deadline = time.time() + 45 * 60
    while True:
        ok, lines = check()
        print("\n".join(lines), flush=True)
        if ok:
            print("plan and code are public and identical", flush=True)
            break
        if time.time() > deadline:
            print("gate failed: public copies missing or different after 45 min; nothing computed",
                  flush=True)
            return 1
        time.sleep(300)
    rc = subprocess.run([sys.executable, "-m", "pip", "install", "--no-cache-dir", "rdata==1.0.0"],
                        check=False).returncode
    print("optional rdata==1.0.0 install exit code %d (non-zero -> CSV route)" % rc, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
