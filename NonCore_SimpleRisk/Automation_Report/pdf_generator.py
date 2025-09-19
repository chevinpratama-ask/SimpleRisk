import os
import time
import datetime
import glob
import threading
import pyautogui
import cv2
import numpy as np
import shutil
import fitz  # PyMuPDF
import pdfplumber
import re
from fpdf import FPDF
from PIL import Image, ImageOps
from NonCore_SimpleRisk.Common.TestData import testcase_data
# from NonCore_SimpleRisk.Automation_TestCase.SimpleRisk_FAD1_SuretyBond import testcase_id, testcase_name, expected_result, VERIFY_RECT
# from NonCore_SimpleRisk.Automation_TestCase.SimpleRisk_FAD1_KontraBankGaransi import testcase_id, testcase_name, expected_result, VERIFY_RECT
# from NonCore_SimpleRisk.Automation_TestCase.SimpleRisk_FAD1_CustomsBond import testcase_id, testcase_name, expected_result, VERIFY_RECT


DOWNLOAD_DIR = "Laporan_Downloads"
TEXT_TO_VERIFY = ["Simple Risk"]
screenshot_rendered = []
project_code = "KP001.ASK.QA"
project_name = "Aplikasi Simple Risk"
project_type = "CR"
core_noncore = "noncore"
tester_name = "chevin"
jenis_test = "Positive"
platform = "Windows 11 64 Bit"
browser = "Chrome"


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
        "Nilai Penjaminan"
    ]

    # Split isi PDF menjadi baris-baris
    lines = full_text.splitlines()
    for field in fields:
        value = None
        for idx, line in enumerate(lines):
            if field.lower() in line.lower():
                # Ambil teks setelah titik dua (:)
                match = re.search(
                    rf"{re.escape(field)}\s*:\s*(.*)", line, re.IGNORECASE)
                if match:
                    value_candidate = match.group(1).strip()
                else:
                    # Jika tidak ada setelah titik dua, ambil dari baris berikutnya
                    value_candidate = lines[idx +
                                            1].strip() if idx + 1 < len(lines) else ""
                # ✂️ KHUSUS: Potong jika mengandung "Status Permohonan"
                if field == "Kantor Cabang" and "status permohonan" in value_candidate.lower():
                    value_candidate = re.split(
                        r"(?i)status permohonan", value_candidate)[0].strip()
                    print(
                        f"✂️ Potong 'Kantor Cabang' sebelum 'Status Permohonan' → '{value_candidate}'")
                # Kosongkan jika nilainya "-" atau kosong
                value = None if value_candidate == "-" or not value_candidate else value_candidate
                break
        result[field] = value
        print(f"🔍 Field '{field}' -> {value}")
    return result


# ================== RECORDING ==================
def start_recording(filename="recording.avi", fps=20.0):
    screen_size = pyautogui.size()  # ambil resolusi layar otomatis
    print(f"Resolusi layar terdeteksi: {screen_size}")
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(filename, fourcc, fps, screen_size)
    recording_flag = {"status": True}  # dict biar mutable di thread

    def record_screen():
        while recording_flag["status"]:
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame)
            time.sleep(0.05)  # biar CPU nggak berat
    t = threading.Thread(target=record_screen, daemon=True)
    t.start()

    def stop():
        recording_flag["status"] = False
        t.join(timeout=2)
        out.release()
        cv2.destroyAllWindows()
        print(f"✅ Recording selesai: {filename}")
    return stop


# ==================Simpan Video ============#
def save_video(source_path, dest_folder="Saved_Videos"):
    os.makedirs(dest_folder, exist_ok=True)
    destination_path = os.path.join(dest_folder, os.path.basename(source_path))
    shutil.move(source_path, destination_path)
    print(f"✅ Video disimpan di: {destination_path}")
    return destination_path


# ========== Simpan Screenshoot ========== #
def save_screenshot(
    driver,
    elements=None,
    base_name="screenshot",
    highlight=False,
    testcase_id=None,
    testcase_name=None,
):
    folder = os.path.join(
        f"{testcase_id}_{testcase_name.replace(' ', '_')}", "Screenshoots")
    os.makedirs(folder, exist_ok=True)
    waktu = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_name}_{waktu}.png"
    path = os.path.join(folder, filename)
    original_styles = []

    # ====== Tambahkan highlight jika diminta ======
    if highlight and elements:
        for elem in elements:
            original_style = elem.get_attribute("style")
            original_styles.append(original_style)
            driver.execute_script(
                "arguments[0].setAttribute('style', arguments[1])", elem, "border: 3px solid red;")
        time.sleep(0.2)

    # Screenshot disimpan (sementara)
    driver.save_screenshot(path)

    # Hapus highlight jika ada
    if highlight and elements:
        for elem, style in zip(elements, original_styles):
            driver.execute_script(
                "arguments[0].setAttribute('style', arguments[1])", elem, style)

    # Tambahkan border hitam ke screenshot
    img = Image.open(path)

    # Ganti nama sesuai apakah pakai highlight atau tidak
    suffix = "_highlight" if highlight else "_border"
    bordered_path = f"{os.path.splitext(path)[0]}{suffix}.png"

    bordered_img = ImageOps.expand(img, border=2, fill='black')
    bordered_img.save(bordered_path)

    # Hapus file asli tanpa border
    os.remove(path)

    print(f"Screenshot disimpan di: {bordered_path}")
    return bordered_path

# ===============================AutoCrop==============================#


def get_content_clip(page, margin=(10, 10, 20, 30)):  # Default margin paramter
    blocks = page.get_text("blocks")
    if blocks:
        x0 = min(b[0] for b in blocks)
        y0 = min(b[1] for b in blocks)
        x1 = max(b[2] for b in blocks)
        y1 = max(b[3] for b in blocks)
        clip = fitz.Rect(x0, y0, x1, y1)
    else:
        clip = page.rect

    # unpack margin
    left, top, right, bottom = margin
    clip = fitz.Rect(
        clip.x0 - left,
        clip.y0 - top,
        clip.x1 + right,
        clip.y1 + bottom
    )
    return clip


# =================================Highlight PDF===========================#
def highlight_latest_pdf(download_dir=None,
                         highlight_texts=None,
                         verify_rect=None,
                         timeout=30,
                         zoom=2,
                         margin=10,
                         debug=False):
    """
    Highlight teks hanya jika ditemukan di verify_rect. 
    Jika teks tidak ditemukan di seluruh PDF → raise Exception (FAILED).
    """
    if download_dir is None:
        download_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_dir, exist_ok=True)

    # Cari PDF terbaru
    start_time = time.time()
    pdf_path = None
    while time.time() - start_time < timeout:
        pdf_files = [f for f in glob.glob(os.path.join(download_dir, "*.pdf"))
                     if not f.endswith(".crdownload") and os.path.isfile(f)]
        if pdf_files:
            pdf_path = max(pdf_files, key=os.path.getctime)
            if debug:
                print(f"[Info] File PDF ditemukan: {pdf_path}")
            time.sleep(2)
            break
        time.sleep(0.5)
    if not pdf_path:
        raise FileNotFoundError(
            f"Tidak ada file PDF valid dalam {download_dir}")

    if highlight_texts is None or verify_rect is None:
        raise ValueError("highlight_texts dan verify_rect harus diisi")

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise Exception(f"Gagal membuka PDF: {pdf_path} | {e}")

    screenshot_paths = []
    found_any = False

    # Loop tiap halaman
    for page_number in range(len(doc)):
        page = doc[page_number]
        rect = fitz.Rect(*verify_rect)
        blocks = page.get_text("dict")["blocks"]

        # Loop semua span di halaman
        for b in blocks:
            for line in b.get("lines", []):
                for span in line.get("spans", []):
                    span_text = span["text"].strip()
                    span_rect = fitz.Rect(span["bbox"])
                    # Highlight jika span ada di rect & teks exact match
                    if rect.intersects(span_rect) and span_text in highlight_texts:
                        hl = page.add_highlight_annot(span_rect)
                        hl.set_colors(stroke=(1, 1, 0))
                        hl.update()
                        found_any = True
                        if debug:
                            print(
                                f"[Highlight] Page {page_number+1}, Text: '{span_text}', Rect: {span_rect}")

        # Screenshot auto crop
        clip = get_content_clip(page, margin=(20, 40, 30, 30))
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, clip=clip)
        img_path = os.path.join(
            download_dir, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_page{page_number+1}.png")
        pix.save(img_path)
        screenshot_paths.append(img_path)

    # Simpan PDF baru
    try:
        tmp_path = pdf_path + ".tmp.pdf"
        doc.save(tmp_path)
        doc.close()
        os.replace(tmp_path, pdf_path)
    except Exception as e:
        raise Exception(f"Gagal menyimpan PDF baru: {e}")

    # Status final
    if not found_any:
        raise Exception(
            f"[FAILED] Teks {highlight_texts} tidak ditemukan di rect {verify_rect} di seluruh PDF")
    else:
        if debug:
            print("[PASSED] Semua teks ditemukan di rect yang sesuai.")

    return pdf_path, screenshot_paths


# ========================Hasil Image Render PDF===========================
def safe_add_images(pdf, image_paths, x=20, max_width=170, max_height=200, y_start=35, bottom_margin=15):
    if isinstance(image_paths, str):
        image_paths = [image_paths]
    for path in image_paths:
        if path and os.path.exists(path):
            try:
                with Image.open(path) as img:
                    w, h = img.size
                    ratio = h / w
                    # Hitung dimensi
                    display_width = max_width
                    display_height = display_width * ratio
                    # Batasi tinggi jika perlu
                    if display_height > max_height:
                        display_height = max_height
                        display_width = display_height / ratio
                    # Cek sisa ruang
                    y_now = pdf.get_y()
                    space_remaining = 297 - y_now - bottom_margin  # A4 height
                    if display_height > space_remaining:
                        pdf.add_page()
                        pdf.set_y(y_start)
                    pdf.image(path, x=x, w=display_width, h=display_height)
                    pdf.set_y(pdf.get_y() + 3)
            except Exception as e:
                print(f"[Warning] Gagal tampilkan gambar {path}: {e}")


# ========================PDF Generator===========================
class CustomPDF(FPDF):
    def header(self):
        if self.page_no() > 2:
            self.set_font("Arial", 'B', 10)
            self.set_fill_color(255, 255, 255)
            # Ukuran tabel
            page_margin = 20
            total_width = 210 - 2 * page_margin
            logo_width = 50
            right_width = 30
            center_width = total_width - logo_width - right_width
            cell_height = 7
            top_y = self.get_y()
            logo_x = page_margin
            logo_y = top_y
            logo_cell_width = logo_width
            logo_cell_height = cell_height * 3  # tinggi kolom logo (3 baris)

            # ===== CELL KIRI (Logo) =====
            self.set_xy(logo_x, logo_y)
            self.cell(logo_cell_width, logo_cell_height, "", border=1)

            # ====== TAMBAHKAN LOGO ======
            logo_path = "logo_askrindo.png"
            if os.path.exists(logo_path):
                # Ukuran asli gambar (ambil langsung)
                from PIL import Image
                img = Image.open(logo_path)
                img_w, img_h = img.size
                aspect_ratio = img_h / img_w

                # Hitung ukuran gambar supaya muat & rata tengah
                max_img_width = logo_cell_width - 6
                max_img_height = logo_cell_height - 4
                draw_w = max_img_width
                draw_h = draw_w * aspect_ratio
                if draw_h > max_img_height:
                    draw_h = max_img_height
                    draw_w = draw_h / aspect_ratio
                img_x = logo_x + (logo_cell_width - draw_w) / 2
                img_y = logo_y + (logo_cell_height - draw_h) / 2
                self.image(logo_path, x=img_x, y=img_y, w=draw_w, h=draw_h)

            # ===== TABEL TENGAH (3 baris) =====
            self.set_font("Arial", '', 10)
            self.set_x(logo_x + logo_cell_width)
            self.cell(center_width, cell_height,
                      "ASKRINDO", border=1, ln=2, align='C')
            self.set_x(logo_x + logo_cell_width)
            self.cell(center_width, cell_height,
                      "DOKUMEN HASIL TESTING", border=1, ln=2, align='C')
            self.set_x(logo_x + logo_cell_width)
            self.cell(center_width, cell_height,
                      "UPR Enhancement Portal Usulan RKAP", border=1, ln=0, align='C')

            # ===== CELL KANAN (UAT) =====
            self.set_xy(logo_x + logo_cell_width + center_width, logo_y)
            self.set_font("Arial", '', 10)
            self.cell(right_width, logo_cell_height,
                      "UAT", border=1, align='C')
            # Spasi ke bawah
            self.ln(logo_cell_height + 8)
            # Jangan tampilkan nomor halaman di halaman pertama

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-15)
        self.set_font("Arial", size=8)
        self.set_fill_color(0, 102, 204)
        self.set_text_color(255, 255, 255)
        box_width = 8
        box_height = 8
        page_number_text = f"{self.page_no()}"  # agar halaman kedua jadi "1"
        x_position = self.w - self.r_margin - box_width
        y_position = self.get_y()
        self.rect(x_position, y_position, box_width,
                  box_height)       # Membuat kotak outline
        self.set_xy(x_position, y_position)
        self.cell(box_width, box_height, align='C', fill=True)


def generate_pdf_report(
    test_steps_rendered,
    screenshot_rendered,
    # Project="Aplikasi SimpleRisk",
    testcase_id,
    testcase_name,
    expected_result,
    actual_result=None,
    logo_path="logo_askrindo.png",
    tester="chevin",
    status=None,
    screenshot_paths=None,
    failed_step_index=None,
    summary_data_pdf={},
    tanggal_revisi_1="22/07/2025",
    tanggal_revisi_2="23/07/2025",
    tanggal_revisi_3="24/07/2025",
    versi_1="V.I.I",
    versi_2="V.I.II",
    versi_3="V.I.III",
    keterangan_revisi_1="Initial Doc",
    keterangan_revisi_2="Dokument Hasil Testing SIT Chevin Rifan Pratama Halloha genter",
    keterangan_revisi_3="Final Doc",
    pic_1="Chevin",
    pic_2="Chevin",
    pic_3="Chevin",
):
    # -------Simpan Folder PDF-----------#
    waktu = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_base = f"{testcase_id}_{testcase_name.replace(' ', '_')}"
    if status == "Passed":
        folder = os.path.join(folder_base, "Laporan_Passed")
        nama_file = f"Laporan_Passed_{testcase_name.replace(' ', '_')}_{waktu}.pdf"
    else:
        folder = os.path.join(folder_base, "Laporan_Failed")
        nama_file = f"Laporan_Failed_{testcase_name.replace(' ', '_')}_{waktu}.pdf"

    # Buat folder jika belum ada
    os.makedirs(folder, exist_ok=True)

    # Buat nama file PDF
    pdf_path = os.path.join(folder, nama_file)
    print(f"PDF akan disimpan di: {pdf_path}")
    pdf = CustomPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ===== Halaman 1: Cover =====
    pdf.add_page()
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=20, y=16, w=45)  # Rata kiri 20 mm
    else:
        print("Logo tidak ditemukan")
    pdf.set_font("Arial", 'B', 25)
    pdf.set_xy(20, 60)
    texts = [
        "Laporan Hasil Pengujian SIT",
        "Aplikasi Simple Risk",
        "12/08/2025",
        "V.I.II"
    ]
    for t in texts:
        pdf.set_x(20)
        pdf.cell(170, 12, t, ln=True, align='L')

    # ===== Halaman 2: Daftar revisi =====
    pdf.add_page()
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=20, y=16, w=45)
    else:
        print("Logo tidak ditemukan")
    pdf.set_font("Arial", 'B', 15)
    pdf.set_xy(20, 45)
    pdf.cell(170, 12, "Daftar Revisi", ln=True, align='L')
    summary_data = [
        ["Tanggal", "Versi", "Keterangan Revisi", "PIC"],
        [tanggal_revisi_1, versi_1, keterangan_revisi_1, pic_1],
        [tanggal_revisi_2, versi_2, keterangan_revisi_2, pic_1],
        [tanggal_revisi_3, versi_3, keterangan_revisi_3, pic_1],
    ]
    col_widths = [40, 25, 80, 30]  # Widths: Tanggal, Versi, Keterangan, PIC
    start_x = 20
    line_height = 8
    for i, row in enumerate(summary_data):
        pdf.set_x(start_x)
        if i == 0:
            # header
            pdf.set_fill_color(230, 230, 230)
            pdf.set_font("Arial", 'B', 10)
            for j, cell in enumerate(row):
                pdf.cell(col_widths[j], line_height, str(
                    cell), border=1, fill=True, align='c')
            pdf.ln(line_height)  # hanya sekali pindah baris setelah header
        else:
            pdf.set_font("Arial", '', 9)
            y_start = pdf.get_y()
            x = start_x
        # MultiCell hanya untuk kolom ke-3 (Keterangan Revisi)
            pdf.set_xy(x + col_widths[0] + col_widths[1], y_start)
            multicell_y_before = pdf.get_y()
            pdf.multi_cell(col_widths[2], line_height-3, str(row[2]), border=1)
            multicell_y_after = pdf.get_y()
            height = multicell_y_after - multicell_y_before
        # Cetak kolom Tanggal & Versi
            pdf.set_xy(x, y_start)
            pdf.cell(col_widths[0], height, str(row[0]), border=1)
            pdf.cell(col_widths[1], height, str(row[1]), border=1)
        # Cetak kolom PIC
            pdf.set_xy(x + col_widths[0] +
                       col_widths[1] + col_widths[2], y_start)
            pdf.cell(col_widths[3], height, str(row[3]), border=1)
        # Pindah ke baris berikutnya
            pdf.set_y(y_start + height)

    # ===== Halaman 3: Header, Logo, Ringkasan =====
    pdf.add_page()
    # # Spacer
    pdf.ln(3)
    pdf.set_x(20)
    # # Set font
    pdf.set_font("Arial", size=10)
    summary_data1 = [
        ["TestCaseID", testcase_id],
        ["TestCaseName", testcase_name],
        ["Jenis Test", jenis_test],
        ["Date", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["Tester", tester],
        ["Status", status],
        ["Expected Result", expected_result],
    ]

    # Ukuran dan posisi
    cell_height = 6
    left_col_width = 40
    right_col_width = 130
    x_start = 20
    for key, value in summary_data1:
        y_start = pdf.get_y()
        if key in ["TestCaseName", "Expected Result"]:
            # Hitung tinggi value saja
            def get_text_height(text, width):
                temp = FPDF()
                temp.add_page()
                temp.set_font("Arial", size=10)
                temp.set_xy(0, 0)
                temp.multi_cell(width, cell_height, str(text))
                return temp.get_y()
            value_height = get_text_height(value, right_col_width)
            row_height = max(value_height, cell_height)

            # Draw background & border untuk key
            pdf.set_fill_color(230, 230, 230)
            pdf.rect(x_start, y_start, left_col_width, row_height, 'F')
            pdf.rect(x_start, y_start, left_col_width, row_height)

            # Draw border untuk value
            pdf.rect(x_start + left_col_width, y_start,
                     right_col_width, row_height)

            # Isi key
            pdf.set_xy(x_start, y_start)
            pdf.multi_cell(left_col_width, cell_height, str(key), border=0)

            # Isi value
            pdf.set_xy(x_start + left_col_width, y_start)
            pdf.multi_cell(right_col_width, cell_height, str(value), border=0)
            pdf.set_y(y_start + row_height)
        else:
            pdf.set_x(x_start)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(left_col_width, cell_height,
                     str(key), border=1, fill=True)
            pdf.cell(right_col_width, cell_height, str(value), border=1)
            pdf.ln()
    pdf.ln(5)
    pdf.set_font("Arial", size=11)
    pdf.set_x(20)
    pdf.cell(0, 8, "Data:", ln=True)
    label_width = 45
    colon_width = 4
    value_width = 136

    def print_data_row(label, value):
        pdf.set_x(20)
        pdf.cell(label_width, 6, label, ln=0)
        pdf.cell(colon_width, 6, ":", ln=0)
        pdf.cell(value_width, 6, str(value if value else "-"), ln=1)

    # Pastikan key sama persis dengan yang ada di result
    print_data_row("Kantor Cabang", summary_data_pdf.get("Kantor Cabang"))
    print_data_row("Nomor Registrasi Sistem",
                   summary_data_pdf.get("Nomor Registrasi Sistem"))
    print_data_row("COB", summary_data_pdf.get("COB"))
    print_data_row("Nilai Penjaminan",
                   summary_data_pdf.get("Nilai Penjaminan"))
    pdf.ln(3)

    # ===== Halaman 4: Daftar Revisi =====
    margin_left = 20
    y_start = 35
    line_height = 8
    text_width = 170
    bottom_margin = 15
    for i, step in enumerate(test_steps_rendered):
        # Hitung tinggi teks
        pdf.set_font("Arial", size=11)
        text_lines = pdf.multi_cell(
            text_width, line_height, step, border=0, split_only=True)
        text_height = len(text_lines) * line_height

        # Hitung tinggi semua gambar
        total_image_height = 0
        images = screenshot_paths[i] if i < len(screenshot_paths) else []
        if isinstance(images, str):
            images = [images]
        for path in images:
            if os.path.exists(path):
                with Image.open(path) as img:
                    w, h = img.size
                    ratio = min(170 / w, 200 / h, 1)
                    display_height = h * ratio
                    total_image_height += display_height + 3

        # Cek page break
        y_now = pdf.get_y()
        needed_height = text_height + total_image_height
        available_height = pdf.h - y_now - bottom_margin
        if needed_height > available_height:
            pdf.add_page()
            pdf.set_y(y_start)

        # Tampilkan teks step
        if failed_step_index is not None and i == failed_step_index:
            pdf.set_text_color(255, 0, 0)  # merah
        else:
            pdf.set_text_color(0, 0, 0)
        pdf.set_x(margin_left)
        pdf.multi_cell(text_width, line_height, step)
        pdf.ln(3)

        # Tampilkan gambar
        for path in images:
            if os.path.exists(path):
                with Image.open(path) as img:
                    w, h = img.size
                    ratio = min(170 / w, 200 / h, 1)
                    w_scaled = w * ratio
                    h_scaled = h * ratio
                    y_now = pdf.get_y()
                    if y_now + h_scaled + bottom_margin > pdf.h:
                        pdf.add_page()
                        y_now = y_start
                    pdf.image(path, x=margin_left, y=y_now,
                              w=w_scaled, h=h_scaled)
                    # Update posisi Y setelah gambar, jangan pakai ln()
                    pdf.set_y(y_now + h_scaled + 3)
                    pdf.set_x(margin_left)  # pastikan X tetap margin kiri
    if status != "Passed":
        pdf.set_text_color(255, 0, 0)
        pdf.set_font("Arial", '', 11)
        pdf.ln(1)
        pdf.set_x(20)
        pdf.cell(170, 10, "Log Error / Gagal:", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.set_x(20)
        pdf.multi_cell(170, 6, actual_result)
        pdf.set_text_color(0, 0, 0)
    else:
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", '', 11)
        pdf.ln(1)
        pdf.set_x(20)
        combined_text = f"Actual Result : {actual_result}"
        pdf.multi_cell(170, 6, combined_text)
    # Simpan PDF
    pdf.output(pdf_path)
    print(f"PDF berhasil disimpan ke: {pdf_path}")
    return pdf_path
