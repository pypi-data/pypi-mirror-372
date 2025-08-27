#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import html
import os
from typing import List, Optional, Tuple
import re
from collections import defaultdict
from typing import Iterable, Iterator, List, Optional, Tuple, Union

BOM = '\ufeff'

GEDCOM7_LINE_RE = re.compile(
    r"""^
    (?P<level>\d+)                    # Level
    (?:\s+@(?P<xref>[^@]+)@)?         # Optional record identifier
    \s+(?P<tag>[A-Z0-9_-]+)           # Tag
    (?:\s+(?P<value>.+))?             # Optional value (may be XREF)
    $""",
    re.VERBOSE
)

XREF_RE = re.compile(r'^@[^@]+@$')

# Add hash table for XREF of Zero Recrods?

nonzero = '[1-9]'
level = f'(?P<level>0|{nonzero}[0-9]*)'
atsign = '@'
underscore = '_'
ucletter = '[A-Z]'
tagchar = f'({ucletter}|[0-9]|{underscore})'
xref = f'{atsign}({tagchar})+{atsign}'
d = '\\ '
stdtag = f'{ucletter}({tagchar})*'
exttag = f'{underscore}({tagchar})+'
tag = f'({stdtag}|{exttag})'
voidptr = '@VOID@'
pointer = f'(?P<pointer>{voidptr}|{xref})'
nonat = '[\t -?A-\\U0010ffff]'
noneol = '[\t -\\U0010ffff]'
linestr = f'(?P<linestr>({nonat}|{atsign}{atsign})({noneol})*)'
lineval = f'({pointer}|{linestr})'
eol = '(\\\r(\\\n)?|\\\n)'
line = f'{level}{d}((?P<xref>{xref}){d})?(?P<tag>{tag})({d}{lineval})?{eol}'

from typing import List, Optional, Iterator, Union


class GedcomRecord():
    def __init__(
        self,
        line_num: Optional[int] = None,
        level: int = -1,
        tag: str = "NONR",
        xref: Optional[str] = None,
        value: Optional[str] = None,
    ) -> None:
        self.line = line_num
        self._subRecords: List[GedcomRecord] = []
        self.level = int(level)
        self.xref = xref
        self.pointer: bool = False
        self.tag = str(tag).strip()
        self.value = value

        self.parent: Optional[GedcomRecord] = None
        self.root: Optional[GedcomRecord] = None

    # ───────────────────────────────
    # Dict/JSON friendly view
    # ───────────────────────────────
    @property
    def _as_dict_(self):
        return {
            "level": self.level,
            "xref": self.xref,
            "tag": self.tag,
            "pointer": self.pointer,
            "value": self.value,
            "subrecords": [sub._as_dict_ for sub in self._subRecords],
        }

    # ───────────────────────────────
    # Subrecord management
    # ───────────────────────────────
    def addSubRecord(self, record: "GedcomRecord"):
       
        if record is not None and (record.level == (self.level + 1)):
            record.parent = self
            self._subRecords.append(record)
        else:
            raise ValueError(
                f"SubRecord must be next level from this record (level:{self.level}, subRecord has level {record.level})"
            )

    def recordOnly(self):
        return GedcomRecord(
            line_num=self.line, level=self.level, tag=self.tag, value=self.value
        )

    # ───────────────────────────────
    # Pretty printers
    # ───────────────────────────────
    def dump(self) -> str:
        record_dump = (
            f"Level: {self.level}, tag: {self.tag}, value: {self.value}, "
            f"subRecords: {len(self._subRecords)}\n"
        )
        for record in self._subRecords:
            record_dump += "\t" + record.dump()
        return record_dump

    def describe(self, subRecords: bool = False) -> str:
        level_str = "\t" * self.level
        description = (
            f"Line {self.line}: {level_str} Level: {self.level}, "
            f"tag: '{self.tag}', xref={self.xref} value: '{self.value}', "
            f"subRecords: {len(self._subRecords)}"
        )
        if subRecords:
            for subRecord in self.subRecords():
                description += "\n" + subRecord.describe(subRecords=True)
        return description

    # ───────────────────────────────
    # Subrecord access
    # ───────────────────────────────
    def subRecord(self, tag: str):
        result = [r for r in self._subRecords if r.tag == tag]
        return None if not result else result

    def subRecords(self, tag: str = None):
        if not tag:
            return self._subRecords
        tags = tag.split("/", 1)

        # Collect matching first-level subrecords
        matches = [r for r in self._subRecords if r.tag == tags[0]]
        if not matches:
            return None

        if len(tags) == 1:
            return matches

        # Recurse deeper
        results = []
        for r in matches:
            sub_result = r.subRecords(tags[1])
            if sub_result:
                if isinstance(sub_result, list):
                    results.extend(sub_result)
                else:
                    results.append(sub_result)
        return results if results else None

    # ───────────────────────────────
    # Iteration / Subscriptability
    # ───────────────────────────────
    def __call__(self) -> str:
        return self.describe()

    def __iter__(self) -> Iterator["GedcomRecord"]:
        """Iterates recursively over self and all subrecords."""
        yield from self._flatten_subrecords(self)

    def _flatten_subrecords(self, record: "GedcomRecord") -> Iterator["GedcomRecord"]:
        yield record
        for sub in record._subRecords:
            yield from self._flatten_subrecords(sub)

    def __len__(self) -> int:
        return len(self._subRecords)

    def __getitem__(self, key: Union[int, slice, str]) -> Union["GedcomRecord", List["GedcomRecord"]]:
        """
        - rec[0] -> first subrecord
        - rec[1:3] -> slice of subrecords
        - rec['NAME'] -> list of subrecords with tag 'NAME'
        """
        if isinstance(key, int) or isinstance(key, slice):
            return self._subRecords[key]
        if isinstance(key, str):
            matches = [r for r in self._subRecords if r.tag == key]
            if not matches:
                raise KeyError(f"No subrecords with tag '{key}'.")
            return matches[0] if len(matches) == 1 else matches
        raise TypeError(f"Unsupported key type: {type(key).__name__}")

    def __contains__(self, key: object) -> bool:
        if isinstance(key, str):
            return any(r.tag == key for r in self._subRecords)
        if isinstance(key, int):
            return 0 <= key < len(self._subRecords)
        return False


TagKey = str
IndexKey = int
Key = Union[IndexKey, slice, TagKey]

class Gedcom5x():
    """
    Object representing a Genealogy in legacy GEDCOM 5.x / 7 format. 

    Parameters
    ----------
    records : List[GedcomReord]
        List of GedcomRecords to initialize the genealogy with
    filepath : str
        path to a GEDCOM (``*``.ged), if provided object will read, parse and initialize with records in the file.
    
    Note
    ----
    **file_path** takes precidence over **records**.
    If no arguments are provided, Gedcom Object will initialize with no records.
    
    """
    _top_level_tags = ['INDI', 'FAM', 'OBJE', 'SOUR', 'REPO', 'NOTE', 'HEAD','SNOTE']
  
    def __init__(self, records: Optional[List[GedcomRecord]] = None,filepath: str = None) -> None:
        if filepath:
            self.records = self._records_from_file(filepath)
        elif records:
            self.records: List[GedcomRecord] = records if records else []
        
        # Fast tag index: {'HEAD': [rec], 'INDI': [rec1, rec2, ...], ...}
        self._tag_index: dict[str, List[GedcomRecord]] = defaultdict(list)
        self._reindex()
        
        self.header: GedcomRecord | None = None
        self._sources: List[GedcomRecord] = []
        self._repositories: List[GedcomRecord] = []
        self._individuals: List[GedcomRecord] = []
        self._families: List[GedcomRecord] = []
        self._objects: List[GedcomRecord] = []
        self._snotes: List[GedcomRecord] = []
        self.version = None

        if self.records:
            for record in self.records:
                if record.tag == 'HEAD':
                    self.header = record
                    self.version = record['GEDC']['VERS'].value
                if record.tag == 'INDI':
                    self._individuals.append(record)
                if record.tag == 'SOUR' and record.level == 0:
                    self._sources.append(record)
                if record.tag == 'REPO' and record.level == 0:
                    self._repositories.append(record)
                if record.tag == 'FAM' and record.level == 0:
                    self._families.append(record)
                if record.tag == 'OBJE' and record.level == 0:
                    self._objects.append(record)
                if record.tag == 'SNOTE' and record.level == 0:
                    record.xref = record.value
                    self._snotes.append(record)

    # ─────────────────────────────────────────────────────────────
    # Subscriptable & iterable behavior
    # ─────────────────────────────────────────────────────────────
    def _reindex(self) -> None:
        """Rebuild the tag index from self.records."""
        self._tag_index.clear()
        for rec in self.records:
            # Normalize tag just in case
            tag = rec.tag if isinstance(rec.tag, str) else str(rec.tag)
            self._tag_index[tag].append(rec)

    def __len__(self) -> int:
        return len(self.records)

    def __iter__(self) -> Iterator['GedcomRecord']:
        # Enables: for x in gedcom:
        return iter(self.records)

    def __contains__(self, key: object) -> bool:
        # Enables: 'HEAD' in gedcom  (tag membership)
        if isinstance(key, str):
            return key in self._tag_index and len(self._tag_index[key]) > 0
        if isinstance(key, int):
            return 0 <= key < len(self.records)
        return False

    def __getitem__(self, key: Key) -> Union['GedcomRecord', List['GedcomRecord']]:
        """
        - gedcom[0] -> GedcomRecord at index 0
        - gedcom[1:5] -> list of GedcomRecord (slice)
        - gedcom['HEAD'] -> single record if exactly one; otherwise list of matching records
        - gedcom['INDI'] -> list of all INDI records (usually many)
        """
        if isinstance(key, int):
            return self.records[key]
        if isinstance(key, slice):
            return self.records[key]
        if isinstance(key, str):
            matches = self._tag_index.get(key, [])
            if not matches:
                raise KeyError(f"No records with tag '{key}'.")
            # If exactly one match (e.g., HEAD), return the record; otherwise return list
            return matches[0] if len(matches) == 1 else matches
        raise TypeError(f"Unsupported key type: {type(key).__name__}")

    # Optional: convenience helpers
    def by_tag(self, tag: str) -> List['GedcomRecord']:
        """Always return a list of records for a tag (empty list if none)."""
        return list(self._tag_index.get(tag, []))

    def first(self, tag: str) -> Optional['GedcomRecord']:
        """Return the first record with a given tag, or None."""
        lst = self._tag_index.get(tag, [])
        return lst[0] if lst else None

    # If you add/replace records after init, keep the index fresh:
    def append(self, rec: 'GedcomRecord') -> None:
        self.records.append(rec)
        self._tag_index.setdefault(rec.tag, []).append(rec)

    def extend(self, recs: Iterable['GedcomRecord']) -> None:
        self.records.extend(recs)
        for r in recs:
            self._tag_index.setdefault(r.tag, []).append(r)

    def insert(self, idx: int, rec: 'GedcomRecord') -> None:
        self.records.insert(idx, rec)
        self._tag_index.setdefault(rec.tag, []).append(rec)

    def remove(self, rec: 'GedcomRecord') -> None:
        self.records.remove(rec)
        try:
            bucket = self._tag_index.get(rec.tag)
            if bucket:
                bucket.remove(rec)
                if not bucket:
                    del self._tag_index[rec.tag]
        except ValueError:
            pass  # already out of index

    def clear(self) -> None:
        self.records.clear()
        self._tag_index.clear()      
    # =========================================================
    # 2. PROPERTY ACCESSORS (GETTERS & SETTERS)
    # =========================================================
    
    @property
    def json(self):
        import json
        return json.dumps({'Individuals': [indi._as_dict_ for indi in self._individuals]},indent=4)

    def stats(self):
        def print_table(pairs):

            # Calculate the width of the columns
            name_width = max(len(name) for name, _ in pairs)
            value_width = max(len(str(value)) for _, value in pairs)

            # Print the header
            print('GEDCOM Import Results')
            header = f"{'Type'.ljust(name_width)} | {'Count'.ljust(value_width)}"
            print('-' * len(header))
            print(header)
            print('-' * len(header))

            # Print each pair in the table
            for name, value in pairs:
                print(f"{name.ljust(name_width)} | {str(value).ljust(value_width)}")
                
        imports_stats = [
            ('Top Level Records', len(self.records)),
            ('Individuals', len(self.individuals)),
            ('Family Group Records', len(self.families)),
            ('Repositories', len(self.repositories)),
            ('Sources', len(self.sources)),
            ('Objects', len(self.objects))
        ]

        print_table(imports_stats)

    @property
    def sources(self) -> List[GedcomRecord]:
        return self._sources

    @sources.setter
    def sources(self, value: List[GedcomRecord]):
        if not isinstance(value, list) or not all(isinstance(item, GedcomRecord) for item in value):
            raise ValueError("sources must be a list of GedcomRecord objects.")
        self._sources = value

    @property
    def repositories(self) -> List[GedcomRecord]:
        """
        List of **REPO** records found in the Genealogy
        """
        return self._repositories

    @repositories.setter
    def repositories(self, value: List[GedcomRecord]):
        if not isinstance(value, list) or not all(isinstance(item, GedcomRecord) for item in value):
            raise ValueError("repositories must be a list of GedcomRecord objects.")
        self._repositories = value

    @property
    def individuals(self) -> List[GedcomRecord]:
        return self._individuals

    @individuals.setter
    def individuals(self, value: List[GedcomRecord]):
        if not isinstance(value, list) or not all(isinstance(item, GedcomRecord) for item in value):
            raise ValueError("individuals must be a list of GedcomRecord objects.")
        self._individuals = value

    @property
    def families(self) -> List[GedcomRecord]:
        return self._families

    @families.setter
    def families(self, value: List[GedcomRecord]):
        if not isinstance(value, list) or not all(isinstance(item, GedcomRecord) for item in value):
            raise ValueError("families must be a list of GedcomRecord objects.")
        self._families = value

    @property
    def objects(self) -> List[GedcomRecord]:
        return self._objects

    @objects.setter
    def objects(self, value: List[GedcomRecord]):
        if not isinstance(value, list) or not all(isinstance(item, GedcomRecord) for item in value):
            raise ValueError("objects must be a list of GedcomRecord objects.")
        self._objects = value

    

    def write(self) -> bool:
        """
        Method placeholder for writing GEDCOM files.
        
        Raises
        ------
        NotImplementedError
         writing to legacy GEDCOM file is not currently implimented.
        """
        raise NotImplementedError("Writing of GEDCOM files is not implemented.")  

    @staticmethod
    def _records_from_file(filepath: str) -> List[GedcomRecord]:
        def parse_gedcom7_line(line: str) -> Optional[Tuple[int, Optional[str], str, Optional[str], Optional[str]]]:
            """
            Parse a GEDCOM 7 line into: level, xref_id (record), tag, value, xref_value (if value is an @X@)
            
            Returns:
                (level, xref_id, tag, value, xref_value)
            """
            match = GEDCOM7_LINE_RE.match(line.strip())
            if not match:
                return None

            level = int(match.group("level"))
            xref_id = match.group("xref")
            tag = match.group("tag")
            value = match.group("value")
            if value == 'None': value = None
            xref_value = value.strip("@") if value and XREF_RE.match(value.strip()) else None

            return level, xref_id, tag, value, xref_value
        extension = '.ged'

        if not os.path.exists(filepath):
            print(f"File does not exist: {filepath}")
            raise FileNotFoundError
        elif not filepath.lower().endswith(extension.lower()):
            print(f"File does not have the correct extension: {filepath}")
            raise Exception("File does not appear to be a GEDCOM")
        
        print("Reading from GEDCOM file")
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file]

            records = []
            record_map = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None}
            
            for l, line in enumerate(lines):
                if line.startswith(BOM):
                    line = line.lstrip(BOM)
                line = html.unescape(line).replace('&quot;', '')

                if line.strip() == '':
                    continue

                level, tag, value = '', '', ''

                # Split the line into the first two columns and the rest
                parts = line.split(maxsplit=2)
                if len(parts) == 3:
                    level, col2, col3 = parts

                    if col3 in Gedcom5x._top_level_tags:
                        tag = col3
                        value = col2
                    else:
                        tag = col2
                        value = col3
                
                else:
                    level, tag = parts

                level, xref, tag, value, xref_value = parse_gedcom7_line(line)
                
                if xref is None and xref_value is not None:
                    xref = xref_value
               # print(l, level, xref, tag, value, xref_value)
                    
                level = int(level)

                new_record = GedcomRecord(line_num=l + 1, level=level, tag=tag, xref=xref,value=value)
                
                
                if level == 0:
                    records.append(new_record)
                else:
                    new_record.root = record_map[0]
                    new_record.parent = record_map[int(level) - 1]
                    record_map[int(level) - 1].addSubRecord(new_record)
                record_map[int(level)] = new_record
        
        
        return records if records else None

    @staticmethod
    def fromFile(filepath: str) -> 'Gedcom':
        """
        Static method to create a Gedcom object from a GEDCOM file.

        Args:
            filepath (str): The path to the GEDCOM file.

        Returns:
            Gedcom: An instance of the Gedcom class.
        """     
        records = Gedcom._records_from_file(filepath)
        
        gedcom = Gedcom(records=records)      

        return gedcom
    
    def merge_with_file(self, file_path: str) -> bool:
        """
        Adds records from a valid (``*``.ged) file to the current Genealogy

        Args:
            filepath (str): The path to the GEDCOM file.

        Returns:
            bool: Indicates if merge was successful.
        """
        return True

