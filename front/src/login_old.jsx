import React, { useState } from "react";
import "./login.css";

import { toast } from "react-toastify";

// Componentes reutilizáveis
import Input from "./components/Input/Input";
import Button from "./components/Button/Button";

const Login = ({ onLogin }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email || !password) {
      toast.error("Preencha todos os campos!");
      return;
    }

    // Backend está esperando FormData
    const formData = new FormData();
    formData.append("nome", email);     // Backend usa "nome"
    formData.append("senha", password); // Backend usa "senha"

    try {
      const response = await fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        toast.error(data.detail || "Erro no login");
        return;
      }

      localStorage.setItem("token", data.token);
      onLogin();

    } catch (err) {
      console.error(err);
      toast.error("Erro de comunicação com o servidor");
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>

      <form id="meu-formulario" onSubmit={handleSubmit}>
        
        <Input
          name="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <Input
          name="senha"
          type="password"
          placeholder="Senha"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <Button type="submit">Entrar</Button>

      </form>
    </div>
  );
};

export default Login;
