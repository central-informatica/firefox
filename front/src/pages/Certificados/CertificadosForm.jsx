import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

import Input from "../../components/Input/Input";
import Button from "../../components/Button/Button";
import SelectCustom from "../../components/Select/Select";
import Label from "../../components/Label/Label"
import "../../components/Forms/Forms.css";

import { useAuth } from "../../auth/useAuth";
import { getEmpresasDoUsuario } from "../../services/empresasService";
import { createCertificado } from "../../services/certificadosService";

export default function CertificadosForm() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [file, setFile] = useState(null);

  const [form, setForm] = useState({
    senha: "",
    empresa_id: null,
    proprietario: "",
    emitido_por: "",
    validade_inicio: "",
    valido_ate: "",
  });

  const [empresas, setEmpresas] = useState([]);
  const [empresaSelecionada, setEmpresaSelecionada] = useState(null);

  useEffect(() => {
    if (!user) return;

    getEmpresasDoUsuario(user.id).then((lista) => {
      const opcoes = lista.map((e) => ({
        value: e.empresa_id,
        label: e.razao_social,
      }));

      setEmpresas(opcoes);

      if (opcoes.length > 0) {
        setEmpresaSelecionada(opcoes[0]);
        setForm((f) => ({ ...f, empresa_id: opcoes[0].value }));
      }
    });
  }, [user]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      toast.error("Selecione um arquivo PFX.");
      return;
    }

    const data = new FormData();
    data.append("empresa_id", form.empresa_id);
    data.append("senha", form.senha || "");
    data.append("arquivo", file);               
    data.append("proprietario", form.proprietario || "");
    data.append("emitido_por", form.emitido_por || "");
    data.append("validade_inicio", form.validade_inicio || "");
    data.append("valido_ate", form.valido_ate || "");

    try {
      await createCertificado(data);
      toast.success("Certificado enviado com sucesso!");
      navigate("/certificados");
    } catch (err) {
      console.error(err);
      toast.error("Erro ao enviar certificado.");
    }
  };

  return (
    <div className="page-form">
      <h1 className="titulo">Novo Certificado</h1>

      <form onSubmit={handleSubmit}>
        {/* Empresa */}
        <label>Empresa</label>
        <SelectCustom
          options={empresas}
          value={empresaSelecionada}
          onChange={(opt) => {
            setEmpresaSelecionada(opt);
            setForm((f) => ({ ...f, empresa_id: opt.value }));
          }}
        />

        {/* Upload */}
        <Label>Certificado (PFX)</Label>
        <input
          type="file"
          accept=".pfx"
          onChange={(e) => {
            console.log("ARQUIVO SELECIONADO:", e.target.files[0]);
            setFile(e.target.files[0]);
          }}
        />

        {file && <p style={{ fontSize: 12 }}>Arquivo: {file.name}</p>}

        {/* Senha */}
        <label style={{ marginTop: 15 }}>Senha (se houver)</label>
        <Input
          name="senha"
          type="password"
          value={form.senha}
          onChange={(e) => setForm({ ...form, senha: e.target.value })}
        />
        <Button type="submit" className="btn" style={{ marginTop: 20 }}>
          Enviar
        </Button>
      </form>
    </div>
  );
}
