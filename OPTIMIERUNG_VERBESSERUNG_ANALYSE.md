# Optimierungsverbesserung: Detaillierte Analyse

## Command 1 – Bessere Entscheidungsvariablen

### Aktuelle Entscheidungsvariablen (aus Code_Final.py Zeilen 887-892):
- `s`: Wind-Skalierungsfaktor (0.95 - 1.00)
- `p_el_mw`: Elektrolyseur-Leistung (1000 - 1200 MW)
- `h2_storage_days`: H₂-Speicher in Tagen (1 - 2 Tage)
- `nh3_storage_ships`: NH₃-Speicher in Schiffs-Ladungen (1.0 - 1.5)
- `water_tank_m3`: Wassertank-Größe (500 - 4500 m³)
- `technology`: Elektrolyse-Technologie (AEL/PEM) - **nur binär, nicht optimiert**

### ❌ Fehlende Entscheidungsvariablen:

#### 1.1 Elektrolyse-Lastprofile & Betriebsstrategie
- **`el_operating_strategy`**: 
  - `"wind_following"` (folgt Windprofil)
  - `"constant_load"` (konstante Last)
  - `"peak_shaving"` (Spitzenlastreduktion)
  - `"storage_optimized"` (Speicher-optimiert)
- **`el_min_load_frac`**: Variable Mindestlast (aktuell fix: AEL=0.20, PEM=0.05)
- **`el_max_load_frac`**: Maximale Auslastung (aktuell implizit 1.0)
- **`el_availability`**: Verfügbarkeit des Elektrolyseurs (aktuell nicht variiert, sollte 0.90-0.98 sein)

#### 1.2 Teillastverluste & Effizienz
- **`el_part_load_efficiency_curve`**: 
  - Polynom-Koeffizienten für Teillastverluste: `η(P/P_nom) = a₀ + a₁·(P/P_nom) + a₂·(P/P_nom)²`
  - Aktuell: Linear angenommen, real: quadratische Verluste bei <50% Last
- **`el_degradation_rate`**: Jährliche Degradation (z.B. 0.5-2% pro Jahr)
- **`el_lifetime_extension`**: Lebensdauerverlängerung durch Betriebsstrategie

#### 1.3 Skalierungsgesetze für CAPEX
- **`capex_scaling_exponent`**: 
  - Elektrolyseur: aktuell linear (1.0), real: 0.85-0.95 (Economies of Scale)
  - H₂-Speicher: aktuell linear, real: 0.80-0.90
  - NH₃-Speicher: aktuell linear, real: 0.75-0.85
  - RO-Anlage: aktuell linear, real: 0.70-0.85
- **`learning_curve_factor`**: Technologie-Lernkurve (z.B. 0.90-0.95 pro Verdopplung)

#### 1.4 Abhängigkeiten Wind ↔ Elektrolyse
- **`wind_el_ratio`**: Verhältnis Windkapazität zu Elektrolyseur-Kapazität (aktuell fix ~2.47 GW / 1-1.2 GW)
  - Sollte variiert werden: 1.5 - 3.5 (zu wenig Wind = hohe Curtailment, zu viel = teuer)
- **`curtailment_tolerance`**: Maximale akzeptierte Curtailment-Rate (z.B. 5-20%)
- **`grid_export_capacity`**: Exportkapazität ins Netz (MW) - ermöglicht Verkauf von Überschussstrom

#### 1.5 Haber-Bosch Betriebsparameter
- **`hb_operating_strategy`**: 
  - `"continuous"` (kontinuierlich)
  - `"batch"` (Chargenbetrieb)
  - `"load_following"` (Lastfolge)
- **`hb_min_load_frac`**: Mindestlast HB (aktuell fix 0.40)
- **`hb_availability`**: Verfügbarkeit HB (aktuell fix 0.94)

#### 1.6 Transport-Logistik
- **`ships_per_year`**: Anzahl Schiffe pro Jahr (aktuell fix 12)
- **`ship_payload_factor`**: Auslastungsfaktor der Schiffe (aktuell implizit 1.0)
- **`transport_distance_km`**: Transportdistanz (aktuell nicht optimiert)
- **`port_time_days`**: Hafenliegezeit (aktuell nicht variiert)

#### 1.7 Speicher-Strategien
- **`h2_soc_control_strategy`**: 
  - `"conservative"` (hohe Reserve)
  - `"aggressive"` (niedrige Reserve)
  - `"adaptive"` (anpassend)
- **`nh3_soc_target_level`**: Ziel-SOC für NH₃ (aktuell fix 1.2 Schiffe)
- **`storage_reserve_fraction`**: Reserve-Anteil (z.B. 0.10-0.30)

---

## Command 2 – Nebenbedingungen (Constraints)

### Aktuelle Constraints (aus Code_Final.py):
- ✅ `ships_failed_count == 0` (keine fehlgeschlagenen Schiffe)
- ✅ `nh3_prod_total_t >= nh3_target_total_t - 1e-9` (Produktionsziel erreicht)
- ✅ `soc_nh3_t <= nh3_storage_t_max` (keine Speicher-Überläufe)
- ✅ `soc_h2_kg <= h2_storage_kg_max` (keine Speicher-Überläufe)

### ❌ Fehlende physikalische Constraints:

#### 2.1 Maximale Rampenraten
- **`el_ramp_rate_max`**: 
  - Aktuell: `el_ramp_frac_per_h = 0.80` (80% pro Stunde) - **zu hoch!**
  - Realistisch: 5-20% pro Stunde für große Anlagen
  - Constraint: `|P_el(t) - P_el(t-1)| ≤ ramp_rate_max * P_el_nom`
- **`hb_ramp_rate_max`**: 
  - Aktuell: `hb_ramp_frac_per_h = 0.10` (10% pro Stunde)
  - Realistisch: 3-10% pro Stunde
- **`h2_storage_ramp_rate`**: Maximale Ein-/Ausspeicherrate (kg/h)

#### 2.2 Start/Stop-Limits
- **`el_min_operating_hours`**: Mindestbetriebsdauer nach Start (z.B. 4-24 h)
- **`el_max_starts_per_year`**: Maximale Startzyklen (z.B. 100-500 Starts/a)
- **`el_startup_cost`**: Startkosten pro Zyklus (€/Start)
- **`hb_min_operating_hours`**: Mindestbetriebsdauer HB (z.B. 8-48 h)
- **`hb_warmup_time_hours`**: Aufwärmzeit HB (z.B. 2-8 h)

#### 2.3 Mindestvollbenutzungsstunden
- **`el_min_full_load_hours`**: Mindest-Vollaststunden für Wirtschaftlichkeit (z.B. 2000-4000 h/a)
- **`hb_min_full_load_hours`**: Mindest-Vollaststunden HB (z.B. 6000-8000 h/a)
- **`el_capacity_factor_min`**: Mindest-Kapazitätsfaktor (z.B. 0.30-0.50)

#### 2.4 Speicher-Reserveanforderungen
- **`h2_reserve_fraction_min`**: Mindest-Reserve im H₂-Speicher (z.B. 0.10-0.30)
- **`nh3_reserve_fraction_min`**: Mindest-Reserve im NH₃-Speicher (z.B. 0.20-0.40)
- **`water_reserve_fraction_min`**: Mindest-Reserve im Wassertank (z.B. 0.10-0.25)
- **`emergency_reserve_days`**: Notfall-Reserve in Tagen (z.B. 1-3 Tage)

#### 2.5 Hafen- und Transportrestriktionen
- **`port_capacity_constraint`**: Maximale Schiffsanzahl gleichzeitig im Hafen (z.B. 1-2 Schiffe)
- **`ship_loading_time_min`**: Mindest-Beladezeit (z.B. 12-48 h)
- **`ship_interval_min`**: Mindest-Abstand zwischen Schiffsankünften (z.B. 20-30 Tage)
- **`transport_window_seasonal`**: Saisonale Transportfenster (z.B. keine Transporte bei Eis)

#### 2.6 Betriebliche Constraints
- **`curtailment_max_fraction`**: Maximale akzeptierte Curtailment-Rate (z.B. 0.05-0.20)
- **`grid_export_max_mw`**: Maximale Exportkapazität ins Netz
- **`water_shortage_max_fraction`**: Maximale akzeptierte Wasserknappheit (z.B. 0.01-0.05)
- **`h2_purity_min`**: Mindest-H₂-Reinheit (z.B. 99.5-99.99%)

#### 2.7 Wirtschaftliche Constraints
- **`irr_min`**: Mindest-IRR (z.B. 5-10%)
- **`npv_min`**: Mindest-NPV (z.B. > 0 oder > Investitionssumme)
- **`payback_period_max`**: Maximale Amortisationszeit (z.B. 10-15 Jahre)
- **`debt_service_coverage_ratio_min`**: Mindest-DSCR (z.B. 1.2-1.5)

#### 2.8 Technische Constraints
- **`el_power_range`**: Leistungsbereich (z.B. 100-2000 MW pro Einheit)
- **`storage_size_min`**: Minimale Speichergröße (z.B. 1 Tag Produktion)
- **`storage_size_max`**: Maximale Speichergröße (z.B. 30 Tage Produktion)
- **`ro_capacity_max`**: Maximale RO-Kapazität (z.B. begrenzt durch Standort)

---

## Command 3 – Zielgröße verbessern

### Aktuelle Zielfunktion:
- **Minimiere**: `€/kg H₂` (total cost per kg)

### ❌ Alternative/Ergänzende Zielfunktionen:

#### 3.1 CAPEX-Risiko
- **`minimize_capex_risk`**: 
  - Zielfunktion: `w₁·(€/kg) + w₂·(CAPEX_Variabilität)`
  - CAPEX-Variabilität = Standardabweichung der CAPEX-Komponenten
  - Gewichtung: `w₁ = 0.7`, `w₂ = 0.3`
- **`minimize_max_capex_component`**: Minimiere die größte CAPEX-Komponente (Risikodiversifikation)

#### 3.2 Systemeffizienz
- **`maximize_system_efficiency`**: 
  - Zielfunktion: `η_system = H₂_delivered / (Wind_energy_total)`
  - Oder: `minimize_energy_losses` (Curtailment + Speicherverluste + Prozessverluste)
- **`maximize_chain_efficiency`**: 
  - `η_chain = H₂_delivered / H₂_produced`
  - Berücksichtigt alle Verluste entlang der Kette

#### 3.3 Volllaststunden
- **`maximize_el_full_load_hours`**: 
  - Höhere Volllaststunden = bessere Auslastung = niedrigere spezifische Kosten
  - Zielfunktion: `minimize(€/kg / FLH_factor)`
- **`minimize_idle_capacity_cost`**: Minimiere Kosten für ungenutzte Kapazität

#### 3.4 Sensitivität gegenüber Strompreisen
- **`minimize_electricity_price_sensitivity`**: 
  - Zielfunktion: `∂(€/kg) / ∂(Strompreis)` minimieren
  - Oder: `minimize_cost_at_price_range` (Kosten bei ±30% Strompreisvariation)
- **`maximize_price_resilience`**: 
  - Robustheit gegenüber Strompreisschwankungen
  - Zielfunktion: `minimize(max_cost - min_cost)` über Preis-Szenarien

#### 3.5 CO₂-Intensität
- **`minimize_co2_intensity`**: 
  - `g CO₂ / kg H₂` minimieren
  - Berücksichtigt: Wind-LCA, Elektrolyse-LCA, Transport-LCA
- **`maximize_renewable_share`**: 
  - Anteil erneuerbarer Energie maximieren

#### 3.6 Multi-Objective Optimierung
- **Pareto-Optimierung** mit mehreren Zielen:
  1. `minimize(€/kg H₂)`
  2. `minimize(CAPEX_Risiko)`
  3. `maximize(Systemeffizienz)`
  4. `minimize(CO₂-Intensität)`
- **Gewichtete Summe**: `w₁·€/kg + w₂·CAPEX_Risk + w₃·(1/η) + w₄·CO₂`

#### 3.7 Robustheit & Stabilität
- **`minimize_cost_variance`**: 
  - Minimiere Varianz der Kosten über verschiedene Szenarien
- **`maximize_configuration_stability`**: 
  - Optimum sollte stabil sein bei kleinen Parameteränderungen
  - Zielfunktion: `minimize(|∂(€/kg)/∂(Parameter)|)`

---

## Command 4 – Suchraum verbessern

### Aktuelle Methode:
- **Brute-Force Grid Search**: Alle Kombinationen werden getestet
- **540 Kombinationen** (6×5×2×3×3)

### ❌ Verbesserungsvorschläge:

#### 4.1 Hierarchische Optimierung (2-Stufen)
**Stufe 1: Grober Raster-Sweep**
- Grobe Schritte: `s: [0.95, 1.0]` (Schritt 0.05), `P_el: [1000, 1200]` (Schritt 200)
- **~18 Kombinationen** → Identifiziert grobe Optima

**Stufe 2: Feiner Raster um Optima**
- Feine Schritte um beste Konfigurationen: `s: [opt-0.02, opt+0.02]` (Schritt 0.01), `P_el: [opt-100, opt+100]` (Schritt 25)
- **~100-200 Kombinationen** → Verfeinert Optima

**Vorteil**: Reduziert von 540 auf ~200 Kombinationen bei besserer Auflösung

#### 4.2 Vorfilterung technisch unrealistischer Konfigurationen
**Pre-Filter vor Optimierung:**
```python
# Filter 1: Wind-EL-Verhältnis
if wind_capacity / p_el < 1.5 or wind_capacity / p_el > 3.5:
    skip_configuration()

# Filter 2: Speicher-Größen-Verhältnis
if h2_storage_days < 0.5 or h2_storage_days > 10:
    skip_configuration()

# Filter 3: Produktionsziel erreichbar?
if p_el * 8760 * capacity_factor * el_efficiency < h2_target * 1.1:
    skip_configuration()

# Filter 4: Curtailment zu hoch?
if estimated_curtailment > 0.30:
    skip_configuration()
```

**Vorteil**: Reduziert Suchraum um 30-50%

#### 4.3 Mehrstufige Optimierung

**Stufe 1: Design-Optimierung (Kapazitäten)**
- Variablen: `P_el`, `H2_storage`, `NH3_storage`, `Water_tank`
- Zielfunktion: `minimize(CAPEX_total)`
- Constraints: Produktionsziel erreichbar

**Stufe 2: Betriebs-Optimierung (Strategien)**
- Variablen: `el_operating_strategy`, `hb_operating_strategy`, `soc_targets`
- Zielfunktion: `minimize(OPEX_total + Variable_Costs)`
- Constraints: Design aus Stufe 1

**Stufe 3: Kosten-Optimierung (Gesamt)**
- Variablen: Alle Parameter
- Zielfunktion: `minimize(€/kg H₂)`
- Constraints: Design + Betrieb aus Stufe 1+2

**Vorteil**: Schnellere Konvergenz, bessere Lösungen

#### 4.4 Adaptive Raster-Verfeinerung
- Starte mit grobem Raster
- Identifiziere Regionen mit niedrigen Kosten
- Verfeinere Raster nur in diesen Regionen
- Iteriere bis Konvergenz

#### 4.5 Gradienten-basierte Methoden (falls möglich)
- **Finite Differences**: Approximiere Gradienten
- **Steepest Descent**: Folge Gradienten zum Optimum
- **Quasi-Newton**: BFGS oder L-BFGS für schnellere Konvergenz

**Problem**: Diskrete Variablen (Schiffe, Tage) → Mixed-Integer Programming nötig

#### 4.6 Heuristische Methoden
- **Simulated Annealing**: Starte mit zufälliger Konfiguration, akzeptiere schlechtere Lösungen mit abnehmender Wahrscheinlichkeit
- **Genetic Algorithm**: Evolutionsbasierte Suche
- **Particle Swarm Optimization**: Schwarm-basierte Suche

**Vorteil**: Kann lokale Minima überwinden

---

## Command 5 – Konfigurations-Clustering

### Ziel:
Ähnliche Konfigurationen identifizieren, um lokale Minima zu erkennen und stabile Optima zu finden.

### ✅ Geeignete KPIs für Clustering:

#### 5.1 Kosten-KPIs
- **`cost_per_kg`**: Primärer KPI (€/kg H₂)
- **`capex_total`**: Gesamt-CAPEX (M€)
- **`opex_total`**: Gesamt-OPEX (M€/a)
- **`variable_costs_total`**: Variable Kosten (M€/a)
- **`cost_structure_vector`**: Normalisierter Vektor `[CAPEX%, OPEX%, Variable%]`

#### 5.2 Technische KPIs
- **`el_capacity_factor`**: Kapazitätsfaktor Elektrolyseur (0-1)
- **`curtailment_fraction`**: Curtailment-Anteil (0-1)
- **`h2_storage_utilization`**: H₂-Speicher-Auslastung (0-1)
- **`nh3_storage_utilization`**: NH₃-Speicher-Auslastung (0-1)
- **`system_efficiency`**: Systemeffizienz `H₂_delivered / Wind_energy` (0-1)
- **`chain_efficiency`**: Ketteneffizienz `H₂_delivered / H₂_produced` (0-1)

#### 5.3 Betriebs-KPIs
- **`el_full_load_hours`**: Vollaststunden Elektrolyseur (h/a)
- **`hb_full_load_hours`**: Volllaststunden Haber-Bosch (h/a)
- **`el_starts_per_year`**: Startzyklen Elektrolyseur (#/a)
- **`hb_starts_per_year`**: Startzyklen Haber-Bosch (#/a)
- **`ships_failed_count`**: Fehlgeschlagene Schiffe (#)

#### 5.4 Design-KPIs (normalisiert)
- **`wind_el_ratio`**: Verhältnis Wind/EL (`wind_capacity / p_el`)
- **`h2_storage_days_normalized`**: H₂-Speicher in Tagen (normalisiert auf Produktion)
- **`nh3_storage_ships_normalized`**: NH₃-Speicher in Schiffs-Ladungen
- **`water_tank_normalized`**: Wassertank relativ zur Produktion (m³/kg H₂)

### Clustering-Methoden:

#### 5.1 K-Means Clustering
**Features**: 
- `[cost_per_kg, capex_total, opex_total, el_capacity_factor, curtailment_fraction, system_efficiency]`
- Normalisiert auf [0,1]

**Interpretation**:
- **Cluster 1**: Niedrige Kosten, hohe Effizienz → **Optimal**
- **Cluster 2**: Niedrige CAPEX, hohe OPEX → **CAPEX-optimiert**
- **Cluster 3**: Hohe CAPEX, niedrige OPEX → **OPEX-optimiert**
- **Cluster 4**: Hohe Kosten, niedrige Effizienz → **Suboptimal**

#### 5.2 Hierarchisches Clustering (Dendrogramm)
- Zeigt Ähnlichkeitshierarchie
- Identifiziert natürliche Gruppen
- Erkennt Ausreißer

#### 5.3 DBSCAN (Density-Based)
- Identifiziert dichte Regionen (stabile Optima)
- Erkennt Ausreißer (instabile Konfigurationen)
- Keine vordefinierte Cluster-Anzahl nötig

#### 5.4 PCA + Clustering
- Reduziert Dimensionalität (z.B. 10 KPIs → 3 Hauptkomponenten)
- Visualisierung in 2D/3D
- Clustering auf reduzierten Features

### Interpretation der Cluster:

#### Stabile Optima erkennen:
- **Hohe Dichte** in einem Cluster → Viele ähnliche Konfigurationen mit ähnlichen Kosten
- **Niedrige Varianz** der Kosten innerhalb eines Clusters → Robustes Optimum
- **Große Cluster** → Breites Optimum (weniger sensitiv)

#### Lokale Minima erkennen:
- **Kleine, isolierte Cluster** mit niedrigen Kosten → Lokales Minimum
- **Viele kleine Cluster** → Viele lokale Minima
- **Große Cluster mit hoher Varianz** → Flaches Optimum (viele ähnliche Lösungen)

#### Praktische Anwendung:
```python
# Beispiel-Clustering-Ergebnis:
Cluster 1 (n=45): cost_mean=0.894 €/kg, cost_std=0.002 → STABILES OPTIMUM
Cluster 2 (n=12): cost_mean=0.901 €/kg, cost_std=0.015 → LOKALES MINIMUM
Cluster 3 (n=8):  cost_mean=0.925 €/kg, cost_std=0.008 → SUBOPTIMAL
```

---

## Command 6 – Robustheitsprüfung (Sensitivitätsanalysen)

### Ziel:
Prüfen, ob die optimale Konfiguration stabil ist bei Parameteränderungen.

### ✅ Relevante Parameter und Variationsbereiche:

#### 6.1 Strompreis-Sensitivität
**Parameter**: `electricity_price` (€/kWh)
**Variationsbereich**: 
- **Basisfall**: 0.05 €/kWh (LCOE Wind)
- **Variation**: ±30% → [0.035, 0.065] €/kWh
- **Extrem**: ±50% → [0.025, 0.075] €/kWh

**Metrik**: 
- `∂(€/kg) / ∂(Strompreis)` → Sensitivitätskoeffizient
- `cost_range = max_cost - min_cost` → Kostenbandbreite

#### 6.2 Windkapazität-Sensitivität
**Parameter**: `wind_capacity` (MW) oder `s` (Skalierungsfaktor)
**Variationsbereich**:
- **Basisfall**: 2470 MW (s=1.0)
- **Variation**: ±10% → [2223, 2717] MW (s=[0.90, 1.10])
- **Extrem**: ±20% → [1976, 2964] MW (s=[0.80, 1.20])

**Metrik**:
- `∂(€/kg) / ∂(wind_capacity)`
- `curtailment_change` → Änderung der Curtailment-Rate

#### 6.3 Elektrolyseur-Kosten-Sensitivität
**Parameter**: `el_capex_per_kw` (€/kW)
**Variationsbereich**:
- **Basisfall**: 464 €/kW (AEL Standard)
- **Variation**: ±20% → [371, 557] €/kW
- **Extrem**: ±40% → [278, 650] €/kW (Technologie-Lernkurve)

**Metrik**:
- `∂(€/kg) / ∂(el_capex)`
- `capex_share_change` → Änderung des CAPEX-Anteils

#### 6.4 Speicher-Kosten-Sensitivität
**Parameter**: 
- `h2_storage_capex_per_t` (€/t H₂)
- `nh3_storage_capex_per_t` (€/t NH₃)

**Variationsbereich**:
- **H₂-Speicher**: ±30% → [23100, 42900] €/t
- **NH₃-Speicher**: ±30% → [567, 1053] €/t

**Metrik**:
- `∂(€/kg) / ∂(storage_capex)`
- `optimal_storage_size_change` → Änderung der optimalen Speichergröße

#### 6.5 Produktionsziel-Sensitivität
**Parameter**: `annual_h2_prod_t` (t/a)
**Variationsbereich**:
- **Basisfall**: 120800 t/a
- **Variation**: ±20% → [96640, 144960] t/a
- **Extrem**: ±50% → [60400, 181200] t/a

**Metrik**:
- `∂(€/kg) / ∂(production_target)` → Economies of Scale
- `optimal_p_el_change` → Änderung der optimalen EL-Leistung

#### 6.6 Diskontierungsrate-Sensitivität
**Parameter**: `discount_rate` (%)
**Variationsbereich**:
- **Basisfall**: 5%
- **Variation**: ±2% → [3%, 7%]
- **Extrem**: ±4% → [1%, 9%]

**Metrik**:
- `∂(€/kg) / ∂(discount_rate)`
- `npv_change` → Änderung des NPV

#### 6.7 Projektlebensdauer-Sensitivität
**Parameter**: `project_lifetime` (Jahre)
**Variationsbereich**:
- **Basisfall**: 20 Jahre
- **Variation**: ±5 Jahre → [15, 25] Jahre
- **Extrem**: ±10 Jahre → [10, 30] Jahre

**Metrik**:
- `∂(€/kg) / ∂(lifetime)`
- `capex_annualization_change` → Änderung der annualisierten CAPEX

#### 6.8 Technologie-Parameter-Sensitivität
**Parameter**:
- `el_efficiency` (kWh/kg H₂): ±5% → [45.6, 50.4] kWh/kg
- `hb_efficiency` (kWh/kg NH₃): ±10% → [0.495, 0.605] kWh/kg
- `cracking_efficiency` (%): ±5% → [90%, 100%]

**Metrik**:
- `∂(€/kg) / ∂(efficiency)`
- `energy_consumption_change` → Änderung des Energieverbrauchs

#### 6.9 Betriebsparameter-Sensitivität
**Parameter**:
- `el_availability`: ±5% → [0.90, 1.00]
- `hb_availability`: ±5% → [0.89, 0.99]
- `el_min_load_frac`: ±50% → [0.10, 0.30] (AEL)

**Metrik**:
- `∂(€/kg) / ∂(availability)`
- `production_loss_change` → Änderung der Produktionsverluste

#### 6.10 Transport-Kosten-Sensitivität
**Parameter**:
- `shipping_cost_per_t_nh3` (€/t): ±30%
- `fuel_cost_per_trip` (€): ±50%
- `transport_distance` (km): ±20%

**Metrik**:
- `∂(€/kg) / ∂(transport_cost)`
- `transport_cost_share_change` → Änderung des Transportkosten-Anteils

### Durchführung der Sensitivitätsanalyse:

#### Methode 1: One-at-a-Time (OAT)
- Variiere einen Parameter, halte alle anderen konstant
- Berechne Kostenänderung
- Wiederhole für alle Parameter

#### Methode 2: Monte-Carlo Simulation
- Ziehe Parameter aus Wahrscheinlichkeitsverteilungen
- Führe 1000-10000 Simulationen durch
- Analysiere Kostenverteilung

#### Methode 3: Tornado-Diagramm
- Sortiere Parameter nach Sensitivität
- Visualisiere Kostenbandbreite pro Parameter

#### Methode 4: Sobol-Indizes (Varianz-basiert)
- Quantifiziere Beitrag jedes Parameters zur Kostenvarianz
- Erkennt Interaktionen zwischen Parametern

### Robustheits-Metriken:

#### Stabilität des Optimums:
- **Kostenänderung < 5%** bei ±10% Parameteränderung → **Robust**
- **Kostenänderung 5-15%** → **Moderat robust**
- **Kostenänderung > 15%** → **Sensitiv**

#### Konfigurations-Stabilität:
- **Optimaler P_el ändert sich < 10%** → Robust
- **Optimaler H2-Speicher ändert sich < 20%** → Robust
- **Optimaler NH3-Speicher ändert sich < 15%** → Robust

#### Empfehlung:
Führe Sensitivitätsanalyse für **Top 10 Konfigurationen** durch, um robusteste Lösung zu identifizieren.

---

## Zusammenfassung & Empfehlungen

### Priorität 1 (Hoch):
1. ✅ **Nebenbedingungen hinzufügen**: Rampenraten, Start/Stop-Limits, Mindest-Vollaststunden
2. ✅ **Vorfilterung**: Technisch unrealistische Konfigurationen ausschließen
3. ✅ **Sensitivitätsanalyse**: Strompreis, Windkapazität, Elektrolyseur-Kosten

### Priorität 2 (Mittel):
4. ✅ **Entscheidungsvariablen erweitern**: `el_operating_strategy`, `wind_el_ratio`, Skalierungsexponenten
5. ✅ **Multi-Objective Optimierung**: Kosten + CAPEX-Risiko + Effizienz
6. ✅ **Hierarchische Optimierung**: Grober → Feiner Raster

### Priorität 3 (Niedrig):
7. ✅ **Clustering**: Identifizierung stabiler Optima
8. ✅ **Heuristische Methoden**: Simulated Annealing oder Genetic Algorithm
9. ✅ **CO₂-Intensität**: Als zusätzliche Zielfunktion

---

**Erstellt**: 2024
**Basierend auf**: Code_Final.py, wasserstoff_simulation.html
