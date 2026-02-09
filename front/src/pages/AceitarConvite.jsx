import { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import {
  FiUserPlus,
  FiCheckCircle,
  FiXCircle,
  FiArrowRight,
  FiShield,
  FiLock,
  FiUser,
  FiEye,
  FiEyeOff,
} from "react-icons/fi";

import { acceptInvitation } from "../api/auth/auth";

const AceitarConvite = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [status, setStatus] = useState("form"); // form, loading, success, error
  const [errorMessage, setErrorMessage] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [form, setForm] = useState({
    firstName: "",
    lastName: "",
    password: "",
    confirmPassword: "",
  });

  const token = searchParams.get("token");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setErrorMessage(
        "Token de convite nao encontrado. Verifique o link recebido por email."
      );
    }
  }, [token]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!form.password || form.password.length < 8) {
      toast.error("A senha deve ter pelo menos 8 caracteres.");
      return;
    }

    if (form.password !== form.confirmPassword) {
      toast.error("As senhas nao conferem.");
      return;
    }

    setStatus("loading");

    try {
      const response = await acceptInvitation(
        token,
        form.password,
        form.firstName,
        form.lastName
      );

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        const errorDetail = data.detail || "";

        let friendlyMessage = "Nao foi possivel aceitar o convite.";

        if (
          errorDetail.toLowerCase().includes("expired") ||
          errorDetail.toLowerCase().includes("expirado")
        ) {
          friendlyMessage =
            "O convite expirou. Solicite um novo convite ao administrador.";
        } else if (
          errorDetail.toLowerCase().includes("invalid") ||
          errorDetail.toLowerCase().includes("invalido")
        ) {
          friendlyMessage =
            "O convite e invalido. Verifique se copiou o link corretamente.";
        } else if (
          errorDetail.toLowerCase().includes("already") ||
          errorDetail.toLowerCase().includes("ja")
        ) {
          friendlyMessage =
            "Este convite ja foi aceito anteriormente. Voce pode fazer login normalmente.";
        } else if (errorDetail) {
          friendlyMessage = errorDetail;
        }

        throw new Error(friendlyMessage);
      }

      setStatus("success");
      toast.success("Conta criada com sucesso!");
    } catch (err) {
      console.error(err);
      setStatus("error");
      setErrorMessage(
        err?.message ||
          "Nao foi possivel aceitar o convite. O token pode ter expirado ou ja foi utilizado."
      );
    }
  };

  const renderContent = () => {
    if (status === "loading") {
      return (
        <>
          <div className="flex justify-center mb-6">
            <div className="bg-gradient-to-br from-xfire-orange to-xfire-red p-4 rounded-2xl shadow-lg shadow-xfire-orange/30 animate-[float_3s_ease-in-out_infinite]">
              <FiUserPlus className="w-8 h-8 text-white" />
            </div>
          </div>

          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-xfire-orange mb-2 font-montserrat">
              Criando sua conta
            </h2>
            <p className="text-neutral-400 text-sm">
              Aguarde enquanto configuramos seu acesso...
            </p>
          </div>

          <div className="flex justify-center">
            <svg
              className="animate-spin h-12 w-12 text-xfire-orange"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
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
              Conta Criada!
            </h2>
            <p className="text-neutral-400 text-sm">
              Sua conta foi criada com sucesso. Agora voce pode acessar o
              sistema.
            </p>
          </div>

          <button
            onClick={() => navigate("/login")}
            className="w-full bg-gradient-to-r from-xfire-orange to-xfire-red hover:from-xfire-orange/90 hover:to-xfire-red/90 text-white font-semibold py-3.5 px-6 rounded-xl shadow-lg shadow-xfire-orange/30 hover:shadow-xl hover:shadow-xfire-orange/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 flex items-center justify-center gap-2 group cursor-pointer"
          >
            <span>Ir para Login</span>
            <FiArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
          </button>
        </>
      );
    }

    if (status === "error") {
      return (
        <>
          <div className="flex justify-center mb-6">
            <div className="bg-gradient-to-br from-red-500 to-red-600 p-4 rounded-2xl shadow-lg shadow-red-500/30 animate-[float_3s_ease-in-out_infinite]">
              <FiXCircle className="w-8 h-8 text-white" />
            </div>
          </div>

          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-red-500 mb-2 font-montserrat">
              Erro no Convite
            </h2>
            <p className="text-neutral-400 text-sm">{errorMessage}</p>
          </div>

          <button
            onClick={() => navigate("/login")}
            className="w-full bg-gradient-to-r from-xfire-orange to-xfire-red hover:from-xfire-orange/90 hover:to-xfire-red/90 text-white font-semibold py-3.5 px-6 rounded-xl shadow-lg shadow-xfire-orange/30 hover:shadow-xl hover:shadow-xfire-orange/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 flex items-center justify-center gap-2 group cursor-pointer"
          >
            <span>Ir para Login</span>
            <FiArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
          </button>
        </>
      );
    }

    // status === "form"
    return (
      <>
        <div className="flex justify-center mb-6">
          <div className="bg-gradient-to-br from-xfire-orange to-xfire-red p-4 rounded-2xl shadow-lg shadow-xfire-orange/30 animate-[float_3s_ease-in-out_infinite]">
            <FiUserPlus className="w-8 h-8 text-white" />
          </div>
        </div>

        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-xfire-orange mb-2 font-montserrat">
            Aceitar Convite
          </h2>
          <p className="text-neutral-400 text-sm">
            Complete seu cadastro para acessar o sistema.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* First Name */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-neutral-400">Nome</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <FiUser className="text-neutral-500" />
              </div>
              <input
                type="text"
                name="firstName"
                placeholder="Seu nome"
                value={form.firstName}
                onChange={handleChange}
                className="w-full pl-12 pr-4 py-3 bg-dark-tertiary border border-neutral-700 rounded-xl text-neutral-100 placeholder-neutral-500 focus:outline-none focus:border-xfire-orange focus:ring-1 focus:ring-xfire-orange transition-all duration-200"
              />
            </div>
          </div>

          {/* Last Name */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-neutral-400">
              Sobrenome
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <FiUser className="text-neutral-500" />
              </div>
              <input
                type="text"
                name="lastName"
                placeholder="Seu sobrenome"
                value={form.lastName}
                onChange={handleChange}
                className="w-full pl-12 pr-4 py-3 bg-dark-tertiary border border-neutral-700 rounded-xl text-neutral-100 placeholder-neutral-500 focus:outline-none focus:border-xfire-orange focus:ring-1 focus:ring-xfire-orange transition-all duration-200"
              />
            </div>
          </div>

          {/* Password */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-neutral-400">
              Senha *
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <FiLock className="text-neutral-500" />
              </div>
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                placeholder="Minimo 8 caracteres"
                value={form.password}
                onChange={handleChange}
                required
                className="w-full pl-12 pr-12 py-3 bg-dark-tertiary border border-neutral-700 rounded-xl text-neutral-100 placeholder-neutral-500 focus:outline-none focus:border-xfire-orange focus:ring-1 focus:ring-xfire-orange transition-all duration-200"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-4 flex items-center text-neutral-500 hover:text-neutral-300 cursor-pointer"
              >
                {showPassword ? <FiEyeOff /> : <FiEye />}
              </button>
            </div>
          </div>

          {/* Confirm Password */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-neutral-400">
              Confirmar Senha *
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <FiLock className="text-neutral-500" />
              </div>
              <input
                type={showConfirmPassword ? "text" : "password"}
                name="confirmPassword"
                placeholder="Repita a senha"
                value={form.confirmPassword}
                onChange={handleChange}
                required
                className="w-full pl-12 pr-12 py-3 bg-dark-tertiary border border-neutral-700 rounded-xl text-neutral-100 placeholder-neutral-500 focus:outline-none focus:border-xfire-orange focus:ring-1 focus:ring-xfire-orange transition-all duration-200"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute inset-y-0 right-0 pr-4 flex items-center text-neutral-500 hover:text-neutral-300 cursor-pointer"
              >
                {showConfirmPassword ? <FiEyeOff /> : <FiEye />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="w-full bg-gradient-to-r from-xfire-orange to-xfire-red hover:from-xfire-orange/90 hover:to-xfire-red/90 text-white font-semibold py-3.5 px-6 rounded-xl shadow-lg shadow-xfire-orange/30 hover:shadow-xl hover:shadow-xfire-orange/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 flex items-center justify-center gap-2 group cursor-pointer mt-6"
          >
            <span>Criar Conta</span>
            <FiArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
          </button>
        </form>
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

export default AceitarConvite;
