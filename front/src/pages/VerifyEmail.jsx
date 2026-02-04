import { useState, useEffect, useRef } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { FiMail, FiCheckCircle, FiXCircle, FiArrowRight, FiShield } from "react-icons/fi";

import { verifyEmail } from "../api/auth";

const VerifyEmail = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [status, setStatus] = useState("loading"); // loading, success, error
  const [errorMessage, setErrorMessage] = useState("");
  const hasVerified = useRef(false); // Prevent double calls in React Strict Mode

  const token = searchParams.get("token");

  useEffect(() => {
    const verify = async () => {
      // Prevent duplicate verification calls
      if (hasVerified.current) {
        return;
      }
      hasVerified.current = true;

      if (!token) {
        setStatus("error");
        setErrorMessage("Token de verificacao nao encontrado. Verifique o link recebido por email.");
        return;
      }

      try {
        const response = await verifyEmail(token);

        if (!response.ok) {
          const data = await response.json().catch(() => ({}));
          const errorDetail = data.detail || "";

          // Mensagens amigáveis baseadas no erro do backend
          let friendlyMessage = "Nao foi possivel verificar seu email.";

          if (errorDetail.toLowerCase().includes("expired") || errorDetail.toLowerCase().includes("expirado")) {
            friendlyMessage = "O link de verificacao expirou. Por favor, solicite um novo email de verificacao.";
          } else if (errorDetail.toLowerCase().includes("invalid") || errorDetail.toLowerCase().includes("invalido")) {
            friendlyMessage = "O link de verificacao e invalido. Verifique se copiou o link corretamente.";
          } else if (errorDetail.toLowerCase().includes("already") || errorDetail.toLowerCase().includes("ja")) {
            friendlyMessage = "Este email ja foi verificado anteriormente. Voce pode fazer login normalmente.";
          } else if (errorDetail) {
            friendlyMessage = errorDetail;
          }

          throw new Error(friendlyMessage);
        }

        setStatus("success");
        toast.success("Email verificado com sucesso!");
      } catch (err) {
        console.error(err);
        setStatus("error");
        setErrorMessage(
          err?.message || "Nao foi possivel verificar seu email. O token pode ter expirado ou ja foi utilizado."
        );
      }
    };

    verify();
  }, [token]);

  const renderContent = () => {
    if (status === "loading") {
      return (
        <>
          <div className="flex justify-center mb-6">
            <div className="bg-gradient-to-br from-xfire-orange to-xfire-red p-4 rounded-2xl shadow-lg shadow-xfire-orange/30 animate-[float_3s_ease-in-out_infinite]">
              <FiMail className="w-8 h-8 text-white" />
            </div>
          </div>

          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-xfire-orange mb-2 font-montserrat">
              Verificando Email
            </h2>
            <p className="text-neutral-400 text-sm">Aguarde enquanto confirmamos seu email...</p>
          </div>

          <div className="flex justify-center">
            <svg className="animate-spin h-12 w-12 text-xfire-orange" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
        </>
      );
    }

    if (status === "success") {
      return (
        <>
          <div className="flex justify-center mb-6">
            <div className="bg-gradient-to-br from-green-500 to-green-600 p-4 rounded-2xl shadow-lg shadow-green-500/30 animate-[float_3s_ease-in-out_infinite]">
              <FiCheckCircle className="w-8 h-8 text-white" />
            </div>
          </div>

          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-green-500 mb-2 font-montserrat">
              Email Verificado!
            </h2>
            <p className="text-neutral-400 text-sm">
              Seu email foi confirmado com sucesso. Agora voce pode acessar sua conta.
            </p>
          </div>

          <button
            onClick={() => navigate("/login")}
            className="w-full bg-gradient-to-r from-xfire-orange to-xfire-red hover:from-xfire-orange/90 hover:to-xfire-red/90 text-white font-semibold py-3.5 px-6 rounded-xl shadow-lg shadow-xfire-orange/30 hover:shadow-xl hover:shadow-xfire-orange/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 flex items-center justify-center gap-2 group"
          >
            <span>Ir para Login</span>
            <FiArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
          </button>
        </>
      );
    }

    // status === "error"
    return (
      <>
        <div className="flex justify-center mb-6">
          <div className="bg-gradient-to-br from-red-500 to-red-600 p-4 rounded-2xl shadow-lg shadow-red-500/30 animate-[float_3s_ease-in-out_infinite]">
            <FiXCircle className="w-8 h-8 text-white" />
          </div>
        </div>

        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-red-500 mb-2 font-montserrat">
            Erro na Verificacao
          </h2>
          <p className="text-neutral-400 text-sm">
            {errorMessage}
          </p>
        </div>

        <div className="space-y-3">
          <button
            onClick={() => navigate("/login")}
            className="w-full bg-gradient-to-r from-xfire-orange to-xfire-red hover:from-xfire-orange/90 hover:to-xfire-red/90 text-white font-semibold py-3.5 px-6 rounded-xl shadow-lg shadow-xfire-orange/30 hover:shadow-xl hover:shadow-xfire-orange/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 flex items-center justify-center gap-2 group"
          >
            <span>Ir para Login</span>
            <FiArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
          </button>

          <button
            onClick={() => navigate("/cadastro")}
            className="w-full bg-transparent border border-neutral-700 hover:border-neutral-600 text-neutral-300 hover:text-white font-semibold py-3.5 px-6 rounded-xl transition-all duration-300 flex items-center justify-center gap-2"
          >
            <span>Criar nova conta</span>
          </button>
        </div>
      </>
    );
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-dark-primary p-4">
      {/* Background decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-xfire-orange/20 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-[blob_7s_infinite]"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-xfire-red/20 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-[blob_9s_infinite_2s]"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-xfire-orange/10 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-[blob_11s_infinite_4s]"></div>
      </div>

      <div className="relative bg-dark-secondary/90 backdrop-blur-xl p-10 rounded-2xl shadow-[0_8px_40px_rgba(0,0,0,0.4)] w-[420px] max-w-[90%] border border-neutral-900 animate-[fadeInUp_0.6s_ease-out]">
        {renderContent()}

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

export default VerifyEmail;
