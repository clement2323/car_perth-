"""
FastAPI backend — Vercel Python serverless runtime.
Tous les /api/* sont routés ici via vercel.json rewrites.
Les CSV dans data/ sont lus en lecture seule (committés dans le repo).
"""

import sys
from pathlib import Path

# Vercel : s'assurer que le dossier racine du projet est dans sys.path
# pour pouvoir importer scoring.py, reliability.py, etc.
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from typing import Optional

import pandas as pd
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from scoring import add_scores_to_dataframe, compute_score, estimate_total_cost
from reliability import RELIABILITY_DB
from scraper_carsales import OUTPUT_FILE as CARSALES_CSV, generate_sample_data
from scraper_capital_motors import (
    OUTPUT_FILE as CAPITAL_CSV,
    generate_sample_data_capital,
)

app = FastAPI(title="Achat Voiture Perth WA API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Cache module-level (DataFrames mutables — pas lru_cache)
# ---------------------------------------------------------------------------
_cache: dict = {"carsales": None, "capital": None}


def _load_carsales() -> pd.DataFrame:
    if _cache["carsales"] is not None:
        return _cache["carsales"]

    if CARSALES_CSV.exists():
        df = pd.read_csv(CARSALES_CSV)
    else:
        df = pd.DataFrame(generate_sample_data())

    for col in ("year", "km", "price"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["price", "km"])
    df["year"] = df["year"].fillna(2015).astype(int)
    df["km"] = df["km"].astype(int)
    df["price"] = df["price"].astype(float)
    df = add_scores_to_dataframe(df)

    _cache["carsales"] = df
    return df


def _load_capital() -> pd.DataFrame:
    if _cache["capital"] is not None:
        return _cache["capital"]

    if CAPITAL_CSV.exists():
        df = pd.read_csv(CAPITAL_CSV)
    else:
        df = pd.DataFrame(generate_sample_data_capital())

    for col in ("year", "km", "price"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["price"])
    df["year"] = df["year"].fillna(2015).astype(int)
    df["km"] = df["km"].fillna(0).astype(int)
    df["price"] = df["price"].astype(float)

    _cache["capital"] = df
    return df


def _invalidate_cache():
    _cache["carsales"] = None
    _cache["capital"] = None


def _df_to_records(df: pd.DataFrame) -> list[dict]:
    df = df.where(pd.notnull(df), None)
    return df.to_dict(orient="records")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/api/listings")
def get_listings(
    max_price: Optional[float] = None,
    max_km: Optional[int] = None,
    models: Optional[str] = None,
    seller_type: Optional[str] = None,
):
    df = _load_carsales().copy()

    if max_price:
        df = df[df["price"] <= max_price]
    if max_km:
        df = df[df["km"] <= max_km]
    if models:
        model_list = [m.strip() for m in models.split(",")]
        mask = df.apply(lambda r: f"{r['make']} {r['model']}" in model_list, axis=1)
        df = df[mask]
    if seller_type and seller_type != "all":
        df = df[df["seller_type"] == seller_type]

    records = _df_to_records(df)
    for rec in records:
        make = rec.get("make") or ""
        model = rec.get("model") or ""
        year = int(rec.get("year") or 2015)
        km = int(rec.get("km") or 0)
        price = float(rec.get("price") or 0)
        median_price = float(rec.get("median_price") or price)
        scored = compute_score(make, model, year, km, price, median_price)
        rec["alerts"] = scored["alerts"]

    return sorted(records, key=lambda x: (x.get("score") or 0), reverse=True)


@app.get("/api/capital-motors")
def get_capital_motors():
    capital_df = _load_capital().copy()
    carsales_df = _load_carsales()

    medians = (
        carsales_df.groupby(["make", "model"])["price"]
        .median()
        .reset_index()
        .rename(columns={"price": "market_median"})
    )
    capital_df = capital_df.merge(medians, on=["make", "model"], how="left")
    capital_df["diff_pct"] = (
        (capital_df["price"] - capital_df["market_median"])
        / capital_df["market_median"]
        * 100
    ).round(1)

    records = _df_to_records(capital_df)
    records.sort(key=lambda x: (x.get("diff_pct") is None, x.get("diff_pct") or 0))
    return records


@app.get("/api/reliability")
def get_reliability():
    return RELIABILITY_DB


@app.get("/api/stats")
def get_stats():
    df = _load_carsales()
    if df.empty:
        return []

    result = []
    for (make, model), grp in df.groupby(["make", "model"]):
        result.append({
            "make": make,
            "model": model,
            "count": int(len(grp)),
            "median_price": round(float(grp["price"].median()), 0),
            "min_price": round(float(grp["price"].min()), 0),
            "max_price": round(float(grp["price"].max()), 0),
            "median_km": round(float(grp["km"].median()), 0),
            "avg_score": round(float(grp["score"].mean()), 1) if "score" in grp else None,
            "last_scraped": str(grp["date_scraped"].max()) if "date_scraped" in grp else None,
        })
    return sorted(result, key=lambda x: x["model"])


class TcoRequest(BaseModel):
    make: str
    model: str
    year: int
    km: int
    price: float
    years: int = 5


@app.post("/api/tco")
def calculate_tco(body: TcoRequest):
    return estimate_total_cost(
        make=body.make,
        model=body.model,
        year=body.year,
        km=body.km,
        price=body.price,
        years=body.years,
    )


def _run_scrapers():
    """Lance les scrapers localement (dev uniquement — pas de filesystem sur Vercel)."""
    import subprocess
    script_dir = ROOT
    subprocess.run([sys.executable, "scraper_carsales.py", "--sample"], cwd=script_dir, capture_output=True)
    subprocess.run([sys.executable, "scraper_capital_motors.py", "--sample"], cwd=script_dir, capture_output=True)
    _invalidate_cache()


@app.post("/api/refresh")
def refresh_data(background_tasks: BackgroundTasks):
    background_tasks.add_task(_run_scrapers)
    return {"status": "ok", "message": "Actualisation lancée (données en cache invalidées)"}


# ---------------------------------------------------------------------------
# Point d'entrée direct (dev local : uvicorn api.index:app --reload)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.index:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=[str(ROOT)])
