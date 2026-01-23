# VERGLEICH: HTML vs. PYTHON BEREICHNUNGSLOGIK

## Übersicht der Kostenkomponenten

### Code_Final.py (cost_components_proxy Funktion)

**Berechnet über gesamte Lebensdauer (years = 20):**

1. **Wind**
   - `wind_capex = capex_eur_per_mw × wind_capacity_mw`
   - `wind_opex = opex_eur_per_kw_per_year × wind_capacity_kw × years`
   - `wind_total = wind_capex + wind_opex`
   - **KEIN Depex** (wind_dapex = 0.0)

2. **Elektrolyse**
   - `el_capex = capex_usd_per_kw × p_el_mw × 1000`
   - `el_opex_total = opex_usd_per_kw_per_year × p_el_mw × 1000 × years`
   - **KEINE Stromkosten separat** (werden anders behandelt)

3. **H2 Storage**
   - `h2_capex = capex_usd_per_tH2 × h2_storage_t_design`
   - `h2_opex_total = h2_capex × opex_fraction_per_year × years`
   - **KEINE Energiekosten separat** (Liquefaction, Regasification, Re-liquefaction)

4. **NH3 Storage**
   - `nh3_capex = capex_usd_per_tNH3 × nh3_storage_t`
   - `nh3_opex_total = nh3_capex × opex_fraction_per_year × years`
   - **KEINE Energiekosten separat** (In/Out, Cooling)

5. **Haber-Bosch**
   - `hb_capex = capex_usd_per_tNH3_per_year × hb_cap_tpy`
   - `hb_opex_total = opex_usd_per_tNH3 × annual_nh3_prod_t × years`
   - **KEINE Stromkosten separat**

6. **N2 (ASU)**
   - `n2_capex = capex_usd_per_kgN2_per_h × n2_capacity_kg_per_h`
   - `n2_opex_total = opex_fraction_per_year × n2_capex × years`
   - **KEINE Stromkosten separat**

7. **RO (Reverse Osmosis)**
   - `ro_capex = capex_usd_per_m3_per_day × ro_m3_per_day_design`
   - `ro_opex_total = ro_capex × ro_opex_frac × years + ro_opex_usd_per_m3 × annual_water_m3 × years`
   - **KEINE Stromkosten separat**

8. **Water Tank**
   - `water_tank_capex = capex_usd_per_m3 × water_tank_m3_design`
   - `water_tank_opex_total = water_tank_capex × opex_fraction_per_year × years`
   - **KEINE Verluste separat**

**Total (über gesamte Lebensdauer):**
```python
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
```

**WICHTIG:** Code_Final.py berechnet **KEINE**:
- Transport-Kosten
- Cracking-Kosten
- Stromkosten separat (werden in stündlicher Simulation berücksichtigt)
- Storage-Energiekosten separat (werden in stündlicher Simulation berücksichtigt)

---

### wasserstoff_simulation.html (calculateCosts Funktion)

**Berechnet jährlich (annualisiert):**

1. **Wind**
   - `windCAPEXannual = annualizeCAPEX(windCAPEX, discountRate, lifetime)`
   - `windOPEX = wind_opex / lifetime` (direkt jährlich)
   - `windDepexAnnual = annualizeDepex(windDepex, discountRate, lifetime)`
   - `windCostAnnualTotal = windCAPEXannual + windOPEX + windDepexAnnual` (wenn includeWindInTotal)

2. **Electrolysis**
   - `electrolysisCAPEXannual = annualizeCAPEX(electrolysisCAPEX, discountRate, lifetime)`
   - `electrolysisOPEX = opex_per_kw_per_year × power` (jährlich)
   - `electrolysisElectricityCost = electricityPrice × electrolysisElectricityDemand`
   - `electrolysisCostAnnual = electrolysisCAPEXannual + electrolysisOPEX + electricityCost`

3. **Desalination (RO + Water Tank)**
   - `desalinationCAPEXannual = annualizeCAPEX(roCapexCalculated, discountRate, lifetime)`
   - `roOpexTotal = roOpexFromFraction + roOpexFromVolume` (jährlich)
   - `desalinationElectricityCost = electricityPrice × desalinationElectricityDemand`
   - `waterTankCAPEXannual = annualizeCAPEX(waterTankCapexCalculated, discountRate, lifetime)`
   - `waterTankOpexFromFraction = waterTankCapexCalculated × opex_fraction_per_year` (jährlich)
   - `waterReplacementCost = waterTankLossAnnual × desalinationSpecificEnergy × electricityPrice` (jährlich)
   - `desalinationCostAnnual = desalinationCAPEXannual + roOpexTotal + electricityCost + waterTankCAPEXannual + waterTankOpexFromFraction + waterReplacementCost`

4. **ASU (N2)**
   - `asuCAPEXannual = annualizeCAPEX(asuCAPEX, discountRate, lifetime)`
   - `asuOPEX = asuCAPEX × opex_share` (jährlich) ODER direkt eingegeben
   - `asuElectricityCost = electricityPrice × asuElectricity`
   - `asuCostAnnual = asuCAPEXannual + asuOPEX + electricityCost`

5. **Haber-Bosch**
   - `haberBoschCAPEXannual = annualizeCAPEX(haberBoschCAPEX, discountRate, lifetime)`
   - `haberBoschOPEX = opex_usd_per_tNH3 × annual_nh3_prod_t` (jährlich) ODER direkt eingegeben
   - `haberBoschElectricityCost = electricityPrice × haberBoschElectricity`
   - `haberBoschCostAnnual = haberBoschCAPEXannual + haberBoschOPEX + electricityCost`

6. **Storage (H2 + NH3 + Water)**
   - `storageCAPEXannual = annualizeCAPEX(storageTotalCAPEX, discountRate, lifetime)`
   - `storageOPEX = (storageH2CAPEX + storageNH3CAPEX) × storageOPEXshare` (jährlich)
   - `h2StorageEnergyCost = electricityPrice × h2StorageEnergyTotal` (Liquefaction + Regasification + Re-liquefaction)
   - `nh3StorageEnergyCost = electricityPrice × nh3StorageEnergyTotal` (In/Out + Cooling)
   - `storageCostAnnual = storageCAPEXannual + storageOPEX + h2StorageEnergyCost + nh3StorageEnergyCost`

7. **Transport**
   - `vesselCAPEXannual = annualizeCAPEX(vesselCAPEXtotal, discountRate, lifetime)`
   - `vesselOPEXtotal = vesselOPEXperVessel × numVessels` (jährlich)
   - `variableShippingCostMain = shipping_cost_per_t_nh3 × nh3TransportRequiredMain` (jährlich)
   - `fuelCostTotalMain = fuel_cost_per_trip × tripsPerShipMain × numVesselsMain` (jährlich)
   - `harborFeesTotalMain = harbor_fees_per_trip × tripsPerShipMain × numVesselsMain` (jährlich)
   - `insuranceCostMain = vesselCAPEXtotal × insurance_rate / 100` (jährlich)
   - `taxesCustomsMain = taxes_customs × 1000000` (jährlich)
   - `transportCostAnnual = vesselCAPEXannual + vesselOPEXtotal + variableShippingCostMain + fuelCostTotalMain + harborFeesTotalMain + insuranceCostMain + taxesCustomsMain`

8. **Cracking**
   - `crackingCAPEXannual = annualizeCAPEX(crackingCAPEX, discountRate, lifetime)`
   - `crackingOPEX = cracking_opex × 1000000` (jährlich)
   - `crackingCostAnnual = crackingCAPEXannual + crackingOPEX`

**Total (jährlich):**
```javascript
totalAnnualCost = windCostAnnualTotal + electrolysisCostAnnual + desalinationCostAnnual + 
                  asuCostAnnual + haberBoschCostAnnual + storageCostAnnual + 
                  transportCostAnnual + crackingCostAnnual;
```

**Cost per kg:**
```javascript
costPerKg = totalAnnualCost / h2DeliveredAnnual;
```

---

## WICHTIGE UNTERSCHIEDE

### 1. **Annualisierung**
- **Python:** Berechnet Gesamtkosten über gesamte Lebensdauer (20 Jahre)
- **HTML:** Berechnet jährliche Kosten (CAPEX wird annualisiert mit CRF)

### 2. **Stromkosten**
- **Python:** Stromkosten werden NICHT separat berechnet (werden in stündlicher Simulation berücksichtigt)
- **HTML:** Stromkosten werden separat für jede Komponente berechnet (Electrolysis, Desalination, ASU, Haber-Bosch, Storage)

### 3. **Storage-Energiekosten**
- **Python:** Storage-Energiekosten werden NICHT separat berechnet (werden in stündlicher Simulation berücksichtigt)
- **HTML:** Storage-Energiekosten werden separat berechnet:
  - H2: Liquefaction, Regasification, Re-liquefaction
  - NH3: In/Out, Cooling

### 4. **Transport & Cracking**
- **Python:** Transport und Cracking werden NICHT in `cost_components_proxy` berechnet
- **HTML:** Transport und Cracking werden vollständig berechnet

### 5. **Water Tank Verluste**
- **Python:** Water Tank Verluste werden NICHT separat berechnet
- **HTML:** Water Tank Verluste werden als `waterReplacementCost` berechnet

---

## FEHLENDE KOMPONENTEN IN HTML

### ✅ Alle wichtigen Komponenten sind vorhanden:
1. ✅ Wind (CAPEX, OPEX, Depex)
2. ✅ Electrolysis (CAPEX, OPEX, Stromkosten)
3. ✅ Desalination/RO (CAPEX, OPEX, Stromkosten)
4. ✅ Water Tank (CAPEX, OPEX, Verluste)
5. ✅ ASU/N2 (CAPEX, OPEX, Stromkosten)
6. ✅ Haber-Bosch (CAPEX, OPEX, Stromkosten)
7. ✅ H2 Storage (CAPEX, OPEX, Energiekosten)
8. ✅ NH3 Storage (CAPEX, OPEX, Energiekosten)
9. ✅ Transport (CAPEX, OPEX, variable Kosten)
10. ✅ Cracking (CAPEX, OPEX)

---

## MÖGLICHE VERBESSERUNGEN

### 1. **Konsistenz mit Python-Modell**
- HTML berechnet mehr Komponenten als Python (Transport, Cracking, Storage-Energie)
- Das ist **KORREKT**, da HTML eine vollständige Kostenberechnung für die gesamte Kette macht

### 2. **Stromkosten-Berechnung**
- HTML berechnet Stromkosten separat für jede Komponente
- Python berücksichtigt Stromkosten in der stündlichen Simulation
- **Beide Ansätze sind korrekt**, aber unterschiedlich

### 3. **Storage-Energiekosten**
- HTML berechnet Storage-Energiekosten separat
- Python berücksichtigt diese in der stündlichen Simulation
- **HTML-Ansatz ist transparenter** für die Kostenaufschlüsselung

---

## FAZIT

**✅ Alle wichtigen Kostenkomponenten sind im HTML-Code berücksichtigt!**

Der HTML-Code ist sogar **vollständiger** als die Python `cost_components_proxy` Funktion, da:
1. Transport-Kosten vollständig berechnet werden
2. Cracking-Kosten berechnet werden
3. Storage-Energiekosten separat berechnet werden
4. Water Tank Verluste berücksichtigt werden
5. Alle Stromkosten transparent aufgeschlüsselt werden

**Die Berechnung im HTML-Code ist korrekt und vollständig!**
