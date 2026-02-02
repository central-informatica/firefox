import React, { useState } from "react";
import { FiLogOut } from "react-icons/fi";
import {
  FiGrid, FiUsers, FiSettings, FiLifeBuoy, FiCreditCard,
  FiFlag, FiChevronDown, FiChevronRight, FiMenu, FiX, FiChevronsLeft, FiChevronsRight,
  FiShield
} from "react-icons/fi";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../auth/useAuth";
import { useSidebar } from "../../contexts/SidebarContext";


export default function Sidebar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [openSub, setOpenSub] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  const { user, logout } = useAuth();
  const { expanded, setExpanded } = useSidebar();

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/login");
    } catch (err) {
      console.error("Erro ao fazer logout", err);
    }
  };


  const menu = [
    { id: "dashboard", label: "Dashboard", icon: <FiGrid />, path: "/dashboard" },
    {
      id: "empresas",
      label: "Empresas",
      icon: <FiLifeBuoy />,
      children: [
        { id: "emp-lista", label: "Listar empresas", path: "/empresas" },
        { id: "emp-nova", label: "Nova empresa", path: "/empresas/nova" }
      ]
    },
    {
      id: "planos",
      label: "Planos de trabalho",
      icon: <FiFlag />,
      children: [
        { id: "planos-lista", label: "Listar planos", path: "/planos" },
        { id: "planos-novo", label: "Novo plano", path: "/planos/novo" }
      ]
    },
    { id: "usuarios", label: "Usuarios", icon: <FiUsers />, path: "/usuarios" },
    {
      id: "grupos",
      label: "Grupos",
      icon: <FiGrid />,
      children: [
        { id: "grupo-lista", label: "Listar grupos", path: "/grupos" },
        { id: "grupo-novo", label: "Novo grupo", path: "/grupos/novo" },
      ]
    },
    {
      id: "certificados",
      label: "Certificados",
      icon: <FiCreditCard />,
      children: [
        { id: "cert-lista", label: "Listar certificados", path: "/certificados" },
        { id: "cert-grupos", label: "Grupos de certificados", path: "/certificados/grupos" }
      ]
    },
    {
      id: "seguranca",
      label: "Seguranca",
      icon: <FiShield />,
      children: [
        { id: "seg-whitelist", label: "Enderecos permitidos", path: "/seguranca/enderecos-permitidos" }
      ]
    },
    { id: "config", label: "Configuracoes", icon: <FiSettings />, path: "/config" },
  ];

  const toggleMobileSidebar = () => setMobileOpen(!mobileOpen);
  const toggleExpanded = () => setExpanded(!expanded);

  const isActive = (item) => location.pathname === item.path;

  const isParentActive = (item) => {
    if (!item.children) return false;
    return item.children.some(child => location.pathname === child.path);
  };

  const handleMainClick = (item) => {
    if (item.children) {
      if (!expanded) {
        setExpanded(true);
      }
      setOpenSub(openSub === item.id ? null : item.id);
      return;
    }

    navigate(item.path);
    setMobileOpen(false);
  };

  return (
    <>
      {/* MOBILE MENU BUTTON */}
      <button
        className="md:hidden fixed top-4 left-4 bg-xfire-orange hover:bg-xfire-orange/90 text-white border-none p-3 rounded-xl cursor-pointer z-[2001] shadow-lg transition-all duration-300"
        onClick={toggleMobileSidebar}
      >
        {mobileOpen ? <FiX size={24} /> : <FiMenu size={24} />}
      </button>

      {/* MOBILE OVERLAY */}
      {mobileOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/70 backdrop-blur-sm z-[1500] transition-opacity duration-300"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* SIDEBAR */}
      <aside
        className={`
          h-screen bg-dark-primary border-r border-neutral-900
          fixed left-0 top-0 flex flex-col z-[2000]
          transition-all duration-300 ease-in-out

          ${expanded ? 'w-64' : 'w-20'}

          ${mobileOpen ? 'translate-x-0' : 'max-md:-translate-x-full'}

          md:translate-x-0
        `}
      >
        {/* HEADER */}
        <div className="flex items-center justify-between p-5 border-b border-neutral-900">
          <div className={`font-bold text-xfire-orange transition-all duration-300 overflow-hidden font-montserrat ${
            expanded ? 'text-xl opacity-100' : 'text-sm opacity-0 w-0'
          }`}>
            XFireSecurity
          </div>

          {/* DESKTOP TOGGLE BUTTON */}
          <button
            onClick={toggleExpanded}
            className="hidden md:flex items-center justify-center w-8 h-8 rounded-lg hover:bg-dark-secondary text-neutral-400 hover:text-xfire-orange transition-all duration-300 group"
            title={expanded ? "Contrair" : "Expandir"}
          >
            {expanded ? (
              <FiChevronsLeft className="group-hover:scale-110 transition-transform" />
            ) : (
              <FiChevronsRight className="group-hover:scale-110 transition-transform" />
            )}
          </button>
        </div>

        {/* NAVIGATION */}
        <nav className="flex-1 overflow-y-auto overflow-x-hidden p-3 space-y-1">
          {menu.map((item) => (
            <div key={item.id}>
              {/* MAIN ITEM */}
              <div
                className={`
                  group relative flex items-center px-3 py-3 rounded-xl cursor-pointer
                  transition-all duration-300
                  ${expanded ? 'justify-start' : 'justify-center'}
                  ${
                    isActive(item) || isParentActive(item)
                      ? "bg-dark-secondary text-white border-l-4 border-xfire-orange"
                      : "text-neutral-400 hover:bg-dark-secondary hover:text-white"
                  }
                `}
                onClick={() => handleMainClick(item)}
              >
                {/* ICON */}
                <span className={`text-xl transition-all duration-300 flex-shrink-0 ${
                  expanded ? 'mr-3' : 'mr-0'
                } ${isActive(item) || isParentActive(item) ? 'text-xfire-orange' : ''}`}>
                  {item.icon}
                </span>

                {/* LABEL (only when expanded) */}
                <span className={`font-medium transition-all duration-300 whitespace-nowrap ${
                  expanded ? 'opacity-100 max-w-[200px]' : 'opacity-0 max-w-0 overflow-hidden'
                }`}>
                  {item.label}
                </span>

                {/* CHEVRON (only when expanded and has children) */}
                {item.children && expanded && (
                  <span className="ml-auto flex items-center transition-transform duration-300">
                    {openSub === item.id ? <FiChevronDown /> : <FiChevronRight />}
                  </span>
                )}

                {/* TOOLTIP (only when collapsed) */}
                {!expanded && (
                  <div className="absolute left-full ml-2 px-3 py-2 bg-dark-tertiary text-white text-sm rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 whitespace-nowrap z-50 shadow-xl border border-neutral-900">
                    {item.label}
                    <div className="absolute top-1/2 -left-1 -translate-y-1/2 border-4 border-transparent border-r-dark-tertiary"></div>
                  </div>
                )}
              </div>

              {/* SUBMENU (only visible when expanded and open) */}
              {item.children && openSub === item.id && expanded && (
                <div className="ml-3 mt-1 space-y-1 animate-[slideDown_0.3s_ease-out] overflow-hidden">
                  {item.children.map((sub) => (
                    <div
                      key={sub.id}
                      className={`
                        pl-10 py-2.5 rounded-lg cursor-pointer text-sm
                        transition-all duration-200
                        ${
                          isActive(sub)
                            ? "bg-dark-tertiary text-xfire-orange font-medium"
                            : "text-neutral-400 hover:bg-dark-secondary hover:text-white"
                        }
                      `}
                      onClick={() => {
                        navigate(sub.path);
                        setMobileOpen(false);
                      }}
                    >
                      {sub.label}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </nav>

        {/* LOGOUT BUTTON */}
        <div className="p-3">
          <div
            onClick={handleLogout}
            className={`
              group relative flex items-center px-3 py-3 rounded-xl cursor-pointer
              transition-all duration-300
              ${expanded ? 'justify-start' : 'justify-center'}
              text-neutral-400 hover:bg-xfire-red/10 hover:text-xfire-red
            `}
          >
            {/* ICON */}
            <span className={`text-xl transition-all duration-300 flex-shrink-0 ${
              expanded ? 'mr-3' : 'mr-0'
            }`}>
              <FiLogOut />
            </span>

            {/* LABEL */}
            <span className={`font-medium transition-all duration-300 whitespace-nowrap ${
              expanded ? 'opacity-100 max-w-[200px]' : 'opacity-0 max-w-0 overflow-hidden'
            }`}>
              Sair
            </span>

            {/* TOOLTIP (collapsed) */}
            {!expanded && (
              <div className="absolute left-full ml-2 px-3 py-2 bg-dark-tertiary text-white text-sm rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 whitespace-nowrap z-50 shadow-xl border border-neutral-900">
                Sair
                <div className="absolute top-1/2 -left-1 -translate-y-1/2 border-4 border-transparent border-r-dark-tertiary"></div>
              </div>
            )}
          </div>
        </div>

        {/* USER PROFILE */}
        <div className={`
          mt-auto border-t border-neutral-900 bg-dark-primary
          transition-all duration-300
        `}>
          <div className="p-4">
            <div className={`flex items-center gap-3 ${expanded ? '' : 'justify-center'}`}>
              <div className="w-10 h-10 bg-gradient-to-br from-xfire-orange to-xfire-red rounded-xl flex justify-center items-center text-white font-bold text-base flex-shrink-0 shadow-lg shadow-xfire-orange/30">
                {(user?.nome || "U").charAt(0).toUpperCase()}
              </div>

              <div className={`flex flex-col leading-tight transition-all duration-300 overflow-hidden ${
                expanded ? 'opacity-100 max-w-[180px]' : 'opacity-0 max-w-0'
              }`}>
                <div className="font-semibold text-sm text-neutral-100 truncate">
                  {user?.nome || "Usuario"}
                </div>
                <div className="text-xs text-neutral-500 truncate">
                  {user?.email || "email@example.com"}
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
