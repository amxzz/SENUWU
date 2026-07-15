# -*- coding: utf-8 -*-
"""
Geocoding script: Generate master_koordinat_id.csv via Nominatim API.
Output format: Wilayah, Provinsi, Latitude, Longitude
"""
import pandas as pd
import json
import time
import urllib.request
import urllib.parse

INPUT = r"D:\STUDY\Kuliah\flutter\PROJECT\research\HKI - new\dataset\raw\_unique_wilayah.csv"
OUTPUT = r"D:\STUDY\Kuliah\flutter\PROJECT\research\HKI - new\dataset\raw\master_koordinat_id.csv"

def normalize_wilayah(s):
    """Format output: KAB. {NAME} atau KOTA {NAME}"""
    s = str(s).upper().strip()
    import re
    s = re.sub(r'\s+', ' ', s)
    is_kota = s.startswith('KOTA ')
    s = re.sub(r'^(KABUPATEN|KAB\.?|KOTA)\s+', '', s).strip()
    s = re.sub(r'\s+', ' ', s).strip()
    return f"KOTA {s}" if is_kota else f"KAB. {s}"

def geocode_nominatim(kab_kota, provinsi):
    """Geocode via Nominatim API. Returns (lat, lon) or (None, None)."""
    # Build search query
    is_kota = str(kab_kota).lower().startswith('kota ')
    clean_name = kab_kota
    if is_kota:
        clean_name = kab_kota  # keep "Kota" prefix for better Nominatim match
    else:
        clean_name = f"Kabupaten {kab_kota}"
    
    query = f"{clean_name}, {provinsi}, Indonesia"
    
    params = urllib.parse.urlencode({
        'q': query,
        'format': 'json',
        'limit': 1,
        'countrycodes': 'id'
    })
    
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    
    req = urllib.request.Request(url, headers={
        'User-Agent': 'HKI-Research-Geocoding/1.0 (academic research)'
    })
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data and len(data) > 0:
                return float(data[0]['lat']), float(data[0]['lon'])
    except Exception as e:
        pass
    
    return None, None

# Main
df = pd.read_csv(INPUT)
print(f"Geocoding {len(df)} unique wilayah...")

results = []
success = 0
fail = 0

for idx, row in df.iterrows():
    kab_kota = row['Kab/Kota']
    provinsi = row['Provinsi']
    
    lat, lon = geocode_nominatim(kab_kota, provinsi)
    
    wilayah_formatted = normalize_wilayah(kab_kota)
    provinsi_formatted = str(provinsi).upper().strip()
    
    if lat is not None:
        success += 1
        results.append({
            'Wilayah': wilayah_formatted,
            'Provinsi': provinsi_formatted,
            'Latitude': lat,
            'Longitude': lon
        })
    else:
        fail += 1
        results.append({
            'Wilayah': wilayah_formatted,
            'Provinsi': provinsi_formatted,
            'Latitude': None,
            'Longitude': None
        })
        print(f"  FAIL: {wilayah_formatted}, {provinsi_formatted}")
    
    if (idx + 1) % 50 == 0:
        print(f"Progress: {idx+1}/{len(df)} | Success: {success} | Fail: {fail}")
    
    time.sleep(1.1)  # Nominatim rate limit: 1 req/sec

# Save
df_out = pd.DataFrame(results)
df_out.to_csv(OUTPUT, index=False)
print(f"\nDONE: {success} success, {fail} fail out of {len(df)}")
print(f"Saved to: {OUTPUT}")
