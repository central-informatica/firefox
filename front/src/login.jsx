import React, { useState } from "react";
import "./login.css";

const Login = ({ onLogin }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError("Preencha todos os campos!");
      return;
    }
    setError("");
    
    fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        body: new FormData(document.getElementById("meu-formulario")),
        mode: "cors",
        cache: "default"
    })
    .then(response => response.json())
    .then((data)=> {
        console.log(data)
        localStorage.setItem('token', data['token'])
        onLogin();
    })
    .catch(error => {
        console.error(error)
    })
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      <form id="meu-formulario" onSubmit={handleSubmit}>
        <input
          name="nome"
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
