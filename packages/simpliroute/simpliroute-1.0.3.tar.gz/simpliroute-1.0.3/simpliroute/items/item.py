from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
@dataclass_json
@dataclass
class Item:
    id: int
    title: str
    load: float
    reference: str
    quantity_planned: float
    
    status: str = "pending"
    load_2: float = 0
    load_3: float = 0
    notes: str = ""
    quantity_delivered: float = field(default=None, metadata=config(exclude=lambda x: not x))
