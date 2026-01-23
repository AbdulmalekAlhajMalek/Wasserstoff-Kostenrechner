# WERTE AUS CODE_FINAL.PY - ÜBERTRAGEN IN HTML

## Alle Werte, die aus Code_Final.py in wasserstoff_simulation.html eingetragen wurden:

### 1. Allgemeine Parameter
- **project_lifetime**: 20 Jahre (vorher: 25)
- **h2_production**: 120.8 kt/a (vorher: 110)
- **h2_steel_demand**: 120.8 kt/a (vorher: 110)
- **h2_import_target**: 120800 t/a (vorher: 100000)

### 2. Wind
- **wind_capacity**: 2.47 GW ✓ (bereits korrekt)
- **wind_capex**: 4.94 Mrd. € (berechnet: 2470 MW × 2 Mio €/MW = 4.94 Mrd. €)
- **wind_opex**: 148.2 Mio. €/Jahr (berechnet: 2470 MW × 1000 × 60 €/kW/a = 148.2 Mio. €/a)

### 3. Elektrolyseur
- **electrolysis_specific_energy**: 48 kWh/kg H₂ (vorher: 50)
- **electrolysis_capex_per_kw**: 464 €/kW (AEL Standard, vorher: 450)
- **min_load_fraction**: 0.20 (AEL Standard, vorher: 0.1)
- **el_ramp_frac_per_h**: 0.80 ✓ (bereits korrekt)

**Technologie-spezifische Werte:**
- **AEL**: CAPEX = 464 $/kW, OPEX = 40.6 $/kW/a, min_load = 0.20
- **PEM**: CAPEX = 580 $/kW, OPEX = 24.36 $/kW/a, min_load = 0.05

### 4. Wasser/RO
- **desalination_specific_energy**: 4 kWh/m³ (vorher: 5)
- **ro_capex_per_m3_per_day**: 1500 €/m³/day ✓ (bereits korrekt)
- **ro_opex_fraction_per_year**: 0 (vorher: 0.05, wird nicht mehr betrachtet)
- **ro_opex_per_m3**: 0.3825 €/m³ ✓ (bereits korrekt)
- **water_tank_capex_per_m3**: 200 €/m³ ✓ (bereits korrekt)
- **water_tank_opex_fraction_per_year**: 0.02 ✓ (bereits korrekt)
- **water_tank_loss_frac_per_hour**: 0.001 ✓ (bereits korrekt)

### 5. ASU (N₂)
- **asu_capex_per_unit**: 1700 €/kg N₂/h (vorher: 0)
- **asu_opex_share**: 0.03 (vorher: 0)
- **ASU spec_kwh_per_kgN2**: 0.33 kWh/kg N₂ (muss in Berechnung verwendet werden)

### 6. Haber-Bosch
- **haber_bosch_availability**: 0.94 ✓ (bereits korrekt)
- **haber_bosch_capex_per_unit**: 491.4 €/t NH₃/year (vorher: 0)
- **haber_bosch_opex**: 24.57 $/t NH₃ (muss berechnet werden: annual_nh3_prod_t × 24.57)
- **hb_ramp_frac_per_h**: 0.10 ✓ (bereits korrekt)
- **ammonia_annual_demand**: 684.5 kt/a (berechnet: 120800 × 17/3 = 684533 t/a)

### 7. H₂ Storage (LH₂)
- **h2_storage_eta_in**: 0.995 ✓ (bereits korrekt)
- **h2_storage_eta_out**: 0.995 ✓ (bereits korrekt)
- **h2_spec_kwh_per_kg_in**: 11.0 kWh/kg H₂ ✓ (bereits korrekt)
- **h2_spec_kwh_per_kg_out**: 0.06 kWh/kg H₂ ✓ (bereits korrekt)
- **h2_boil_off_loss_frac_per_hour**: 0.0000208 (0.05%/Tag / 24) ✓ (bereits korrekt)
- **h2_reliq_kwh_per_kg_bog**: 11.0 kWh/kg BOG ✓ (bereits korrekt)
- **h2_reliq_frac**: 1.0 ✓ (bereits korrekt)
- **H2 Storage CAPEX**: 33000 $/t H₂ (muss aus Kapazität berechnet werden)

### 8. NH₃ Storage
- **nh3_spec_kwh_per_t_in**: 1.0 kWh/t NH₃ ✓ (bereits korrekt)
- **nh3_spec_kwh_per_t_out**: 1.0 kWh/t NH₃ ✓ (bereits korrekt)
- **nh3_cooling_kwh_per_t_per_day**: 40.0 kWh/t NH₃/Tag ✓ (bereits korrekt)
- **capex_per_t_nh3_storage**: 810 €/t NH₃ (vorher: 0)
- **NH3 Storage CAPEX**: 810 $/t NH₃ (muss aus Kapazität berechnet werden)

### 9. SOC Control Parameter
- **h2_soc_low_frac**: 0.3 ✓ (bereits korrekt)
- **h2_soc_high_frac**: 0.60 ✓ (bereits korrekt)
- **h2_el_stop_frac**: 0.95 ✓ (bereits korrekt)
- **h2_el_start_frac**: 0.30 ✓ (bereits korrekt)
- **nh3_target_level_ships**: 1.2 ✓ (bereits korrekt)
- **nh3_deadband_ships**: 1.1 ✓ (bereits korrekt)
- **hb_min_frac_when_on**: 0.40 ✓ (bereits korrekt)

### 10. Berechnete Werte (aus Code_Final.py)
- **annual_nh3_prod_t**: 120800 × 17/3 = 684533.33 t/a = 684.5 kt/a
- **hb_capacity_tNH3_per_day**: 684533.33 / (0.94 × 365) = 1995.3 t/d ≈ 1995 t/d ✓

### 11. Storage OPEX
- **storage_opex_share**: 0.03 (für H₂, vorher: 0)
- **NH3 Storage OPEX**: 0.02 (fraction, muss separat behandelt werden)

---

## WICHTIGE HINWEISE:

1. **Storage CAPEX** werden aus Kapazitäten berechnet:
   - H₂: 33000 $/t H₂ × Kapazität [t]
   - NH₃: 810 $/t NH₃ × Kapazität [t]

2. **Haber-Bosch CAPEX** wird berechnet als:
   - 491.4 $/t NH₃/year × Kapazität [t/a]

3. **ASU CAPEX** wird berechnet als:
   - 1700 $/kg N₂/h × Kapazität [kg N₂/h]

4. **Technologie-Auswahl** beeinflusst:
   - CAPEX/OPEX des Elektrolyseurs
   - Mindestlastanteil

5. **Alle Energieverbräuche** sind jetzt in der Berechnung integriert:
   - H₂ Storage (Liquefaction, Regasification, Re-liquefaction)
   - NH₃ Storage (In/Out, Cooling)
   - Water Tank Losses

---

**Erstellt**: $(date)
**Quelle**: Code_Final.py
