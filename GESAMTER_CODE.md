# Wasserstoff-Kostenrechner - Gesamter Code

## 1. Kern-Berechnungsmodul: `wasserstoff_kostenrechner.py`

```python
# -*- coding: utf-8 -*-
"""
Wasserstoff-Kostenrechner
Berechnet die Gesamtkosten fuer Wasserstoffproduktion in Paraguay
und Transport nach Deutschland
"""

class WasserstoffKostenrechner:
    def __init__(self):
        # Produktionskosten in Paraguay (EUR/kg H2)
        self.produktionskosten = {
            'elektrolyse_strom': 0.0,  # EUR/kWh
            'stromverbrauch': 50.0,    # kWh/kg H2 (typisch für Elektrolyse)
            'anlagenkosten': 0.0,      # EUR/kg H2 (Amortisation)
            'betriebskosten': 0.0,     # EUR/kg H2 (Wartung, Personal)
            'wasseraufbereitung': 0.5, # EUR/kg H2
            'infrastruktur': 0.0       # EUR/kg H2
        }
        
        # Transportkosten Paraguay -> Deutschland
        self.transportkosten = {
            'verflüssigung': 2.5,      # EUR/kg H2 (Liquefaction)
            'schiffstransport': 1.5,   # EUR/kg H2 (Shipping)
            'wiedererwärmung': 0.3,    # EUR/kg H2 (Regasification)
            'lagerung': 0.2,           # EUR/kg H2 (Storage)
            'versicherung': 0.1        # EUR/kg H2 (Insurance)
        }
        
        # Zusätzliche Kosten
        self.zusatzkosten = {
            'zertifizierung': 0.1,     # EUR/kg H2
            'co2_abgabe': 0.0,         # EUR/kg H2 (falls grüner H2)
            'margen': 0.0              # EUR/kg H2 (Gewinnmarge)
        }
    
    def setze_strompreis(self, preis_eur_per_kwh):
        """Setzt den Strompreis in Paraguay"""
        self.produktionskosten['elektrolyse_strom'] = preis_eur_per_kwh
    
    def setze_anlagenkosten(self, investition_eur, kapazität_kg_pro_jahr, nutzungsdauer_jahre=20):
        """Berechnet Amortisationskosten der Anlage"""
        jährliche_amortisation = investition_eur / nutzungsdauer_jahre
        self.produktionskosten['anlagenkosten'] = jährliche_amortisation / kapazität_kg_pro_jahr
    
    def setze_betriebskosten(self, kosten_eur_pro_jahr, kapazität_kg_pro_jahr):
        """Setzt jährliche Betriebskosten"""
        self.produktionskosten['betriebskosten'] = kosten_eur_pro_jahr / kapazität_kg_pro_jahr
    
    def setze_infrastrukturkosten(self, kosten_eur_pro_jahr, kapazität_kg_pro_jahr):
        """Setzt Infrastrukturkosten"""
        self.produktionskosten['infrastruktur'] = kosten_eur_pro_jahr / kapazität_kg_pro_jahr
    
    def setze_co2_abgabe(self, abgabe_eur_per_kg):
        """Setzt CO2-Abgabe (0 für grünen Wasserstoff)"""
        self.zusatzkosten['co2_abgabe'] = abgabe_eur_per_kg
    
    def berechne_produktionskosten(self):
        """Berechnet Gesamtproduktionskosten pro kg H2"""
        stromkosten = (self.produktionskosten['elektrolyse_strom'] * 
                      self.produktionskosten['stromverbrauch'])
        
        gesamt = (
            stromkosten +
            self.produktionskosten['anlagenkosten'] +
            self.produktionskosten['betriebskosten'] +
            self.produktionskosten['wasseraufbereitung'] +
            self.produktionskosten['infrastruktur']
        )
        
        return {
            'stromkosten': stromkosten,
            'anlagenkosten': self.produktionskosten['anlagenkosten'],
            'betriebskosten': self.produktionskosten['betriebskosten'],
            'wasseraufbereitung': self.produktionskosten['wasseraufbereitung'],
            'infrastruktur': self.produktionskosten['infrastruktur'],
            'gesamt': gesamt
        }
    
    def berechne_transportkosten(self):
        """Berechnet Gesamttransportkosten pro kg H2"""
        gesamt = sum(self.transportkosten.values())
        return {
            **self.transportkosten,
            'gesamt': gesamt
        }
    
    def berechne_gesamtkosten(self, menge_kg=1.0, marge_prozent=0.0):
        """Berechnet Gesamtkosten für gegebene Menge"""
        produktions = self.berechne_produktionskosten()
        transport = self.berechne_transportkosten()
        
        kosten_pro_kg = (
            produktions['gesamt'] +
            transport['gesamt'] +
            sum(self.zusatzkosten.values())
        )
        
        # Marge hinzufügen
        if marge_prozent > 0:
            marge = kosten_pro_kg * (marge_prozent / 100)
            kosten_pro_kg += marge
            self.zusatzkosten['margen'] = marge
        
        gesamtkosten = kosten_pro_kg * menge_kg
        
        return {
            'produktionskosten': produktions,
            'transportkosten': transport,
            'zusatzkosten': self.zusatzkosten.copy(),
            'kosten_pro_kg': kosten_pro_kg,
            'menge_kg': menge_kg,
            'gesamtkosten_eur': gesamtkosten
        }
```

---

## 2. Desktop-App (tkinter): `wasserstoff_app.py`

```python
# -*- coding: utf-8 -*-
"""
Windows Desktop App für Wasserstoff-Kostenrechner
Erstellt mit tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from wasserstoff_kostenrechner import WasserstoffKostenrechner

class WasserstoffApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wasserstoff-Kostenrechner")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        
        # Stil konfigurieren
        style = ttk.Style()
        style.theme_use('clam')
        
        # Farben
        self.primary_color = "#667eea"
        self.secondary_color = "#764ba2"
        self.bg_color = "#f8f9fa"
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg=self.primary_color, height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🌊 Wasserstoff-Kostenrechner",
            font=("Arial", 20, "bold"),
            bg=self.primary_color,
            fg="white"
        )
        title_label.pack(pady=15)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Produktion: Paraguay → Verbrauch: Deutschland",
            font=("Arial", 10),
            bg=self.primary_color,
            fg="white"
        )
        subtitle_label.pack()
        
        # Hauptcontainer
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Linke Seite - Eingabefelder
        input_frame = tk.LabelFrame(
            main_container,
            text="Eingabeparameter",
            font=("Arial", 12, "bold"),
            bg=self.bg_color,
            padx=15,
            pady=15
        )
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Eingabefelder
        self.create_input_field(input_frame, "Strompreis in Paraguay (EUR/kWh):", "strompreis", "0.03")
        self.create_input_field(input_frame, "Investition Anlage (EUR):", "investition", "100000000")
        self.create_input_field(input_frame, "Jährliche Kapazität (kg/Jahr):", "kapazität", "20000000")
        self.create_input_field(input_frame, "Jährliche Betriebskosten (EUR):", "betrieb", "5000000")
        self.create_input_field(input_frame, "Jährliche Infrastrukturkosten (EUR):", "infrastruktur", "2000000")
        self.create_input_field(input_frame, "Menge Wasserstoff (kg):", "menge", "1000")
        self.create_input_field(input_frame, "Gewinnmarge (%):", "marge", "10")
        self.create_input_field(input_frame, "CO2-Abgabe (EUR/kg):", "co2_abgabe", "0")
        
        # Berechnen Button
        calc_button = tk.Button(
            input_frame,
            text="Berechnen",
            command=self.berechne_kosten,
            bg=self.secondary_color,
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
            cursor="hand2",
            relief=tk.FLAT
        )
        calc_button.pack(pady=15)
        
        # Rechte Seite - Ergebnisse
        result_frame = tk.LabelFrame(
            main_container,
            text="Kostenaufstellung",
            font=("Arial", 12, "bold"),
            bg=self.bg_color,
            padx=15,
            pady=15
        )
        result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Zusammenfassung oben
        summary_frame = tk.Frame(result_frame, bg="white", relief=tk.RAISED, borderwidth=2)
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.summary_label = tk.Label(
            summary_frame,
            text="Bitte Parameter eingeben und berechnen",
            font=("Arial", 11, "bold"),
            bg="white",
            fg=self.primary_color,
            pady=10
        )
        self.summary_label.pack()
        
        # Ergebnis-Textbereich
        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            wrap=tk.WORD,
            width=40,
            height=25,
            font=("Consolas", 9),
            bg="white",
            fg="#333",
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Initiale Nachricht
        self.result_text.insert(tk.END, "Bitte geben Sie die Parameter ein\nund klicken Sie auf 'Berechnen'.\n\n")
        self.result_text.config(state=tk.DISABLED)
        
    def create_input_field(self, parent, label_text, field_name, default_value):
        """Erstellt ein Eingabefeld mit Label"""
        frame = tk.Frame(parent, bg=self.bg_color)
        frame.pack(fill=tk.X, pady=8)
        
        label = tk.Label(
            frame,
            text=label_text,
            font=("Arial", 9),
            bg=self.bg_color,
            anchor="w"
        )
        label.pack(fill=tk.X)
        
        entry = tk.Entry(
            frame,
            font=("Arial", 10),
            relief=tk.SOLID,
            borderwidth=1
        )
        entry.insert(0, default_value)
        entry.pack(fill=tk.X, ipady=5)
        
        setattr(self, field_name, entry)
        
    def berechne_kosten(self):
        """Führt die Kostenberechnung durch"""
        try:
            # Werte aus Eingabefeldern lesen
            strompreis = float(self.strompreis.get())
            investition = float(self.investition.get())
            kapazität = float(self.kapazität.get())
            betrieb = float(self.betrieb.get())
            infrastruktur = float(self.infrastruktur.get())
            menge = float(self.menge.get())
            marge = float(self.marge.get())
            co2_abgabe = float(self.co2_abgabe.get())
            
            # Validierung
            if any(val < 0 for val in [strompreis, investition, kapazität, betrieb, infrastruktur, menge, marge, co2_abgabe]):
                messagebox.showerror("Fehler", "Alle Werte müssen positiv sein!")
                return
            
            if kapazität == 0:
                messagebox.showerror("Fehler", "Kapazität darf nicht 0 sein!")
                return
            
            # Rechner initialisieren
            rechner = WasserstoffKostenrechner()
            rechner.setze_strompreis(strompreis)
            rechner.setze_anlagenkosten(investition, kapazität)
            rechner.setze_betriebskosten(betrieb, kapazität)
            rechner.setze_infrastrukturkosten(infrastruktur, kapazität)
            rechner.setze_co2_abgabe(co2_abgabe)
            
            # Berechnung durchführen
            ergebnis = rechner.berechne_gesamtkosten(menge_kg=menge, marge_prozent=marge)
            
            # Ergebnisse anzeigen
            self.zeige_ergebnisse(ergebnis, rechner)
            
        except ValueError:
            messagebox.showerror("Fehler", "Bitte geben Sie gültige Zahlen ein!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten:\n{str(e)}")
    
    def zeige_ergebnisse(self, ergebnis, rechner):
        """Zeigt die Berechnungsergebnisse an"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        # Formatierung
        def format_currency(value):
            return f"{value:,.4f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        def format_number(value):
            return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        # Zusammenfassung oben aktualisieren
        kosten_pro_kg = format_currency(ergebnis['kosten_pro_kg'])
        gesamtkosten = format_currency(ergebnis['gesamtkosten_eur'])
        menge = format_number(ergebnis['menge_kg'])
        
        summary_text = f"Kosten: {kosten_pro_kg} EUR/kg  |  Gesamt ({menge} kg): {gesamtkosten} EUR"
        self.summary_label.config(text=summary_text)
        
        # Header
        output = "=" * 60 + "\n"
        output += "WASSERSTOFF-KOSTENRECHNUNG\n"
        output += "Produktion: Paraguay → Verbrauch: Deutschland\n"
        output += "=" * 60 + "\n\n"
        output += f"Menge: {format_number(ergebnis['menge_kg'])} kg H₂\n\n"
        
        # Produktionskosten
        output += "PRODUKTIONSKOSTEN (Paraguay):\n"
        output += "-" * 60 + "\n"
        output += f"  Stromkosten ({rechner.produktionskosten['stromverbrauch']} kWh/kg × "
        output += f"{rechner.produktionskosten['elektrolyse_strom']:.4f} EUR/kWh):\n"
        output += f"    {format_currency(ergebnis['produktionskosten']['stromkosten'])} EUR/kg\n"
        output += f"  Anlagenkosten (Amortisation):\n"
        output += f"    {format_currency(ergebnis['produktionskosten']['anlagenkosten'])} EUR/kg\n"
        output += f"  Betriebskosten:\n"
        output += f"    {format_currency(ergebnis['produktionskosten']['betriebskosten'])} EUR/kg\n"
        output += f"  Wasseraufbereitung:\n"
        output += f"    {format_currency(ergebnis['produktionskosten']['wasseraufbereitung'])} EUR/kg\n"
        output += f"  Infrastruktur:\n"
        output += f"    {format_currency(ergebnis['produktionskosten']['infrastruktur'])} EUR/kg\n"
        output += f"\n  → Gesamt Produktion:\n"
        output += f"    {format_currency(ergebnis['produktionskosten']['gesamt'])} EUR/kg\n\n"
        
        # Transportkosten
        output += "TRANSPORTKOSTEN (Paraguay → Deutschland):\n"
        output += "-" * 60 + "\n"
        output += f"  Verflüssigung:\n"
        output += f"    {format_currency(ergebnis['transportkosten']['verflüssigung'])} EUR/kg\n"
        output += f"  Schiffstransport:\n"
        output += f"    {format_currency(ergebnis['transportkosten']['schiffstransport'])} EUR/kg\n"
        output += f"  Wiedererwärmung:\n"
        output += f"    {format_currency(ergebnis['transportkosten']['wiedererwärmung'])} EUR/kg\n"
        output += f"  Lagerung:\n"
        output += f"    {format_currency(ergebnis['transportkosten']['lagerung'])} EUR/kg\n"
        output += f"  Versicherung:\n"
        output += f"    {format_currency(ergebnis['transportkosten']['versicherung'])} EUR/kg\n"
        output += f"\n  → Gesamt Transport:\n"
        output += f"    {format_currency(ergebnis['transportkosten']['gesamt'])} EUR/kg\n\n"
        
        # Zusatzkosten
        output += "ZUSATZKOSTEN:\n"
        output += "-" * 60 + "\n"
        output += f"  Zertifizierung:\n"
        output += f"    {format_currency(ergebnis['zusatzkosten']['zertifizierung'])} EUR/kg\n"
        output += f"  CO2-Abgabe:\n"
        output += f"    {format_currency(ergebnis['zusatzkosten']['co2_abgabe'])} EUR/kg\n"
        if ergebnis['zusatzkosten']['margen'] > 0:
            marge_prozent = float(self.marge.get())
            output += f"  Gewinnmarge ({marge_prozent}%):\n"
            output += f"    {format_currency(ergebnis['zusatzkosten']['margen'])} EUR/kg\n"
        
        # Zusammenfassung
        output += "\n" + "=" * 60 + "\n"
        output += "ZUSAMMENFASSUNG:\n"
        output += "=" * 60 + "\n"
        output += f"Kosten pro kg H₂: {format_currency(ergebnis['kosten_pro_kg'])} EUR/kg\n"
        output += f"Gesamtkosten ({format_number(ergebnis['menge_kg'])} kg):\n"
        output += f"  {format_currency(ergebnis['gesamtkosten_eur'])} EUR\n"
        output += "=" * 60 + "\n"
        
        self.result_text.insert(tk.END, output)
        self.result_text.config(state=tk.DISABLED)
        
        # Scroll nach oben
        self.result_text.see(1.0)

def main():
    root = tk.Tk()
    app = WasserstoffApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
```

---

## 3. Flask Web-App: `app.py`

```python
# -*- coding: utf-8 -*-
"""
Flask Web Application für Wasserstoff-Kostenrechner
"""

from flask import Flask, render_template, request, jsonify
from wasserstoff_kostenrechner import WasserstoffKostenrechner

app = Flask(__name__)

@app.route('/')
def index():
    """Hauptseite"""
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    """API Endpoint für Kostenberechnung"""
    try:
        data = request.get_json()
        
        # Parameter aus Request extrahieren
        strompreis = float(data.get('strompreis', 0.03))
        investition = float(data.get('investition', 100000000))
        kapazität = float(data.get('kapazität', 20000000))
        betrieb = float(data.get('betrieb', 5000000))
        infrastruktur = float(data.get('infrastruktur', 2000000))
        menge = float(data.get('menge', 1000))
        marge = float(data.get('marge', 10))
        co2_abgabe = float(data.get('co2_abgabe', 0))
        
        # Rechner initialisieren und Parameter setzen
        rechner = WasserstoffKostenrechner()
        rechner.setze_strompreis(strompreis)
        rechner.setze_anlagenkosten(investition, kapazität)
        rechner.setze_betriebskosten(betrieb, kapazität)
        rechner.setze_infrastrukturkosten(infrastruktur, kapazität)
        rechner.setze_co2_abgabe(co2_abgabe)
        
        # Berechnung durchführen
        ergebnis = rechner.berechne_gesamtkosten(menge_kg=menge, marge_prozent=marge)
        
        return jsonify({
            'success': True,
            'result': ergebnis
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

---

## 4. HTML-Version: `wasserstoff_rechner.html`

Siehe separate Datei `wasserstoff_rechner.html` - zu lang für diese Zusammenfassung.

Die HTML-Datei enthält:
- Vollständiges HTML/CSS/JavaScript
- Identische Berechnungslogik wie Python-Version
- Moderne, responsive Benutzeroberfläche
- Funktioniert ohne Server (standalone)

---

## Berechnungsformeln (Zusammenfassung)

### Produktionskosten pro kg H₂:
```
Stromkosten = Strompreis (EUR/kWh) × 50 kWh/kg
Anlagenkosten = (Investition / 20 Jahre) / Kapazität (kg/Jahr)
Betriebskosten = Jährliche Betriebskosten / Kapazität (kg/Jahr)
Infrastruktur = Jährliche Infrastrukturkosten / Kapazität (kg/Jahr)

Gesamt Produktion = Stromkosten + Anlagenkosten + Betriebskosten + 
                    Wasseraufbereitung (0,5 EUR/kg) + Infrastruktur
```

### Transportkosten pro kg H₂:
```
Gesamt Transport = Verflüssigung (2,5) + Schiffstransport (1,5) + 
                   Wiedererwärmung (0,3) + Lagerung (0,2) + Versicherung (0,1)
                   = 4,6 EUR/kg
```

### Gesamtkosten:
```
Kosten pro kg = Produktionskosten + Transportkosten + 
                Zertifizierung (0,1) + CO2-Abgabe + Marge

Gesamtkosten = Kosten pro kg × Menge (kg)
```

---

## Verwendung

### Desktop-App:
```bash
python wasserstoff_app.py
```

### Flask Web-App:
```bash
python app.py
# Dann Browser öffnen: http://localhost:5000
```

### HTML-Version:
Einfach `wasserstoff_rechner.html` im Browser öffnen (Doppelklick)
