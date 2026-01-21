# -*- coding: utf-8 -*-
"""
WASSERSTOFF-KOSTENRECHNER - ERWEITERTE VERSION
==============================================

Berechnet die Gesamtkosten für Wasserstoffproduktion mit allen Parametern:
- Offshore-Windpark
- Elektrolyse
- Wasseraufbereitung
- Ammoniaksynthese (Haber-Bosch)
- Transport (NH₃)
- NH₃-Cracking in Deutschland

Verwendung:
-----------
python wasserstoff_komplett.py
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# Matplotlib und NumPy - optional für Diagramme
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import numpy as np
    MATPLOTLIB_VERFÜGBAR = True
except ImportError:
    MATPLOTLIB_VERFÜGBAR = False
    print("Warnung: matplotlib oder numpy nicht installiert.")
    print("Installieren Sie sie mit: pip install matplotlib numpy")
    print("Diagramme werden nicht angezeigt.")

# ============================================================================
# 0. TOOLTIP-KLASSE
# ============================================================================

class ToolTip:
    """Tooltip-Klasse für tkinter Widgets"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind('<Enter>', self.on_enter)
        self.widget.bind('<Leave>', self.on_leave)
        self.widget.bind('<Motion>', self.on_motion)
    
    def on_enter(self, event=None):
        self.show_tooltip()
    
    def on_leave(self, event=None):
        self.hide_tooltip()
    
    def on_motion(self, event=None):
        if self.tooltip_window:
            self.hide_tooltip()
            self.show_tooltip()
    
    def show_tooltip(self):
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=("Arial", 9),
            justify=tk.LEFT,
            wraplength=300
        )
        label.pack()
    
    def hide_tooltip(self):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

# ============================================================================
# 1. TOOLTIP-TEXTE
# ============================================================================

TOOLTIP_TEXTE = {
    # Produktion
    'zielproduktion_kt': 'Zielproduktion in Kilotonnen Wasserstoff pro Jahr. Aus der Präsentation: 110 kt H₂/a.',
    'energiebedarf_twh_a': 'Gesamter elektrischer Energiebedarf in Terawattstunden pro Jahr. Aus der Präsentation: 5,5 TWh/a.',
    'strombedarf_kwh_kg': 'Spezifischer Strombedarf für die Elektrolyse in kWh pro kg H₂. Typischer Wert: 50 kWh/kg H₂.',
    'usd_zu_eur_kurs': 'Wechselkurs für die Umrechnung von USD zu EUR. Standard: 0.92 (1 USD = 0.92 EUR).',
    
    # Windpark
    'anzahl_turbinen': 'Anzahl der Offshore-Windkraftanlagen. Aus der Präsentation: 240 Turbinen.',
    'windpark_leistung_gw': 'Installierte Gesamtleistung des Windparks in Gigawatt. Aus der Präsentation: 2,4 GW.',
    'kapazitaetsfaktor_prozent': 'Kapazitätsfaktor des Windparks in Prozent. Aus der Präsentation: ≈51%.',
    'windpark_opex_jaehrlich_mio_usd': 'Jährliche Betriebskosten (OpEx) des Windparks in Millionen USD. Aus der Präsentation: 229,5 Mio. USD/a.',
    'windpark_capex_25j_mrd_usd': 'Gesamtkosten (CapEx) des Windparks über 25 Jahre in Milliarden USD. Aus der Präsentation: 5,74 Mrd. USD.',
    
    # Elektrolyse - Variable Kosten
    'strompreis_eur_kwh': 'KRITISCH: LCOE (Levelized Cost of Energy) oder Strompreis in EUR/kWh. Wichtigster Parameter für variable Kosten. Berechnung: Stromkosten pro kg = Strombedarf (kWh/kg) × Strompreis (EUR/kWh).',
    'lcoe_eur_kwh': 'Alternative zu strompreis_eur_kwh: Levelized Cost of Energy in EUR/kWh. Stromkosten aus erneuerbarer Energiequelle (Offshore-Wind).',
    
    # Elektrolyse - CapEx/OpEx
    'elektrolyseur_leistung_mw': 'Leistung des Elektrolyseurs in Megawatt. Aus der Präsentation: ca. 630 MW bei 8760 h/a. Technologie: PEM-Elektrolyseur.',
    'elektrolyse_capex_mio_eur': 'Investitionskosten (CapEx) für die Elektrolyseanlage in Millionen EUR. Falls 0: automatische Schätzung basierend auf Leistung (ca. 1000 EUR/kW).',
    'elektrolyse_nutzungsdauer_jahre': 'Nutzungsdauer der Elektrolyseanlage in Jahren für die Amortisation. Standard: 20 Jahre.',
    'elektrolyse_opex_mio_eur_a': 'NEU: Jährliche Betriebskosten (OpEx) für die Elektrolyseanlage in Millionen EUR pro Jahr. Enthält Wartung, Personal, etc.',
    'elektrolyse_opex_prozent_capex': 'Alternative zu elektrolyse_opex_mio_eur_a: OpEx als Prozentsatz des CapEx pro Jahr.',
    
    # Wasseraufbereitung
    'wasserbedarf_l_h': 'Wasserbedarf in Litern pro Stunde. Aus der Präsentation: ca. 125.000 Liter pro Stunde. Wasserquelle: Meerwasser mit Umkehrosmose.',
    'wasseraufbereitung_capex_mio_eur': 'Investitionskosten (CapEx) für die Wasseraufbereitungsanlage in Millionen EUR.',
    'wasseraufbereitung_nutzungsdauer_jahre': 'Nutzungsdauer der Wasseraufbereitungsanlage in Jahren. Standard: 20 Jahre.',
    'wasseraufbereitung_opex_mio_eur_a': 'NEU: Jährliche Betriebskosten (OpEx) für die Wasseraufbereitung in Millionen EUR pro Jahr.',
    'wasserpreis_eur_m3': 'Alternative zu OpEx: Wasserpreis in EUR pro m³. Berechnung: Wasserkosten pro kg = (Wasserbedarf m³/kg) × (Wasserpreis EUR/m³).',
    
    # Ammoniak - Haber-Bosch
    'nh3_bedarf_kt': 'NH₃-Bedarf inkl. Verluste in Kilotonnen pro Jahr. Aus der Präsentation: 687 kt NH₃ pro Jahr.',
    'haber_bosch_leistung_mw': 'OPTIONAL: Haber-Bosch Leistung in MW. Nur nötig wenn CapEx über Leistung skaliert wird. Referenz: 100 MW ≈ 25 Mio. USD, 1 GW ≈ 125 Mio. USD.',
    'haber_bosch_capex_mio_usd': 'Investitionskosten (CapEx) für die Haber-Bosch-Anlage in Millionen USD. Falls 0: automatische Schätzung basierend auf Leistung.',
    'haber_bosch_nutzungsdauer_jahre': 'Nutzungsdauer der Haber-Bosch-Anlage in Jahren. Standard: 20 Jahre.',
    'haber_bosch_opex_mio_eur_a': 'NEU: Jährliche Betriebskosten (OpEx) für Haber-Bosch in Millionen EUR pro Jahr.',
    'haber_bosch_strombedarf_gwh_a': 'NEU: Jährlicher Strombedarf für Haber-Bosch in GWh/a. OpEx überwiegend Stromkosten (aus Windpark gedeckt).',
    
    # ASU (Stickstoff)
    'asu_kapazitaet_t_n2_tag': 'ASU-Kapazität in Tonnen N₂ pro Tag. Aus der Präsentation: 1550 t N₂ pro Tag.',
    'asu_capex_mio_usd': 'Investitionskosten (CapEx) für die ASU-Anlage in Millionen USD. Aus der Präsentation: ≈200 Mio. USD.',
    'asu_nutzungsdauer_jahre': 'Nutzungsdauer der ASU-Anlage in Jahren. Standard: 20 Jahre.',
    'asu_opex_mio_eur_a': 'NEU: Jährliche Betriebskosten (OpEx) für ASU in Millionen EUR pro Jahr.',
    'asu_strombedarf_kwh_t_n2': 'NEU: Spezifischer Strombedarf für ASU in kWh pro t N₂. Alternative zu OpEx.',
    
    # Transport - Terminal & Schiffe
    'transport_distanz_km': 'Transportdistanz in Kilometern. Aus der Präsentation: ca. 13.000 km (Montevideo → Hamburg/Rotterdam → Köln).',
    'nh3_terminal_capex_mio_eur': 'NEU: Investitionskosten (CapEx) für NH₃-Terminals (Export + Import) in Millionen EUR.',
    'nh3_terminal_opex_mio_eur_a': 'NEU: Jährliche Betriebskosten (OpEx) für NH₃-Terminals in Millionen EUR pro Jahr.',
    'schiffe_capex_mio_eur': 'NEU: Investitionskosten (CapEx) für NH₃-Tanker in Millionen EUR. Alternative: Charter-OpEx verwenden.',
    'charter_opex_mio_eur_a': 'NEU: Jährliche Charterkosten (OpEx) für NH₃-Tanker in Millionen EUR pro Jahr. Alternative zu Schiffs-CapEx.',
    'lager_tanks_capex_mio_eur': 'NEU: Investitionskosten (CapEx) für NH₃-Speichertanks im Hafen in Millionen EUR.',
    'transport_dauer_tage': 'OPTIONAL: Transportdauer in Tagen. Aus der Präsentation: ca. 26 Tage pro Fahrt. Nur relevant wenn in Kostenberechnung verwendet.',
    'anzahl_schiffe': 'OPTIONAL: Anzahl benötigter Schiffe. Aus der Präsentation: 4 NH₃-Tanker. Nur relevant wenn in Kostenberechnung verwendet.',
    'anzahl_fahrten_pro_jahr': 'OPTIONAL: Anzahl Schiffstransporte pro Jahr. Aus der Präsentation: ≈24 Fahrten pro Jahr. Nur relevant wenn in Kostenberechnung verwendet.',
    
    # Cracking
    'cracker_kapazitaet_t_h2_d': 'Cracker-Kapazität in Tonnen H₂ pro Tag. Referenz: 200 t H₂/d. Hochskalierung: 330 t H₂/d.',
    'cracker_capex_mio_eur': 'Investitionskosten (CapEx) für NH₃-Cracker in Millionen EUR. Referenz: ≈369 Mio. € (200 t/d). Hochskalierung: ≈500 Mio. € (330 t/d).',
    'cracker_nutzungsdauer_jahre': 'Nutzungsdauer des Crackers in Jahren. Standard: 20 Jahre.',
    'cracking_thermisch_eur_kg': 'NEU: Thermische Energiekosten für Cracking in EUR pro kg H₂. Standard: 0 (wenn Abwärme aus DRI-Stahlwerk verwendet wird, wie in Präsentation).',
    
    # Sonstiges
    'speicher_capex_mio_eur': 'Investitionskosten (CapEx) für H₂- und NH₃-Speicher in Millionen EUR.',
    'speicher_nutzungsdauer_jahre': 'Nutzungsdauer der Speicher in Jahren. Standard: 20 Jahre.',
    'infrastruktur_capex_mio_eur': 'Investitionskosten (CapEx) für Transportinfrastruktur in Millionen EUR.',
    'infrastruktur_nutzungsdauer_jahre': 'Nutzungsdauer der Infrastruktur in Jahren. Standard: 20 Jahre.',
    'steuern_zoll_mio_eur_a': 'NEU: Jährliche Steuern und Zollkosten in Millionen EUR pro Jahr. Aus der Präsentation: 75,688 Mio. €/a.',
}

# ============================================================================
# 2. ERWEITERTES BERECHNUNGSMODUL
# ============================================================================

class WasserstoffKostenrechnerErweitert:
    """
    Erweiterte Berechnung der Gesamtkosten für Wasserstoffproduktion
    mit allen Prozessschritten - Strukturiert nach CapEx, OpEx und variablen Kosten
    """
    
    def __init__(self):
        pass
    
    def berechne_alle_kosten(self, parameter):
        """
        Berechnet alle Kostenkomponenten basierend auf den Parametern
        Strukturiert nach: Variable Kosten, CapEx (amortisiert), OpEx (jährlich)
        
        Args:
            parameter: Dictionary mit allen Eingabeparametern
        
        Returns:
            Dictionary mit allen Kostenkomponenten
        """
        # Umrechnungen
        jahresproduktion_kg = parameter['zielproduktion_kt'] * 1_000_000  # kt zu kg
        usd_zu_eur = parameter.get('usd_zu_eur_kurs', 0.92)
        
        # ====================================================================
        # VARIABLE KOSTEN (€/kWh oder €/kg)
        # ====================================================================
        
        # 1. STROMKOSTEN (Variable) - KRITISCH
        strombedarf_kwh_kg = parameter.get('strombedarf_kwh_kg', 50.0)
        strompreis_eur_kwh = parameter.get('strompreis_eur_kwh', 0.0)
        if strompreis_eur_kwh == 0:
            # Fallback auf LCOE falls vorhanden
            strompreis_eur_kwh = parameter.get('lcoe_eur_kwh', 0.0)
        
        if strompreis_eur_kwh == 0:
            raise ValueError("KRITISCH: Strompreis (strompreis_eur_kwh) oder LCOE (lcoe_eur_kwh) muss eingegeben werden!")
        
        stromkosten_pro_kg = strombedarf_kwh_kg * strompreis_eur_kwh
        
        # 2. WASSERKOSTEN (Variable, falls wasserpreis verwendet)
        wasserpreis_eur_m3 = parameter.get('wasserpreis_eur_m3', 0.0)
        wasserkosten_pro_kg = 0.0
        if wasserpreis_eur_m3 > 0:
            # Wasserbedarf: 125.000 L/h = 125 m³/h
            # Bei 110 kt/a = 110.000.000 kg/a
            # Stunden pro Jahr: 8760
            wasserbedarf_m3_a = (parameter.get('wasserbedarf_l_h', 125_000) / 1000) * 8760
            wasserkosten_pro_kg = (wasserbedarf_m3_a * wasserpreis_eur_m3) / jahresproduktion_kg
        
        # 3. CRACKING THERMISCHE ENERGIE (Variable, kann 0 sein)
        cracking_thermisch_eur_kg = parameter.get('cracking_thermisch_eur_kg', 0.0)
        
        # ====================================================================
        # CAPEX (Investition, amortisiert über Nutzungsdauer)
        # ====================================================================
        
        # 1. OFFSHORE-WINDPARK CAPEX
        windpark_capex_25j = parameter['windpark_capex_25j_mrd_usd'] * 1_000_000_000
        windpark_capex_25j_eur = windpark_capex_25j * usd_zu_eur
        windpark_amortisation_jaehrlich = windpark_capex_25j_eur / 25
        windpark_capex_pro_kg = windpark_amortisation_jaehrlich / jahresproduktion_kg
        
        # 2. ELEKTROLYSE CAPEX
        elektrolyseur_leistung_mw = parameter.get('elektrolyseur_leistung_mw', 630)
        elektrolyse_capex = parameter.get('elektrolyse_capex_mio_eur', 0) * 1_000_000
        elektrolyse_nutzungsdauer = parameter.get('elektrolyse_nutzungsdauer_jahre', 20)
        
        if elektrolyse_capex > 0:
            elektrolyse_amortisation_jaehrlich = elektrolyse_capex / elektrolyse_nutzungsdauer
        else:
            # Schätzung: ca. 1000 EUR/kW
            elektrolyse_capex_geschätzt = elektrolyseur_leistung_mw * 1_000 * 1_000
            elektrolyse_amortisation_jaehrlich = elektrolyse_capex_geschätzt / elektrolyse_nutzungsdauer
        
        elektrolyse_capex_pro_kg = elektrolyse_amortisation_jaehrlich / jahresproduktion_kg
        
        # 3. WASSERAUFBEREITUNG CAPEX
        wasseraufbereitung_capex = parameter.get('wasseraufbereitung_capex_mio_eur', 0) * 1_000_000
        wasseraufbereitung_nutzungsdauer = parameter.get('wasseraufbereitung_nutzungsdauer_jahre', 20)
        
        if wasseraufbereitung_capex > 0:
            wasseraufbereitung_amortisation = wasseraufbereitung_capex / wasseraufbereitung_nutzungsdauer
            wasseraufbereitung_capex_pro_kg = wasseraufbereitung_amortisation / jahresproduktion_kg
        else:
            wasseraufbereitung_capex_pro_kg = 0.0
        
        # 4. HABER-BOSCH CAPEX
        nh3_bedarf_kt = parameter.get('nh3_bedarf_kt', 687)
        haber_bosch_leistung_mw = parameter.get('haber_bosch_leistung_mw', 0)
        haber_bosch_capex = parameter.get('haber_bosch_capex_mio_usd', 0) * 1_000_000 * usd_zu_eur
        
        if haber_bosch_capex > 0:
            haber_bosch_nutzungsdauer = parameter.get('haber_bosch_nutzungsdauer_jahre', 20)
            haber_bosch_amortisation = haber_bosch_capex / haber_bosch_nutzungsdauer
            nh3_produktion_kg = nh3_bedarf_kt * 1_000_000
            haber_bosch_kosten_pro_kg_nh3 = haber_bosch_amortisation / nh3_produktion_kg
            haber_bosch_capex_pro_kg_h2 = haber_bosch_kosten_pro_kg_nh3 * (nh3_bedarf_kt / parameter['zielproduktion_kt'])
        elif haber_bosch_leistung_mw > 0:
            # Schätzung basierend auf Leistung
            if haber_bosch_leistung_mw < 1000:
                geschätzte_capex = (haber_bosch_leistung_mw / 100) * 25_000_000 * usd_zu_eur
            else:
                geschätzte_capex = (haber_bosch_leistung_mw / 1000) * 125_000_000 * usd_zu_eur
            haber_bosch_amortisation = geschätzte_capex / 20
            nh3_produktion_kg = nh3_bedarf_kt * 1_000_000
            haber_bosch_kosten_pro_kg_nh3 = haber_bosch_amortisation / nh3_produktion_kg
            haber_bosch_capex_pro_kg_h2 = haber_bosch_kosten_pro_kg_nh3 * (nh3_bedarf_kt / parameter['zielproduktion_kt'])
        else:
            haber_bosch_capex_pro_kg_h2 = 0.0
        
        # 5. ASU CAPEX
        asu_capex = parameter.get('asu_capex_mio_usd', 200) * 1_000_000 * usd_zu_eur
        asu_nutzungsdauer = parameter.get('asu_nutzungsdauer_jahre', 20)
        asu_amortisation = asu_capex / asu_nutzungsdauer
        asu_capex_pro_kg_h2 = asu_amortisation / jahresproduktion_kg
        
        # 6. TRANSPORT TERMINAL CAPEX
        nh3_terminal_capex = parameter.get('nh3_terminal_capex_mio_eur', 0) * 1_000_000
        nh3_terminal_nutzungsdauer = parameter.get('nh3_terminal_nutzungsdauer_jahre', 20)
        nh3_terminal_capex_pro_kg = 0.0
        if nh3_terminal_capex > 0:
            nh3_terminal_amortisation = nh3_terminal_capex / nh3_terminal_nutzungsdauer
            nh3_terminal_capex_pro_kg = nh3_terminal_amortisation / jahresproduktion_kg
        
        # 7. SCHIFFE CAPEX
        schiffe_capex = parameter.get('schiffe_capex_mio_eur', 0) * 1_000_000
        schiffe_nutzungsdauer = parameter.get('schiffe_nutzungsdauer_jahre', 20)
        schiffe_capex_pro_kg = 0.0
        if schiffe_capex > 0:
            schiffe_amortisation = schiffe_capex / schiffe_nutzungsdauer
            schiffe_capex_pro_kg = schiffe_amortisation / jahresproduktion_kg
        
        # 8. LAGER TANKS CAPEX
        lager_tanks_capex = parameter.get('lager_tanks_capex_mio_eur', 0) * 1_000_000
        lager_tanks_nutzungsdauer = parameter.get('lager_tanks_nutzungsdauer_jahre', 20)
        lager_tanks_capex_pro_kg = 0.0
        if lager_tanks_capex > 0:
            lager_tanks_amortisation = lager_tanks_capex / lager_tanks_nutzungsdauer
            lager_tanks_capex_pro_kg = lager_tanks_amortisation / jahresproduktion_kg
        
        # 9. CRACKER CAPEX
        cracker_capex = parameter.get('cracker_capex_mio_eur', 500) * 1_000_000
        cracker_nutzungsdauer = parameter.get('cracker_nutzungsdauer_jahre', 20)
        cracker_amortisation = cracker_capex / cracker_nutzungsdauer
        cracker_capex_pro_kg_h2 = cracker_amortisation / jahresproduktion_kg
        
        # 10. SPEICHER CAPEX
        speicher_capex = parameter.get('speicher_capex_mio_eur', 0) * 1_000_000
        speicher_nutzungsdauer = parameter.get('speicher_nutzungsdauer_jahre', 20)
        speicher_capex_pro_kg = 0.0
        if speicher_capex > 0:
            speicher_amortisation = speicher_capex / speicher_nutzungsdauer
            speicher_capex_pro_kg = speicher_amortisation / jahresproduktion_kg
        
        # 11. INFRASTRUKTUR CAPEX
        infrastruktur_capex = parameter.get('infrastruktur_capex_mio_eur', 0) * 1_000_000
        infrastruktur_nutzungsdauer = parameter.get('infrastruktur_nutzungsdauer_jahre', 20)
        infrastruktur_capex_pro_kg = 0.0
        if infrastruktur_capex > 0:
            infrastruktur_amortisation = infrastruktur_capex / infrastruktur_nutzungsdauer
            infrastruktur_capex_pro_kg = infrastruktur_amortisation / jahresproduktion_kg
        
        # ====================================================================
        # OPEX (Jährliche Fixkosten, €/a)
        # ====================================================================
        
        # 1. WINDPARK OPEX
        windpark_opex_jaehrlich = parameter['windpark_opex_jaehrlich_mio_usd'] * 1_000_000 * usd_zu_eur
        windpark_opex_pro_kg = windpark_opex_jaehrlich / jahresproduktion_kg
        
        # 2. ELEKTROLYSE OPEX
        elektrolyse_opex_jaehrlich = parameter.get('elektrolyse_opex_mio_eur_a', 0) * 1_000_000
        # Alternative: OpEx als % vom CapEx
        if elektrolyse_opex_jaehrlich == 0:
            elektrolyse_opex_prozent = parameter.get('elektrolyse_opex_prozent_capex', 0)
            if elektrolyse_opex_prozent > 0:
                if elektrolyse_capex > 0:
                    elektrolyse_opex_jaehrlich = (elektrolyse_capex * elektrolyse_opex_prozent / 100)
                else:
                    elektrolyse_capex_geschätzt = elektrolyseur_leistung_mw * 1_000 * 1_000
                    elektrolyse_opex_jaehrlich = (elektrolyse_capex_geschätzt * elektrolyse_opex_prozent / 100)
        
        elektrolyse_opex_pro_kg = elektrolyse_opex_jaehrlich / jahresproduktion_kg
        
        # 3. WASSERAUFBEREITUNG OPEX
        wasseraufbereitung_opex_jaehrlich = parameter.get('wasseraufbereitung_opex_mio_eur_a', 0) * 1_000_000
        wasseraufbereitung_opex_pro_kg = wasseraufbereitung_opex_jaehrlich / jahresproduktion_kg
        
        # 4. HABER-BOSCH OPEX
        haber_bosch_opex_jaehrlich = parameter.get('haber_bosch_opex_mio_eur_a', 0) * 1_000_000
        # Alternative: Strombedarf für Haber-Bosch
        if haber_bosch_opex_jaehrlich == 0:
            haber_bosch_strombedarf_gwh_a = parameter.get('haber_bosch_strombedarf_gwh_a', 0)
            if haber_bosch_strombedarf_gwh_a > 0:
                haber_bosch_opex_jaehrlich = haber_bosch_strombedarf_gwh_a * 1_000_000 * strompreis_eur_kwh
        
        haber_bosch_opex_pro_kg_h2 = haber_bosch_opex_jaehrlich / jahresproduktion_kg
        
        # 5. ASU OPEX
        asu_opex_jaehrlich = parameter.get('asu_opex_mio_eur_a', 0) * 1_000_000
        # Alternative: Strombedarf für ASU
        if asu_opex_jaehrlich == 0:
            asu_strombedarf_kwh_t_n2 = parameter.get('asu_strombedarf_kwh_t_n2', 0)
            if asu_strombedarf_kwh_t_n2 > 0:
                asu_kapazitaet_t_n2_tag = parameter.get('asu_kapazitaet_t_n2_tag', 1550)
                asu_produktion_t_n2_a = asu_kapazitaet_t_n2_tag * 365
                asu_strombedarf_kwh_a = asu_produktion_t_n2_a * asu_strombedarf_kwh_t_n2
                asu_opex_jaehrlich = (asu_strombedarf_kwh_a / 1_000_000) * strompreis_eur_kwh * 1_000_000
        
        asu_opex_pro_kg_h2 = asu_opex_jaehrlich / jahresproduktion_kg
        
        # 6. TRANSPORT TERMINAL OPEX
        nh3_terminal_opex_jaehrlich = parameter.get('nh3_terminal_opex_mio_eur_a', 0) * 1_000_000
        nh3_terminal_opex_pro_kg = nh3_terminal_opex_jaehrlich / jahresproduktion_kg
        
        # 7. SCHIFFE CHARTER OPEX
        charter_opex_jaehrlich = parameter.get('charter_opex_mio_eur_a', 0) * 1_000_000
        schiffe_opex_pro_kg = charter_opex_jaehrlich / jahresproduktion_kg
        
        # 8. STEUERN & ZOLL OPEX
        steuern_zoll_jaehrlich = parameter.get('steuern_zoll_mio_eur_a', 75.688) * 1_000_000
        steuern_zoll_pro_kg = steuern_zoll_jaehrlich / jahresproduktion_kg
        
        # ====================================================================
        # ZUSAMMENFASSUNG
        # ====================================================================
        
        kosten_pro_kg = {
            # Variable Kosten
            'Stromkosten (variabel)': stromkosten_pro_kg,
            'Wasserkosten (variabel)': wasserkosten_pro_kg,
            'Cracking thermisch (variabel)': cracking_thermisch_eur_kg,
            
            # CapEx (amortisiert)
            'Offshore-Windpark (CapEx)': windpark_capex_pro_kg,
            'Elektrolyse (CapEx)': elektrolyse_capex_pro_kg,
            'Wasseraufbereitung (CapEx)': wasseraufbereitung_capex_pro_kg,
            'Ammoniaksynthese (CapEx)': haber_bosch_capex_pro_kg_h2,
            'ASU (CapEx)': asu_capex_pro_kg_h2,
            'NH₃-Terminal (CapEx)': nh3_terminal_capex_pro_kg,
            'Schiffe (CapEx)': schiffe_capex_pro_kg,
            'Lager Tanks (CapEx)': lager_tanks_capex_pro_kg,
            'NH₃-Cracking (CapEx)': cracker_capex_pro_kg_h2,
            'Speicher (CapEx)': speicher_capex_pro_kg,
            'Infrastruktur (CapEx)': infrastruktur_capex_pro_kg,
            
            # OpEx (jährlich)
            'Offshore-Windpark (OpEx)': windpark_opex_pro_kg,
            'Elektrolyse (OpEx)': elektrolyse_opex_pro_kg,
            'Wasseraufbereitung (OpEx)': wasseraufbereitung_opex_pro_kg,
            'Ammoniaksynthese (OpEx)': haber_bosch_opex_pro_kg_h2,
            'ASU (OpEx)': asu_opex_pro_kg_h2,
            'NH₃-Terminal (OpEx)': nh3_terminal_opex_pro_kg,
            'Schiffe Charter (OpEx)': schiffe_opex_pro_kg,
            'Steuern & Zoll (OpEx)': steuern_zoll_pro_kg,
        }
        
        gesamt_kosten_pro_kg = sum(kosten_pro_kg.values())
        gesamtkosten_jaehrlich = gesamt_kosten_pro_kg * jahresproduktion_kg
        
        return {
            'kosten_pro_kg': kosten_pro_kg,
            'gesamt_kosten_pro_kg': gesamt_kosten_pro_kg,
            'jahresproduktion_kg': jahresproduktion_kg,
            'gesamtkosten_jaehrlich_eur': gesamtkosten_jaehrlich,
            'parameter': parameter
        }


# ============================================================================
# 3. DESKTOP-APP MIT ALLEN PARAMETERN
# ============================================================================

class WasserstoffAppErweitert:
    """Erweiterte Desktop-Anwendung mit allen Parametern und Diagramm"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Wasserstoff-Kostenrechner - Erweiterte Version")
        self.root.geometry("1400x900")
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
        """Erstellt die Benutzeroberfläche"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.primary_color, height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🌊 Wasserstoff-Kostenrechner - Erweiterte Version",
            font=("Arial", 18, "bold"),
            bg=self.primary_color,
            fg="white"
        )
        title_label.pack(pady=15)
        
        # Hauptcontainer mit Scrollbar
        canvas = tk.Canvas(self.root, bg=self.bg_color)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Hauptcontainer
        main_container = tk.Frame(scrollable_frame, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Linke Seite - Eingabefelder in Tabs
        notebook = ttk.Notebook(main_container)
        notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Tab 1: Produktion
        tab_produktion = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(tab_produktion, text="1. Produktion")
        self.create_produktion_tab(tab_produktion)
        
        # Tab 2: Windpark
        tab_windpark = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(tab_windpark, text="2. Windpark")
        self.create_windpark_tab(tab_windpark)
        
        # Tab 3: Elektrolyse
        tab_elektrolyse = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(tab_elektrolyse, text="3. Elektrolyse")
        self.create_elektrolyse_tab(tab_elektrolyse)
        
        # Tab 4: Ammoniak
        tab_ammoniak = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(tab_ammoniak, text="4. Ammoniak")
        self.create_ammoniak_tab(tab_ammoniak)
        
        # Tab 5: Transport
        tab_transport = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(tab_transport, text="5. Transport")
        self.create_transport_tab(tab_transport)
        
        # Tab 6: Cracking
        tab_cracking = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(tab_cracking, text="6. Cracking")
        self.create_cracking_tab(tab_cracking)
        
        # Tab 7: Sonstiges
        tab_sonstiges = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(tab_sonstiges, text="7. Sonstiges")
        self.create_sonstiges_tab(tab_sonstiges)
        
        # Berechnen Button
        button_frame = tk.Frame(scrollable_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        calc_button = tk.Button(
            button_frame,
            text="🔢 BERECHNUNG DURCHFÜHREN",
            command=self.berechne_kosten,
            bg=self.secondary_color,
            fg="white",
            font=("Arial", 14, "bold"),
            padx=30,
            pady=15,
            cursor="hand2",
            relief=tk.FLAT
        )
        calc_button.pack()
        
        # Rechte Seite - Ergebnisse und Diagramm
        result_container = tk.Frame(main_container, bg=self.bg_color)
        result_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Ergebnis-Felder
        result_frame = tk.LabelFrame(
            result_container,
            text="Ergebnisse",
            font=("Arial", 12, "bold"),
            bg=self.bg_color,
            padx=15,
            pady=15
        )
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Ergebnis-Textbereich
        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            wrap=tk.WORD,
            width=50,
            height=20,
            font=("Consolas", 9),
            bg="white",
            fg="#333",
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Diagramm-Frame
        diagram_frame = tk.LabelFrame(
            result_container,
            text="Kostenverteilung (Gestapeltes Säulendiagramm)",
            font=("Arial", 12, "bold"),
            bg=self.bg_color,
            padx=15,
            pady=15
        )
        diagram_frame.pack(fill=tk.BOTH, expand=True)
        
        # Matplotlib Figure
        if MATPLOTLIB_VERFÜGBAR:
            self.fig, self.ax = plt.subplots(figsize=(10, 6))
            self.canvas_diagram = FigureCanvasTkAgg(self.fig, diagram_frame)
            self.canvas_diagram.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            self.diagram_label = tk.Label(
                diagram_frame,
                text="Matplotlib nicht verfügbar.\nBitte installieren Sie matplotlib und numpy:\npip install matplotlib numpy",
                font=("Arial", 10),
                bg=self.bg_color,
                fg="red",
                justify=tk.LEFT
            )
            self.diagram_label.pack(fill=tk.BOTH, expand=True)
            self.fig = None
            self.ax = None
            self.canvas_diagram = None
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Initiale Nachricht
        self.result_text.insert(tk.END, "Bitte geben Sie alle Parameter ein\nund klicken Sie auf 'BERECHNUNG DURCHFÜHREN'.\n\n")
        self.result_text.config(state=tk.DISABLED)
    
    def create_produktion_tab(self, parent):
        """Tab für Produktionsparameter"""
        frame = tk.Frame(parent, bg=self.bg_color)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_input_field(frame, "Zielproduktion (kt H₂/Jahr):", "zielproduktion_kt", "110", "zielproduktion_kt")
        self.create_input_field(frame, "Elektrischer Energiebedarf (TWh/a):", "energiebedarf_twh_a", "5.5", "energiebedarf_twh_a")
        self.create_input_field(frame, "Spezifischer Strombedarf (kWh/kg H₂):", "strombedarf_kwh_kg", "50", "strombedarf_kwh_kg")
        self.create_input_field(frame, "USD zu EUR Kurs:", "usd_zu_eur_kurs", "0.92", "usd_zu_eur_kurs")
    
    def create_windpark_tab(self, parent):
        """Tab für Windpark-Parameter"""
        frame = tk.Frame(parent, bg=self.bg_color)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_input_field(frame, "Anzahl Windkraftanlagen:", "anzahl_turbinen", "240", "anzahl_turbinen")
        self.create_input_field(frame, "Installierte Gesamtleistung (GW):", "windpark_leistung_gw", "2.4", "windpark_leistung_gw")
        self.create_input_field(frame, "Kapazitätsfaktor (%):", "kapazitaetsfaktor_prozent", "51", "kapazitaetsfaktor_prozent")
        self.create_input_field(frame, "Jährliche OpEx Windpark (Mio USD/a):", "windpark_opex_jaehrlich_mio_usd", "229.5", "windpark_opex_jaehrlich_mio_usd")
        self.create_input_field(frame, "Gesamtkosten über 25 Jahre (Mrd USD):", "windpark_capex_25j_mrd_usd", "5.74", "windpark_capex_25j_mrd_usd")
    
    def create_elektrolyse_tab(self, parent):
        """Tab für Elektrolyse-Parameter"""
        frame = tk.Frame(parent, bg=self.bg_color)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Variable Kosten
        tk.Label(frame, text="Variable Kosten:", font=("Arial", 10, "bold"), bg=self.bg_color).pack(anchor="w", pady=(0, 5))
        self.create_input_field(frame, "Strompreis (EUR/kWh) *:", "strompreis_eur_kwh", "0", "strompreis_eur_kwh")
        self.create_input_field(frame, "oder LCOE (EUR/kWh):", "lcoe_eur_kwh", "0", "lcoe_eur_kwh")
        
        # CapEx
        tk.Label(frame, text="CapEx (Investition):", font=("Arial", 10, "bold"), bg=self.bg_color).pack(anchor="w", pady=(10, 5))
        self.create_input_field(frame, "Elektrolyseur-Leistung (MW):", "elektrolyseur_leistung_mw", "630", "elektrolyseur_leistung_mw")
        self.create_input_field(frame, "CAPEX Elektrolyse (Mio EUR):", "elektrolyse_capex_mio_eur", "0", "elektrolyse_capex_mio_eur")
        self.create_input_field(frame, "Nutzungsdauer Elektrolyse (Jahre):", "elektrolyse_nutzungsdauer_jahre", "20", "elektrolyse_nutzungsdauer_jahre")
        
        # OpEx
        tk.Label(frame, text="OpEx (Betriebskosten):", font=("Arial", 10, "bold"), bg=self.bg_color).pack(anchor="w", pady=(10, 5))
        self.create_input_field(frame, "OpEx Elektrolyse (Mio EUR/a):", "elektrolyse_opex_mio_eur_a", "0", "elektrolyse_opex_mio_eur_a")
        self.create_input_field(frame, "oder OpEx (% vom CapEx):", "elektrolyse_opex_prozent_capex", "0", "elektrolyse_opex_prozent_capex")
        
        # Wasseraufbereitung
        tk.Label(frame, text="Wasseraufbereitung:", font=("Arial", 10, "bold"), bg=self.bg_color).pack(anchor="w", pady=(10, 5))
        self.create_input_field(frame, "Wasserbedarf (Liter/Stunde):", "wasserbedarf_l_h", "125000", "wasserbedarf_l_h")
        self.create_input_field(frame, "CAPEX Wasseraufbereitung (Mio EUR):", "wasseraufbereitung_capex_mio_eur", "0", "wasseraufbereitung_capex_mio_eur")
        self.create_input_field(frame, "Nutzungsdauer Wasseraufbereitung (Jahre):", "wasseraufbereitung_nutzungsdauer_jahre", "20", "wasseraufbereitung_nutzungsdauer_jahre")
        self.create_input_field(frame, "OpEx Wasseraufbereitung (Mio EUR/a):", "wasseraufbereitung_opex_mio_eur_a", "0", "wasseraufbereitung_opex_mio_eur_a")
        self.create_input_field(frame, "oder Wasserpreis (EUR/m³):", "wasserpreis_eur_m3", "0", "wasserpreis_eur_m3")
    
    def create_ammoniak_tab(self, parent):
        """Tab für Ammoniak-Parameter"""
        frame = tk.Frame(parent, bg=self.bg_color)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_input_field(frame, "NH₃-Bedarf (kt NH₃/Jahr):", "nh3_bedarf_kt", "687", "nh3_bedarf_kt")
        
        # Haber-Bosch
        tk.Label(frame, text="Haber-Bosch (Ammoniaksynthese):", font=("Arial", 10, "bold"), bg=self.bg_color).pack(anchor="w", pady=(10, 5))
        self.create_input_field(frame, "Leistung (MW) [optional]:", "haber_bosch_leistung_mw", "0", "haber_bosch_leistung_mw")
        self.create_input_field(frame, "CAPEX Haber-Bosch (Mio USD):", "haber_bosch_capex_mio_usd", "0", "haber_bosch_capex_mio_usd")
        self.create_input_field(frame, "Nutzungsdauer Haber-Bosch (Jahre):", "haber_bosch_nutzungsdauer_jahre", "20", "haber_bosch_nutzungsdauer_jahre")
        self.create_input_field(frame, "OpEx Haber-Bosch (Mio EUR/a):", "haber_bosch_opex_mio_eur_a", "0", "haber_bosch_opex_mio_eur_a")
        self.create_input_field(frame, "oder Strombedarf (GWh/a):", "haber_bosch_strombedarf_gwh_a", "0", "haber_bosch_strombedarf_gwh_a")
        
        # ASU
        tk.Label(frame, text="ASU (Stickstoffbereitstellung):", font=("Arial", 10, "bold"), bg=self.bg_color).pack(anchor="w", pady=(10, 5))
        self.create_input_field(frame, "ASU-Kapazität (t N₂/Tag):", "asu_kapazitaet_t_n2_tag", "1550", "asu_kapazitaet_t_n2_tag")
        self.create_input_field(frame, "CAPEX ASU (Mio USD):", "asu_capex_mio_usd", "200", "asu_capex_mio_usd")
        self.create_input_field(frame, "Nutzungsdauer ASU (Jahre):", "asu_nutzungsdauer_jahre", "20", "asu_nutzungsdauer_jahre")
        self.create_input_field(frame, "OpEx ASU (Mio EUR/a):", "asu_opex_mio_eur_a", "0", "asu_opex_mio_eur_a")
        self.create_input_field(frame, "oder Strombedarf (kWh/t N₂):", "asu_strombedarf_kwh_t_n2", "0", "asu_strombedarf_kwh_t_n2")
    
    def create_transport_tab(self, parent):
        """Tab für Transport-Parameter"""
        frame = tk.Frame(parent, bg=self.bg_color)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_input_field(frame, "Transportdistanz (km):", "transport_distanz_km", "13000", "transport_distanz_km")
        
        # Terminal
        tk.Label(frame, text="NH₃-Terminal:", font=("Arial", 10, "bold"), bg=self.bg_color).pack(anchor="w", pady=(10, 5))
        self.create_input_field(frame, "CAPEX Terminal (Mio EUR):", "nh3_terminal_capex_mio_eur", "0", "nh3_terminal_capex_mio_eur")
        self.create_input_field(frame, "Nutzungsdauer Terminal (Jahre):", "nh3_terminal_nutzungsdauer_jahre", "20", "nh3_terminal_nutzungsdauer_jahre")
        self.create_input_field(frame, "OpEx Terminal (Mio EUR/a):", "nh3_terminal_opex_mio_eur_a", "0", "nh3_terminal_opex_mio_eur_a")
        
        # Schiffe
        tk.Label(frame, text="Schiffe:", font=("Arial", 10, "bold"), bg=self.bg_color).pack(anchor="w", pady=(10, 5))
        self.create_input_field(frame, "CAPEX Schiffe (Mio EUR):", "schiffe_capex_mio_eur", "0", "schiffe_capex_mio_eur")
        self.create_input_field(frame, "Nutzungsdauer Schiffe (Jahre):", "schiffe_nutzungsdauer_jahre", "20", "schiffe_nutzungsdauer_jahre")
        self.create_input_field(frame, "oder Charter OpEx (Mio EUR/a):", "charter_opex_mio_eur_a", "0", "charter_opex_mio_eur_a")
        
        # Lager
        tk.Label(frame, text="Lager:", font=("Arial", 10, "bold"), bg=self.bg_color).pack(anchor="w", pady=(10, 5))
        self.create_input_field(frame, "CAPEX Lager Tanks (Mio EUR):", "lager_tanks_capex_mio_eur", "0", "lager_tanks_capex_mio_eur")
        self.create_input_field(frame, "Nutzungsdauer Lager (Jahre):", "lager_tanks_nutzungsdauer_jahre", "20", "lager_tanks_nutzungsdauer_jahre")
        
        # Optional
        tk.Label(frame, text="Optional (nur für Info):", font=("Arial", 10, "italic"), bg=self.bg_color).pack(anchor="w", pady=(10, 5))
        self.create_input_field(frame, "Transportdauer (Tage):", "transport_dauer_tage", "26", "transport_dauer_tage")
        self.create_input_field(frame, "Anzahl Schiffe:", "anzahl_schiffe", "4", "anzahl_schiffe")
        self.create_input_field(frame, "Anzahl Fahrten pro Jahr:", "anzahl_fahrten_pro_jahr", "24", "anzahl_fahrten_pro_jahr")
    
    def create_cracking_tab(self, parent):
        """Tab für Cracking-Parameter"""
        frame = tk.Frame(parent, bg=self.bg_color)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_input_field(frame, "Cracker-Kapazität (t H₂/Tag):", "cracker_kapazitaet_t_h2_d", "330", "cracker_kapazitaet_t_h2_d")
        self.create_input_field(frame, "CAPEX Cracker (Mio EUR):", "cracker_capex_mio_eur", "500", "cracker_capex_mio_eur")
        self.create_input_field(frame, "Nutzungsdauer Cracker (Jahre):", "cracker_nutzungsdauer_jahre", "20", "cracker_nutzungsdauer_jahre")
        self.create_input_field(frame, "Thermische Energiekosten (EUR/kg H₂):", "cracking_thermisch_eur_kg", "0", "cracking_thermisch_eur_kg")
    
    def create_sonstiges_tab(self, parent):
        """Tab für sonstige Parameter"""
        frame = tk.Frame(parent, bg=self.bg_color)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_input_field(frame, "CAPEX Speicher (Mio EUR):", "speicher_capex_mio_eur", "0", "speicher_capex_mio_eur")
        self.create_input_field(frame, "Nutzungsdauer Speicher (Jahre):", "speicher_nutzungsdauer_jahre", "20", "speicher_nutzungsdauer_jahre")
        self.create_input_field(frame, "CAPEX Infrastruktur (Mio EUR):", "infrastruktur_capex_mio_eur", "0", "infrastruktur_capex_mio_eur")
        self.create_input_field(frame, "Nutzungsdauer Infrastruktur (Jahre):", "infrastruktur_nutzungsdauer_jahre", "20", "infrastruktur_nutzungsdauer_jahre")
        self.create_input_field(frame, "Steuern & Zoll (Mio EUR/a):", "steuern_zoll_mio_eur_a", "75.688", "steuern_zoll_mio_eur_a")
    
    def create_input_field(self, parent, label_text, field_name, default_value, tooltip_key=None):
        """Erstellt ein Eingabefeld mit Label und Info-Icon"""
        frame = tk.Frame(parent, bg=self.bg_color)
        frame.pack(fill=tk.X, pady=5)
        
        # Label-Frame für Label und Info-Icon
        label_frame = tk.Frame(frame, bg=self.bg_color)
        label_frame.pack(fill=tk.X)
        
        label = tk.Label(
            label_frame,
            text=label_text,
            font=("Arial", 9),
            bg=self.bg_color,
            anchor="w"
        )
        label.pack(side=tk.LEFT)
        
        # Info-Icon
        if tooltip_key and tooltip_key in TOOLTIP_TEXTE:
            info_icon = tk.Label(
                label_frame,
                text="ℹ️",
                font=("Arial", 10),
                bg=self.bg_color,
                fg="#667eea",
                cursor="hand2"
            )
            info_icon.pack(side=tk.LEFT, padx=(5, 0))
            ToolTip(info_icon, TOOLTIP_TEXTE[tooltip_key])
        
        entry = tk.Entry(
            frame,
            font=("Arial", 10),
            relief=tk.SOLID,
            borderwidth=1
        )
        entry.insert(0, default_value)
        entry.pack(fill=tk.X, ipady=3)
        
        setattr(self, field_name, entry)
    
    def berechne_kosten(self):
        """Führt die Kostenberechnung durch"""
        try:
            # Alle Parameter sammeln
            parameter = {}
            
            # Produktion
            parameter['zielproduktion_kt'] = float(self.zielproduktion_kt.get())
            parameter['energiebedarf_twh_a'] = float(self.energiebedarf_twh_a.get())
            parameter['strombedarf_kwh_kg'] = float(self.strombedarf_kwh_kg.get())
            parameter['usd_zu_eur_kurs'] = float(self.usd_zu_eur_kurs.get())
            
            # Windpark
            parameter['anzahl_turbinen'] = float(self.anzahl_turbinen.get())
            parameter['windpark_leistung_gw'] = float(self.windpark_leistung_gw.get())
            parameter['kapazitaetsfaktor_prozent'] = float(self.kapazitaetsfaktor_prozent.get())
            parameter['windpark_opex_jaehrlich_mio_usd'] = float(self.windpark_opex_jaehrlich_mio_usd.get())
            parameter['windpark_capex_25j_mrd_usd'] = float(self.windpark_capex_25j_mrd_usd.get())
            
            # Elektrolyse
            parameter['elektrolyseur_leistung_mw'] = float(self.elektrolyseur_leistung_mw.get())
            parameter['elektrolyse_capex_mio_eur'] = float(self.elektrolyse_capex_mio_eur.get())
            parameter['elektrolyse_nutzungsdauer_jahre'] = float(self.elektrolyse_nutzungsdauer_jahre.get())
            parameter['strompreis_eur_kwh'] = float(self.strompreis_eur_kwh.get())
            parameter['lcoe_eur_kwh'] = float(self.lcoe_eur_kwh.get())
            parameter['elektrolyse_opex_mio_eur_a'] = float(self.elektrolyse_opex_mio_eur_a.get())
            parameter['elektrolyse_opex_prozent_capex'] = float(self.elektrolyse_opex_prozent_capex.get())
            parameter['wasserbedarf_l_h'] = float(self.wasserbedarf_l_h.get())
            parameter['wasseraufbereitung_capex_mio_eur'] = float(self.wasseraufbereitung_capex_mio_eur.get())
            parameter['wasseraufbereitung_nutzungsdauer_jahre'] = float(self.wasseraufbereitung_nutzungsdauer_jahre.get())
            parameter['wasseraufbereitung_opex_mio_eur_a'] = float(self.wasseraufbereitung_opex_mio_eur_a.get())
            parameter['wasserpreis_eur_m3'] = float(self.wasserpreis_eur_m3.get())
            
            # Ammoniak
            parameter['nh3_bedarf_kt'] = float(self.nh3_bedarf_kt.get())
            parameter['haber_bosch_leistung_mw'] = float(self.haber_bosch_leistung_mw.get())
            parameter['haber_bosch_capex_mio_usd'] = float(self.haber_bosch_capex_mio_usd.get())
            parameter['haber_bosch_nutzungsdauer_jahre'] = float(self.haber_bosch_nutzungsdauer_jahre.get())
            parameter['haber_bosch_opex_mio_eur_a'] = float(self.haber_bosch_opex_mio_eur_a.get())
            parameter['haber_bosch_strombedarf_gwh_a'] = float(self.haber_bosch_strombedarf_gwh_a.get())
            parameter['asu_kapazitaet_t_n2_tag'] = float(self.asu_kapazitaet_t_n2_tag.get())
            parameter['asu_capex_mio_usd'] = float(self.asu_capex_mio_usd.get())
            parameter['asu_nutzungsdauer_jahre'] = float(self.asu_nutzungsdauer_jahre.get())
            parameter['asu_opex_mio_eur_a'] = float(self.asu_opex_mio_eur_a.get())
            parameter['asu_strombedarf_kwh_t_n2'] = float(self.asu_strombedarf_kwh_t_n2.get())
            
            # Transport
            parameter['transport_distanz_km'] = float(self.transport_distanz_km.get())
            parameter['nh3_terminal_capex_mio_eur'] = float(self.nh3_terminal_capex_mio_eur.get())
            parameter['nh3_terminal_nutzungsdauer_jahre'] = float(self.nh3_terminal_nutzungsdauer_jahre.get())
            parameter['nh3_terminal_opex_mio_eur_a'] = float(self.nh3_terminal_opex_mio_eur_a.get())
            parameter['schiffe_capex_mio_eur'] = float(self.schiffe_capex_mio_eur.get())
            parameter['schiffe_nutzungsdauer_jahre'] = float(self.schiffe_nutzungsdauer_jahre.get())
            parameter['charter_opex_mio_eur_a'] = float(self.charter_opex_mio_eur_a.get())
            parameter['lager_tanks_capex_mio_eur'] = float(self.lager_tanks_capex_mio_eur.get())
            parameter['lager_tanks_nutzungsdauer_jahre'] = float(self.lager_tanks_nutzungsdauer_jahre.get())
            # Optional
            parameter['transport_dauer_tage'] = float(self.transport_dauer_tage.get())
            parameter['anzahl_schiffe'] = float(self.anzahl_schiffe.get())
            parameter['anzahl_fahrten_pro_jahr'] = float(self.anzahl_fahrten_pro_jahr.get())
            
            # Cracking
            parameter['cracker_kapazitaet_t_h2_d'] = float(self.cracker_kapazitaet_t_h2_d.get())
            parameter['cracker_capex_mio_eur'] = float(self.cracker_capex_mio_eur.get())
            parameter['cracker_nutzungsdauer_jahre'] = float(self.cracker_nutzungsdauer_jahre.get())
            parameter['cracking_thermisch_eur_kg'] = float(self.cracking_thermisch_eur_kg.get())
            
            # Sonstiges
            parameter['speicher_capex_mio_eur'] = float(self.speicher_capex_mio_eur.get())
            parameter['speicher_nutzungsdauer_jahre'] = float(self.speicher_nutzungsdauer_jahre.get())
            parameter['infrastruktur_capex_mio_eur'] = float(self.infrastruktur_capex_mio_eur.get())
            parameter['infrastruktur_nutzungsdauer_jahre'] = float(self.infrastruktur_nutzungsdauer_jahre.get())
            parameter['steuern_zoll_mio_eur_a'] = float(self.steuern_zoll_mio_eur_a.get())
            
            # Validierung
            if parameter['zielproduktion_kt'] <= 0:
                messagebox.showerror("Fehler", "Zielproduktion muss größer als 0 sein!")
                return
            
            # Rechner initialisieren
            rechner = WasserstoffKostenrechnerErweitert()
            ergebnis = rechner.berechne_alle_kosten(parameter)
            
            # Ergebnisse anzeigen
            self.zeige_ergebnisse(ergebnis)
            
        except ValueError as e:
            if "KRITISCH" in str(e):
                messagebox.showerror("Kritischer Fehler", str(e))
            else:
                messagebox.showerror("Fehler", "Bitte geben Sie gültige Zahlen ein!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def zeige_ergebnisse(self, ergebnis):
        """Zeigt die Berechnungsergebnisse an"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        # Formatierung
        def format_currency(value):
            return f"{value:,.4f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        def format_number(value):
            return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        # Header
        output = "=" * 70 + "\n"
        output += "WASSERSTOFF-KOSTENRECHNUNG - ERWEITERTE VERSION\n"
        output += "Strukturiert nach: Variable Kosten | CapEx | OpEx\n"
        output += "=" * 70 + "\n\n"
        
        output += f"Jahresproduktion: {format_number(ergebnis['jahresproduktion_kg'] / 1_000_000)} Mio kg H₂\n\n"
        
        output += "KOSTENAUFSTELLUNG PRO KG H₂:\n"
        output += "-" * 70 + "\n"
        
        kosten_pro_kg = ergebnis['kosten_pro_kg']
        
        # Gruppiert nach Typ
        output += "\nVARIABLE KOSTEN:\n"
        for kategorie, kosten in kosten_pro_kg.items():
            if "(variabel)" in kategorie:
                output += f"  {kategorie:35s}: {format_currency(kosten):>15s} EUR/kg\n"
        
        output += "\nCAPEX (amortisiert):\n"
        for kategorie, kosten in kosten_pro_kg.items():
            if "(CapEx)" in kategorie:
                output += f"  {kategorie:35s}: {format_currency(kosten):>15s} EUR/kg\n"
        
        output += "\nOPEX (jährlich):\n"
        for kategorie, kosten in kosten_pro_kg.items():
            if "(OpEx)" in kategorie:
                output += f"  {kategorie:35s}: {format_currency(kosten):>15s} EUR/kg\n"
        
        output += "-" * 70 + "\n"
        output += f"{'GESAMT':35s}: {format_currency(ergebnis['gesamt_kosten_pro_kg']):>15s} EUR/kg\n\n"
        
        output += "JÄHRLICHE GESAMTKOSTEN:\n"
        output += "-" * 70 + "\n"
        output += f"{format_currency(ergebnis['gesamtkosten_jaehrlich_eur'] / 1_000_000):>15s} Mio EUR/Jahr\n"
        output += f"{format_currency(ergebnis['gesamtkosten_jaehrlich_eur'] / 1_000_000_000):>15s} Mrd EUR/Jahr\n"
        output += "=" * 70 + "\n"
        
        self.result_text.insert(tk.END, output)
        self.result_text.config(state=tk.DISABLED)
        
        # Diagramm erstellen
        self.erstelle_diagramm(ergebnis)
    
    def erstelle_diagramm(self, ergebnis):
        """Erstellt ein gestapeltes Säulendiagramm"""
        if not MATPLOTLIB_VERFÜGBAR or self.ax is None:
            return
        
        self.ax.clear()
        
        kosten_pro_kg = ergebnis['kosten_pro_kg']
        
        # Daten für gestapeltes Diagramm
        kategorien = list(kosten_pro_kg.keys())
        werte = list(kosten_pro_kg.values())
        
        # Farben für jede Kategorie
        farben = plt.cm.Set3(np.linspace(0, 1, len(kategorien)))
        
        # Gestapeltes Säulendiagramm
        bars = self.ax.barh(kategorien, werte, color=farben, edgecolor='black', linewidth=0.5)
        
        # Werte auf den Balken anzeigen
        for i, (kategorie, wert) in enumerate(zip(kategorien, werte)):
            if wert > 0:
                self.ax.text(wert, i, f' {wert:.4f} EUR/kg', 
                           va='center', fontsize=8, fontweight='bold')
        
        self.ax.set_xlabel('Kosten (EUR/kg H₂)', fontsize=11, fontweight='bold')
        self.ax.set_title('Kostenverteilung nach Kategorien (Gestapeltes Säulendiagramm)', 
                         fontsize=12, fontweight='bold', pad=20)
        self.ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        # Gesamtkosten als Text hinzufügen
        gesamt = ergebnis['gesamt_kosten_pro_kg']
        self.ax.text(0.95, 0.02, f'Gesamtkosten: {gesamt:.4f} EUR/kg H₂',
                    transform=self.ax.transAxes, fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                    horizontalalignment='right')
        
        plt.tight_layout()
        self.canvas_diagram.draw()


# ============================================================================
# HAUPTFUNKTION
# ============================================================================

def main():
    """Hauptfunktion - startet Desktop-App"""
    root = tk.Tk()
    app = WasserstoffAppErweitert(root)
    root.mainloop()


if __name__ == "__main__":
    main()
