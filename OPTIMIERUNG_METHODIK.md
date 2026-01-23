# Parametrische Systemoptimierung: Detaillierte Methodik

## Überblick

Die Optimierung in diesem Projekt ist eine **parametrische Systemoptimierung** basierend auf einer techno-ökonomischen Simulation. Es ist **KEIN** mathematischer Solver, sondern eine **strukturierte Suche über Designparameter** (Brute-Force Grid Search).

---

## Die 9 Schritte der Optimierung

### Schritt 1: Systemgrenze definieren

Das System umfasst alle relevanten Komponenten der Wasserstoff-Produktionskette:

**Komponenten:**
1. **Windpark** - Stromerzeugung (Offshore)
2. **Elektrolyse** - H₂-Produktion (AEL oder PEM)
3. **Wasserstoffspeicher** - H₂-Lagerung (flüssig)
4. **Haber-Bosch-Synthese** - NH₃-Produktion
5. **Stickstoffversorgung** - ASU (Air Separation Unit)
6. **Ammoniakspeicher** - NH₃-Lagerung
7. **Wasseraufbereitung** - RO (Reverse Osmosis)
8. **Wassertank** - Wasserspeicherung
9. **Transport** - Seeschiffstransport
10. **Cracking** - NH₃ → H₂ Rückumwandlung

**Systemgrenze:**
- Vom Windrad bis zum gelieferten Wasserstoff
- Alle Umwandlungs- und Speicherungsverluste werden berücksichtigt
- Alle CAPEX, OPEX und variablen Kosten werden erfasst

Alle Komponenten werden **konsistent** im Python-Modell abgebildet.

---

### Schritt 2: Entscheidungsvariablen auswählen

Dies sind die Parameter, die während der Optimierung variiert werden:

#### Python-Code (5 Parameter):

| Parameter | Symbol | Bereich | Schritt | Einheit |
|-----------|--------|---------|---------|---------|
| Wind-Skalierung | s | 0.95 - 1.0 | 0.01 | - |
| Elektrolyseur-Leistung | P_el | 1000 - 1200 | 50 | MW |
| H₂-Speicher | h2_days | 1 - 2 | 1 | Tage |
| NH₃-Speicher | nh3_ships | 1 - 1.5 | 0.25 | Schiffe |
| Wassertank | water_tank | 500 - 4500 | 2000 | m³ |

**Anzahl Kombinationen:** 6 × 5 × 2 × 3 × 3 = **540**

#### HTML-Code (4 Parameter):

Identisch, aber **ohne** "s" (Wind ist fix bei 2470 MW)

**Anzahl Kombinationen:** 5 × 2 × 3 × 3 = **90**

**Jede Kombination repräsentiert ein Systemdesign.**

---

### Schritt 3: Zeitaufgelöste Simulation durchführen

#### Python-Code (Vollständig):

Das System wird **stündlich** über ein repräsentatives Jahr simuliert (8760 Stunden):

1. **Windenergieerzeugung**
   - Windprofil aus Excel-Datei laden
   - Skalierung mit Faktor `s`
   - Stündliche Leistung: `P_wind(t) = s × P_wind_profile(t)`

2. **Elektrolyseur-Dispatch**
   - Mindestlast berücksichtigen (z.B. 20% für AEL)
   - Rampenbeschränkungen (z.B. ±10%/h)
   - Verfügbarkeit (z.B. 95%)
   - H₂-SOC-gesteuerte Steuerung (Start/Stop-Schwellwerte)

3. **H₂-Storage Tracking**
   - Stündliche Ein-/Ausspeicherung
   - Wirkungsgrade (eta_in, eta_out)
   - Boil-off-Verluste
   - Re-Liquefaction
   - SOC-Grenzen (0% - 100%)

4. **Haber-Bosch Betrieb**
   - NH₃-SOC-gesteuerte Steuerung
   - Mindestlast (z.B. 40%)
   - Rampenbeschränkungen
   - N₂-Bedarf aus ASU

5. **NH₃-Storage Tracking**
   - Stündliche Ein-/Ausspeicherung
   - Kühlungsenergiebedarf
   - Schiffsverladung (12 Schiffe/Jahr)
   - Verladelogik und Fehlerzähler

6. **Wasser-System**
   - Wasserbedarf aus Elektrolyse
   - RO-Entsalzung
   - Tankspeicherung mit Verlusten

7. **Verluste und Wirkungsgrade**
   - Haber-Bosch: 5% Verlust
   - Storage: 0.5% Verlust
   - Shipping: 0.1% Verlust
   - Cracking: 95% Effizienz

**Ergebnis:** Stündliche Zeitreihen für alle Zustandsgrößen (SOC, Leistungen, Verluste, etc.)

#### HTML-Code (Vereinfacht):

**Keine** zeitaufgelöste Simulation!

Stattdessen:
- Statische Jahresbilanzen
- Vereinfachte Ketteneffizienz: `η_chain = (1-0.05) × (1-0.005) × (1-0.001) × 0.95 = 0.897`
- Keine dynamischen Effekte (Curtailment, Rampen, SOC-Schwankungen)

---

### Schritt 4: Technische Machbarkeit prüfen

#### Python-Code:

Nur Konfigurationen, die **alle** Kriterien erfüllen, werden behalten:

**Kriterien:**
1. ✅ Jährliches H₂-Produktionsziel erreicht (z.B. 120.8 kt/a)
2. ✅ Speicherrestriktionen nicht verletzt (0% ≤ SOC ≤ 100%)
3. ✅ Negative Speicherstände nie aufgetreten
4. ✅ Alle 12 Schiffe erfolgreich beladen
5. ✅ Keine kritischen Fehler (z.B. Wassermangel)

**Bei Nicht-Erfüllung:** Konfiguration wird verworfen.

#### HTML-Code:

Vereinfachte Prüfungen:
1. ✅ Ketteneffizienz > 0 und ≤ 1
2. ✅ Gelieferte H₂-Menge > 0
3. ✅ Kosten pro kg > 0 und < 1000 €/kg
4. ✅ Keine NaN oder Infinity-Werte

---

### Schritt 5: Key Performance Indicators (KPIs) extrahieren

#### Python-Code (aus Simulation):

Die folgenden KPIs werden aus der stündlichen Simulation berechnet:

**Produktions-KPIs:**
- Jährliche H₂-Produktion (t/a)
- Jährliche NH₃-Produktion (t/a)
- Gelieferte H₂-Menge nach Verlusten (t/a)

**Speicher-KPIs:**
- Maximaler H₂-Speicherstand (t)
- Maximaler NH₃-Speicherstand (t)
- Maximaler Wasserspeicherstand (m³)
- Mittlerer SOC für alle Speicher (%)

**Energie-KPIs:**
- Curtailment (GWh/a)
- Energieverbrauch pro Komponente (GWh/a):
  - Elektrolyse
  - RO
  - Haber-Bosch
  - N₂ (ASU)
  - H₂-Storage (Liquefaction, Re-liquefaction)
  - NH₃-Storage (Kühlung)

**Betriebs-KPIs:**
- Elektrolyse Volllaststunden (h/a)
- Haber-Bosch Volllaststunden (h/a)
- Anzahl Schiffsverladefehler (-)

Diese KPIs werden in `Simulierte_Speicherstände.csv` geschrieben.

#### HTML-Code (vereinfacht):

- Gelieferte H₂-Menge (kg/a)
- Ketteneffizienz (-)
- Gesamtkosten (€/a)
- Kosten pro kg H₂ (€/kg)

---

### Schritt 6: Kostenberechnung anwenden

Für jede machbare Konfiguration werden alle Kosten berechnet.

#### 6.1 CAPEX-Berechnung

**Formel:**
```
CAPEX_Komponente = Kapazität × Spezifische_CAPEX
```

**Beispiele:**

| Komponente | Kapazität | Spez. CAPEX | CAPEX |
|------------|-----------|-------------|-------|
| Wind | 2470 MW | 2 Mio €/MW | 4.94 Mrd € |
| Elektrolyse | 1000 MW | 464 €/kW | 464 Mio € |
| H₂-Speicher | 331 t | 33000 €/t | 10.9 Mio € |
| NH₃-Speicher | 57 t | 810 €/t | 0.046 Mio € |
| RO | 3014 m³/d | 1000 €/(m³/d) | 3.0 Mio € |
| ASU | 49.5 kg N₂/h | 1700 €/(kg/h) | 0.084 Mio € |
| Haber-Bosch | 1875 t NH₃/a | 491.4 €/(t/a) | 0.92 Mio € |

**Gesamt-CAPEX:** ~5.4 Mrd €

#### 6.2 CAPEX-Annualisierung

**Capital Recovery Factor (CRF):**
```
CRF = [r × (1+r)^n] / [(1+r)^n - 1]

wobei:
  r = Diskontsatz (z.B. 7%)
  n = Projektlaufzeit (z.B. 20 Jahre)
```

**Annualisierte CAPEX:**
```
CAPEX_annualisiert = CAPEX × CRF
```

**Beispiel:**
```
r = 0.07, n = 20
CRF = [0.07 × (1.07)^20] / [(1.07)^20 - 1] = 0.0944

CAPEX_annualisiert = 5.4 Mrd € × 0.0944 = 509.8 Mio €/a
```

#### 6.3 OPEX-Berechnung

**OPEX wird typischerweise als Anteil von CAPEX berechnet:**
```
OPEX_jährlich = CAPEX × OPEX_Anteil
```

**Oder als spezifische Werte:**
```
OPEX_jährlich = Kapazität × Spez_OPEX
```

**Beispiele:**

| Komponente | OPEX-Anteil | OPEX |
|------------|-------------|------|
| Wind | 3% von CAPEX | 148.2 Mio €/a |
| Elektrolyse | 3% von CAPEX | 13.9 Mio €/a |
| H₂-Speicher | 3% von CAPEX | 0.33 Mio €/a |
| NH₃-Speicher | 3% von CAPEX | 0.0014 Mio €/a |
| RO | 3% von CAPEX | 0.09 Mio €/a |
| ASU | 3% von CAPEX | 0.0025 Mio €/a |
| Haber-Bosch | 16.8 Mio €/a | 16.8 Mio €/a |

**Gesamt-OPEX:** ~179.3 Mio €/a

#### 6.4 Variable Kosten

**Variable Kosten hängen von der Nutzung ab:**

- **Stromkosten:** Bereits in Wind-LCOE enthalten (internal) oder separat (external)
- **Transportkosten:** €/t NH₃ oder €/tkm
- **Wartungskosten:** €/Betriebsstunde

**In diesem Projekt:**
- Stromkosten sind in Wind-CAPEX/OPEX enthalten (LCOE-Ansatz)
- Transportkosten werden separat berechnet

#### 6.5 Gesamtkosten

```
Gesamtkosten (€/a) = CAPEX_annualisiert + OPEX_jährlich + Variable_Kosten

Beispiel:
  = 509.8 + 179.3 + 0
  = 689.1 Mio €/a
```

---

### Schritt 7: Zielfunktion bewerten

Die Zielfunktion ist das **Optimierungskriterium**.

#### Zielfunktion in diesem Projekt:

```
Zielfunktion = Kosten pro kg H₂ = Gesamtkosten (€/a) / Gelieferte H₂ (kg/a)
```

**Beispiel:**
```
Gesamtkosten = 689.1 Mio €/a = 689100000 €/a
Gelieferte H₂ = 120800 t/a × 0.897 (Ketteneff.) = 108358 t/a = 108358000 kg/a

Kosten pro kg = 689100000 / 108358000 = 6.36 €/kg
```

**Ziel:** Minimierung dieser Zielfunktion!

**Alternative Zielfunktionen** (nicht in diesem Projekt):
- Minimiere Gesamtsystemkosten (€)
- Minimiere CO₂-Emissionen (t CO₂/kg H₂)
- Maximiere Systemeffizienz (%)
- Multi-objektiv: Kosten UND Emissionen

---

### Schritt 8: Vergleich und Auswahl

Alle Konfigurationen werden nach ihrer Zielfunktion sortiert:

**Beispiel (Top 10):**

| Rang | s | P_el | H₂ | NH₃ | Water | Kosten |
|------|---|------|----|-----|-------|--------|
| 1 | 0.95 | 1000 | 1.0 | 1.00 | 500 | **0.7067 €/kg** |
| 2 | 0.96 | 1000 | 1.0 | 1.00 | 500 | 0.7089 €/kg |
| 3 | 0.95 | 1050 | 1.0 | 1.00 | 500 | 0.7112 €/kg |
| 4 | 0.97 | 1000 | 1.0 | 1.00 | 500 | 0.7135 €/kg |
| 5 | 0.95 | 1000 | 1.5 | 1.00 | 500 | 0.7158 €/kg |
| ... | ... | ... | ... | ... | ... | ... |
| 10 | 0.98 | 1050 | 1.5 | 1.25 | 2500 | 0.7523 €/kg |

**Die Konfiguration mit dem niedrigsten Wert ist die optimale Lösung.**

In diesem Beispiel:
- **s = 0.95** (95% Windkapazität)
- **P_el = 1000 MW** (Elektrolyse)
- **H₂ = 1.0 Tage** (331 t)
- **NH₃ = 1.00 Schiffe** (57044 t)
- **Water = 500 m³**
- **Kosten = 0.7067 €/kg**

#### Interpretation der Top 10 Konfigurationen

Das Diagramm zeigt die **10 günstigsten Konfigurationen** sortiert nach Kosten:

**Wichtige Beobachtungen:**

1. **Konfig. 1 (Dunkelrot)**: Die beste Lösung
   - Niedrigste Kosten
   - Optimal für das gegebene System

2. **Konfig. 2-10 (Orange/Rot)**: Alternative Lösungen
   - Nur geringfügig teurer als Konfig. 1
   - Können bei geänderten Randbedingungen relevant werden

3. **Kostendifferenz**: Typischerweise 0.1-5% zwischen Rang 1 und Rang 10
   - Beispiel: 0.9505 €/kg (Rang 1) vs. 0.9507 €/kg (Rang 10) = 0.02% Differenz

**Warum sind die Kosten so ähnlich?**

- Die Top 10 repräsentieren **ähnliche Systemdesigns**
- Unterschiede liegen meist in **einem oder zwei Parametern**
- Flache Kostenkurve → System ist robust gegenüber kleinen Parameteränderungen

**Beispiel: Top 10 Detaillierte Konfigurationen**

| Rang | s | P_el (MW) | H₂ (Tage) | NH₃ (Schiffe) | Water (m³) | Kosten (€/kg) | Δ zu Rang 1 |
|------|---|-----------|-----------|---------------|------------|---------------|-------------|
| 1 | 0.95 | 1000 | 1.0 | 1.00 | 500 | 0.9505 | 0.00% |
| 2 | 0.95 | 1000 | 1.0 | 1.25 | 500 | 0.95051 | 0.001% |
| 3 | 0.96 | 1000 | 1.0 | 1.00 | 500 | 0.95052 | 0.002% |
| 4 | 0.95 | 1000 | 1.5 | 1.00 | 500 | 0.95053 | 0.003% |
| 5 | 0.95 | 1050 | 1.0 | 1.00 | 500 | 0.95055 | 0.005% |
| 6 | 0.96 | 1000 | 1.0 | 1.25 | 500 | 0.95056 | 0.006% |
| 7 | 0.95 | 1000 | 1.0 | 1.00 | 2500 | 0.95058 | 0.008% |
| 8 | 0.97 | 1000 | 1.0 | 1.00 | 500 | 0.95062 | 0.012% |
| 9 | 0.96 | 1050 | 1.0 | 1.00 | 500 | 0.95065 | 0.015% |
| 10 | 0.95 | 1000 | 1.5 | 1.25 | 500 | 0.95068 | 0.018% |

**Analyse der Top 10:**

1. **Windkapazität (s)**
   - Die meisten Top-Konfigurationen haben s = 0.95 oder 0.96
   - **Erkenntnis**: Leicht reduzierte Windkapazität ist optimal
   - **Grund**: Balance zwischen CAPEX und Auslastung

2. **Elektrolyseur-Leistung (P_el)**
   - Die meisten haben P_el = 1000 MW
   - Nur wenige mit 1050 MW
   - **Erkenntnis**: Kleinere Elektrolyseure sind kosteneffizienter
   - **Grund**: Niedrigere CAPEX überwiegt Effizienzvorteile

3. **H₂-Speicher (Tage)**
   - Meistens 1.0 Tage (Minimum)
   - Einige mit 1.5 Tagen
   - **Erkenntnis**: Minimaler H₂-Speicher ist optimal
   - **Grund**: Hohe spezifische Kosten für LH₂-Speicherung

4. **NH₃-Speicher (Schiffe)**
   - Variiert zwischen 1.00 und 1.25 Schiffe
   - **Erkenntnis**: Kleiner NH₃-Speicher bevorzugt
   - **Grund**: NH₃-Speicherung ist günstiger als H₂, aber mehr als minimal nötig erhöht Kosten

5. **Wassertank (m³)**
   - Meistens 500 m³ (Minimum)
   - Selten 2500 m³
   - **Erkenntnis**: Minimaler Wassertank ausreichend
   - **Grund**: Geringer Einfluss auf Gesamtkosten

**Sensitivität:**

Die geringen Kostenunterschiede zeigen:
- ✅ System ist **robust** gegenüber Parameteränderungen
- ✅ Mehrere Designs sind **nahezu gleichwertig**
- ✅ Flexibilität bei der Umsetzung (z.B. größerer Speicher für Redundanz)

**Praktische Empfehlung:**

Nicht nur Rang 1 betrachten, sondern:
1. **Top 3-5 Konfigurationen** im Detail prüfen
2. **Nicht-monetäre Kriterien** einbeziehen:
   - Technische Risiken
   - Lieferzeiten
   - Wartungsfreundlichkeit
   - Skalierbarkeit
3. **Sensitivitätsanalysen** durchführen:
   - Was passiert bei geänderten Strompreisen?
   - Wie reagiert das System auf Komponentenausfälle?

---

### Schritt 9: Nachbearbeitung und Konsistenzprüfung

Die Ergebnisse werden auf **Plausibilität** geprüft:

#### 9.1 Python-Code:

**Konsistenzprüfungen:**
1. ✅ Sind die Speichergrößen aus der Simulation realistisch?
2. ✅ Stimmen die Energiebilanzen (Erzeugung = Verbrauch + Verluste)?
3. ✅ Sind alle Kosten positiv und plausibel?
4. ✅ Sind die KPIs konsistent mit den Eingabeparametern?

**Datenübertragung:**
- Designgrößen aus der Optimierung (z.B. max. Speicher aus CSV) werden zum **HTML-Kostenmodell** übertragen
- Konsistenz zwischen **detaillierter Simulation** und **vereinfachter Kostenberechnung** sicherstellen

#### 9.2 HTML-Code:

**Validierungen:**
1. ✅ Prüfung auf ungültige Werte (NaN, Infinity, negative Kosten)
2. ✅ Vergleich zwischen aktueller und optimierter Konfiguration
3. ✅ Berechnung der Kosteneinsparung
4. ✅ Visuelle Darstellung der Top 10

**Ausgabe:**
- Beste Konfiguration wird angezeigt
- Vergleich mit aktueller Konfiguration
- Kosteneinsparung in €/kg und %
- Diagramm der Top 10 Konfigurationen

---

## Vergleich: Python vs. HTML Optimierung

### Python-Optimierung (Vollständig)

**Vorteile:**
- ✅ Zeitaufgelöste Simulation (stündlich, 8760 Stunden/Jahr)
- ✅ Berücksichtigung von Speicherdynamik und SOC
- ✅ Realistische Abbildung von Rampen, Mindestlast, Verfügbarkeit
- ✅ Berechnung von Curtailment und Schiffsverladefehlern
- ✅ 5 Optimierungsparameter (inkl. Wind-Skalierung)
- ✅ KPIs aus Simulation (Max SOC, Energieverbrauch, etc.)
- ✅ Genauere Kostenberechnung

**Nachteile:**
- ❌ Langsam (540 Kombinationen × Simulation)
- ❌ Benötigt Python-Umgebung
- ❌ Benötigt Windprofil-Datei (Excel)
- ❌ Keine interaktive Visualisierung

### HTML-Optimierung (Vereinfacht)

**Vorteile:**
- ✅ Schnell (90-540 Kombinationen, reine Kostenberechnung)
- ✅ Läuft im Browser (keine Installation)
- ✅ Interaktiv und visuell
- ✅ Sofortige Ergebnisse
- ✅ Einfach zu bedienen

**Nachteile:**
- ❌ Keine zeitaufgelöste Simulation
- ❌ Keine Speicherdynamik
- ❌ Vereinfachte Annahmen
- ❌ Ketteneffizienz statisch (keine Curtailment-Berechnung)
- ❌ Weniger genau

---

## Fazit: Brute-Force Parametrische Optimierung

Dieser Ansatz ist eine **Brute-Force Parametrische Optimierung mit physikalischen Constraints**, die häufig in der Energiesystemmodellierung verwendet wird.

### Vorteile:

1. **Transparenz**
   - Alle Annahmen sind nachvollziehbar
   - Jede Berechnung kann manuell überprüft werden
   - Keine "Black Box"

2. **Rückverfolgbarkeit**
   - Jede Konfiguration kann einzeln geprüft werden
   - Ergebnisse sind reproduzierbar
   - Sensitivitätsanalysen einfach möglich

3. **Robustheit**
   - Keine Konvergenzprobleme wie bei mathematischen Solvern
   - Funktioniert auch mit diskontinuierlichen Funktionen
   - Keine Anfangswerte erforderlich

4. **Flexibilität**
   - Beliebige Zielfunktionen und Constraints möglich
   - Einfache Erweiterung um neue Parameter
   - Multi-objektiv-Optimierung möglich

### Nachteile:

1. **Rechenzeit**
   - Wächst exponentiell mit Anzahl der Parameter
   - Beispiel: 5 Parameter mit je 10 Werten = 100.000 Kombinationen

2. **Auflösung**
   - Nur diskrete Werte werden getestet
   - Optimum liegt möglicherweise zwischen den Testpunkten

3. **Globales Optimum**
   - Möglicherweise nicht gefunden (abhängig von Schrittweite)
   - Lokale Optima werden nicht erkannt

### Typische Anwendung:

Diese Methode wird häufig in Studien zur Energiesystemplanung verwendet, z.B.:

- ✅ Dimensionierung von Power-to-X-Anlagen
- ✅ Optimierung von Speichersystemen
- ✅ Auslegung von Wasserstoff-Infrastrukturen
- ✅ Netzplanung und -ausbau
- ✅ Sektorenkopplung (Power-to-Gas, Power-to-Heat)

**Literatur:**
- Rueda et al.: "Design and economic evaluation of a hydrogen supply chain from solar/wind energy" (2018)
- Giampieri et al.: "Comparative life cycle cost analysis of electric and hydrogen buses" (2021)
- Brown et al.: "PyPSA-Eur: An open optimisation model of the European transmission system" (2018)

---

## Zusammenfassung

Die **parametrische Systemoptimierung** in diesem Projekt:

1. ✅ Testet systematisch alle Kombinationen von 4-5 Designparametern
2. ✅ Führt für jede Kombination eine Kostenberechnung (HTML) oder Simulation (Python) durch
3. ✅ Bewertet jede Konfiguration anhand der Zielfunktion (Kosten pro kg H₂)
4. ✅ Wählt die beste Konfiguration aus
5. ✅ Stellt einen guten Kompromiss zwischen Genauigkeit, Transparenz und Rechenaufwand dar

**Diese Methode ist Standard in der Energiesystemplanung und liefert robuste, nachvollziehbare Ergebnisse.**
