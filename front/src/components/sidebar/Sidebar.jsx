import React, { useState } from "react";
import "./Sidebar.css";
import { 
  FiGrid, 
  FiUsers, 
  FiGitPullRequest, 
  FiSettings, 
  FiFigma,
  FiFeather,
  FiLifeBuoy,
  FiCast,
  FiCreditCard
} from "react-icons/fi";
import { useNavigate } from "react-router-dom";

export default function Sidebar() {
  const [active, setActive] = useState("dashboard");
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  const menuItems = [
    { id: "dashboard", label: "Dashboard", icon: <FiGrid />, path: "/dashboard" },
    { id: "empresas", label: "Empresas", icon: <FiLifeBuoy />, path: "/empresas" },  
    { id: "usuarios", label: "Usuários", icon: <FiUsers />, path: "/usuarios" },
    { id: "cedrtificados", label: "Certificados", icon: <FiCreditCard />, path: "/certificados" },
    { id: "config", label: "Configurações", icon: <FiSettings />, path: "/config" },
  ];

  const toggleSidebar = () => setOpen(!open);

  return (
    <>
      {/* Botão Mobile */}
      <button className="sidebar-toggle" onClick={toggleSidebar}>
        ☰
      </button>

      {open && <div className="sidebar-overlay" onClick={() => setOpen(false)} />}

      <aside className={`sidebar ${open ? "open" : ""}`}>
        
        <div className="sidebar-title">Certi Pro</div>

        <nav className="sidebar-menu">
          {menuItems.map((item) => (
            <div
              key={item.id}
              className={`menu-item ${active === item.id ? "active" : ""}`}
              onClick={() => {
                setActive(item.id);
                navigate(item.path);     // ✔ NAVEGAÇÃO REALIZADA
                setOpen(false);
              }}
            >
              <span className="icon">{item.icon}</span>
              <span className="label">{item.label}</span>
            </div>
          ))}
        </nav>

        {/* Perfil fixo */}
        <div className="sidebar-footer">
          <div className="avatar">F</div>
          <div>
            <div className="user-name">fabricio_developer</div>
            <div className="user-email">fabricio@centranet.com.br</div>
          </div>
        </div>
      </aside>
    </>
  );
}
