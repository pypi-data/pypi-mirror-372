from typing import List, Optional

from .Attribution import Attribution
from .Conclusion import ConfidenceLevel
from .Date import Date
from .EvidenceReference import EvidenceReference
from .Identifier import IdentifierList
from .Note import Note
from .SourceReference import SourceReference
from .TextValue import TextValue
from .Resource import Resource
from .Serialization import Serialization
from .Subject import Subject
from .URI import URI

class PlaceDescription(Subject):
    identifier = "http://gedcomx.org/v1/PlaceDescription"
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, id: Optional[str] =None,
                 lang: str = 'en',
                 sources: Optional[List[SourceReference]] = None,
                 analysis: Optional[Resource] = None,
                 notes: Optional[List[Note]] =None,
                 confidence: Optional[ConfidenceLevel] = None,
                 attribution: Optional[Attribution] = None,
                 extracted: Optional[bool] = None,
                 evidence: Optional[List[EvidenceReference]] = None,
                 media: Optional[List[SourceReference]] = None,
                 identifiers: Optional[IdentifierList] = None,
                 names: Optional[List[TextValue]] = None,
                 type: Optional[str] = None,
                 place: Optional[URI] = None,
                 jurisdiction: Optional["Resource | PlaceDescription"] = None, # PlaceDescription
                 latitude: Optional[float] = None,
                 longitude: Optional[float] = None,
                 temporalDescription: Optional[Date] = None,
                 spatialDescription: Optional[Resource] = None,) -> None:
        
        super().__init__(id, lang, sources, analysis, notes, confidence, attribution, extracted, evidence, media, identifiers)
        self.names = names
        self.type = type
        self.place = place
        self.jurisdiction = jurisdiction
        self.latitide = latitude
        self.longitute = longitude
        self.temporalDescription = temporalDescription
        self.spacialDescription = spatialDescription

    @property
    def _as_dict_(self):
        type_as_dict = super()._as_dict_
        type_as_dict.update({
            "names": [n for n in self.names] if self.names else None,
            "type": self.type if self.type else None,
            "place": self.place._as_dict_ if self.place else None,
            "jurisdiction": self.jurisdiction._as_dict_ if self.jurisdiction else None,
            "latitude": float(self.latitide) if self.latitide else None,
            "longitude": float(self.longitute) if self.longitute else None,
            "temporalDescription": self.temporalDescription if self.temporalDescription else None,
            "spatialDescription": self.spacialDescription._as_dict_ if self.spacialDescription else None            
        })
        return Serialization.serialize_dict(type_as_dict) 

    @classmethod
    def _from_json_(cls, data: dict):
        """
        Create a PlaceDescription instance from a JSON-dict (already parsed).
        """
        return Serialization.deserialize(data, PlaceDescription)   