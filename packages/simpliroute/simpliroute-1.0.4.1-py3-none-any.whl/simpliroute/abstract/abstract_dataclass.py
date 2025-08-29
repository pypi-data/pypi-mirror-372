import configparser
from dataclasses import asdict, dataclass, field
from dataclasses_json import config, dataclass_json
from simpliroute.config.config import AConfig, ConfigV1

@dataclass_json
@dataclass
class AbstractSimplirouteDataclass:
    config:AConfig = field( metadata=config(exclude=lambda x:True))

    @property
    def endpoint(self):
        raise NotImplementedError("You need to subclass this to get a valid endpoint")

    def asdict(self):
        return asdict(self)
    
@dataclass_json
@dataclass
class AbstractSimplirouteV1Dataclass(AbstractSimplirouteDataclass):
    config:ConfigV1 = field( metadata=config(exclude=lambda x:True))
    # endpoint:str = field(default='no_endpoint', metadata=config(exclude=lambda x: True))

    @property
    def endpoint_url(self):
        return self.config.get_endpoint(self.endpoint)    
