import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { FiMail, FiArrowLeft, FiShield, FiSend } from "react-icons/fi";

import Input from "../components/Input/Input";
import { forgotPassword } from "../api/auth";

const ForgotPassword = () => {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email) {
      toast.error("Digite seu email!");
      return;
    }

    setIsLoading(true);
    try {
      const response = await forgotPassword(email);

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || "Erro ao solicitar recuperacao de senha");
      }

      setEmailSent(true);
      toast.success("Email enviado com sucesso!");
    } catch (err) {
      console.error(err);
      // Always show success to prevent email enumeration
      setEmailSent(true);
      toast.success("Se o email existir, voce recebera as instrucoes.");
    } finally {
      setIsLoading(false);
    }
  };

  if (emailSent) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-dark-primary p-4">
        {/* Background decorative elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-xfire-orange/20 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-[blob_7s_infinite]"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-xfire-red/20 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-[blob_9s_infinite_2s]"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-xfire-orange/10 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-[blob_11s_infinite_4s]"></div>
        </div>

        <div className="relative bg-dark-secondary/90 backdrop-blur-xl p-10 rounded-2xl shadow-[0_8px_40px_rgba(0,0,0,0.4)] w-[420px] max-w-[90%] border border-neutral-900 animate-[fadeInUp_0.6s_ease-out]">
          <div className="flex justify-center mb-6">
            <div className="bg-gradient-to-br from-green-500 to-green-600 p-4 rounded-2xl shadow-lg shadow-green-500/30 animate-[float_3s_ease-in-out_infinite]">
              <FiSend className="w-8 h-8 text-white" />
            </div>
          </div>

          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-green-500 mb-2 font-montserrat">
              Email Enviado!
            </h2>
            <p className="text-neutral-400 text-sm">
              Se o email <span className="text-white font-medium">{email}</span> estiver cadastrado,
              voce recebera um link para redefinir sua senha.
            </p>
          </div>

          <div className="space-y-3">
            <button
              onClick={() => navigate("/login")}
              className="w-full bg-gradient-to-r from-xfire-orange to-xfire-red hover:from-xfire-orange/90 hover:to-xfire-red/90 text-white font-semibold py-3.5 px-6 rounded-xl shadow-lg shadow-xfire-orange/30 hover:shadow-xl hover:shadow-xfire-orange/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 flex items-center justify-center gap-2 group"
            >
              <span>Voltar para Login</span>
            </button>

            <button
              onClick={() => setEmailSent(false)}
              className="w-full bg-transparent border border-neutral-700 hover:border-neutral-600 text-neutral-300 hover:text-white font-semibold py-3.5 px-6 rounded-xl transition-all duration-300 flex items-center justify-center gap-2"
            >
              <span>Tentar outro email</span>
            </button>
          </div>

          <div className="mt-8 pt-6 border-t border-neutral-800">
            <div className="flex items-center justify-center gap-2 text-xs text-neutral-500">
              <FiShield className="w-4 h-4 text-xfire-orange" />
              <span>Conexao segura e criptografada</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-center items-center min-h-screen bg-dark-primary p-4">
      {/* Background decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-xfire-orange/20 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-[blob_7s_infinite]"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-xfire-red/20 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-[blob_9s_infinite_2s]"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-xfire-orange/10 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-[blob_11s_infinite_4s]"></div>
      </div>

      <div className="relative bg-dark-secondary/90 backdrop-blur-xl p-10 rounded-2xl shadow-[0_8px_40px_rgba(0,0,0,0.4)] w-[420px] max-w-[90%] border border-neutral-900 animate-[fadeInUp_0.6s_ease-out]">
        <div className="flex justify-center mb-6">
          <div className="bg-gradient-to-br from-xfire-orange to-xfire-red p-4 rounded-2xl shadow-lg shadow-xfire-orange/30 animate-[float_3s_ease-in-out_infinite]">
            <FiMail className="w-8 h-8 text-white" />
          </div>
        </div>

        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-xfire-orange mb-2 font-montserrat">
            Esqueceu sua senha?
          </h2>
          <p className="text-neutral-400 text-sm">
            Digite seu email e enviaremos um link para redefinir sua senha.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
              <FiMail className="text-neutral-500 group-focus-within:text-xfire-orange transition-colors duration-300" />
            </div>
            <Input
              name="email"
              type="email"
              placeholder="seu@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="pl-12 w-full"
              autoComplete="email"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-xfire-orange to-xfire-red hover:from-xfire-orange/90 hover:to-xfire-red/90 text-white font-semibold py-3.5 px-6 rounded-xl shadow-lg shadow-xfire-orange/30 hover:shadow-xl hover:shadow-xfire-orange/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-70 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2 group"
          >
            {isLoading ? (
              <>
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Enviando...</span>
              </>
            ) : (
              <>
                <span>Enviar link de recuperacao</span>
              </>
            )}
          </button>

          <div className="text-center">
            <button
              type="button"
              onClick={() => navigate('/login')}
              className="inline-flex items-center gap-2 text-sm text-neutral-400 hover:text-xfire-orange transition-colors duration-300"
            >
              <FiArrowLeft className="w-4 h-4" />
              <span>Voltar para o login</span>
            </button>
          </div>
        </form>

        <div className="mt-8 pt-6 border-t border-neutral-800">
          <div className="flex items-center justify-center gap-2 text-xs text-neutral-500">
            <FiShield className="w-4 h-4 text-xfire-orange" />
            <span>Conexao segura e criptografada</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;