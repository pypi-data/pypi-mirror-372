# pysh/__init__.py

try:
    from importlib.metadata import version
    __version__ = version("shsim")
except Exception:
    __version__ = "0.0.0"

def hello():
    return "Hello from shsim!"
