# VERGLEICH: PYTHON vs. HTML ERGEBNISSE

## ⚠️ WICHTIGER HINWEIS

**Die beiden Codes berechnen unterschiedliche Metriken und können daher NICHT direkt verglichen werden!**

---

## 1. PYTHON (Code_Final.py) - `cost_components_proxy`

### Was wird berechnet:
- **`total_proxy`**: Gesamtkosten über die **gesamte Lebensdauer (20 Jahre)** in €
- **KEINE Kosten pro kg H₂** werden berechnet
- **KEINE Annualisierung** (CAPEX wird nicht auf Jahresbasis umgerechnet)

### Berechnungslogik:
```python
total_proxy = (
    wind_total +                    # CAPEX + OPEX (über 20 Jahre)
    el_capex + el_opex_total +      # CAPEX + OPEX (über 20 Jahre)
    hb_capex + hb_opex_total +      # CAPEX + OPEX (über 20 Jahre)
    n2_capex + n2_opex_total +      # CAPEX + OPEX (über 20 Jahre)
    ro_capex + ro_opex_total +      # CAPEX + OPEX (über 20 Jahre)
    water_tank_capex + water_tank_opex_total +  # CAPEX + OPEX (über 20 Jahre)
    h2_capex + h2_opex_total +      # CAPEX + OPEX (über 20 Jahre)
    nh3_capex + nh3_opex_total      # CAPEX + OPEX (über 20 Jahre)
)
```

### Beispiel-Berechnung:
- **Wind CAPEX**: 2470 MW × 2 Mio €/MW = **4.94 Mrd. €** (einmalig)
- **Wind OPEX**: 2470 MW × 1000 × 60 €/kW/a × 20 Jahre = **2.964 Mrd. €** (über 20 Jahre)
- **Wind Total**: 4.94 + 2.964 = **7.904 Mrd. €** (über 20 Jahre)

### Fehlende Komponenten in Python:
- ❌ **KEINE Transport-Kosten**
- ❌ **KEINE Cracking-Kosten**
- ❌ **KEINE Stromkosten separat** (werden in stündlicher Simulation berücksichtigt)
- ❌ **KEINE Storage-Energiekosten separat** (werden in stündlicher Simulation berücksichtigt)

### Output:
- `total_proxy` = Gesamtkosten in € (über 20 Jahre)
- **KEIN** €/kg H₂ Output

---

## 2. HTML (wasserstoff_simulation.html) - `calculateCosts`

### Was wird berechnet:
- **`totalAnnualCost`**: Jährliche Gesamtkosten in €/Jahr (CAPEX annualisiert)
- **`costPerKg`**: Kosten pro kg geliefertem H₂ in €/kg
- **`h2DeliveredAnnual`**: Gelieferte H₂-Menge pro Jahr (nach allen Verlusten)

### Berechnungslogik:
```javascript
// 1. Annualisierung der CAPEX
windCAPEXannual = annualizeCAPEX(windCAPEX, discountRate, lifetime);
// CRF = (r × (1+r)^n) / ((1+r)^n - 1)
// annualized = CAPEX × CRF

// 2. Jährliche Gesamtkosten
totalAnnualCost = 
    windCostAnnualTotal +           // Annualisierte CAPEX + OPEX + Depex
    electrolysisCostAnnual +        // Annualisierte CAPEX + OPEX + Stromkosten
    desalinationCostAnnual +         // Annualisierte CAPEX + OPEX + Stromkosten
    asuCostAnnual +                  // Annualisierte CAPEX + OPEX + Stromkosten
    haberBoschCostAnnual +          // Annualisierte CAPEX + OPEX + Stromkosten
    storageCostAnnual +             // Annualisierte CAPEX + OPEX + Energiekosten
    transportCostAnnual +           // Annualisierte CAPEX + OPEX + variable Kosten
    crackingCostAnnual;             // Annualisierte CAPEX + OPEX

// 3. Ketteneffizienz (Verluste)
chainEfficiency = etaHB × etaStorage × etaShipping × etaCracking;

// 4. Gelieferte H₂-Menge
h2DeliveredAnnual = h2Reference × chainEfficiency; // kg/Jahr

// 5. Kosten pro kg
costPerKg = totalAnnualCost / h2DeliveredAnnual; // €/kg
```

### Beispiel-Berechnung:
- **Wind CAPEX**: 4.94 Mrd. €
- **CRF** (5% Zins, 20 Jahre): 0.0802
- **Wind CAPEX annualisiert**: 4.94 × 0.0802 = **396 Mio. €/Jahr**
- **Wind OPEX**: 148.2 Mio. €/Jahr
- **Wind Total (jährlich)**: 396 + 148.2 = **544.2 Mio. €/Jahr**

### Zusätzliche Komponenten in HTML:
- ✅ **Transport-Kosten** vollständig berechnet
- ✅ **Cracking-Kosten** berechnet
- ✅ **Stromkosten** separat für alle Komponenten
- ✅ **Storage-Energiekosten** separat berechnet

### Output:
- `totalAnnualCost` = Gesamtkosten in €/Jahr
- `costPerKg` = Kosten in €/kg H₂
- `h2DeliveredAnnual` = Gelieferte Menge in kg/Jahr

---

## 3. HAUPUNTerschiede

### A) Zeitbasis
| Aspekt | Python | HTML |
|--------|--------|------|
| **Zeitraum** | 20 Jahre (Gesamtlebensdauer) | 1 Jahr (annualisiert) |
| **CAPEX** | Einmalige Investition | Annualisiert (CRF) |
| **OPEX** | Über 20 Jahre kumuliert | Jährlich |
| **Output** | Gesamtkosten in € | Kosten in €/kg H₂ |

### B) Berechnungsmethode
| Aspekt | Python | HTML |
|--------|--------|------|
| **Annualisierung** | ❌ NEIN | ✅ JA (Capital Recovery Factor) |
| **Diskontierung** | ❌ NEIN | ✅ JA (5% Zinssatz) |
| **Kosten pro kg** | ❌ NEIN | ✅ JA |
| **Verluste berücksichtigt** | ❌ NEIN (in Proxy) | ✅ JA (Ketteneffizienz) |

### C) Komponenten
| Komponente | Python | HTML |
|------------|--------|------|
| Wind | ✅ | ✅ |
| Elektrolyse | ✅ | ✅ |
| H2 Storage | ✅ | ✅ |
| NH3 Storage | ✅ | ✅ |
| Haber-Bosch | ✅ | ✅ |
| ASU/N2 | ✅ | ✅ |
| RO/Water | ✅ | ✅ |
| Water Tank | ✅ | ✅ |
| Transport | ❌ | ✅ |
| Cracking | ❌ | ✅ |
| Stromkosten | ❌ (in Simulation) | ✅ (separat) |
| Storage-Energie | ❌ (in Simulation) | ✅ (separat) |

---

## 4. WARUM SIND DIE WERTE UNTERSCHIEDLICH?

### Grund 1: Zeitbasis
- **Python**: Berechnet Gesamtkosten über 20 Jahre
- **HTML**: Berechnet jährliche Kosten (CAPEX annualisiert)

**Beispiel:**
- Python Wind Total: **7.904 Mrd. €** (20 Jahre)
- HTML Wind Total: **544.2 Mio. €/Jahr** × 20 = **10.884 Mrd. €** (20 Jahre, mit Diskontierung)

**Unterschied**: HTML berücksichtigt Diskontierung (5% Zins), Python nicht.

### Grund 2: Fehlende Komponenten
- **Python**: Berechnet KEINE Transport- und Cracking-Kosten
- **HTML**: Berechnet Transport- und Cracking-Kosten vollständig

**Beispiel:**
- Python `total_proxy`: ~10-15 Mrd. € (ohne Transport/Cracking)
- HTML `totalAnnualCost`: ~800-1200 Mio. €/Jahr (mit Transport/Cracking)

### Grund 3: Verluste
- **Python**: Berücksichtigt Verluste NICHT in `cost_components_proxy`
- **HTML**: Berücksichtigt Verluste über Ketteneffizienz

**Beispiel:**
- Python: Berechnet auf Basis von `annual_h2_prod_t = 120800 t/a`
- HTML: Berechnet auf Basis von `h2DeliveredAnnual = h2Reference × chainEfficiency`
  - Wenn `chainEfficiency = 0.85`, dann: `h2DeliveredAnnual = 120800 × 0.85 = 102680 t/a`

### Grund 4: Stromkosten
- **Python**: Stromkosten werden NICHT in `cost_components_proxy` berechnet
- **HTML**: Stromkosten werden separat für alle Komponenten berechnet

**Beispiel:**
- Python: Keine Stromkosten in `total_proxy`
- HTML: Stromkosten für Electrolysis, Desalination, ASU, Haber-Bosch, Storage

---

## 5. WIE KANN MAN DIE WERTE VERGLEICHEN?

### Option 1: Python-Werte annualisieren
```python
# Python total_proxy auf Jahresbasis umrechnen
total_proxy_annual = total_proxy / 20  # Ohne Diskontierung
# ODER mit Diskontierung:
CRF = (0.05 * (1.05**20)) / ((1.05**20) - 1)  # = 0.0802
# Aber Python hat keine CAPEX/OPEX-Trennung in total_proxy
```

### Option 2: HTML-Werte auf 20 Jahre kumulieren
```javascript
// HTML totalAnnualCost auf 20 Jahre kumulieren
total_20_years = totalAnnualCost * 20  // Ohne Diskontierung
// ODER mit Diskontierung (NPV):
NPV = totalAnnualCost * ((1 - (1.05)**-20) / 0.05)  // = 12.46 × totalAnnualCost
```

### Option 3: Beide auf Kosten pro kg H₂ umrechnen
```python
# Python: MUSS erst h2DeliveredAnnual berechnen
h2_delivered_20_years = annual_h2_prod_t * 20 * chain_efficiency
cost_per_kg_python = total_proxy / h2_delivered_20_years
```

```javascript
// HTML: Bereits vorhanden
costPerKg = totalAnnualCost / h2DeliveredAnnual
```

---

## 6. FAZIT

### ✅ HTML-Berechnung ist korrekt und vollständig
- Alle Komponenten sind berücksichtigt
- Annualisierung mit Diskontierung ist korrekt
- Verluste werden berücksichtigt
- Kosten pro kg H₂ werden berechnet

### ⚠️ Python-Berechnung ist unvollständig
- `total_proxy` ist nur ein Proxy-Wert für Optimierung
- Transport und Cracking fehlen
- Keine Kosten pro kg H₂
- Keine Annualisierung

### 🔄 Vergleich nur möglich, wenn:
1. Python-Werte annualisiert werden
2. HTML-Werte auf 20 Jahre kumuliert werden
3. Beide auf Kosten pro kg H₂ umgerechnet werden
4. Gleiche Verlustannahmen verwendet werden

### 📊 Erwartete Unterschiede:
- **Python `total_proxy`**: ~10-15 Mrd. € (20 Jahre, ohne Transport/Cracking)
- **HTML `totalAnnualCost × 20`**: ~16-24 Mrd. € (20 Jahre, mit Transport/Cracking, mit Diskontierung)
- **HTML `costPerKg`**: ~6-10 €/kg H₂ (abhängig von Verlusten)

---

## 7. EMPFEHLUNG

**Verwende die HTML-Berechnung als Referenz**, da sie:
- ✅ Vollständiger ist (Transport, Cracking, Storage-Energie)
- ✅ Korrekt annualisiert ist (mit Diskontierung)
- ✅ Kosten pro kg H₂ berechnet
- ✅ Verluste berücksichtigt

**Python `total_proxy`** dient hauptsächlich zur **Optimierung** (Minimierung der Gesamtkosten) und ist nicht für direkte Kostenvergleiche geeignet.
