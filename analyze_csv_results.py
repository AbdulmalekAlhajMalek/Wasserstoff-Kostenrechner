# -*- coding: utf-8 -*-
"""
Analyse der Simulierte_Speicherstände.csv
Extrahiert Maxima, Minima, Durchschnitte und wichtige KPIs
"""

import pandas as pd
import numpy as np

# CSV einlesen
print("=" * 80)
print("ANALYSE DER SIMULIERTEN SPEICHERSTÄNDE")
print("=" * 80)
print()

df = pd.read_csv("Simulierte_Speicherstände.csv", parse_dates=['time'])

print(f"Anzahl Zeilen: {len(df):,}")
print(f"Zeitraum: {df['time'].min()} bis {df['time'].max()}")
print(f"Anzahl Jahre: {(df['time'].max() - df['time'].min()).days / 365.25:.1f}")
print()

# H2 Analyse
print("=" * 80)
print("H₂-SPEICHER (LH₂) - ANALYSE")
print("=" * 80)
h2_kg = df['H2_SOC_kg']
h2_t = df['H2_SOC_t']

print(f"Maximaler H₂-SOC: {h2_kg.max():,.2f} kg ({h2_t.max():,.2f} t)")
print(f"Minimaler H₂-SOC: {h2_kg.min():,.2f} kg ({h2_t.min():,.2f} t)")
print(f"Durchschnittlicher H₂-SOC: {h2_kg.mean():,.2f} kg ({h2_t.mean():,.2f} t)")
print(f"Median H₂-SOC: {h2_kg.median():,.2f} kg ({h2_t.median():,.2f} t)")
print(f"Standardabweichung: {h2_kg.std():,.2f} kg ({h2_t.std():,.2f} t)")
print()

# NH3 Analyse
print("=" * 80)
print("NH₃-SPEICHER - ANALYSE")
print("=" * 80)
nh3_t = df['NH3_SOC_t']

print(f"Maximaler NH₃-SOC: {nh3_t.max():,.2f} t")
print(f"Minimaler NH₃-SOC: {nh3_t.min():,.2f} t")
print(f"Durchschnittlicher NH₃-SOC: {nh3_t.mean():,.2f} t")
print(f"Median NH₃-SOC: {nh3_t.median():,.2f} t")
print(f"Standardabweichung: {nh3_t.std():,.2f} t")
print()

# Water Analyse
print("=" * 80)
print("WASSER-SPEICHER - ANALYSE")
print("=" * 80)
water_m3 = df['Water_SOC_m3']

print(f"Maximaler Water SOC: {water_m3.max():,.2f} m³")
print(f"Minimaler Water SOC: {water_m3.min():,.2f} m³")
print(f"Durchschnittlicher Water SOC: {water_m3.mean():,.2f} m³")
print(f"Median Water SOC: {water_m3.median():,.2f} m³")
print(f"Standardabweichung: {water_m3.std():,.2f} m³")
print()

# Zeitreihen-Analyse
print("=" * 80)
print("ZEITREIHEN-ANALYSE")
print("=" * 80)

# H2 Füllstände über Zeit
h2_empty = (h2_kg < 1000).sum()  # < 1 t
h2_low = ((h2_kg >= 1000) & (h2_kg < 100000)).sum()  # 1-100 t
h2_medium = ((h2_kg >= 100000) & (h2_kg < 300000)).sum()  # 100-300 t
h2_high = (h2_kg >= 300000).sum()  # > 300 t

print(f"H₂-Speicher Füllstände:")
print(f"  Sehr niedrig (< 1 t): {h2_empty:,} h ({h2_empty/len(df)*100:.1f}%)")
print(f"  Niedrig (1-100 t): {h2_low:,} h ({h2_low/len(df)*100:.1f}%)")
print(f"  Mittel (100-300 t): {h2_medium:,} h ({h2_medium/len(df)*100:.1f}%)")
print(f"  Hoch (> 300 t): {h2_high:,} h ({h2_high/len(df)*100:.1f}%)")
print()

# NH3 Füllstände
nh3_empty = (nh3_t < 1).sum()
nh3_low = ((nh3_t >= 1) & (nh3_t < 20)).sum()
nh3_medium = ((nh3_t >= 20) & (nh3_t < 40)).sum()
nh3_high = (nh3_t >= 40).sum()

print(f"NH₃-Speicher Füllstände:")
print(f"  Sehr niedrig (< 1 t): {nh3_empty:,} h ({nh3_empty/len(df)*100:.1f}%)")
print(f"  Niedrig (1-20 t): {nh3_low:,} h ({nh3_low/len(df)*100:.1f}%)")
print(f"  Mittel (20-40 t): {nh3_medium:,} h ({nh3_medium/len(df)*100:.1f}%)")
print(f"  Hoch (> 40 t): {nh3_high:,} h ({nh3_high/len(df)*100:.1f}%)")
print()

# Water Füllstände
water_empty = (water_m3 < 100).sum()
water_low = ((water_m3 >= 100) & (water_m3 < 1000)).sum()
water_medium = ((water_m3 >= 1000) & (water_m3 < 2000)).sum()
water_high = (water_m3 >= 2000).sum()

print(f"Wasser-Speicher Füllstände:")
print(f"  Sehr niedrig (< 100 m³): {water_empty:,} h ({water_empty/len(df)*100:.1f}%)")
print(f"  Niedrig (100-1000 m³): {water_low:,} h ({water_low/len(df)*100:.1f}%)")
print(f"  Mittel (1000-2000 m³): {water_medium:,} h ({water_medium/len(df)*100:.1f}%)")
print(f"  Hoch (> 2000 m³): {water_high:,} h ({water_high/len(df)*100:.1f}%)")
print()

# Jahresanalyse
print("=" * 80)
print("JAHRESANALYSE (Erstes und Letztes Jahr)")
print("=" * 80)

df['year'] = df['time'].dt.year
first_year = df[df['year'] == df['year'].min()]
last_year = df[df['year'] == df['year'].max()]

print(f"Erstes Jahr ({df['year'].min()}):")
print(f"  H₂ max: {first_year['H2_SOC_kg'].max():,.0f} kg")
print(f"  NH₃ max: {first_year['NH3_SOC_t'].max():,.2f} t")
print(f"  Water max: {first_year['Water_SOC_m3'].max():,.2f} m³")
print()

print(f"Letztes Jahr ({df['year'].max()}):")
print(f"  H₂ max: {last_year['H2_SOC_kg'].max():,.0f} kg")
print(f"  NH₃ max: {last_year['NH3_SOC_t'].max():,.2f} t")
print(f"  Water max: {last_year['Water_SOC_m3'].max():,.2f} m³")
print()

print("=" * 80)
print("ANALYSE ABGESCHLOSSEN")
print("=" * 80)
