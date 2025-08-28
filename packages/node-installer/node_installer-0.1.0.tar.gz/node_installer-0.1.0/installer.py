#installer.py
import subprocess

def install_node(version="18.18.2"):
    url = f"https://nodejs.org/dist/v{version}/node-v{version}-x64.msi"
    filename = "node.msi"

    # Download Node.js installer via PowerShell
    subprocess.run(["powershell", "iwr", url, "-o", filename], check=True)

    # Silent install using msiexec
    subprocess.run(["msiexec", "/i", filename, "/quiet"], check=True)

    # Verify installation
    subprocess.run(["node", "-v"])
    subprocess.run(["npm", "-v"])
