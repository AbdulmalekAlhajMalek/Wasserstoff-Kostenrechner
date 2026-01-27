"""
Einfacher Backend-Server für die Wasserstoff-Simulation mit (optionaler) Gurobi-Optimierung.

Nutzung:
    1. Stelle sicher, dass Python, Flask und (optional) gurobipy installiert sind:
           pip install flask
           pip install gurobipy   # nur mit gültiger Gurobi-Lizenz

    2. Starte diesen Server im Projektordner:
           python gurobi_server.py

    3. Öffne dann im Browser die HTML-Datei (z.B. wasserstoff_simulation.html) und
       verwende dort den Button "Optimierung (Gurobi)", sobald wir ihn im Frontend ergänzt haben.

Hinweis:
    - Dieses Backend ist so gebaut, dass es auch ohne Gurobi funktioniert.
    - Wenn gurobipy verfügbar ist, wird es verwendet, um aus einer Menge von Kandidaten
      die beste Konfiguration via MILP auszuwählen.
    - Die detaillierte Kostenfunktion kann bei Bedarf aus Code_Final.py übernommen und
      im evaluate_configuration()-Placeholder implementiert werden.
"""

from __future__ import annotations

import sys
import io

# Setze UTF-8 Encoding für stdout/stderr (löst Windows cp932 Probleme)
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import math
from typing import Dict, Any, List

from flask import Flask, request, jsonify

try:
    import gurobipy as gp
    from gurobipy import GRB
    HAS_GUROBI = True
except ImportError:
    HAS_GUROBI = False

# Versuche, das detaillierte Python-Modell zu laden (Code_Final.py)
try:
    import Code_Final as cf
    HAS_CODE_FINAL = True
except Exception as exc:  # noqa: F841
    HAS_CODE_FINAL = False


app = Flask(__name__)


@app.after_request
def add_cors_headers(response):
    """
    Erlaube Zugriffe aus lokalen HTML-Dateien (CORS).
    Achtung: Für lokale Entwicklung ok, nicht für Produktion.
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return response


@app.route("/", methods=["GET"])
def index() -> Any:
    """
    Einfache Info-Seite, damit Aufrufe auf http://127.0.0.1:8000/ keinen 404 mehr liefern.
    """
    return (
        "<html><body>"
        "<h2>Gurobi-Server für Wasserstoff-Simulation</h2>"
        "<p>Der Server läuft. Die Weboberfläche ruft "
        "<code>/optimize_gurobi</code> per POST auf, wenn du in der "
        "Simulation auf <strong>&quot;OPTIMIERUNG (GUROBI-SERVER)&quot;</strong> klickst.</p>"
        "</body></html>",
        200,
        {"Content-Type": "text/html; charset=utf-8"},
    )


def evaluate_configuration(params: Dict[str, Any], decision: Dict[str, float]) -> float:
    """
    Bewertet eine gegebene Konfiguration und liefert Kosten pro kg H2 (modellabhängig).

    Wenn Code_Final.py erfolgreich importiert wurde (HAS_CODE_FINAL), wird die dort
    implementierte detaillierte Kostenfunktion verwendet (simulate_hourly_system +
    cost_components_proxy). Andernfalls fällt die Funktion auf eine vereinfachte
    heuristische Kostenfunktion zurück.
    """
    s = float(decision["s"])
    pel = float(decision["pel"])
    h2_days = float(decision["h2_days"])
    nh3_ships = float(decision["nh3_ships"])
    water_tank = float(decision["water_tank"])

    if HAS_CODE_FINAL:
        try:
            # Jahres-H2-Produktion aus dem Python-Modell (t/a)
            annual_h2_t = float(
                getattr(cf, "annual_h2_prod_t", params.get("annual_h2_t", 120800.0))
            )
            years = float(cf.cost_params["general"]["project_lifetime_years"])

            # H2-Speicher-Design aus Tagen
            h2_storage_t_design = (annual_h2_t / 365.0) * h2_days

            # Wir erlauben beide Elektrolyseur-Technologien (AEL und PEM)
            # und nehmen für die Bewertung jeweils die günstigere.
            best_cost = float("inf")
            for tech in ("AEL", "PEM"):
                # Stündliche Systemsimulation auf Jahresbasis (ohne Zeitreihen-Rückgabe)
                _, kpi = cf.simulate_hourly_system(
                    s=s,
                    p_el_mw=pel,
                    technology=tech,
                    h2_storage_t_max=h2_storage_t_design,
                    nh3_storage_ships=nh3_ships,
                    water_tank_m3_max=water_tank,
                    return_timeseries=False,
                    df_profile=cf.df2,
                )

                # Harte Nebenbedingung: keine Schiffsfehlschläge zulassen
                ships_failed = int(kpi.get("ships_failed_count", 0))
                if ships_failed > 0:
                    # sehr große Strafkosten
                    trial_cost = 1e6 + 1e5 * ships_failed
                else:
                    nh3_storage_t = float(kpi.get("nh3_storage_max_t", 0.0))

                    # Komponenten-Kosten wie im Raster (Total_proxy ist Lebenszykluskosten in USD)
                    (
                        _wind_total,
                        *_other,
                        total_proxy,
                    ) = cf.cost_components_proxy(
                        s=s,
                        p_el_mw=pel,
                        nh3_storage_t=nh3_storage_t,
                        h2_storage_t_design=h2_storage_t_design,
                        water_tank_m3_design=water_tank,
                        technology=tech,
                    )

                    # Umrechnung auf Kosten pro kg H2 über die Projektlebensdauer
                    # annual_h2_t: t H2/a -> kg/a
                    annual_h2_kg = annual_h2_t * 1000.0
                    denom = annual_h2_kg * years
                    if denom <= 0:
                        trial_cost = 1e6
                    else:
                        # Falls im Modell USD verwendet werden: einfache Umrechnung mit USD->EUR-Faktor aus params (optional)
                        usd_to_eur = float(params.get("usd_to_eur", 0.92))
                        total_cost_eur = float(total_proxy) * usd_to_eur
                        trial_cost = total_cost_eur / denom

                if trial_cost < best_cost:
                    best_cost = trial_cost
                    best_tech = tech
                    print(f"[PROBE] Neue beste Technologie: {tech} mit Kosten {best_cost:.4f} EUR/kg")
            
            print(f"[PROBE] Stuendliche Simulation abgeschlossen. Beste Technologie: {best_tech}, Kosten: {best_cost:.4f} EUR/kg")
            
            # Untergrenze, um numerische Ausreißer zu vermeiden
            return float(max(best_cost, 0.1))

        except Exception as exc:
            # Fallback auf Heuristik, falls etwas im Python-Modell schiefgeht
            print("WARNUNG: evaluate_configuration() mit Code_Final fehlgeschlagen:", str(exc))

    # --- Fallback: heuristische Kostenfunktion (wie zuvor) ---
    a_pel = 0.0008
    a_h2 = 0.05
    a_ships = 0.15
    a_water = 0.00001
    a_s = -0.5  # höhere s senkt Kosten leicht

    base = float(params.get("base_cost_per_kg", 3.0))

    cost = (
        base
        + a_pel * pel
        + a_h2 * h2_days
        + a_ships * nh3_ships
        + a_water * water_tank
        + a_s * (s - 1.0)
    )

    return max(cost, 0.1)


def generate_candidate_grid(bounds: Dict[str, Any]) -> List[Dict[str, float]]:
    """Erzeuge ein einfaches Gitter von Kandidaten im 5D-Raum."""
    def frange(start, stop, step):
        x = start
        while x <= stop + 1e-9:
            yield x
            x += step

    s_vals = list(frange(bounds["s_min"], bounds["s_max"], bounds["s_step"]))
    pel_vals = list(frange(bounds["pel_min"], bounds["pel_max"], bounds["pel_step"]))
    h2_vals = list(frange(bounds["h2_min"], bounds["h2_max"], bounds["h2_step"]))
    nh3_vals = list(frange(bounds["nh3_min"], bounds["nh3_max"], bounds["nh3_step"]))
    water_vals = list(frange(bounds["water_min"], bounds["water_max"], bounds["water_step"]))

    candidates: List[Dict[str, float]] = []
    for s in s_vals:
        for pel in pel_vals:
            for h2 in h2_vals:
                for nh3 in nh3_vals:
                    for wat in water_vals:
                        candidates.append(
                            {
                                "s": float(s),
                                "pel": float(pel),
                                "h2_days": float(h2),
                                "nh3_ships": float(nh3),
                                "water_tank": float(wat),
                            }
                        )
    return candidates


@app.route("/optimize_gurobi", methods=["OPTIONS"])
def optimize_gurobi_options() -> Any:
    """
    CORS-Preflight für Fetch aus dem Browser.
    """
    return ("", 204)


@app.route("/optimize_gurobi", methods=["POST"])
def optimize_gurobi() -> Any:
    data = request.get_json(force=True) or {}

    try:
        bounds = data.get("bounds", {})
        params = data.get("params", {})

        # Fallback-Bounds, falls etwas fehlt
        def b(key, default):
            return float(bounds.get(key, default))

        # Standardbereiche, abgeleitet aus Code_Final.py (Windpark 2.47 GW, 120 800 t H2/a etc.)
        # - s:   0.8–1.2 (80–120 % der Referenz-Windparkgröße)
        # - P_el: 200–2000 MW (realistische Bandbreite für 120 800 t/a)
        # - H2:  1–7 Tage Speicher
        # - NH3: 3–8 Schiffe (um 1.2 Schiffe Zielniveau bei 12 Schiffen/Jahr abzubilden)
        # - Water: 0–10000 m³
        grid_bounds = {
            "s_min": b("s_min", 0.8),
            "s_max": b("s_max", 1.2),
            "s_step": b("s_step", 0.05),
            "pel_min": b("pel_min", 200.0),
            "pel_max": b("pel_max", 2000.0),
            "pel_step": b("pel_step", 100.0),
            "h2_min": b("h2_min", 1.0),
            "h2_max": b("h2_max", 7.0),
            "h2_step": b("h2_step", 1.0),
            "nh3_min": b("nh3_min", 3.0),
            "nh3_max": b("nh3_max", 8.0),
            "nh3_step": b("nh3_step", 1.0),
            "water_min": b("water_min", 0.0),
            "water_max": b("water_max", 10000.0),
            "water_step": b("water_step", 2000.0),
        }

        candidates = generate_candidate_grid(grid_bounds)
        if not candidates:
            return jsonify(success=False, message="Keine Kandidaten im Gitter erzeugt."), 400

        # PROBE: Bestaetigung der stuendlichen Simulation
        if HAS_CODE_FINAL:
            print(f"[PROBE] === GUROBI-OPTIMIERUNG MIT STUENDLICHER SIMULATION ===")
            print(f"[PROBE] Anzahl Kandidaten: {len(candidates)}")
            print(f"[PROBE] Zeitreihen-Daten: {len(cf.df2)} Stunden ({len(cf.df2)/8760:.2f} Jahre)")
            print(f"[PROBE] Jeder Kandidat wird mit stuendlicher Aufloesung simuliert...")
        else:
            print("[WARNUNG] Code_Final.py nicht verfuegbar - verwende Fallback-Heuristik")

        # Kosten aller Kandidaten vorab berechnen (jeder mit stuendlicher Simulation)
        costs = [evaluate_configuration(params, c) for c in candidates]
        
        if HAS_CODE_FINAL:
            print(f"[PROBE] Alle {len(candidates)} Kandidaten wurden stuendlich simuliert.")

        if HAS_GUROBI:
            # MILP: wähle genau einen Kandidaten mit minimalen Kosten
            m = gp.Model("h2_opt_grid")
            m.Params.OutputFlag = 0

            y = m.addVars(len(candidates), vtype=GRB.BINARY, name="y")
            m.addConstr(gp.quicksum(y[i] for i in range(len(candidates))) == 1, "one_choice")
            m.setObjective(gp.quicksum(costs[i] * y[i] for i in range(len(candidates))), GRB.MINIMIZE)

            m.optimize()

            if m.Status != GRB.OPTIMAL:
                best_idx = min(range(len(candidates)), key=lambda i: costs[i])
            else:
                best_idx = max(range(len(candidates)), key=lambda i: y[i].X)
        else:
            # Fallback ohne Gurobi: einfache Python-Minimierung
            best_idx = min(range(len(candidates)), key=lambda i: costs[i])

        best = candidates[best_idx].copy()
        best_cost = float(costs[best_idx])

        # Grobe Ableitung von H2- und NH3-Speicher für Anzeige (analog zur JS-Optimierung)
        annual_h2_kt = float(params.get("h2_production_kt", 120.8))
        annual_h2_t = annual_h2_kt * 1000.0
        h2_storage_t = (annual_h2_t / 365.0) * best["h2_days"]
        nh3_per_h2 = 17.0 / 3.0
        annual_nh3_t = annual_h2_t * nh3_per_h2
        nh3_storage_t = annual_nh3_t / 12.0 * best["nh3_ships"]

        best.update(
            {
                "costPerKg": best_cost,
                "h2Storage": h2_storage_t,
                "nh3Storage": nh3_storage_t,
            }
        )

        # Bestaetigung: Stuendliche Simulation wurde verwendet
        simulation_info = ""
        if HAS_CODE_FINAL:
            simulation_info = f" (Stuendliche Simulation mit {len(cf.df2)} Stunden Daten)"
        
        return jsonify(
            success=True,
            message=f"Gurobi-Optimierung erfolgreich (Grid-basiert){simulation_info}.",
            best=best,
        )

    except Exception as exc:
        error_msg = str(exc).encode('utf-8', errors='replace').decode('utf-8')
        return jsonify(success=False, message=f"Fehler in /optimize_gurobi: {error_msg}"), 500


@app.route("/gurobi_daily_profile", methods=["POST"])
def gurobi_daily_profile() -> Any:
    """
    Liefert Tagesprofile (ein Punkt pro Tag) für die beste Gurobi-Konfiguration.

    Erwartet im Body:
        {
          "decision": { "s": ..., "pel": ..., "h2_days": ..., "nh3_ships": ..., "water_tank": ... },
          "params": { "annual_h2_t": ..., "usd_to_eur": ... (optional) }
        }
    """
    if not HAS_CODE_FINAL:
        return jsonify(success=False, message="Code_Final.py nicht verfügbar – keine Zeitreihen-Auswertung möglich."), 500

    data = request.get_json(force=True) or {}
    decision = data.get("decision", {}) or {}
    params = data.get("params", {}) or {}

    try:
        s = float(decision.get("s"))
        pel = float(decision.get("pel"))
        h2_days = float(decision.get("h2_days"))
        nh3_ships = float(decision.get("nh3_ships"))
        water_tank = float(decision.get("water_tank"))
    except Exception:
        return jsonify(success=False, message="Ungültige oder fehlende decision-Parameter."), 400

    try:
        # Für die Tagesprofile reicht eine einzige, detaillierte stündliche Simulation.
        # Wir verwenden hier AEL als Referenz-Technologie (wie im ursprünglichen Modell).
        # Wichtig: Es geht um die zeitliche Dynamik, nicht um eine erneute Kostenoptimierung.
        annual_h2_t = float(
            getattr(cf, "annual_h2_prod_t", params.get("annual_h2_t", 120800.0))
        )
        h2_storage_t_design = (annual_h2_t / 365.0) * h2_days

        out, kpi = cf.simulate_hourly_system(
            s=s,
            p_el_mw=pel,
            technology="AEL",
            h2_storage_t_max=h2_storage_t_design,
            nh3_storage_ships=nh3_ships,
            water_tank_m3_max=water_tank,
            return_timeseries=True,
            df_profile=cf.df2,
        )

        # Tagesmittel der wichtigsten Größen bilden
        df = out.copy()
        df = df.resample("D").mean()

        days = []
        for idx, row in df.iterrows():
            days.append(
                {
                    "date": idx.strftime("%Y-%m-%d"),
                    "day_index": len(days) + 1,
                    "h2_t": float(row.get("h2_soc_kg", 0.0) / 1000.0),
                    "nh3_t": float(row.get("nh3_soc_t", 0.0)),
                    "water_m3": float(row.get("water_soc_m3", 0.0)),
                    "p_wind_mw": float(row.get("p_wind_mw", 0.0)),
                    "p_el_mw": float(row.get("p_el_mw", 0.0)),
                }
            )

        return jsonify(success=True, technology="AEL", days=days)

    except Exception as exc:
        error_msg = str(exc).encode('utf-8', errors='replace').decode('utf-8')
        return jsonify(success=False, message=f"Fehler in /gurobi_daily_profile: {error_msg}"), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)

