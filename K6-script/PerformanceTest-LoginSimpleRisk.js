import http from 'k6/http';
import { check, sleep } from 'k6';

// OPTIONS
export let options = {
  vus: 5,
  duration: '30s',
};

export default function () {
  // 1. LOGIN
  const loginPayload = JSON.stringify({
    username: '1939',             // GANTI DENGAN USER AKTIF
    password: '@Askrindo123',     // GANTI DENGAN PASSWORD VALID
  });

  const loginHeaders = {
    headers: { 'Content-Type': 'application/json' },
  };

  const loginRes = http.post('http://10.100.20.53:8084/url/v1/simplerisk/auth/login', loginPayload, loginHeaders);

  // DEBUG: Tampilkan response login
  console.log("Login Response:", loginRes.body);

  // 2. PARSE TOKEN DENGAN AMAN
  let token = null;
  try {
    const parsedBody = JSON.parse(loginRes.body);
    token = parsedBody?.data?.token; // UBAH SESUAI STRUKTUR RESPON
  } catch (e) {
    console.error("Gagal parse token:", e);
  }

  // 3. CEK LOGIN DAN TOKEN
  check(loginRes, {
    'login berhasil (200)': (res) => res.status === 200,
    'token diterima': () => token !== null && token !== '',
  });

  // 4. AKSES ENDPOINT PROTECTED
  const secureRes = http.get('http://10.100.20.53:8084/simple-risk/form', {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  check(secureRes, {
    'akses endpoint berhasil': (res) => res.status === 200,
  });

  // 5. TUNGGU ANTAR ITERASI
  sleep(1);
}
