# Optimierung: Formeln und Konfigurationen - Erklärung

## 1. Was ist die Optimierung?

Die Optimierung in diesem Projekt ist eine **parametrische Systemoptimierung** basierend auf einer techno-ökonomischen Simulation.

**Es ist KEIN mathematischer Solver**, sondern eine **strukturierte Suche über Designparameter**.

Die Optimierung sucht automatisch nach der **günstigsten Konfiguration** für die Wasserstoffproduktion, indem sie verschiedene Kombinationen von Parametern testet und für jede Kombination eine vollständige Systemsimulation durchführt.

### Aktuell optimierte Parameter (HTML-Version):

1. **P_el** (Elektrolyseur-Leistung) in MW
2. **H₂-Speicher** in Tagen
3. **NH₃-Speicher** in Schiffs-Ladungen
4. **Water Tank** in m³

### Im Python-Code werden 5 Parameter optimiert:

1. **s** (Wind-Skalierungsfaktor): 0.95 bis 1.0, Schritt 0.01
2. **P_el** (Elektrolyseur-Leistung): 1000 bis 1200 MW, Schritt 50
3. **H₂-Speicher** in Tagen: 1 bis 2, Schritt 1
4. **NH₃-Speicher** in Schiffs-Ladungen: 1 bis 1.5, Schritt 0.25
5. **Water Tank** in m³: 500 bis 4500, Schritt 2000

### Warum nur 4 Parameter im HTML-Code?

Der Parameter **s (Wind-Skalierungsfaktor)** wurde im HTML-Code weggelassen, weil:
- Er die Windkapazität skaliert (0.95 = 95% der installierten Leistung)
- Im HTML-Code wird die Windkapazität als fixer Wert behandelt (2470 MW)
- Die Optimierung fokussiert sich auf die **variablen Systemkomponenten** (Elektrolyseur, Speicher)
- Wind-Kosten sind fix und hängen nicht von den Optimierungsparametern ab

**Hinweis:** Der Parameter `s` könnte später hinzugefügt werden, um auch die Windkapazität zu optimieren.

---

## 2. Wie werden die Konfigurationen erzeugt?

### Grid Search (Rastersuche)

Die Optimierung erstellt **alle möglichen Kombinationen** der Parameter:

```javascript
// HTML-Version (4 Parameter):
P_el: 1000, 1050, 1100, 1150, 1200 MW (Schritt: 50)
H₂-Speicher: 1, 2 Tage (Schritt: 1)
NH₃-Speicher: 1, 1.25, 1.5 Schiffe (Schritt: 0.25)
Water Tank: 500, 2500, 4500 m³ (Schritt: 2000)

// Gesamt: 5 × 2 × 3 × 3 = 90 Kombinationen
```

```python
# Python-Version (5 Parameter):
s (Wind-Skalierung): 0.95, 0.96, ..., 1.0 (Schritt: 0.01) = 6 Werte
P_el: 1000, 1050, 1100, 1150, 1200 MW (Schritt: 50) = 5 Werte
H₂-Speicher: 1, 2 Tage (Schritt: 1) = 2 Werte
NH₃-Speicher: 1, 1.25, 1.5 Schiffe (Schritt: 0.25) = 3 Werte
Water Tank: 500, 2500, 4500 m³ (Schritt: 2000) = 3 Werte

// Gesamt: 6 × 5 × 2 × 3 × 3 = 540 Kombinationen
```

**Jede Kombination** ist eine "Konfiguration" (Konfig. 1, Konfig. 2, ...).

**Warum weniger Parameter im HTML-Code?**
- **Performance**: 90 Kombinationen sind schneller zu berechnen als 540
- **Fokus**: Die wichtigsten variablen Komponenten werden optimiert
- **Wind ist fix**: Die Windkapazität (2470 MW) wird als gegeben angenommen

---

## 3. Hauptformel: Kosten pro kg H₂

### Die zentrale Formel:

```
Kosten pro kg H₂ = Gesamtkosten pro Jahr / Gelieferte H₂-Menge pro Jahr
```

### In Code:
```javascript
costPerKg = totalAnnualCost / h2DeliveredAnnual
```

---

## 4. Berechnung der Gesamtkosten (totalAnnualCost)

Die Gesamtkosten setzen sich aus **8 Komponenten** zusammen:

### 4.1 Wind Farm (Fix)
```
Wind CAPEX = 2.000.000 €/MW × Wind-Kapazität (MW)
Wind OPEX = 60 €/kW/a × Wind-Kapazität (kW) × Lebensdauer (Jahre)

Wind CAPEX (annualisiert) = CAPEX × CRF
CRF = Capital Recovery Factor = r(1+r)^n / ((1+r)^n - 1)
  r = Diskontsatz (z.B. 5% = 0.05)
  n = Lebensdauer (z.B. 20 Jahre)

Wind Kosten/Jahr = Wind CAPEX (annualisiert) + Wind OPEX/Jahr
```

### 4.2 Elektrolyse (Variabel - abhängig von P_el)
```
Elektrolyse CAPEX = 464 €/kW (AEL) × P_el (kW) × 0.92 (USD→EUR)
Elektrolyse OPEX = 40.6 €/kW/a (AEL) × P_el (kW) × 0.92 × Lebensdauer

Elektrolyse CAPEX (annualisiert) = CAPEX × CRF
Elektrolyse Kosten/Jahr = CAPEX (annualisiert) + OPEX/Jahr
```

### 4.3 H₂-Speicher (Variabel - abhängig von H₂-Tagen)
```
H₂-Speicher Kapazität (t) = (Jahresproduktion H₂ (kt/a) / 365) × H₂-Tage

H₂-Speicher CAPEX = 33.000 €/t × H₂-Speicher Kapazität (t)
H₂-Speicher OPEX = CAPEX × 3% × Lebensdauer

H₂-Speicher Kosten/Jahr = CAPEX (annualisiert) + OPEX/Jahr
```

### 4.4 NH₃-Speicher (Variabel - abhängig von NH₃-Schiffen)
```
NH₃ pro Schiff (t) = (Jahresproduktion H₂ (kt/a) × 17/3) / 12 Schiffe/Jahr
NH₃-Speicher Kapazität (t) = NH₃-Schiffe × NH₃ pro Schiff (t)

NH₃-Speicher CAPEX = 810 €/t × NH₃-Speicher Kapazität (t)
NH₃-Speicher OPEX = CAPEX × 2% × Lebensdauer

NH₃-Speicher Kosten/Jahr = CAPEX (annualisiert) + OPEX/Jahr
```

### 4.5 Water Tank (Variabel - abhängig von Tank-Größe)
```
Water Tank CAPEX = 50 €/m³ × Water Tank Größe (m³)
Water Tank OPEX = CAPEX × 2% × Lebensdauer

Water Tank Kosten/Jahr = CAPEX (annualisiert) + OPEX/Jahr
```

### 4.6 RO (Umkehrosmose) - Abhängig von P_el
```
H₂ Produktion pro Stunde (kg/h) = (P_el (MW) × 1000) / 48 kWh/kg
Wasserbedarf pro Stunde (m³/h) = (H₂ (kg/h) × 10 kg Wasser/kg H₂) / 1000
RO Kapazität (m³/Tag) = Wasserbedarf (m³/h) × 24

RO CAPEX = 1200 €/(m³/Tag) × RO Kapazität (m³/Tag)
RO OPEX = CAPEX × 5% × Lebensdauer

RO Kosten/Jahr = CAPEX (annualisiert) + OPEX/Jahr
```

### 4.7 Haber-Bosch (Fix - abhängig von H₂-Produktion)
```
NH₃ Produktion (t/a) = H₂ Produktion (kt/a) × 17/3
HB Kapazität (t NH₃/Tag) = NH₃ Produktion (t/a) / 365
HB Kapazität (t NH₃/Jahr) = HB Kapazität (t/Tag) × 365

HB CAPEX = 491.4 €/(t NH₃/Jahr) × HB Kapazität (t NH₃/Jahr)
HB OPEX = 16.8 M€/Jahr (berechnet aus 24.57 $/t NH₃)

HB Kosten/Jahr = CAPEX (annualisiert) + OPEX/Jahr
```

### 4.8 N₂ (ASU) - Abhängig von Haber-Bosch
```
N₂ Bedarf (kg N₂/kg NH₃) = 28/34 = 0.824
N₂ Kapazität (kg N₂/h) = HB Kapazität (t NH₃/h) × 1000 × 0.824

ASU CAPEX = 1700 €/(kg N₂/h) × N₂ Kapazität (kg N₂/h)
ASU OPEX = CAPEX × 3% × Lebensdauer

ASU Kosten/Jahr = CAPEX (annualisiert) + OPEX/Jahr
```

### 4.9 Transport & Cracking (Fix - werden aus Hauptberechnung übernommen)
```
Transport Kosten/Jahr = aus DOM-Element (falls verfügbar)
Cracking Kosten/Jahr = aus DOM-Element (falls verfügbar)
```

### 4.10 Gesamtkosten
```
totalAnnualCost = Wind + Elektrolyse + RO + N₂ + HB + 
                  H₂-Speicher + NH₃-Speicher + Water Tank + 
                  Transport + Cracking
```

---

## 5. Berechnung der gelieferten H₂-Menge (h2DeliveredAnnual)

### 5.1 Ketteneffizienz (Chain Efficiency)

Die Ketteneffizienz berücksichtigt **alle Verluste** entlang der Kette:

```
Ketteneffizienz = (1 - Haber-Bosch Verlust/100) × 
                  (1 - Storage Verlust/100) × 
                  (1 - NH₃ Shipping Verlust/100) × 
                  (Cracking Effizienz/100)
```

**Beispiel:**
- Haber-Bosch Verlust: 5% → Faktor: 0.95
- Storage Verlust: 0.5% → Faktor: 0.995
- NH₃ Shipping Verlust: 0.1% → Faktor: 0.999
- Cracking Effizienz: 95% → Faktor: 0.95

```
Ketteneffizienz = 0.95 × 0.995 × 0.999 × 0.95 = 0.897 (89.7%)
```

### 5.2 Gelieferte H₂-Menge

```
H₂ Referenz (kg/a) = Jahresproduktion H₂ (kt/a) × 1.000.000
Gelieferte H₂ (kg/a) = H₂ Referenz (kg/a) × Ketteneffizienz
```

**Beispiel:**
- H₂ Produktion: 120.8 kt/a = 120.800.000 kg/a
- Ketteneffizienz: 0.897
- Gelieferte H₂: 120.800.000 × 0.897 = 108.357.600 kg/a = 108.36 kt/a

---

## 6. Finale Kostenberechnung

```
Kosten pro kg H₂ = totalAnnualCost (€/Jahr) / h2DeliveredAnnual (kg/Jahr)
```

**Beispiel:**
- Gesamtkosten: 76.5 M€/Jahr = 76.500.000 €/Jahr
- Gelieferte H₂: 108.357.600 kg/Jahr
- Kosten pro kg: 76.500.000 / 108.357.600 = **0.706 €/kg**

---

## 7. Wie funktioniert die Optimierung?

### Schritt 1: Kombinationen generieren
```
Für jede Kombination von:
  - P_el: 1000, 1050, 1100, 1150, 1200 MW
  - H₂-Tage: 1, 2 Tage
  - NH₃-Schiffe: 1, 1.25, 1.5 Schiffe
  - Water Tank: 500, 2500, 4500 m³

→ 90 verschiedene Konfigurationen
```

### Schritt 2: Für jede Konfiguration berechnen
1. **Speicher-Kapazitäten** aus Parametern ableiten
2. **Alle Kostenkomponenten** berechnen
3. **Gesamtkosten** summieren
4. **Gelieferte H₂-Menge** berechnen
5. **Kosten pro kg** = Gesamtkosten / Gelieferte H₂

### Schritt 3: Sortieren und Auswählen
```
Alle Konfigurationen nach Kosten pro kg sortieren
→ Konfig. 1 = Günstigste
→ Konfig. 2 = Zweitgünstigste
...
→ Konfig. 10 = Zehntgünstigste
```

### Schritt 4: Top 10 anzeigen
Das Diagramm zeigt die **10 günstigsten Konfigurationen**:
- **X-Achse**: Konfig. 1 bis Konfig. 10
- **Y-Achse**: Kosten in €/kg H₂
- **Balken**: Höhe = Kosten pro kg (je niedriger, desto besser)

---

## 8. Warum sind die Y-Achsen-Werte alle gleich?

Das ist ein **Anzeigefehler** im Diagramm. Die tatsächlichen Werte sind unterschiedlich, aber die Y-Achsen-Beschriftung zeigt fälschlicherweise alle den gleichen Wert.

**Die Balkenhöhen zeigen die korrekten Werte!**
- Konfig. 1 hat den **niedrigsten Balken** = günstigste Lösung
- Konfig. 10 hat den **höchsten Balken** = teuerste der Top 10

---

## 9. Beispiel-Berechnung für eine Konfiguration

### Konfiguration: P_el=1000 MW, H₂=1 Tag, NH₃=1 Schiff, Water=500 m³

**1. Speicher-Kapazitäten:**
```
H₂-Speicher = (120.8 kt/a / 365) × 1 Tag = 331 t
NH₃-Speicher = 1 Schiff × (120.8 × 17/3 / 12) = 57.0 t
```

**2. Kostenkomponenten (vereinfacht):**
```
Wind: 0.4 M€/a (fix)
Elektrolyse: 58.8 M€/a (1000 MW)
RO: 0.55 M€/a
N₂: 0.008 M€/a
HB: 16.8 M€/a
H₂-Speicher: 0.005 M€/a (331 t)
NH₃-Speicher: 0.001 M€/a (57 t)
Water Tank: 0.0005 M€/a (500 m³)
Transport: 0 M€/a (aus DOM)
Cracking: 0 M€/a (aus DOM)

Gesamt: ~76.5 M€/a
```

**3. Gelieferte H₂:**
```
H₂ Referenz: 120.8 kt/a = 120.800.000 kg/a
Ketteneffizienz: 0.897
Gelieferte H₂: 108.357.600 kg/a
```

**4. Kosten pro kg:**
```
Kosten pro kg = 76.500.000 €/a / 108.357.600 kg/a = 0.706 €/kg
```

---

## 10. Was bedeutet "Optimale Konfiguration"?

Die **optimale Konfiguration** (Konfig. 1) ist die Kombination von:
- P_el (MW)
- H₂-Speicher (Tage)
- NH₃-Speicher (Schiffe)
- Water Tank (m³)

...die die **niedrigsten Kosten pro kg H₂** ergibt.

**Ziel:** Minimierung der Produktionskosten bei gegebener H₂-Produktionsmenge.

---

## 11. Warum werden manche Konfigurationen abgelehnt?

Eine Konfiguration wird abgelehnt, wenn:
- Ketteneffizienz ≤ 0 oder > 1
- Gelieferte H₂-Menge ≤ 0
- Gesamtkosten ≤ 0 oder NaN
- Kosten pro kg ≤ 0, > 1000 €/kg oder NaN

---

## 12. Zusammenfassung

1. **Grid Search** erstellt alle möglichen Kombinationen
2. **Für jede Kombination** werden Kosten und gelieferte H₂-Menge berechnet
3. **Kosten pro kg** = Gesamtkosten / Gelieferte H₂
4. **Sortierung** nach Kosten pro kg (niedrigste zuerst)
5. **Top 10** werden angezeigt im Diagramm

**Die beste Konfiguration** hat den niedrigsten Wert für "Kosten pro kg H₂".

---

## 13. Warum nur 4 Parameter statt 5? (Detaillierte Erklärung)

### Vergleich: Python vs HTML

| Parameter | Python-Code | HTML-Code | Grund |
|-----------|-------------|-----------|-------|
| **s** (Wind-Skalierung) | ✅ 0.95-1.0 | ❌ Nicht optimiert | Wind ist fix (2470 MW) |
| **P_el** (Elektrolyseur) | ✅ 1000-1200 MW | ✅ 1000-1200 MW | Variable Komponente |
| **H₂-Speicher** | ✅ 1-2 Tage | ✅ 1-2 Tage | Variable Komponente |
| **NH₃-Speicher** | ✅ 1-1.5 Schiffe | ✅ 1-1.5 Schiffe | Variable Komponente |
| **Water Tank** | ✅ 500-4500 m³ | ✅ 500-4500 m³ | Variable Komponente |

### Was ist der Parameter "s" (Wind-Skalierungsfaktor)?

Der Parameter **s** skaliert die Windkapazität:
- **s = 1.0**: 100% der installierten Windkapazität (2470 MW)
- **s = 0.95**: 95% der installierten Windkapazität (2346.5 MW)
- **s = 0.98**: 98% der installierten Windkapazität (2420.6 MW)

**Im Python-Code:**
```python
# Wind-Leistung wird skaliert
p_wind_scaled = p_wind_rated_mw * s

# Beispiel: s=0.95 → 2470 MW × 0.95 = 2346.5 MW
```

### Warum wurde "s" im HTML-Code weggelassen?

1. **Wind-Kapazität ist fix im HTML-Modell:**
   - Die Windkapazität wird als gegebener Wert (2470 MW) behandelt
   - Sie wird nicht als optimierbare Variable betrachtet
   - Wind-Kosten sind fix und hängen nicht von den Optimierungsparametern ab

2. **Performance:**
   - **4 Parameter**: 90 Kombinationen → schnell (1-3 Minuten)
   - **5 Parameter**: 540 Kombinationen (6× mehr) → 6-18 Minuten
   - Für eine Web-Anwendung ist Geschwindigkeit wichtig

3. **Fokus auf variable Komponenten:**
   - Die Optimierung konzentriert sich auf die **variablen Systemkomponenten**
   - Elektrolyseur, Speicher und Water Tank können angepasst werden
   - Wind ist eine gegebene Infrastruktur

4. **Praktische Relevanz:**
   - In der Praxis wird die Windkapazität meist als **gegebene Größe** betrachtet
   - Die Optimierung sucht die beste Kombination von **Elektrolyseur und Speichern**
   - Wind-Kosten sind unabhängig von den Optimierungsparametern

### Mögliche Erweiterung

Der Parameter **s** könnte später hinzugefügt werden, um auch die Windkapazität zu optimieren. Dies würde jedoch:

- ✅ **Vorteile:**
  - Vollständigere Optimierung (wie im Python-Code)
  - Berücksichtigung von Windkapazitäts-Variationen
  - Mehr Kombinationen = bessere Lösung möglich

- ❌ **Nachteile:**
  - Berechnungszeit erhöht sich um Faktor 6 (90 → 540 Kombinationen)
  - Wind-Kostenberechnung muss angepasst werden
  - Komplexität des Optimierungsproblems steigt
  - Für Web-Anwendung möglicherweise zu langsam

### Empfehlung

Für die **HTML-Version** ist die Optimierung mit **4 Parametern** sinnvoll, weil:
- Sie fokussiert sich auf die **wichtigsten variablen Komponenten**
- Die Berechnung ist **schnell genug** für eine Web-Anwendung
- Die Windkapazität wird als **gegebene Infrastruktur** behandelt
- Die Ergebnisse sind **praktisch relevant** und **verständlich**

Wenn eine vollständigere Optimierung benötigt wird, sollte der Python-Code verwendet werden, der alle 5 Parameter optimiert.
