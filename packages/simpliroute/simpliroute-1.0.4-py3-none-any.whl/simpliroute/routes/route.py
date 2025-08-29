from dataclasses import dataclass, field
import requests
from simpliroute.abstract.abstract_dataclass import  AbstractSimplirouteV1Dataclass   
from dataclasses_json import dataclass_json, config
from simpliroute.config.config import ConfigV1
@dataclass_json
@dataclass
class Route(AbstractSimplirouteV1Dataclass):
    vehicle: int 
    driver: int 
    planned_date: str
    status: str
    total_load: int
    location_start_address: str
    location_end_address: str
    plan: str
    id:str = ''
    endpoint:str = field(default='routes', metadata=config(exclude=lambda x: True))
    estimated_time_start: str = "00:00:00"
    estimated_time_end: str = "23:59:00"
    total_duration: str = '00:00:10'
    total_distance: int = 0
    total_load_percentage: int = 0
    location_start_latitude: str = field(default='', metadata=config(exclude=lambda x: not x))
    location_start_longitude: str = field(default='', metadata=config(exclude=lambda x: not x))
    location_end_latitude: str = field(default='', metadata=config(exclude=lambda x: not x))
    location_end_longitude: str = field(default='', metadata=config(exclude=lambda x: not x))
    comment: str = ""
    visits: list = field(default_factory=list)


    def create(self):
        response = requests.post(f'{self.endpoint_url}/routes/', data=self.to_json(), headers=self.config.headers)
        return response
    
    @classmethod
    def list(cls, config:ConfigV1, plan_id:str):
        response = requests.get(config.get_endpoint(f"plans/routes/{plan_id}/visits/"),headers=config.headers)
        return response
    
    @classmethod
    def get_observations(cls, config:ConfigV1):
        response = requests.get(config.get_endpoint(f"{cls.endpoint}/observations"),headers=config.headers)
        return response
        


    #Create route que tiene un request, en webhook routeobject crearlo como en visit
    #Revisar que campos de la ruta y de la visit para ver que fields van con cual en Odoo