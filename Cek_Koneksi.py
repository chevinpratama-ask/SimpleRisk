from Utils.db_writer import get_connection

def cek_koneksi():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Cek nama database aktif
        cursor.execute("SELECT DB_NAME()")
        current_db = cursor.fetchone()[0]
        print("✅ Koneksi berhasil ke database:", current_db)

        # Optional: Cek apakah tabel `test_result` ada
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'test_result'
        """)
        if cursor.fetchone()[0] == 1:
            print("✅ Tabel 'test_result' ditemukan.")
        else:
            print("⚠️  Tabel 'test_result' tidak ditemukan.")

        conn.close()
    except Exception as e:
        print("❌ Gagal koneksi:", e)

if __name__ == "__main__":
    cek_koneksi()
