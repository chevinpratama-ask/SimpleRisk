import pyodbc

def get_connection():
    return pyodbc.connect(
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=localhost;"
        "Database=Dashboard_Automation_DB;"
        "Trusted_Connection=yes;"
    )

try:
    conn = get_connection()
    cursor = conn.cursor()

    # Cek koneksi
    print("✅ Koneksi berhasil ke database: Dashboard_Automation_DB")

    # Cek apakah tabel test_result ada
    cursor.execute("""
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = 'test_result'
    """)
    if cursor.fetchone()[0] == 0:
        print("❌ Tabel 'test_result' tidak ditemukan.")
    else:
        print("✅ Tabel 'test_result' ditemukan.")

        # Ambil 10 data terakhir
        cursor.execute("""
            SELECT TOP 10 * 
            FROM test_result 
            ORDER BY execution_time DESC
        """)
        rows = cursor.fetchall()

        print("\n📄 10 Data terakhir di test_result:")
        if rows:
            for row in rows:
                print(row)
        else:
            print("📭 Tidak ada data di tabel.")
    
    conn.close()

except Exception as e:
    print("❌ Gagal koneksi atau query:", e)
