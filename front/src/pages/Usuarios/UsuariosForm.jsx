import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { toast } from "react-toastify";
import {
  FiUser,
  FiMail,
  FiShield,
  FiArrowLeft,
  FiSave,
  FiUserPlus,
  FiAlertCircle,
  FiCheck
} from "react-icons/fi";

import Input from "../../components/Input/Input";

import {
  createUsuario,
  getUsuarioById,
  updateUsuario,
} from "../../services/usuariosService";

const UsuarioForm = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const location = useLocation();
  const empresaId = location.state?.empresa_id ?? null;

  const isEdit = Boolean(id);
  const [isLoading, setIsLoading] = useState(false);

  const [form, setForm] = useState({
    nome: "",
    email: "",
    nivel: "COMUM",
  });

  useEffect(() => {
    if (isEdit) {
      getUsuarioById(id).then((data) => {
        if (data) setForm(data);
      });
    }
  }, [id, isEdit]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((old) => ({ ...old, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!form.nome || !form.email) {
      toast.error("Preencha todos os campos obrigatórios!");
      return;
    }
    setIsLoading(true);
    try {
      if (isEdit) {
        await updateUsuario(empresaId, id, {
          nome: form.nome,
          email: form.email,
          telefone: form.telefone,
        });
        toast.success("Usuário atualizado com sucesso!");
      } else {
        await createUsuario(form);
        toast.success("Usuário criado com sucesso!");
      }
      navigate("/usuarios");
    } catch (error) {
      var erro = JSON.parse(error.message)
      toast.error(erro.detail);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6 w-full animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate("/usuarios")}
            className="p-2 hover:bg-white rounded-lg transition-all duration-200 text-gray-600 hover:text-emerald-600 hover:shadow-md group"
          >
            <FiArrowLeft size={24} className="group-hover:-translate-x-1 transition-transform duration-200" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              {isEdit ? "Editar Usuário" : "Novo Usuário"}
            </h1>
            <p className="text-gray-600">
              {isEdit ? "Atualize as informações do usuário" : "Adicione um novo usuário ao sistema"}
            </p>
          </div>
        </div>
      </div>

      {/* Form Card */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden animate-slideUp">
        <form onSubmit={handleSubmit} className="p-8">
          <div className="space-y-6">
            {/* Nome Input */}
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                <FiUser className="text-emerald-600" size={18} />
                Nome Completo
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <FiUser className="text-gray-400 group-focus-within:text-emerald-500 transition-colors duration-300" />
                </div>
                <Input
                  name="nome"
                  placeholder="Digite o nome completo"
                  value={form.nome}
                  onChange={handleChange}
                  className="pl-12 w-full"
                  required
                />
              </div>
            </div>

            {/* Email Input */}
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                <FiMail className="text-emerald-600" size={18} />
                Email
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <FiMail className="text-gray-400 group-focus-within:text-emerald-500 transition-colors duration-300" />
                </div>
                <Input
                  name="email"
                  type="email"
                  placeholder="usuario@exemplo.com"
                  value={form.email}
                  onChange={handleChange}
                  className="pl-12 w-full"
                  required
                />
              </div>
            </div>

            {/* Nível Select */}
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                <FiShield className="text-emerald-600" size={18} />
                Nível de Acesso
              </label>

              {/* Radio buttons moderno ao invés de select */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {/* Usuário Comum */}
                <label className={`
                  relative flex items-center p-4 border-2 rounded-xl cursor-pointer transition-all duration-200
                  ${form.nivel === 'COMUM'
                    ? 'border-emerald-500 bg-emerald-50 shadow-md shadow-emerald-500/20'
                    : 'border-gray-200 hover:border-emerald-300 hover:bg-gray-50'
                  }
                `}>
                  <input
                    type="radio"
                    name="nivel"
                    value="COMUM"
                    checked={form.nivel === 'COMUM'}
                    onChange={handleChange}
                    className="sr-only"
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <div className={`p-1.5 rounded-lg ${form.nivel === 'COMUM' ? 'bg-blue-100' : 'bg-gray-100'}`}>
                        <FiUser className={form.nivel === 'COMUM' ? 'text-blue-600' : 'text-gray-500'} size={16} />
                      </div>
                      <span className={`font-semibold text-sm ${form.nivel === 'COMUM' ? 'text-emerald-700' : 'text-gray-700'}`}>
                        Comum
                      </span>
                    </div>
                    <p className="text-xs text-gray-600">Acesso básico ao sistema</p>
                  </div>
                  {form.nivel === 'COMUM' && (
                    <div className="absolute top-2 right-2">
                      <div className="w-5 h-5 bg-emerald-500 rounded-full flex items-center justify-center">
                        <FiCheck className="text-white" size={12} />
                      </div>
                    </div>
                  )}
                </label>

                {/* Administrador */}
                <label className={`
                  relative flex items-center p-4 border-2 rounded-xl cursor-pointer transition-all duration-200
                  ${form.nivel === 'ADMINISTRADOR'
                    ? 'border-emerald-500 bg-emerald-50 shadow-md shadow-emerald-500/20'
                    : 'border-gray-200 hover:border-emerald-300 hover:bg-gray-50'
                  }
                `}>
                  <input
                    type="radio"
                    name="nivel"
                    value="ADMINISTRADOR"
                    checked={form.nivel === 'ADMINISTRADOR'}
                    onChange={handleChange}
                    className="sr-only"
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <div className={`p-1.5 rounded-lg ${form.nivel === 'ADMINISTRADOR' ? 'bg-purple-100' : 'bg-gray-100'}`}>
                        <FiShield className={form.nivel === 'ADMINISTRADOR' ? 'text-purple-600' : 'text-gray-500'} size={16} />
                      </div>
                      <span className={`font-semibold text-sm ${form.nivel === 'ADMINISTRADOR' ? 'text-emerald-700' : 'text-gray-700'}`}>
                        Admin
                      </span>
                    </div>
                    <p className="text-xs text-gray-600">Acesso total</p>
                  </div>
                  {form.nivel === 'ADMINISTRADOR' && (
                    <div className="absolute top-2 right-2">
                      <div className="w-5 h-5 bg-emerald-500 rounded-full flex items-center justify-center">
                        <FiCheck className="text-white" size={12} />
                      </div>
                    </div>
                  )}
                </label>
              </div>
            </div>

            {/* Info Banner */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4 animate-fadeIn">
              <div className="flex gap-3">
                <FiAlertCircle className="text-blue-600 flex-shrink-0 mt-0.5" size={20} />
                <div>
                  <p className="text-sm font-medium text-blue-900 mb-1">Informações importantes</p>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• O email será usado para login no sistema</li>
                    <li>• Administradores têm acesso total ao sistema</li>
                    <li>• Você pode alterar o nível de acesso posteriormente</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Botões */}
          <div className="flex gap-3 mt-8 pt-6 border-t border-gray-100">
            <button
              type="button"
              onClick={() => navigate("/usuarios")}
              className="flex-1 px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded-xl transition-all duration-200 hover:shadow-md cursor-pointer"
              disabled={isLoading}
            >
              Cancelar
            </button>

            <button
              type="submit"
              disabled={isLoading}
              className={`
                flex-1 px-6 py-3 font-semibold rounded-xl transition-all duration-300 transform
                flex items-center justify-center gap-2
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
                  <span>Salvando...</span>
                </>
              ) : (
                <>
                  <FiSave className="w-5 h-5" />
                  <span>{isEdit ? "Salvar Alterações" : "Criar Usuário"}</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UsuarioForm;
