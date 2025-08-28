from dataclasses import asdict, dataclass, field
from typing import List
import json

from simpliroute.abstract.abstract_dataclass import  AbstractSimplirouteV1Dataclass
from simpliroute.config.config import ConfigV1   
import requests
from dataclasses_json import dataclass_json, config
from simpliroute.items.item import Item

@dataclass_json
@dataclass
class Vehicle(AbstractSimplirouteV1Dataclass):
    name: str
    capacity: int
    location_start_address: str
    location_start_latitude: str
    location_start_longitude: str
    location_end_address: str
    location_end_latitude: str
    location_end_longitude: str
    default_driver: int = None
    endpoint:str = field(default='routes/vehicles/', metadata=config(exclude=lambda x: True))
    skills: list = field(default_factory=list)

    def create(self):
        response = requests.post(f'{self.endpoint_url}/', data=self.to_json(), headers=self.config.headers)
        return response
    
        
    @classmethod
    def list(cls, config:ConfigV1):
        response = requests.get(config.get_endpoint(f"{cls.endpoint}/"),headers=config.headers)
        return response
    
    @classmethod
    def delete(cls, config:ConfigV1, vechile_id:int):
        delete_url = config.get_endpoint(f"{cls.endpoint}/{vechile_id}/")
        response = requests.delete(delete_url, headers=config.headers)
        return response
    
    