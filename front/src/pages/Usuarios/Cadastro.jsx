import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/useAuth";
import { IMaskInput } from "react-imask";
import {
  FiUser,
  FiMail,
  FiLock,
  FiUserPlus,
  FiArrowLeft,
  FiShield,
  FiCheck,
  FiArrowRight,
  FiBriefcase,
  FiMapPin,
  FiHome,
} from "react-icons/fi";

import Input from "../../components/Input/Input";
import { toast } from "react-toastify";

const BRAZILIAN_STATES = [
  { value: "AC", label: "Acre" },
  { value: "AL", label: "Alagoas" },
  { value: "AP", label: "Amapa" },
  { value: "AM", label: "Amazonas" },
  { value: "BA", label: "Bahia" },
  { value: "CE", label: "Ceara" },
  { value: "DF", label: "Distrito Federal" },
  { value: "ES", label: "Espirito Santo" },
  { value: "GO", label: "Goias" },
  { value: "MA", label: "Maranhao" },
  { value: "MT", label: "Mato Grosso" },
  { value: "MS", label: "Mato Grosso do Sul" },
  { value: "MG", label: "Minas Gerais" },
  { value: "PA", label: "Para" },
  { value: "PB", label: "Paraiba" },
  { value: "PR", label: "Parana" },
  { value: "PE", label: "Pernambuco" },
  { value: "PI", label: "Piaui" },
  { value: "RJ", label: "Rio de Janeiro" },
  { value: "RN", label: "Rio Grande do Norte" },
  { value: "RS", label: "Rio Grande do Sul" },
  { value: "RO", label: "Rondonia" },
  { value: "RR", label: "Roraima" },
  { value: "SC", label: "Santa Catarina" },
  { value: "SP", label: "Sao Paulo" },
  { value: "SE", label: "Sergipe" },
  { value: "TO", label: "Tocantins" },
];

export default function Cadastro() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);

  // Step 1: Dados da Empresa
  const [organizationName, setOrganizationName] = useState("");
  const [cnpj, setCnpj] = useState("");

  // Step 2: Endereco
  const [addressStreet, setAddressStreet] = useState("");
  const [addressCity, setAddressCity] = useState("");
  const [addressState, setAddressState] = useState("");
  const [addressPostalCode, setAddressPostalCode] = useState("");
  const [addressCountry] = useState("Brasil");

  // Step 3: Dados do Administrador
  const [adminFirstName, setAdminFirstName] = useState("");
  const [adminLastName, setAdminLastName] = useState("");
  const [adminEmail, setAdminEmail] = useState("");

  // Step 4: Senha
  const [adminPassword, setAdminPassword] = useState("");
  const [confirmar, setConfirmar] = useState("");

  const [isLoading, setIsLoading] = useState(false);

  const { register } = useAuth();

  const totalSteps = 4;

  const stepTitles = [
    "Dados da Empresa",
    "Endereco",
    "Administrador",
    "Senha",
  ];

  // Extract only digits from CNPJ
  const getCnpjDigits = () => cnpj.replace(/\D/g, "");

  // Extract only digits from CEP
  const getCepDigits = () => addressPostalCode.replace(/\D/g, "");

  const validateStep1 = () => {
    if (!organizationName.trim()) {
      toast.error("Digite o nome da empresa!");
      return false;
    }
    const cnpjDigits = getCnpjDigits();
    if (cnpjDigits.length !== 14) {
      toast.error("CNPJ deve ter 14 digitos!");
      return false;
    }
    return true;
  };

  const validateStep2 = () => {
    if (!addressStreet.trim() || addressStreet.length < 3) {
      toast.error("Digite o endereco completo (minimo 3 caracteres)!");
      return false;
    }
    if (!addressCity.trim() || addressCity.length < 2) {
      toast.error("Digite a cidade (minimo 2 caracteres)!");
      return false;
    }
    if (!addressState) {
      toast.error("Selecione o estado!");
      return false;
    }
    const cepDigits = getCepDigits();
    if (cepDigits.length !== 8) {
      toast.error("CEP deve ter 8 digitos!");
      return false;
    }
    return true;
  };

  const validateStep3 = () => {
    if (!adminFirstName.trim()) {
      toast.error("Digite o primeiro nome do administrador!");
      return false;
    }
    if (!adminLastName.trim()) {
      toast.error("Digite o sobrenome do administrador!");
      return false;
    }
    if (!adminEmail.trim() || !adminEmail.includes("@")) {
      toast.error("Digite um email valido!");
      return false;
    }
    return true;
  };

  const validateStep4 = () => {
    if (!adminPassword || !confirmar) {
      toast.error("Preencha todos os campos de senha!");
      return false;
    }
    if (adminPassword !== confirmar) {
      toast.error("As senhas nao coincidem!");
      return false;
    }
    if (adminPassword.length < 6) {
      toast.error("A senha deve ter pelo menos 6 caracteres!");
      return false;
    }
    return true;
  };

  const nextStep = () => {
    let isValid = false;
    switch (currentStep) {
      case 1:
        isValid = validateStep1();
        break;
      case 2:
        isValid = validateStep2();
        break;
      case 3:
        isValid = validateStep3();
        break;
      default:
        isValid = true;
    }
    if (isValid) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    setCurrentStep(currentStep - 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateStep4()) {
      return;
    }

    setIsLoading(true);
    try {
      await register({
        organization_name: organizationName,
        cnpj: getCnpjDigits(),
        address_street: addressStreet,
        address_city: addressCity,
        address_state: addressState,
        address_country: addressCountry,
        address_postal_code: getCepDigits(),
        admin_email: adminEmail,
        admin_password: adminPassword,
        admin_first_name: adminFirstName,
        admin_last_name: adminLastName,
      });
      toast.success(
        "Cadastro realizado com sucesso! Faca login para continuar."
      );
      navigate("/login");
    } catch (err) {
      console.error(err);
      toast.error(err.message || "Erro ao cadastrar");
    } finally {
      setIsLoading(false);
    }
  };

  const renderProgressSteps = () => {
    return (
      <div className="mb-8">
        <div className="flex items-start justify-between">
          {[1, 2, 3, 4].map((step, index) => (
            <div key={step} className="flex items-center flex-1">
              <div className="flex flex-col items-center">
                <div
                  className={`
                    flex items-center justify-center w-10 h-10 rounded-full font-semibold text-sm transition-all duration-500 transform mb-2
                    ${
                      currentStep >= step
                        ? "bg-gradient-to-br from-xfire-orange to-xfire-red text-white shadow-lg shadow-xfire-orange/40 scale-110"
                        : "bg-neutral-800 text-neutral-500 scale-100"
                    }
                  `}
                >
                  {currentStep > step ? (
                    <FiCheck size={18} className="animate-fadeIn" />
                  ) : (
                    step
                  )}
                </div>
                <span
                  className={`text-[10px] font-medium transition-colors duration-300 text-center max-w-[70px] ${
                    currentStep === step ? "text-xfire-orange" : "text-neutral-500"
                  }`}
                >
                  {stepTitles[index]}
                </span>
              </div>
              {index < 3 && (
                <div className="flex-1 px-2 pt-0 -mt-6">
                  <div className="h-1 rounded-full bg-neutral-800 overflow-hidden">
                    <div
                      className={`
                        h-full bg-gradient-to-r from-xfire-orange to-xfire-red transition-all duration-700 ease-out
                        ${currentStep > step ? "w-full" : "w-0"}
                      `}
                    ></div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const inputBaseClass =
    "w-full bg-dark-tertiary border border-neutral-800 rounded-xl py-3 px-4 pl-12 text-white placeholder-neutral-500 focus:outline-none focus:border-xfire-orange/50 focus:ring-2 focus:ring-xfire-orange/20 transition-all duration-300";

  return (
    <div className="flex justify-center items-center min-h-screen bg-dark-primary p-4">
      {/* Background decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-xfire-orange/20 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-blob"></div>
        <div
          className="absolute -bottom-40 -left-40 w-80 h-80 bg-xfire-red/20 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-blob"
          style={{ animationDelay: "2s" }}
        ></div>
        <div
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-xfire-orange/10 rounded-full mix-blend-normal filter blur-3xl opacity-30 animate-blob"
          style={{ animationDelay: "4s" }}
        ></div>
      </div>

      <div className="relative bg-dark-secondary/90 backdrop-blur-xl p-8 rounded-2xl shadow-[0_8px_40px_rgba(0,0,0,0.4)] w-[520px] max-w-[95%] border border-neutral-900 animate-[fadeInUp_0.6s_ease-out]">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="flex justify-center mb-4">
            <div className="bg-gradient-to-br from-xfire-orange to-xfire-red p-3 rounded-2xl shadow-lg shadow-xfire-orange/30 animate-[float_3s_ease-in-out_infinite]">
              <FiUserPlus className="w-7 h-7 text-white" />
            </div>
          </div>
          <h2 className="text-2xl font-bold text-xfire-orange mb-1 font-montserrat">
            Criar sua conta
          </h2>
          <p className="text-neutral-400 text-sm">
            Preencha seus dados em {totalSteps} etapas simples
          </p>
        </div>

        {/* Progress Steps */}
        {renderProgressSteps()}

        <form
          onSubmit={
            currentStep === totalSteps
              ? handleSubmit
              : (e) => {
                  e.preventDefault();
                  nextStep();
                }
          }
        >
          {/* Etapa 1: Dados da Empresa */}
          {currentStep === 1 && (
            <div className="space-y-4 animate-slideUp">
              {/* Organization Name Input */}
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
                  <FiBriefcase className="text-neutral-500 group-focus-within:text-xfire-orange transition-colors duration-300" />
                </div>
                <Input
                  type="text"
                  name="organizationName"
                  placeholder="Nome da empresa"
                  value={organizationName}
                  onChange={(e) => setOrganizationName(e.target.value)}
                  className="pl-12 w-full"
                  autoComplete="organization"
                  autoFocus
                  required
                />
              </div>

              {/* CNPJ Input */}
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
                  <FiShield className="text-neutral-500 group-focus-within:text-xfire-orange transition-colors duration-300" />
                </div>
                <IMaskInput
                  mask="00.000.000/0000-00"
                  value={cnpj}
                  unmask={false}
                  onAccept={(value) => setCnpj(value)}
                  placeholder="00.000.000/0000-00"
                  className={inputBaseClass}
                  autoComplete="off"
                  required
                />
              </div>

              {/* Info box */}
              <div className="bg-status-monitorado/10 border border-status-monitorado/30 rounded-lg p-3 flex items-start gap-2 animate-fadeIn">
                <FiShield
                  className="text-status-monitorado flex-shrink-0 mt-0.5"
                  size={16}
                />
                <p className="text-xs text-status-monitorado">
                  Os dados da sua empresa sao protegidos com criptografia de
                  ponta
                </p>
              </div>
            </div>
          )}

          {/* Etapa 2: Endereco */}
          {currentStep === 2 && (
            <div className="space-y-4 animate-slideUp">
              {/* Street Input */}
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
                  <FiHome className="text-neutral-500 group-focus-within:text-xfire-orange transition-colors duration-300" />
                </div>
                <Input
                  type="text"
                  name="addressStreet"
                  placeholder="Endereco completo"
                  value={addressStreet}
                  onChange={(e) => setAddressStreet(e.target.value)}
                  className="pl-12 w-full"
                  autoComplete="street-address"
                  autoFocus
                  required
                />
              </div>

              {/* City and State Row */}
              <div className="flex gap-3">
                {/* City Input */}
                <div className="relative group flex-1">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
                    <FiMapPin className="text-neutral-500 group-focus-within:text-xfire-orange transition-colors duration-300" />
                  </div>
                  <Input
                    type="text"
                    name="addressCity"
                    placeholder="Cidade"
                    value={addressCity}
                    onChange={(e) => setAddressCity(e.target.value)}
                    className="pl-12 w-full"
                    autoComplete="address-level2"
                    required
                  />
                </div>

                {/* State Select */}
                <div className="relative group w-32">
                  <select
                    name="addressState"
                    value={addressState}
                    onChange={(e) => setAddressState(e.target.value)}
                    className="w-full bg-dark-tertiary border border-neutral-800 rounded-xl py-3 px-4 text-white focus:outline-none focus:border-xfire-orange/50 focus:ring-2 focus:ring-xfire-orange/20 transition-all duration-300 appearance-none cursor-pointer"
                    required
                  >
                    <option value="" disabled>
                      UF
                    </option>
                    {BRAZILIAN_STATES.map((state) => (
                      <option key={state.value} value={state.value}>
                        {state.value}
                      </option>
                    ))}
                  </select>
                  <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                    <svg
                      className="w-4 h-4 text-neutral-500"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 9l-7 7-7-7"
                      />
                    </svg>
                  </div>
                </div>
              </div>

              {/* CEP and Country Row */}
              <div className="flex gap-3">
                {/* CEP Input */}
                <div className="relative group flex-1">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
                    <FiMapPin className="text-neutral-500 group-focus-within:text-xfire-orange transition-colors duration-300" />
                  </div>
                  <IMaskInput
                    mask="00000-000"
                    value={addressPostalCode}
                    unmask={false}
                    onAccept={(value) => setAddressPostalCode(value)}
                    placeholder="00000-000"
                    className={inputBaseClass}
                    autoComplete="postal-code"
                    required
                  />
                </div>

                {/* Country (readonly) */}
                <div className="relative group flex-1">
                  <Input
                    type="text"
                    name="addressCountry"
                    value={addressCountry}
                    readOnly
                    className="w-full bg-dark-tertiary/50 cursor-not-allowed"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Etapa 3: Dados do Administrador */}
          {currentStep === 3 && (
            <div className="space-y-4 animate-slideUp">
              {/* First Name and Last Name Row */}
              <div className="flex gap-3">
                {/* First Name Input */}
                <div className="relative group flex-1">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
                    <FiUser className="text-neutral-500 group-focus-within:text-xfire-orange transition-colors duration-300" />
                  </div>
                  <Input
                    type="text"
                    name="adminFirstName"
                    placeholder="Primeiro nome"
                    value={adminFirstName}
                    onChange={(e) => setAdminFirstName(e.target.value)}
                    className="pl-12 w-full"
                    autoComplete="given-name"
                    autoFocus
                    required
                  />
                </div>

                {/* Last Name Input */}
                <div className="relative group flex-1">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
                    <FiUser className="text-neutral-500 group-focus-within:text-xfire-orange transition-colors duration-300" />
                  </div>
                  <Input
                    type="text"
                    name="adminLastName"
                    placeholder="Sobrenome"
                    value={adminLastName}
                    onChange={(e) => setAdminLastName(e.target.value)}
                    className="pl-12 w-full"
                    autoComplete="family-name"
                    required
                  />
                </div>
              </div>

              {/* Email Input */}
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
                  <FiMail className="text-neutral-500 group-focus-within:text-xfire-orange transition-colors duration-300" />
                </div>
                <Input
                  type="email"
                  name="adminEmail"
                  placeholder="seu@email.com"
                  value={adminEmail}
                  onChange={(e) => setAdminEmail(e.target.value)}
                  className="pl-12 w-full"
                  autoComplete="email"
                  required
                />
              </div>

              {/* Info box */}
              <div className="bg-status-monitorado/10 border border-status-monitorado/30 rounded-lg p-3 flex items-start gap-2 animate-fadeIn">
                <FiShield
                  className="text-status-monitorado flex-shrink-0 mt-0.5"
                  size={16}
                />
                <p className="text-xs text-status-monitorado">
                  Voce sera o administrador principal da organizacao
                </p>
              </div>
            </div>
          )}

          {/* Etapa 4: Senha */}
          {currentStep === 4 && (
            <div className="space-y-4 animate-slideUp">
              {/* Senha Input */}
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
                  <FiLock className="text-neutral-500 group-focus-within:text-xfire-orange transition-colors duration-300" />
                </div>
                <Input
                  type="password"
                  name="adminPassword"
                  placeholder="Crie uma senha forte"
                  value={adminPassword}
                  onChange={(e) => setAdminPassword(e.target.value)}
                  className="pl-12 w-full"
                  autoComplete="new-password"
                  autoFocus
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
              {adminPassword && (
                <div className="px-1 animate-fadeIn">
                  <div className="flex items-center gap-2 text-xs">
                    <div className="flex-1 h-2 bg-neutral-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all duration-500 ${
                          adminPassword.length < 6
                            ? "w-1/3 bg-status-bloqueado"
                            : adminPassword.length < 10
                            ? "w-2/3 bg-status-expirando"
                            : "w-full bg-status-permitido"
                        }`}
                      />
                    </div>
                    <span
                      className={`font-semibold min-w-[45px] ${
                        adminPassword.length < 6
                          ? "text-status-bloqueado"
                          : adminPassword.length < 10
                          ? "text-status-expirando"
                          : "text-status-permitido"
                      }`}
                    >
                      {adminPassword.length < 6
                        ? "Fraca"
                        : adminPassword.length < 10
                        ? "Media"
                        : "Forte"}
                    </span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex gap-3 mt-6">
            {currentStep > 1 && (
              <button
                type="button"
                onClick={prevStep}
                className="flex-1 px-6 py-3 bg-dark-tertiary hover:bg-neutral-800 text-neutral-300 font-semibold rounded-xl transition-all duration-200 flex items-center justify-center gap-2 group cursor-pointer border border-neutral-800"
              >
                <FiArrowLeft className="group-hover:-translate-x-1 transition-transform duration-200" />
                Voltar
              </button>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className={`
                px-6 py-3 font-semibold rounded-xl transition-all duration-300 transform
                flex items-center justify-center gap-2 group flex-1
                ${
                  isLoading
                    ? "bg-neutral-700 text-neutral-400 cursor-not-allowed"
                    : "bg-gradient-to-r from-xfire-orange to-xfire-red hover:from-xfire-orange/90 hover:to-xfire-red/90 text-white shadow-lg shadow-xfire-orange/30 hover:shadow-xl hover:shadow-xfire-orange/40 hover:-translate-y-0.5 active:translate-y-0 cursor-pointer"
                }
              `}
            >
              {isLoading ? (
                <>
                  <svg
                    className="animate-spin h-5 w-5 text-white"
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
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-neutral-800"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-dark-secondary text-neutral-500">
                ou
              </span>
            </div>
          </div>

          {/* Back to Login Link */}
          <div className="text-center">
            <p className="text-sm text-neutral-400">
              Ja possui conta?{" "}
              <button
                type="button"
                onClick={() => navigate("/login")}
                className="font-semibold text-xfire-orange hover:text-xfire-orange/80 transition-colors duration-300 bg-transparent border-none cursor-pointer hover:underline decoration-2 underline-offset-2 inline-flex items-center gap-1"
              >
                <FiArrowLeft className="w-4 h-4" />
                Voltar para login
              </button>
            </p>
          </div>
        </form>

        {/* Security Badge */}
        <div className="mt-6 pt-4 border-t border-neutral-800">
          <div className="flex items-center justify-center gap-2 text-xs text-neutral-500">
            <FiShield className="w-4 h-4 text-xfire-orange" />
            <span>Seus dados estao protegidos e criptografados</span>
          </div>
        </div>
      </div>
    </div>
  );
}
