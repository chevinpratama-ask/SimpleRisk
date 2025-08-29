import fitz  # PyMuPDF

def cari_posisi_teks(pdf_path, keyword):
    doc = fitz.open(pdf_path)

    for page_num, page in enumerate(doc, start=1):
        hasil = page.search_for(keyword)
        for rect in hasil:
            print(f"Teks '{keyword}' ditemukan di halaman {page_num}:")
            print(f"  x0={rect.x0:.2f}, y0={rect.y0:.2f}")
            print(f"  x1={rect.x1:.2f}, y1={rect.y1:.2f}")
            print(f"  Lebar = {rect.width:.2f}, Tinggi = {rect.height:.2f}")
            print("-" * 40)

# Ganti nama file PDF dan kata kunci yang dicari
pdf_file = "FAD1_SuretyBond_SimpleRisk.pdf"
kata_kunci = "Simple Risk"

cari_posisi_teks(pdf_file, kata_kunci)
