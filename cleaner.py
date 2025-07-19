import platform
import subprocess
from pathlib import Path

def get_current_folder():
    system = platform.system()

    if system == "Darwin":
        try:
            script = '''
                try
                    tell application "Finder"
                        if (count of windows) is 0 then
                            error "No Finder window is open"
                        end if
                        set thePath to (POSIX path of (target of front Finder window as alias))
                    end tell
                    return thePath
                on error errMsg
                    return "ERROR:" & errMsg
                end try
            '''
            output = subprocess.check_output(["osascript", "-e", script], text=True).strip()
            if output.startswith("ERROR:"):
                print(f"AppleScript error: {output[6:].strip()}")
                return None
            return Path(output)
        except subprocess.CalledProcessError as e:
            print(f"Failed to run AppleScript: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    elif system == "Windows":
        try:
            ps_script = r'''
                $paths = (New-Object -ComObject Shell.Application).Windows() |
                    Where-Object { $_.Document.Folder.Self.Path -ne $null } |
                    ForEach-Object { $_.Document.Folder.Self.Path }
                if ($paths.Count -gt 0) {
                    Write-Output $paths[0]
                }
            '''
            completed = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_script],
                text=True,
                stdout=subprocess.PIPE
            )
            path = completed.stdout.strip()
            if path:
                return Path(path)
        except Exception:
            return None
    else:
        return None

def clean_ds_store():
    folder = get_current_folder()
    if not folder:
        print("Could not determine current folder.")
        return

    ds_path = folder / ".DS_Store"
    if ds_path.exists():
        try:
            ds_path.unlink()
            print(f"Deleted .DS_Store in {folder}")
        except Exception as e:
            print(f"Error deleting .DS_Store: {e}")
    else:
        print(f"No .DS_Store found in {folder}")

def poo():
    folder = get_current_folder()
    if not folder:
        print("Could not determine current folder.")
        return

    base_name = ".DS_Store"
    candidate = folder / base_name
    index = 0

    while candidate.exists():
        candidate = folder / f"{base_name}{index}"
        index += 1

    try:
        candidate.touch()
        print(f"Created empty file: {candidate}")
    except Exception as e:
        print(f"Error creating file: {e}")