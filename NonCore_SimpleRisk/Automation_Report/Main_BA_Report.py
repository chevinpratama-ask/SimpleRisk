import os
from PyPDF2 import PdfMerger, PdfReader
from fpdf import FPDF
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from NonCore_SimpleRisk.Common.TestData import testcase_data


logo_path = "logo_askrindo.png"


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
        self.rect(x_position, y_position, box_width,
                  box_height)       # Membuat kotak outline
        self.set_xy(x_position, y_position)
        self.cell(box_width, box_height, align='C', fill=True)


# ======== File Setup =========
file1 = os.path.join("TC01_Output_FAD1_Surety_Bond_SimpleRisk", "Laporan_Passed",
                     "Laporan_Passed_Output_FAD1_Surety_Bond_SimpleRisk_20250919_152855.pdf")  # Ganti dengan path file yang benar
file2 = os.path.join("TC02_Output_FAD1_Kontra_Bank_Garansi_SimpleRisk", "Laporan_Passed",
                     "Laporan_Passed_Output_FAD1_Kontra_Bank_Garansi_SimpleRisk_20250919_134317.pdf")
file3 = os.path.join("TC03_Output_FAD1_Customs_Bond_SimpleRisk", "Laporan_Passed",
                     "Laporan_Passed_Output_FAD1_Customs_Bond_SimpleRisk_20250919_134325.pdf")
output_file = "Laporan_Gabungan_Final.pdf"
# Validasi file
for file_path in [file1, file2, file3]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File tidak ditemukan: {file_path}")
# ======== Hitung Halaman dan Siapkan TOC =========
reader1 = PdfReader(file1)
reader2 = PdfReader(file2)
reader3 = PdfReader(file3)
total_pages_file1 = len(reader1.pages)
total_pages_file2 = len(reader2.pages)
total_pages_file3 = len(reader3.pages)
# Halaman 1: Cover, Halaman 2: Revisi, Halaman 3: TOC
start_page_file1 = 4  # TC-01 mulai dari halaman ke-4
start_page_file2 = start_page_file1 + \
    (total_pages_file1 - 2)  # setelah cover+revisi+TOC
# ======== Generate TOC PDF =========
toc = PDFWithFooter()
toc.add_page()
if os.path.exists(logo_path):
    toc.image(logo_path, x=20, y=16, w=45)
else:
    print("Logo tidak ditemukan")
toc.set_font("Arial", 'B', 15)
toc.set_xy(20, 45)
toc.cell(170, 12, "Daftar Isi", ln=True, align='L')
toc.set_font("Arial", size=12)
toc.ln(2)


# Fungsi bantuan untuk garis titik otomatis
def add_toc_entry(pdf, tc_id, title, page_number):
    pdf.set_x(20)

    # Tentukan teks kiri
    if tc_id:
        left_text = f"{tc_id}"
        subtitle = title
    else:
        left_text = title
        subtitle = ""

    right_text = str(page_number)

    # Lebar total baris
    max_width = 170
    right_width = pdf.get_string_width(right_text) + 4  # space untuk nomor
    left_width = max_width - right_width

    # Hitung titik-titik
    dots_width = pdf.get_string_width(".")
    dots_count = int(
        (left_width - pdf.get_string_width(left_text)) / dots_width)
    dots = "." * max(2, dots_count)

    # Cetak kiri
    pdf.set_font("Arial", "", 12)
    pdf.cell(left_width, 8, f"{left_text} {dots}", ln=0)

    # Cetak kanan (angka halaman rata kanan)
    pdf.cell(right_width, 8, right_text, ln=1, align="R")

    # Subjudul
    if subtitle and tc_id:
        pdf.set_x(25)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 6, subtitle, ln=True)

    pdf.set_font("Arial", "", 12)


# Tambahkan isi TOC
add_toc_entry(toc, "", "Daftar Revisi", 2)
add_toc_entry(toc, "", "Daftar Isi", 3)
add_toc_entry(toc, "", "Dokumen Testing", 4)
add_toc_entry(
    toc,
    testcase_data["SimpleRisk_FAD1_SuretyBond"]["testcase_id_SB"],
    testcase_data["SimpleRisk_FAD1_SuretyBond"]["testcase_name_SB"],
    start_page_file1
)

add_toc_entry(
    toc,
    testcase_data["SimpleRisk_FAD1_KontraBankGaransi"]["testcase_id_CB"],
    testcase_data["SimpleRisk_FAD1_KontraBankGaransi"]["testcase_name_CB"],
    start_page_file2
)

add_toc_entry(
    toc,
    testcase_data["SimpleRisk_FAD1_CustomsBond"]["testcase_id_SB"],
    testcase_data["SimpleRisk_FAD1_CustomsBond"]["testcase_name_SB"],
    start_page_file2 + total_pages_file2  # supaya lanjut setelah file2
)


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

# Kontra Bank Garansi
# Tambahkan isi file2 mulai dari halaman ke-2
merger.append(file2, pages=(2, len(reader2.pages)))

# Customs Bond
# Tambahkan isi file3 mulai dari halaman ke-2
merger.append(file3, pages=(2, len(reader3.pages)))

# merger.append(file2)
# Customs Bond
# Simpan hasil akhir
merger.write(output_file)
merger.close()
os.remove(toc_file)
print(
    f"Laporan digabung dengan TOC disisipkan di halaman ke-3:\n{output_file}")
