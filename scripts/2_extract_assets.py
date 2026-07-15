import fitz
import os

pdf_path = r"D:\Kuliyeah\sem 6\Project HKI SENUWU\Manual Book SENUWU.pdf"
assets_dir = r"D:\Kuliyeah\sem 6\Project HKI SENUWU\assets"
os.makedirs(assets_dir, exist_ok=True)

print(f"Mengekstrak aset dari: {pdf_path}")
try:
    doc = fitz.open(pdf_path)
    image_count = 0
    for page_index in range(len(doc)):
        page = doc[page_index]
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            # Abaikan gambar yang terlalu kecil (kemungkinan icon/logo kecil)
            if len(image_bytes) < 5000:
                continue
                
            image_filename = f"img_p{page_index+1}_{img_index+1}.{image_ext}"
            image_filepath = os.path.join(assets_dir, image_filename)
            
            with open(image_filepath, "wb") as f:
                f.write(image_bytes)
            
            print(f"Diekstrak: {image_filename} (Halaman {page_index+1})")
            image_count += 1
            
    print(f"Selesai! Berhasil mengekstrak {image_count} gambar ke folder assets.")
except Exception as e:
    print(f"Terjadi kesalahan saat ekstraksi: {e}")
