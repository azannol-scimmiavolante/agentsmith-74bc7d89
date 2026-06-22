"""Custom exceptions for the WeatherApp CLI."""

from __future__ import annotations


class WeatherError(Exception):
    """Raised for any user-facing weather app failure.

    Carries an optional ``hint`` describing how the user can recover
    (e.g. fix their API key, check spelling, try again later). The CLI
    layer renders these as Rich panels instead of tracebacks.
    """

    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint

    def __str__(self) -> str:
        return self.message
