from fpdf import FPDF
from PyPDF2 import PdfMerger, PdfReader
import os
from fpdf import FPDF
from SimpleRisk_FAD1_SuretyBond import testcase_id_SB, testcase_name_SB
from SimpleRisk_FAD1_KontraBankGaransi import testcase_id_CB, testcase_name_CB


# ======== PDF Class with Footer =========
class PDFWithFooter(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", size=8)
        self.set_fill_color(0, 102, 204)
        self.set_text_color(255, 255, 255)

        box_width = 8
        box_height = 8
        page_number_text = f"{self.page_no()}"

        x_position = self.w - self.r_margin - box_width
        y_position = self.get_y()

        self.rect(x_position, y_position, box_width, box_height)       # Membuat kotak outline
        self.set_xy(x_position, y_position)
        self.cell(box_width, box_height, align='C', fill=True)


# ======== File Setup =========
file1 = os.path.join("TC1", "Laporan Passed", "Laporan_Passed_SuretyBond_20250730_161641.pdf")
file2 = os.path.join("TC1", "Laporan Passed", "Laporan_Passed_KontraBankGaransi_20250730_162242.pdf")

output_file = "Laporan_Gabungan_Final.pdf"

# Validasi file
for file_path in [file1, file2]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File tidak ditemukan: {file_path}")

# ======== Hitung Halaman dan Siapkan TOC =========
reader1 = PdfReader(file1)
reader2 = PdfReader(file2)

total_pages_file1 = len(reader1.pages)
total_pages_file2 = len(reader2.pages)


# Halaman 1: Cover, Halaman 2: Revisi, Halaman 3: TOC
start_page_file1 = 4  # TC-01 mulai dari halaman ke-4
start_page_file2 = start_page_file1 + (total_pages_file1 - 2)  # setelah cover+revisi+TOC

# ======== Generate TOC PDF =========
toc = PDFWithFooter()
toc.add_page()
toc.set_font("Arial", 'B', 16)
toc.set_xy(20, 20)
toc.cell(0, 10, "DAFTAR ISI", ln=True)

toc.set_font("Arial", size=12)
toc.ln(5)

# Fungsi bantuan untuk garis titik otomatis
def add_toc_entry(pdf, tc_id, title, page_number):
    pdf.set_x(20)

    if tc_id:  # Jika ada TC-ID (misalnya: "TC.011")
        left_text = f"{tc_id}"
        subtitle = title
    else:  # Jika tidak ada TC-ID (misalnya: "Daftar Revisi")
        left_text = f"{title}"
        subtitle = ""

    right_text = str(page_number)
    max_width = 170  # Lebar maksimum yang diperbolehkan
    dot_width = pdf.get_string_width(".")
    text_width = pdf.get_string_width(left_text + right_text)
    dots = "." * int((max_width - text_width) / dot_width)

    # Baris utama
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"{left_text}{dots}{right_text}", ln=True)

    # Subjudul (jika ada subtitle)
    if subtitle and tc_id:
        pdf.set_x(25)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 6, subtitle, ln=True)

    # Reset font (optional)
    pdf.set_font("Arial", "", 12)

# Tambahkan isi TOC
add_toc_entry(toc, "", "Daftar Revisi", 2)
add_toc_entry(toc, "", "Dokumen Testing", 3)
add_toc_entry(toc, testcase_id_SB, testcase_name_SB, start_page_file1)
add_toc_entry(toc, testcase_id_CB, testcase_name_CB, start_page_file2)


# Simpan TOC sementara
toc_file = "TOC_TEMP.pdf"
toc.output(toc_file)

# ======== Gabungkan Semua File =========
merger = PdfMerger()

# Tambahkan halaman 1–2 dari file1 (Cover + Revisi)
merger.append(file1, pages=(0, 2))

# Halaman 3: TOC
merger.append(toc_file)

# Sisanya: Isi Surety Bond
merger.append(file1, pages=(2, total_pages_file1))

# Lalu Kontra Bank Garansi
merger.append(file2)
# Customs Bond


# Simpan hasil akhir
merger.write(output_file)
merger.close()
os.remove(toc_file)

print(f"Laporan digabung dengan TOC disisipkan di halaman ke-3:\n{output_file}")
