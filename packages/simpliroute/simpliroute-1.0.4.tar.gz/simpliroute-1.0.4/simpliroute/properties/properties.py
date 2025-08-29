from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
@dataclass_json
@dataclass
class Property:
    city: str
    delivery_type: str
    source: str
    source_ident: str
    merchant: str