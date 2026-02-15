import urllib.request
import json
import ssl

def get_latest_version(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(url, context=ctx) as response:
            data = json.loads(response.read().decode())
            return data["info"]["version"]
    except Exception as e:
        return f"Error: {e}"

packages = [
    "Flask",
    "Pillow",
    "piexif",
    "python-dotenv",
    "gunicorn",
    "Flask-WTF",
    "Flask-Talisman",
    "pillow-heif"
]

print("Latest versions:")
for package in packages:
    version = get_latest_version(package)
    print(f"{package}=={version}")
