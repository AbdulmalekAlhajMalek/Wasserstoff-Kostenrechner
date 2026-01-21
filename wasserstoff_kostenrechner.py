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
