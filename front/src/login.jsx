// src/login.jsx
import React, { useState } from "react";
import "./login.css";
import { toast } from "react-toastify";

import Input from "./components/Input/Input";
import Button from "./components/Button/Button";
import { useAuth } from "./auth/useAuth";

const Login = () => {
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email || !senha) {
      toast.error("Preencha todos os campos!");
      return;
    }

    try {
      await login(email, senha);
      toast.success("Login realizado com sucesso!");
    } catch (err) {
      console.error(err);
      toast.error("Credenciais inválidas.");
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>

      <form onSubmit={handleSubmit}>
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
          value={senha}
          onChange={(e) => setSenha(e.target.value)}
        />

        <Button type="submit">Entrar</Button>
      </form>
    </div>
  );
};

export default Login;
