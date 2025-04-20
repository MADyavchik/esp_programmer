from dataclasses import dataclass


@dataclass
class PrinterConfig:
    width: int = 176
    height: int = 112
    quantity: int = 2
    density: int = 3

DEFAULT_PRINTER_CONFIG = PrinterConfig()
