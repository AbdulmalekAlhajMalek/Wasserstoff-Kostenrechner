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
