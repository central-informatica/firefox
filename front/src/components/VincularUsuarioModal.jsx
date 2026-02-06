import { useState, useEffect } from 'react';
import { FiX, FiUserPlus } from 'react-icons/fi';
import { apiFetchWithToken } from '../api/api';
import { listarUsuariosEmpresa } from '../services/empresasService';

export default function VincularUsuarioModal({ open, empresaId, empresaNome, onClose, onSuccess }) {
  const [usuarios, setUsuarios] = useState([]);
  const [usuariosVinculados, setUsuariosVinculados] = useState([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (open && empresaId) {
      loadUsuarios();
    } else {
      // Reset state when closed
      setSelectedUserId('');
      setSearchTerm('');
      setUsuarios([]);
      setUsuariosVinculados([]);
    }
  }, [open, empresaId]);

  const loadUsuarios = async () => {
    setLoading(true);
    try {
      // Carrega todos os usuários da organização e os já vinculados em paralelo
      const [resUsuarios, usuariosEmpresa] = await Promise.all([
        apiFetchWithToken('/usuarios/?limit=100'),
        listarUsuariosEmpresa(empresaId)
      ]);

      if (!resUsuarios.ok) throw new Error('Erro ao carregar usuários');

      const data = await resUsuarios.json();
      const todosUsuarios = data.users || [];

      // Cria um Set com os IDs dos usuários já vinculados para filtragem rápida
      const idsVinculados = new Set(usuariosEmpresa.map(u => u.usuario_id || u.id));

      // Filtra apenas os usuários que NÃO estão vinculados
      const usuariosDisponiveis = todosUsuarios.filter(u => !idsVinculados.has(u.id));

      setUsuarios(usuariosDisponiveis);
      setUsuariosVinculados(usuariosEmpresa);
    } catch (error) {
      console.error('Erro ao carregar usuários:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedUserId) return;

    setSubmitting(true);
    try {
      const res = await apiFetchWithToken(`/empresas/id/${empresaId}/usuarios`, {
        method: 'POST',
        body: JSON.stringify({ user_id: selectedUserId }),
      });

      if (!res.ok) {
        const error = await res.text();
        throw new Error(error);
      }

      onSuccess?.();
      onClose();
    } catch (error) {
      console.error('Erro ao vincular usuário:', error);
      alert(error.message || 'Erro ao vincular usuário');
    } finally {
      setSubmitting(false);
    }
  };

  // Filtra usuários baseado no termo de busca
  const filteredUsuarios = usuarios.filter(user => {
    const searchLower = searchTerm.toLowerCase();
    const nome = `${user.first_name || ''} ${user.last_name || ''}`.toLowerCase();
    const email = (user.email || '').toLowerCase();
    return nome.includes(searchLower) || email.includes(searchLower);
  });

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />

      <div className="relative bg-dark-secondary rounded-modal shadow-2xl w-[90%] max-w-lg p-6 mx-4 border border-neutral-900 animate-[fadeInUp_0.3s_ease-out]">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-neutral-100 font-montserrat">
              Vincular Usuário
            </h3>
            <p className="text-sm text-neutral-400 mt-1">
              Empresa: <span className="text-neutral-300">{empresaNome}</span>
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-neutral-800 rounded-lg transition-colors"
          >
            <FiX size={20} className="text-neutral-400" />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Search Input */}
          <div className="mb-4">
            <input
              type="text"
              placeholder="Buscar usuário por nome ou email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2.5 bg-dark-tertiary border border-neutral-800 rounded-lg text-neutral-100 placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-xfire-orange focus:border-transparent"
            />
          </div>

          {/* Users List */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-neutral-300 mb-2">
              Selecione o usuário
            </label>

            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-xfire-orange"></div>
              </div>
            ) : (
              <div className="max-h-64 overflow-y-auto bg-dark-tertiary border border-neutral-800 rounded-lg">
                {filteredUsuarios.length === 0 ? (
                  <div className="p-4 text-center text-neutral-500">
                    {usuarios.length === 0
                      ? 'Todos os usuários já estão vinculados a esta empresa'
                      : 'Nenhum usuário encontrado com esse filtro'}
                  </div>
                ) : (
                  filteredUsuarios.map((user) => (
                    <label
                      key={user.id}
                      className={`flex items-center gap-3 p-3 cursor-pointer hover:bg-neutral-800/50 transition-colors border-b border-neutral-800 last:border-b-0 ${
                        selectedUserId === user.id ? 'bg-xfire-orange/10' : ''
                      }`}
                    >
                      <input
                        type="radio"
                        name="usuario"
                        value={user.id}
                        checked={selectedUserId === user.id}
                        onChange={(e) => setSelectedUserId(e.target.value)}
                        className="w-4 h-4 text-xfire-orange focus:ring-xfire-orange focus:ring-offset-dark-tertiary"
                      />
                      <div className="flex-1">
                        <div className="text-sm font-medium text-neutral-100">
                          {user.first_name} {user.last_name}
                        </div>
                        <div className="text-xs text-neutral-500">{user.email}</div>
                      </div>
                    </label>
                  ))
                )}
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 bg-dark-tertiary hover:bg-neutral-800 text-neutral-300 rounded-button transition-colors border border-neutral-800"
              disabled={submitting}
            >
              Cancelar
            </button>

            <button
              type="submit"
              disabled={!selectedUserId || submitting}
              className={`px-4 py-2.5 rounded-button text-white font-medium transition-all duration-200 flex items-center gap-2 ${
                !selectedUserId || submitting
                  ? 'bg-neutral-700 cursor-not-allowed'
                  : 'bg-xfire-orange hover:bg-xfire-orange/90'
              }`}
            >
              {submitting ? (
                <>
                  <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Vinculando...
                </>
              ) : (
                <>
                  <FiUserPlus size={16} />
                  Vincular Usuário
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
