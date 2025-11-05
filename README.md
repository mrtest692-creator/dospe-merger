# ✨ DOSPE Merger Framework

<p align="center">
  <img src="https://img-url.svc.ai.google.com/api/image?query=shield+python+3&color=blue" alt="Python 3">
  <img src="https://img-url.svc.ai.google.com/api/image?query=shield+license+MIT&color=green" alt="License">
  <img src="https://img-url.svc.ai.google.com/api/image?query=shield+os+windows+required&color=red" alt="Windows Required">
</p>

## 🚀 Overview

The **DOSPE Merger Framework** is a specialized Python utility for creating **True Polyglot Executables** that run natively on both **MS-DOS** and **Microsoft Windows** (Win32 & Win64) operating systems from a single file.

This tool bypasses the need for custom loaders or wrappers by expertly patching the standard DOS MZ header to embed and correctly relocate the Windows PE header and sections.

### What is a True Polyglot?

A true polyglot binary is a single file that is recognized as a valid, runnable executable by **two different operating system loaders** without modification. The DOSPE Merger achieves this by exploiting the backward compatibility layer built into the Windows PE format.

---

## ⚙️ How It Works

The program executes a multi-step patching process on the DOS host file:

1.  **Header Analysis:** It reads the structure of the Windows PE file to determine the size of its essential header components and section data offsets.
2.  **DOS Header Expansion:** It pads the DOS executable's header area (after the relocation table) to create sufficient space for the Windows PE header block.
3.  **The Critical Patch:** It updates the `e_lfanew` pointer (located at offset `0x3C` in the DOS header) to point to the newly embedded location of the PE header within the DOS file.
4.  **Section Relocation:** It adjusts the file offsets for all code and data sections within the embedded PE header, ensuring the Windows loader correctly finds its program payload appended at the end of the combined file.

| Environment | Loader Action | Result |
| :--- | :--- | :--- |
| **MS-DOS** | Sees a valid MZ header and runs the original DOS stub code. | **DOS Program Executes.** |
| **Windows** | Reads the DOS header, follows the patched `e_lfanew` pointer, finds a valid PE header, and runs the embedded PE program. | **Windows Program Executes.** |

---

## 🛠️ Requirements

* **Operating System:** Windows (Windows 7 or later is recommended). *The script includes a check and will exit if run on Linux or macOS.*
* **Python:** Python 3.x
* **Binaries:**
    * One **DOS Executable** (Host, typically a minimal DOS stub or program).
    * One **Windows PE Executable** (Payload, can be Win32 or Win64 `.exe`).

---

## 🚀 Usage

### 1. Installation

Clone the repository and navigate to the directory:

```bash
git clone https://github.com/mrtest692-creator/dospe-merger/edit.git
cd dospe-merger
```
### 2.Execution 
After navigating to repo folder 
```bash
python dospe_merger.py
```
