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
