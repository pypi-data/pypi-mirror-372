from dataclasses import dataclass


@dataclass
class MenuItem:
    url: str
    name: str
    extra_html: str = ""
