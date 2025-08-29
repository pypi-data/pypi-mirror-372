import unittest

from faker import Faker
from mockito import mock, unstub, when, verify, patch
from slack_sdk import WebClient

from platform_sdk.clients.slack import SlackClient

fake = Faker()


class TestSlackClient(unittest.TestCase):
    def setUp(self) -> None:
        self.channel = f"#{fake.name()}"
        self.slack_web_client = mock(WebClient)
        self.uut = SlackClient(slack_bot_token=fake.word(), channel=self.channel, slack_client=self.slack_web_client)

    def tearDown(self) -> None:
        unstub()

    def test_it_uses_token(self):
        slack_bot_token = fake.word()

        patch(WebClient.__init__, lambda token: None)

        # Act
        SlackClient(slack_bot_token=slack_bot_token, channel=self.channel)

    def test_it_uploads_contents(self):
        # Arrange
        content = fake.text()
        initial_comment = fake.text()
        title = fake.word()
        filetype = fake.word()
        when(self.slack_web_client).files_upload(...)

        # Act
        self.uut.upload_contents(content, initial_comment, title, filetype)

        # Assert
        verify(self.slack_web_client, times=1).files_upload(channels=self.channel,
                                                            content=content,
                                                            initial_comment=initial_comment,
                                                            title=title,
                                                            filetype=filetype)

    def test_it_posts_message(self):
        # Arrange
        message = fake.text()
        when(self.slack_web_client).chat_postMessage(...)

        # Act
        self.uut.post_message(message)

        # Assert
        verify(self.slack_web_client, times=1).chat_postMessage(channel=self.channel, text=message)


if __name__ == '__main__':
    unittest.main()
