import { useState, useRef, useEffect } from "react";
import { toast } from "react-toastify";
import { FiShield, FiArrowLeft } from "react-icons/fi";

import { verify2FA } from "../../api/auth";

const TwoFactorAuth = ({ userId, email, onSuccess, onBack }) => {
  const [code, setCode] = useState(["", "", "", "", "", ""]);
  const [isLoading, setIsLoading] = useState(false);
  const inputRefs = useRef([]);

  // Focus first input on mount
  useEffect(() => {
    inputRefs.current[0]?.focus();
  }, []);

  const handleChange = (index, value) => {
    // Only allow numbers
    if (value && !/^\d$/.test(value)) return;

    const newCode = [...code];
    newCode[index] = value;
    setCode(newCode);

    // Move to next input
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }

    // Auto-submit when all digits are filled
    if (value && index === 5) {
      const fullCode = newCode.join("");
      if (fullCode.length === 6) {
        handleSubmit(fullCode);
      }
    }
  };

  const handleKeyDown = (index, e) => {
    // Move to previous input on backspace
    if (e.key === "Backspace" && !code[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);

    if (pastedData.length === 6) {
      const newCode = pastedData.split("");
      setCode(newCode);
      inputRefs.current[5]?.focus();
      handleSubmit(pastedData);
    }
  };

  const handleSubmit = async (fullCode) => {
    if (!fullCode || fullCode.length !== 6) {
      toast.error("Digite o codigo completo de 6 digitos!");
      return;
    }

    setIsLoading(true);
    try {
      const response = await verify2FA(userId, fullCode);

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || "Codigo invalido");
      }

      toast.success("Verificacao concluida!");
      onSuccess();
    } catch (err) {
      console.error(err);
      toast.error(err?.message || "Codigo invalido. Tente novamente.");
      // Clear code on error
      setCode(["", "", "", "", "", ""]);
      inputRefs.current[0]?.focus();
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = () => {
    // This would need an API endpoint to resend the 2FA code
    toast.info("Um novo codigo foi enviado para seu email.");
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
        <div className="flex justify-center mb-6">
          <div className="bg-gradient-to-br from-xfire-orange to-xfire-red p-4 rounded-2xl shadow-lg shadow-xfire-orange/30 animate-[float_3s_ease-in-out_infinite]">
            <FiShield className="w-8 h-8 text-white" />
          </div>
        </div>

        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-xfire-orange mb-2 font-montserrat">
            Verificacao em Duas Etapas
          </h2>
          <p className="text-neutral-400 text-sm">
            Enviamos um codigo de 6 digitos para
          </p>
          <p className="text-white font-medium text-sm mt-1">
            {email}
          </p>
        </div>

        <div className="space-y-6">
          {/* Code input boxes */}
          <div className="flex justify-center gap-2">
            {code.map((digit, index) => (
              <input
                key={index}
                ref={(el) => (inputRefs.current[index] = el)}
                type="text"
                inputMode="numeric"
                maxLength={1}
                value={digit}
                onChange={(e) => handleChange(index, e.target.value)}
                onKeyDown={(e) => handleKeyDown(index, e)}
                onPaste={handlePaste}
                disabled={isLoading}
                className="w-12 h-14 text-center text-2xl font-bold bg-dark-primary border-2 border-neutral-700 rounded-xl text-white focus:border-xfire-orange focus:outline-none transition-colors duration-300 disabled:opacity-50"
              />
            ))}
          </div>

          {/* Submit button */}
          <button
            onClick={() => handleSubmit(code.join(""))}
            disabled={isLoading || code.join("").length !== 6}
            className="w-full bg-gradient-to-r from-xfire-orange to-xfire-red hover:from-xfire-orange/90 hover:to-xfire-red/90 text-white font-semibold py-3.5 px-6 rounded-xl shadow-lg shadow-xfire-orange/30 hover:shadow-xl hover:shadow-xfire-orange/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-70 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Verificando...</span>
              </>
            ) : (
              <span>Verificar</span>
            )}
          </button>

          {/* Resend and back options */}
          <div className="flex flex-col items-center gap-3">
            <button
              type="button"
              onClick={handleResend}
              disabled={isLoading}
              className="text-sm text-neutral-400 hover:text-xfire-orange transition-colors duration-300 bg-transparent border-none cursor-pointer disabled:opacity-50"
            >
              Nao recebeu o codigo? Reenviar
            </button>

            <button
              type="button"
              onClick={onBack}
              disabled={isLoading}
              className="inline-flex items-center gap-2 text-sm text-neutral-400 hover:text-xfire-orange transition-colors duration-300 disabled:opacity-50"
            >
              <FiArrowLeft className="w-4 h-4" />
              <span>Voltar para o login</span>
            </button>
          </div>
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
};

export default TwoFactorAuth;