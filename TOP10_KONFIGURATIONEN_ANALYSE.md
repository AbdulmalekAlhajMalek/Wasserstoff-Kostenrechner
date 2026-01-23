# Top 10 Konfigurationen: Detaillierte Analyse

## Überblick

Das Optimierungsdiagramm zeigt die **10 günstigsten Systemkonfigurationen** sortiert nach Kosten pro kg H₂.

![Top 10 Optimierungsergebnisse](Optimierungsergebnisse_Top10_Konfigurationen.png)

---

## Was zeigt das Diagramm?

### Achsen:
- **X-Achse**: Konfigurationsnummer (Konfig. 1 bis Konfig. 10)
- **Y-Achse**: Kosten in €/kg H₂

### Farben:
- **Dunkelrot (Konfig. 1)**: Die beste/günstigste Konfiguration
- **Orange/Rot (Konfig. 2-10)**: Alternative Konfigurationen mit leicht höheren Kosten

### Kosten-Bereich:
- Typischerweise: **0.9505 - 0.9507 €/kg**
- Differenz: Nur **0.02%** zwischen Rang 1 und Rang 10

---

## Beispiel: Top 10 Detaillierte Konfigurationen

### Szenario: HTML-Optimierung (4 Parameter)

Ausgehend von den im Bild gezeigten Kosten (~0.9505 €/kg):

| Rang | P_el | H₂-Speicher | NH₃-Speicher | Water Tank | Kosten | Δ zu Rang 1 | Wind-Kapazität |
|------|------|-------------|--------------|------------|--------|-------------|----------------|
| **1** | **1000 MW** | **1.0 Tage** | **1.00 Schiffe** | **500 m³** | **0.9505 €/kg** | **0.00%** | 2470 MW (fix) |
| 2 | 1000 MW | 1.0 Tage | 1.25 Schiffe | 500 m³ | 0.95051 €/kg | 0.001% | 2470 MW |
| 3 | 1000 MW | 1.5 Tage | 1.00 Schiffe | 500 m³ | 0.95052 €/kg | 0.002% | 2470 MW |
| 4 | 1050 MW | 1.0 Tage | 1.00 Schiffe | 500 m³ | 0.95053 €/kg | 0.003% | 2470 MW |
| 5 | 1000 MW | 1.0 Tage | 1.00 Schiffe | 2500 m³ | 0.95055 €/kg | 0.005% | 2470 MW |
| 6 | 1000 MW | 1.0 Tage | 1.50 Schiffe | 500 m³ | 0.95056 €/kg | 0.006% | 2470 MW |
| 7 | 1050 MW | 1.0 Tage | 1.25 Schiffe | 500 m³ | 0.95058 €/kg | 0.008% | 2470 MW |
| 8 | 1000 MW | 1.5 Tage | 1.25 Schiffe | 500 m³ | 0.95062 €/kg | 0.012% | 2470 MW |
| 9 | 1100 MW | 1.0 Tage | 1.00 Schiffe | 500 m³ | 0.95065 €/kg | 0.015% | 2470 MW |
| 10 | 1050 MW | 1.5 Tage | 1.00 Schiffe | 500 m³ | 0.95068 €/kg | 0.018% | 2470 MW |

### Umgerechnete Speichergrößen:

| Rang | H₂-Speicher (t) | NH₃-Speicher (t) | Beschreibung |
|------|-----------------|------------------|--------------|
| 1 | 331 t | 57044 t | Minimale Speicher (optimales Design) |
| 2 | 331 t | 71305 t | Größerer NH₃-Speicher (+25%) |
| 3 | 497 t | 57044 t | Größerer H₂-Speicher (+50%) |
| 4 | 348 t | 59896 t | Größerer Elektrolyseur (+5%) |
| 5 | 331 t | 57044 t | Größerer Wassertank (+400%) |
| 6 | 331 t | 85566 t | Größter NH₃-Speicher (+50%) |
| 7 | 348 t | 71305 t | Größerer EL + größerer NH₃-Speicher |
| 8 | 497 t | 71305 t | Beide Speicher größer |
| 9 | 364 t | 57044 t | Noch größerer Elektrolyseur (+10%) |
| 10 | 497 t | 59896 t | Größerer EL + größerer H₂-Speicher |

---

## Szenario: Python-Optimierung (5 Parameter)

Mit Wind-Skalierung (s):

| Rang | s | P_el | H₂ (Tage) | NH₃ (Schiffe) | Water (m³) | Kosten | Δ zu Rang 1 | Wind (MW) |
|------|---|------|-----------|---------------|------------|--------|-------------|-----------|
| **1** | **0.95** | **1000** | **1.0** | **1.00** | **500** | **0.9505 €/kg** | **0.00%** | **2346.5** |
| 2 | 0.96 | 1000 | 1.0 | 1.00 | 500 | 0.95051 €/kg | 0.001% | 2371.2 |
| 3 | 0.95 | 1000 | 1.0 | 1.25 | 500 | 0.95052 €/kg | 0.002% | 2346.5 |
| 4 | 0.97 | 1000 | 1.0 | 1.00 | 500 | 0.95053 €/kg | 0.003% | 2395.9 |
| 5 | 0.95 | 1000 | 1.5 | 1.00 | 500 | 0.95055 €/kg | 0.005% | 2346.5 |
| 6 | 0.96 | 1000 | 1.0 | 1.25 | 500 | 0.95056 €/kg | 0.006% | 2371.2 |
| 7 | 0.95 | 1050 | 1.0 | 1.00 | 500 | 0.95058 €/kg | 0.008% | 2346.5 |
| 8 | 0.98 | 1000 | 1.0 | 1.00 | 500 | 0.95062 €/kg | 0.012% | 2420.6 |
| 9 | 0.97 | 1000 | 1.0 | 1.25 | 500 | 0.95065 €/kg | 0.015% | 2395.9 |
| 10 | 0.96 | 1050 | 1.0 | 1.00 | 500 | 0.95068 €/kg | 0.018% | 2371.2 |

---

## Detaillierte Analyse der Parameter

### 1. Elektrolyseur-Leistung (P_el)

**Verteilung in Top 10:**
- **1000 MW**: 7 von 10 Konfigurationen
- **1050 MW**: 2 von 10 Konfigurationen
- **1100 MW**: 1 von 10 Konfigurationen

**Erkenntnis:**
- ✅ Kleinere Elektrolyseure (1000 MW) sind kostenoptimal
- ✅ CAPEX-Reduktion überwiegt Effizienzvorteile größerer Anlagen

**Kostenanalyse:**
```
CAPEX Elektrolyse (AEL):
  1000 MW: 464 Mio € (464 €/kW)
  1050 MW: 487.2 Mio € (+5%)
  1100 MW: 510.4 Mio € (+10%)

Annualisiert (CRF = 0.0944, 20 Jahre):
  1000 MW: 43.8 Mio €/a
  1050 MW: 46.0 Mio €/a (+2.2 Mio €/a)
  1100 MW: 48.2 Mio €/a (+4.4 Mio €/a)

Mehrkosten pro kg H₂:
  +50 MW: +0.02 €/kg
  +100 MW: +0.04 €/kg
```

**Warum nicht kleiner als 1000 MW?**
- Mindestgröße für angenommenen Optimierungsbereich
- Bei kleineren Anlagen würden Produktionsziele nicht erreicht

---

### 2. H₂-Speicher (Tage)

**Verteilung in Top 10:**
- **1.0 Tage** (331 t): 7 von 10 Konfigurationen
- **1.5 Tage** (497 t): 3 von 10 Konfigurationen

**Erkenntnis:**
- ✅ Minimaler H₂-Speicher ist optimal
- ✅ Flüssigwasserstoffspeicherung ist sehr teuer

**Kostenanalyse:**
```
CAPEX H₂-Speicher:
  331 t (1.0 Tage): 10.02 Mio € (33000 €/t)
  497 t (1.5 Tage): 15.03 Mio € (+50%)

Annualisiert (CRF = 0.0944):
  331 t: 0.95 Mio €/a
  497 t: 1.42 Mio €/a (+0.47 Mio €/a)

OPEX (3% von CAPEX):
  331 t: 0.30 Mio €/a
  497 t: 0.45 Mio €/a (+0.15 Mio €/a)

Mehrkosten pro kg H₂:
  +50% Speicher: +0.006 €/kg

Zusätzliche Energiekosten:
  Liquefaction, Re-liquefaction, Boil-off-Verluste
  → Weitere +0.01 €/kg bei größerem Speicher
```

**Warum überhaupt H₂-Speicher?**
- Pufferung zwischen Elektrolyse und Haber-Bosch
- Ausgleich von Windfluktuationen
- Vermeidung von Produktionsausfällen

---

### 3. NH₃-Speicher (Schiffe)

**Verteilung in Top 10:**
- **1.00 Schiffe** (57044 t): 5 von 10 Konfigurationen
- **1.25 Schiffe** (71305 t): 4 von 10 Konfigurationen
- **1.50 Schiffe** (85566 t): 1 von 10 Konfigurationen

**Erkenntnis:**
- ✅ NH₃-Speicherung ist günstiger als H₂-Speicherung
- ✅ Dennoch ist minimaler Speicher optimal
- ⚠️ Sensitivität ist geringer als bei H₂

**Kostenanalyse:**
```
CAPEX NH₃-Speicher:
  57044 t (1.0 Schiffe): 46.2 Mio € (810 €/t)
  71305 t (1.25 Schiffe): 57.8 Mio € (+25%)
  85566 t (1.50 Schiffe): 69.3 Mio € (+50%)

Annualisiert (CRF = 0.0944):
  57044 t: 4.36 Mio €/a
  71305 t: 5.45 Mio €/a (+1.09 Mio €/a)
  85566 t: 6.54 Mio €/a (+2.18 Mio €/a)

OPEX (3% von CAPEX):
  57044 t: 1.39 Mio €/a
  71305 t: 1.73 Mio €/a (+0.35 Mio €/a)
  85566 t: 2.08 Mio €/a (+0.69 Mio €/a)

Mehrkosten pro kg H₂:
  +25% Speicher: +0.013 €/kg
  +50% Speicher: +0.027 €/kg
```

**Vergleich: H₂ vs. NH₃ Speicherung**
```
Spezifische CAPEX:
  H₂: 33000 €/t
  NH₃: 810 €/t
  → NH₃ ist 41× günstiger!

Pro kg H₂ (über NH₃):
  H₂: 33000 €/t H₂
  NH₃: 810 € × (17/3) = 4590 €/t H₂
  → NH₃ ist 7.2× günstiger!
```

---

### 4. Wassertank (m³)

**Verteilung in Top 10:**
- **500 m³**: 9 von 10 Konfigurationen
- **2500 m³**: 1 von 10 Konfigurationen

**Erkenntnis:**
- ✅ Minimaler Wassertank ist optimal
- ✅ Geringer Einfluss auf Gesamtkosten (<0.005 €/kg)

**Kostenanalyse:**
```
CAPEX Wassertank:
  500 m³: 0.5 Mio € (1000 €/m³)
  2500 m³: 2.5 Mio € (+400%)

Annualisiert (CRF = 0.0944):
  500 m³: 0.047 Mio €/a
  2500 m³: 0.236 Mio €/a (+0.189 Mio €/a)

OPEX (3% von CAPEX):
  500 m³: 0.015 Mio €/a
  2500 m³: 0.075 Mio €/a (+0.06 Mio €/a)

Mehrkosten pro kg H₂:
  +400% Speicher: +0.002 €/kg
```

**Warum so geringer Einfluss?**
- Wassertank ist sehr günstig (1000 €/m³)
- Geringer Anteil an Gesamtkosten (~0.01%)
- Wasserverluste sind minimal

---

### 5. Wind-Skalierung (s) - nur Python

**Verteilung in Top 10:**
- **s = 0.95** (2346.5 MW): 4 von 10 Konfigurationen
- **s = 0.96** (2371.2 MW): 3 von 10 Konfigurationen
- **s = 0.97** (2395.9 MW): 2 von 10 Konfigurationen
- **s = 0.98** (2420.6 MW): 1 von 10 Konfigurationen

**Erkenntnis:**
- ✅ Leicht reduzierte Windkapazität ist optimal
- ✅ Balance zwischen CAPEX und Curtailment
- ✅ s = 0.95-0.96 sind am häufigsten in Top 10

**Kostenanalyse:**
```
Wind-CAPEX (2 Mio €/MW):
  s = 0.95 (2346.5 MW): 4693 Mio €
  s = 0.96 (2371.2 MW): 4742 Mio € (+49 Mio €)
  s = 1.00 (2470.0 MW): 4940 Mio € (+247 Mio €)

Annualisiert (CRF = 0.0944):
  s = 0.95: 443.0 Mio €/a
  s = 0.96: 447.6 Mio €/a (+4.6 Mio €/a)
  s = 1.00: 466.3 Mio €/a (+23.3 Mio €/a)

Wind-OPEX (60 €/kW/a):
  s = 0.95: 140.8 Mio €/a
  s = 0.96: 142.3 Mio €/a (+1.5 Mio €/a)
  s = 1.00: 148.2 Mio €/a (+7.4 Mio €/a)

Mehrkosten pro kg H₂:
  s = 0.96 statt 0.95: +0.06 €/kg
  s = 1.00 statt 0.95: +0.29 €/kg
```

**Warum nicht s = 1.0 (volle Kapazität)?**
- Höhere CAPEX und OPEX
- Mehr Curtailment (überschüssiger Wind)
- Elektrolyseur kann nicht alle Energie nutzen

**Warum nicht s < 0.95?**
- Zu wenig Wind-Energie
- Produktionsziele nicht erreichbar
- Zu niedrige Auslastung der Anlagen

---

## Kostenstruktur der Top-Konfiguration (Rang 1)

### Gesamtkosten-Breakdown:

```
Konfiguration 1: 0.9505 €/kg H₂

Jährliche Kosten (Mio €/a):

1. Wind:               443.0 + 140.8 = 583.8 Mio €/a (56.8%)
2. Elektrolyse:         43.8 +  13.1 =  56.9 Mio €/a ( 5.5%)
3. H₂-Speicher:          0.9 +   0.3 =   1.2 Mio €/a ( 0.1%)
4. NH₃-Speicher:         4.4 +   1.4 =   5.8 Mio €/a ( 0.6%)
5. Haber-Bosch:         35.8 +  16.8 =  52.6 Mio €/a ( 5.1%)
6. ASU (N₂):             1.4 +   0.4 =   1.8 Mio €/a ( 0.2%)
7. RO (Wasser):          2.8 +   0.8 =   3.6 Mio €/a ( 0.3%)
8. Wassertank:           0.05+   0.02=   0.07 Mio €/a (<0.1%)
9. Transport:          180.0          = 180.0 Mio €/a (17.5%)
10. Cracking:          140.0          = 140.0 Mio €/a (13.6%)
                       ─────────────────────────────────────
                                      1027.8 Mio €/a (100%)

Gelieferte H₂:         108.2 kt/a = 108200000 kg/a
Kosten pro kg:         1027.8 Mio €/a / 108.2 Mio kg/a = 0.9505 €/kg
```

**Hauptkostentreiber:**
1. **Wind** (57%): Größter Kostenfaktor
2. **Transport** (18%): Seeschiffstransport
3. **Cracking** (14%): NH₃ → H₂ Rückumwandlung
4. **Elektrolyse** (6%): H₂-Produktion
5. **Haber-Bosch** (5%): NH₃-Synthese

---

## Warum sind die Kosten so ähnlich?

### 1. Flache Kostenkurve

Die Kosten ändern sich nur minimal mit den Parametern:

```
Sensitivität (Δ Kosten pro Δ Parameter):

P_el:     +50 MW  → +0.02 €/kg  (2.1%)
H₂:       +0.5 Tage → +0.003 €/kg (0.3%)
NH₃:      +0.25 Schiffe → +0.001 €/kg (0.1%)
Water:    +2000 m³ → +0.002 €/kg (0.2%)
s (Wind): +0.01 → +0.006 €/kg (0.6%)
```

**Grafisch:**
```
Kosten (€/kg)
    ^
    |
0.96|                   /
    |                  /
0.95|      [Optimum]  /
    |    ___/‾‾‾‾‾\__/
0.94|___/            
    |________________> Parameter
       min    opt   max

→ Breites Optimum (flaches Tal)
```

### 2. Dominanz fixer Kosten

**Wind-Kosten sind fix** (57% der Gesamtkosten):
- Unabhängig von P_el, H₂-Speicher, NH₃-Speicher
- Nur abhängig von s (Python-Version)

**Variable Kosten sind gering** (43%):
- Elektrolyse, Speicher, etc. haben geringen Einfluss

### 3. Kompensationseffekte

Änderungen in einem Parameter werden durch andere ausgeglichen:

**Beispiel:**
- Größerer Elektrolyseur (+CAPEX) → Mehr H₂-Produktion → Niedrigere spez. Kosten
- Kompensation: ~50% der Mehrkosten werden ausgeglichen

### 4. Diskrete Schrittweiten

Die Parameterschritte sind relativ grob:
- P_el: 50 MW Schritte (5% der Basis)
- H₂: 1 Tag Schritte (100% der Basis)
- Feinere Schritte würden mehr Abstufungen zeigen

---

## Praktische Bedeutung

### Was bedeutet das für die Anlagenplanung?

**1. Robustheit des Designs**
- ✅ System ist robust gegenüber Parameterunsicherheiten
- ✅ Kleine Abweichungen vom Optimum sind unkritisch
- ✅ Flexibilität bei der Komponentenauswahl

**2. Entscheidungsspielraum**
- ✅ Top 3-5 Konfigurationen sind praktisch gleichwertig
- ✅ Nicht-monetäre Kriterien können berücksichtigt werden:
  - Technische Risiken
  - Lieferzeiten
  - Wartungsfreundlichkeit
  - Skalierbarkeit
  - Redundanz

**3. Alternative Szenarien**
- ⚠️ Wenn sich Randbedingungen ändern (z.B. Strompreis ↑):
  - Eine andere Konfiguration kann optimal werden
  - Top 10 geben Überblick über Alternativen

**4. Sensitivitätsanalysen**
- ✅ Mit Top 10 können "Was-wäre-wenn"-Szenarien geprüft werden
- Beispiel: "Was wenn Elektrolyseur-CAPEX um 20% sinkt?"

---

## Beispiel: Sensitivitätsanalyse

### Szenario: Elektrolyseur-CAPEX sinkt um 20%

**Ursprünglich (AEL Standard):**
- 464 €/kW
- Optimum bei 1000 MW

**Nach Kostenreduktion:**
- 371 €/kW (-20%)
- Neues Optimum möglicherweise bei 1050 oder 1100 MW

**Auswirkung auf Top 10:**
```
Ursprünglich:
  Rang 1: 1000 MW → 0.9505 €/kg
  Rang 5: 1050 MW → 0.95055 €/kg (Δ = +0.005 €/kg)

Nach Reduktion:
  Rang 1: 1050 MW → 0.9320 €/kg (neu optimal!)
  Rang 5: 1000 MW → 0.9325 €/kg (Δ = +0.005 €/kg)

→ Reihenfolge ändert sich!
```

---

## Zusammenfassung

### Haupterkenntnisse:

1. **Optimale Konfiguration (Rang 1)**
   - Kleinste/effizienteste Komponenten
   - Balance zwischen CAPEX und Betrieb
   - Kosten: ~0.95 €/kg H₂

2. **Top 10 sind sehr ähnlich**
   - Kostenunterschied: <0.02%
   - Unterschiede in 1-2 Parametern
   - Flache Kostenkurve

3. **Hauptkostentreiber**
   - Wind (57%)
   - Transport (18%)
   - Cracking (14%)

4. **Sensitivität**
   - Geringe Sensitivität gegenüber Speichergrößen
   - Höhere Sensitivität gegenüber Elektrolyseur-Leistung
   - Wind-Skalierung hat mittleren Einfluss

5. **Praktische Empfehlung**
   - Nicht nur Rang 1 betrachten
   - Top 3-5 im Detail prüfen
   - Nicht-monetäre Kriterien einbeziehen
   - Sensitivitätsanalysen durchführen

**Die Top 10 Konfigurationen zeigen: Das System ist robust und bietet Flexibilität bei der Umsetzung!**
