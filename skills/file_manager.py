# skills/file_manager.py — File & Document Management
import os, shutil, subprocess, glob
from pathlib import Path
from datetime import datetime

DESKTOP   = os.path.expanduser("~/Desktop")
DOCUMENTS = os.path.expanduser("~/Documents")
DOWNLOADS = os.path.expanduser("~/Downloads")

# ── File Operations ───────────────────────────────────────────────
def list_files(folder="desktop", extension=None):
    folders = {
        "desktop":   DESKTOP,
        "documents": DOCUMENTS,
        "downloads": DOWNLOADS,
    }
    path = folders.get(folder.lower(), folder)
    if not os.path.exists(path):
        return f"Folder not found: {path}"
    files = os.listdir(path)
    if extension:
        files = [f for f in files if f.endswith(extension)]
    if not files:
        return f"No files found in {folder}."
    return f"{folder} has {len(files)} files: " + ", ".join(files[:8])

def open_file(filename, folder="desktop"):
    folders = {
        "desktop":   DESKTOP,
        "documents": DOCUMENTS,
        "downloads": DOWNLOADS,
    }
    base = folders.get(folder.lower(), folder)
    # Search for file
    matches = glob.glob(os.path.join(base, f"*{filename}*"), recursive=False)
    if matches:
        os.startfile(matches[0])
        return f"Opening {os.path.basename(matches[0])}."
    # Search recursively
    matches = glob.glob(os.path.join(base, "**", f"*{filename}*"), recursive=True)
    if matches:
        os.startfile(matches[0])
        return f"Opening {os.path.basename(matches[0])}."
    return f"Could not find {filename}."

def delete_file(filename, folder="desktop"):
    folders = {"desktop": DESKTOP, "documents": DOCUMENTS, "downloads": DOWNLOADS}
    base    = folders.get(folder.lower(), folder)
    matches = glob.glob(os.path.join(base, f"*{filename}*"))
    if matches:
        os.remove(matches[0])
        return f"Deleted {os.path.basename(matches[0])}."
    return f"File not found: {filename}"

def move_file(filename, from_folder="downloads", to_folder="desktop"):
    folders = {"desktop": DESKTOP, "documents": DOCUMENTS, "downloads": DOWNLOADS}
    src_base = folders.get(from_folder.lower(), from_folder)
    dst_base = folders.get(to_folder.lower(), to_folder)
    matches  = glob.glob(os.path.join(src_base, f"*{filename}*"))
    if matches:
        dst = os.path.join(dst_base, os.path.basename(matches[0]))
        shutil.move(matches[0], dst)
        return f"Moved {os.path.basename(matches[0])} to {to_folder}."
    return f"File not found: {filename}"

def copy_file(filename, from_folder="desktop", to_folder="documents"):
    folders  = {"desktop": DESKTOP, "documents": DOCUMENTS, "downloads": DOWNLOADS}
    src_base = folders.get(from_folder.lower(), from_folder)
    dst_base = folders.get(to_folder.lower(), to_folder)
    matches  = glob.glob(os.path.join(src_base, f"*{filename}*"))
    if matches:
        dst = os.path.join(dst_base, os.path.basename(matches[0]))
        shutil.copy2(matches[0], dst)
        return f"Copied {os.path.basename(matches[0])} to {to_folder}."
    return f"File not found: {filename}"

def rename_file(old_name, new_name, folder="desktop"):
    folders = {"desktop": DESKTOP, "documents": DOCUMENTS, "downloads": DOWNLOADS}
    base    = folders.get(folder.lower(), folder)
    matches = glob.glob(os.path.join(base, f"*{old_name}*"))
    if matches:
        ext     = os.path.splitext(matches[0])[1]
        new_path= os.path.join(base, new_name + ext)
        os.rename(matches[0], new_path)
        return f"Renamed to {new_name}{ext}."
    return f"File not found: {old_name}"

def create_folder(folder_name, location="desktop"):
    folders  = {"desktop": DESKTOP, "documents": DOCUMENTS}
    base     = folders.get(location.lower(), location)
    new_path = os.path.join(base, folder_name)
    os.makedirs(new_path, exist_ok=True)
    return f"Folder '{folder_name}' created on {location}."

def search_files(query, location="desktop"):
    folders = {
        "desktop":   DESKTOP,
        "documents": DOCUMENTS,
        "downloads": DOWNLOADS,
        "all":       os.path.expanduser("~"),
    }
    base    = folders.get(location.lower(), DESKTOP)
    matches = glob.glob(os.path.join(base, "**", f"*{query}*"), recursive=True)
    if matches:
        names = [os.path.basename(m) for m in matches[:5]]
        return f"Found {len(matches)} files matching '{query}': " + ", ".join(names)
    return f"No files found matching '{query}'."

def get_file_info(filename, folder="desktop"):
    folders = {"desktop": DESKTOP, "documents": DOCUMENTS, "downloads": DOWNLOADS}
    base    = folders.get(folder.lower(), folder)
    matches = glob.glob(os.path.join(base, f"*{filename}*"))
    if matches:
        f    = matches[0]
        size = os.path.getsize(f)
        mod  = datetime.fromtimestamp(os.path.getmtime(f))
        size_str = f"{size//1024} KB" if size > 1024 else f"{size} bytes"
        return (f"{os.path.basename(f)}: {size_str}, "
                f"modified {mod.strftime('%d %b %Y %I:%M %p')}.")
    return f"File not found: {filename}"

# ── PDF Reading ───────────────────────────────────────────────────
def read_pdf(filename, folder="desktop"):
    try:
        import PyPDF2
        folders = {"desktop": DESKTOP, "documents": DOCUMENTS, "downloads": DOWNLOADS}
        base    = folders.get(folder.lower(), folder)
        matches = glob.glob(os.path.join(base, f"*{filename}*"))
        if not matches:
            return f"PDF not found: {filename}"
        with open(matches[0], 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text   = ""
            for page in reader.pages[:3]:  # first 3 pages
                text += page.extract_text() or ""
        return f"PDF content: {text[:600].strip()}"
    except ImportError:
        return "Install PyPDF2: pip install PyPDF2"
    except Exception as e:
        return f"Could not read PDF: {e}"

def read_text_file(filename, folder="desktop"):
    try:
        folders = {"desktop": DESKTOP, "documents": DOCUMENTS, "downloads": DOWNLOADS}
        base    = folders.get(folder.lower(), folder)
        matches = glob.glob(os.path.join(base, f"*{filename}*"))
        if not matches:
            return f"File not found: {filename}"
        with open(matches[0], 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(800)
        return f"File content: {content.strip()}"
    except Exception as e:
        return f"Could not read file: {e}"

def open_folder(folder="desktop"):
    folders = {
        "desktop":   DESKTOP,
        "documents": DOCUMENTS,
        "downloads": DOWNLOADS,
    }
    path = folders.get(folder.lower(), folder)
    os.startfile(path)
    return f"Opened {folder} folder."

def get_recent_files(folder="downloads", count=5):
    folders = {"desktop": DESKTOP, "documents": DOCUMENTS, "downloads": DOWNLOADS}
    base    = folders.get(folder.lower(), folder)
    try:
        files = [(f, os.path.getmtime(os.path.join(base,f)))
                 for f in os.listdir(base)
                 if os.path.isfile(os.path.join(base,f))]
        files.sort(key=lambda x: x[1], reverse=True)
        names = [f[0] for f in files[:count]]
        return f"Recent files in {folder}: " + ", ".join(names)
    except Exception as e:
        return f"Could not list files: {e}"

def get_disk_usage():
    import psutil
    usage = psutil.disk_usage('C:\\')
    total = round(usage.total/1024**3, 1)
    used  = round(usage.used/1024**3, 1)
    free  = round(usage.free/1024**3, 1)
    return f"Disk: {used}GB used of {total}GB total, {free}GB free."