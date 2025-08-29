from .dccConv import XMLToJson, JSONToXML

# Try to import dccServer only if FastAPI is installed
try:
    from .dccServer import app  # FastAPI app
except ImportError:
    app = None