import re
from urllib.parse import ParseResult, urlparse, parse_qs

from platform_sdk.models.link_header import LinkHeader


def links_from_header(link_header_str: str) -> LinkHeader:
    first_link = ""
    prev_link = ""
    next_link = ""
    last_link = ""
    if link_header_str:
        link_strings = link_header_str.split(',')
        if link_strings:
            for link_string in link_strings:
                rel_match = re.search(pattern="(?<=rel=\").+?(?=\")",
                                      string=link_string,
                                      flags=re.IGNORECASE)
                link_match = re.search(pattern="(?<=<).+?(?=>;)",
                                       string=link_string,
                                       flags=re.IGNORECASE)
                if rel_match and link_match:
                    rel = rel_match.group(0).upper()
                    link = link_match.group(0)
                    if rel == "FIRST":
                        first_link = link
                    elif rel == "PREV":
                        prev_link = link
                    elif rel == "NEXT":
                        next_link = link
                    elif rel == "LAST":
                        last_link = link

        return LinkHeader(first_link, prev_link, next_link, last_link)
    else:
        return LinkHeader()


def get_continuation_token_from_next_link(next_link: str) -> str:
    parsed_results: ParseResult = urlparse(next_link)
    continuation_token: list[str] = parse_qs(parsed_results.query).get('continuationToken')
    if continuation_token:
        return continuation_token[0]
