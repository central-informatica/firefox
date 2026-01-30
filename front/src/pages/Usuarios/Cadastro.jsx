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
        toast.error("Digite um email valido!");
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
      toast.error("As senhas nao coincidem!");
      return;
    }

    if (senha.length < 6) {
      toast.error("A senha deve ter pelo menos 6 caracteres!");
      return;
    }

    setIsLoading(true);
    try {
      await register({ nome, email, senha, telefone });
      toast.success("Cadastro realizado com sucesso! Faca login para continuar.");
      navigate('/login');
    } catch (err) {
      console.error(err);
      toast.error(err.message || "Erro ao cadastrar");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-dark-primary p-4">
      {/* Background decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-xfire-orange/20 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-xfire-red/20 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-blob" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-xfire-orange/10 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-blob" style={{ animationDelay: '4s' }}></div>
      </div>

      <div className="relative bg-dark-secondary/90 backdrop-blur-xl p-10 rounded-2xl shadow-[0_8px_40px_rgba(0,0,0,0.4)] w-[480px] max-w-[90%] border border-neutral-900 animate-[fadeInUp_0.6s_ease-out]">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-6">
            <div className="bg-gradient-to-br from-xfire-orange to-xfire-red p-4 rounded-2xl shadow-lg shadow-xfire-orange/30 animate-[float_3s_ease-in-out_infinite]">
              <FiUserPlus className="w-8 h-8 text-white" />
            </div>
          </div>
          <h2 className="text-2xl font-bold text-xfire-orange mb-2 font-montserrat">
            Criar sua conta
          </h2>
          <p className="text-neutral-400 text-sm">Preencha seus dados em {totalSteps} etapas simples</p>
        </div>

        {/* Progress Steps */}
        <div className="mb-10">
          <div className="flex items-start justify-between">
            {/* Step 1 */}
            <div className="flex flex-col items-center">
              <div className={`
                flex items-center justify-center w-11 h-11 rounded-full font-semibold text-sm transition-all duration-500 transform mb-3
                ${currentStep >= 1
                  ? 'bg-gradient-to-br from-xfire-orange to-xfire-red text-white shadow-lg shadow-xfire-orange/40 scale-110'
                  : 'bg-neutral-800 text-neutral-500 scale-100'}
              `}>
                {currentStep > 1 ? <FiCheck size={20} className="animate-fadeIn" /> : 1}
              </div>
              <span className={`text-xs font-medium transition-colors duration-300 text-center ${currentStep === 1 ? 'text-xfire-orange' : 'text-neutral-500'}`}>
                Dados Pessoais
              </span>
            </div>

            {/* Progress Bar */}
            <div className="flex-1 px-4 pt-5">
              <div className="h-1.5 rounded-full bg-neutral-800 overflow-hidden">
                <div className={`
                  h-full bg-gradient-to-r from-xfire-orange to-xfire-red transition-all duration-700 ease-out
                  ${currentStep > 1 ? 'w-full' : 'w-0'}
                `}></div>
              </div>
            </div>

            {/* Step 2 */}
            <div className="flex flex-col items-center">
              <div className={`
                flex items-center justify-center w-11 h-11 rounded-full font-semibold text-sm transition-all duration-500 transform mb-3
                ${currentStep >= 2
                  ? 'bg-gradient-to-br from-xfire-orange to-xfire-red text-white shadow-lg shadow-xfire-orange/40 scale-110'
                  : 'bg-neutral-800 text-neutral-500 scale-100'}
              `}>
                {currentStep > 2 ? <FiCheck size={20} className="animate-fadeIn" /> : 2}
              </div>
              <span className={`text-xs font-medium transition-colors duration-300 text-center ${currentStep === 2 ? 'text-xfire-orange' : 'text-neutral-500'}`}>
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
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
                  <FiUser className="text-neutral-500 group-focus-within:text-xfire-orange transition-colors duration-300" />
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
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
                  <FiMail className="text-neutral-500 group-focus-within:text-xfire-orange transition-colors duration-300" />
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
              <div className="bg-status-monitorado/10 border border-status-monitorado/30 rounded-lg p-3 flex items-start gap-2 animate-fadeIn">
                <FiShield className="text-status-monitorado flex-shrink-0 mt-0.5" size={16} />
                <p className="text-xs text-status-monitorado">
                  Seus dados pessoais sao protegidos com criptografia de ponta
                </p>
              </div>
            </div>
          )}

          {/* Etapa 2: Contato e Senha */}
          {currentStep === 2 && (
            <div className="space-y-5 animate-slideUp">
              {/* Telefone Input */}
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
                  <FiPhone className="text-neutral-500 group-focus-within:text-xfire-orange transition-colors duration-300" />
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
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
                  <FiLock className="text-neutral-500 group-focus-within:text-xfire-orange transition-colors duration-300" />
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
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
                  <FiCheck className="text-neutral-500 group-focus-within:text-xfire-orange transition-colors duration-300" />
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
                    <div className="flex-1 h-2 bg-neutral-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all duration-500 ${
                          senha.length < 6 ? 'w-1/3 bg-status-bloqueado' :
                          senha.length < 10 ? 'w-2/3 bg-status-expirando' :
                          'w-full bg-status-permitido'
                        }`}
                      />
                    </div>
                    <span className={`font-semibold min-w-[45px] ${
                      senha.length < 6 ? 'text-status-bloqueado' :
                      senha.length < 10 ? 'text-status-expirando' :
                      'text-status-permitido'
                    }`}>
                      {senha.length < 6 ? 'Fraca' : senha.length < 10 ? 'Media' : 'Forte'}
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
                className="flex-1 px-6 py-3.5 bg-dark-tertiary hover:bg-neutral-800 text-neutral-300 font-semibold rounded-xl transition-all duration-200 flex items-center justify-center gap-2 group cursor-pointer border border-neutral-800"
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
                  ? 'bg-neutral-700 text-neutral-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-xfire-orange to-xfire-red hover:from-xfire-orange/90 hover:to-xfire-red/90 text-white shadow-lg shadow-xfire-orange/30 hover:shadow-xl hover:shadow-xfire-orange/40 hover:-translate-y-0.5 active:translate-y-0 cursor-pointer'
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
                  <span>Proximo</span>
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
              <div className="w-full border-t border-neutral-800"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-dark-secondary text-neutral-500">ou</span>
            </div>
          </div>

          {/* Back to Login Link */}
          <div className="text-center">
            <p className="text-sm text-neutral-400">
              Ja possui conta?{" "}
              <button
                type="button"
                onClick={() => navigate('/login')}
                className="font-semibold text-xfire-orange hover:text-xfire-orange/80 transition-colors duration-300 bg-transparent border-none cursor-pointer hover:underline decoration-2 underline-offset-2 inline-flex items-center gap-1"
              >
                <FiArrowLeft className="w-4 h-4" />
                Voltar para login
              </button>
            </p>
          </div>
        </form>

        {/* Security Badge */}
        <div className="mt-8 pt-6 border-t border-neutral-800">
          <div className="flex items-center justify-center gap-2 text-xs text-neutral-500">
            <FiShield className="w-4 h-4 text-xfire-orange" />
            <span>Seus dados estao protegidos e criptografados</span>
          </div>
        </div>
      </div>
    </div>
  );
}
