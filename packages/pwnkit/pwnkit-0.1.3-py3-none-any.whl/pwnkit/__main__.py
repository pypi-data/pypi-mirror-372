from __future__ import annotations
from pathlib import Path
from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from pwnkit import *
import os

TEMPLATE = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Title : Linux Pwn Exploit
# Author: {author} - {blog}
#
# Description:
# ------------
# A Python exploit for Linux binex interaction
#
# Usage:
# ------
# - Local mode  : ./xpl.py
# - Remote mode : ./xpl.py [ <IP> <PORT> | <IP:PORT> ]
#

from pwnkit import *
from pwn import *
import os, sys

BIN_PATH   = {file_path!r}
LIBC_PATH  = {libc_path!r}
elf        = ELF(BIN_PATH, checksec=False)
libc       = ELF(LIBC_PATH) if LIBC_PATH else None
host, port = parse_argv(sys.argv[1:], {host!r}, {port!r})

ctx = Context(
    arch      = {arch!r},
    os        = {os!r},
    endian    = {endian!r},
    log_level = {log!r},
    terminal  = {term!r}
).push()

io = Tube(
    file_path = BIN_PATH,
    libc_path = LIBC_PATH,
    host      = host,
    port      = port,
    env       = {{}}
).init().alias()
set_global_io(io._t())  # s, sa, sl, sla, r, ru, uu64

init_pr("debug", "%(asctime)s - %(levelname)s - %(message)s", "%H:%M:%S")

def xpl():

    # exploit chain here




    io.interactive()

if __name__ == "__main__":
    xpl()
"""

# Argument Parsing
# ------------------------------------------------------------------------
def init_args() -> Namespace:
    ap = ArgumentParser(
        prog="pwnkit",
        usage="pwnkit [options] <exp.py>",
        description=(
            "Generate a clean exploit scaffold with embedded Context config.\n"
            "Examples:\n"
            "  pwnkit xpl.py --file ./vuln\n"
            "  pwnkit xpl.py --file ./vuln --host 10.10.10.10 --port 31337\n"
            "  pwnkit xpl.py -f ./vuln -i 10.10.10.10 -p 31337 -A aarch64 -E big\n"
            "  (default context preset: Linux amd64 little debug\n)"
        ),
        epilog=(
            "Author: Axura (@4xura) - https://4xura.com\n"
        ),
        formatter_class=RawTextHelpFormatter,
    )

    ap.add_argument(
        "out",
        metavar="exp.py",
        type=Path,
        help="output exploit path (e.g., xpl.py)"
    )

    # - Paths
    paths = ap.add_argument_group("Paths")
    paths.add_argument(
        "-f", "--file", 
        dest="file_path",
        default="",
        metavar="target",
        help="target binary path to pwn (default: ./vuln)"
    )
    paths.add_argument(
        "-l", "--libc", dest="libc_path",
        default="",
        metavar="libc",
        help="optional target libc to preload"
    )

    # - Target (decides local vs remote purely by presence of host+port)
    target = ap.add_argument_group("Target")
    target.add_argument(
        "-i", "--ip", "--host",
        metavar="ip",
        dest="host",
        help="remote host (if provided with --port → remote mode)"
    )
    target.add_argument(
        "-p", "--port",
        metavar="port",
        dest="port",
        type=int,
        help="remote port (requires --host)"
    )

    # - Context
    ctx = ap.add_argument_group("Pwntools context")
    ctx.add_argument(
        "-P", "--preset",
        choices=list(Context.presets()),
        default="linux-amd64-debug",
        help=(
            "context preset; individual flags below override this\n"
            "(default: linux-amd64-debug)"
        ),
    )

    ctx.add_argument(
        "-A", "--arch",
        default=None,
        choices=["amd64", "i386", "arm", "aarch64"],
        help=(
            "target architecture for pwntools context (default: amd64)"
        ),
    )

    ctx.add_argument(
        "-O", "--os",
        dest="os_name",
        metavar="os",
        default=None,
        choices=["linux", "freebsd"],
        help=(
            "target operating system (default: linux)"
        ),
    )

    ctx.add_argument(
        "-E", "--endian",
        metavar="endianness",
        default=None,
        choices=["little", "big"],
        help=(
            "endianness of the target (default: little)"
        ),
    )

    ctx.add_argument(
        "-L", "--log",
        default=None,
        metavar="log_level",
        choices=["debug", "info", "warning", "error"],
        help=(
            "pwntools logging level (default: \"debug\" from preset)"
        ),
    )

    ctx.add_argument(
        "-T", "--term",
        nargs="*",
        default=None,
        metavar="cmd",
        help=(
            "terminal command to use when spawning GDB (default: tmux splitw -h).\n"
        ),
    )

    # - Personel
    ps = ap.add_argument_group("Personel")
    ps.add_argument(
        "-a", "--author",
        metavar="author",
        dest="author",
        default="Axura (@4xura)",
        help=(
            "author name in exploit template"
        ),
    )

    ps.add_argument(
        "-b", "--blog",
        metavar="link",
        dest="blog",
        default="https://4xura.com",
        help=(
            "blog link in exploit template"
        ),
    )

    return ap.parse_args()

def cli():
    args = init_args()

    ctx = Context.preset(args.preset)
    if args.arch is not None:      ctx.arch = args.arch
    if args.os_name is not None:   ctx.os = args.os_name
    if args.endian is not None:    ctx.endian = args.endian
    if args.log is not None:       ctx.log_level = args.log
    if args.term is not None:      ctx.terminal = tuple(args.term)

    io = Tube(
        file_path=args.file_path or None,
        libc_path=args.libc_path or None,
        host=args.host or None,
        port=args.port or None,
    )
    io_line = io.as_code()

    content = TEMPLATE.format(
        arch=ctx.arch,
        os=ctx.os,
        endian=ctx.endian,
        log=ctx.log_level,
        term=tuple(ctx.terminal),
        file_path=io.file_path,
        libc_path=io.libc_path,
        host=io.host,
        port=io.port,
        io_line=io_line,
        author=args.author,
        blog=args.blog,
    )

    out = Path(args.out)
    out.write_text(content)
    out.chmod(0o755)
    print(f"[+] Wrote {out}")

