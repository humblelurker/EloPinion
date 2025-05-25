const API = "http://localhost:8000";

export async function register(email, password) {
  const r = await fetch(`${API}/auth/register/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return r.json();
}

export async function login(email, password) {
  const r = await fetch(`${API}/auth/login/`, {
    method: "POST",
    credentials: "include",          // guarda cookie de sesión
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return r.json();
}

export async function logout() {
  await fetch(`${API}/auth/logout/`, { credentials: "include" });
}
