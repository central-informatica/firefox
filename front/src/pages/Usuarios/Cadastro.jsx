import { useState } from "react";
import { useAuth } from "../../auth/useAuth";
import "../../login.css";

import Input from "../../components/Input/Input";
import Button from "../../components/Button/Button";
import { toast } from "react-toastify";

export default function Cadastro({ onVoltar }) {
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [telefone, setTelefone] = useState("");
  const [senha, setSenha] = useState("");
  const [confirmar, setConfirmar] = useState("");
  const [erro, setErro] = useState("");

  const { register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro("");

    if (!nome || !email || !senha || !confirmar) {
      toast.error("Preencha todos os campos!");
      return;
    }

    if (senha !== confirmar) {
      toast.error("As senhas não coincidem!");
      return;
    }

    try {
      await register({ nome, email, senha, telefone });
      toast.success("Cadastro realizado com sucesso!");

      if (onVoltar) onVoltar();
    } catch (err) {
      console.error(err);
      toast.error(err.message || "Erro ao cadastrar");
    }
  };

  return (
    <div className="login-container">
      <form className="login-form" onSubmit={handleSubmit}>
        <h2>Criar Conta</h2>

        {erro && <p className="error">{erro}</p>}

        <Input
          type="text"
          placeholder="Nome completo"
          value={nome}
          onChange={(e) => setNome(e.target.value)}
          required
        />

        <Input
          type="email"
          placeholder="E-mail"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <Input
          type="phone"
          placeholder="(00) - 00000 0000"
          value={telefone}
          onChange={(e) => setTelefone(e.target.value)}
        />
        <Input
          type="password"
          placeholder="Senha"
          value={senha}
          onChange={(e) => setSenha(e.target.value)}
          required
        />

        <Input
          type="password"
          placeholder="Confirmar senha"
          value={confirmar}
          onChange={(e) => setConfirmar(e.target.value)}
          required
        />

        <Button type="submit">Cadastrar</Button>

        <p className="register-link">
          Já possui conta?{" "}
          <Button
            type="button"
            onClick={onVoltar}
            className="link-button"
          >
            Voltar
          </Button>
        </p>
      </form>
    </div>
  );
}
