from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime

app = FastAPI(
    title="Global Inflation Tracker API",
    description="Global inflation and consumer price index (CPI) data for 190+ countries. Powered by World Bank Open Data.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

WB_BASE = "https://api.worldbank.org/v2"

INDICATORS = {
    "cpi":              {"id": "FP.CPI.TOTL.ZG",  "name": "Inflation, Consumer Prices",    "unit": "Annual %"},
    "cpi_index":        {"id": "FP.CPI.TOTL",      "name": "Consumer Price Index (2010=100)","unit": "Index"},
    "gdp_deflator":     {"id": "NY.GDP.DEFL.KD.ZG","name": "GDP Deflator",                  "unit": "Annual %"},
    "pce":              {"id": "NE.CON.PRVT.KD.ZG","name": "Private Consumption Growth",    "unit": "Annual %"},
    "food_inflation":   {"id": "AG.PRD.FOOD.XD",   "name": "Food Production Index",         "unit": "2014-2016=100"},
}

COUNTRIES = {
    "WLD": "World",
    "USA": "United States",
    "CHN": "China",
    "IND": "India",
    "BRA": "Brazil",
    "RUS": "Russia",
    "ZAF": "South Africa",
    "TUR": "Turkey",
    "ARG": "Argentina",
    "VEN": "Venezuela",
    "ZWE": "Zimbabwe",
    "DEU": "Germany",
    "JPN": "Japan",
    "GBR": "United Kingdom",
    "FRA": "France",
    "ITA": "Italy",
    "KOR": "South Korea",
    "MEX": "Mexico",
    "IDN": "Indonesia",
    "SAU": "Saudi Arabia",
    "EGY": "Egypt",
    "NGA": "Nigeria",
    "ETH": "Ethiopia",
    "PAK": "Pakistan",
    "BGD": "Bangladesh",
    "PHL": "Philippines",
    "VNM": "Vietnam",
    "IRN": "Iran",
    "COL": "Colombia",
    "ESP": "Spain",
    "CAN": "Canada",
    "AUS": "Australia",
    "NZL": "New Zealand",
    "CHE": "Switzerland",
    "SWE": "Sweden",
    "NOR": "Norway",
    "POL": "Poland",
    "UKR": "Ukraine",
    "KAZ": "Kazakhstan",
    "THA": "Thailand",
    "MYS": "Malaysia",
    "SGP": "Singapore",
}


async def fetch_wb_country(country_code: str, indicator_id: str, limit: int = 10):
    url = f"{WB_BASE}/country/{country_code}/indicator/{indicator_id}"
    params = {"format": "json", "mrv": limit, "per_page": limit}
    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.get(url, params=params)
        data = res.json()
    if not data or len(data) < 2:
        return []
    records = data[1] or []
    return [
        {"year": str(r["date"]), "value": r["value"]}
        for r in records
        if r.get("value") is not None
    ]


async def fetch_wb_all_countries(indicator_id: str):
    """Fetch latest value for all countries"""
    url = f"{WB_BASE}/country/all/indicator/{indicator_id}"
    params = {"format": "json", "mrv": 1, "per_page": 300}
    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.get(url, params=params)
        data = res.json()
    if not data or len(data) < 2:
        return []
    records = data[1] or []
    results = []
    for r in records:
        if r.get("value") is not None and r.get("countryiso3code"):
            results.append({
                "country_code": r["countryiso3code"],
                "country": r["country"]["value"],
                "year": str(r["date"]),
                "value": r["value"],
            })
    return results


@app.get("/")
def root():
    return {
        "api": "Global Inflation Tracker API",
        "version": "1.0.0",
        "provider": "GlobalData Store",
        "source": "World Bank Open Data",
        "endpoints": [
            "/summary", "/cpi", "/cpi-index", "/gdp-deflator",
            "/food-prices", "/compare", "/highest", "/lowest"
        ],
        "countries": list(COUNTRIES.keys()),
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/summary")
async def summary(
    country: str = Query(default="WLD", description="ISO3 country code (default: WLD = World)"),
    limit: int = Query(default=5, ge=1, le=30)
):
    """All inflation indicators for a country"""
    country = country.upper()
    results = {}
    for key, meta in INDICATORS.items():
        results[key] = await fetch_wb_country(country, meta["id"], limit)
    formatted = {
        key: {
            "name": INDICATORS[key]["name"],
            "unit": INDICATORS[key]["unit"],
            "data": results[key],
        }
        for key in INDICATORS
    }
    return {
        "country_code": country,
        "country": COUNTRIES.get(country, country),
        "source": "World Bank Open Data",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "indicators": formatted,
    }


@app.get("/cpi")
async def cpi(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Consumer Price Index inflation rate (annual %)"""
    country = country.upper()
    data = await fetch_wb_country(country, "FP.CPI.TOTL.ZG", limit)
    return {
        "indicator": "Inflation, Consumer Prices",
        "series_id": "FP.CPI.TOTL.ZG",
        "unit": "Annual %",
        "frequency": "Annual",
        "country_code": country,
        "country": COUNTRIES.get(country, country),
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }


@app.get("/cpi-index")
async def cpi_index(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Consumer Price Index level (2010 = 100)"""
    country = country.upper()
    data = await fetch_wb_country(country, "FP.CPI.TOTL", limit)
    return {
        "indicator": "Consumer Price Index (2010=100)",
        "series_id": "FP.CPI.TOTL",
        "unit": "Index (2010=100)",
        "frequency": "Annual",
        "country_code": country,
        "country": COUNTRIES.get(country, country),
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }


@app.get("/gdp-deflator")
async def gdp_deflator(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """GDP deflator — annual inflation based on GDP (annual %)"""
    country = country.upper()
    data = await fetch_wb_country(country, "NY.GDP.DEFL.KD.ZG", limit)
    return {
        "indicator": "GDP Deflator",
        "series_id": "NY.GDP.DEFL.KD.ZG",
        "unit": "Annual %",
        "frequency": "Annual",
        "country_code": country,
        "country": COUNTRIES.get(country, country),
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }


@app.get("/food-prices")
async def food_prices(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Food production index (2014-2016 = 100)"""
    country = country.upper()
    data = await fetch_wb_country(country, "AG.PRD.FOOD.XD", limit)
    return {
        "indicator": "Food Production Index",
        "series_id": "AG.PRD.FOOD.XD",
        "unit": "Index (2014-2016=100)",
        "frequency": "Annual",
        "country_code": country,
        "country": COUNTRIES.get(country, country),
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }


@app.get("/compare")
async def compare(
    countries: str = Query(default="USA,DEU,JPN,GBR,CHN", description="Comma-separated ISO3 country codes (max 10)"),
    limit: int = Query(default=5, ge=1, le=20)
):
    """Compare CPI inflation across multiple countries"""
    codes = [c.strip().upper() for c in countries.split(",")][:10]
    results = {}
    for code in codes:
        data = await fetch_wb_country(code, "FP.CPI.TOTL.ZG", limit)
        results[code] = {
            "country": COUNTRIES.get(code, code),
            "data": data,
        }
    return {
        "indicator": "Inflation, Consumer Prices",
        "series_id": "FP.CPI.TOTL.ZG",
        "unit": "Annual %",
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "comparison": results,
    }


@app.get("/highest")
async def highest(
    limit: int = Query(default=20, ge=1, le=50)
):
    """Countries with highest current inflation rates"""
    data = await fetch_wb_all_countries("FP.CPI.TOTL.ZG")
    sorted_data = sorted(
        [d for d in data if len(d["country_code"]) == 3],
        key=lambda x: x["value"] if x["value"] is not None else 0,
        reverse=True
    )
    ranked = [{"rank": i + 1, **entry} for i, entry in enumerate(sorted_data[:limit])]
    return {
        "indicator": "Inflation, Consumer Prices",
        "series_id": "FP.CPI.TOTL.ZG",
        "unit": "Annual %",
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "highest_inflation": ranked,
    }


@app.get("/lowest")
async def lowest(
    limit: int = Query(default=20, ge=1, le=50)
):
    """Countries with lowest current inflation rates (including deflation)"""
    data = await fetch_wb_all_countries("FP.CPI.TOTL.ZG")
    sorted_data = sorted(
        [d for d in data if len(d["country_code"]) == 3],
        key=lambda x: x["value"] if x["value"] is not None else float("inf")
    )
    ranked = [{"rank": i + 1, **entry} for i, entry in enumerate(sorted_data[:limit])]
    return {
        "indicator": "Inflation, Consumer Prices",
        "series_id": "FP.CPI.TOTL.ZG",
        "unit": "Annual %",
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "lowest_inflation": ranked,
    }

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path == "/":
        return await call_next(request)
    key = request.headers.get("X-RapidAPI-Key", "")
    if not key:
        return JSONResponse(status_code=401, content={"detail": "Missing X-RapidAPI-Key header"})
    return await call_next(request)
