# Copyright 2026 MV2, Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in MV2's name.
"""Fetch the registered, unchanged clan_marking.py from GitHub main and check that it is the exact
file the registered run used (md5 of the CRLF-normalised text, as printed by gate.py in
clan-marking-v1)."""
import hashlib
import sys
import time
import urllib.request

URL = "https://raw.githubusercontent.com/munimtechnologies/whale-clan-marking-test/main/clan_marking.py"
MD5 = "8347dbd91d8d1af7117b89f638384e69"


def main():
    last = "no attempt"
    for _ in range(5):
        try:
            with urllib.request.urlopen(URL + "?t=%d" % int(time.time()), timeout=60) as r:
                blob = r.read()
            got = hashlib.md5(blob.replace(b"\r\n", b"\n")).hexdigest()
            if got != MD5:
                print("clan_marking.py md5 %s differs from the registered %s" % (got, MD5), flush=True)
                return 1
            with open("clan_marking.py", "wb") as fh:
                fh.write(blob)
            print("clan_marking.py fetched, md5 %s = registered" % got, flush=True)
            return 0
        except Exception as exc:  # noqa: BLE001
            last = repr(exc)
            time.sleep(30)
    print("fetch failed: %s" % last, flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())
