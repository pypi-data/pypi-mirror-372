# -*- coding: utf-8 -*-

class MockupUser:
    def __init__(self, provider, user, provider_name="authentic-agents"):
        self.provider = provider
        self.provider.name = provider_name
        self.user = user
        self.user.provider = self.provider
        self.user.data = {}
