from dataclasses import dataclass

class AConfig:
    base_url:str = 'https://api.simpliroute.com'

    @property
    def headers(self):
        raise NotImplementedError("You need to subclass this to get a valid header")

    def get_endpoint(self, endpoint:str):
        return f'{self.base_url}/{endpoint}'
    
@dataclass
class ConfigV1(AConfig):
    token:str = None

    def get_endpoint(self, endpoint: str):
        return f'{self.base_url}/v1/{endpoint}' 
    
    @property
    def headers(self):
       return {
        "Content-Type": "application/json",
        "authorization": f"Token {self.token}",
        "Accept": "*/*"
    }


