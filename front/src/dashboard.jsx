import React, { useState } from "react";
import "./dashboard.css";

const Dashboard = ({ onLogout }) => {
  const [password, setPassword] = useState("");
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");

  const handleUploadChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!password) {
      setError("Por favor, insira a senha.");
      return;
    }

    if (!file) {
      setError("Selecione um certificado para enviar.");
      return;
    }
    let token = localStorage.getItem('token')
    fetch("http://127.0.0.1:8000/upload/certificado", {
        method: "POST",
        body: new FormData(document.getElementById("formulario")),
        mode: "cors",
        cache: "default",
         headers: {
            "Authorization": `Bearer ${token}`
        }
    })
  };

  return (
    <>
      <div className="navbar">
        <h1>Dashboard</h1>
        <button className="logout-btn" onClick={onLogout}>
          Sair
        </button>
      </div>

      <div className="dashboard-container">
        <h2>Upload de Certificado</h2>
        <form id="formulario" onSubmit={handleSubmit}>
          <input
            type="password"
            name="senha"
            placeholder="Digite sua senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <input
            type="file"
            name="arquivo"
            accept=".crt,.pem,.cer,.pfx"
            onChange={handleUploadChange}
          />

          {file && <p className="file-name">Selecionado: {file.name}</p>}
          {error && <p className="error-message">{error}</p>}

          <button type="submit" className="upload-btn">
            Enviar
          </button>
        </form>
      </div>
    </>
  );
};

export default Dashboard;
