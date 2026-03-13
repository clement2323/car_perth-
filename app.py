"""
Dashboard Streamlit — Achat voiture d'occasion Perth WA
4 onglets : Marché global | Score & Bonnes affaires | Capital Motors | Coût total
"""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from scoring import add_scores_to_dataframe, compute_score, estimate_total_cost
from reliability import RELIABILITY_DB, get_model_info

DATA_DIR = Path(__file__).parent / "data"
CARSALES_CSV = DATA_DIR / "carsales_listings.csv"
CAPITAL_CSV = DATA_DIR / "capital_motors_listings.csv"

st.set_page_config(
    page_title="Achat Voiture Perth WA",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS custom ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
.score-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 14px;
    color: white;
}
.score-green { background-color: #2ecc71; }
.score-lightgreen { background-color: #27ae60; }
.score-orange { background-color: #e67e22; }
.score-red { background-color: #e74c3c; }
.alert-critical { color: #e74c3c; font-weight: bold; }
.alert-warning { color: #e67e22; }
.alert-bonus { color: #2ecc71; }
</style>
""", unsafe_allow_html=True)


# ─── Chargement des données ────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Charge les données CSV et calcule les scores."""

    def read_csv(path: Path) -> pd.DataFrame:
        if not path.exists():
            return pd.DataFrame()
        df = pd.read_csv(path)
        for col in ["year", "km", "price"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["price"])
        df = df[df["price"] > 1000]
        return df

    df_cars = read_csv(CARSALES_CSV)
    df_cap = read_csv(CAPITAL_CSV)

    if not df_cars.empty:
        df_cars = add_scores_to_dataframe(df_cars)
    if not df_cap.empty:
        # Enrichir Capital Motors avec médiane carsales
        if not df_cars.empty:
            medians = (
                df_cars.groupby(["make", "model", "year"])["price"]
                .median()
                .reset_index()
                .rename(columns={"price": "median_price"})
            )
            df_cap = df_cap.merge(medians, on=["make", "model", "year"], how="left")
            df_cap["median_price"] = df_cap["median_price"].fillna(df_cap["price"])
        else:
            df_cap["median_price"] = df_cap["price"]
        df_cap = add_scores_to_dataframe(df_cap)

    return df_cars, df_cap


def refresh_data():
    """Relance les scrapers."""
    import subprocess
    with st.spinner("Scraping carsales.com.au..."):
        subprocess.run(["python", "scraper_carsales.py", "--sample"], check=False)
    with st.spinner("Scraping Capital Motors WA..."):
        subprocess.run(["python", "scraper_capital_motors.py", "--sample"], check=False)
    st.cache_data.clear()
    st.rerun()


# ─── Sidebar ───────────────────────────────────────────────────────────────────
def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.title("🔧 Filtres")

    if st.sidebar.button("🔄 Actualiser les données", use_container_width=True):
        refresh_data()

    if df.empty:
        return df

    # Budget
    max_budget = int(df["price"].max()) if not df.empty else 15000
    budget = st.sidebar.slider(
        "Budget max ($AUD)",
        min_value=5000,
        max_value=max(max_budget, 15000),
        value=15000,
        step=500,
        format="$%d",
    )

    # Kilométrage
    max_km = int(df["km"].max()) if "km" in df.columns and not df["km"].isna().all() else 200000
    km_max = st.sidebar.slider(
        "Kilométrage max",
        min_value=0,
        max_value=max(max_km, 200000),
        value=180000,
        step=5000,
        format="%d km",
    )

    # Modèles
    if "make" in df.columns and "model" in df.columns:
        df["make_model"] = df["make"].astype(str) + " " + df["model"].astype(str)
        all_models = sorted(df["make_model"].dropna().unique().tolist())
        selected_models = st.sidebar.multiselect(
            "Modèles",
            options=all_models,
            default=all_models,
        )
    else:
        selected_models = []

    # Type vendeur
    if "seller_type" in df.columns:
        seller_types = st.sidebar.multiselect(
            "Type vendeur",
            options=["dealer", "private"],
            default=["dealer", "private"],
            format_func=lambda x: "Concessionnaire" if x == "dealer" else "Particulier",
        )
    else:
        seller_types = ["dealer", "private"]

    # Appliquer les filtres
    mask = df["price"] <= budget
    if "km" in df.columns:
        mask &= (df["km"].isna() | (df["km"] <= km_max))
    if selected_models and "make_model" in df.columns:
        mask &= df["make_model"].isin(selected_models)
    if "seller_type" in df.columns:
        mask &= df["seller_type"].isin(seller_types)

    return df[mask]


# ─── Onglet 1 : Marché global ──────────────────────────────────────────────────
def tab_marche(df: pd.DataFrame):
    st.header("📊 Marché global — Perth WA")

    if df.empty:
        st.warning("Aucune donnée disponible. Cliquez sur 'Actualiser les données' dans la sidebar.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Annonces totales", len(df))
    col2.metric("Prix médian", f"${df['price'].median():,.0f}")
    col3.metric("Prix min", f"${df['price'].min():,.0f}")
    col4.metric("Prix max", f"${df['price'].max():,.0f}")

    st.divider()

    # Scatter Prix vs KM
    df_plot = df.dropna(subset=["km", "price"])
    if not df_plot.empty:
        df_plot["make_model"] = df_plot["make"].astype(str) + " " + df_plot["model"].astype(str)
        df_plot["hover_text"] = (
            df_plot["year"].astype(str) + " " +
            df_plot["make_model"] + "<br>" +
            df_plot["km"].apply(lambda x: f"{x:,.0f} km") + "<br>" +
            df_plot["price"].apply(lambda x: f"${x:,.0f}")
        )

        fig = px.scatter(
            df_plot,
            x="km",
            y="price",
            color="make_model",
            hover_data={"km": True, "price": True, "year": True, "make_model": True},
            hover_name="hover_text",
            trendline="lowess",
            trendline_scope="overall",
            title="Prix vs Kilométrage par modèle",
            labels={"km": "Kilométrage", "price": "Prix ($AUD)", "make_model": "Modèle"},
        )
        fig.update_traces(marker=dict(size=10, opacity=0.7))
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    # Tableau récapitulatif par modèle/année
    st.subheader("Récapitulatif par modèle")
    summary = (
        df.groupby(["make", "model", "year"])
        .agg(
            count=("price", "count"),
            prix_median=("price", "median"),
            prix_min=("price", "min"),
            prix_max=("price", "max"),
            km_median=("km", "median"),
        )
        .reset_index()
        .sort_values(["make", "model", "year"])
    )
    summary["prix_median"] = summary["prix_median"].apply(lambda x: f"${x:,.0f}")
    summary["prix_min"] = summary["prix_min"].apply(lambda x: f"${x:,.0f}")
    summary["prix_max"] = summary["prix_max"].apply(lambda x: f"${x:,.0f}")
    summary["km_median"] = summary["km_median"].apply(
        lambda x: f"{x:,.0f} km" if pd.notna(x) else "N/A"
    )
    st.dataframe(summary, use_container_width=True, hide_index=True)


# ─── Onglet 2 : Score & Bonnes affaires ───────────────────────────────────────
def tab_scores(df: pd.DataFrame):
    st.header("⭐ Score & Bonnes affaires")

    if df.empty or "score" not in df.columns:
        st.warning("Données non disponibles.")
        return

    # Tri par score décroissant
    df_sorted = df.sort_values("score", ascending=False).reset_index(drop=True)

    # Filtres rapides
    col1, col2 = st.columns(2)
    min_score = col1.slider("Score minimum", 0, 100, 40)
    only_alerts = col2.checkbox("Afficher uniquement avec alertes critiques", value=False)

    df_filtered = df_sorted[df_sorted["score"] >= min_score]
    if only_alerts and "alerts_detail" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["alerts_detail"].str.contains("🔴", na=False)]

    st.write(f"**{len(df_filtered)} annonces affichées**")

    # Affichage avec badges
    for _, row in df_filtered.iterrows():
        score = row.get("score", 0)
        color = row.get("score_color", "orange")
        category = row.get("score_category", "")

        css_class = f"score-{color}" if color in ["green", "lightgreen", "orange", "red"] else "score-orange"

        make = row.get("make", "")
        model = row.get("model", "")
        year = row.get("year", "")
        km = row.get("km", "")
        price = row.get("price", 0)
        url = row.get("listing_url", "")
        alerts = row.get("alerts_detail", "")
        seller = row.get("seller_type", "")
        dealer = row.get("dealer_name", "")

        km_str = f"{km:,.0f} km" if isinstance(km, (int, float)) and pd.notna(km) else "N/A"

        with st.container():
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            with c1:
                st.markdown(
                    f"**{year} {make} {model}** — {km_str} — "
                    f"<span class='score-badge {css_class}'>{score:.0f}/100 {category}</span>",
                    unsafe_allow_html=True,
                )
                if alerts:
                    for alert in alerts.split(" | "):
                        if alert.strip():
                            st.caption(alert.strip())
            with c2:
                st.metric("Prix", f"${price:,.0f}")
            with c3:
                seller_label = "Concessionnaire" if seller == "dealer" else "Particulier"
                st.caption(f"📍 {seller_label}")
                if dealer:
                    st.caption(dealer)
            with c4:
                if url:
                    st.link_button("Voir l'annonce", url)
            st.divider()


# ─── Onglet 3 : Capital Motors vs Marché ──────────────────────────────────────
def tab_capital_motors(df_cars: pd.DataFrame, df_cap: pd.DataFrame):
    st.header("🏪 Capital Motors WA vs Marché")

    if df_cap.empty:
        st.warning("Aucune donnée Capital Motors. Cliquez sur 'Actualiser les données'.")
        return

    # Métriques Capital Motors
    col1, col2, col3 = st.columns(3)
    col1.metric("Véhicules en stock", len(df_cap))
    col2.metric("Prix médian stock", f"${df_cap['price'].median():,.0f}")
    if "score" in df_cap.columns:
        col3.metric("Score moyen", f"{df_cap['score'].mean():.1f}/100")

    st.divider()

    # Comparaison prix Capital Motors vs médiane marché
    if not df_cars.empty and "median_price" in df_cap.columns:
        df_cap_plot = df_cap.dropna(subset=["price", "median_price"]).copy()
        df_cap_plot = df_cap_plot[df_cap_plot["median_price"] > 0]
        df_cap_plot["diff_pct"] = (
            (df_cap_plot["price"] - df_cap_plot["median_price"]) / df_cap_plot["median_price"] * 100
        )
        df_cap_plot["make_model_year"] = (
            df_cap_plot["year"].astype(str) + " " +
            df_cap_plot["make"].astype(str) + " " +
            df_cap_plot["model"].astype(str)
        )
        df_cap_plot["diff_label"] = df_cap_plot["diff_pct"].apply(
            lambda x: f"+{x:.1f}%" if x > 0 else f"{x:.1f}%"
        )
        df_cap_plot["color"] = df_cap_plot["diff_pct"].apply(
            lambda x: "Bonne affaire" if x < -10 else ("Dans la norme" if x < 10 else "Cher")
        )

        fig = px.bar(
            df_cap_plot.sort_values("diff_pct"),
            x="diff_pct",
            y="make_model_year",
            color="color",
            color_discrete_map={
                "Bonne affaire": "#2ecc71",
                "Dans la norme": "#f39c12",
                "Cher": "#e74c3c",
            },
            orientation="h",
            title="Capital Motors : écart prix vs médiane marché (%)",
            labels={"diff_pct": "Écart (%)", "make_model_year": "Véhicule"},
            text="diff_label",
        )
        fig.update_layout(height=max(400, len(df_cap_plot) * 30))
        st.plotly_chart(fig, use_container_width=True)

    # Tableau détaillé Capital Motors
    st.subheader("Inventaire Capital Motors WA")
    display_cols = ["year", "make", "model", "km", "price", "score", "score_category", "alerts_detail"]
    available_cols = [c for c in display_cols if c in df_cap.columns]
    df_display = df_cap[available_cols].copy()

    # Formatage
    if "km" in df_display.columns:
        df_display["km"] = df_display["km"].apply(
            lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) and pd.notna(x) else "N/A"
        )
    if "price" in df_display.columns:
        df_display["price"] = df_display["price"].apply(lambda x: f"${x:,.0f}")

    st.dataframe(
        df_display.sort_values("score", ascending=False) if "score" in df_display.columns else df_display,
        use_container_width=True,
        hide_index=True,
    )


# ─── Onglet 4 : Coût total de possession ──────────────────────────────────────
def tab_tco(df: pd.DataFrame):
    st.header("💰 Coût total de possession (5 ans)")

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.subheader("Analyser une annonce")

        mode = st.radio("Mode", ["Annonce spécifique", "Modèle générique"])

        if mode == "Annonce spécifique" and not df.empty:
            # Sélection d'une annonce
            if "make" in df.columns and "model" in df.columns:
                df["label"] = (
                    df["year"].astype(str) + " " +
                    df["make"].astype(str) + " " +
                    df["model"].astype(str) + " — " +
                    df["km"].apply(lambda x: f"{x:,.0f} km" if pd.notna(x) else "N/A") + " — " +
                    df["price"].apply(lambda x: f"${x:,.0f}")
                )
                selected_label = st.selectbox("Choisir une annonce", df["label"].tolist())
                selected_row = df[df["label"] == selected_label].iloc[0]
                make = str(selected_row["make"])
                model = str(selected_row["model"])
                year = int(selected_row.get("year", 2015))
                km = int(selected_row.get("km", 100000)) if pd.notna(selected_row.get("km")) else 100000
                price = float(selected_row["price"])
            else:
                st.warning("Données insuffisantes.")
                return
        else:
            # Modèle générique
            model_options = list(RELIABILITY_DB.keys())
            selected_model_key = st.selectbox("Modèle", model_options)
            parts = selected_model_key.split(" ", 1)
            make = parts[0]
            model = parts[1] if len(parts) > 1 else parts[0]
            year = st.number_input("Année", min_value=2008, max_value=2023, value=2015)
            km = st.number_input("Kilométrage", min_value=0, max_value=300000, value=100000, step=5000)
            price = st.number_input("Prix d'achat ($AUD)", min_value=1000, max_value=50000, value=12000, step=500)

        years_horizon = st.slider("Horizon (années)", 1, 10, 5)

    tco = estimate_total_cost(make, model, year, km, price, years_horizon)
    score_result = compute_score(make, model, year, km, price, price)

    with col_right:
        st.subheader(f"Analyse : {year} {make} {model}")

        # Métriques clés
        c1, c2, c3 = st.columns(3)
        c1.metric("Score achat", f"{score_result['global_score']:.0f}/100")
        c2.metric("Coût net total", f"${tco['net_total_cost']:,.0f}")
        c3.metric("Coût annuel", f"${tco['annual_cost']:,.0f}/an")

        # Breakdown graphique
        breakdown = {
            "Prix d'achat": tco["purchase_price"],
            f"Entretiens ({years_horizon} ans)": tco["total_service"],
            "Réparations estimées": tco["total_repairs"],
        }

        fig_breakdown = go.Figure(go.Bar(
            x=list(breakdown.keys()),
            y=list(breakdown.values()),
            marker_color=["#3498db", "#f39c12", "#e74c3c"],
            text=[f"${v:,.0f}" for v in breakdown.values()],
            textposition="auto",
        ))
        fig_breakdown.add_hline(
            y=tco["resale_value"],
            line_dash="dash",
            line_color="green",
            annotation_text=f"Valeur revente estimée : ${tco['resale_value']:,.0f}",
        )
        fig_breakdown.update_layout(
            title="Décomposition du coût total",
            yaxis_title="Montant ($AUD)",
            height=350,
        )
        st.plotly_chart(fig_breakdown, use_container_width=True)

        # Alertes
        if score_result["alerts"]:
            st.subheader("Alertes")
            for alert in score_result["alerts"]:
                msg = alert["message"]
                if "🔴" in msg:
                    st.error(msg)
                elif "🟡" in msg:
                    st.warning(msg)
                elif "🟢" in msg:
                    st.success(msg)
                else:
                    st.info(msg)

    # Comparaison multi-modèles
    st.divider()
    st.subheader("Comparaison 4 modèles (coût total estimé)")

    compare_models = [
        ("Toyota", "Corolla", 2015, 100000, 12000),
        ("Mazda", "3", 2015, 100000, 12000),
        ("Honda", "Jazz", 2014, 90000, 10500),
        ("Hyundai", "i30", 2015, 85000, 11000),
    ]

    tco_data = []
    for m_make, m_model, m_year, m_km, m_price in compare_models:
        t = estimate_total_cost(m_make, m_model, m_year, m_km, m_price, years_horizon)
        tco_data.append({
            "Modèle": f"{m_year} {m_make} {m_model}",
            "Prix achat": t["purchase_price"],
            "Entretiens": t["total_service"],
            "Réparations": t["total_repairs"],
            "Revente (-)": -t["resale_value"],
            "Total net": t["net_total_cost"],
        })

    df_compare = pd.DataFrame(tco_data)

    fig_compare = px.bar(
        df_compare.melt(
            id_vars="Modèle",
            value_vars=["Prix achat", "Entretiens", "Réparations"],
            var_name="Catégorie",
            value_name="Montant",
        ),
        x="Modèle",
        y="Montant",
        color="Catégorie",
        barmode="stack",
        title=f"Coût total comparé sur {years_horizon} ans",
        labels={"Montant": "$AUD"},
        color_discrete_map={
            "Prix achat": "#3498db",
            "Entretiens": "#f39c12",
            "Réparations": "#e74c3c",
        },
        text_auto=".2s",
    )
    fig_compare.update_layout(height=400)
    st.plotly_chart(fig_compare, use_container_width=True)


# ─── Main ──────────────────────────────────────────────────────────────────────
def main():
    st.title("🚗 Dashboard Achat Voiture Perth WA")
    st.caption("Données : carsales.com.au + Capital Motors WA | Budget max $15,000")

    # Chargement données
    df_cars, df_cap = load_data()

    # Vérification données initiales
    if df_cars.empty and df_cap.empty:
        st.info("Aucune donnée trouvée. Génération des données d'exemple...")
        import subprocess
        subprocess.run(["python", "scraper_carsales.py", "--sample"], cwd=Path(__file__).parent, check=False)
        subprocess.run(["python", "scraper_capital_motors.py", "--sample"], cwd=Path(__file__).parent, check=False)
        st.cache_data.clear()
        st.rerun()

    # Filtres sidebar
    df_filtered = sidebar_filters(df_cars.copy() if not df_cars.empty else pd.DataFrame())

    # Onglets
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Marché global",
        "⭐ Score & Bonnes affaires",
        "🏪 Capital Motors WA",
        "💰 Coût total de possession",
    ])

    with tab1:
        tab_marche(df_filtered)

    with tab2:
        tab_scores(df_filtered)

    with tab3:
        tab_capital_motors(df_cars, df_cap)

    with tab4:
        tab_tco(df_filtered if not df_filtered.empty else df_cars)


if __name__ == "__main__":
    main()
