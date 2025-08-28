from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TypeVar

IManifest = TypeVar('IManifest', bound='ManifestBase')


class MalformedJSONRepresentation(Exception):
    pass


class ManifestSource(Enum):
    # 'Our' representation of a clients Data
    # i.e. what's in our SQL database
    local = 'LOCAL'
    # 'Their' data. I.e. data in their Github,
    # Gitlab, BBCloud, or Jira instances
    remote = 'REMOTE'
    # The delta between any two manifests
    delta = 'DELTA'


# Currently used to codify the different types
# of manifests accessible via pulling from S3
# This field IS NOT used in the actual manifest class!
# The actual manifest class uses only str types for
# determining its type; this is to leave the typing
# as generalized as possible
class ManifestType(Enum):
    git = 'GitDataManifest'
    jira = 'JiraDataManifest'


# Separating the model from the adapter behavior as a base class to make the data more transportable and reusable
@dataclass
class ManifestBase(ABC):
    company: str
    # Where the data came from (local, remote, or delta)
    data_source: ManifestSource
    date: datetime = field(init=False)
    manifest_type: str = field(init=False)
    _module_name: str = field(init=False)
