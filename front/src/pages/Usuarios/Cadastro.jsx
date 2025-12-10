import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/useAuth";
import { FiUser, FiMail, FiPhone, FiLock, FiUserPlus, FiArrowLeft, FiShield, FiCheck, FiArrowRight } from "react-icons/fi";

import Input from "../../components/Input/Input";
import { toast } from "react-toastify";

export default function Cadastro() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [telefone, setTelefone] = useState("");
  const [senha, setSenha] = useState("");
  const [confirmar, setConfirmar] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const { register } = useAuth();

  const totalSteps = 2;

  const nextStep = () => {
    if (currentStep === 1) {
      if (!nome || !email) {
        toast.error("Preencha seu nome e email!");
        return;
      }
      if (!email.includes('@')) {
        toast.error("Digite um email válido!");
        return;
      }
    }
    setCurrentStep(currentStep + 1);
  };

  const prevStep = () => {
    setCurrentStep(currentStep - 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!senha || !confirmar) {
      toast.error("Preencha todos os campos de senha!");
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
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-emerald-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob" style={{ animationDelay: '4s' }}></div>
      </div>

      <div className="relative bg-white/90 backdrop-blur-xl p-10 rounded-2xl shadow-[0_8px_40px_rgba(0,0,0,0.12)] w-[480px] max-w-[90%] border border-white/20 animate-[fadeInUp_0.6s_ease-out]">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-6">
            <div className="bg-gradient-to-br from-emerald-400 to-emerald-600 p-4 rounded-2xl shadow-lg shadow-emerald-500/30 animate-[float_3s_ease-in-out_infinite]">
              <FiUserPlus className="w-8 h-8 text-white" />
            </div>
          </div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent mb-2">
            Criar sua conta
          </h2>
          <p className="text-gray-600 text-sm">Preencha seus dados em {totalSteps} etapas simples</p>
        </div>

        {/* Progress Steps */}
        <div className="mb-10">
          <div className="flex items-start justify-between">
            {/* Step 1 */}
            <div className="flex flex-col items-center">
              <div className={`
                flex items-center justify-center w-11 h-11 rounded-full font-semibold text-sm transition-all duration-500 transform mb-3
                ${currentStep >= 1
                  ? 'bg-gradient-to-br from-emerald-500 to-emerald-600 text-white shadow-lg shadow-emerald-500/40 scale-110'
                  : 'bg-gray-200 text-gray-500 scale-100'}
              `}>
                {currentStep > 1 ? <FiCheck size={20} className="animate-fadeIn" /> : 1}
              </div>
              <span className={`text-xs font-medium transition-colors duration-300 text-center ${currentStep === 1 ? 'text-emerald-600' : 'text-gray-500'}`}>
                Dados Pessoais
              </span>
            </div>

            {/* Progress Bar */}
            <div className="flex-1 px-4 pt-5">
              <div className="h-1.5 rounded-full bg-gray-200 overflow-hidden">
                <div className={`
                  h-full bg-gradient-to-r from-emerald-500 to-emerald-600 transition-all duration-700 ease-out
                  ${currentStep > 1 ? 'w-full' : 'w-0'}
                `}></div>
              </div>
            </div>

            {/* Step 2 */}
            <div className="flex flex-col items-center">
              <div className={`
                flex items-center justify-center w-11 h-11 rounded-full font-semibold text-sm transition-all duration-500 transform mb-3
                ${currentStep >= 2
                  ? 'bg-gradient-to-br from-emerald-500 to-emerald-600 text-white shadow-lg shadow-emerald-500/40 scale-110'
                  : 'bg-gray-200 text-gray-500 scale-100'}
              `}>
                {currentStep > 2 ? <FiCheck size={20} className="animate-fadeIn" /> : 2}
              </div>
              <span className={`text-xs font-medium transition-colors duration-300 text-center ${currentStep === 2 ? 'text-emerald-600' : 'text-gray-500'}`}>
                Contato e Senha
              </span>
            </div>
          </div>
        </div>

        <form onSubmit={currentStep === totalSteps ? handleSubmit : (e) => { e.preventDefault(); nextStep(); }}>
          {/* Etapa 1: Dados Pessoais */}
          {currentStep === 1 && (
            <div className="space-y-5 animate-slideUp">
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
                  autoFocus
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

              {/* Info box */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-start gap-2 animate-fadeIn">
                <FiShield className="text-blue-600 flex-shrink-0 mt-0.5" size={16} />
                <p className="text-xs text-blue-800">
                  Seus dados pessoais são protegidos com criptografia de ponta
                </p>
              </div>
            </div>
          )}

          {/* Etapa 2: Contato e Senha */}
          {currentStep === 2 && (
            <div className="space-y-5 animate-slideUp">
              {/* Telefone Input */}
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <FiPhone className="text-gray-400 group-focus-within:text-emerald-500 transition-colors duration-300" />
                </div>
                <Input
                  type="tel"
                  name="telefone"
                  placeholder="(00) 00000-0000 (opcional)"
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
                  placeholder="Crie uma senha forte"
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
                <div className="px-1 animate-fadeIn">
                  <div className="flex items-center gap-2 text-xs">
                    <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all duration-500 ${
                          senha.length < 6 ? 'w-1/3 bg-red-500' :
                          senha.length < 10 ? 'w-2/3 bg-yellow-500' :
                          'w-full bg-emerald-500'
                        }`}
                      />
                    </div>
                    <span className={`font-semibold min-w-[45px] ${
                      senha.length < 6 ? 'text-red-500' :
                      senha.length < 10 ? 'text-yellow-600' :
                      'text-emerald-600'
                    }`}>
                      {senha.length < 6 ? 'Fraca' : senha.length < 10 ? 'Média' : 'Forte'}
                    </span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex gap-3 mt-8">
            {currentStep > 1 && (
              <button
                type="button"
                onClick={prevStep}
                className="flex-1 px-6 py-3.5 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded-xl transition-all duration-200 flex items-center justify-center gap-2 group cursor-pointer"
              >
                <FiArrowLeft className="group-hover:-translate-x-1 transition-transform duration-200" />
                Voltar
              </button>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className={`
                px-6 py-3.5 font-semibold rounded-xl transition-all duration-300 transform
                flex items-center justify-center gap-2 group
                ${currentStep === 1 ? 'flex-1' : 'flex-1'}
                ${isLoading
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 hover:-translate-y-0.5 active:translate-y-0 cursor-pointer'
                }
              `}
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Criando conta...</span>
                </>
              ) : currentStep < totalSteps ? (
                <>
                  <span>Próximo</span>
                  <FiArrowRight className="group-hover:translate-x-1 transition-transform duration-200" />
                </>
              ) : (
                <>
                  <FiUserPlus className="w-5 h-5" />
                  <span>Criar conta</span>
                </>
              )}
            </button>
          </div>

          {/* Divider */}
          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-white/90 text-gray-500">ou</span>
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
