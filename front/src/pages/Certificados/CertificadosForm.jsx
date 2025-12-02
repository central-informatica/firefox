import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { createCertificado } from "../../services/certificadosService";

import Input from "../../components/Input/Input";
import Button from "../../components/Button/Button";

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
    <div>
      <h1>Novo Certificado</h1>

      <form onSubmit={handleSubmit} style={{ maxWidth: "800px" }}>
        
        {/* Upload */}
        <Input
          type="file"
          name="arquivo"
          accept=".crt,.pem,.cer,.pfx"
          onChange={handleUploadChange}
        />

        {file && <p className="file-name">Selecionado: {file.name}</p>}

        {/* Senha opcional */}
        <Input
          name="senha"
          placeholder="Senha do certificado (se houver)"
          type="password"
          value={form.senha}
          onChange={handleChange}
        />

        <Button type="submit" className="upload-btn">
          Enviar
        </Button>
      </form>
    </div>
  );
};

export default CertificadosForm;
