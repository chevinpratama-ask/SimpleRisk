import pdfplumber
import re

def data_pdf_reader(pdf_path):
    result = {}
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    # Field yang ingin diambil
    fields = [
        "Kantor Cabang",
        "Status Permohonan",
        "Nomor Registrasi Sistem",
        "COB",
        "Nilai Penjaminan",
    ]

    # Split isi PDF menjadi baris-baris
    lines = full_text.splitlines()

    for field in fields:
        value = None
        for idx, line in enumerate(lines):
            if field.lower() in line.lower():
                # Ambil teks setelah titik dua (:)
                match = re.search(rf"{re.escape(field)}\s*:\s*(.*)", line, re.IGNORECASE)
                if match:
                    value_candidate = match.group(1).strip()
                else:
                    # Jika tidak ada setelah titik dua, ambil dari baris berikutnya
                    value_candidate = lines[idx + 1].strip() if idx + 1 < len(lines) else ""

                # ✂️ KHUSUS: Potong jika mengandung "Status Permohonan"
                if field == "Kantor Cabang" and "status permohonan" in value_candidate.lower():
                    value_candidate = re.split(r"(?i)status permohonan", value_candidate)[0].strip()
                    print(f"✂️ Potong 'Kantor Cabang' sebelum 'Status Permohonan' → '{value_candidate}'")

                # Kosongkan jika nilainya "-" atau kosong
                value = None if value_candidate == "-" or not value_candidate else value_candidate
                break

        result[field] = value
        print(f"🔍 Field '{field}' -> {value}")

    return result
