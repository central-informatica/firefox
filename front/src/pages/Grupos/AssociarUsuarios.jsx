import { useEffect, useState } from "react";
import SelectEmpresa from "../../components/Select/SelectEmpresa";
import Label from "../../components/Label/Label";
import { listarUsuariosPaginado } from "../../services/usuariosService";
import { listarGruposPorEmpresa, addUsuariosToGrupoBulk, getUsuariosByGrupo, listarGruposUsuariosPorEmpresa } from "../../services/gruposService";
import { toast } from "react-toastify";
import { FiUsers, FiPlus, FiCheck } from "react-icons/fi";

export default function AssociarUsuarios() {
  const [empresaId, setEmpresaId] = useState(null);
  const [users, setUsers] = useState([]);
  const [selectedUsers, setSelectedUsers] = useState(new Set());
  const [grupos, setGrupos] = useState([]);
  const [selectedGrupo, setSelectedGrupo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");

  // Map usuario_id -> [{ grupo_id, nome }]
  const [userGroupsMap, setUserGroupsMap] = useState(new Map());

  useEffect(() => {
    if (!empresaId) {
      setUsers([]);
      setGrupos([]);
      setSelectedUsers(new Set());
      setSelectedGrupo(null);
      setUserGroupsMap(new Map());
      return;
    }

    // fetch base data
    fetchUsers();
    fetchGrupos();
    // build associations map
    buildUserGroupsMap();
  }, [empresaId]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const res = await listarUsuariosPaginado({ empresa_id: empresaId, page: 1, limit: 100, search });
      setUsers(res.data || []);
    } catch (err) {
      console.error(err);
      toast.error("Erro ao carregar usuários");
    } finally {
      setLoading(false);
    }
  };

  const buildUserGroupsMap = async (maybeGroups) => {
    // ensure groups list
    let groupsList = maybeGroups || grupos;
    if (!groupsList || groupsList.length === 0) {
      try {
        const gdata = await listarGruposPorEmpresa(empresaId);
        groupsList = Array.isArray(gdata) ? gdata : (gdata.data || []);
      } catch (err) {
        console.error("Erro ao buscar grupos para montar mapa:", err);
        groupsList = [];
      }
    }

    try {
      const associations = await listarGruposUsuariosPorEmpresa(empresaId);
      const assocList = Array.isArray(associations) ? associations : (associations.data || associations);

      const groupById = Object.fromEntries((groupsList || []).map((g) => [g.grupo_id, g]));
      const map = new Map();
      (assocList || []).forEach((a) => {
        const uid = a.usuario_id;
        const gid = a.grupo_id;
        const info = groupById[gid] ? { grupo_id: gid, nome: groupById[gid].nome } : { grupo_id: gid, nome: null };
        const cur = map.get(uid) || [];
        cur.push(info);
        map.set(uid, cur);
      });

      setUserGroupsMap(map);
    } catch (err) {
      console.error("Erro ao carregar associações grupos-usuarios:", err);
      setUserGroupsMap(new Map());
    }
  };

  const fetchGrupos = async () => {
    try {
      if (!empresaId) {
        setGrupos([]);
        return;
      }

      console.debug("fetchGrupos: empresaId=", empresaId);
      const data = await listarGruposPorEmpresa(empresaId);
      console.debug("fetchGrupos: resposta=", data);

      // Normalizar diferentes formatos de retorno
      if (!data) {
        setGrupos([]);
        return;
      }

      const gruposArray = Array.isArray(data) ? data : (data.data || []);
      setGrupos(gruposArray);

      // Rebuild mapping with names
      await buildUserGroupsMap(gruposArray);
    } catch (err) {
      console.error(err);
      //toast.error("Erro ao carregar grupos");
      setGrupos([]);
    }
  };

  const isUserMemberOfSelectedGroup = (usuario_id) => {
    if (!selectedGrupo) return false;
    const list = userGroupsMap.get(usuario_id) || [];
    return list.some((g) => g.grupo_id === selectedGrupo.grupo_id);
  };

  const toggleSelectUser = (id) => {
    // prevent toggling if already member of selected group
    if (isUserMemberOfSelectedGroup(id)) return;

    setSelectedUsers((prev) => {
      const s = new Set(prev);
      if (s.has(id)) s.delete(id);
      else s.add(id);
      return s;
    });
  };

  const selectAll = () => {
    // select only users not already in selected group
    const selectable = users.filter((u) => !isUserMemberOfSelectedGroup(u.usuario_id)).map((u) => u.usuario_id);
    setSelectedUsers(new Set(selectable));
  };

  const clearSelection = () => {
    setSelectedUsers(new Set());
  };

  const handleAdicionarSelecionados = async () => {
    if (!selectedGrupo) {
      toast.error("Selecione um grupo à direita");
      return;
    }

    if (!selectedUsers.size) {
      toast.error("Selecione ao menos um usuário");
      return;
    }

    try {
      setLoading(true);
      const usuario_ids = Array.from(selectedUsers);
      const res = await addUsuariosToGrupoBulk(selectedGrupo.grupo_id, usuario_ids, empresaId);
      const created = res.created?.length || 0;
      const skipped = res.skipped?.length || 0;
      toast.success(`${created} usuário(s) adicionados; ${skipped} ignorado(s)`);

      // Refresh lists and mappings
      await fetchUsers();
      await fetchGruposUsuarios();
      clearSelection();
    } catch (err) {
      console.error(err);
      toast.error("Erro ao adicionar usuários ao grupo");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 w-full animate-[fadeInUp_0.6s_ease-out]">
      <div className="flex items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-3">
            <FiUsers className="text-purple-600" />
            Associar Usuários a Grupos
          </h1>
          <p className="text-sm text-gray-600">Selecione usuários à esquerda e um grupo à direita para associá-los em lote</p>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <Label>Empresa</Label>
            <SelectEmpresa value={empresaId} onChange={setEmpresaId} />
          </div>

          <div className="md:col-span-2">
            <Label>Buscar usuários</Label>
            <div className="flex gap-2">
              <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Pesquisar por nome ou email" className="flex-1 px-3 py-2 border rounded-lg" />
              <button onClick={fetchUsers} className="px-3 py-2 bg-emerald-500 text-white rounded-lg">Buscar</button>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Usuários (esquerda) */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold">Usuários</h3>
            <div className="flex items-center gap-2">
              <button onClick={selectAll} className="px-2 py-1 text-sm bg-gray-100 rounded">Selecionar todos</button>
              <button onClick={clearSelection} className="px-2 py-1 text-sm bg-gray-100 rounded">Limpar</button>
            </div>
          </div>

          <div className="max-h-96 overflow-y-auto space-y-2">
            {users.length === 0 ? (
              <p className="text-sm text-gray-500">Nenhum usuário encontrado</p>
            ) : (
              users.map((u) => (
                <div key={u.usuario_id} className="flex items-center justify-between p-2 rounded hover:bg-gray-50">
                  <div className="flex items-center gap-3">
                    <input type="checkbox" checked={selectedUsers.has(u.usuario_id)} onChange={() => toggleSelectUser(u.usuario_id)} disabled={isUserMemberOfSelectedGroup(u.usuario_id)} />
                    <div>
                      <p className="font-medium text-sm">{u.nome}</p>
                      <p className="text-xs text-gray-500">{u.email}</p>

                      {/* Mostrar badges dos grupos do usuário (dentro da empresa) */}
                      <div className="mt-1 flex gap-2">
                        {(userGroupsMap.get(u.usuario_id) || []).map((g) => (
                          <span key={g.grupo_id} className="text-xs bg-gray-100 px-2 py-0.5 rounded-full text-gray-700">{g.nome || g.grupo_id}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="text-xs text-gray-500">{u.cargo || ''}</div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Espaço central com ação */}
        <div className="flex flex-col items-center justify-center gap-4">
          <div className="text-center">
            <p className="text-sm text-gray-500">Selecionados</p>
            <p className="text-2xl font-bold">{selectedUsers.size}</p>
          </div>

          <button onClick={handleAdicionarSelecionados} disabled={!selectedGrupo || selectedUsers.size === 0 || loading} className="px-4 py-2 bg-emerald-600 text-white rounded-lg">
            <FiPlus size={16} /> Adicionar selecionados
          </button>
        </div>

        {/* Grupos (direita) */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold">Grupos</h3>
            <span className="text-xs bg-gray-100 px-2 py-1 rounded">{grupos.length}</span>
          </div>

          <div className="max-h-96 overflow-y-auto space-y-2">
            {grupos.length === 0 ? (
              <p className="text-sm text-gray-500">Nenhum grupo encontrado</p>
            ) : (
              grupos.map((g) => (
                <div key={g.grupo_id} onClick={() => {
                    // Select group and remove already-associated users from selection
                    setSelectedGrupo(g);
                    setSelectedUsers((prev) => {
                      const next = new Set(prev);
                      for (const uid of Array.from(next)) {
                        const groupsForUser = userGroupsMap.get(uid) || [];
                        if (groupsForUser.some((gg) => gg.grupo_id === g.grupo_id)) {
                          next.delete(uid);
                        }
                      }
                      return next;
                    });
                  }} className={`p-3 rounded cursor-pointer border ${selectedGrupo?.grupo_id === g.grupo_id ? 'border-emerald-500 bg-emerald-50' : 'border-transparent hover:bg-gray-50'}`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{g.nome}</p>
                      <p className="text-xs text-gray-500">{g.descricao || ''}</p>
                    </div>
                    {selectedGrupo?.grupo_id === g.grupo_id && (
                      <FiCheck className="text-emerald-600" />
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
