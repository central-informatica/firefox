import React, { useState } from "react";
import "./Sidebar.css";
import { 
  FiGrid, FiUsers, FiSettings, FiLifeBuoy, FiCreditCard, 
  FiFlag, FiChevronDown, FiChevronRight
} from "react-icons/fi";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/useAuth";

export default function Sidebar() {
  const [active, setActive] = useState("dashboard");
  const [open, setOpen] = useState(false);
  const [openSub, setOpenSub] = useState(null); // controla qual submenu está aberto
  const navigate = useNavigate();
  const { user } = useAuth() || {}; // ← usuário real do sistema
  const auth = useAuth();
  

  // ---- CONFIG DO MENU ----
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

    { id: "usuarios", label: "Usuários", icon: <FiUsers />, path: "/usuarios" },

    {
      id: "certificados",
      label: "Certificados",
      icon: <FiCreditCard />,
      children: [
        { id: "cert-lista", label: "Listar certificados", path: "/certificados" },
        { id: "cert-grupos", label: "Grupos de certificados", path: "/certificados/grupos" }
      ]
    },

    { id: "config", label: "Configurações", icon: <FiSettings />, path: "/config" },
  ];

  const toggleSidebar = () => setOpen(!open);

  const handleMainClick = (item) => {
    if (item.children) {
      setOpenSub(openSub === item.id ? null : item.id);
      return;
    }

    navigate(item.path);
    setActive(item.id);
    setOpen(false);
  };

  return (
    <>
      {/* MOBILE */}
      <button className="sidebar-toggle" onClick={toggleSidebar}>☰</button>
      {open && <div className="sidebar-overlay" onClick={() => setOpen(false)} />}

      <aside className={`sidebar ${open ? "open" : ""}`}>
        
        <div className="sidebar-title">Certi Pro</div>

        <nav className="sidebar-menu">
          {menu.map((item) => (
            <div key={item.id}>
              
              {/* ITEM PRINCIPAL */}
              <div
                className={`menu-item ${active === item.id ? "active" : ""}`}
                onClick={() => handleMainClick(item)}
              >
                <span className="icon">{item.icon}</span>
                <span className="label">{item.label}</span>

                {item.children && (
                  <span className="submenu-arrow">
                    {openSub === item.id ? <FiChevronDown /> : <FiChevronRight />}
                  </span>
                )}
              </div>

              {/* SUBMENU */}
              {item.children && openSub === item.id && (
                <div className="submenu">
                  {item.children.map((sub) => (
                    <div
                      key={sub.id}
                      className={`submenu-item ${active === sub.id ? "active" : ""}`}
                      onClick={() => {
                        setActive(sub.id);
                        navigate(sub.path);
                        setOpen(false);
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

        {/* ---- PERFIL DO USUÁRIO ---- */}
        <div className="sidebar-footer">
          <div className="avatar">
            {(user?.nome || "U").charAt(0).toUpperCase()}
          </div>
          <div>
            <div className="user-name">{user?.nome || "Usuário"}</div>
            <div className="user-email">{user?.email || "email@example.com"}</div>
          </div>
        </div>
      </aside>
    </>
  );
}
