import platform

from importlib import metadata

default_headers = {
    "lang": "python",
    "lang_version": platform.python_version(),
    "machine": platform.machine(),
    "os": platform.platform(),
    "package_version": metadata.version("agentsphere"),
    "processor": platform.processor(),
    "publisher": "agentsphere",
    "release": platform.release(),
    "sdk_runtime": "python",
    "system": platform.system(),
}
