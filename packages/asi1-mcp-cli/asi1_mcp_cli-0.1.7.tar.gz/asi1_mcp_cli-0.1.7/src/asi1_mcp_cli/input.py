import io
import platform
import subprocess
import base64
import filetype
import mimetypes

def get_clipboard_content() -> tuple[str | bytes, str | None] | None:
    """Get content from clipboard, handling both text and images in native and WSL environments."""
    system = platform.system()
    is_wsl = 'microsoft-standard' in platform.uname().release.lower()

    if is_wsl or system == 'Windows':
        try:
            ps_script = '''
            Add-Type -AssemblyName System.Windows.Forms
            if ([Windows.Forms.Clipboard]::ContainsImage()) {
                $image = [Windows.Forms.Clipboard]::GetImage()
                $ms = New-Object System.IO.MemoryStream
                $image.Save($ms, [System.Drawing.Imaging.ImageFormat]::Png)
                Write-Output "IMAGE:"
                [Convert]::ToBase64String($ms.ToArray())
            } elseif ([Windows.Forms.Clipboard]::ContainsText()) {
                Write-Output "TEXT:"
                [Windows.Forms.Clipboard]::GetText()
            }
            '''
            powershell_cmd = 'powershell.exe' if is_wsl else 'powershell'
            result = subprocess.run(
                [powershell_cmd, '-Command', ps_script],
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                lines = result.stdout.strip().split('\n', 1)
                if len(lines) == 2:
                    content_type, content = lines
                    if content_type.strip() == "IMAGE:":
                        img_bytes = base64.b64decode(content.strip())
                        return img_bytes, 'image/png'
                    elif content_type.strip() == "TEXT:":
                        return content.strip(), None
        except Exception as e:
            print(f"Error accessing Windows clipboard: {e}")
        return None
    elif system == 'Darwin':
        try:
            result = subprocess.run(['pngpaste', '-'], capture_output=True)
            if result.returncode == 0 and result.stdout:
                return result.stdout, 'image/png'
            result = subprocess.run(['pbpaste'], capture_output=True, text=True)
            if result.stdout:
                return result.stdout.strip(), None
        except FileNotFoundError:
            print("Error: pngpaste not installed. Install it with 'brew install pngpaste' for image clipboard support")
            try:
                result = subprocess.run(['pbpaste'], capture_output=True, text=True)
                if result.stdout:
                    return result.stdout.strip(), None
            except:
                pass
        except Exception as e:
            print(f"Error accessing macOS clipboard: {e}")
            raise e
    elif system == 'Linux':
        try:
            result = subprocess.run(
                ['xclip', '-selection', 'clipboard', '-t', 'image/png', '-o'],
                capture_output=True
            )
            if result.returncode == 0 and result.stdout:
                return result.stdout, 'image/png'
            result = subprocess.run(
                ['xclip', '-selection', 'clipboard', '-o'],
                capture_output=True,
                text=True
            )
            if result.stdout:
                return result.stdout.strip(), None
        except Exception as e:
            print(f"Error accessing Linux clipboard: {e}")
            raise e
    raise Exception("Clipboard is empty")
