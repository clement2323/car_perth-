"""
Base de données de fiabilité par modèle de voiture.
Danger zones, années à éviter, coûts d'entretien estimés.
"""

RELIABILITY_DB = {
    "Toyota Corolla": {
        "best_years": list(range(2014, 2020)),
        "avoid_years": [],
        "timing_type": "chain",
        "km_belt_change": None,
        "class_action": False,
        "class_action_url": None,
        "base_reliability_score": 88,
        "avg_annual_service_cost_aud": 550,
        "depreciation_5yr_pct": 0.45,
        "danger_zones": [
            {
                "km_threshold": 150000,
                "issue": "Révision majeure moteur / joints",
                "severity": "medium",
                "repair_cost_aud": 800,
            },
            {
                "km_threshold": 100000,
                "issue": "Remplacement bougies, filtres, courroie accessoires",
                "severity": "low",
                "repair_cost_aud": 400,
            },
        ],
        "notes": "Très fiable. Chaîne de distribution, pas de courroie. Idéal pour fort kilométrage.",
    },
    "Mazda 3": {
        "best_years": [2014, 2015, 2016, 2017],
        "avoid_years": [2010, 2011],
        "timing_type": "chain",
        "km_belt_change": None,
        "class_action": False,
        "class_action_url": None,
        "base_reliability_score": 82,
        "avg_annual_service_cost_aud": 600,
        "depreciation_5yr_pct": 0.48,
        "danger_zones": [
            {
                "km_threshold": 120000,
                "issue": "Système d'injection directe Skyactiv : dépôts carbone",
                "severity": "medium",
                "repair_cost_aud": 600,
            },
            {
                "km_threshold": 160000,
                "issue": "Boîte automatique Skyactiv — vidange fluide critique",
                "severity": "medium",
                "repair_cost_aud": 400,
            },
        ],
        "notes": "Skyactiv G fiable. Surveiller dépôts carbone sur injection directe après 120k.",
    },
    "Honda Civic": {
        "best_years": [2012, 2013, 2015],
        "avoid_years": [2014],
        "timing_type": "chain",
        "km_belt_change": None,
        "class_action": False,
        "class_action_url": None,
        "base_reliability_score": 78,
        "avg_annual_service_cost_aud": 650,
        "depreciation_5yr_pct": 0.50,
        "danger_zones": [
            {
                "km_threshold": 100000,
                "issue": "Roulements de roue, suspension — usure précoce 9e génération",
                "severity": "medium",
                "repair_cost_aud": 700,
            },
            {
                "km_threshold": 130000,
                "issue": "Boîte CVT : surveiller le comportement, fluide à changer",
                "severity": "high",
                "repair_cost_aud": 2500,
            },
        ],
        "notes": "9e génération (2012-2015) moins bien notée que la 8e. CVT fragile.",
    },
    "Hyundai i30": {
        "best_years": [2015, 2016, 2017],
        "avoid_years": [2012, 2013],
        "timing_type": "belt",
        "km_belt_change": 90000,
        "class_action": True,
        "class_action_url": "https://www.accc.gov.au/consumers/product-safety/product-recalls",
        "base_reliability_score": 68,
        "avg_annual_service_cost_aud": 700,
        "depreciation_5yr_pct": 0.52,
        "danger_zones": [
            {
                "km_threshold": 90000,
                "issue": "Courroie de distribution — REMPLACEMENT OBLIGATOIRE",
                "severity": "critical",
                "repair_cost_aud": 1200,
            },
            {
                "km_threshold": 60000,
                "issue": "Pompe à eau souvent remplacée avec la courroie",
                "severity": "medium",
                "repair_cost_aud": 350,
            },
            {
                "km_threshold": 150000,
                "issue": "Moteur Theta II (2.0L) : risque grippage — class action",
                "severity": "critical",
                "repair_cost_aud": 5000,
            },
        ],
        "notes": "⚠️ Moteur Theta II concerné par class action en Australie. Vérifier l'historique d'entretien.",
    },
    "Honda Jazz": {
        "best_years": [2010, 2011, 2013, 2014],
        "avoid_years": [2009],
        "timing_type": "chain",
        "km_belt_change": None,
        "class_action": False,
        "class_action_url": None,
        "base_reliability_score": 84,
        "avg_annual_service_cost_aud": 480,
        "depreciation_5yr_pct": 0.42,
        "danger_zones": [
            {
                "km_threshold": 100000,
                "issue": "Boîte CVT Honda : point de vigilance, fluide à contrôler",
                "severity": "medium",
                "repair_cost_aud": 1800,
            },
            {
                "km_threshold": 80000,
                "issue": "Embrayage CVT — signes de glissement à surveiller",
                "severity": "medium",
                "repair_cost_aud": 1200,
            },
        ],
        "notes": "Très fiable, économique. Espace intérieur surprenant. CVT à surveiller.",
    },
    "Suzuki Swift": {
        "best_years": [2011, 2012, 2013, 2014, 2015],
        "avoid_years": [2010],
        "timing_type": "chain",
        "km_belt_change": None,
        "class_action": False,
        "class_action_url": None,
        "base_reliability_score": 80,
        "avg_annual_service_cost_aud": 420,
        "depreciation_5yr_pct": 0.50,
        "danger_zones": [
            {
                "km_threshold": 120000,
                "issue": "Roulements de roue arrière — usure courante",
                "severity": "low",
                "repair_cost_aud": 300,
            },
            {
                "km_threshold": 100000,
                "issue": "Bougie d'allumage et filtre air — révision importante",
                "severity": "low",
                "repair_cost_aud": 250,
            },
        ],
        "notes": "Très économique à l'entretien. Petit moteur robuste.",
    },
}


def get_model_info(make: str, model: str) -> dict | None:
    """Retourne les infos de fiabilité pour un modèle donné."""
    key = f"{make} {model}"
    # Recherche exacte
    if key in RELIABILITY_DB:
        return RELIABILITY_DB[key]
    # Recherche partielle
    for db_key in RELIABILITY_DB:
        if model.lower() in db_key.lower() or make.lower() in db_key.lower():
            return RELIABILITY_DB[db_key]
    return None


def get_danger_alerts(make: str, model: str, km: int) -> list[dict]:
    """Retourne les alertes de danger selon le kilométrage."""
    info = get_model_info(make, model)
    if not info:
        return []

    alerts = []
    for zone in info.get("danger_zones", []):
        threshold = zone["km_threshold"]
        diff = threshold - km
        if diff < 0:
            # Déjà dépassé
            alerts.append({
                "type": "critical" if zone["severity"] == "critical" else "warning",
                "message": f"⚠️ Seuil dépassé ({threshold:,} km) : {zone['issue']}",
                "cost": zone["repair_cost_aud"],
                "severity": zone["severity"],
                "km_threshold": threshold,
            })
        elif diff < 5000:
            # Moins de 5,000 km avant le seuil
            alerts.append({
                "type": "critical",
                "message": f"🔴 IMMINENT ({diff:,} km restants) : {zone['issue']}",
                "cost": zone["repair_cost_aud"],
                "severity": zone["severity"],
                "km_threshold": threshold,
            })
        elif diff < 15000:
            alerts.append({
                "type": "warning",
                "message": f"🟡 Proche ({diff:,} km) : {zone['issue']}",
                "cost": zone["repair_cost_aud"],
                "severity": zone["severity"],
                "km_threshold": threshold,
            })

    # Alerte class action
    if info.get("class_action"):
        alerts.append({
            "type": "warning",
            "message": "🟡 CLASS ACTION applicable sur ce modèle — vérifier éligibilité",
            "cost": 0,
            "severity": "medium",
            "km_threshold": None,
        })

    # Alerte courroie de distribution
    if info.get("timing_type") == "belt":
        belt_km = info.get("km_belt_change", 90000)
        if km > belt_km * 0.9:
            alerts.append({
                "type": "critical",
                "message": f"🔴 COURROIE DE DISTRIBUTION : remplacement requis tous les {belt_km:,} km",
                "cost": 1200,
                "severity": "critical",
                "km_threshold": belt_km,
            })

    return alerts


def get_all_models() -> list[str]:
    """Retourne la liste de tous les modèles dans la base."""
    return list(RELIABILITY_DB.keys())


if __name__ == "__main__":
    # Test
    print("=== Test Hyundai i30 à 85,000 km ===")
    alerts = get_danger_alerts("Hyundai", "i30", 85000)
    for a in alerts:
        print(f"  [{a['type'].upper()}] {a['message']} (coût estimé: ${a['cost']})")

    print("\n=== Test Toyota Corolla à 148,000 km ===")
    alerts = get_danger_alerts("Toyota", "Corolla", 148000)
    for a in alerts:
        print(f"  [{a['type'].upper()}] {a['message']} (coût estimé: ${a['cost']})")
