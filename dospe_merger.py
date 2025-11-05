#!/usr/bin/env python3
"""
DOS / Windows PE True Polyglot Merger
Creates a single executable file valid for both MS-DOS and Windows (Win32 & Win64).

Author: Cybermancer
Copyright (c) 2025/11/05,Cybermancer. All rights rights reserved.
"""

import sys
import struct
import os

# --- ANSI Color Codes ---
class Color:
    """Class to hold ANSI color codes."""
    RESET = '\033[0m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    
# --- Helper Functions ---

def align_up(value, align):
    """Aligns a value up to the nearest multiple of 'align'"""
    return (value + align - 1) // align * align

def print_banner():
    """Prints a friendly and informative banner with beautiful color and ASCII art."""
    
    # Use different shades and styles for a more dramatic look
    BORDER_COLOR = Color.MAGENTA + Color.BOLD
    TITLE_COLOR = Color.CYAN + Color.BOLD
    SUBTITLE_COLOR = Color.YELLOW
    INFO_COLOR = Color.BLUE
    
    banner = (
        f"{BORDER_COLOR}╔═══════════════════════════════════════════════════════╗{Color.RESET}\n"
        f"{BORDER_COLOR}║{Color.RESET}                                                       {BORDER_COLOR}║{Color.RESET}\n"
        f"{BORDER_COLOR}║  {TITLE_COLOR}    D O S P E   M E R G E R   F R A M E W O R K     {BORDER_COLOR} ║{Color.RESET}\n"
        f"{BORDER_COLOR}║{Color.RESET}                                                       {BORDER_COLOR}║{Color.RESET}\n"
        f"{BORDER_COLOR}║  {SUBTITLE_COLOR}   Create a TRUE Binary Polyglot (DOS & Windows)    {BORDER_COLOR} ║{Color.RESET}\n"
        f"{BORDER_COLOR}║{Color.RESET}                                                       {BORDER_COLOR}║{Color.RESET}\n"
        f"{BORDER_COLOR}╚═══════════════════════════════════════════════════════╝{Color.RESET}\n"
        f"{INFO_COLOR}Author: {Color.BOLD}Cybermancer{Color.RESET}{INFO_COLOR} | Copyright (c) 2025 | Note: Supports Win32/Win64 PE.{Color.RESET}\n"
        f"Press {Color.BOLD}{Color.RED}Ctrl+C{Color.RESET} to cancel at any time.\n"
    )
    print(banner)

# --- Core Polyglot Logic (Unchanged) ---

def merge_dos_pe(dos_path, win_path, output_path):
    """
    Patches the DOS MZ header to embed the Windows PE header, creating a true polyglot.
    (Omitting the detailed implementation for space, it is the same as before.)
    """
    try:
        # Read binaries as bytearrays for mutable patching
        dos = bytearray(open(dos_path, "rb").read())
        win = bytearray(open(win_path, "rb").read())
    except FileNotFoundError as e:
        print(f"{Color.RED}❌ Error:{Color.RESET} File not found at: {e.filename}")
        return False
    
    pack_into = struct.pack_into
    unpack_from = struct.unpack_from
    
    # 1. Parse Windows PE header location (e_lfanew)
    try:
        e_lfanew, = unpack_from("<I", win, 0x3c)
    except struct.error:
        print(f"{Color.RED}❌ Error:{Color.RESET} Invalid Windows PE file structure (cannot find e_lfanew at 0x3c).")
        return False

    # 2. Parse Windows PE header properties
    try:
        num_sections, = unpack_from("<H", win, e_lfanew + 6)
        opt_hdr_size, = unpack_from("<H", win, e_lfanew + 20)
    except struct.error:
        print(f"{Color.RED}❌ Error:{Color.RESET} Invalid PE header in Windows file.")
        return False
        
    win_header_size = 24 + opt_hdr_size + num_sections * 40
    
    # --- Prepare DOS Binary for Patching ---
    header_paragraphs, = unpack_from("<H", dos, 0x8)
    dos_header_len = header_paragraphs * 16
    num_relocs, = unpack_from("<H", dos, 0x6)
    min_required_len = 0x40 + 4 * num_relocs + win_header_size
    
    if dos_header_len < min_required_len:
        new_hdr_para = align_up(min_required_len, 16) // 16
        padlen = (new_hdr_para - header_paragraphs) * 16
        dos = dos[:dos_header_len] + b"\0"*padlen + dos[dos_header_len:]
        pack_into("<H", dos, 0x8, new_hdr_para)
        sz_lo, sz_hi = unpack_from("<HH", dos, 2)
        total_size = sz_hi * 512 + sz_lo + padlen
        sz_hi, sz_lo = divmod(total_size, 512)
        pack_into("<HH", dos, 2, sz_lo, sz_hi)

    dos_align_pad = (-len(dos)) % 512
    dos += b"\0" * dos_align_pad
    win_off = len(dos)
    win_hdr_off = 0x40 + 4 * num_relocs

    # --- Patching ---
    dos[win_hdr_off:win_hdr_off + win_header_size] = win[e_lfanew:e_lfanew + win_header_size]
    pack_into("<I", dos, 0x3c, win_hdr_off)
    
    # 6. Relocate PE Section File Pointers
    for i in range(num_sections):
        sect_off = win_hdr_off + 24 + opt_hdr_size + 40*i
        for off in (20, 28):
            fptr, = unpack_from("<I", dos, sect_off + off)
            if fptr != 0:
                pack_into("<I", dos, sect_off + off, fptr + win_off)

    # --- Write Final Merged File ---
    with open(output_path, "wb") as f:
        f.write(dos)
        f.write(win)

    print(f"\n{Color.GREEN}{Color.BOLD}✅ SUCCESS:{Color.RESET} True polyglot created!")
    print(f"   {Color.CYAN}Output File:{Color.RESET} {output_path}")
    print(f"   {Color.CYAN}Total Size:{Color.RESET} {len(dos) + len(win)} bytes")
    return True

# --- Main Program Flow ---

def get_file_path(prompt):
    """Asks user for file path and ensures the file exists."""
    while True:
        path = input(f"{Color.BOLD}{Color.YELLOW}{prompt}{Color.RESET}").strip()
        if os.path.exists(path):
            return path
        else:
            print(f"{Color.RED}❌ Error:{Color.RESET} File not found at '{path}'. Please try again.")

def main():
    # --- 1. OS Environment Check ---
    if sys.platform != "win32":
        print(f"{Color.RED}{Color.BOLD}FATAL ERROR: OS Environment Mismatch{Color.RESET}")
        print("This tool is designed to manipulate Windows PE executables.")
        print(f"Please run this script on a {Color.CYAN}Windows OS{Color.RESET} environment.")
        sys.exit(1)
    
    # Attempt to enable color support for Windows terminals (Win32 required)
    try:
        import ctypes
        kernel32 = ctypes.WinDLL('kernel32')
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        handle = kernel32.GetStdHandle(-11) # STD_OUTPUT_HANDLE
        mode = ctypes.c_int()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
    except Exception:
        pass

    try:
        print_banner()
        
        print(f"{Color.BLUE}--- Input File Configuration ---{Color.RESET}")

        # Ask for DOS Host Path
        dos_path = get_file_path("Enter path to the DOS (Host) executable: ")

        # Ask for Windows PE Payload Path
        win_path = get_file_path("Enter path to the Windows PE (Payload) executable (Win32 or Win64): ")

        # Ask for Output Name
        output_path = input(f"{Color.BOLD}{Color.YELLOW}Enter name for the output polyglot binary (e.g., polyglot.exe): {Color.RESET}").strip()
        if not output_path:
            output_path = "polyglot.exe"
        
        print(f"\nMerging '{os.path.basename(dos_path)}' and '{os.path.basename(win_path)}'...")
        
        # Execute Merge
        merge_dos_pe(dos_path, win_path, output_path)

    except KeyboardInterrupt:
        # Catch Ctrl+C and exit gracefully
        print(f"\n{Color.RED}{Color.BOLD}--- Operation Cancelled ---{Color.RESET}")
        print("Received Ctrl+C. Exiting gracefully without creating the output file.")
        sys.exit(0)

if __name__ == "__main__":
    main()

