"""Plain values and helpers shared by auth tests. Fixtures stay in conftest.py; import these instead."""

from datetime import datetime, timedelta

TEST_PASSWORD = "correct-horse-battery"
TOKEN_LIFETIME = timedelta(minutes=60)


class FakeClock:
    """A clock the test moves by hand, so expiry is tested without sleeping."""

    def __init__(self, start: datetime) -> None:
        self.current_time = start

    def __call__(self) -> datetime:
        return self.current_time

    def advance(self, duration: timedelta) -> None:
        self.current_time += duration
