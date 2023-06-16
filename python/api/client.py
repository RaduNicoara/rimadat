import openai
from django.conf import settings


class OpenAPIClient:

    def __init__(self):
        self.client = openai
        self.client.api_key = settings.API_KEY
        self.gpt_model = "gpt-3.5-turbo-0301"

    def submit(self, messages) -> str:
        """
        Accepts a list of dictionaries with the following keys: role, content and returns
        a reply to this conversation.
        The messages must be in the order they were created.
        :param messages: List of messages
        :return: replay in string form
        """
        response = self.client.ChatCompletion.create(
            model=self.gpt_model,
            messages=messages,
            temperature=0
        )
        return response["choices"][0]["message"]

