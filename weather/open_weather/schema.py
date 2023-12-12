import datetime
import pydantic


class Coordinates(pydantic.BaseModel):
    lon: float
    lat: float


class Weather(pydantic.BaseModel):
    id: int
    main: str
    description: str
    icon: str


class Wind(pydantic.BaseModel):
    speed: float
    deg: float
    gust: float | None = None


class Clouds(pydantic.BaseModel):
    all: float


class System(pydantic.BaseModel):
    sunrise: datetime.datetime
    sunset: datetime.datetime


class CurrentRequest(pydantic.BaseModel):
    lat: float
    lon: float
    units: str = "metric"
    lang: str = "lang"
    appid: str


class CurrentResponse(pydantic.BaseModel):
    coord: Coordinates
    weather: list[Weather]
    base: str

    class Main(pydantic.BaseModel):
        temp: float
        feels_like: float
        pressure: float
        humidity: float
        temp_min: float
        temp_max: float
        sea_level: float | None = None
        grnd_level: float | None = None

    main: Main
    visibility: float
    wind: Wind
    # rain
    # snow
    dt: datetime.datetime
    sys: System
    timezone: int
    id: int
    name: str
    cod: int
