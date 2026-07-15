# -*- coding: utf-8 -*-
"""
narrative.py — Module untuk generate narrative sentences (bahasa publik)
untuk dashboard Streamlit HKI.

Revisi Lecture #5: Hasil & Evaluasi berisi sentences pemetaan yang:
- Menjelaskan kenapa daerah cocok ke klaster tersebut
- Menyebutkan fitur dominan yang berbobot
- Bahasa mudah dipahami publik (hindari akademik/teknikal tinggi)
"""

import pandas as pd
import numpy as np

# Mapping fitur ke label publik
FEATURE_LABELS = {
    'UHH': 'Umur Harapan Hidup',
    'Rata_rata_Lama_Sekolah': 'Rata-rata Lama Sekolah',
    'PDRB_Konstan': 'PDRB (Perekonomian)',
    'Persentase_Penduduk_Miskin': 'Persentase Penduduk Miskin',
    'Pengeluaran_per_Kapita': 'Pengeluaran per Kapita',
    'Sanitasi_Layak': 'Akses Sanitasi Layak',
    'TPT': 'Tingkat Pengangguran Terbuka',
}

FEATURE_EMOJI = {
    'UHH': ':material/health_and_safety:',
    'Rata_rata_Lama_Sekolah': ':material/school:',
    'PDRB_Konstan': ':material/account_balance:',
    'Persentase_Penduduk_Miskin': ':material/trending_down:',
    'Pengeluaran_per_Kapita': ':material/shopping_bag:',
    'Sanitasi_Layak': ':material/water_drop:',
    'TPT': ':material/work_off:',
}

# Deskripsi tipologi klaster (bahasa publik)
CLUSTER_DESCRIPTIONS = {
    0: "Sentra Industri — daerah dengan aktivitas ekonomi yang didominasi manufaktur/industri, kualitas hidup menengah, dan infrastruktur yang cukup.",
    1: "Area Rentan — daerah yang masih menghadapi tantangan pembangunan, dengan tingkat kemiskinan tinggi dan ekonomi terbatas.",
    2: "Transisi Seimbang — daerah dengan perekonomian kuat, kualitas hidup baik, dan akses infrastruktur yang memadai.",
    3: "Urban Maju — daerah perkotaan/metropolitan dengan tingkat pembangunan tinggi, meski masih ada tantangan pengangguran.",
    -1: "Entitas Atipikal — daerah dengan profil indikator ekstrem atau unik (outlier statistik) yang tidak mengikuti pola umum nasional."
}


def format_value(value, feature_name):
    """Format nilai fitur untuk display yang user-friendly."""
    if feature_name == 'PDRB_Konstan':
        actual_val = value * 1e6
        if actual_val >= 1e12:
            return f"Rp {actual_val/1e12:.1f} triliun"
        elif actual_val >= 1e9:
            return f"Rp {actual_val/1e9:.1f} miliar"
        elif actual_val >= 1e6:
            return f"Rp {actual_val/1e6:.1f} juta"
        else:
            return f"Rp {actual_val:,.0f}"
    elif feature_name in ['Persentase_Penduduk_Miskin', 'Sanitasi_Layak', 'TPT']:
        return f"{value:.1f}%"
    elif feature_name == 'UHH':
        return f"{value:.1f} tahun"
    elif feature_name == 'Rata_rata_Lama_Sekolah':
        return f"{value:.1f} tahun"
    elif feature_name == 'Pengeluaran_per_Kapita':
        # value is in 'Ribu Rp', so 14911 = 14,911,000
        formatted = f"{value * 1000:,.0f}".replace(',', '.')
        return f"Rp {formatted} / Tahun"
    else:
        return f"{value:.2f}"


def interpret_z_score(z):
    """Interpretasi z-score ke bahasa publik."""
    abs_z = abs(z)
    if abs_z >= 2.0:
        return "sangat jauh" + (" di atas" if z > 0 else " di bawah")
    elif abs_z >= 1.0:
        return "jauh" + (" di atas" if z > 0 else " di bawah")
    elif abs_z >= 0.5:
        return ("di atas" if z > 0 else "di bawah")
    else:
        return "mendekati"


def interpret_fitur(feat, value, centroid, z, is_positive=True):
    """Interpretasi singkat per fitur dalam bahasa publik."""
    interp = interpret_z_score(z)

    if feat == 'UHH':
        if z > 0.5:
            return f"warga di sini cenderung hidup lebih lama ({value:.1f} tahun vs rata-rata {centroid:.1f} tahun)"
        elif z < -0.5:
            return f"warga di sini cenderung hidup lebih singkat ({value:.1f} tahun vs rata-rata {centroid:.1f} tahun)"
        else:
            return f"usia harapan hidup warga setara rata-rata klaster ({value:.1f} tahun)"
    elif feat == 'PDRB_Konstan':
        if z > 0.5:
            return f"aktivitas ekonomi sangat tinggi ({format_value(value, feat)} vs rata-rata {format_value(centroid, feat)})"
        elif z < -0.5:
            return f"aktivitas ekonomi terbatas ({format_value(value, feat)} vs rata-rata {format_value(centroid, feat)})"
        else:
            return f"aktivitas ekonomi setara rata-rata klaster ({format_value(value, feat)})"
    elif feat == 'TPT':
        if z > 0.5:
            return f"pengangguran cukup tinggi ({value:.1f}% vs rata-rata {centroid:.1f}%) — lapangan kerja terbatas"
        elif z < -0.5:
            return f"pengangguran rendah ({value:.1f}% vs rata-rata {centroid:.1f}%) — banyak lapangan kerja"
        else:
            return f"tingkat pengangguran setara rata-rata ({value:.1f}%)"
    elif feat == 'Persentase_Penduduk_Miskin':
        if z > 0.5:
            return f"kemiskinan masih tinggi ({value:.1f}% vs rata-rata {centroid:.1f}%) — perlu perhatian khusus"
        elif z < -0.5:
            return f"kemiskinan rendah ({value:.1f}% vs rata-rata {centroid:.1f}%) — kesejahteraan baik"
        else:
            return f"tingkat kemiskinan setara rata-rata ({value:.1f}%)"
    elif feat == 'Rata_rata_Lama_Sekolah':
        if z > 0.5:
            return f"warga lebih berpendidikan ({value:.1f} tahun vs rata-rata {centroid:.1f} tahun)"
        elif z < -0.5:
            return f"pendidikan warga masih rendah ({value:.1f} tahun vs rata-rata {centroid:.1f} tahun)"
        else:
            return f"pendidikan setara rata-rata ({value:.1f} tahun)"
    elif feat == 'Pengeluaran_per_Kapita':
        if z > 0.5:
            return f"daya beli warga tinggi ({format_value(value, feat)} vs rata-rata {format_value(centroid, feat)})"
        elif z < -0.5:
            return f"daya beli warga rendah ({format_value(value, feat)} vs rata-rata {format_value(centroid, feat)})"
        else:
            return f"daya beli setara rata-rata ({format_value(value, feat)})"
    elif feat == 'Sanitasi_Layak':
        if z > 0.5:
            return f"akses sanitasi sangat baik ({value:.1f}% vs rata-rata {centroid:.1f}%)"
        elif z < -0.5:
            return f"akses sanitasi masih terbatas ({value:.1f}% vs rata-rata {centroid:.1f}%)"
        else:
            return f"akses sanitasi setara rata-rata ({value:.1f}%)"
    return ""


def generate_narrative(daerah_name, provinsi, klaster, tipologi, welfare_score,
                       feature_values, centroid_values, z_scores, feature_weights,
                       top_features, feature_importances):
    """
    Generate narrative sentences untuk Hasil & Evaluasi (bahasa publik).

    Parameters:
    -----------
    daerah_name : str — nama kab/kota
    provinsi : str — nama provinsi
    klaster : int — nomor klaster
    tipologi : str — nama tipologi klaster
    welfare_score : float — composite welfare score (0-1)
    feature_values : dict — nilai aktual per fitur
    centroid_values : dict — nilai centroid klaster per fitur
    z_scores : dict — z-score per fitur
    feature_weights : dict — bobot per fitur
    top_features : list of (feat, z, weight) — top-3 fitur dominan
    feature_importances : dict — RF importance per fitur

    Returns:
    --------
    str — narrative dalam bahasa publik (markdown)
    """
    narrative = []
    skor_str = f"{welfare_score:.3f}".replace('.', ',')
    
    html = []
    # Style definitions inline
    html.append("<style>")
    html.append(".n-title { font-weight:bold; font-size:1.5em; color:#1C1714; margin-top:0px; margin-bottom:16px; border-bottom:2px solid #8a620b; padding-bottom:8px; }")
    html.append(".n-section { font-weight:bold; font-size:1.2em; color:#1C1714; margin-top:24px; margin-bottom:8px; }")
    html.append(".n-text { margin-bottom: 8px; line-height: 1.6; }")
    html.append(".n-table { width:100%; border-collapse:collapse; margin: 16px 0; }")
    html.append(".n-table th { text-align:left; padding:8px; border-bottom:2px solid #9C8B7A; color:#1C1714; }")
    html.append(".n-table td { padding:8px; border-bottom:1px solid #E8DFD4; }")
    html.append(".n-list { margin-top: 0; margin-bottom: 8px; padding-left: 20px; }")
    html.append("</style>")
    
    html.append("<div style='font-family: \"Crimson Pro\", serif; font-size: 16px; color: #1C1714;'>")
    
    html.append("<div class='n-title'>Hasil Analisis Wilayah</div>")
    
    # Ringkasan
    html.append("<div class='n-section' style='margin-top:0;'>Ringkasan</div>")
    html.append(f"<div class='n-text'>Kabupaten/Kota : {daerah_name}</div>")
    html.append(f"<div class='n-text'>Provinsi : {provinsi}</div>")
    html.append(f"<div class='n-text'>Klaster : Klaster {klaster} – {tipologi}</div>")
    html.append(f"<div class='n-text' style='display:flex; align-items:center;'>Skor Kesejahteraan : <span style='background-color:#F3EFE9; border:1px solid #8a620b; color:#8a620b; padding:2px 8px; border-radius:4px; margin-left:8px; font-weight:bold;'>{skor_str} (skala 0–1)</span></div>")
    
    # Interpretasi
    html.append("<div class='n-section'>Interpretasi</div>")
    html.append(f"<div class='n-text'>Berdasarkan hasil analisis terhadap tujuh indikator kesejahteraan, Kabupaten/Kota {daerah_name} termasuk dalam Klaster {tipologi} dengan skor kesejahteraan {skor_str}.</div>")
    cluster_desc = CLUSTER_DESCRIPTIONS.get(klaster, "aktivitas ekonomi relatif berkembang, didukung oleh kualitas hidup dan infrastruktur yang cukup baik")
    html.append(f"<div class='n-text'>Klaster ini menggambarkan wilayah yang memiliki {cluster_desc}. Meskipun demikian, beberapa indikator masih menunjukkan adanya aspek yang perlu mendapat perhatian untuk meningkatkan kesejahteraan masyarakat secara berkelanjutan.</div>")
    
    # Karakteristik Klaster
    html.append("<div class='n-section'>Karakteristik Klaster</div>")
    html.append(f"<div class='n-text'>Wilayah dalam Klaster {tipologi} umumnya memiliki karakteristik:</div>")
    desc_points = [x.strip() for x in cluster_desc.split(',')]
    html.append("<div class='n-text'>")
    for dp in desc_points:
        if dp: html.append(f"<div>• {dp.capitalize()}.</div>")
    html.append("<div>• Masih terdapat indikator tertentu yang memerlukan peningkatan agar pembangunan lebih merata.</div>")
    html.append("</div>")
    
    # Faktor yang Paling Berpengaruh
    html.append("<div class='n-section'>Faktor yang Paling Berpengaruh</div>")
    html.append(f"<div class='n-text'>Tiga indikator yang paling berkontribusi terhadap klasifikasi {daerah_name} adalah:</div>")
    html.append("<table class='n-table'><tr><th>Indikator</th><th>Bobot</th><th>Kondisi</th></tr>")
    
    for i, (feat, z, weight) in enumerate(top_features):
        label = FEATURE_LABELS.get(feat, feat)
        val = feature_values[feat]
        cen = centroid_values[feat]
        interp = interpret_fitur(feat, val, cen, z)
        html.append(f"<tr><td>{label}</td><td>{weight*100:.0f}%</td><td>{interp.capitalize()}.</td></tr>")
    html.append("</table>")
    
    # Interpretasi Indikator
    html.append("<div class='n-section'>Interpretasi Indikator</div>")
    for feat, z, weight in top_features:
        label = FEATURE_LABELS.get(feat, feat)
        val = feature_values[feat]
        cen = centroid_values[feat]
        interp = interpret_fitur(feat, val, cen, z)
        
        satuan = ""
        if feat in ['Persentase_Penduduk_Miskin', 'Sanitasi_Layak', 'TPT']: satuan = "%"
        elif feat in ['UHH', 'Rata_rata_Lama_Sekolah']: satuan = "tahun"
        elif feat == 'Pengeluaran_per_Kapita': satuan = "rupiah/tahun"
        elif feat == 'PDRB_Konstan': satuan = "rupiah"
        
        val_str = format_value(val, feat)
        
        html.append(f"<div class='n-text' style='font-weight:bold; color:#1C1714; margin-top:12px;'>{label}</div>")
        html.append(f"<div class='n-text'>Nilai: {val_str}</div>")
        html.append(f"<div class='n-text'>{interp.capitalize()}. Nilai ini menjadi salah satu faktor penentu dalam proses klasifikasi klaster wilayah ini.</div>")
    
    # Kesimpulan
    html.append("<div class='n-section'>Kesimpulan</div>")
    html.append(f"<div class='n-text'>Secara keseluruhan, Kabupaten/Kota {daerah_name} diklasifikasikan ke dalam Klaster {tipologi} dengan skor kesejahteraan {skor_str}.</div>")
    
    # find weakest feature
    weakest_feat = ""
    for feat in ['Persentase_Penduduk_Miskin', 'TPT']:
        if feat in [f[0] for f in top_features] and z_scores[feat] > 0.5:
            weakest_feat = FEATURE_LABELS[feat]
            break
    if not weakest_feat:
        for feat in ['Sanitasi_Layak', 'UHH', 'Rata_rata_Lama_Sekolah', 'Pengeluaran_per_Kapita', 'PDRB_Konstan']:
            if feat in [f[0] for f in top_features] and z_scores[feat] < -0.5:
                weakest_feat = FEATURE_LABELS[feat]
                break
    
    if not weakest_feat:
        weakest_feat = "pemerataan pembangunan"
        
    html.append(f"<div class='n-text'>Hasil ini menunjukkan bahwa wilayah ini memiliki fondasi ekonomi dan pembangunan yang cukup baik, namun masih menghadapi tantangan terutama pada indikator {weakest_feat}. Peningkatan kualitas kesehatan, pengurangan kemiskinan, serta penguatan pendidikan dan pembangunan ekonomi lokal berpotensi meningkatkan tingkat kesejahteraan wilayah.</div>")
    
    html.append("</div>")
    
    return '\n'.join(html)


def generate_radar_data(feature_values, centroid_values, domain_max, mapped_features,
                        positive_features, negative_features):
    """Generate data untuk radar chart (nilai normalisasi 0-1)."""
    daerah_norm = []
    centroid_norm = []
    for feat in mapped_features:
        max_val = domain_max[feat]
        if feat in negative_features:
            d_norm = max(0, min(1, 1 - (feature_values[feat] / max_val)))
            c_norm = max(0, min(1, 1 - (centroid_values[feat] / max_val)))
        else:
            d_norm = max(0, min(1, feature_values[feat] / max_val))
            c_norm = max(0, min(1, centroid_values[feat] / max_val))
        daerah_norm.append(d_norm)
        centroid_norm.append(c_norm)
    return daerah_norm, centroid_norm
