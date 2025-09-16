import pyodbc
from datetime import datetime
import pytz
import random


# ✅ Fungsi untuk mendapatkan waktu WIB


def get_current_time_wib():
    wib = pytz.timezone("Asia/Jakarta")
    return datetime.now(pytz.utc).astimezone(wib).replace(tzinfo=None)

# ✅ Fungsi koneksi ke SQL Server


def get_connection():
    return pyodbc.connect(
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=localhost;"
        "Database=Dashboard_Automation_DB;"
        "Trusted_Connection=yes;"
    )

# ✅ Generate ID unik (cek ke DB biar tidak duplikat)


def generate_unique_id(prefix: str, execution_time, table_name: str, field_name: str, conn) -> str:
    mm_yy = execution_time.strftime('%m%y')
    cursor = conn.cursor()

    while True:
        rand = str(random.randint(1000, 9999))
        new_id = f"{prefix}{mm_yy}{rand}"

        cursor.execute(
            f"SELECT COUNT(*) FROM {table_name} WHERE {field_name} = ?", (new_id,))
        exists = cursor.fetchone()[0]

        if exists == 0:
            return new_id  # ✅ ID unik ditemukan

# ✅ Fungsi utama untuk menyimpan hasil test
# ================= Simpan Hasil Test =================


def save_test_result_auto(data: dict):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        execution_time = get_current_time_wib()
        id_test_result_history = generate_unique_id(
            "PRJQATRHistory", execution_time, "test_result_history", "id_test_result_history", conn
        )

        # ================= Cek data di test_result =================
        cursor.execute("""
            SELECT id_test_result FROM test_result
            WHERE project_code = ? AND testcase_id = ? AND tester_name = ?
        """, (data["project_code"], data["testcase_id"], data["tester_name"]))
        existing = cursor.fetchone()

        if existing:
            # Update record lama (tanpa log_error)
            id_test_result = existing[0]
            cursor.execute("""
                UPDATE test_result
                SET project_name = ?, project_type = ?, core_noncore = ?, 
                    module_name = ?, testcase_name = ?, jenis_test = ?, 
                    platform = ?, browser = ?, status = ?, execution_time = ?
                WHERE id_test_result = ?
            """, (
                data["project_name"],
                data["project_type"],
                data["core_noncore"],
                data["module_name"],
                data["testcase_name"],
                data["jenis_test"],
                data["platform"],
                data["browser"],
                data["status"],
                execution_time,
                id_test_result
            ))
            print(f"♻️ UPDATE test_result ID {id_test_result} berhasil.")
        else:
            # Insert baru (tanpa log_error)
            id_test_result = generate_unique_id(
                "PRJQATResult", execution_time, "test_result", "id_test_result", conn
            )
            cursor.execute("""
                INSERT INTO test_result (
                    id_test_result, project_code, project_name, project_type,
                    core_noncore, tester_name, module_name, testcase_id,
                    testcase_name, jenis_test, platform, browser,
                    status, execution_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                id_test_result,
                data["project_code"],
                data["project_name"],
                data["project_type"],
                data["core_noncore"],
                data["tester_name"],
                data["module_name"],
                data["testcase_id"],
                data["testcase_name"],
                data["jenis_test"],
                data["platform"],
                data["browser"],
                data["status"],
                execution_time
            ))
            print(f"✅ INSERT ke test_result ID {id_test_result} berhasil.")

        # ================= Simpan riwayat (termasuk log_error) =================
        cursor.execute("""
            INSERT INTO test_result_history (
                id_test_result_history, original_id, project_code, project_name,
                project_type, core_noncore, tester_name, module_name,
                testcase_id, testcase_name, jenis_test, platform, browser,
                status, log_error, execution_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_test_result_history,
            id_test_result,
            data["project_code"],
            data["project_name"],
            data["project_type"],
            data["core_noncore"],
            data["tester_name"],
            data["module_name"],
            data["testcase_id"],
            data["testcase_name"],
            data["jenis_test"],
            data["platform"],
            data["browser"],
            data["status"],
            data.get("log_error"),  # ✅ hanya di history
            execution_time
        ))
        print("📝 INSERT ke test_result_history berhasil.")

        conn.commit()
        print("✅ Semua perubahan berhasil disimpan ke database.")

    except Exception as e:
        print(f"❌ ERROR saat menyimpan ke database: {e}")

    finally:
        if conn:
            conn.close()
            print("🔒 Koneksi database ditutup.")
