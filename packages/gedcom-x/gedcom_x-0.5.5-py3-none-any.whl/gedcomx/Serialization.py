from typing import Dict

from .Logging import get_logger

log = get_logger(__name__)
log.setLevel("DEBUG")
log.info("Logger initialized.")

from collections.abc import Sized
from typing import Any, get_origin, get_args, List, Set, Tuple, Dict, Union, ForwardRef, Annotated
import types

import enum
from .Resource import Resource
from .Identifier import IdentifierList
from .URI import URI

_PRIMITIVES = (str, int, float, bool, type(None))

def _has_parent_class(obj) -> bool:
    return hasattr(obj, '__class__') and hasattr(obj.__class__, '__bases__') and len(obj.__class__.__bases__) > 0


class Serialization:

    @staticmethod
    def serialize_dict(dict_to_serialize: dict) -> dict:
        """
        Iterates through the dict, serilaizing all Gedcom Types into a json compatible value
        
        Parameters
        ----------
        dict_to_serialize: dict
            dict that has been created from any Gedcom Type Object's _as_dict_ property

        Raises
        ------
        ValueError
            If `id` is not a valid UUID.
        """
        def _serialize(value):
            if isinstance(value, (str, int, float, bool, type(None))):
                return value
            elif isinstance(value, dict):
                return {k: _serialize(v) for k, v in value.items()}
            elif isinstance(value, (list, tuple, set)):
                return [_serialize(v) for v in value]
            elif hasattr(value, "_as_dict_"):
                return value._as_dict_
            else:
                return str(value)  # fallback for unknown objects
        
        if dict_to_serialize and isinstance(dict_to_serialize,dict):
            for key, value in dict_to_serialize.items():
                if value is not None:
                    dict_to_serialize[key] = _serialize(value)
        
            return {
                    k: v
                    for k, v in dict_to_serialize.items()
                    if v is not None and not (isinstance(v, Sized) and len(v) == 0)
                }
        return {}
   
    @staticmethod
    def _coerce_value(value: Any, typ: Any) -> Any:
        """Coerce `value` to `typ`:
        - primitives: pass through
        - containers: recurse into elements
        - objects: call typ._from_json_(dict) if available and value is dict
        - already-instantiated objects of typ: pass through
        - otherwise: return value unchanged
        """
        def is_enum_type(T) -> bool:
            """Return True if T (possibly a typing construct) is or contains an Enum type."""
            origin = get_origin(T)

            # Unwrap Union/Optional/PEP 604 (A | B)
            if origin in (Union, types.UnionType):
                return any(is_enum_type(a) for a in get_args(T))

            # Unwrap Annotated[T, ...]
            if origin is Annotated:
                return is_enum_type(get_args(T)[0])

            # Resolve forward refs / strings if you use them
            if isinstance(T, ForwardRef):
                T = globals().get(T.__forward_arg__, T)
            if isinstance(T, str):
                T = globals().get(T, T)

            # Finally check enum-ness
            try:
                return issubclass(T, enum.Enum)
            except TypeError:
                return False  # not a class (e.g., typing.List[int], etc.)
        log.debug(f"Coercing value '{value}' of type '{type(value).__name__}' to '{typ}'")

        def _resolve(t):
            # resolve ForwardRef('Resource') -> actual object if already in globals()
            if isinstance(t, ForwardRef):
                return globals().get(t.__forward_arg__, t)
            return t

        if is_enum_type(typ):
            log.debug(f"Enum type detected: {typ}")
            return typ(value)  # cast to enum
        
        origin = get_origin(typ)
        if origin in (Union, types.UnionType):
            args = tuple(_resolve(a) for a in get_args(typ))
        else:
            args = (_resolve(typ),)
        log.debug(f"Origin: {origin}, args: {args}")
        
        if Resource in args and isinstance(value, dict):
            if Resource in args:
                log.info(f"Deserializing Resource from value: {value}")
                return Resource(uri=value.get('resource'), id=value.get('resourceId', None))

        if isinstance(value, _PRIMITIVES):
            if Resource in args:
                log.info(f"Deserializing Resource from value: {value}")
                return Resource(uri=value)
            if URI in args:
                log.info(f"Deserializing URI from value: {value}")
                return URI.from_url(value)
            return value
        
        if IdentifierList in args:
                log.error(f"Deserializing IdentifierList from value: {value}")
                return IdentifierList._from_json_(value)
  
        if origin in (list, List):
            elem_args = get_args(typ)          # NOT get_args(args)
            elem_t = elem_args[0] if elem_args else Any
            log.debug(f"List: {typ}, elem={elem_t}")
            return [Serialization._coerce_value(v, elem_t) for v in (value or [])]

        if origin in (set, Set):
            (elem_t,) = args or (Any,)
            return { Serialization._coerce_value(v, elem_t) for v in (value or []) }

        if origin in (tuple, Tuple):
            if not args:
                return tuple(value)
            if len(args) == 2 and args[1] is Ellipsis:  # Tuple[T, ...]
                elem_t = args[0]
                return tuple(Serialization._coerce_value(v, elem_t) for v in (value or []))
            return tuple(Serialization._coerce_value(v, t) for v, t in zip(value, args))

        if origin in (dict, Dict):
            k_t, v_t = args or (Any, Any)
            return {
                Serialization._coerce_value(k, k_t): Serialization._coerce_value(v, v_t)
                for k, v in (value or {}).items()
            }

        # If `typ` has _from_json_ and value is a dict, use it
        if hasattr(typ, "_from_json_") and isinstance(value, dict):
            log.info(f"Deserializing {typ} from json method with value: {value}")
            return typ._from_json_(value)

        # If already the right type, keep it
        try:
            if isinstance(value, typ):
                return value
        except TypeError:
            log.debug(f"Could not coerce value '{value}' to type '{typ}'")
            pass  # `typ` may be a typing construct not valid for isinstance

        # Fallback: leave as-is
        log.debug(f"Returning '{type(value)}' type")
        return value

    @staticmethod
    def get_class_fields(cls_name) -> Dict:
        from typing import List, Optional
        from gedcomx.Attribution import Attribution
        from gedcomx.Document import Document  , DocumentType, TextType 
        from gedcomx.Note import Note
        from gedcomx.Resource import Resource
        from gedcomx.SourceReference import SourceReference
        from gedcomx.extensions.rs10.rsLink import _rsLinkList
        from gedcomx.Conclusion import ConfidenceLevel
        from gedcomx.EvidenceReference import EvidenceReference
        from gedcomx.Identifier import IdentifierList
        from gedcomx.Gender import  Gender, GenderType
        from gedcomx.Fact import Fact
        from gedcomx.Name import Name  
        from gedcomx.URI import URI
        from gedcomx.Qualifier import Qualifier 
        from gedcomx.PlaceDescription import PlaceDescription
        from gedcomx.PlaceReference import PlaceReference   
        from gedcomx.Person import Person
        from gedcomx.Relationship import Relationship, RelationshipType
        from gedcomx.Identifier import Identifier   
        from gedcomx.Date import Date
        from gedcomx.TextValue import TextValue
        from gedcomx.Address import Address
        from gedcomx.OnlineAccount import OnlineAccount
        from gedcomx.Event import Event, EventType, EventRole
        from .SourceDescription import SourceDescription

        fields = { 'Conclusion' : {
                                    "id": str,
                                    "lang": str,
                                    "sources": List["SourceReference"],
                                    "analysis": Document | Resource,
                                    "notes": List[Note],
                                    "confidence": ConfidenceLevel,
                                    "attribution": Attribution,
                                    "uri": "Resource",
                                    "max_note_count": int,
                                    "links": _rsLinkList
                                    },
                    'Subject' : {
                                    "id": str,
                                    "lang": str,
                                    "sources": List["SourceReference"],
                                    "analysis": Resource,
                                    "notes": List["Note"],
                                    "confidence": ConfidenceLevel,
                                    "attribution": Attribution,
                                    "extracted": bool,
                                    "evidence": List[EvidenceReference],
                                    "media": List[SourceReference],
                                    "identifiers": IdentifierList,
                                    "uri": Resource,
                                    "links": _rsLinkList
                                },
                    'Person' : {
                                    "id": str,
                                    "lang": str,
                                    "sources": List[SourceReference],
                                    "analysis": Resource,
                                    "notes": List[Note],
                                    "confidence": ConfidenceLevel,
                                    "attribution": Attribution,
                                    "extracted": bool,
                                    "evidence": List[EvidenceReference],
                                    "media": List[SourceReference],
                                    "identifiers": IdentifierList,
                                    "private": bool,
                                    "gender": Gender,
                                    "names": List[Name],
                                    "facts": List[Fact],
                                    "living": bool,
                                    "links": _rsLinkList,
                                    'uri': Resource
                                },
                    'SourceReference' : {
                                    "description": SourceDescription | URI | Resource,
                                    "descriptionId": str,
                                    "attribution": Attribution,
                                    "qualifiers": List[Qualifier],
},
                    'Attribution' : {
                                    "contributor": Resource | Attribution,
                                    "modified": str,
                                    "changeMessage": str,
                                    "creator": Resource | Attribution,
                                    "created": str  
        },
                    'Gender' : {
                                    "id": str,
                                    "lang": str,
                                    "sources": List[SourceReference],
                                    "analysis": Resource,
                                    "notes": List[Note],
                                    "confidence": ConfidenceLevel,
                                    "attribution": Attribution,
                                    "type": GenderType,
                                                    },
                    'PlaceReference' : {
                                    "original": str,
                                    "description": PlaceDescription | URI,
                                    },
                    'Relationship' : {
                                    "id": str,
                                    "lang": str,
                                    "sources": List[SourceReference],
                                    "analysis": Document | Resource,
                                    "notes": List[Note],
                                    "confidence": ConfidenceLevel,
                                    "attribution": Attribution,
                                    "extracted": bool,
                                    "evidence": List[EvidenceReference],
                                    "media": List[SourceReference],
                                    "identifiers": IdentifierList,
                                    "type": RelationshipType,
                                    "person1": Person | Resource,
                                    "person2": Person | Resource,
                                    "facts": List[Fact],
},
                    'Document' : {
                                    "id": str,
                                    "lang": str,
                                    "sources": List[SourceReference],
                                    "analysis": Resource,
                                    "notes": List[Note],
                                    "confidence": ConfidenceLevel,
                                    "attribution": Attribution,
                                    "type": DocumentType,
                                    "extracted": bool,
                                    "textType": TextType,
                                    "text": str,
                                },
                    'PlaceDescription' : {
                                    "id": str,
                                    "lang": str,
                                    "sources": List[SourceReference],
                                    "analysis": Resource,
                                    "notes": List[Note],
                                    "confidence": ConfidenceLevel,
                                    "attribution": Attribution,
                                    "extracted": bool,
                                    "evidence": List[EvidenceReference],
                                    "media": List[SourceReference],
                                    "identifiers": List[IdentifierList],
                                    "names": List[TextValue],
                                    "type": str,
                                    "place": URI,
                                    "jurisdiction": Resource | PlaceDescription,
                                    "latitude": float,
                                    "longitude": float,
                                    "temporalDescription": Date,
                                    "spatialDescription": Resource,
                                },
                    "Agent" : {
    "id": str,
    "identifiers": IdentifierList,
    "names": List[TextValue],
    "homepage": URI,
    "openid": URI,
    "accounts": List[OnlineAccount],
    "emails": List[URI],
    "phones": List[URI],
    "addresses": List[Address],
    "person": object | Resource,  # intended to be Person | Resource
    # "xnotes": List[Note],  # commented out in your __init__
    "attribution": object,  # for GEDCOM5/7 compatibility
    "uri": URI | Resource,
},
'Event' : {
    "id": str,
    "lang": str,
    "sources": List[SourceReference],
    "analysis": Resource,
    "notes": List[Note],
    "confidence": ConfidenceLevel,
    "attribution": Attribution,
    "extracted": bool,
    "evidence": List[EvidenceReference],
    "media": List[SourceReference],
    "identifiers": List[Identifier],
    "type": EventType,
    "date": Date,
    "place": PlaceReference,
    "roles": List[EventRole],
}

}
        
        
        return fields[cls_name] if cls_name in fields else {}

    @staticmethod
    def deserialize(data: dict[str, Any], class_type) -> Any:
        """
        Deserialize `data` according to `fields` (field -> type).
        - Primitives are assigned directly.
        - Objects use `type._from_json_(dict)` when present.
        - Lists/Sets/Tuples/Dicts are recursively processed.
        Returns (result, unknown_keys).
        """
        log.debug(f"Deserializing '{data}' into '{class_type.__name__}'")
        class_fields = Serialization.get_class_fields(str(class_type.__name__))
        if class_fields == {}:
            log.warning(f"No class fields found for '{class_type.__name__}'")
        log.debug(f"class fields: {class_fields}")
        result: dict[str, Any] = {}
        known = set(class_fields.keys())
        log.debug(f"keys found in JSON: {data.keys()}")
        #log.debug(f"known fields: {known}")
        for name, typ in class_fields.items():
            if name in data:
                log.debug(f"Field '{name}' of {class_type.__name__} found in data")
                result[name] = Serialization._coerce_value(data[name], typ)
                #if type(result[name]) != class_fields[name]:# TODO Write better type checking 
                #    log.error(f"Field '{name}' of {class_type.__name__} was expected to be of type '{class_fields[name]}', but got '{type(result[name])}' with value '{result[name]}'")
                #    raise TypeError(f"Field '{name}' expected type '{class_fields[name]}', got '{type(result[name])}'")
                log.debug(f"Field '{name}' of '{class_type.__name__}' resulted in a '{type(result[name]).__name__}' with value '{result[name]}'")
            else:
                log.debug(f"Field '{name}' of '{class_type.__name__}' not found in JSON data")

        unknown_keys = [k for k in data.keys() if k not in known]
        log.info(f"Creating instance of {class_type.__name__} with fields: {result.keys()}")
        new_cls = class_type(**result)
        log.debug(f"Deserialized {class_type.__name__} with unknown keys: {unknown_keys}")
        return new_cls  # type: ignore, unknown_keys