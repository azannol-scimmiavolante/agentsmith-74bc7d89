"""Entrypoint for running weatherapp as a module (python -m weatherapp)."""

from weatherapp.cli import weather

if __name__ == "__main__":
    weather()
