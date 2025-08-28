import subprocess
import platform
import time
import requests

class OllamaEmbedder:
    def __init__(self):
        self.ensure_ollama_installed()

    def ensure_ollama_installed(self) -> bool:
        try:
            subprocess.run(["ollama", "--version"], check=True, capture_output=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("Ollama is not installed. Installing now...")

            os_type = platform.system().lower()

            if os_type in ("darwin", "linux"):
                try:
                    subprocess.run(
                        ["sh", "-c", "curl -fsSL https://ollama.com/install.sh | sh"],
                        check=True
                    )
                    print("✅ Ollama installed successfully.")
                    return True
                except subprocess.CalledProcessError as e:
                    print("❌ Failed to install Ollama automatically.")
                    print("Run this manually:\n  curl -fsSL https://ollama.com/install.sh | sh")
                    return False

            elif os_type == "windows":
                print("⚠️ Automatic install on Windows is not supported.")
                print("Please download and install Ollama manually:")
                print("👉 https://ollama.com/download/windows")
                return False


    def summarize(self, code: str, model: str = "codellama") -> str:
        if not self.ensure_ollama_installed():
            raise RuntimeError("Ollama is not installed. Please follow instructions above.")
        
        ollama_proc = subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,  # or subprocess.PIPE if you want logs
        stderr=subprocess.DEVNULL
        )

        print("Ollama server started (PID:", ollama_proc.pid, ")")

        # Give the server a moment to start
        time.sleep(2)

        # Ensure model is available
        subprocess.run(["ollama", "pull", model], check=False)

        url = "http://localhost:11434/api/generate"
        prompt = f"""Summarize the following error \n\n```python\n{code}\n``` 
        - so that we get to understand the root cause and also list possible solutions also:"""

        resp = requests.post(url, json={"model": model, "prompt": prompt, "stream": False})
        resp.raise_for_status()
        return resp.json()["response"].strip()

