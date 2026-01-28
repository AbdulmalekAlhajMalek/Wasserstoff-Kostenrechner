# %%
# %%
# %% Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display

# %%
# -----------------------------
# Projektannahmen (Excel Wasserstoffberechnungen (3).xlsx)
# -----------------------------
ships_per_year = 12                 # Schiffe/Jahr
annual_h2_prod_t = 120799           # t H2/a (m_H2_el), Excel Wasserstoffbilanz

# Startbuffer in Schiffsladungen NH3 0, weil Projektstart
startup_buffer_ships = 0

# Regler für H2-SOC (Anteile bezogen auf H2 Designgröße)
h2_soc_low_frac  = 0.3   # darunter: EL priorisieren
h2_soc_high_frac = 0.60   # darüber: HB priorisieren
hb_min_frac_when_on = 0.40  # Mindestlast HB, wenn HB an ist (0.0 zum Debuggen)

# -----------------------------
# Dynamik / Rampen (realistischere Fahrweise)
# -----------------------------
el_ramp_frac_per_h = 0.80   # max 10% der EL-Nennleistung pro Stunde Änderung
hb_ramp_frac_per_h = 0.10   # 3%/h (realistisch eher konservativ)

# -----------------------------
# NH3-Regelung: Zielniveau 
# -----------------------------
nh3_target_level_ships = 1.2   # halte ~1.2 Schiffe im Tank
nh3_deadband_ships     = 1.1   # Hysterese (+- im Tank erlauben)

# H2-Level-Control: EL Stoppen bei bestimmten speicherständen
h2_el_stop_frac  = 0.95   # ab 95% H2-SOC: EL stoppen
h2_el_start_frac = 0.30   # unter 60%: EL wieder frei geben (Hysterese)

# -----------------------------
# Windparkgröße auslegung
# -----------------------------
p_wind_rated_mw = 2470       #2,47 GW



# %%
# %%
# -----------------------------
# Kostenparameter: Trotz der Namen der Variablen wurde alles in € angegeben, damit nicht ganzes Programm geändert werden musste.
# -----------------------------
cost_params = {
    "general": {
        "project_lifetime_years": 20,
    },

    "wind": {
    "capex_eur_per_mw": 2000000,        # €/MW
    "opex_eur_per_kw_per_year": 60.0,       # €/kW/a
    },


    "h2": {
        "electrolyzer": {
            "AEL": {
                "capex_usd_per_kw": 464.0,
                "opex_usd_per_kw_per_year": 40.6,
                "spec_kwh_per_kgH2": 48.0,
                "min_load_frac": 0.20,
            },
            "PEM": {
                "capex_usd_per_kw": 580.0,
                "opex_usd_per_kw_per_year": 24.36,
                "spec_kwh_per_kgH2": 48.0,
                "min_load_frac": 0.05,
            },
        },

        # -------- LH2 STORAGE (KRYOGEN) --------
        "storage": {
            "capex_usd_per_tH2": 33000.0,
            "opex_fraction_per_year": 0.03,

            "eta_in": 0.995,
            "eta_out": 0.995,

            # physikalischer Boil-off
            "loss_frac_per_hour": 0.0005 / 24,   # 0.05 % / Tag

            # Ein-/Ausspeichern
            "spec_kwh_per_kg_in": 11.0,         # Verflüssiger
            "spec_kwh_per_kg_out": 0.06,        # Regas

            
            "reliq_kwh_per_kg_bog": 11.0,       # Rückverflüssigung
            "reliq_frac": 1.0,                  # 100 % BOG reliquefy
        },
    },

    "haber_bosch": {
        "availability": 0.94,
        "capex_usd_per_tNH3_per_year": 491.4,
        "opex_usd_per_tNH3": 24.57,
        "spec_kwh_per_kgNH3": 0.55,
    },

    "n2": {
        "spec_kwh_per_kgN2": 0.33,          # Rueda et al. (~0.33 kWh/kg)
        "capex_usd_per_kgN2_per_h": 1700.0, # Rueda 1758 €/kgN2/h, Giampieri 1247 £/kgN2/h
        "opex_fraction_per_year": 0.03      # typische 2–4 %/a
    },


    # -------- NH3 STORAGE (ATMOSPHÄRISCH, GEKÜHLT) --------
    "nh3_storage": {
        "capex_usd_per_tNH3": 810.0,
        "opex_fraction_per_year": 0.02,

        "spec_kwh_per_t_in": 1.0,
        "spec_kwh_per_t_out": 1.0,

        "cooling_kwh_per_tNH3_per_day": 40.0,
    },

    # -------- WATER SYSTEM --------
    "water": {
        "ro": {
            "water_kg_per_kgH2": 10.0,
            "spec_kwh_per_m3": 4.0,
            "capex_usd_per_m3_per_day": 1500.0,
            "opex_fraction_per_year": 0.0,          #wird nicht mehr betrachtet
            "opex_usd_per_m3": 0.3825,
        },

        "tank": {
            "capex_usd_per_m3": 200.0,
            "opex_fraction_per_year": 0.02,
            "loss_frac_per_hour": 0.001,
        },
    },
}

assert "capex_eur_per_mw" in cost_params["wind"]
assert "opex_eur_per_kw_per_year" in cost_params["wind"]


# %%
# %% Excel einlesen
df = pd.read_excel("Wind Erzeugerprofil3.xlsx")

p_gw = df["Leistung  Windpark [GW]"].astype(float)
p_mw = (p_gw * 1000).clip(lower=0)

t = pd.to_datetime(df["datetime"])
df2 = pd.DataFrame({"t": t, "p_mw": p_mw}).set_index("t")

annual_wind_mwh_base = df2["p_mw"].sum()
print("Jahresenergie Windpark (s=1) [MWh]:", round(annual_wind_mwh_base, 1))
print("Zeitschritte:", len(df2))

# %% Derived assumptions
years = float(cost_params["general"]["project_lifetime_years"])
annual_nh3_prod_t = annual_h2_prod_t * 17.0 / 3.0

hb_avail = float(cost_params["haber_bosch"]["availability"])
hb_capacity_tNH3_per_year = annual_nh3_prod_t / hb_avail
hb_capacity_tNH3_per_day = hb_capacity_tNH3_per_year / 365.0

print("annual_nh3_prod_t [t/a]:", round(annual_nh3_prod_t, 1))
print("HB capacity [t NH3/day]:", round(hb_capacity_tNH3_per_day, 2))

# %%
# -----------------------------
# Mehrjahres-Windprofil erzeugen
# -----------------------------
def make_multi_year_profile(df_one_year: pd.DataFrame, years_sim: int = 2) -> pd.DataFrame:
    """
    Hängt ein 1-Jahres-Profil years_sim-mal hintereinander.
    Index wird pro Jahr um +1 Jahr verschoben.
    """
    blocks = []
    for i in range(years_sim):
        dfi = df_one_year.copy()
        dfi.index = dfi.index + pd.DateOffset(years=i)
        blocks.append(dfi)
    return pd.concat(blocks)

years_sim = 20            # Anzahl an Jahren, die simuliert werden
df2_sim = make_multi_year_profile(df2, years_sim=years_sim)

print("Sim hours:", len(df2_sim))
print("Sim start/end:", df2_sim.index.min(), "->", df2_sim.index.max())


# %%
def simulate_hourly_system(
    s: float,
    p_el_mw: float,
    technology: str,
    h2_storage_t_max: float,
    nh3_storage_ships: float = 3.0,
    water_tank_m3_max: float = 0.0,
    return_timeseries: bool = False,
    debug_ships: bool = False,
    df_profile: pd.DataFrame = None
):
    tech = technology.upper()

    if df_profile is None:
        df_profile = df2

    el = cost_params["h2"]["electrolyzer"][tech]
    h2s = cost_params["h2"]["storage"]
    hb  = cost_params["haber_bosch"]
    n2  = cost_params["n2"]
    nh3s = cost_params["nh3_storage"]

    # --- Kühlparameter ---
    h2_reliq_kwh_per_kg = float(h2s.get("reliq_kwh_per_kg_bog", 0.0))
    h2_reliq_frac = float(h2s.get("reliq_frac", 0.0))
    nh3_cooling_kwh_per_t_per_day = float(nh3s.get("cooling_kwh_per_tNH3_per_day", 0.0))

    # --- WATER / RO ---
    water = cost_params.get("water", {})
    rop = water.get("ro", {})
    tankp = water.get("tank", {})

    water_kg_per_kgH2 = float(rop.get("water_kg_per_kgH2", 9.0))
    ro_spec_kwh_per_m3 = float(rop.get("spec_kwh_per_m3", 4.0))
    water_loss_frac_per_hour = float(tankp.get("loss_frac_per_hour", 0.0))

    # --- EL ---
    spec_kwh_per_kgH2_el = float(el["spec_kwh_per_kgH2"])
    el_min_load_frac = float(el["min_load_frac"])

    # --- HB/N2 ---
    hb_spec_kwh_per_kgNH3 = float(hb["spec_kwh_per_kgNH3"])
    spec_kwh_per_kgN2 = float(n2["spec_kwh_per_kgN2"])

    # --- Speicher ---
    h2_storage_kg_max = float(h2_storage_t_max) * 1000.0
    eta_in = float(h2s.get("eta_in", 1.0))
    eta_out = float(h2s.get("eta_out", 1.0))
    loss_frac_per_hour = float(h2s.get("loss_frac_per_hour", 0.0))

    h2_spec_kwh_per_kg_in = float(h2s.get("spec_kwh_per_kg_in", 0.0))
    h2_spec_kwh_per_kg_out = float(h2s.get("spec_kwh_per_kg_out", 0.0))
    nh3_spec_kwh_per_t_in = float(nh3s.get("spec_kwh_per_t_in", 0.0))
    nh3_spec_kwh_per_t_out = float(nh3s.get("spec_kwh_per_t_out", 0.0))

    # Umrechnung
    h2_kg_per_mwh = 1000.0 / spec_kwh_per_kgH2_el

    # Stöchiometrie
    h2_kg_per_kg_nh3 = 6.0 / 34.0
    n2_kg_per_kg_nh3 = 28.0 / 34.0

    # HB Kapazität
    hb_capacity_tNH3_per_h = float(hb_capacity_tNH3_per_day) / 24.0

    # -------------------------
    # Schiffe + NH3 Speicher
    # -------------------------
    nh3_target_per_ship_t = float(annual_nh3_prod_t) / float(ships_per_year)
    nh3_storage_ships_eff = max(float(nh3_storage_ships), float(startup_buffer_ships) + 1.0)
    nh3_storage_t_max = nh3_storage_ships_eff * nh3_target_per_ship_t

    # NH3 Zielniveau + Deadband (wie vorher "gut")
    nh3_soc_target_t = float(nh3_target_level_ships) * nh3_target_per_ship_t
    nh3_soc_high_t   = float(nh3_target_level_ships + nh3_deadband_ships) * nh3_target_per_ship_t
    nh3_soc_low_t    = max(0.0, float(nh3_target_level_ships - nh3_deadband_ships) * nh3_target_per_ship_t)

    nh3_soc_target_t = min(nh3_soc_target_t, nh3_storage_t_max)
    nh3_soc_high_t   = min(nh3_soc_high_t, nh3_storage_t_max)
    nh3_soc_low_t    = min(nh3_soc_low_t, nh3_storage_t_max)

    ship_interval = 8760.0 / float(ships_per_year)
    next_ship_time = ship_interval

    # Target über gesamte Simulation
    sim_hours = float(len(df_profile))
    sim_years_est = sim_hours / 8760.0
    nh3_target_total_t = sim_years_est * float(annual_nh3_prod_t)

    # Regler-Grenzen
    p_el_max = float(p_el_mw)
    p_el_min = el_min_load_frac * p_el_max

    # H2-SOC Grenzen
    h2_soc_low_kg  = float(h2_soc_low_frac)  * h2_storage_kg_max
    h2_soc_high_kg = float(h2_soc_high_frac) * h2_storage_kg_max

    # H2-Level-Control für EL
    h2_el_stop_kg  = float(h2_el_stop_frac)  * h2_storage_kg_max
    h2_el_start_kg = float(h2_el_start_frac) * h2_storage_kg_max

    # States
    soc_h2_kg = 0.0
    soc_nh3_t = float(startup_buffer_ships) * nh3_target_per_ship_t
    soc_nh3_t = min(soc_nh3_t, nh3_storage_t_max)
    soc_water_m3 = 0.0

    el_allowed = True
    p_stack_prev = 0.0          # EL ramp state
    nh3_hb_prev_t = 0.0         # HB ramp state

    curtailed_mwh = 0.0
    ships_failed_count = 0

    h2_soc_max_kg = soc_h2_kg
    nh3_soc_max_t = soc_nh3_t
    water_soc_max_m3 = soc_water_m3

    # Energie-KPIs (MWh)
    el_energy_mwh_sum = 0.0
    hb_energy_mwh_sum = 0.0
    n2_energy_mwh_sum = 0.0
    h2_store_in_mwh_sum = 0.0
    h2_store_out_mwh_sum = 0.0
    nh3_store_in_mwh_sum = 0.0
    nh3_store_out_mwh_sum = 0.0
    ro_energy_mwh_sum = 0.0

    # Kühlung
    h2_reliq_mwh_sum = 0.0
    nh3_cooling_mwh_sum = 0.0

    # Debug / Balance
    nh3_prod_total_t = 0.0
    nh3_spill_t_sum = 0.0
    ship_out_total_t = 0.0
    ship_count = 0

    # Wasser-Balance Summen
    water_need_total_m3 = 0.0
    ro_make_total_m3 = 0.0
    water_short_total_m3 = 0.0

    rows = [] if return_timeseries else None

    # -------------------------
    # Helper: RO <-> Power
    # -------------------------
    def ro_m3_from_power(p_mw: float) -> float:
        if ro_spec_kwh_per_m3 <= 0.0:
            return 0.0
        return max(0.0, (p_mw * 1000.0) / ro_spec_kwh_per_m3)  # m3/h

    def ro_power_from_m3(m3: float) -> float:
        return max(0.0, (m3 * ro_spec_kwh_per_m3) / 1000.0)  # MW

    # -------------------------
    # EL + RO + Tank (bilanz-sicher, ramp, H2-level control)
    # -------------------------
    def run_el_with_ro_and_tank(p_available_mw, soc_water_m3_current, soc_h2_kg_current, p_stack_prev_local):
        nonlocal el_allowed

        # H2-Level-Control (Hysterese)
        if soc_h2_kg_current >= h2_el_stop_kg:
            el_allowed = False
        elif soc_h2_kg_current <= h2_el_start_kg:
            el_allowed = True

        if (not el_allowed) or (p_available_mw <= 0.0):
            return 0.0, 0.0, 0.0, soc_h2_kg_current, 0.0, 0.0, 0.0, 0.0, soc_water_m3_current, 0.0, p_available_mw, 0.0

        # Ziel-Stackleistung aus verfügbarem Strom (inkl. Ladeenergie)
        el_total_factor = 1.0 + (h2_kg_per_mwh * eta_in * h2_spec_kwh_per_kg_in / 1000.0)
        p_el_candidate = min(p_el_max, p_available_mw / el_total_factor)
        p_stack_target = 0.0 if p_el_candidate < p_el_min else p_el_candidate

        if p_stack_target <= 0.0:
            return 0.0, 0.0, 0.0, soc_h2_kg_current, 0.0, 0.0, 0.0, 0.0, soc_water_m3_current, 0.0, p_available_mw, 0.0

        # Rampenlimit direkt auf p_stack (bilanz-sicher)
        p_step = float(el_ramp_frac_per_h) * float(p_el_max)
        p_stack = max(0.0, min(p_stack_prev_local + p_step, max(p_stack_prev_local - p_step, p_stack_target)))

        if p_stack < p_el_min:
            p_stack = 0.0

        if p_stack <= 0.0:
            return 0.0, 0.0, 0.0, soc_h2_kg_current, 0.0, 0.0, 0.0, 0.0, soc_water_m3_current, 0.0, p_available_mw, 0.0

        # Produktion + Wasserbedarf
        h2_prod_kg = p_stack * h2_kg_per_mwh
        water_need_m3 = (h2_prod_kg * water_kg_per_kgH2) / 1000.0

        tank_cap = max(0.0, float(water_tank_m3_max))

        water_from_tank = min(max(0.0, soc_water_m3_current), water_need_m3)
        missing_m3 = max(0.0, water_need_m3 - water_from_tank)

        # H2 rein
        h2_in_kg = h2_prod_kg * eta_in

        # H2 headroom erzwingen (verhindert "an die Decke knallen")
        headroom_kg = max(0.0, h2_storage_kg_max - soc_h2_kg_current)
        if h2_in_kg > headroom_kg + 1e-12 and h2_in_kg > 0:
            scale = max(0.0, min(1.0, headroom_kg / h2_in_kg))
            p_stack *= scale
            h2_prod_kg = p_stack * h2_kg_per_mwh
            water_need_m3 = (h2_prod_kg * water_kg_per_kgH2) / 1000.0
            water_from_tank = min(max(0.0, soc_water_m3_current), water_need_m3)
            missing_m3 = max(0.0, water_need_m3 - water_from_tank)
            h2_in_kg = h2_prod_kg * eta_in

        # Ladeenergie
        p_in = (h2_in_kg * h2_spec_kwh_per_kg_in) / 1000.0
        p_el_total = p_stack + p_in

        # RO mit Reststrom
        p_left_for_ro = max(0.0, p_available_mw - p_el_total)
        ro_possible_m3 = ro_m3_from_power(p_left_for_ro)

        ro_make_m3 = min(missing_m3, ro_possible_m3)
        p_ro = ro_power_from_m3(ro_make_m3)

        water_available_m3 = water_from_tank + ro_make_m3

        water_short_m3 = 0.0
        if water_need_m3 > water_available_m3 + 1e-12 and water_need_m3 > 0.0:
            scale = max(0.0, min(1.0, water_available_m3 / water_need_m3))
            p_stack *= scale
            h2_prod_kg = p_stack * h2_kg_per_mwh
            water_need_m3 = (h2_prod_kg * water_kg_per_kgH2) / 1000.0
            h2_in_kg = h2_prod_kg * eta_in
            p_in = (h2_in_kg * h2_spec_kwh_per_kg_in) / 1000.0
            p_el_total = p_stack + p_in
            if water_need_m3 > water_available_m3 + 1e-12:
                water_short_m3 = water_need_m3 - water_available_m3

        # Tank update
        soc_water_after = soc_water_m3_current - water_from_tank + ro_make_m3
        if tank_cap > 0.0:
            soc_water_after = min(tank_cap, soc_water_after)
        else:
            soc_water_after = 0.0

        # H2 update
        soc_h2_after = min(h2_storage_kg_max, soc_h2_kg_current + h2_in_kg)
        h2_spill = max(0.0, (soc_h2_kg_current + h2_in_kg) - h2_storage_kg_max)

        p_used = p_el_total + p_ro
        p_remaining_after = max(0.0, p_available_mw - p_used)

        return (float(p_stack), float(p_in), float(p_el_total), float(soc_h2_after), float(h2_spill),
                float(p_ro), float(ro_make_m3),
                float(water_need_m3), float(soc_water_after), float(water_short_m3),
                float(p_remaining_after), float(p_stack))

    def run_ro_fill_tank_with_rest(p_available_mw, soc_water_m3_current):
        tank_cap = max(0.0, float(water_tank_m3_max))
        if tank_cap <= 0.0 or p_available_mw <= 0.0:
            return 0.0, 0.0, soc_water_m3_current

        headroom = max(0.0, tank_cap - soc_water_m3_current)
        if headroom <= 0.0:
            return 0.0, 0.0, soc_water_m3_current

        ro_make_m3 = min(headroom, ro_m3_from_power(p_available_mw))
        p_ro_mw = ro_power_from_m3(ro_make_m3)
        soc_after = soc_water_m3_current + ro_make_m3
        return float(p_ro_mw), float(ro_make_m3), float(soc_after)

    # -------------------------
    # Loop
    # -------------------------
    for hour_index, (ts, p_wind_base) in enumerate(df_profile["p_mw"].items()):
        p_wind = float(p_wind_base) * float(s)

        # Water Tank Verluste
        if water_loss_frac_per_hour > 0.0:
            soc_water_m3 *= (1.0 - water_loss_frac_per_hour)

        # -------------------------
        # KÜHLUNG FIRST: zieht Windstrom ab
        # -------------------------
        bog_kg = soc_h2_kg * loss_frac_per_hour
        reliq_kg = bog_kg * h2_reliq_frac
        p_h2_reliq_mw = (reliq_kg * h2_reliq_kwh_per_kg) / 1000.0
        soc_h2_kg -= bog_kg

        p_nh3_cooling_mw = (soc_nh3_t * nh3_cooling_kwh_per_t_per_day / 24.0) / 1000.0

        h2_reliq_mwh_sum += p_h2_reliq_mw
        nh3_cooling_mwh_sum += p_nh3_cooling_mw

        # HB-Hilfsgrößen
        nh3_possible_from_h2_kg = (soc_h2_kg * eta_out) / h2_kg_per_kg_nh3
        nh3_possible_from_h2_t = nh3_possible_from_h2_kg / 1000.0

        kwh_per_t_hb = hb_spec_kwh_per_kgNH3 * 1000.0
        kwh_per_t_n2 = (n2_kg_per_kg_nh3 * 1000.0) * spec_kwh_per_kgN2
        kwh_per_t_h2_out = (h2_kg_per_kg_nh3 * 1000.0) * h2_spec_kwh_per_kg_out
        kwh_per_t_nh3_in = nh3_spec_kwh_per_t_in
        kwh_per_t_hbchain = kwh_per_t_hb + kwh_per_t_n2 + kwh_per_t_h2_out + kwh_per_t_nh3_in

        # Init pro Stunde
        nh3_hb_t = 0.0
        p_hbchain_mw = 0.0

        p_el = 0.0
        p_h2_in_mw = 0.0
        p_el_total_mw = 0.0
        h2_spill_kg = 0.0

        p_ro_mw = 0.0
        ro_make_m3 = 0.0
        water_need_m3 = 0.0
        water_short_m3 = 0.0

        def run_hb(p_available_mw):
            nonlocal nh3_possible_from_h2_t, nh3_hb_prev_t

            if nh3_prod_total_t >= nh3_target_total_t - 1e-9:
                nh3_hb_prev_t = 0.0
                return 0.0, 0.0

            # NH3 Level Control: wenn Tank "hoch genug", HB aus
            if soc_nh3_t >= nh3_soc_high_t:
                nh3_hb_prev_t = 0.0
                return 0.0, 0.0

            if nh3_possible_from_h2_t <= 0.0 or hb_capacity_tNH3_per_h <= 0.0:
                nh3_hb_prev_t = 0.0
                return 0.0, 0.0

            # nur bis Zielniveau auffüllen
            nh3_free_t = max(0.0, nh3_soc_target_t - soc_nh3_t)
            if nh3_free_t <= 0.0:
                nh3_hb_prev_t = 0.0
                return 0.0, 0.0

            if kwh_per_t_hbchain > 0.0:
                nh3_power_limit_t = (p_available_mw * 1000.0) / kwh_per_t_hbchain
            else:
                nh3_power_limit_t = hb_capacity_tNH3_per_h

            nh3_remaining_total_t = max(0.0, nh3_target_total_t - nh3_prod_total_t)

            nh3_t = min(
                hb_capacity_tNH3_per_h,
                nh3_possible_from_h2_t,
                nh3_power_limit_t,
                nh3_free_t,
                nh3_remaining_total_t
            )

            if nh3_t > 0.0 and nh3_t < hb_min_frac_when_on * hb_capacity_tNH3_per_h:
                nh3_hb_prev_t = 0.0
                return 0.0, 0.0

            # -------- HB Ramp (bilanz-sicher) --------
            nh3_step = float(hb_ramp_frac_per_h) * float(hb_capacity_tNH3_per_h)
            nh3_t = max(0.0, min(nh3_hb_prev_t + nh3_step, max(nh3_hb_prev_t - nh3_step, nh3_t)))

            p_used = (nh3_t * kwh_per_t_hbchain) / 1000.0
            nh3_hb_prev_t = float(nh3_t)
            return nh3_t, p_used

        # -------------------------
        # Dispatch (Kühlung abgezogen!)
        # -------------------------
        p_rem = max(0.0, p_wind - p_h2_reliq_mw - p_nh3_cooling_mw)

        # HB zuerst
        nh3_0, p0 = run_hb(p_rem)
        nh3_hb_t += nh3_0
        p_hbchain_mw += p0
        p_rem = max(0.0, p_rem - p0)

        # EL + RO gekoppelt (bilanz-sicher)
        (p_el, p_h2_in_mw, p_el_total_mw, soc_h2_kg, h2_spill_kg,
         p_ro_mw, ro_make_m3,
         water_need_m3, soc_water_m3, water_short_m3,
         p_rem, p_stack_used) = run_el_with_ro_and_tank(p_rem, soc_water_m3, soc_h2_kg, p_stack_prev)

        p_stack_prev = p_stack_used

        # Optional: Tank mit Rest füllen
        p_ro2_mw, ro_make2_m3, soc_water_m3 = run_ro_fill_tank_with_rest(p_rem, soc_water_m3)
        p_ro_mw += p_ro2_mw
        ro_make_m3 += ro_make2_m3
        p_rem = max(0.0, p_rem - p_ro2_mw)

        # nach EL nochmal HB
        nh3_possible_from_h2_kg = (soc_h2_kg * eta_out) / h2_kg_per_kg_nh3
        nh3_possible_from_h2_t = nh3_possible_from_h2_kg / 1000.0

        nh3_1, p1 = run_hb(p_rem)
        nh3_hb_t += nh3_1
        p_hbchain_mw += p1
        p_rem = max(0.0, p_rem - p1)

        # -------------------------
        # Material + Energie aus HB
        # -------------------------
        if nh3_hb_t > 0.0:
            h2_cons_kg = nh3_hb_t * 1000.0 * h2_kg_per_kg_nh3
            soc_h2_kg = max(0.0, soc_h2_kg - (h2_cons_kg / eta_out))

            soc_nh3_t += nh3_hb_t
            nh3_prod_total_t += nh3_hb_t

            if soc_nh3_t > nh3_storage_t_max:
                nh3_spill_t_sum += (soc_nh3_t - nh3_storage_t_max)
                soc_nh3_t = nh3_storage_t_max

            hb_energy_mwh_sum += (nh3_hb_t * 1000.0 * hb_spec_kwh_per_kgNH3) / 1000.0

            n2_need_kg = nh3_hb_t * 1000.0 * n2_kg_per_kg_nh3
            n2_energy_mwh_sum += (n2_need_kg * spec_kwh_per_kgN2) / 1000.0

            h2_store_out_mwh_sum += (h2_cons_kg * h2_spec_kwh_per_kg_out) / 1000.0
            nh3_store_in_mwh_sum += (nh3_hb_t * nh3_spec_kwh_per_t_in) / 1000.0

        # EL Energie
        el_energy_mwh_sum += p_el
        h2_store_in_mwh_sum += p_h2_in_mw

        # RO Energie
        ro_energy_mwh_sum += p_ro_mw

        # Wasser Summen
        water_need_total_m3 += water_need_m3
        ro_make_total_m3 += ro_make_m3
        water_short_total_m3 += water_short_m3

        # -------------------------
        # Schiff (kontinuierlich)
        # -------------------------
        p_nh3_out_mw = 0.0
        loaded_t = 0.0
        hour_number = hour_index + 1

        if hour_number >= next_ship_time - 1e-9:
            ship_count += 1

            if soc_nh3_t >= nh3_target_per_ship_t:
                loaded_t = nh3_target_per_ship_t
                soc_nh3_t -= nh3_target_per_ship_t
            else:
                ships_failed_count += 1
                loaded_t = soc_nh3_t
                soc_nh3_t = 0.0

            ship_out_total_t += loaded_t

            p_nh3_out_mw = (loaded_t * nh3_spec_kwh_per_t_out) / 1000.0
            nh3_store_out_mwh_sum += p_nh3_out_mw

            next_ship_time += ship_interval

        # Curtailment + Maxima
        p_used_total = (
            p_h2_reliq_mw +
            p_nh3_cooling_mw +
            p_hbchain_mw +
            p_ro_mw +
            p_el_total_mw +
            p_nh3_out_mw
        )

        curtailed_mwh += max(p_wind - p_used_total, 0.0)

        h2_soc_max_kg = max(h2_soc_max_kg, soc_h2_kg)
        nh3_soc_max_t = max(nh3_soc_max_t, soc_nh3_t)
        water_soc_max_m3 = max(water_soc_max_m3, soc_water_m3)

        if return_timeseries:
            rows.append({
                "t": ts,
                "p_wind_mw": p_wind,
                "p_h2_reliq_mw": p_h2_reliq_mw,
                "p_nh3_cooling_mw": p_nh3_cooling_mw,
                "p_hbchain_mw": p_hbchain_mw,
                "p_ro_mw": p_ro_mw,
                "p_el_mw": p_el,
                "p_used_total_mw": p_used_total,
                "curtail_mwh": max(p_wind - p_used_total, 0.0),

                "h2_soc_kg": soc_h2_kg,
                "nh3_soc_t": soc_nh3_t,
                "water_soc_m3": soc_water_m3,

                "nh3_prod_t": nh3_hb_t,
                "ship_loaded_t": loaded_t,
                "h2_spill_kg": h2_spill_kg,

                "ro_make_m3": ro_make_m3,
                "water_need_m3": water_need_m3,
                "water_short_m3": water_short_m3,
            })

    # KPIs (Raster-kompatibel!)
    kpis = {
        "nh3_storage_max_t": float(nh3_soc_max_t),
        "h2_storage_max_t": float(h2_soc_max_kg / 1000.0),
        "water_storage_max_m3": float(water_soc_max_m3),

        "curtail_GWh_per_sim": float(curtailed_mwh / 1000.0),

        "ships_failed_count": int(ships_failed_count),
        "failed_ship": bool(ships_failed_count > 0),
        "ship_count": int(ship_count),

        "EL_el_MWh_per_sim": float(el_energy_mwh_sum),
        "HB_el_MWh_per_sim": float(hb_energy_mwh_sum),
        "N2_el_MWh_per_sim": float(n2_energy_mwh_sum),
        "RO_el_MWh_per_sim": float(ro_energy_mwh_sum),

        "H2_store_in_MWh_per_sim": float(h2_store_in_mwh_sum),
        "H2_store_out_MWh_per_sim": float(h2_store_out_mwh_sum),
        "NH3_store_in_MWh_per_sim": float(nh3_store_in_mwh_sum),
        "NH3_store_out_MWh_per_sim": float(nh3_store_out_mwh_sum),

        "H2_reliq_MWh_per_sim": float(h2_reliq_mwh_sum),
        "NH3_cooling_MWh_per_sim": float(nh3_cooling_mwh_sum),

        "nh3_prod_total_t": float(nh3_prod_total_t),
        "nh3_target_total_t": float(nh3_target_total_t),
        "nh3_spill_t_per_sim": float(nh3_spill_t_sum),
        "ship_out_total_t": float(ship_out_total_t),

        "nh3_storage_t_max": float(nh3_storage_t_max),
        "sim_years_est": float(sim_years_est),

        "water_need_total_m3": float(water_need_total_m3),
        "ro_make_total_m3": float(ro_make_total_m3),
        "water_short_total_m3": float(water_short_total_m3),
    }

    if debug_ships:
        print("\n--- FINAL CHECK (Raster-kompatibel) ---")
        print("sim_years_est:", round(sim_years_est, 3))
        print("ship_count:", ship_count, "| expected ~:", int(round(sim_years_est * ships_per_year)))
        print("ships_failed_count:", ships_failed_count)
        print("NH3 target total [t]:", round(nh3_target_total_t, 2))
        print("NH3 produced total [t]:", round(nh3_prod_total_t, 2))
        print("ship_out_total_t:", round(ship_out_total_t, 2))
        print("nh3_soc_end_t:", round(soc_nh3_t, 2))
        print("nh3_storage_t_max:", round(nh3_storage_t_max, 2))
        print("NH3 target level [t]:", round(nh3_soc_target_t, 2), "| band:", round(nh3_soc_low_t, 2), "-", round(nh3_soc_high_t, 2))
        print("H2 end [t]:", round(soc_h2_kg / 1000.0, 2), "| H2 max [t]:", round(h2_soc_max_kg / 1000.0, 2))
        print("Curtailment [GWh]:", round(curtailed_mwh / 1000.0, 3))
        print("Water end [m3]:", round(soc_water_m3, 2), "| Water max [m3]:", round(water_soc_max_m3, 2))

    out = pd.DataFrame(rows).set_index("t") if return_timeseries else None
    return out, kpis


# %%
# %%
# %% Kosten der Komponenten (inkl. N2 + RO + Water Tank)

def cost_components_proxy(
    s: float,
    p_el_mw: float,
    nh3_storage_t: float,
    h2_storage_t_design: float,
    water_tank_m3_design: float,          # <- NEU (Design-Volumen)
    technology: str = "AEL"
):
    tech = technology.upper()
    years = float(cost_params["general"]["project_lifetime_years"])

    # -----------------------------
    # Wind (CAPEX/OPEX, installierte Nennleistung fix)
    # -----------------------------
    wind = cost_params["wind"]

    wind_capacity_mw = float(p_wind_rated_mw)      # FIX: installierte Leistung
    wind_capacity_kw = wind_capacity_mw * 1000.0

    wind_capex = float(wind["capex_eur_per_mw"]) * wind_capacity_mw
    wind_opex  = float(wind["opex_eur_per_kw_per_year"]) * wind_capacity_kw * years

    wind_total = wind_capex + wind_opex
    wind_dapex = 0.0
   

# Relikt aus vorheriger Simulation, wurde rausgenommen. Wär aber viel aufwand raus zu bekommen.
    # -----------------------------
    # Elektrolyse
    # -----------------------------
    elp = cost_params["h2"]["electrolyzer"][tech]
    el_capex = elp["capex_usd_per_kw"] * p_el_mw * 1000.0
    el_opex_total = elp["opex_usd_per_kw_per_year"] * p_el_mw * 1000.0 * years

    # -----------------------------
    # H2 Speicher
    # -----------------------------
    h2p = cost_params["h2"]["storage"]
    h2_capex = h2p["capex_usd_per_tH2"] * h2_storage_t_design
    h2_opex_total = h2_capex * h2p["opex_fraction_per_year"] * years

    # -----------------------------
    # NH3 Speicher
    # -----------------------------
    nh3p = cost_params["nh3_storage"]
    nh3_capex = nh3p["capex_usd_per_tNH3"] * nh3_storage_t
    nh3_opex_total = nh3_capex * nh3p["opex_fraction_per_year"] * years

    # -----------------------------
    # Haber-Bosch
    # -----------------------------
    hbp = cost_params["haber_bosch"]
    hb_cap_tpy = hb_capacity_tNH3_per_day * 365.0
    hb_capex = hbp["capex_usd_per_tNH3_per_year"] * hb_cap_tpy
    hb_opex_total = hbp["opex_usd_per_tNH3"] * annual_nh3_prod_t * years

    # -----------------------------
    # N2-Aufbereitung (Platzhalter)
    # -----------------------------
    n2p = cost_params["n2"]
    n2_kg_per_kg_nh3 = 28.0 / 34.0
    hb_capacity_tNH3_per_h = hb_capacity_tNH3_per_day / 24.0
    n2_capacity_kg_per_h = hb_capacity_tNH3_per_h * 1000.0 * n2_kg_per_kg_nh3

    n2_capex = float(n2p["capex_usd_per_kgN2_per_h"]) * float(n2_capacity_kg_per_h)
    n2_opex_total = float(n2p["opex_fraction_per_year"]) * n2_capex * years

    # -----------------------------
    # RO (Platzhalter) – Design gekoppelt an EL Designleistung
    # -----------------------------
    rop = cost_params.get("water", {}).get("ro", {})
    water_kg_per_kgH2 = float(rop.get("water_kg_per_kgH2", 10.0))
    ro_capex_usd_per_m3pd = float(rop.get("capex_usd_per_m3_per_day", 1200.0))
    ro_opex_frac = float(rop.get("opex_fraction_per_year", 0.05))
    ro_opex_usd_per_m3 = float(rop.get("opex_usd_per_m3", 0.0))

    spec_kwh_per_kgH2_el = float(cost_params["h2"]["electrolyzer"][tech]["spec_kwh_per_kgH2"])
    h2_kg_per_h_design = (p_el_mw * 1000.0) / spec_kwh_per_kgH2_el

    ro_m3_per_h_design = (h2_kg_per_h_design * water_kg_per_kgH2) / 1000.0
    ro_m3_per_day_design = ro_m3_per_h_design * 24.0

    ro_capex = ro_capex_usd_per_m3pd * ro_m3_per_day_design
    ro_opex_total = ro_capex * ro_opex_frac * years

    # variable OPEX über Lebensdauer anhand Jahres-H2-Ziel
    annual_water_m3 = (annual_h2_prod_t * 1000.0 * water_kg_per_kgH2) / 1000.0
    ro_opex_total += ro_opex_usd_per_m3 * annual_water_m3 * years

    # -----------------------------
    # Water Tank (Platzhalter)
    # -----------------------------
    wtp = cost_params.get("water", {}).get("tank", {})
    tank_capex_per_m3 = float(wtp.get("capex_usd_per_m3", 50.0))
    tank_opex_frac = float(wtp.get("opex_fraction_per_year", 0.02))

    water_tank_capex = tank_capex_per_m3 * float(water_tank_m3_design)
    water_tank_opex_total = water_tank_capex * tank_opex_frac * years

    # -----------------------------
    # Total
    # -----------------------------
    total_proxy = (
        wind_total +
        el_capex + el_opex_total +
        hb_capex + hb_opex_total +
        n2_capex + n2_opex_total +
        ro_capex + ro_opex_total +
        water_tank_capex + water_tank_opex_total +
        h2_capex + h2_opex_total +
        nh3_capex + nh3_opex_total
    )

    return (
        wind_total, wind_capex, wind_opex, wind_dapex,
        el_capex, el_opex_total,
        hb_capex, hb_opex_total,
        n2_capex, n2_opex_total,
        ro_capex, ro_opex_total,
        water_tank_capex, water_tank_opex_total,
        h2_capex, h2_opex_total,
        nh3_capex, nh3_opex_total,
        total_proxy
    )


# %%
# %%
# %% Raster (NH3-Speicher + Wassertank als Raster, inkl. RO/Tank-Kosten)

s_values = np.arange(0.95, 1.00001, 0.01)
pel_values = np.arange(1000, 1200, 50)
h2_storage_days_values = np.arange(1, 2.1, 1)

nh3_storage_ships_values = np.arange(1, 1.51, 0.25)
water_tank_m3_values = np.arange(500, 4501, 2000)

rows_ael = []
rows_pem = []

for s in s_values:
    for pel in pel_values:
        for h2_days in h2_storage_days_values:
            h2_storage_t_candidate = (annual_h2_prod_t / 365.0) * float(h2_days)

            for nh3_ships in nh3_storage_ships_values:
                for w_tank_m3 in water_tank_m3_values:

                    # ---------- AEL ----------
                    _, kpi_ael = simulate_hourly_system(
                        s=float(s),
                        p_el_mw=float(pel),
                        technology="AEL",
                        h2_storage_t_max=float(h2_storage_t_candidate),
                        nh3_storage_ships=float(nh3_ships),
                        water_tank_m3_max=float(w_tank_m3),
                        return_timeseries=False,
                        df_profile=df2
                    )

                    (wind_total_a, wind_capex_a, wind_opex_a, wind_dapex_a,
                     el_capex_a, el_opex_a,
                     hb_capex_a, hb_opex_a,
                     n2_capex_a, n2_opex_a,
                     ro_capex_a, ro_opex_a,
                     wt_capex_a, wt_opex_a,
                     h2_capex_a, h2_opex_a,
                     nh3_capex_a, nh3_opex_a,
                     tot_a) = cost_components_proxy(
                        s=float(s),
                        p_el_mw=float(pel),
                        nh3_storage_t=float(kpi_ael["nh3_storage_max_t"]),
                        h2_storage_t_design=float(h2_storage_t_candidate),
                        water_tank_m3_design=float(w_tank_m3),
                        technology="AEL"
                    )

                    rows_ael.append((
                        float(s), float(pel), float(h2_days), float(h2_storage_t_candidate),
                        float(nh3_ships), float(w_tank_m3),

                        float(kpi_ael["nh3_storage_max_t"]),
                        float(kpi_ael["h2_storage_max_t"]),
                        float(kpi_ael["water_storage_max_m3"]),
                        float(kpi_ael["curtail_GWh_per_sim"]),
                        int(kpi_ael["ships_failed_count"]),

                        float(kpi_ael["EL_el_MWh_per_sim"]),
                        float(kpi_ael["RO_el_MWh_per_sim"]),
                        float(kpi_ael["HB_el_MWh_per_sim"]),
                        float(kpi_ael["N2_el_MWh_per_sim"]),

                        float(kpi_ael["H2_store_in_MWh_per_sim"]),
                        float(kpi_ael["H2_store_out_MWh_per_sim"]),
                        float(kpi_ael["NH3_store_in_MWh_per_sim"]),
                        float(kpi_ael["NH3_store_out_MWh_per_sim"]),

                        float(wind_total_a), float(wind_capex_a), float(wind_opex_a), float(wind_dapex_a),
                        float(el_capex_a), float(el_opex_a),
                        float(hb_capex_a), float(hb_opex_a),
                        float(n2_capex_a), float(n2_opex_a),
                        float(ro_capex_a), float(ro_opex_a),
                        float(wt_capex_a), float(wt_opex_a),
                        float(h2_capex_a), float(h2_opex_a),
                        float(nh3_capex_a), float(nh3_opex_a),

                        float(tot_a),
                    ))

                    # ---------- PEM ----------
                    _, kpi_pem = simulate_hourly_system(
                        s=float(s),
                        p_el_mw=float(pel),
                        technology="PEM",
                        h2_storage_t_max=float(h2_storage_t_candidate),
                        nh3_storage_ships=float(nh3_ships),
                        water_tank_m3_max=float(w_tank_m3),
                        return_timeseries=False,
                        df_profile=df2
                    )

                    (wind_total_p, wind_capex_p, wind_opex_p, wind_dapex_p,
                     el_capex_p, el_opex_p,
                     hb_capex_p, hb_opex_p,
                     n2_capex_p, n2_opex_p,
                     ro_capex_p, ro_opex_p,
                     wt_capex_p, wt_opex_p,
                     h2_capex_p, h2_opex_p,
                     nh3_capex_p, nh3_opex_p,
                     tot_p) = cost_components_proxy(
                        s=float(s),
                        p_el_mw=float(pel),
                        nh3_storage_t=float(kpi_pem["nh3_storage_max_t"]),
                        h2_storage_t_design=float(h2_storage_t_candidate),
                        water_tank_m3_design=float(w_tank_m3),
                        technology="PEM"
                    )

                    rows_pem.append((
                        float(s), float(pel), float(h2_days), float(h2_storage_t_candidate),
                        float(nh3_ships), float(w_tank_m3),

                        float(kpi_pem["nh3_storage_max_t"]),
                        float(kpi_pem["h2_storage_max_t"]),
                        float(kpi_pem["water_storage_max_m3"]),
                        float(kpi_pem["curtail_GWh_per_sim"]),
                        int(kpi_pem["ships_failed_count"]),

                        float(kpi_pem["EL_el_MWh_per_sim"]),
                        float(kpi_pem["RO_el_MWh_per_sim"]),
                        float(kpi_pem["HB_el_MWh_per_sim"]),
                        float(kpi_pem["N2_el_MWh_per_sim"]),

                        float(kpi_pem["H2_store_in_MWh_per_sim"]),
                        float(kpi_pem["H2_store_out_MWh_per_sim"]),
                        float(kpi_pem["NH3_store_in_MWh_per_sim"]),
                        float(kpi_pem["NH3_store_out_MWh_per_sim"]),

                        float(wind_total_p), float(wind_capex_p), float(wind_opex_p), float(wind_dapex_p),
                        float(el_capex_p), float(el_opex_p),
                        float(hb_capex_p), float(hb_opex_p),
                        float(n2_capex_p), float(n2_opex_p),
                        float(ro_capex_p), float(ro_opex_p),
                        float(wt_capex_p), float(wt_opex_p),
                        float(h2_capex_p), float(h2_opex_p),
                        float(nh3_capex_p), float(nh3_opex_p),

                        float(tot_p),
                    ))

cols = [
    "s", "P_el_MW", "h2_storage_days", "h2_storage_t_design",
    "nh3_storage_ships", "water_tank_m3_max",

    "NH3_storage_max_t", "H2_storage_max_t", "Water_storage_max_m3",
    "Curtail_GWh_per_sim", "ships_failed_count",

    "EL_el_MWh_per_sim", "RO_el_MWh_per_sim", "HB_el_MWh_per_sim", "N2_el_MWh_per_sim",
    "H2_store_in_MWh_per_sim", "H2_store_out_MWh_per_sim",
    "NH3_store_in_MWh_per_sim", "NH3_store_out_MWh_per_sim",

    "Wind_TOTAL", "Wind_CAPEX", "Wind_OPEX", "Wind_DAPEX",
    "EL_CAPEX", "EL_OPEX_total",
    "HB_CAPEX", "HB_OPEX_total",
    "N2_CAPEX", "N2_OPEX_total",
    "RO_CAPEX", "RO_OPEX_total",
    "WATER_TANK_CAPEX", "WATER_TANK_OPEX_total",
    "H2_STORE_CAPEX", "H2_STORE_OPEX_total",
    "NH3_STORE_CAPEX", "NH3_STORE_OPEX_total",

    "Total_proxy",
]

res_ael = pd.DataFrame(rows_ael, columns=cols)
res_pem = pd.DataFrame(rows_pem, columns=cols)

print("Raster fertig.")
print("AEL rows:", len(res_ael), "| PEM rows:", len(res_pem))
print("Feasible AEL:", int((res_ael["ships_failed_count"] == 0).sum()),
      "| Feasible PEM:", int((res_pem["ships_failed_count"] == 0).sum()))


# %%
# %%
# %% Top 3 + Winner

res_ael_ok = res_ael[res_ael["ships_failed_count"] == 0].copy()
res_pem_ok = res_pem[res_pem["ships_failed_count"] == 0].copy()

print("AEL – Top 3 (feasible):")
display(res_ael_ok.sort_values("Total_proxy").head(3).reset_index(drop=True))

print("PEM – Top 3 (feasible):")
display(res_pem_ok.sort_values("Total_proxy").head(3).reset_index(drop=True))

res_ael_ok["tech"] = "AEL"
res_pem_ok["tech"] = "PEM"
combined_ok = pd.concat([res_ael_ok, res_pem_ok], ignore_index=True)

if len(combined_ok) == 0:
    print("WARNUNG: Keine fully-feasible Lösung. Wähle minimal failures + Penalty.")
    res_ael_all = res_ael.copy(); res_ael_all["tech"] = "AEL"
    res_pem_all = res_pem.copy(); res_pem_all["tech"] = "PEM"
    combined_all = pd.concat([res_ael_all, res_pem_all], ignore_index=True)
    penalty = 1e12
    combined_all["Total_proxy_penalized"] = combined_all["Total_proxy"] + combined_all["ships_failed_count"] * penalty
    winner = combined_all.loc[combined_all["Total_proxy_penalized"].idxmin()].copy()
else:
    winner = combined_ok.loc[combined_ok["Total_proxy"].idxmin()].copy()

def fmt_money(x):
    x = float(x)
    if x >= 1e9: return f"{x/1e9:.2f} Mrd. $"
    if x >= 1e6: return f"{x/1e6:.1f} Mio. $"
    if x >= 1e3: return f"{x/1e3:.1f} Tsd. $"
    return f"{x:.0f} $"

winner_table = pd.DataFrame([
    ("Technologie", winner.get("tech","")),
    ("Windfaktor s [-]", float(winner["s"])),
    ("P_el [MW]", float(winner["P_el_MW"])),
    ("H2-Speicher [Tage]", float(winner["h2_storage_days"])),
    ("H2-Speicher [t H2] (Design)", float(winner["h2_storage_t_design"])),

    ("NH3-Speicher [Ships]", float(winner["nh3_storage_ships"])),
    ("Water Tank [m3] (Design)", float(winner["water_tank_m3_max"])),

    ("NH3-Speicher max [t]", float(winner["NH3_storage_max_t"])),
    ("Water SOC max [m3]", float(winner["Water_storage_max_m3"])),

    ("Curtailment [GWh/sim]", float(winner["Curtail_GWh_per_sim"])),
    ("Schiffsausfälle [#]", int(winner["ships_failed_count"])),
    ("Gesamt-Proxy-Kosten", fmt_money(winner["Total_proxy"])),
], columns=["Kennzahl","Wert"])
display(winner_table)


# %%
# %%
# %% Winner Timeseries erzeugen (WICHTIG: out_winner + kpi_w)
# Kernel-Reset-safe: wird jedes Mal sauber neu berechnet

out_winner, kpi_w = simulate_hourly_system(
    s=float(winner["s"]),
    p_el_mw=float(winner["P_el_MW"]),
    technology=str(winner.get("tech", "AEL")),
    h2_storage_t_max=float(winner["h2_storage_t_design"]),
    nh3_storage_ships=float(winner["nh3_storage_ships"]),
    water_tank_m3_max=float(winner["water_tank_m3_max"]),
    return_timeseries=True,
    debug_ships=False,
    df_profile=df2_sim  # <- WICHTIG: multi-year Profil für deine Projektjahre
)

print("out_winner ready:", out_winner.shape)


# %%
# %%
# %% Plots: SOC über alle Jahre (H2, NH3, Water) – X-Achse als Projektjahr 1..N

import numpy as np
import matplotlib.pyplot as plt

def apply_project_year_axis(ax, n, years_sim, hours_per_year=8760):
    tick_pos = [i * hours_per_year for i in range(years_sim) if i * hours_per_year < n]
    tick_lab = [f"Jahr {i+1}" for i in range(len(tick_pos))]
    ax.set_xlim(0, max(n - 1, 1))
    ax.set_xticks(tick_pos)
    ax.set_xticklabels(tick_lab, rotation=0)
    ax.set_xlabel("Projektjahr")

# Stundenachse 0..n-1 (immer safe, egal ob DatetimeIndex oder RangeIndex)
n = len(out_winner)
t = np.arange(n)

# H2
plt.figure(figsize=(13, 4))
ax = plt.gca()
ax.plot(t, out_winner["h2_soc_kg"])
ax.set_title("H2 Speicherfüllstand")
ax.set_ylabel("H2 SOC [kg]")
ax.grid(True)
apply_project_year_axis(ax, n, years_sim=years_sim, hours_per_year=8760)
plt.tight_layout()
plt.show()

# NH3
plt.figure(figsize=(13, 4))
ax = plt.gca()
ax.plot(t, out_winner["nh3_soc_t"])
ax.set_title("NH3 Tankfüllstand")
ax.set_ylabel("NH3 SOC [t]")
ax.grid(True)
apply_project_year_axis(ax, n, years_sim=years_sim, hours_per_year=8760)
plt.tight_layout()
plt.show()

# Water
plt.figure(figsize=(13, 4))
ax = plt.gca()
ax.plot(t, out_winner["water_soc_m3"])
ax.set_title("Wassertankfüllstand")
ax.set_ylabel("Water SOC [m³]")
ax.grid(True)
apply_project_year_axis(ax, n, years_sim=years_sim, hours_per_year=8760)
plt.tight_layout()
plt.show()

# Ship Events auf NH3 Plot
show_ship_events = True
if show_ship_events and "ship_loaded_t" in out_winner.columns:
    ship_mask = out_winner["ship_loaded_t"].to_numpy() > 0

    plt.figure(figsize=(13, 4))
    ax = plt.gca()
    ax.plot(t, out_winner["nh3_soc_t"], label="NH3 SOC")

    if ship_mask.any():
        ship_pos = np.where(ship_mask)[0]  # <- garantiert Stundenpositionen
        ax.scatter(ship_pos, out_winner.loc[ship_mask, "nh3_soc_t"], s=10, label="Abholung")

    ax.set_title("NH3 Tankfüllstand (mit Abholungen)")
    ax.set_ylabel("NH3 SOC [t]")
    ax.grid(True)
    apply_project_year_axis(ax, n, years_sim=years_sim, hours_per_year=8760)
    if ship_mask.any():
        ax.legend()
    plt.tight_layout()
    plt.show()


# %%
# %% SOC_Speicherstände – Zeitreihen als CSV ausgeben
# Erwartet: out_winner (Timeseries DataFrame)

import pandas as pd

# -----------------------------
# SOC-Zeitreihen zusammenstellen
# -----------------------------
SOC_Speicherstände = pd.DataFrame(index=out_winner.index)

SOC_Speicherstände["H2_SOC_kg"]    = out_winner["h2_soc_kg"].astype(float)
SOC_Speicherstände["H2_SOC_t"]     = out_winner["h2_soc_kg"].astype(float) / 1000.0
SOC_Speicherstände["NH3_SOC_t"]    = out_winner["nh3_soc_t"].astype(float)
SOC_Speicherstände["Water_SOC_m3"] = out_winner["water_soc_m3"].astype(float)

# Optional: Zeitspalte explizit mitschreiben
SOC_Speicherstände_out = SOC_Speicherstände.copy()
SOC_Speicherstände_out.insert(0, "time", SOC_Speicherstände_out.index)

# -----------------------------
# CSV schreiben
# -----------------------------
csv_path = "SOC_Speicherstände.csv"
SOC_Speicherstände_out.to_csv(csv_path, index=False)

print(f"CSV exportiert: {csv_path}")
print("Spalten:", list(SOC_Speicherstände_out.columns))
print("Zeilen:", len(SOC_Speicherstände_out))


# %%
# %% NH3 Speicher – Jahr 10 mit Durchschnittslinie

import numpy as np
import matplotlib.pyplot as plt

YEAR = 10
HOURS_PER_YEAR = 8760

start = (YEAR - 1) * HOURS_PER_YEAR
end   = YEAR * HOURS_PER_YEAR

out_y10 = out_winner.iloc[start:end].copy()
t = np.arange(len(out_y10))

nh3_mean = out_y10["nh3_soc_t"].mean()

plt.figure(figsize=(12,4))
plt.plot(t, out_y10["nh3_soc_t"], label="NH₃ SOC")
plt.axhline(nh3_mean, color="red", linestyle="--",
            label=f"Ø NH₃ = {nh3_mean:,.0f} t")

plt.ylabel("NH₃ Speicherstand [t]")
plt.xlabel("Stunde im Jahr")
plt.title("NH₃-Speicherfüllstand – Jahr 10")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# %% H2 Speicher – Jahr 10 mit Durchschnittslinie

h2_mean = (out_y10["h2_soc_kg"] / 1000.0).mean()

plt.figure(figsize=(12,4))
plt.plot(t, out_y10["h2_soc_kg"] / 1000.0, label="H₂ SOC")
plt.axhline(h2_mean, color="red", linestyle="--",
            label=f"Ø H₂ = {h2_mean:,.1f} t")

plt.ylabel("H₂ Speicherstand [t]")
plt.xlabel("Stunde im Jahr")
plt.title("H₂-Speicherfüllstand – Jahr 10")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# %% Water Tank – Jahr 10 mit Durchschnittslinie (rot)

import numpy as np
import matplotlib.pyplot as plt

YEAR = 10
HOURS_PER_YEAR = 8760

start = (YEAR - 1) * HOURS_PER_YEAR
end   = YEAR * HOURS_PER_YEAR

out_y10 = out_winner.iloc[start:end].copy()
t = np.arange(len(out_y10))

water_mean = out_y10["water_soc_m3"].mean()

plt.figure(figsize=(12,4))
plt.plot(t, out_y10["water_soc_m3"], label="Water SOC")
plt.axhline(water_mean, color="red", linestyle="--",
            label=f"Ø Water = {water_mean:,.0f} m³")

plt.ylabel("Wasser Speicherstand [m³]")
plt.xlabel("Stunde im Jahr")
plt.title("Wassertankfüllstand – Jahr 10")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()



# %%
# %% Kombifolie (NH3 + H2) – Jahr 10 mit Durchschnittslinien (rot)

import numpy as np
import matplotlib.pyplot as plt

YEAR = 10
HOURS_PER_YEAR = 8760

start = (YEAR - 1) * HOURS_PER_YEAR
end   = YEAR * HOURS_PER_YEAR

out_y10 = out_winner.iloc[start:end].copy()
t = np.arange(len(out_y10))

nh3 = out_y10["nh3_soc_t"]
h2  = out_y10["h2_soc_kg"] / 1000.0  # t

nh3_mean = nh3.mean()
h2_mean  = h2.mean()

fig, axes = plt.subplots(2, 1, figsize=(13, 7), sharex=True)

# --- NH3 ---
axes[0].plot(t, nh3, label="NH₃ SOC")
axes[0].axhline(nh3_mean, color="red", linestyle="--",
                label=f"Ø NH₃ = {nh3_mean:,.0f} t")
axes[0].set_ylabel("NH₃ [t]")
axes[0].set_title("Speicherfüllstände – Jahr 10")
axes[0].grid(True)
axes[0].legend()

# --- H2 ---
axes[1].plot(t, h2, label="H₂ SOC")
axes[1].axhline(h2_mean, color="red", linestyle="--",
                label=f"Ø H₂ = {h2_mean:,.1f} t")
axes[1].set_ylabel("H₂ [t]")
axes[1].set_xlabel("Stunde im Jahr")
axes[1].grid(True)
axes[1].legend()

plt.tight_layout()
plt.show()


# %%
# %%
# %% Jahresdauerlinie + Elektrolyseur-Auslegung: Vollaststunden & Betriebsstunden
import numpy as np
import matplotlib.pyplot as plt

def duration_curve_sizing(
    p_wind_mw: np.ndarray,
    p_el_rated_mw: float,
    p_el_min_frac: float = 0.05,
    title: str = "Jahresdauerlinie + Elektrolyseur"
):
    """
    Erstellt eine Jahresdauerlinie (Wind sortiert absteigend) und überlagert den Elektrolyseur.
    Annahme (Sizing): Elektrolyse nutzt Wind direkt bis P_el_rated; darunter nur wenn >= Mindestlast.
    """
    p = np.asarray(p_wind_mw, dtype=float)
    p = np.clip(p, 0.0, None)
    n = len(p)

    p_sorted = np.sort(p)[::-1]
    x = np.arange(n)

    p_min = p_el_min_frac * p_el_rated_mw

    # "Idealer" Elektrolyse-Betrieb nur aus Wind (Sizing-Annäherung)
    p_el_ideal = np.minimum(p_sorted, p_el_rated_mw)
    p_el_ideal = np.where((p_el_ideal > 0) & (p_el_ideal < p_min), 0.0, p_el_ideal)

    # Kennzahlen
    el_energy_mwh = float(np.sum(p_el_ideal))                  # weil 1h Zeitschritt
    flh_equiv_h   = el_energy_mwh / float(p_el_rated_mw)       # rechnerische Vollaststunden
    op_hours_h    = int(np.sum(p_el_ideal > 0))                # Betriebsstunden (an)
    full_hours_h  = int(np.sum(p_sorted >= p_el_rated_mw))     # Stunden mit genügend Wind für Vollast
    part_hours_h  = int(np.sum((p_el_ideal > 0) & (p_sorted < p_el_rated_mw)))

    # Plot
    plt.figure(figsize=(11,5))
    plt.plot(x, p_sorted, label="Windpark (sortiert) [MW]")
    plt.axhline(p_el_rated_mw, linestyle="--", label=f"Elektrolyse Nennlast = {p_el_rated_mw:.0f} MW")

    # Vollastfläche: 0..full_hours_h bei P_rated
    if full_hours_h > 0:
        xx = np.arange(full_hours_h)
        plt.fill_between(xx, 0, p_el_rated_mw, alpha=0.35, label=f"Vollastbereich ({full_hours_h} h)")

    # Teillastfläche: dort wo 0 < p_el_ideal < P_rated
    mask_part = (p_el_ideal > 0) & (p_sorted < p_el_rated_mw)
    if np.any(mask_part):
        plt.fill_between(x[mask_part], 0, p_el_ideal[mask_part], alpha=0.25,
                         label=f"Teillastbereich ({part_hours_h} h)")

    # Vertikale Linien wie in der Folie
    plt.axvline(flh_equiv_h, linestyle=":", label=f"rechn. Vollaststunden = {flh_equiv_h:.0f} h")
    plt.axvline(op_hours_h, linestyle=":", label=f"Betriebsstunden = {op_hours_h} h")

    plt.xlabel("Stunden [h/a] (sortiert)")
    plt.ylabel("Leistung [MW]")
    plt.title(title)
    plt.grid(True)
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.show()

    return {
        "EL_energy_MWh_per_year_equiv": el_energy_mwh,
        "EL_full_load_hours_equiv_h": flh_equiv_h,
        "EL_operating_hours_h": op_hours_h,
        "EL_full_load_hours_count_h": full_hours_h,
        "EL_part_load_hours_h": part_hours_h,
        "P_el_rated_MW": float(p_el_rated_mw),
        "P_el_min_MW": float(p_min),
    }

def electrolyzer_hours_from_timeseries(p_el_mw_ts: np.ndarray, p_el_rated_mw: float, p_el_min_frac: float=0.05):
    """
    Kennzahlen aus deiner echten Simulation (out_winner["p_el_mw"]).
    """
    p = np.asarray(p_el_mw_ts, dtype=float)
    p = np.clip(p, 0.0, None)
    p_min = p_el_min_frac * p_el_rated_mw

    energy_mwh = float(np.sum(p))
    flh_equiv_h = energy_mwh / float(p_el_rated_mw)
    op_hours_h = int(np.sum(p > 0))
    op_hours_above_min_h = int(np.sum(p >= p_min))
    full_hours_count_h = int(np.sum(p >= (0.999 * p_el_rated_mw)))
    cf = energy_mwh / (float(p_el_rated_mw) * len(p)) if len(p) > 0 else np.nan

    return {
        "EL_energy_MWh": energy_mwh,
        "EL_full_load_hours_equiv_h": flh_equiv_h,
        "EL_operating_hours_h": op_hours_h,
        "EL_operating_hours_above_min_h": op_hours_above_min_h,
        "EL_full_load_hours_count_h": full_hours_count_h,
        "capacity_factor_avg": cf,
        "P_el_rated_MW": float(p_el_rated_mw),
        "P_el_min_MW": float(p_min),
        "n_hours": int(len(p)),
    }

# -----------------------------
# ANWENDUNG AUF DEIN SETUP
# -----------------------------
# 1) Jahresdauerlinie für Wind (Sizing-Annäherung)
#    -> nutze dein df2 (1 Jahr) und ggf. s
s_for_plot = float(winner["s"]) if "winner" in globals() else 1.0
p_el_rated = float(winner["P_el_MW"]) if "winner" in globals() else 1000.0

p_wind_year = (df2["p_mw"].values * s_for_plot)  # MW, 1 Jahr

sizing_kpis = duration_curve_sizing(
    p_wind_year,
    p_el_rated_mw=p_el_rated,
    p_el_min_frac=float(cost_params["h2"]["electrolyzer"][str(winner["tech"]).upper()]["min_load_frac"])
        if "winner" in globals() else 0.05,
    title=f"Jahresdauerlinie + Elektrolyseur (s={s_for_plot:.2f}, P_el={p_el_rated:.0f} MW)"
)

print("\n--- Sizing aus Jahresdauerlinie (Wind -> EL direkt) ---")
for k,v in sizing_kpis.items():
    if "hours" in k or "h" in k:
        pass
print(sizing_kpis)

# 2) Echte Vollaststunden/Betriebsstunden aus Simulation (falls out_winner vorhanden)
if "out_winner" in globals() and out_winner is not None and "p_el_mw" in out_winner.columns:
    sim_kpis = electrolyzer_hours_from_timeseries(
        out_winner["p_el_mw"].values,
        p_el_rated_mw=p_el_rated,
        p_el_min_frac=float(cost_params["h2"]["electrolyzer"][str(winner["tech"]).upper()]["min_load_frac"])
            if "winner" in globals() else 0.05,
    )
    print("\n--- Aus Simulation (out_winner['p_el_mw']) ---")
    print(sim_kpis)
else:
    print("\nHinweis: out_winner['p_el_mw'] nicht gefunden -> Sim-KPIs werden übersprungen.")


# %%
# %%
# %% Tabelle: Elektrolyse-Auslegung aus Jahresdauerlinie

sizing_table = pd.DataFrame({
    "Kennzahl": [
        "Elektrolyse-Nennleistung",
        "Mindestlast",
        "Jahresenergie Elektrolyse",
        "Rechnerische Vollaststunden",
        "Betriebsstunden",
        "Vollaststunden (Wind >= P_el)",
        "Teillaststunden"
    ],
    "Wert": [
        f"{sizing_kpis['P_el_rated_MW']:.0f} MW",
        f"{sizing_kpis['P_el_min_MW']:.1f} MW",
        f"{sizing_kpis['EL_energy_MWh_per_year_equiv']:.0f} MWh/a",
        f"{sizing_kpis['EL_full_load_hours_equiv_h']:.0f} h/a",
        f"{sizing_kpis['EL_operating_hours_h']} h/a",
        f"{sizing_kpis['EL_full_load_hours_count_h']} h/a",
        f"{sizing_kpis['EL_part_load_hours_h']} h/a",
    ]
})

display(sizing_table)



# %%
# %% Energieübersicht (Winner) – NUR Technologienamen + gestapeltes Säulendiagramm inkl. Curtailment
# Erwartet: kpi_w (aus simulate_hourly_system)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display

def energy_breakdown_grouped(kpi_w: dict) -> pd.DataFrame:
    # Direktverbraucher
    el_mwh = float(kpi_w.get("EL_el_MWh_per_sim", 0.0))
    ro_mwh = float(kpi_w.get("RO_el_MWh_per_sim", 0.0))
    hb_mwh = float(kpi_w.get("HB_el_MWh_per_sim", 0.0))
    n2_mwh = float(kpi_w.get("N2_el_MWh_per_sim", 0.0))

    # Speicher-Hilfsstrom: IN + OUT zusammenfassen (aber Label bleibt nur Technologie)
    h2_store_mwh = float(kpi_w.get("H2_store_in_MWh_per_sim", 0.0)) + float(kpi_w.get("H2_store_out_MWh_per_sim", 0.0))
    nh3_store_mwh = float(kpi_w.get("NH3_store_in_MWh_per_sim", 0.0)) + float(kpi_w.get("NH3_store_out_MWh_per_sim", 0.0))

    # Curtailment (nicht genutzt)
    curt_mwh = float(kpi_w.get("curtail_GWh_per_sim", 0.0)) * 1000.0

    rows = [
        ("Elektrolyseur", el_mwh),
        ("Umkehrosmose", ro_mwh),
        ("Haber-Bosch", hb_mwh),
        ("N2-Aufbereitung", n2_mwh),
        ("H2-Speicher", h2_store_mwh),
        ("NH3-Speicher", nh3_store_mwh),
        ("Ungenutzt", curt_mwh),
    ]
    dfE = pd.DataFrame(rows, columns=["Technologie", "Energie_MWh"])
    dfE["Energie_GWh"] = dfE["Energie_MWh"] / 1000.0

    used_mwh = dfE.loc[dfE["Technologie"] != "Ungenutzt", "Energie_MWh"].sum()
    total_mwh = used_mwh + curt_mwh

    dfE["Anteil_an_Gesamt_%"] = np.where(total_mwh > 0, 100.0 * dfE["Energie_MWh"] / total_mwh, 0.0)

    summary = pd.DataFrame([
        ("SUMME genutzt", used_mwh, used_mwh/1000.0, 100.0 * used_mwh/total_mwh if total_mwh > 0 else 0.0),
        ("SUMME Curtailment", curt_mwh, curt_mwh/1000.0, 100.0 * curt_mwh/total_mwh if total_mwh > 0 else 0.0),
        ("SUMME Erzeugung", total_mwh, total_mwh/1000.0, 100.0),
    ], columns=["Technologie", "Energie_MWh", "Energie_GWh", "Anteil_an_Gesamt_%"])

    return dfE, summary

def plot_stacked_energy_grouped(dfE: pd.DataFrame, title="Energieverteilung (gestapelt)"):
    order = [
        "Elektrolyseur",
        "Umkehrosmose",
        "Haber-Bosch",
        "N2-Aufbereitung",
        "H2-Speicher",
        "NH3-Speicher",
        "Ungenutzt",
    ]
    dfP = dfE.set_index("Technologie").loc[order].reset_index()
    vals = dfP["Energie_GWh"].values

    plt.figure(figsize=(9, 5))
    bottom = 0.0
    for name, v in zip(dfP["Technologie"], vals):
        plt.bar(["Winner"], [v], bottom=bottom, label=name)
        bottom += v

    plt.ylabel("Energie [GWh pro Simulation]")
    plt.title(title)
    plt.grid(True, axis="y")
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.show()

# --- Ausführen ---
dfE_g, summaryE_g = energy_breakdown_grouped(kpi_w)

print("Energie (gruppiert, aus KPI-Summen):")
display(dfE_g.sort_values("Energie_MWh", ascending=False).reset_index(drop=True))

print("\nZusammenfassung:")
display(summaryE_g)

plot_stacked_energy_grouped(dfE_g, title="Energieverteilung")


# %%
# %% KOSTEN-EXTRABLOCK (Winner): Tabelle (formatiert ohne Exponenten) + gestapelte CAPEX/OPEX Säulen + Kuchendiagramme
# Erwartet: `winner` (eine Zeile/Series aus deinem Raster mit den Kostenfeldern)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display

def fmt_money(x):
    x = float(x)
    if x >= 1e9: return f"{x/1e9:.2f} Mrd. $"
    if x >= 1e6: return f"{x/1e6:.1f} Mio. $"
    if x >= 1e3: return f"{x/1e3:.1f} Tsd. $"
    return f"{x:.0f} $"

def cost_breakdown_from_winner(winner) -> pd.DataFrame:
    components = [
        "Windpark",
        "Elektrolyseur",
        "H2-Speicher",
        "N2-Aufbereitung",
        "Haber-Bosch",
        "Umkehrosmose (RO)",
        "Wassertank",
        "NH3-Speicher",
    ]

    capex = [
        float(winner.get("Wind_CAPEX", 0.0)),
        float(winner.get("EL_CAPEX", 0.0)),
        float(winner.get("H2_STORE_CAPEX", 0.0)),
        float(winner.get("N2_CAPEX", 0.0)),
        float(winner.get("HB_CAPEX", 0.0)),
        float(winner.get("RO_CAPEX", 0.0)),
        float(winner.get("WATER_TANK_CAPEX", 0.0)),
        float(winner.get("NH3_STORE_CAPEX", 0.0)),
    ]

    opex = [
        float(winner.get("Wind_OPEX", 0.0)),
        float(winner.get("EL_OPEX_total", 0.0)),
        float(winner.get("H2_STORE_OPEX_total", 0.0)),
        float(winner.get("N2_OPEX_total", 0.0)),
        float(winner.get("HB_OPEX_total", 0.0)),
        float(winner.get("RO_OPEX_total", 0.0)),
        float(winner.get("WATER_TANK_OPEX_total", 0.0)),
        float(winner.get("NH3_STORE_OPEX_total", 0.0)),
    ]

    dfC = pd.DataFrame({
        "Komponente": components,
        "CAPEX_$": capex,
        "OPEX_$": opex,
    })
    dfC["Total_$"] = dfC["CAPEX_$"] + dfC["OPEX_$"]

    total = dfC["Total_$"].sum()
    dfC["Anteil_Total_%"] = np.where(total > 0, 100.0 * dfC["Total_$"] / total, 0.0)

    cap_total = dfC["CAPEX_$"].sum()
    op_total  = dfC["OPEX_$"].sum()
    dfC["Anteil_CAPEX_%"] = np.where(cap_total > 0, 100.0 * dfC["CAPEX_$"] / cap_total, 0.0)
    dfC["Anteil_OPEX_%"]  = np.where(op_total > 0, 100.0 * dfC["OPEX_$"] / op_total, 0.0)

    return dfC

def plot_costs_stacked_bars(dfC: pd.DataFrame, sort_by="Total_$"):
    dfP = dfC.sort_values(sort_by, ascending=False).reset_index(drop=True)

    x = np.arange(len(dfP))
    cap = dfP["CAPEX_$"].values
    op  = dfP["OPEX_$"].values

    plt.figure(figsize=(12, 5))
    plt.bar(x, cap, label="CAPEX")
    plt.bar(x, op, bottom=cap, label="OPEX (über Laufzeit)")
    plt.xticks(x, dfP["Komponente"], rotation=20, ha="right")
    plt.ylabel("Kosten [$]")
    plt.title("Kostenstruktur (gestapelt): CAPEX + OPEX je Komponente")
    plt.grid(True, axis="y")
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_cost_pies(dfC: pd.DataFrame, min_share_pct=2.0):
    def compress(values, labels, min_share):
        total = float(np.sum(values))
        if total <= 0:
            return values, labels
        share = 100.0 * np.array(values) / total
        keep = share >= min_share
        if np.all(keep):
            return np.array(values), list(labels)
        rest = float(np.sum(np.array(values)[~keep]))
        new_vals = list(np.array(values)[keep])
        new_labs = list(np.array(labels)[keep])
        if rest > 0:
            new_vals.append(rest)
            new_labs.append("Sonstiges")
        return np.array(new_vals), new_labs

    labels = dfC["Komponente"].values

    cap_vals, cap_labs = compress(dfC["CAPEX_$"].values, labels, min_share_pct)
    plt.figure(figsize=(7, 7))
    plt.pie(cap_vals, labels=cap_labs, autopct="%1.1f%%")
    plt.title("CAPEX-Verteilung (Kuchendiagramm)")
    plt.tight_layout()
    plt.show()

    op_vals, op_labs = compress(dfC["OPEX_$"].values, labels, min_share_pct)
    plt.figure(figsize=(7, 7))
    plt.pie(op_vals, labels=op_labs, autopct="%1.1f%%")
    plt.title("OPEX-Verteilung (Kuchendiagramm, über Laufzeit)")
    plt.tight_layout()
    plt.show()

# --- Ausführen ---
dfC = cost_breakdown_from_winner(winner)

print("Kostenübersicht (Winner):")

# -> Hier kommt der Trick: nur für die Anzeige formatieren (Strings), Daten bleiben in dfC numerisch für Plots
dfC_disp = dfC.copy()
for col in ["CAPEX_$", "OPEX_$", "Total_$"]:
    dfC_disp[col] = dfC_disp[col].map(fmt_money)

# Prozente hübsch runden
for col in ["Anteil_Total_%", "Anteil_CAPEX_%", "Anteil_OPEX_%"]:
    dfC_disp[col] = dfC_disp[col].map(lambda v: f"{float(v):.1f} %")

display(dfC_disp.sort_values("Total_$", ascending=False).reset_index(drop=True))

cap_sum = dfC["CAPEX_$"].sum()
op_sum  = dfC["OPEX_$"].sum()
tot_sum = dfC["Total_$"].sum()
print("SUM CAPEX:", fmt_money(cap_sum), "| SUM OPEX:", fmt_money(op_sum), "| SUM Total:", fmt_money(tot_sum))

plot_costs_stacked_bars(dfC, sort_by="Total_$")
plot_cost_pies(dfC, min_share_pct=2.0)


# %%
import numpy as np
import matplotlib.pyplot as plt

def plot_electrolyzer_loadline_percent_one_year(
    out_ts,
    p_el_rated_mw: float,
    year_index: int = 0,
    hours_per_year: int = 8760
):
    """
    Elektrolyseur-Lastlinie über 1 Jahr
    Y-Achse: Leistung in % der Nennleistung
    """
    start = int(year_index * hours_per_year)
    end   = int(start + hours_per_year)

    out1 = out_ts.iloc[start:end].copy()
    if len(out1) == 0:
        raise ValueError("Ausgewähltes Jahr hat keine Daten.")

    if "p_el_mw" not in out1.columns:
        raise KeyError("Spalte 'p_el_mw' fehlt in out_ts.")

    p_el = out1["p_el_mw"].to_numpy(dtype=float)
    p_el = np.clip(p_el, 0.0, None)

    if p_el_rated_mw <= 0:
        raise ValueError("p_el_rated_mw muss > 0 sein.")

    # Umrechnung in %
    p_el_pct = 100.0 * p_el / float(p_el_rated_mw)

    t = np.arange(len(p_el_pct))

    plt.figure(figsize=(13,5))
    plt.plot(t, p_el_pct)
    plt.ylim(0, 105)
    plt.xlabel("Stunde im Jahr [h]")
    plt.ylabel("Elektrolyseur-Leistung [% von Pₙ]")
    plt.title(f"Elektrolyseur-Lastlinie über 1 Jahr (Jahr {year_index+1})")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Kennzahlen (weiterhin sinnvoll)
    on_hours = int(np.sum(p_el > 1e-6))
    energy_mwh = float(np.sum(p_el))
    flh_equiv = energy_mwh / float(p_el_rated_mw)

    print(f"--- Elektrolyseur Kennzahlen (Jahr {year_index+1}) ---")
    print(f"Nennleistung: {p_el_rated_mw:.1f} MW")
    print(f"Betriebsstunden (P>0): {on_hours} h/a")
    print(f"Energie: {energy_mwh:.0f} MWh/a")
    print(f"Rechnerische Vollaststunden: {flh_equiv:.0f} h/a")

# Anwendung (Winner, erstes Jahr)
plot_electrolyzer_loadline_percent_one_year(
    out_winner,
    p_el_rated_mw=float(winner["P_el_MW"]),
    year_index=0,
    hours_per_year=8760
)


# %%
import numpy as np
import matplotlib.pyplot as plt

def plot_electrolyzer_duration_curve_percent_avg_year(
    out_ts,
    p_el_rated_mw: float,
    hours_per_year: int = 8760,
    n_points: int = 8760
):
    """
    Elektrolyseur-Dauerlinie in % als "durchschnittliches Jahr" über die gesamte Projektlaufzeit.
    Vorgehen:
    - alle Stunden der Simulation -> p_el [%]
    - sortieren absteigend
    - auf 8760 Punkte per Quantilen resamplen (typischer Jahresverlauf der Dauerlinie)
    """
    if "p_el_mw" not in out_ts.columns:
        raise KeyError("Spalte 'p_el_mw' fehlt in out_ts.")
    if p_el_rated_mw <= 0:
        raise ValueError("p_el_rated_mw muss > 0 sein.")

    p_el = out_ts["p_el_mw"].to_numpy(dtype=float)
    p_el = np.clip(p_el, 0.0, None)

    # in %
    p_pct = 100.0 * p_el / float(p_el_rated_mw)

    # sortiert (hoch -> runter) über gesamte Laufzeit
    p_sorted = np.sort(p_pct)[::-1]

    # Simulationsdauer
    n_hours = len(p_sorted)
    sim_years_est = n_hours / float(hours_per_year) if n_hours > 0 else np.nan

    # "typisches Jahr" als Quantil-Kurve mit 8760 Punkten
    # x_frac läuft von 0..1: 0 = höchste Laststunden, 1 = niedrigste
    x_frac = (np.arange(n_points) + 0.5) / n_points
    idx = np.clip((x_frac * n_hours).astype(int), 0, n_hours - 1)
    p_avg_year = p_sorted[idx]

    # Plot
    x = np.arange(n_points)
    plt.figure(figsize=(11,5))
    plt.plot(x, p_avg_year)
    plt.ylim(0, 105)
    plt.xlabel("Stunden [h/a] (sortiert) – durchschnittliches Jahr")
    plt.ylabel("Elektrolyseur-Leistung [% von Pₙ]")
    plt.title(f"Elektrolyseur-Dauerlinie (gemittelt über {sim_years_est:.1f} Jahre)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Kennzahlen (pro Jahr im Mittel, aus der avg-year Kurve)
    full_load_hours = int(np.sum(p_avg_year >= 99.0))
    operating_hours = int(np.sum(p_avg_year > 0.0))
    flh_equiv = float(np.sum(p_avg_year) / 100.0)  # weil 1 Punkt ~ 1h im Jahr

    print("--- Gemittelte Jahres-Kennzahlen (aus Dauerlinie) ---")
    print(f"Simulationsdauer: {sim_years_est:.2f} a ({n_hours} h)")
    print(f"Nennleistung: {p_el_rated_mw:.1f} MW")
    print(f"Betriebsstunden (P>0): {operating_hours} h/a")
    print(f"Vollaststunden (≥99 %): {full_load_hours} h/a")
    print(f"Rechnerische Vollaststunden: {flh_equiv:.0f} h/a")

# Anwendung:
plot_electrolyzer_duration_curve_percent_avg_year(
    out_winner,
    p_el_rated_mw=float(winner["P_el_MW"]),
    hours_per_year=8760,
    n_points=8760
)


# %%
# %% RO- und ASU-Kapazität (pro Tag) sauber ausgeben
# Erwartet: out_winner (DataFrame mit stündlichen Werten) und kpi_w (dict)

import numpy as np

def _first_existing(d: dict, keys):
    for k in keys:
        if k in d and d[k] is not None:
            return d[k], k
    return None, None

def print_ro_asu_capacity_per_day(out_winner, kpi_w):
    # -------------------------
    # RO (m3/day)
    # -------------------------
    ro_val, ro_key = _first_existing(kpi_w, [
        "RO_capacity_m3_per_day",
        "ro_m3_per_day_design",
        "ro_cap_m3_per_day",
        "RO_m3_per_day",
        "RO_m3_per_d"
    ])

    ro_from_ts = None
    ro_ts_col = None
    # Falls RO nicht im KPI steckt: aus Timeseries ableiten (Design = max stündlich * 24)
    for c in ["RO_m3_per_h", "ro_m3_per_h", "water_ro_m3_per_h", "ro_flow_m3_per_h"]:
        if c in out_winner.columns:
            ro_ts_col = c
            ro_from_ts = float(np.nanmax(out_winner[c].to_numpy()) * 24.0)
            break

    # -------------------------
    # ASU / N2 (t/day)
    # -------------------------
    asu_val, asu_key = _first_existing(kpi_w, [
        "ASU_capacity_tN2_per_day",
        "asu_tN2_per_day_design",
        "N2_capacity_t_per_day",
        "n2_t_per_day_design",
        "ASU_t_per_day"
    ])

    asu_from_ts = None
    asu_ts_col = None
    # Falls ASU nicht im KPI steckt: aus N2-Production Timeseries ableiten (max stündlich -> t/day)
    # Hinweis: oft ist die Spalte in kg/h. Dann: *24 / 1000.
    for c in ["N2_kg_per_h", "n2_kg_per_h", "asu_n2_kg_per_h", "N2_prod_kg_per_h"]:
        if c in out_winner.columns:
            asu_ts_col = c
            asu_from_ts = float(np.nanmax(out_winner[c].to_numpy()) * 24.0 / 1000.0)
            break
    # Alternative falls du schon t/h speicherst:
    if asu_from_ts is None:
        for c in ["N2_t_per_h", "n2_t_per_h", "asu_n2_t_per_h"]:
            if c in out_winner.columns:
                asu_ts_col = c
                asu_from_ts = float(np.nanmax(out_winner[c].to_numpy()) * 24.0)
                break

    # -------------------------
    # Ausgabe (Priorität: KPI > Timeseries)
    # -------------------------
    print("\n--- Kapazitäten (Design) ---")

    if ro_val is not None:
        print(f"RO-Kapazität:  {float(ro_val):,.2f} m³/d  (aus KPI: {ro_key})")
    elif ro_from_ts is not None:
        print(f"RO-Kapazität:  {ro_from_ts:,.2f} m³/d  (aus Timeseries: max({ro_ts_col})*24)")
    else:
        print("RO-Kapazität:  NICHT GEFUNDEN (weder in kpi_w noch als bekannte Timeseries-Spalte)")

    if asu_val is not None:
        print(f"ASU/N₂-Kapazität: {float(asu_val):,.2f} tN₂/d  (aus KPI: {asu_key})")
    elif asu_from_ts is not None:
        print(f"ASU/N₂-Kapazität: {asu_from_ts:,.2f} tN₂/d  (aus Timeseries: max({asu_ts_col}) auf Tagesbasis)")
    else:
        print("ASU/N₂-Kapazität: NICHT GEFUNDEN (weder in kpi_w noch als bekannte Timeseries-Spalte)")

# Call
print_ro_asu_capacity_per_day(out_winner, kpi_w)



