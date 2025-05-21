import { useState } from "react";
import { register } from "../api/auth";

export default function RegisterForm() {
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [msg, setMsg] = useState("");

  const handle = async () => {
    const data = await register(email, pw);
    setMsg(data.detail || JSON.stringify(data));
  };

  return (
    <div>
      <h3>Registro</h3>
      <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="email" />
      <input value={pw} onChange={e=>setPw(e.target.value)} type="password" placeholder="contraseña" />
      <button onClick={handle}>Crear cuenta</button>
      {msg && <p>{msg}</p>}
    </div>
  );
}
