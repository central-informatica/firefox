import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/useAuth";
import { FiUser, FiMail, FiPhone, FiLock, FiUserPlus, FiArrowLeft, FiShield, FiCheck } from "react-icons/fi";

import Input from "../../components/Input/Input";
import { toast } from "react-toastify";

export default function Cadastro() {
  const navigate = useNavigate();
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [telefone, setTelefone] = useState("");
  const [senha, setSenha] = useState("");
  const [confirmar, setConfirmar] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const { register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!nome || !email || !senha || !confirmar) {
      toast.error("Preencha todos os campos obrigatórios!");
      return;
    }

    if (senha !== confirmar) {
      toast.error("As senhas não coincidem!");
      return;
    }

    if (senha.length < 6) {
      toast.error("A senha deve ter pelo menos 6 caracteres!");
      return;
    }

    setIsLoading(true);
    try {
      await register({ nome, email, senha, telefone });
      toast.success("Cadastro realizado com sucesso! Faça login para continuar.");
      navigate('/login');
    } catch (err) {
      console.error(err);
      toast.error(err.message || "Erro ao cadastrar");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-gradient-to-br from-emerald-50 via-blue-50 to-purple-50 p-4">
      {/* Background decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-emerald-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-[blob_7s_infinite]"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-[blob_9s_infinite_2s]"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-[blob_11s_infinite_4s]"></div>
      </div>

      <div className="relative bg-white/80 backdrop-blur-xl p-10 rounded-2xl shadow-[0_8px_40px_rgba(0,0,0,0.12)] w-[480px] max-w-[90%] border border-white/20 animate-[fadeInUp_0.6s_ease-out]">
        {/* Logo/Icon */}
        <div className="flex justify-center mb-6">
          <div className="bg-gradient-to-br from-emerald-400 to-emerald-600 p-4 rounded-2xl shadow-lg shadow-emerald-500/30 animate-[float_3s_ease-in-out_infinite]">
            <FiUserPlus className="w-8 h-8 text-white" />
          </div>
        </div>

        {/* Title */}
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent mb-2">
            Criar sua conta
          </h2>
          <p className="text-gray-600 text-sm">Preencha seus dados para começar</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Nome Input */}
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <FiUser className="text-gray-400 group-focus-within:text-emerald-500 transition-colors duration-300" />
            </div>
            <Input
              type="text"
              name="nome"
              placeholder="Nome completo"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              className="pl-12 w-full"
              autoComplete="name"
              required
            />
          </div>

          {/* Email Input */}
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <FiMail className="text-gray-400 group-focus-within:text-emerald-500 transition-colors duration-300" />
            </div>
            <Input
              type="email"
              name="email"
              placeholder="seu@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="pl-12 w-full"
              autoComplete="email"
              required
            />
          </div>

          {/* Telefone Input */}
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <FiPhone className="text-gray-400 group-focus-within:text-emerald-500 transition-colors duration-300" />
            </div>
            <Input
              type="tel"
              name="telefone"
              placeholder="(00) 00000-0000"
              value={telefone}
              onChange={(e) => setTelefone(e.target.value)}
              className="pl-12 w-full"
              autoComplete="tel"
            />
          </div>

          {/* Senha Input */}
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <FiLock className="text-gray-400 group-focus-within:text-emerald-500 transition-colors duration-300" />
            </div>
            <Input
              type="password"
              name="senha"
              placeholder="Crie uma senha"
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              className="pl-12 w-full"
              autoComplete="new-password"
              required
            />
          </div>

          {/* Confirmar Senha Input */}
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <FiCheck className="text-gray-400 group-focus-within:text-emerald-500 transition-colors duration-300" />
            </div>
            <Input
              type="password"
              name="confirmar"
              placeholder="Confirme sua senha"
              value={confirmar}
              onChange={(e) => setConfirmar(e.target.value)}
              className="pl-12 w-full"
              autoComplete="new-password"
              required
            />
          </div>

          {/* Password strength indicator */}
          {senha && (
            <div className="px-1">
              <div className="flex items-center gap-2 text-xs">
                <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all duration-300 ${
                      senha.length < 6 ? 'w-1/3 bg-red-500' :
                      senha.length < 10 ? 'w-2/3 bg-yellow-500' :
                      'w-full bg-emerald-500'
                    }`}
                  />
                </div>
                <span className={`font-medium ${
                  senha.length < 6 ? 'text-red-500' :
                  senha.length < 10 ? 'text-yellow-600' :
                  'text-emerald-600'
                }`}>
                  {senha.length < 6 ? 'Fraca' : senha.length < 10 ? 'Média' : 'Forte'}
                </span>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold py-3.5 px-6 rounded-xl shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-70 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2 group mt-6"
          >
            {isLoading ? (
              <>
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Criando conta...</span>
              </>
            ) : (
              <>
                <FiUserPlus className="w-5 h-5" />
                <span>Criar conta</span>
              </>
            )}
          </button>

          {/* Divider */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-white/80 text-gray-500">ou</span>
            </div>
          </div>

          {/* Back to Login Link */}
          <div className="text-center">
            <p className="text-sm text-gray-600">
              Já possui conta?{" "}
              <button
                type="button"
                onClick={() => navigate('/login')}
                className="font-semibold text-emerald-600 hover:text-emerald-700 transition-colors duration-300 bg-transparent border-none cursor-pointer hover:underline decoration-2 underline-offset-2 inline-flex items-center gap-1"
              >
                <FiArrowLeft className="w-4 h-4" />
                Voltar para login
              </button>
            </p>
          </div>
        </form>

        {/* Security Badge */}
        <div className="mt-8 pt-6 border-t border-gray-100">
          <div className="flex items-center justify-center gap-2 text-xs text-gray-500">
            <FiShield className="w-4 h-4 text-emerald-500" />
            <span>Seus dados estão protegidos e criptografados</span>
          </div>
        </div>
      </div>
    </div>
  );
}
