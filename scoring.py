"""
Algorithme de scoring "bon achat" (0-100) pour les voitures d'occasion.
Score composite : prix (30%) + km (25%) + fiabilité (30%) + année (15%)
"""

import pandas as pd
from reliability import RELIABILITY_DB, get_model_info, get_danger_alerts


def compute_prix_score(price: float, median_price: float) -> float:
    """
    Score basé sur la position dans le marché.
    < -15% du médian → 100 ; au médian → 50 ; > +20% → 0
    """
    if median_price <= 0:
        return 50.0
    ratio = (price - median_price) / median_price
    if ratio <= -0.15:
        return 100.0
    elif ratio >= 0.20:
        return 0.0
    else:
        # Interpolation linéaire entre -15% (100) et +20% (0)
        return 100.0 * (0.20 - ratio) / (0.20 + 0.15)


def compute_km_score(make: str, model: str, km: int) -> float:
    """
    Score kilométrage : pénalité progressive selon les seuils de danger.
    Base: 100 - pénalités cumulées
    """
    base_score = 100.0

    # Pénalité linéaire basée sur le km absolu (100k = score 70, 200k = score 20)
    if km <= 50000:
        base_score = 100.0
    elif km <= 100000:
        base_score = 100.0 - (km - 50000) / 50000 * 30  # 100 → 70
    elif km <= 150000:
        base_score = 70.0 - (km - 100000) / 50000 * 30  # 70 → 40
    elif km <= 200000:
        base_score = 40.0 - (km - 150000) / 50000 * 25  # 40 → 15
    else:
        base_score = max(0.0, 15.0 - (km - 200000) / 50000 * 15)

    # Pénalités supplémentaires selon les danger zones
    info = get_model_info(make, model)
    if info:
        for zone in info.get("danger_zones", []):
            threshold = zone["km_threshold"]
            diff = threshold - km
            severity = zone["severity"]

            if diff < 0:
                # Seuil dépassé sans documentation → pénalité forte
                penalty = {"critical": 30, "high": 20, "medium": 10, "low": 5}.get(severity, 10)
                base_score -= penalty
            elif diff < 5000:
                # Imminent
                penalty = {"critical": 20, "high": 15, "medium": 8, "low": 3}.get(severity, 8)
                base_score -= penalty

    return max(0.0, min(100.0, base_score))


def compute_fiabilite_score(make: str, model: str, year: int) -> float:
    """
    Score de fiabilité basé sur la base de données.
    Bonus/malus selon modèle et année.
    """
    info = get_model_info(make, model)
    if not info:
        return 50.0

    base = float(info.get("base_reliability_score", 70))

    # Bonus années recommandées
    if year in info.get("best_years", []):
        base = min(100.0, base + 10)

    # Malus années à éviter
    if year in info.get("avoid_years", []):
        base = max(0.0, base - 20)

    # Malus class action
    if info.get("class_action"):
        base = max(0.0, base - 15)

    return base


def compute_annee_score(make: str, model: str, year: int) -> float:
    """Score basé sur l'année du véhicule."""
    info = get_model_info(make, model)

    # Score de base selon l'âge (2025 = référence)
    age = 2025 - year
    if age <= 3:
        base = 100.0
    elif age <= 6:
        base = 80.0
    elif age <= 9:
        base = 60.0
    elif age <= 12:
        base = 40.0
    else:
        base = max(0.0, 40.0 - (age - 12) * 3)

    if info:
        if year in info.get("best_years", []):
            base = min(100.0, base + 15)
        if year in info.get("avoid_years", []):
            base = max(0.0, base - 25)

    return base


def compute_score(
    make: str,
    model: str,
    year: int,
    km: int,
    price: float,
    median_price: float,
) -> dict:
    """
    Calcule le score global "bon achat" pour une annonce.
    Retourne le score (0-100) et le détail des composantes.
    """
    prix_score = compute_prix_score(price, median_price)
    km_score = compute_km_score(make, model, km)
    fiabilite_score = compute_fiabilite_score(make, model, year)
    annee_score = compute_annee_score(make, model, year)

    # Pondération
    global_score = (
        prix_score * 0.30
        + km_score * 0.25
        + fiabilite_score * 0.30
        + annee_score * 0.15
    )
    global_score = round(global_score, 1)

    # Catégorie
    if global_score >= 75:
        category = "Excellente affaire"
        badge_color = "green"
    elif global_score >= 55:
        category = "Bonne affaire"
        badge_color = "lightgreen"
    elif global_score >= 40:
        category = "Prix marché"
        badge_color = "orange"
    else:
        category = "À éviter"
        badge_color = "red"

    # Alertes
    alerts = get_danger_alerts(make, model, km)

    # Alertes supplémentaires prix
    if median_price > 0:
        ratio = (price - median_price) / median_price
        if ratio <= -0.15:
            alerts.insert(0, {
                "type": "bonus",
                "message": f"🟢 PRIX SOUS LE MARCHÉ : {abs(ratio)*100:.0f}% sous la médiane",
                "cost": 0,
                "severity": "bonus",
                "km_threshold": None,
            })
        elif ratio >= 0.20:
            alerts.append({
                "type": "warning",
                "message": f"🔴 PRIX ÉLEVÉ : {ratio*100:.0f}% au-dessus de la médiane",
                "cost": 0,
                "severity": "high",
                "km_threshold": None,
            })

    # Alertes années recommandées
    info = get_model_info(make, model)
    if info:
        if year in info.get("best_years", []):
            alerts.insert(0, {
                "type": "bonus",
                "message": f"🟢 ANNÉE RECOMMANDÉE ({year})",
                "cost": 0,
                "severity": "bonus",
                "km_threshold": None,
            })
        if year in info.get("avoid_years", []):
            alerts.append({
                "type": "critical",
                "message": f"🔴 ANNÉE À ÉVITER ({year}) — problèmes connus",
                "cost": 0,
                "severity": "critical",
                "km_threshold": None,
            })

    return {
        "global_score": global_score,
        "category": category,
        "badge_color": badge_color,
        "prix_score": round(prix_score, 1),
        "km_score": round(km_score, 1),
        "fiabilite_score": round(fiabilite_score, 1),
        "annee_score": round(annee_score, 1),
        "alerts": alerts,
    }


def estimate_total_cost(
    make: str,
    model: str,
    year: int,
    km: int,
    price: float,
    years: int = 5,
) -> dict:
    """
    Estime le coût total de possession sur N années.
    """
    info = get_model_info(make, model)

    # Entretiens annuels
    annual_service = 550.0
    if info:
        annual_service = float(info.get("avg_annual_service_cost_aud", 550))
    total_service = annual_service * years

    # Réparations probables selon danger zones
    total_repairs = 0.0
    if info:
        for zone in info.get("danger_zones", []):
            threshold = zone["km_threshold"]
            km_projected = km + (15000 * years)  # ~15k km/an
            if km < threshold <= km_projected:
                # Réparation probable dans la période
                total_repairs += zone["repair_cost_aud"]

    # Valeur de revente
    depreciation = 0.50
    if info:
        depreciation = float(info.get("depreciation_5yr_pct", 0.50))
    # Ajuster pour les années déjà écoulées
    age = 2025 - year
    remaining_depreciation = max(0.05, depreciation - age * 0.05)
    resale_value = price * (1 - remaining_depreciation)

    total_cost = price + total_service + total_repairs - resale_value

    return {
        "purchase_price": price,
        "total_service": total_service,
        "total_repairs": total_repairs,
        "resale_value": round(resale_value, 0),
        "net_total_cost": round(total_cost, 0),
        "annual_cost": round(total_cost / years, 0),
    }


def add_scores_to_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute les colonnes de score à un DataFrame d'annonces."""
    if df.empty:
        return df

    # Calcul du prix médian par modèle/année pour le benchmark
    df = df.copy()

    # Médiane par make+model+year
    median_prices = (
        df.groupby(["make", "model", "year"])["price"]
        .median()
        .reset_index()
        .rename(columns={"price": "median_price"})
    )
    df = df.merge(median_prices, on=["make", "model", "year"], how="left")

    scores = []
    for _, row in df.iterrows():
        result = compute_score(
            make=str(row.get("make", "")),
            model=str(row.get("model", "")),
            year=int(row.get("year", 2015)),
            km=int(row.get("km", 100000)),
            price=float(row.get("price", 0)),
            median_price=float(row.get("median_price", row.get("price", 0))),
        )
        scores.append(result)

    df["score"] = [s["global_score"] for s in scores]
    df["score_category"] = [s["category"] for s in scores]
    df["score_color"] = [s["badge_color"] for s in scores]
    df["alerts_count"] = [len(s["alerts"]) for s in scores]
    df["alerts_detail"] = [
        " | ".join([a["message"] for a in s["alerts"]]) for s in scores
    ]
    df["prix_score"] = [s["prix_score"] for s in scores]
    df["km_score"] = [s["km_score"] for s in scores]
    df["fiabilite_score"] = [s["fiabilite_score"] for s in scores]
    df["annee_score"] = [s["annee_score"] for s in scores]

    return df


if __name__ == "__main__":
    # Test : Toyota Corolla 2015, 120k km, $12,000 (médiane $13,500)
    print("=== Test Toyota Corolla 2015, 120k km, $12,000 ===")
    result = compute_score("Toyota", "Corolla", 2015, 120000, 12000, 13500)
    print(f"  Score global : {result['global_score']}/100 ({result['category']})")
    print(f"  Prix: {result['prix_score']}, KM: {result['km_score']}, "
          f"Fiabilité: {result['fiabilite_score']}, Année: {result['annee_score']}")
    print(f"  Alertes : {len(result['alerts'])}")
    for a in result["alerts"]:
        print(f"    {a['message']}")

    print("\n=== Coût total de possession (5 ans) ===")
    tco = estimate_total_cost("Toyota", "Corolla", 2015, 120000, 12000)
    print(f"  Achat: ${tco['purchase_price']:,.0f}")
    print(f"  Entretiens: ${tco['total_service']:,.0f}")
    print(f"  Réparations: ${tco['total_repairs']:,.0f}")
    print(f"  Revente: -${tco['resale_value']:,.0f}")
    print(f"  TOTAL NET: ${tco['net_total_cost']:,.0f} (${tco['annual_cost']:,.0f}/an)")
