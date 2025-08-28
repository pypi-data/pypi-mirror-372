from pydantic.dataclasses import dataclass


@dataclass
class Institution:
    name: str


@dataclass
class Pipeline:
    name: str
    institution: str


@dataclass
class Collection:
    name: str
    institution: str


@dataclass
class Workstation:
    name: str
    status: str
    institution: str
