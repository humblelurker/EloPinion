import { useState } from "react";
import { login } from "../api/auth";

export default function LoginForm({ onSuccess }) {
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [msg, setMsg] = useState("");

  const handle = async () => {
    const data = await login(email, pw);
    if (data.detail === "ok") onSuccess?.(data.user);
    else setMsg(data.detail);
  };

  return (
    <div>
      <h3>Iniciar sesión</h3>
      <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="email" />
      <input value={pw} onChange={e=>setPw(e.target.value)} type="password" placeholder="contraseña" />
      <button onClick={handle}>Entrar</button>
      <p>¿No tienes cuenta? <a href="/register">Regístrate aquí</a></p>
      {msg && <p>{msg}</p>}
    </div>
  );
}
