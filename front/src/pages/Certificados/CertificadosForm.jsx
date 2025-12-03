import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { createCertificado } from "../../services/certificadosService";

import Input from "../../components/Input/Input";
import Button from "../../components/Button/Button";
import "../../components/Forms/Forms.css";

const CertificadosForm = () => {
  const navigate = useNavigate();

  const [file, setFile] = useState(null);
  const [form, setForm] = useState({
    senha: "",
  });

  const handleUploadChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      toast.error("Selecione um arquivo para enviar.");
      return;
    }

    const data = new FormData();
    data.append("nome_arquivo", file);
    data.append("senha", form.senha);

    await createCertificado(data);

    navigate("/certificados");
  };

  return (
    <div className="page-form">
      <h1 className="titulo">Novo Certificado</h1>

      <form onSubmit={handleSubmit}>
        {/* Upload */}
        <div className="form-group" style={{ marginBottom: "12px" }}>
          <label>Arquivo do certificado</label>
          <Input
            type="file"
            name="arquivo"
            accept=".crt,.pem,.cer,.pfx"
            onChange={handleUploadChange}
          />
          {file && (
            <p className="file-name" style={{ marginTop: "6px", fontSize: "13px" }}>
              Selecionado: {file.name}
            </p>
          )}
        </div>

        {/* Senha opcional */}
        <div className="form-group" style={{ marginBottom: "16px" }}>
          <label>Senha do certificado (se houver)</label>
          <Input
            name="senha"
            type="password"
            value={form.senha}
            onChange={handleChange}
          />
        </div>

        <Button type="submit" className="btn">
          Enviar
        </Button>
      </form>
    </div>
  );
};

export default CertificadosForm;
