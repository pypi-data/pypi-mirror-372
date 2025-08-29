from dataclasses import dataclass, field
import requests
from simpliroute.abstract.abstract_dataclass import  AbstractSimplirouteV1Dataclass   
from dataclasses_json import dataclass_json, config
from simpliroute.config.config import ConfigV1
@dataclass_json
@dataclass
class Users(AbstractSimplirouteV1Dataclass):
    endpoint:str = field(default='accounts/drivers', metadata=config(exclude=lambda x: True))

    @classmethod
    def list(cls, config:ConfigV1):
        response = requests.get(config.get_endpoint(f"{cls.endpoint}/"),headers=config.headers)
        return response