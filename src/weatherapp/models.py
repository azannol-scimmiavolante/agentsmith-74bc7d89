"""Pydantic models for weatherapi.com JSON response structure."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Condition(BaseModel):
    """Weather condition (text, icon, code)."""

    text: str
    icon: str
    code: int


class Location(BaseModel):
    """Location information from the API response."""

    name: str
    region: str
    country: str
    lat: float
    lon: float
    tz_id: str
    localtime_epoch: int
    localtime: str


class CurrentCondition(BaseModel):
    """Current weather conditions."""

    last_updated_epoch: int
    last_updated: str
    temp_c: float
    temp_f: float
    is_day: int
    condition: Condition
    wind_mph: float
    wind_kph: float
    wind_degree: int
    wind_dir: str
    pressure_mb: float
    pressure_in: float
    precip_mm: float
    precip_in: float
    humidity: int
    cloud: int
    feelslike_c: float
    feelslike_f: float
    vis_km: float
    vis_miles: float
    uv: float
    gust_mph: float
    gust_kph: float


class HourlyForecast(BaseModel):
    """Hourly forecast data within a daily forecast."""

    time_epoch: int
    time: str
    temp_c: float
    temp_f: float
    is_day: int
    condition: Condition
    wind_mph: float
    wind_kph: float
    wind_degree: int
    wind_dir: str
    pressure_mb: float
    pressure_in: float
    precip_mm: float
    precip_in: float
    humidity: int
    cloud: int
    feelslike_c: float
    feelslike_f: float
    windchill_c: Optional[float] = None
    windchill_f: Optional[float] = None
    heatindex_c: Optional[float] = None
    heatindex_f: Optional[float] = None
    dewpoint_c: Optional[float] = None
    dewpoint_f: Optional[float] = None
    will_it_rain: int = 0
    chance_of_rain: int = 0
    will_it_snow: int = 0
    chance_of_snow: int = 0
    vis_km: float
    vis_miles: float
    gust_mph: float
    gust_kph: float
    uv: float


class DayDetails(BaseModel):
    """Daily summary statistics for a forecast day."""

    maxtemp_c: float
    maxtemp_f: float
    mintemp_c: float
    mintemp_f: float
    avgtemp_c: float
    avgtemp_f: float
    maxwind_mph: float
    maxwind_kph: float
    totalprecip_mm: float
    totalprecip_in: float
    avgvis_km: float
    avgvis_miles: float
    avghumidity: float
    daily_will_it_rain: int = 0
    daily_chance_of_rain: int = 0
    daily_will_it_snow: int = 0
    daily_chance_of_snow: int = 0
    condition: Condition
    uv: float


class Astro(BaseModel):
    """Astronomical data for a forecast day."""

    sunrise: Optional[str] = None
    sunset: Optional[str] = None
    moonrise: Optional[str] = None
    moonset: Optional[str] = None
    moon_phase: Optional[str] = None
    moon_illumination: Optional[str] = None


class DailyForecast(BaseModel):
    """A single day's forecast with daily summary and hourly breakdown."""

    date: str
    date_epoch: int
    day: DayDetails
    astro: Optional[Astro] = None
    hour: list[HourlyForecast]


class ForecastData(BaseModel):
    """Container for forecast days."""

    forecastday: list[DailyForecast]


class WeatherResponse(BaseModel):
    """Top-level response from weatherapi.com.
    
    Contains location info and either current conditions (for current.json)
    or both current and forecast data (for forecast.json).
    """

    location: Location
    current: Optional[CurrentCondition] = None
    forecast: Optional[ForecastData] = None
