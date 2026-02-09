import React, { useState, useEffect } from "react";
import { FiSearch, FiUsers, FiBriefcase, FiGrid, FiTrash2 } from "react-icons/fi";
import { toast } from "react-toastify";
import {
  listarTodosUsuarios,
  getUsuarioGrupos,
  getUsuarioCompanies,
  removeUsuarioFromGrupo,
  removeUsuarioFromCompany
} from "../../services/usuariosService";
import ConfirmModal from "../../components/ConfirmModal";

const UsuariosRelacionamentos = () => {
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedUser, setSelectedUser] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [userGrupos, setUserGrupos] = useState([]);
  const [userCompanies, setUserCompanies] = useState([]);
  const [confirmModal, setConfirmModal] = useState({ open: false, type: null, data: null });
  const [removing, setRemoving] = useState(false);

  useEffect(() => {
    fetchUsuarios();
  }, []);

  const fetchUsuarios = async () => {
    setLoading(true);
    try {
      const response = await listarTodosUsuarios({
        limit: 100,
      });
      setUsuarios(response.users || []);
    } catch (error) {
      console.error("Erro:", error);
      toast.error("Erro ao carregar usuários");
    } finally {
      setLoading(false);
    }
  };

  const fetchUserDetails = async (user) => {
    setDetailsLoading(true);
    setSelectedUser(user);
    try {
      const [grupos, companies] = await Promise.all([
        getUsuarioGrupos(user.id),
        getUsuarioCompanies(user.id)
      ]);
      setUserGrupos(grupos || []);
      setUserCompanies(companies || []);
    } catch (error) {
      console.error("Erro ao carregar detalhes:", error);
      toast.error("Erro ao carregar detalhes do usuário");
    } finally {
      setDetailsLoading(false);
    }
  };

  const handleRemoveGrupoClick = (grupo) => {
    setConfirmModal({
      open: true,
      type: "grupo",
      data: grupo,
    });
  };

  const handleRemoveCompanyClick = (company) => {
    setConfirmModal({
      open: true,
      type: "company",
      data: company,
    });
  };

  const handleConfirmRemove = async () => {
    if (!confirmModal.data) return;
    setRemoving(true);
    try {
      if (confirmModal.type === "grupo") {
        await removeUsuarioFromGrupo(confirmModal.data.grupo_usuario_id);
        toast.success("Usuário removido do grupo com sucesso");
        setUserGrupos(prev => prev.filter(g => g.grupo_usuario_id !== confirmModal.data.grupo_usuario_id));
      } else if (confirmModal.type === "company") {
        await removeUsuarioFromCompany(confirmModal.data.company_id, selectedUser.id);
        toast.success("Usuário removido da empresa com sucesso");
        setUserCompanies(prev => prev.filter(c => c.company_id !== confirmModal.data.company_id));
      }
    } catch (error) {
      console.error("Erro ao remover:", error);
      toast.error("Erro ao remover usuário");
    } finally {
      setRemoving(false);
      setConfirmModal({ open: false, type: null, data: null });
    }
  };

  const filteredUsuarios = usuarios.filter((user) => {
    const nome = String(user.first_name || "") + " " + String(user.last_name || "");
    const email = String(user.email || "");
    const search = String(searchTerm).toLowerCase();
    return nome.toLowerCase().includes(search) || email.toLowerCase().includes(search);
  });

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-white mb-2">
          Usuários e Relacionamentos
        </h1>
        <p className="text-gray-400">
          Visualize e gerencie empresas e grupos dos usuários
        </p>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-1 bg-gray-800 rounded-lg p-6">
          <div className="mb-4">
            <div className="relative">
              <FiSearch className="absolute left-3 top-3 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar por nome ou email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded text-white"
              />
            </div>
          </div>

          <div className="space-y-2 max-h-96 overflow-y-auto">
            {loading ? (
              <div className="text-center text-gray-400 py-8">Carregando...</div>
            ) : filteredUsuarios.length === 0 ? (
              <div className="text-center text-gray-400 py-8">Nenhum usuário encontrado</div>
            ) : (
              filteredUsuarios.map((user) => (
                <div
                  key={user.id}
                  onClick={() => fetchUserDetails(user)}
                  className={`p-4 rounded cursor-pointer transition-colors ${
                    selectedUser?.id === user.id
                      ? "bg-orange-600 hover:bg-orange-500"
                      : "bg-gray-700 hover:bg-gray-600"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-orange-500 rounded-full flex items-center justify-center text-white font-bold">
                      {String(user.first_name || "U").charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <p className="text-white font-medium">
                        {user.first_name} {user.last_name}
                      </p>
                      <p className="text-sm text-gray-400">{user.email}</p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="col-span-2 bg-gray-800 rounded-lg p-6">
          {!selectedUser ? (
            <div className="flex flex-col items-center justify-center h-full min-h-96">
              <FiUsers className="text-gray-600 mb-4" size={48} />
              <p className="text-gray-400">Selecione um usuário para ver detalhes</p>
            </div>
          ) : detailsLoading ? (
            <div className="flex items-center justify-center h-full min-h-96">
              <div className="text-center text-gray-400">Carregando detalhes...</div>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="border-b border-gray-700 pb-4">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 bg-orange-500 rounded-full flex items-center justify-center text-white font-bold text-2xl">
                    {String(selectedUser.first_name || "U").charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-white">
                      {selectedUser.first_name} {selectedUser.last_name}
                    </h2>
                    <p className="text-gray-400">{selectedUser.email}</p>
                  </div>
                </div>
              </div>

              <div>
                <div className="flex items-center gap-2 mb-4">
                  <FiBriefcase className="text-orange-500" size={20} />
                  <h3 className="text-xl font-semibold text-white">Empresas</h3>
                </div>
                {userCompanies.length === 0 ? (
                  <p className="text-gray-400 text-sm">Nenhuma empresa associada</p>
                ) : (
                  <div className="space-y-2">
                    {userCompanies.map((company) => (
                      <div
                        key={company.company_id}
                        className="bg-gray-700 p-4 rounded flex items-center justify-between group hover:bg-gray-600 transition-colors"
                      >
                        <div>
                          <p className="text-white font-medium">{company.name}</p>
                          {company.cnpj && (
                            <p className="text-sm text-gray-400">CNPJ: {company.cnpj}</p>
                          )}
                        </div>
                        <button
                          onClick={() => handleRemoveCompanyClick(company)}
                          className="text-red-400 hover:text-red-300 p-2 opacity-0 group-hover:opacity-100 transition-opacity"
                          title="Remover usuário desta empresa"
                        >
                          <FiTrash2 size={18} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <div className="flex items-center gap-2 mb-4">
                  <FiGrid className="text-orange-500" size={20} />
                  <h3 className="text-xl font-semibold text-white">Grupos</h3>
                </div>
                {userGrupos.length === 0 ? (
                  <p className="text-gray-400 text-sm">Nenhum grupo associado</p>
                ) : (
                  <div className="space-y-2">
                    {userGrupos.map((grupo) => (
                      <div
                        key={grupo.grupo_usuario_id}
                        className="bg-gray-700 p-4 rounded flex items-center justify-between group hover:bg-gray-600 transition-colors"
                      >
                        <div>
                          <p className="text-white font-medium">{grupo.nome}</p>
                        </div>
                        <button
                          onClick={() => handleRemoveGrupoClick(grupo)}
                          className="text-red-400 hover:text-red-300 p-2 opacity-0 group-hover:opacity-100 transition-opacity"
                          title="Remover usuário deste grupo"
                        >
                          <FiTrash2 size={18} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {selectedUser && confirmModal.open && (
        <ConfirmModal
          open={confirmModal.open}
          title={confirmModal.type === "grupo" ? "Remover do Grupo" : "Remover da Empresa"}
          description={
            confirmModal.type === "grupo"
              ? `Tem certeza que deseja remover ${[selectedUser.first_name, selectedUser.last_name].filter(Boolean).join(' ') || 'este usuário'} do grupo "${confirmModal.data?.nome}"?`
              : `Tem certeza que deseja remover ${[selectedUser.first_name, selectedUser.last_name].filter(Boolean).join(' ') || 'este usuário'} da empresa "${confirmModal.data?.name}"?`
          }
          confirmText="Remover"
          cancelText="Cancelar"
          onConfirm={handleConfirmRemove}
          onCancel={() => setConfirmModal({ open: false, type: null, data: null })}
          loading={removing}
          variant="danger"
        />
      )}
    </div>
  );
};

export default UsuariosRelacionamentos;
