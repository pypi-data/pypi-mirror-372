from slack_sdk import WebClient


# Wrapper for Slack WebClient
class SlackClient:
    def __init__(self, slack_bot_token: str, channel: str, slack_client: WebClient = None):
        self.client = slack_client if slack_client else WebClient(token=slack_bot_token)
        self.channel = channel

    def upload_contents(self, content, initial_comment, title, filetype='json'):
        self.client.files_upload(channels=self.channel,
                                 content=content,
                                 initial_comment=initial_comment,
                                 title=title,
                                 filetype=filetype)

    def post_message(self, message):
        self.client.chat_postMessage(channel=self.channel, text=message)
