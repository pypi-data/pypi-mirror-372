# kamiwaza_sdk/__init__.py
from .client import KamiwazaClient

# Export as kamiwaza_sdk for the import pattern: from kamiwaza_sdk import kamiwaza_sdk as kz
kamiwaza_sdk = KamiwazaClient

__version__ = "0.5.0"