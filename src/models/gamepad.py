from dataclasses import dataclass
from typing import Optional


@dataclass
class Gamepad:
    id: str
    name: str
    num_player: Optional[int] = None
    descriptor: Optional[str] = None
    vendor_id: Optional[int] = None
    product_id: Optional[int] = None
    device_path: Optional[str] = None
