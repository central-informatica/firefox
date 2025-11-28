import React, { useState } from "react";
import "./Dashboard.css";
import { toast } from "react-toastify";

import Input from "../../components/Input/Input";
import Button from "../../components/Button/Button";
import MainLayout from "../../layouts/MainLayout"; 

const Dashboard = ({ onLogout }) => {
  const [password, setPassword] = useState("");
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");

  const handleUploadChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!password) {
      toast.error("Por favor, insira a senha.");
      return;
    }

    if (!file) {
      toast.warning("Selecione um certificado para enviar.");
      return;
    }

    const formData = new FormData();
    formData.append("arquivo", file);
    formData.append("senha", password);

    // PEGAR CSRF DO COOKIE
    const csrf = document.cookie
      .split("; ")
      .find((row) => row.startsWith("csrf_token="))
      ?.split("=")[1];

    const response = await fetch("http://127.0.0.1:8000/upload/certificado", {
      method: "POST",
      body: formData,
      credentials: "include",              // 👈 OBRIGATÓRIO!!!
      headers: {
        "X-CSRF-Token": csrf,              // 👈 OBRIGATÓRIO!!!
      },
    });

    const data = await response.json();

    if (!response.ok) {
      toast.error(data.detail || "Erro ao enviar certificado.");
      return;
    }

    toast.success("O certificado foi salvo com sucesso!");
    setPassword("");
    setFile(null);
    e.target.reset();
  };


  return (
    <MainLayout>
      <div className="dashboard-container">
        <h2>Upload de Certificado</h2>

        <form id="formulario" onSubmit={handleSubmit}>
          <Input
            type="password"
            name="senha"
            placeholder="Digite sua senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <Input
            type="file"
            name="arquivo"
            accept=".crt,.pem,.cer,.pfx"
            onChange={handleUploadChange}
          />

          {file && <p className="file-name">Selecionado: {file.name}</p>}
          {error && <p className="error-message">{error}</p>}

          <Button type="submit" className="upload-btn">
            Enviar
          </Button>

          <Button type="button" onClick={onLogout} style={{ marginTop: "20px" }}>
            Sair
          </Button>
        </form>
      </div>
    </MainLayout>
  );
};

export default Dashboard;
