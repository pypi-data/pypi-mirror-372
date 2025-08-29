import unittest

from platform_sdk.helpers.link_header import links_from_header, get_continuation_token_from_next_link
from platform_sdk.models.link_header import LinkHeader


class TestLinkHeader(unittest.TestCase):
    BASE_URL = 'https://api.platform.strongmind.com/ims/oneroster/v1p1/enrollments/'

    def test_links_from_header_has_next_link(self):
        # Arrange
        link_header_str = f'<{self.BASE_URL}?limit=999&filter=endDate>' \
                          f'=%272021-09-15%27 AND role=student>; rel=\"first\",<{self.BASE_URL}?limit=999&' \
                          f'nextfilter=endDate>%3d%272021-09-15%27+AND+role%3dstudent&continuationToken=XQ%3d%3d>; ' \
                          f'rel=\"next\", <{self.BASE_URL}?limit=999&filter=endDate>%3d%272021-09-15%27+AND' \
                          f'+role%3dstudent&continuationToken=XQ%3d%3d'

        expected_link_header = LinkHeader(first_link=f"{self.BASE_URL}?limit=999&filter=endDate>=%272021-09-15%27 AND "
                                                     f"role=student",
                                          prev_link="",
                                          next_link=f"{self.BASE_URL}?limit=999&nextfilter=endDate>%3d%272021-09-15%27+"
                                                    f"AND+role%3dstudent&continuationToken=XQ%3d%3d",
                                          last_link="")

        # Act
        link_header = links_from_header(link_header_str=link_header_str)

        # Assert
        self.assertEqual(expected_link_header, link_header)

    def test_links_from_header_has_no_next_link(self):
        # Arrange
        link_header_str = f'<{self.BASE_URL}?limit=999&filter=endDate>=%272021-09-15%27 AND role=student>; ' \
                          f'rel=\"first\", <{self.BASE_URL}?limit=999&lastfilter=endDate>%3d%272021-09-15%27+' \
                          'AND+role%3dstudent&continuationToken=XQ%3d%3d>; rel=\"last\""'

        expected_link_header = LinkHeader(first_link=f"{self.BASE_URL}?limit=999&filter=endDate>=%272021-09-15%27 AND "
                                                     f"role=student",
                                          prev_link="",
                                          next_link="",
                                          last_link=f"{self.BASE_URL}?limit=999&lastfilter=endDate>%3d%272021-09-15%27+"
                                                    f"AND+role%3dstudent&continuationToken=XQ%3d%3d")

        # Act
        link_header = links_from_header(link_header_str=link_header_str)

        # Assert
        self.assertEqual(expected_link_header, link_header)

    def test_get_continuation_token_from_next_link(self):
        # Arrange
        expected_continuation_token = "SOME_RANDOM_CONTINUATION_TOKEN_VALUE"
        next_link = f"{self.BASE_URL}?continuationToken={expected_continuation_token}"

        # Act
        returned_continuation_token = get_continuation_token_from_next_link(next_link)

        # Assert
        assert returned_continuation_token == expected_continuation_token

    def test_get_continuation_token_from_next_link_returns_none(self):
        # Arrange
        expected_continuation_token = None
        next_link = f"{self.BASE_URL}"

        # Act
        returned_continuation_token = get_continuation_token_from_next_link(next_link)

        # Assert
        assert returned_continuation_token == expected_continuation_token


if __name__ == '__main__':
    unittest.main()
