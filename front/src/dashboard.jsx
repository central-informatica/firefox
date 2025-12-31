// src/pages/Dashboard/Dashboard.jsx
import React, { useState } from "react";
import "./dashboard.css";
import { toast } from "react-toastify";

import Input from "./components/Input/Input";
import Button from "./components/Button/Button";
import { apiFetch } from "../../api/api";
import { useAuth } from "../../auth/useAuth";
import { apiFetchWithToken } from "./api/api";

const Dashboard = () => {
  const { logout } = useAuth();

  const [password, setPassword] = useState("");
  const [file, setFile] = useState(null);

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

    try {
      const formData = new FormData(document.getElementById("formulario"));

      const response = await apiFetchWithToken("/upload/certificado", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        toast.error(data.detail || "Erro ao enviar certificado.");
        return;
      }

      toast.success("Certificado enviado com sucesso!");
      setPassword("");
      setFile(null);
      e.target.reset();
    } catch (err) {
      console.error(err);
      toast.error("Erro ao comunicar com servidor.");
    }
  };

  return (
    <>
      <div className="navbar">
        <h1>Dashboard</h1>
        <button className="logout-btn" onClick={logout}>
          Sair
        </button>
      </div>

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

          <Button type="submit" className="upload-btn">
            Enviar
          </Button>
        </form>
      </div>
    </>
  );
};

export default Dashboard;