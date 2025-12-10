import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  FiPlus, FiEdit2, FiTrash2, FiUsers, FiUserCheck, FiShield, FiAlertCircle, FiMail
} from "react-icons/fi";
import { getUsuarios, deleteUsuario } from "../../services/usuariosService";

const UsuariosList = () => {
  const navigate = useNavigate();
  const [usuarios, setUsuarios] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const load = async () => {
    setIsLoading(true);
    try {
      const data = await getUsuarios();
      setUsuarios(data);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleDelete = async (id, nome) => {
    if (!confirm(`Deseja realmente excluir o usuário "${nome}"?\n\nEsta ação não pode ser desfeita.`)) return;

    try {
      await deleteUsuario(id);
      load();
    } catch (error) {
      console.error(error);
      alert("Erro ao excluir usuário");
    }
  };

  const getNivelBadge = (nivel) => {
    const badges = {
      ADMINISTRADOR: { color: "bg-purple-50 text-purple-700", icon: <FiShield size={12} />, label: "Admin" },
      COMUM: { color: "bg-blue-50 text-blue-700", icon: <FiUsers size={12} />, label: "Usuário" },
      MODERADOR: { color: "bg-orange-50 text-orange-700", icon: <FiUserCheck size={12} />, label: "Moderador" },
    };

    // Convert nivel to string and uppercase safely
    const nivelKey = String(nivel || 'COMUM').toUpperCase();
    const badge = badges[nivelKey] || badges.COMUM;

    return (
      <span className={`inline-flex items-center gap-1.5 px-3 py-1 ${badge.color} rounded-full text-xs font-medium`}>
        {badge.icon}
        {badge.label}
      </span>
    );
  };

  return (
    <div className="space-y-6 w-full">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Usuários</h1>
          <p className="text-gray-600">Gerencie os usuários cadastrados no sistema</p>
        </div>

        <button
          onClick={() => navigate("/usuarios/novo")}
          className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold rounded-xl shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 cursor-pointer"
        >
          <FiPlus size={20} />
          Novo Usuário
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-all duration-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-50 rounded-xl">
              <FiUsers className="text-blue-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-600 font-medium">Total de Usuários</p>
              <p className="text-2xl font-bold text-gray-800">{usuarios.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-all duration-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-emerald-50 rounded-xl">
              <FiUserCheck className="text-emerald-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-600 font-medium">Usuários Ativos</p>
              <p className="text-2xl font-bold text-gray-800">{usuarios.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-all duration-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-50 rounded-xl">
              <FiShield className="text-purple-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-600 font-medium">Administradores</p>
              <p className="text-2xl font-bold text-gray-800">
                {usuarios.filter(u => String(u.nivel || '').toUpperCase() === 'ADMINISTRADOR').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Usuário</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Email</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Nível</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Status</th>
                <th className="px-6 py-4 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">Ações</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-gray-100">
              {isLoading ? (
                <tr>
                  <td colSpan="5" className="px-6 py-12 text-center">
                    <div className="flex flex-col items-center gap-3">
                      <svg className="animate-spin h-8 w-8 text-emerald-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span className="text-gray-500">Carregando usuários...</span>
                    </div>
                  </td>
                </tr>
              ) : usuarios.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-12 text-center">
                    <div className="flex flex-col items-center gap-3">
                      <div className="p-4 bg-gray-100 rounded-full">
                        <FiUsers size={32} className="text-gray-400" />
                      </div>
                      <div>
                        <p className="text-gray-700 font-medium mb-1">Nenhum usuário cadastrado</p>
                        <p className="text-sm text-gray-500">Comece adicionando o primeiro usuário</p>
                      </div>
                      <button
                        onClick={() => navigate("/usuarios/novo")}
                        className="mt-2 inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition-colors cursor-pointer"
                      >
                        <FiPlus size={16} />
                        Adicionar Usuário
                      </button>
                    </div>
                  </td>
                </tr>
              ) : (
                usuarios.map((u) => (
                  <tr key={u.id} className="hover:bg-gray-50 transition-colors duration-150">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-emerald-400 to-emerald-600 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                          {u.nome?.charAt(0).toUpperCase() || "U"}
                        </div>
                        <div>
                          <div className="font-semibold text-gray-800">{u.nome}</div>
                          <div className="text-xs text-gray-500">ID: {u.id}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <FiMail size={14} className="text-gray-400" />
                        {u.email}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {getNivelBadge(u.nivel)}
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1 px-3 py-1 bg-emerald-50 text-emerald-700 rounded-full text-xs font-medium">
                        <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full"></div>
                        Ativo
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => navigate(`/usuarios/editar/${u.id}`)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer"
                          title="Editar usuário"
                        >
                          <FiEdit2 size={14} />
                          Editar
                        </button>
                        <button
                          onClick={() => handleDelete(u.id, u.nome)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-50 hover:bg-red-100 text-red-700 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer"
                          title="Excluir usuário"
                        >
                          <FiTrash2 size={14} />
                          Excluir
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Info Banner */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-100 rounded-xl p-5 flex items-start gap-4">
        <div className="p-3 bg-white rounded-xl shadow-sm">
          <FiAlertCircle className="text-blue-600" size={24} />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 mb-1 flex items-center gap-2">
            <span>Importante:</span>
            <span className="text-blue-600">Gerenciamento de Usuários</span>
          </h3>
          <p className="text-sm text-gray-700">
            Os usuários podem ter diferentes níveis de acesso: Administrador (controle total), Moderador (gerenciamento limitado) ou Usuário (acesso básico). Administradores podem gerenciar empresas, certificados e permissões.
          </p>
        </div>
      </div>
    </div>
  );
};

export default UsuariosList;
