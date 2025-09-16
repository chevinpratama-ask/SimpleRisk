import random
from datetime import datetime
import pyodbc


def get_connection():
    return pyodbc.connect(
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=localhost;"
        "Database=Dashboard_Automation_DB;"
        "Trusted_Connection=yes;"
    )


def generate_custom_id(prefix: str, field_name: str, table_name: str, conn) -> str:
    """
    Generate ID format: PREFIX.MMYY-XXXX (XXXX random, unik di table_name untuk field_name)
    """
    now = datetime.now()
    mmyy = now.strftime("%m%y")

    cursor = conn.cursor()
    while True:
        random_number = str(random.randint(0, 9999)).zfill(4)
        candidate_id = f"{prefix}.{mmyy}-{random_number}"

        # Cek apakah ID ini sudah ada
        cursor.execute(
            f"SELECT COUNT(*) FROM {table_name} WHERE {field_name} = ?", (candidate_id,))
        if cursor.fetchone()[0] == 0:
            return candidate_id
        # Kalau duplikat, loop lagi sampai dapat yang unik


def save_test_result_auto(data):
    required_fields = [
        "project_code", "project_name", "project_type", "core_noncore",
        "tester_name", "module_name", "testcase_id", "testcase_name",
        "jenis_test", "platform", "browser", "status"
    ]

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Validasi semua kolom wajib
        for key in required_fields:
            if not data.get(key):
                raise ValueError(
                    f"Field '{key}' wajib diisi dan tidak boleh kosong.")

        # Generate ID unik (cek di DB)
        id_test_result = generate_custom_id(
            "PRJ.QA.TS", "id_test_result", "test_result", conn)
        id_test_result_history = generate_custom_id(
            "PRJ.QA.TSH", "id_test_result_history", "test_result_history", conn)
        execution_time = data.get("execution_time", datetime.now())

        # Mulai transaksi
        conn.autocommit = False

        # Hapus jika sudah ada di test_result
        cursor.execute("""
            DELETE FROM test_result
            WHERE project_code = ? AND testcase_id = ? AND tester_name = ?
        """, (
            data["project_code"], data["testcase_id"], data["tester_name"]
        ))

        # Insert ke tabel utama (test_result)
        cursor.execute("""
            INSERT INTO test_result (
                id_test_result, project_code, project_name, project_type,
                core_noncore, tester_name, module_name, testcase_id,
                testcase_name, jenis_test, platform, browser, status, execution_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_test_result, data["project_code"], data["project_name"], data["project_type"],
            data["core_noncore"], data["tester_name"], data["module_name"],
            data["testcase_id"], data["testcase_name"], data["jenis_test"],
            data["platform"], data["browser"], data["status"], execution_time
        ))

        # Insert ke tabel history (test_result_history)
        cursor.execute("""
            INSERT INTO test_result_history (
                id_test_result_history, original_id, project_code, project_name,
                project_type, core_noncore, tester_name, module_name, testcase_id,
                testcase_name, jenis_test, platform, browser, status, execution_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_test_result_history, id_test_result,
            data["project_code"], data["project_name"], data["project_type"],
            data["core_noncore"], data["tester_name"], data["module_name"],
            data["testcase_id"], data["testcase_name"], data["jenis_test"],
            data["platform"], data["browser"], data["status"], execution_time
        ))

        # Commit transaksi
        conn.commit()
        print(
            f"Data berhasil disimpan.\nID Test Result: {id_test_result}\nID History: {id_test_result_history}")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Gagal menyimpan data ke DB: {e}")
    finally:
        if conn:
            conn.close()
