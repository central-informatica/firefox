import React, { useState } from "react";
import "./login.css";

const Login = ({ onLogin }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email || !password) {
      setError("Preencha todos os campos!");
      return;
    }

    setError("");

    // Backend está esperando FormData
    const formData = new FormData();
    formData.append("nome", email);     // <-- O backend usa "nome"
    formData.append("senha", password); // <-- O backend usa "senha"

    try {
      const response = await fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        body: formData,   // <-- FormData, não JSON
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || "Erro no login");
        return;
      }

      localStorage.setItem("token", data.token);
      onLogin();

    } catch (err) {
      console.error(err);
      setError("Erro de comunicação com servidor");
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>

      <form id="meu-formulario" onSubmit={handleSubmit}>
        <input
          name="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          name="senha"
          type="password"
          placeholder="Senha"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        {error && <p className="error-message">{error}</p>}

        <button type="submit">Entrar</button>
      </form>
    </div>
  );
};

export default Login;
