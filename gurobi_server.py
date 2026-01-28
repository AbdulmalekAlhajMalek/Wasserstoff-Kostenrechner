"""
Gurobi-Backend für die Wasserstoff-Simulation (Version 2).

- Optimierung auf stündlicher Auflösung (simulate_hourly_system mit df2/df2_sim).
- Alle kostenbeeinflussenden Parameter werden berücksichtigt (Wind, EL, H2/NH3-Speicher,
  RO, N2, HB, Water-Tank; cost_components_proxy; annual_h2_t, Lebensdauer, USD/EUR).
- Feste Mindestgrenzen (minimale Zahlen): P_el, H2-Tage, NH3-Schiffe, Water-Tank werden
  nicht unter feste Minima gesenkt, damit die angeforderte H2-Menge fürs Stahlwerk
  (z.B. 110 000 t/a) sicher erbracht werden kann. Diese Minima werden aus dem
  Code_Final-Raster abgeleitet und können durch User-Bounds nicht unterschritten werden.

Nutzung:
    pip install flask
    pip install gurobipy   # optional, mit gültiger Lizenz
    python gurobi_server.py
"""

from __future__ import annotations

import sys
import io

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from typing import Dict, Any, List, Tuple

from flask import Flask, request, jsonify

try:
    import gurobipy as gp
    from gurobipy import GRB
    HAS_GUROBI = True
except ImportError:
    HAS_GUROBI = False

try:
    import Code_Final as cf
    HAS_CODE_FINAL = True
except Exception:
    HAS_CODE_FINAL = False


app = Flask(__name__)


# Feste Mindestgrenzen: nicht unterschreiten, damit H2-Bedarf Stahlwerk erfüllt werden kann.
# Abgeleitet aus Code_Final-Raster (pel 1000+, h2_days 1+, nh3_ships 1+, water 500+).
MINIMUM_BOUNDS = {
    "pel_min": 1000.0,
    "h2_days_min": 1.0,
    "nh3_ships_min": 1.0,
    "water_tank_min": 500.0,
}


def get_hourly_profile(params: Dict[str, Any]):
    """Stuendliches Windprofil: df2 (1 Jahr) oder df2_sim (Mehrjahr), falls use_multiyear."""
    if not HAS_CODE_FINAL:
        return None
    df2_sim = getattr(cf, "df2_sim", None)
    if params.get("use_multiyear") and df2_sim is not None:
        return df2_sim
    return getattr(cf, "df2", None)


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return response


@app.route("/", methods=["GET"])
def index() -> Any:
    return (
        "<html><body>"
        "<h2>Gurobi-Server Wasserstoff-Simulation (v2)</h2>"
        "<p>Stuendliche Aufloesung, alle kostenrelevanten Parameter, feste Mindestgrenzen "
        "fuer H2-Bedarf Stahlwerk.</p>"
        "<p>POST <code>/optimize_gurobi</code> wird von der Weboberflaeche aufgerufen.</p>"
        "</body></html>",
        200,
        {"Content-Type": "text/html; charset=utf-8"},
    )


def evaluate_configuration(
    params: Dict[str, Any],
    decision: Dict[str, float],
    df_profile=None,
) -> Tuple[float, bool]:
    """
    Bewertet eine Konfiguration: Kosten pro kg H2 (EUR) und Machbarkeit (ships_failed == 0).

    Verwendet stündliche Simulation (simulate_hourly_system) und cost_components_proxy.
    Alle kostenbeeinflussenden Parameter (Wind, EL, H2/NH3-Speicher, RO, N2, HB, Water-Tank)
    fließen ueber Code_Final ein. Zusaetzlich: annual_h2_t, project_lifetime_years, usd_to_eur
    aus params.
    """
    s = float(decision["s"])
    pel = float(decision["pel"])
    h2_days = float(decision["h2_days"])
    nh3_ships = float(decision["nh3_ships"])
    water_tank = float(decision["water_tank"])

    if HAS_CODE_FINAL and df_profile is not None:
        try:
            annual_h2_t = float(
                params.get("annual_h2_t")
                or getattr(cf, "annual_h2_prod_t", 120800.0)
            )
            years = float(
                params.get("project_lifetime_years")
                or (cf.cost_params["general"]["project_lifetime_years"] if hasattr(cf, "cost_params") else 20)
            )
            usd_to_eur = float(params.get("usd_to_eur", 0.92))

            h2_storage_t_design = (annual_h2_t / 365.0) * h2_days

            best_cost = float("inf")
            best_tech = "AEL"
            any_feasible = False

            for tech in ("AEL", "PEM"):
                _, kpi = cf.simulate_hourly_system(
                    s=s,
                    p_el_mw=pel,
                    technology=tech,
                    h2_storage_t_max=h2_storage_t_design,
                    nh3_storage_ships=nh3_ships,
                    water_tank_m3_max=water_tank,
                    return_timeseries=False,
                    df_profile=df_profile,
                )

                ships_failed = int(kpi.get("ships_failed_count", 0))
                feasible = ships_failed == 0

                if ships_failed > 0:
                    trial_cost = 1e6 + 1e5 * ships_failed
                else:
                    any_feasible = True
                    nh3_storage_t = float(kpi.get("nh3_storage_max_t", 0.0))
                    (
                        _w,
                        *_o,
                        total_proxy,
                    ) = cf.cost_components_proxy(
                        s=s,
                        p_el_mw=pel,
                        nh3_storage_t=nh3_storage_t,
                        h2_storage_t_design=h2_storage_t_design,
                        water_tank_m3_design=water_tank,
                        technology=tech,
                    )
                    annual_h2_kg = annual_h2_t * 1000.0
                    denom = annual_h2_kg * years
                    if denom <= 0:
                        trial_cost = 1e6
                    else:
                        total_eur = float(total_proxy) * usd_to_eur
                        trial_cost = total_eur / denom

                if trial_cost < best_cost:
                    best_cost = trial_cost
                    best_tech = tech

            cost = float(max(best_cost, 0.1))
            return (cost, any_feasible and best_cost < 1e5)

        except Exception as exc:
            print("WARNUNG: evaluate_configuration (Code_Final) fehlgeschlagen:", str(exc))

    # Fallback: Heuristik
    base = float(params.get("base_cost_per_kg", 3.0))
    cost = base + 0.0008 * pel + 0.05 * h2_days + 0.15 * nh3_ships + 0.00001 * water_tank - 0.5 * (s - 1.0)
    return (max(cost, 0.1), True)


def evaluate_configuration_detailed(
    params: Dict[str, Any],
    decision: Dict[str, float],
    df_profile=None,
) -> Dict[str, Any]:
    """
    Wie evaluate_configuration(), aber mit zusätzlichen Details für Empfehlungen:
    - gewählte Technologie (AEL/PEM)
    - Komponenten-Kostenanteile in EUR/kg (Wind, Electrolysis, HB, N2, RO, WaterTank, H2-Storage, NH3-Storage)
    """
    result: Dict[str, Any] = {
        "feasible": False,
        "costPerKg": None,
        "technology": None,
        "componentsPerKg": {},
    }

    if not HAS_CODE_FINAL or df_profile is None:
        # Fallback: einfache Heuristik ohne Komponentenzerlegung
        cost, feasible = evaluate_configuration(params, decision, df_profile=None)
        result["feasible"] = bool(feasible)
        result["costPerKg"] = float(cost)
        return result

    s = float(decision["s"])
    pel = float(decision["pel"])
    h2_days = float(decision["h2_days"])
    nh3_ships = float(decision["nh3_ships"])
    water_tank = float(decision["water_tank"])

    try:
        annual_h2_t = float(
            params.get("annual_h2_t")
            or getattr(cf, "annual_h2_prod_t", 120800.0)
        )
        years = float(
            params.get("project_lifetime_years")
            or (cf.cost_params["general"]["project_lifetime_years"] if hasattr(cf, "cost_params") else 20)
        )
        usd_to_eur = float(params.get("usd_to_eur", 0.92))

        h2_storage_t_design = (annual_h2_t / 365.0) * h2_days

        best_cost = float("inf")
        best_tech = None
        best_kpi = None

        for tech in ("AEL", "PEM"):
            _, kpi = cf.simulate_hourly_system(
                s=s,
                p_el_mw=pel,
                technology=tech,
                h2_storage_t_max=h2_storage_t_design,
                nh3_storage_ships=nh3_ships,
                water_tank_m3_max=water_tank,
                return_timeseries=False,
                df_profile=df_profile,
            )

            ships_failed = int(kpi.get("ships_failed_count", 0))
            if ships_failed > 0:
                trial_cost = 1e6 + 1e5 * ships_failed
            else:
                nh3_storage_t = float(kpi.get("nh3_storage_max_t", 0.0))
                (
                    wind_total,
                    wind_capex,
                    wind_opex,
                    wind_dapex,
                    el_capex,
                    el_opex_total,
                    hb_capex,
                    hb_opex_total,
                    n2_capex,
                    n2_opex_total,
                    ro_capex,
                    ro_opex_total,
                    water_tank_capex,
                    water_tank_opex_total,
                    h2_capex,
                    h2_opex_total,
                    nh3_capex,
                    nh3_opex_total,
                    total_proxy,
                ) = cf.cost_components_proxy(
                    s=s,
                    p_el_mw=pel,
                    nh3_storage_t=nh3_storage_t,
                    h2_storage_t_design=h2_storage_t_design,
                    water_tank_m3_design=water_tank,
                    technology=tech,
                )

                annual_h2_kg = annual_h2_t * 1000.0
                denom = annual_h2_kg * years
                if denom <= 0:
                    trial_cost = 1e6
                else:
                    total_eur = float(total_proxy) * usd_to_eur
                    trial_cost = total_eur / denom

            if trial_cost < best_cost:
                best_cost = trial_cost
                best_tech = tech
                best_kpi = kpi

        if best_tech is None or best_cost >= 1e5:
            # keine sinnvolle, machbare Lösung gefunden
            result["feasible"] = False
            result["costPerKg"] = float(max(best_cost, 0.1))
            return result

        # Komponentenzerlegung für die beste Technologie erneut berechnen
        nh3_storage_t = float(best_kpi.get("nh3_storage_max_t", 0.0)) if best_kpi is not None else 0.0
        (
            wind_total,
            wind_capex,
            wind_opex,
            wind_dapex,
            el_capex,
            el_opex_total,
            hb_capex,
            hb_opex_total,
            n2_capex,
            n2_opex_total,
            ro_capex,
            ro_opex_total,
            water_tank_capex,
            water_tank_opex_total,
            h2_capex,
            h2_opex_total,
            nh3_capex,
            nh3_opex_total,
            total_proxy,
        ) = cf.cost_components_proxy(
            s=s,
            p_el_mw=pel,
            nh3_storage_t=nh3_storage_t,
            h2_storage_t_design=h2_storage_t_design,
            water_tank_m3_design=water_tank,
            technology=best_tech,
        )

        annual_h2_kg = annual_h2_t * 1000.0
        denom = annual_h2_kg * years
        if denom <= 0:
            result["feasible"] = False
            result["costPerKg"] = float(1e6)
            return result

        total_eur = float(total_proxy) * usd_to_eur
        cost_per_kg = total_eur / denom

        def comp_per_kg(total_usd: float) -> float:
            eur = float(total_usd) * usd_to_eur
            return float(eur / denom)

        components = {
            "wind": comp_per_kg(wind_total),
            "electrolysis": comp_per_kg(el_capex + el_opex_total),
            "haber_bosch": comp_per_kg(hb_capex + hb_opex_total),
            "n2": comp_per_kg(n2_capex + n2_opex_total),
            "ro": comp_per_kg(ro_capex + ro_opex_total),
            "water_tank": comp_per_kg(water_tank_capex + water_tank_opex_total),
            "h2_storage": comp_per_kg(h2_capex + h2_opex_total),
            "nh3_storage": comp_per_kg(nh3_capex + nh3_opex_total),
        }

        result["feasible"] = True
        result["costPerKg"] = float(max(cost_per_kg, 0.1))
        result["technology"] = str(best_tech)
        result["componentsPerKg"] = components
        return result

    except Exception as exc:
        print("WARNUNG: evaluate_configuration_detailed fehlgeschlagen:", str(exc))
        cost, feasible = evaluate_configuration(params, decision, df_profile=None)
        result["feasible"] = bool(feasible)
        result["costPerKg"] = float(cost)
        return result

def compute_minimum_bounds(params: Dict[str, Any]) -> Dict[str, float]:
    """
    Feste Mindestgrenzen fuer das Suchgitter. Unterschreiten nicht erlaubt, damit
    die angeforderte H2-Menge fuer das Stahlwerk (z.B. 110 000 t/a) erricht werden kann.
    """
    return dict(MINIMUM_BOUNDS)


def clamp_grid_bounds(
    user_bounds: Dict[str, Any],
    minimum_bounds: Dict[str, float],
    defaults: Dict[str, float],
) -> Dict[str, float]:
    """
    Grid-Bounds aus User-Input, aber Minima werden auf die festen Mindestgrenzen
    angehoben (niemals darunter).
    """
    def b(key: str, default: float) -> float:
        return float(user_bounds.get(key, default))

    pel_min = max(b("pel_min", defaults["pel_min"]), minimum_bounds["pel_min"])
    h2_min = max(b("h2_min", defaults["h2_min"]), minimum_bounds["h2_days_min"])
    nh3_min = max(b("nh3_min", defaults["nh3_min"]), minimum_bounds["nh3_ships_min"])
    water_min = max(b("water_min", defaults["water_min"]), minimum_bounds["water_tank_min"])

    return {
        "s_min": b("s_min", defaults["s_min"]),
        "s_max": b("s_max", defaults["s_max"]),
        "s_step": b("s_step", defaults["s_step"]),
        "pel_min": pel_min,
        "pel_max": max(b("pel_max", defaults["pel_max"]), pel_min),
        "pel_step": b("pel_step", defaults["pel_step"]),
        "h2_min": h2_min,
        "h2_max": max(b("h2_max", defaults["h2_max"]), h2_min),
        "h2_step": b("h2_step", defaults["h2_step"]),
        "nh3_min": nh3_min,
        "nh3_max": max(b("nh3_max", defaults["nh3_max"]), nh3_min),
        "nh3_step": b("nh3_step", defaults["nh3_step"]),
        "water_min": water_min,
        "water_max": max(b("water_max", defaults["water_max"]), water_min),
        "water_step": b("water_step", defaults["water_step"]),
    }


def generate_candidate_grid(bounds: Dict[str, float]) -> List[Dict[str, float]]:
    """Gitter von Kandidaten (s, pel, h2_days, nh3_ships, water_tank)."""
    def frange(start, stop, step):
        x = start
        while x <= stop + 1e-9:
            yield x
            x += step

    out: List[Dict[str, float]] = []
    for s in frange(bounds["s_min"], bounds["s_max"], bounds["s_step"]):
        for pel in frange(bounds["pel_min"], bounds["pel_max"], bounds["pel_step"]):
            for h2 in frange(bounds["h2_min"], bounds["h2_max"], bounds["h2_step"]):
                for nh3 in frange(bounds["nh3_min"], bounds["nh3_max"], bounds["nh3_step"]):
                    for wat in frange(bounds["water_min"], bounds["water_max"], bounds["water_step"]):
                        out.append({
                            "s": float(s),
                            "pel": float(pel),
                            "h2_days": float(h2),
                            "nh3_ships": float(nh3),
                            "water_tank": float(wat),
                        })
    return out


@app.route("/optimize_gurobi", methods=["OPTIONS"])
def optimize_gurobi_options() -> Any:
    return ("", 204)


@app.route("/optimize_gurobi", methods=["POST"])
def optimize_gurobi() -> Any:
    data = request.get_json(force=True) or {}
    bounds = data.get("bounds", {}) or {}
    params = data.get("params", {}) or {}

    try:
        defaults = {
            "s_min": 0.95,
            "s_max": 1.0,
            "s_step": 0.01,
            "pel_min": 1000.0,
            "pel_max": 2500.0,
            "pel_step": 100.0,
            "h2_min": 1.0,
            "h2_max": 7.0,
            "h2_step": 1.0,
            "nh3_min": 3.0,
            "nh3_max": 8.0,
            "nh3_step": 1.0,
            "water_min": 500.0,
            "water_max": 10000.0,
            "water_step": 2000.0,
        }

        minimum_bounds = compute_minimum_bounds(params)
        grid_bounds = clamp_grid_bounds(bounds, minimum_bounds, defaults)

        candidates = generate_candidate_grid(grid_bounds)
        if not candidates:
            return jsonify(
                success=False,
                message="Keine Kandidaten im Gitter (evtl. Min > Max nach Clamp).",
            ), 400

        df_profile = get_hourly_profile(params) if HAS_CODE_FINAL else None
        if HAS_CODE_FINAL and df_profile is None:
            df_profile = cf.df2

        n_hours = len(df_profile) if df_profile is not None else 0
        sim_note = f"Stuendliche Simulation, {n_hours} h" if n_hours else "keine Zeitreihe"

        costs: List[float] = []
        feasible_mask: List[bool] = []
        for c in candidates:
            cost, feasible = evaluate_configuration(params, c, df_profile)
            costs.append(cost)
            feasible_mask.append(feasible)

        feasible_indices = [i for i in range(len(candidates)) if feasible_mask[i]]
        if not feasible_indices:
            h2_demand = params.get("h2_steel_demand_t", 110000.0)
            return jsonify(
                success=False,
                message=(
                    f"Keine zulaessige Konfiguration. Der H2-Bedarf Stahlwerk "
                    f"({h2_demand:.0f} t/a) kann mit den gewaehlten Grenzen nicht erfuellt werden "
                    f"(z.B. Schiffsausfaelle). Minima sind fest: P_el>={minimum_bounds['pel_min']:.0f} MW, "
                    f"H2-Tage>={minimum_bounds['h2_days_min']:.0f}, NH3-Schiffe>={minimum_bounds['nh3_ships_min']:.1f}, "
                    f"Water>={minimum_bounds['water_tank_min']:.0f} m3."
                ),
            ), 400

        best_idx = min(feasible_indices, key=lambda i: costs[i])
        best = candidates[best_idx].copy()
        best_cost = float(costs[best_idx])

        annual_h2_kt = float(params.get("h2_production_kt", 120.799))
        annual_h2_t = annual_h2_kt * 1000.0
        h2_storage_t = (annual_h2_t / 365.0) * best["h2_days"]
        nh3_per_h2 = 17.0 / 3.0
        annual_nh3_t = annual_h2_t * nh3_per_h2
        nh3_storage_t = annual_nh3_t / 12.0 * best["nh3_ships"]

        # Detaillierte Bewertung der besten Konfiguration (inkl. Technologie & Komponenten)
        details = evaluate_configuration_detailed(params, best, df_profile=df_profile)
        tech = details.get("technology")
        comp_per_kg = details.get("componentsPerKg") or {}
        cost_per_kg_detail = details.get("costPerKg", best_cost)

        best["costPerKg"] = float(cost_per_kg_detail)
        best["h2Storage"] = h2_storage_t
        best["nh3Storage"] = nh3_storage_t
        if tech:
            best["technology"] = tech
        if comp_per_kg:
            best["componentsPerKg"] = comp_per_kg

        return jsonify(
            success=True,
            message=f"Optimierung erfolgreich (Grid, {sim_note}). Feste Minima eingehalten.",
            best=best,
        )

    except Exception as exc:
        err = str(exc).encode("utf-8", errors="replace").decode("utf-8")
        return jsonify(success=False, message=f"Fehler in /optimize_gurobi: {err}"), 500


@app.route("/gurobi_daily_profile", methods=["POST"])
def gurobi_daily_profile() -> Any:
    if not HAS_CODE_FINAL:
        return jsonify(
            success=False,
            message="Code_Final.py nicht verfuegbar – keine Zeitreihen-Auswertung.",
        ), 500

    data = request.get_json(force=True) or {}
    decision = (data.get("decision") or {}).copy()
    params = data.get("params") or {}

    try:
        s = float(decision.get("s"))
        pel = float(decision.get("pel"))
        h2_days = float(decision.get("h2_days"))
        nh3_ships = float(decision.get("nh3_ships"))
        water_tank = float(decision.get("water_tank"))
    except Exception:
        return jsonify(success=False, message="Ungueltige oder fehlende decision-Parameter."), 400

    try:
        annual_h2_t = float(
            params.get("annual_h2_t") or getattr(cf, "annual_h2_prod_t", 120800.0)
        )
        h2_storage_t_design = (annual_h2_t / 365.0) * h2_days
        df_profile = get_hourly_profile(params) or cf.df2

        out, _ = cf.simulate_hourly_system(
            s=s,
            p_el_mw=pel,
            technology="AEL",
            h2_storage_t_max=h2_storage_t_design,
            nh3_storage_ships=nh3_ships,
            water_tank_m3_max=water_tank,
            return_timeseries=True,
            df_profile=df_profile,
        )

        df = out.copy().resample("D").mean()
        days = []
        for idx, row in df.iterrows():
            days.append({
                "date": idx.strftime("%Y-%m-%d"),
                "day_index": len(days) + 1,
                "h2_t": float(row.get("h2_soc_kg", 0.0) / 1000.0),
                "nh3_t": float(row.get("nh3_soc_t", 0.0)),
                "water_m3": float(row.get("water_soc_m3", 0.0)),
                "p_wind_mw": float(row.get("p_wind_mw", 0.0)),
                "p_el_mw": float(row.get("p_el_mw", 0.0)),
            })

        return jsonify(success=True, technology="AEL", days=days)

    except Exception as exc:
        err = str(exc).encode("utf-8", errors="replace").decode("utf-8")
        return jsonify(success=False, message=f"Fehler in /gurobi_daily_profile: {err}"), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
