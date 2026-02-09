import { useState, useRef, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { FiLock, FiCheckCircle, FiXCircle, FiArrowRight, FiShield, FiEye, FiEyeOff } from "react-icons/fi";

import Input from "../components/Input/Input";
import { resetPassword } from "../api/auth";

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState("form"); // form, success, error
  const [errorMessage, setErrorMessage] = useState("");

  const token = searchParams.get("token");

  // Password strength calculation
  const getPasswordStrength = (pwd) => {
    let strength = 0;
    if (pwd.length >= 12) strength++;
    if (/[a-z]/.test(pwd)) strength++;
    if (/[A-Z]/.test(pwd)) strength++;
    if (/[0-9]/.test(pwd)) strength++;
    if (/[^a-zA-Z0-9]/.test(pwd)) strength++;
    return strength;
  };

  const passwordStrength = getPasswordStrength(password);

  const getStrengthColor = () => {
    if (passwordStrength <= 2) return "bg-red-500";
    if (passwordStrength <= 3) return "bg-yellow-500";
    return "bg-green-500";
  };

  const getStrengthText = () => {
    if (passwordStrength <= 2) return "Fraca";
    if (passwordStrength <= 3) return "Media";
    return "Forte";
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!token) {
      setStatus("error");
      setErrorMessage("Token de recuperacao nao encontrado. Solicite um novo link.");
      return;
    }

    if (!password || !confirmPassword) {
      toast.error("Preencha todos os campos!");
      return;
    }

    if (password !== confirmPassword) {
      toast.error("As senhas nao coincidem!");
      return;
    }

    if (password.length < 12) {
      toast.error("A senha deve ter pelo menos 12 caracteres!");
      return;
    }

    if (passwordStrength < 4) {
      toast.error("A senha deve conter letras maiusculas, minusculas, numeros e caracteres especiais!");
      return;
    }

    setIsLoading(true);
    try {
      const response = await resetPassword(token, password);

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        const errorDetail = data.detail || "";

        let friendlyMessage = "Nao foi possivel redefinir sua senha.";

        if (errorDetail.toLowerCase().includes("expired") || errorDetail.toLowerCase().includes("expirado")) {
          friendlyMessage = "O link de recuperacao expirou. Solicite um novo link.";
        } else if (errorDetail.toLowerCase().includes("invalid") || errorDetail.toLowerCase().includes("invalido")) {
          friendlyMessage = "O link de recuperacao e invalido. Verifique se copiou o link corretamente.";
        } else if (errorDetail.toLowerCase().includes("password") || errorDetail.toLowerCase().includes("senha")) {
          friendlyMessage = errorDetail;
        } else if (errorDetail) {
          friendlyMessage = errorDetail;
        }

        throw new Error(friendlyMessage);
      }

      setStatus("success");
      toast.success("Senha redefinida com sucesso!");
    } catch (err) {
      console.error(err);
      setStatus("error");
      setErrorMessage(err?.message || "Nao foi possivel redefinir sua senha. Tente novamente.");
    } finally {
      setIsLoading(false);
    }
  };

  // Check if token exists on mount
  useEffect(() => {
    if (!token) {
      setStatus("error");
      setErrorMessage("Token de recuperacao nao encontrado. Solicite um novo link de recuperacao de senha.");
    }
  }, [token]);

  if (status === "success") {
    return (
      <div className="flex justify-center items-center min-h-screen bg-dark-primary p-4">
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-xfire-orange/20 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-[blob_7s_infinite]"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-xfire-red/20 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-[blob_9s_infinite_2s]"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-xfire-orange/10 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-[blob_11s_infinite_4s]"></div>
        </div>

        <div className="relative bg-dark-secondary/90 backdrop-blur-xl p-10 rounded-2xl shadow-[0_8px_40px_rgba(0,0,0,0.4)] w-[420px] max-w-[90%] border border-neutral-900 animate-[fadeInUp_0.6s_ease-out]">
          <div className="flex justify-center mb-6">
            <div className="bg-gradient-to-br from-green-500 to-green-600 p-4 rounded-2xl shadow-lg shadow-green-500/30 animate-[float_3s_ease-in-out_infinite]">
              <FiCheckCircle className="w-8 h-8 text-white" />
            </div>
          </div>

          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-green-500 mb-2 font-montserrat">
              Senha Redefinida!
            </h2>
            <p className="text-neutral-400 text-sm">
              Sua senha foi alterada com sucesso. Agora voce pode fazer login com a nova senha.
            </p>
          </div>

          <button
            onClick={() => navigate("/login")}
            className="w-full bg-gradient-to-r from-xfire-orange to-xfire-red hover:from-xfire-orange/90 hover:to-xfire-red/90 text-white font-semibold py-3.5 px-6 rounded-xl shadow-lg shadow-xfire-orange/30 hover:shadow-xl hover:shadow-xfire-orange/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 flex items-center justify-center gap-2 group"
          >
            <span>Ir para Login</span>
            <FiArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
          </button>

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

  if (status === "error") {
    return (
      <div className="flex justify-center items-center min-h-screen bg-dark-primary p-4">
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-xfire-orange/20 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-[blob_7s_infinite]"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-xfire-red/20 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-[blob_9s_infinite_2s]"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-xfire-orange/10 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-[blob_11s_infinite_4s]"></div>
        </div>

        <div className="relative bg-dark-secondary/90 backdrop-blur-xl p-10 rounded-2xl shadow-[0_8px_40px_rgba(0,0,0,0.4)] w-[420px] max-w-[90%] border border-neutral-900 animate-[fadeInUp_0.6s_ease-out]">
          <div className="flex justify-center mb-6">
            <div className="bg-gradient-to-br from-red-500 to-red-600 p-4 rounded-2xl shadow-lg shadow-red-500/30 animate-[float_3s_ease-in-out_infinite]">
              <FiXCircle className="w-8 h-8 text-white" />
            </div>
          </div>

          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-red-500 mb-2 font-montserrat">
              Erro na Recuperacao
            </h2>
            <p className="text-neutral-400 text-sm">
              {errorMessage}
            </p>
          </div>

          <div className="space-y-3">
            <button
              onClick={() => navigate("/esqueci-senha")}
              className="w-full bg-gradient-to-r from-xfire-orange to-xfire-red hover:from-xfire-orange/90 hover:to-xfire-red/90 text-white font-semibold py-3.5 px-6 rounded-xl shadow-lg shadow-xfire-orange/30 hover:shadow-xl hover:shadow-xfire-orange/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 flex items-center justify-center gap-2"
            >
              <span>Solicitar novo link</span>
            </button>

            <button
              onClick={() => navigate("/login")}
              className="w-full bg-transparent border border-neutral-700 hover:border-neutral-600 text-neutral-300 hover:text-white font-semibold py-3.5 px-6 rounded-xl transition-all duration-300 flex items-center justify-center gap-2"
            >
              <span>Voltar para Login</span>
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
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-xfire-orange/20 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-[blob_7s_infinite]"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-xfire-red/20 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-[blob_9s_infinite_2s]"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-xfire-orange/10 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-[blob_11s_infinite_4s]"></div>
      </div>

      <div className="relative bg-dark-secondary/90 backdrop-blur-xl p-10 rounded-2xl shadow-[0_8px_40px_rgba(0,0,0,0.4)] w-[420px] max-w-[90%] border border-neutral-900 animate-[fadeInUp_0.6s_ease-out]">
        <div className="flex justify-center mb-6">
          <div className="bg-gradient-to-br from-xfire-orange to-xfire-red p-4 rounded-2xl shadow-lg shadow-xfire-orange/30 animate-[float_3s_ease-in-out_infinite]">
            <FiLock className="w-8 h-8 text-white" />
          </div>
        </div>

        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-xfire-orange mb-2 font-montserrat">
            Redefinir Senha
          </h2>
          <p className="text-neutral-400 text-sm">
            Digite sua nova senha abaixo.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
              <FiLock className="text-neutral-500 group-focus-within:text-xfire-orange transition-colors duration-300" />
            </div>
            <Input
              name="password"
              type={showPassword ? "text" : "password"}
              placeholder="Nova senha"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="pl-12 pr-12 w-full"
              autoComplete="new-password"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 pr-4 flex items-center z-10 text-neutral-500 hover:text-xfire-orange transition-colors"
            >
              {showPassword ? <FiEyeOff className="w-5 h-5" /> : <FiEye className="w-5 h-5" />}
            </button>
          </div>

          {/* Password strength indicator */}
          {password && (
            <div className="space-y-2">
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map((level) => (
                  <div
                    key={level}
                    className={`h-1 flex-1 rounded-full transition-all duration-300 ${
                      level <= passwordStrength ? getStrengthColor() : "bg-neutral-700"
                    }`}
                  />
                ))}
              </div>
              <p className={`text-xs ${
                passwordStrength <= 2 ? "text-red-400" : passwordStrength <= 3 ? "text-yellow-400" : "text-green-400"
              }`}>
                Forca da senha: {getStrengthText()}
              </p>
            </div>
          )}

          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
              <FiLock className="text-neutral-500 group-focus-within:text-xfire-orange transition-colors duration-300" />
            </div>
            <Input
              name="confirmPassword"
              type={showConfirmPassword ? "text" : "password"}
              placeholder="Confirmar nova senha"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="pl-12 pr-12 w-full"
              autoComplete="new-password"
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="absolute inset-y-0 right-0 pr-4 flex items-center z-10 text-neutral-500 hover:text-xfire-orange transition-colors"
            >
              {showConfirmPassword ? <FiEyeOff className="w-5 h-5" /> : <FiEye className="w-5 h-5" />}
            </button>
          </div>

          {/* Password match indicator */}
          {confirmPassword && (
            <p className={`text-xs ${password === confirmPassword ? "text-green-400" : "text-red-400"}`}>
              {password === confirmPassword ? "As senhas coincidem" : "As senhas nao coincidem"}
            </p>
          )}

          <div className="text-xs text-neutral-500 space-y-1">
            <p>A senha deve conter:</p>
            <ul className="list-disc list-inside space-y-0.5">
              <li className={password.length >= 12 ? "text-green-400" : ""}>Pelo menos 12 caracteres</li>
              <li className={/[A-Z]/.test(password) ? "text-green-400" : ""}>Letras maiusculas</li>
              <li className={/[a-z]/.test(password) ? "text-green-400" : ""}>Letras minusculas</li>
              <li className={/[0-9]/.test(password) ? "text-green-400" : ""}>Numeros</li>
              <li className={/[^a-zA-Z0-9]/.test(password) ? "text-green-400" : ""}>Caracteres especiais (!@#$%...)</li>
            </ul>
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
                <span>Redefinindo...</span>
              </>
            ) : (
              <>
                <span>Redefinir senha</span>
                <FiArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
              </>
            )}
          </button>
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

export default ResetPassword;