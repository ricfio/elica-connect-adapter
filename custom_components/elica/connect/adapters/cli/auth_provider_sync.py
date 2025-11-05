"""Synchronous wrapper for Async AuthProvider (CLI use)."""

import asyncio


class LocalAuthProviderSync:
    """Synchronous AuthProvider wrapper for CLI."""

    def __init__(self, async_provider_cls, *args, **kwargs):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.provider = async_provider_cls(*args, **kwargs)

    def _run(self, coro):
        return self.loop.run_until_complete(coro)

    def ensure_authenticated(self):
        return self._run(self.provider.ensure_authenticated())

    def authenticate_with_password(self, username, password):
        return self._run(self.provider.authenticate_with_password(username, password))

    def refresh_access_token(self):
        return self._run(self.provider.refresh_access_token())

    def get_access_token(self):
        return self._run(self.provider.get_access_token())

    def authenticate_with_token(self, token):
        return self._run(self.provider.authenticate_with_token(token))
