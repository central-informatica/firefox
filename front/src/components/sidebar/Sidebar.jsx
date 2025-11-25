import React, { useState } from "react";
import "./Sidebar.css";
import { 
  FiGrid, 
  FiUsers, 
  FiGitPullRequest, 
  FiSettings 
} from "react-icons/fi";

export default function Sidebar() {
  const [active, setActive] = useState("dashboard");
  const [open, setOpen] = useState(false);

  const menuItems = [
    { id: "dashboard", label: "Dashboard", icon: <FiGrid /> },
    { id: "empresas", label: "Empresas", icon: <FiUsers /> },
    { id: "funcionarios", label: "Funcionarios", icon: <FiGitPullRequest /> },
    { id: "config", label: "Configurações", icon: <FiSettings /> },
  ];

  const toggleSidebar = () => setOpen(!open);

  return (
    <>
      {/* Botão Mobile */}
      <button className="sidebar-toggle" onClick={toggleSidebar}>
        ☰
      </button>

      {/* Overlay mobile */}
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
