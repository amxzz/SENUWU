import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import os
import time
import json
import ssl

def download_arxiv_papers(query, max_results, start_index=0):
    url = f'http://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(query)}&start={start_index}&max_results={max_results}&sortBy=submittedDate&sortOrder=descending'
    print(f"Fetching from: {url}")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    response = urllib.request.urlopen(url, context=ctx)
    data = response.read()
    root = ET.fromstring(data)
    
    papers = []
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    for entry in root.findall('atom:entry', ns):
        title = entry.find('atom:title', ns).text.replace('\n', ' ').strip()
        published = entry.find('atom:published', ns).text
        year = published.split('-')[0]
        if int(year) < 2021: # Fallback to 2021 to ensure enough papers if 2023 is too strict
            continue
            
        authors = [author.find('atom:name', ns).text for author in entry.findall('atom:author', ns)]
        
        pdf_url = None
        for link in entry.findall('atom:link', ns):
            if link.attrib.get('title') == 'pdf':
                pdf_url = link.attrib.get('href')
                break
                
        if pdf_url:
            papers.append({
                'title': title,
                'authors': authors,
                'year': year,
                'pdf_url': pdf_url + ".pdf"
            })
    return papers

queries = ["HDBSCAN", "K-Means anomaly", "Isolation Forest anomaly", "Spatial clustering inequality"]
all_papers = []

print("Mencari referensi dari arXiv API...")
for q in queries:
    papers = download_arxiv_papers(q, 15)
    all_papers.extend(papers)
    time.sleep(3) # Be nice to API

# Deduplicate
unique_papers = {p['title']: p for p in all_papers}
# We need at least 15 papers. Sort by year descending.
final_papers = sorted(list(unique_papers.values()), key=lambda x: x['year'], reverse=True)[:18]

out_dir = r"D:\Kuliyeah\sem 6\Project HKI SENUWU\sumber"
os.makedirs(out_dir, exist_ok=True)

references_metadata = []

for i, p in enumerate(final_papers):
    filename = f"ref_{i+1}_{p['year']}.pdf"
    filepath = os.path.join(out_dir, filename)
    print(f"Mengunduh [{i+1}/{len(final_papers)}]: {p['title'][:50]}... -> {filename}")
    try:
        req = urllib.request.Request(p['pdf_url'], headers={'User-Agent': 'Mozilla/5.0'})
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, context=ctx) as response, open(filepath, 'wb') as out_file:
            out_file.write(response.read())
        
        references_metadata.append({
            'id': f"ref_{i+1}",
            'title': p['title'],
            'authors': p['authors'],
            'year': p['year'],
            'filename': filename
        })
        time.sleep(2)
    except Exception as e:
        print(f"Gagal mengunduh {filename}: {e}")

metadata_path = os.path.join(out_dir, "references.json")
with open(metadata_path, 'w', encoding='utf-8') as f:
    json.dump(references_metadata, f, indent=4)

print(f"Berhasil mengunduh {len(references_metadata)} referensi dan menyimpan metadata di {metadata_path}")
