from typing import List, TypedDict

class NotifierConfig(TypedDict):
    name: str
    events: List[str]

