import { useState } from "react";
import { register } from "../api/auth";

export default function RegisterForm() {
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [msg, setMsg] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  const handle = async () => {
    setLoading(true);
    setMsg("");
    try {
      const data = await register(email, pw);
      setMsg(data.detail || "Respuesta inesperada");

      const isSuccess = data.detail?.toLowerCase().includes("exitosamente");
      setIsError(!isSuccess);

      if (isSuccess) {
        setEmail("");
        setPw("");
      }
    } catch (err) {
      setMsg("Error inesperado.");
      setIsError(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-form">
      <input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="email"
      />
      <input
        value={pw}
        onChange={(e) => setPw(e.target.value)}
        type="password"
        placeholder="contraseña"
      />
      <button onClick={handle} disabled={loading}>
        {loading ? "Creando..." : "Crear cuenta"}
      </button>
      {msg && (
        <p style={{ color: isError ? "crimson" : "green" }}>{msg}</p>
      )}
    </div>
  );
}