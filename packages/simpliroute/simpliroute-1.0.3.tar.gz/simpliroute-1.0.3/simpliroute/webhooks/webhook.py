from dataclasses import asdict, dataclass, field
from typing import List, TypedDict
import json
from typing_extensions import Self
from simpliroute.abstract.abstract_dataclass import  AbstractSimplirouteV1Dataclass
from simpliroute.config.config import ConfigV1   
import requests
from dataclasses_json import dataclass_json, config
from simpliroute.items.item import Item
import logging
_logger = logging.getLogger(__name__)  

class WebhookRequestBody(TypedDict):
    url: str
    webhook: str
    headers: None
 
@dataclass_json
@dataclass
class Webhook(AbstractSimplirouteV1Dataclass):
    url: str
    webhook: str
    headers: None
    endpoint:str = field(default='addons/webhooks/', metadata=config(exclude=lambda x: True))
    
    def create(self):
        response = requests.post(f'{self.endpoint_url}', data=self.to_json(), headers=self.config.headers)
        _logger.info(self.endpoint_url) 
        _logger.info(self.to_json())
        # if not response.ok:
        #     raise Exception(f'Response fail: {response.text}')
        # self.id = response.json()['id']
        return response
        
    
    @classmethod    
    def update(cls, config:ConfigV1, update_data:WebhookRequestBody):
        update_url = config.get_endpoint(f"{cls.endpoint}")
        response = requests.put(update_url,json=update_data, headers=config.headers)
        return response

    @classmethod
    def delete(cls, config:ConfigV1, webhook:str):
        delete_url = config.get_endpoint(f"{cls.endpoint}")
        response = requests.delete(delete_url, headers=config.headers, json={"webhook":webhook})
        return response
    
    @classmethod
    def get(cls, config:ConfigV1, webhook:str) -> Self:
        response = requests.get(config.get_endpoint(f"{cls.endpoint}"), headers=config.headers, json={"webhook":webhook})        
        return cls.from_dict({"config":config, "webhook":webhook, "url":cls.endpoint})

    @classmethod
    def list(cls, config:ConfigV1) -> List[Self]:
        response = requests.get(config.get_endpoint(f"{cls.endpoint}"), headers=config.headers)        
        # TODO: Get all possible repsonses of webhooks and map them as webhooks
        return cls.from_dict({"config":config, **response.json()})
 
@dataclass_json
@dataclass
class PlanCreatedWebhook(Webhook):
    webhook = "plan_created"

@dataclass_json
@dataclass
class PlanEditedWebhook(Webhook):
    webhook = "plan_edited"

@dataclass_json
@dataclass
class RouteCreatedWebhook(Webhook):
    webhook = "route_created"

@dataclass_json
@dataclass
class RouteStartedWebhook(Webhook):
    webhook = "route_started"
 
@dataclass_json
@dataclass
class RouteFinishedWebhook(Webhook):
    webhook = "route_finished"
 
@dataclass_json
@dataclass
class OnItsWayWebhook(Webhook):
    webhook = "on_its_way"
 
@dataclass_json
@dataclass
class VisitCheckoutWebhook(Webhook):
    webhook = "visit_checkout"
 
@dataclass_json
@dataclass
class VisitCheckoutDetailedWebhook(Webhook):
    webhook = "visit_checkout_detailed"
