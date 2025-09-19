import os
import time
import datetime
import pytest
import traceback
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from NonCore_SimpleRisk.Automation_Report.pdf_generator import *
from NonCore_SimpleRisk.Automation_DataAccess.db_writer import save_test_result_auto
from NonCore_SimpleRisk.Common.TestData import testcase_data

data = testcase_data["SimpleRisk_FAD1_CustomsBond"]
testcase_id = data["testcase_id"]
testcase_name = data["testcase_name"]
module_name = data["module_name"]
actual_result = data["actual_result"]
expected_result = data["expected_result"]
VERIFY_RECT = data["VERIFY_RECT"]


# ========== Konfigurasi Test Case ========== #
@pytest.fixture
def driver():
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": os.path.abspath(DOWNLOAD_DIR),
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True,
        "safebrowsing.enabled": True,
        "safebrowsing.disable_download_protection": True,
        "download.directory_upgrade": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-features=InsecureDownloadWarnings")
    chrome_options.add_argument(
        "--unsafely-treat-insecure-origin-as-secure=http://10.100.20.53:8084/")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.set_page_load_timeout(30)
    yield driver
    driver.quit()


# ========== Test Case 01 ========== #
def test_TC_03(driver):
    test_steps_rendered = []
    screenshot_rendered = []
    username = "1939"
    password = "@Askrindo123"
    target_url = "http://10.100.20.53:8084/"
    currency = "IDR"
    kurs = "10000"
    nilaipenjaminan = "200000000"
    execution_time = datetime.datetime.now().strftime("%Y-%m-%d %H%M%S")
    summary_data_pdf = {}
    status = "Passed"       # default status
    log_error = None
    test_steps = [
        "[Test_Step_1]: Input username dan password yang benar Input username dan password yang benarInput username dan password yang benar",
        "[Test_Step_2]: Klik tombol login",
        "[Test_Step_3]: Input field pada Informasi Umum",
        "[Test_Step_4]: Input field pada Informasi Principal pada Pilih Debitur",
        "[Test_Step_5]: Lanjutkan Input field pada Informasi Principal",
        "[Test_Step_6]: Input field pada Informasi Proyek",
        "[Test_Step_7]: Input field pada Informasi Lainnya",
        "[Test_Step_8]: Input field pada Hasil Pengecekan",
        "[Test_Step_9]: Input field pada Disclaimer",
        "[Test_Step_10]: Input field pada Pengusul",
        "[Test_Step_11]: Validasi Checkbox Dokumen Sesuai",
        "[Test_Step_12]: Simpan",
        "[Test_Step_13]: Cek data PDF",
    ]
    video_name = f"{testcase_id}_{testcase_name}_{execution_time}.avi"
    stop_recording = start_recording(video_name)
    try:
        driver.get(target_url)
        wait = WebDriverWait(driver, 20)
        driver.delete_all_cookies()
        time.sleep(2)
        test_steps_rendered.append(test_steps[0])
        input_email = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//input[@id='login-email']")))
        input_password = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//input[@placeholder='Masukan Password']")))
        input_email.send_keys(username)
        input_password.send_keys(password)
        elements = [input_email, input_password]
        path = save_screenshot(driver, elements=elements, base_name="step_1",
                               testcase_id=testcase_id, testcase_name=testcase_name, highlight=True)
        screenshot_rendered.append(path)

        # Tunggu halaman berhasil login
        test_steps_rendered.append(test_steps[1])
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space()='Sign in']"))).click()
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//h2[normalize-space()='SimpleRisk']")))
        screenshot_rendered.append(save_screenshot(
            driver, base_name="step_2", testcase_id=testcase_id, testcase_name=testcase_name, highlight=False))

        # Informasi Umum
        test_steps_rendered.append(test_steps[2])
        select_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//select[@id='sumber_bisnis']")))
        Select(select_elem).select_by_visible_text("Direct")
        select_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//select[@id='cob']")))
        Select(select_elem).select_by_visible_text("Customs Bond")

        if currency in ["USD", "EUR", "SGD", "YEN", "AUD", "GBP"]:
            select_elem = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//select[@id='currency']")))
            Select(select_elem).select_by_visible_text(currency)
            wait.until(EC.visibility_of_element_located(
                (By.NAME, "tanggal_kurs"))).send_keys("17/07/2025")  # Sesuaikan dengan format tanggal dd/mm/yyyy atau mm//dd/yyyy yang diharapkan
            wait.until(EC.visibility_of_element_located(
                (By.NAME, "kurs"))).send_keys(kurs)
            wait.until(EC.visibility_of_element_located(
                (By.NAME, "nilaiPenjaminan"))).send_keys(nilaipenjaminan)
        else:
            select_elem = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//select[@id='currency']")))
            Select(select_elem).select_by_visible_text(currency)
            wait.until(EC.visibility_of_element_located(
                (By.NAME, "nilaiPenjaminan"))).send_keys(nilaipenjaminan)

        select_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//select[@id='jenis_permohonan']")))
        Select(select_elem).select_by_visible_text("Permohonan Baru")
        select_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//select[@id='jenis_penjaminan']")))
        Select(select_elem).select_by_visible_text("KABER/EPTE")
        wait.until(EC.visibility_of_element_located(
            (By.NAME, "tanggal_awal"))).send_keys("07/17/2025")  # Sesuaikan dengan format tanggal dd/mm/yyyy atau mm//dd/yyyy yang diharapkan
        wait.until(EC.visibility_of_element_located(
            (By.NAME, "tanggal_akhir"))).send_keys("12/30/2025")  # Sesuaikan dengan format tanggal dd/mm/yyyy atau mm//dd/yyyy yang diharapkan
        wait.until(EC.visibility_of_element_located(
            (By.NAME, "tanggal_permohonan"))).send_keys("07/17/2025")  # Sesuaikan dengan format tanggal dd/mm/yyyy atau mm//dd/yyyy yang diharapkan
        wait.until(EC.visibility_of_element_located(
            (By.NAME, "nomor_surat_permohonan"))).send_keys("NSP/ASK/09088")
        wait.until(EC.visibility_of_element_located(
            (By.NAME, "tanggal_penerimaan_dokumen"))).send_keys("07/18/2025")  # Sesuaikan dengan format tanggal dd/mm/yyyy atau mm//dd/yyyy yang diharapkan
        screenshot_rendered.append(save_screenshot(
            driver, base_name="step_3", testcase_id=testcase_id, testcase_name=testcase_name, highlight=False))

        # Informasi Principal
        test_steps_rendered.append(test_steps[3])
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "/html/body/app-root/vertical-layout/div/content/div/app-form/form/div[2]/div[2]/div/div[1]/div/div[2]/div/div/div/button"))).click()
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "/html/body/ngb-modal-window/div/div/div[2]/form/div/div/div/div[2]/div/input"))).send_keys("Tunas Jaya")
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "/html/body/ngb-modal-window/div/div/div[2]/form/div/div/div/div[2]/div/div/button"))).click()
        wait.until(lambda driver: len(driver.find_elements(
            By.XPATH, "//datatable-body-row")) > 0)
        screenshot_rendered.append(save_screenshot(
            driver, base_name="step_4", testcase_id=testcase_id, testcase_name=testcase_name, highlight=False))

        test_steps_rendered.append(test_steps[4])
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "/html[1]/body[1]/ngb-modal-window[1]/div[1]/div[1]/div[2]/section[1]/ngx-datatable[1]/div[1]/datatable-body[1]/datatable-selection[1]/datatable-scroller[1]/datatable-row-wrapper[1]/datatable-body-row[1]/div[2]/datatable-body-cell[6]/div[1]/a[1]/*[name()='svg'][1]"))).click()
        select_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//select[@id='provinsi']")))
        Select(select_elem).select_by_visible_text("Kepulauan Bangka Belitung")
        select_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//select[@id='kota']")))
        time.sleep(1)
        Select(select_elem).select_by_visible_text("Kota Pangkal Pinang")
        wait.until(EC.visibility_of_element_located(
            (By.NAME, "pic"))).send_keys("Annisa Rizka Aulia")
        wait.until(EC.visibility_of_element_located(
            (By.NAME, "telp"))).send_keys("8785683445")
        select_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//select[@id='nsa']")))
        Select(select_elem).select_by_visible_text("Nasabah Baru")
        select_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//select[@id='bentuk_principal']")))
        screenshot_rendered.append(save_screenshot(
            driver, base_name="step_5", testcase_id=testcase_id, testcase_name=testcase_name, highlight=False))

        # Informasi Proyek
        test_steps_rendered.append(test_steps[5])
        wait.until(EC.visibility_of_element_located(
            (By.NAME, "nama_obligee"))).send_keys("Arlina")
        select_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//select[@id='bentuk_obligee']")))
        Select(select_elem).select_by_visible_text("Pemerintahan")
        select_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//select[@id='lokasi_obligee_provinsi']")))
        Select(select_elem).select_by_visible_text("Kepulauan Bangka Belitung")
        time.sleep(1)
        select_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//select[@id='lokasi_obligee_kota']")))
        Select(select_elem).select_by_visible_text("Kota Pangkal Pinang")
        screenshot_rendered.append(save_screenshot(
            driver, base_name="step_6", testcase_id=testcase_id, testcase_name=testcase_name, highlight=False))

        # Informasi Lainnya
        test_steps_rendered.append(test_steps[6])
        wait.until(EC.visibility_of_element_located(
            (By.NAME, "nomor_underlying"))).send_keys("NU/ASK/98878")
        wait.until(EC.visibility_of_element_located(
            (By.NAME, "tanggal_underlying"))).send_keys("07/17/2025")  # Sesuaikan dengan format tanggal dd/mm/yyyy atau mm//dd/yyyy yang diharapkan

        wait.until(EC.visibility_of_element_located(
            (By.NAME, "sekp"))).send_keys("1")
        wait.until(EC.visibility_of_element_located(
            (By.NAME, "tanggal_sekp"))).send_keys("07/17/2025")  # Sesuaikan dengan format tanggal dd/mm/yyyy atau mm//dd/yyyy yang diharapkan

        wait.until(EC.visibility_of_element_located(
            (By.NAME, "pib"))).send_keys("1")
        wait.until(EC.visibility_of_element_located(
            (By.NAME, "tanggal_pib"))).send_keys("07/17/2025")  # Sesuaikan dengan format tanggal dd/mm/yyyy atau mm//dd/yyyy yang diharapkan
        screenshot_rendered.append(save_screenshot(
            driver, base_name="step_7", testcase_id=testcase_id, testcase_name=testcase_name, highlight=False))

        # Hasil Pengecekan
        test_steps_rendered.append(test_steps[7])
        select_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//select[@id='nasabah_blacklist']")))
        time.sleep(1)
        Select(select_elem).select_by_visible_text(
            "Tidak (Bukan Nasabah Blacklist)")
        select_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//select[@id='tarif_rate_premi_sesuai']")))
        time.sleep(1)
        Select(select_elem).select_by_visible_text("Ya")
        wait.until(EC.visibility_of_element_located(
            (By.NAME, "besaran_cash_collateral"))).send_keys("10")
        screenshot_rendered.append(save_screenshot(
            driver, base_name="step_8", testcase_id=testcase_id, testcase_name=testcase_name, highlight=False))

        # Disclaimer
        test_steps_rendered.append(test_steps[8])
        select_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//select[@id='menggunakan_hukum_indonesia']")))
        time.sleep(1)
        Select(select_elem).select_by_visible_text("Ya")
        select_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//select[@id='isi_wording_sesuai_sop']")))
        time.sleep(1)
        Select(select_elem).select_by_visible_text("Ya")
        select_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//select[@id='spkmgr_sesuai_sop']")))
        time.sleep(1)
        Select(select_elem).select_by_visible_text("Ya")
        screenshot_rendered.append(save_screenshot(
            driver, base_name="step_9", testcase_id=testcase_id, testcase_name=testcase_name, highlight=False))

        # Pengusul
        test_steps_rendered.append(test_steps[9])
        wait.until(EC.visibility_of_element_located(
            (By.NAME, "nama_admin_polis"))).send_keys("Chevin Rifan P")
        wait.until(EC.visibility_of_element_located(
            (By.NAME, "nama_pemutus"))).send_keys("Cynthia")
        wait.until(EC.visibility_of_element_located(
            (By.NAME, "nama_fungsional_pemasaran"))).send_keys("Abdurrahman")
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//button[normalize-space()='Preview']"))).click()
        screenshot_rendered.append(save_screenshot(
            driver, base_name="step_10", testcase_id=testcase_id, testcase_name=testcase_name, highlight=False))

        # Checkbox Validasi Dokumen Sesuai
        test_steps_rendered.append(test_steps[10])
        checkbox = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='validasi_dokumen_sesuai']")))
        if not checkbox.is_selected():
            checkbox.click()
        screenshot_rendered.append(save_screenshot(
            driver, base_name="step_11", testcase_id=testcase_id, testcase_name=testcase_name, highlight=False))

        # Klik tombol Accept dan Simpan
        test_steps_rendered.append(test_steps[11])
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//button[normalize-space()='Accept']"))).click()
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//button[normalize-space()='Simpan']"))).click()
        screenshot_rendered.append(save_screenshot(
            driver, base_name="step_12", testcase_id=testcase_id, testcase_name=testcase_name, highlight=False))
        test_steps_rendered.append(test_steps[12])
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//button[normalize-space()='Ya']"))).click()
        time.sleep(3)

        # Cek data PDF
        highlighted_pdf_path, screenshot_paths = highlight_latest_pdf(
            download_dir=DOWNLOAD_DIR,
            highlight_texts=TEXT_TO_VERIFY,
            verify_rect=VERIFY_RECT,
            timeout=30,
            debug=True
        )

        # ✅ Simpan 2 gambar untuk 1 step
        screenshot_rendered.append(screenshot_paths)
        print("✅ PDF terakhir berhasil di-highlight:", highlighted_pdf_path)
        data = data_pdf_reader(highlighted_pdf_path)
        print("📄 Data dari PDF:", data)

        summary_data_pdf["Kantor Cabang"] = data.get("Kantor Cabang")
        summary_data_pdf["Nomor Registrasi Sistem"] = data.get(
            "Nomor Registrasi Sistem")
        summary_data_pdf["COB"] = data.get("COB")
        summary_data_pdf["Nilai Penjaminan"] = data.get("Nilai Penjaminan")

        # Generate report berhasil
        generate_pdf_report(
            status=status,
            testcase_id=testcase_id,
            testcase_name=testcase_name,
            tester=tester_name,
            screenshot_paths=screenshot_rendered,
            actual_result=actual_result,
            expected_result=expected_result,
            test_steps_rendered=test_steps_rendered,
            screenshot_rendered=screenshot_rendered,
            summary_data_pdf=summary_data_pdf
        )
    except Exception as e:
        # ===== Tangani error test =====
        status = "Not Passed"
        tb = traceback.extract_tb(sys.exc_info()[2])[0]
        line_number = tb.lineno
        error_type = type(e).__name__
        error_detail = str(e).strip() or "Tidak ada detail error"
        error_description = (
            "Gagal menemukan atau menunggu kondisi elemen dalam batas waktu tertentu."
            if error_type == "TimeoutException" else error_detail
        )
        log_error = f"{error_type} | Baris: {line_number} | Detail: {error_description}"
        log_error = log_error[:500]  # pastikan tidak melebihi panjang kolom DB

        # Ambil screenshot gagal
        screenshot_path_fail = save_screenshot(
            driver,
            base_name="screenshot_gagal",
            testcase_id=testcase_id,
            testcase_name=testcase_name
        )

        # Generate PDF report gagal
        generate_pdf_report(
            status=status,
            testcase_id=testcase_id,
            testcase_name=testcase_name,
            tester=tester_name,
            test_steps_rendered=test_steps_rendered,
            screenshot_rendered=screenshot_rendered,
            screenshot_paths=screenshot_rendered + [screenshot_path_fail],
            actual_result=log_error,
            expected_result=expected_result,
            failed_step_index=len(test_steps_rendered) - 1,
            summary_data_pdf=summary_data_pdf
        )
    finally:
        driver.quit()
        stop_recording()
        save_video(video_name)
    # ===== Simpan hasil ke DB =====
    try:
        save_test_result_auto({
            "project_code": project_code,
            "project_name": project_name,
            "project_type": project_type,
            "core_noncore": core_noncore,
            "tester_name": tester_name,
            "module_name": module_name,
            "testcase_id": testcase_id,
            "testcase_name": testcase_name,
            "jenis_test": jenis_test,
            "platform": platform,
            "browser": browser,
            "status": status,
            "log_error": log_error,
            "execution_time": execution_time
        })
        print(f"[{status}] {testcase_id} - {testcase_name} berhasil disimpan ke DB")
    except Exception as e:
        print(f"[Failed] Gagal simpan ke DB: {e}")
    # ===== Paksa pytest menangkap jika Not Passed =====
    if status == "Not Passed":
        raise AssertionError(log_error)
