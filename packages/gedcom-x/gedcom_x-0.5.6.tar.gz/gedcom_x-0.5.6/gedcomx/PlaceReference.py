from typing import Optional

from .Resource import Resource
from .Serialization import Serialization

class PlaceReference:
    identifier = 'http://gedcomx.org/v1/PlaceReference'
    version = 'http://gedcomx.org/conceptual-model/v1'
    
    def __init__(self,
                 original: Optional[str] = None,
                 description: Optional[Resource] = None) -> None:
        self.original = original
        self.description = description

    @property
    def _as_dict_(self):
        type_as_dict = {
            'original': self.original,
            'description': self.description._as_dict_ if self.description else None
            } 
        return Serialization.serialize_dict(type_as_dict)
    
    @classmethod
    def _from_json_(cls, data):
        
        return Serialization.deserialize(data, PlaceReference)



