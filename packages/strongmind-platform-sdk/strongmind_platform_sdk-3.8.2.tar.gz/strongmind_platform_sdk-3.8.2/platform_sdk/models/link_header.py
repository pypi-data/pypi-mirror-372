from dataclasses import dataclass


@dataclass
class LinkHeader:
    first_link: str = None
    prev_link: str = None
    next_link: str = None
    last_link: str = None
