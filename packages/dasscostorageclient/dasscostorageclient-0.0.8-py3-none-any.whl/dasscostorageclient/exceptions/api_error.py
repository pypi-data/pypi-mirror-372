class APIError(Exception):
    def __init__(self, response):
        self.response = response
        self.status_code = response.status_code
        super().__init__(self.create_message())

    def create_message(self):
        return f"API request failed with status code {self.status_code}: {self.response.content}"

