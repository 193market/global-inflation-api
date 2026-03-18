# Global Inflation Tracker API

Global inflation and Consumer Price Index (CPI) data for 190+ countries. Compare inflation rates, find countries with highest/lowest inflation, and track CPI trends over time. Powered by World Bank Open Data.

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | API info and available endpoints |
| `GET /summary` | All inflation indicators snapshot for a country |
| `GET /cpi` | Consumer Price Index inflation rate (annual %) |
| `GET /cpi-index` | CPI level index (2010 = 100) |
| `GET /gdp-deflator` | GDP deflator inflation rate |
| `GET /food-prices` | Food production index |
| `GET /compare` | Compare CPI across multiple countries |
| `GET /highest` | Countries with highest inflation rates |
| `GET /lowest` | Countries with lowest inflation (including deflation) |

## Query Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `country` | ISO3 country code (e.g., USA, DEU, TUR) | `WLD` |
| `countries` | Comma-separated ISO3 codes for /compare (max 10) | `USA,DEU,JPN,GBR,CHN` |
| `limit` | Number of years or countries to return | `10` |

## Data Source

World Bank Open Data
https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG

## Authentication

Requires `X-RapidAPI-Key` header via RapidAPI.
