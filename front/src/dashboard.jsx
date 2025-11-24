import React, { useState } from "react";
import "./dashboard.css";
import { toast } from "react-toastify";


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
    let token = localStorage.getItem('token')
    fetch("http://127.0.0.1:8000/upload/certificado", {
        method: "POST",
        body: new FormData(document.getElementById("formulario")),
        mode: "cors",
        cache: "default",
         headers: {
            "Authorization": `Bearer ${token}`
        }
    }).then(async (response) => {
      const data = await response.json();

        if (!response.ok) {
          toast.error(data.detail || "Erro ao enviar certificado.");
          return;
        }else{
          toast.success("O certificado foi salvo com sucesso!");
        }
      
        setPassword("");
        setFile(null);
        e.target.reset();
    }).catch((err)=> {
      console.error(err);
      toast.error("Erro ao comunicar com o servidor.");
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
