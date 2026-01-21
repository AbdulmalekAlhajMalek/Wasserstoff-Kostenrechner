# Wasserstoff-Kostenrechner / Hydrogen Cost Calculator

Ein Programm zur Berechnung der Entstehungskosten von Wasserstoff, der in Paraguay produziert und in Deutschland verbraucht wird.

A program for calculating the production costs of hydrogen produced in Paraguay and consumed in Germany.

## 🖥️ Windows Desktop-App

### Installation und Start / Installation and Start:

**Einfachste Methode / Easiest Method:**
```bash
start_app.bat
```

**Oder manuell / Or manually:**
```bash
python wasserstoff_komplett.py
```

Die Windows Desktop-App bietet / The Windows Desktop App provides:
- ✅ Native Windows-Anwendung (kein Browser nötig) / Native Windows application (no browser required)
- ✅ Einfache Bedienung mit Eingabefeldern / Easy-to-use input fields
- ✅ Detaillierte Kostenaufstellung / Detailed cost breakdown
- ✅ Alle Parameter anpassbar / All parameters adjustable
- ✅ Info-Icons mit Erklärungen / Info icons with explanations
- ✅ Gestapeltes Säulendiagramm / Stacked bar chart
- ✅ Strukturierte Kosten (Variable, CapEx, OpEx) / Structured costs (Variable, CapEx, OpEx)
- ✅ Keine zusätzlichen Installationen nötig (tkinter ist in Python enthalten) / No additional installations needed (tkinter is included in Python)

## 🌐 Web-Anwendung / Web Application

### Installation und Start / Installation and Start:

**Einfachste Methode / Easiest Method:**
Einfach die Datei `wasserstoff_rechner_erweitert.html` im Browser öffnen (Doppelklick).

Simply open the file `wasserstoff_rechner_erweitert.html` in your browser (double-click).

**Oder mit Flask-Server / Or with Flask Server:**

1. **Abhängigkeiten installieren / Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Web-Server starten / Start web server:**
```bash
python app.py
```

3. **Im Browser öffnen / Open in browser:**
```
http://localhost:5000
```

Die Web-Anwendung bietet / The web application provides:
- ✅ Interaktives Eingabeformular / Interactive input form
- ✅ Detaillierte Kostenaufstellung / Detailed cost breakdown
- ✅ Übersichtliche Ergebnisdarstellung / Clear result display
- ✅ Info-Icons mit Tooltips / Info icons with tooltips
- ✅ Gestapeltes Säulendiagramm (Chart.js) / Stacked bar chart (Chart.js)
- ✅ Strukturierte Kosten (Variable, CapEx, OpEx) / Structured costs (Variable, CapEx, OpEx)
- ✅ Responsive Design für alle Geräte / Responsive design for all devices
- ✅ Funktioniert offline (HTML-Version) / Works offline (HTML version)

## 📊 Funktionen / Features

### Kostenstruktur / Cost Structure

Die Berechnung ist strukturiert nach drei Kostentypen / The calculation is structured by three cost types:

1. **Variable Kosten / Variable Costs** (€/kWh oder €/kg):
   - Stromkosten / Electricity costs (kritisch / critical)
   - Wasserkosten / Water costs (optional)
   - Thermische Energiekosten für Cracking / Thermal energy costs for cracking

2. **CapEx / Capital Expenditure** (Investition, amortisiert / Investment, amortized):
   - Offshore-Windpark / Offshore wind farm
   - Elektrolyse / Electrolysis
   - Wasseraufbereitung / Water treatment
   - Ammoniaksynthese (Haber-Bosch) / Ammonia synthesis (Haber-Bosch)
   - ASU (Stickstoffbereitstellung) / ASU (Nitrogen supply)
   - NH₃-Terminal / NH₃ terminal
   - Schiffe / Ships
   - Lager Tanks / Storage tanks
   - NH₃-Cracking / NH₃ cracking
   - Speicher / Storage
   - Infrastruktur / Infrastructure

3. **OpEx / Operating Expenditure** (Jährliche Fixkosten / Annual fixed costs):
   - Offshore-Windpark OpEx / Offshore wind farm OpEx
   - Elektrolyse OpEx / Electrolysis OpEx
   - Wasseraufbereitung OpEx / Water treatment OpEx
   - Haber-Bosch OpEx / Haber-Bosch OpEx
   - ASU OpEx / ASU OpEx
   - Terminal OpEx / Terminal OpEx
   - Schiffe Charter OpEx / Ship charter OpEx
   - Steuern & Zoll / Taxes & customs

### Wichtige Parameter / Important Parameters

- **Strompreis (EUR/kWh)** - KRITISCH / CRITICAL: LCOE oder Strompreis für variable Kosten
- **Komponenten-spezifische OpEx** - Separate OpEx für jede Anlagenkomponente
- **Terminal & Schiffs-Kosten** - CapEx/OpEx für Transportinfrastruktur
- **Steuern & Zoll** - 75,688 Mio. €/a (aus Präsentation)

- **Electricity Price (EUR/kWh)** - CRITICAL: LCOE or electricity price for variable costs
- **Component-specific OpEx** - Separate OpEx for each plant component
- **Terminal & Ship Costs** - CapEx/OpEx for transport infrastructure
- **Taxes & Customs** - 75.688 Mio. €/a (from presentation)

## 💻 Kommandozeilen-Version / Command Line Version

### Einfache Ausführung / Simple Execution:
```bash
python wasserstoff_komplett.py
```

Das Programm startet die Desktop-App mit grafischer Oberfläche.

The program starts the desktop app with graphical interface.

### Programmgesteuert / Programmatic Usage:
```python
from wasserstoff_komplett import WasserstoffKostenrechnerErweitert

rechner = WasserstoffKostenrechnerErweitert()

# Parameter setzen / Set parameters
parameter = {
    'zielproduktion_kt': 110,
    'strompreis_eur_kwh': 0.05,  # KRITISCH / CRITICAL
    'elektrolyseur_leistung_mw': 630,
    'elektrolyse_opex_mio_eur_a': 10.0,
    # ... weitere Parameter / more parameters
}

# Kosten berechnen / Calculate costs
ergebnis = rechner.berechne_alle_kosten(parameter)
print(f"Kosten pro kg: {ergebnis['gesamt_kosten_pro_kg']:.4f} EUR/kg")
print(f"Gesamtkosten: {ergebnis['gesamtkosten_jaehrlich_eur']:,.2f} EUR")
```

## 📈 Beispielwerte / Example Values

Aus der Präsentation / From the presentation:

- **Zielproduktion / Target Production**: 110 kt H₂/a
- **Elektrischer Energiebedarf / Electrical Energy Demand**: 5,5 TWh/a
- **Strombedarf / Electricity Demand**: 50 kWh/kg H₂
- **Elektrolyseur-Leistung / Electrolyzer Capacity**: 630 MW
- **Windpark CapEx (25 Jahre) / Wind Farm CapEx (25 years)**: 5,74 Mrd. USD
- **Windpark OpEx / Wind Farm OpEx**: 229,5 Mio. USD/a
- **Steuern & Zoll / Taxes & Customs**: 75,688 Mio. €/a

**WICHTIG / IMPORTANT**: Der Strompreis (LCOE) muss eingegeben werden - dies ist der wichtigste Parameter für variable Kosten!

**IMPORTANT**: The electricity price (LCOE) must be entered - this is the most important parameter for variable costs!

## 📦 Anforderungen / Requirements

- Python 3.7 oder höher / Python 3.7 or higher
- tkinter (meist bereits in Python enthalten / usually included in Python)
- matplotlib, numpy (für Diagramme / for charts): `pip install matplotlib numpy`
- Flask (nur für Flask-Web-App / only for Flask web app): `pip install flask`
- Keine weiteren Abhängigkeiten für HTML-Version / No additional dependencies for HTML version

## 🆕 Neue Features / New Features

### Info-Icons mit Tooltips
- ℹ️ Icons neben jedem Eingabefeld
- Hover über Icon zeigt Erklärung
- Erklärt jeden Parameter basierend auf der Präsentation

### Info Icons with Tooltips
- ℹ️ Icons next to each input field
- Hover over icon shows explanation
- Explains each parameter based on the presentation

### Strukturierte Kostenberechnung / Structured Cost Calculation
- Klare Trennung: Variable Kosten | CapEx | OpEx
- Alle Komponenten einzeln berechenbar
- Transparente Kostenaufstellung

### Structured Cost Calculation
- Clear separation: Variable Costs | CapEx | OpEx
- All components individually calculable
- Transparent cost breakdown

## 📝 Verwendung / Usage

1. **Desktop-App starten / Start Desktop App:**
   ```bash
   python wasserstoff_komplett.py
   ```

2. **Alle Parameter eingeben / Enter all parameters:**
   - Tab 1: Produktion / Production
   - Tab 2: Windpark / Wind Farm
   - Tab 3: Elektrolyse / Electrolysis (inkl. Strompreis! / including electricity price!)
   - Tab 4: Ammoniak / Ammonia
   - Tab 5: Transport / Transport
   - Tab 6: Cracking
   - Tab 7: Sonstiges / Miscellaneous

3. **Berechnung durchführen / Perform calculation:**
   - Klicken Sie auf "BERECHNUNG DURCHFÜHREN" / Click "BERECHNUNG DURCHFÜHREN"
   - Ergebnisse werden angezeigt / Results are displayed
   - Gestapeltes Diagramm zeigt Kostenverteilung / Stacked chart shows cost distribution

## ⚠️ Wichtige Hinweise / Important Notes

- **Strompreis ist kritisch / Electricity price is critical**: Ohne Eingabe des Strompreises (oder LCOE) kann die Berechnung nicht durchgeführt werden.
- **Without entering the electricity price (or LCOE), the calculation cannot be performed.**

- Alle Kosten werden pro kg H₂ berechnet und dann auf die Jahresproduktion hochgerechnet.
- All costs are calculated per kg H₂ and then scaled up to annual production.

- Die Berechnung folgt der Struktur aus der Präsentation (14.01).
- The calculation follows the structure from the presentation (14.01).
