import React from "react";
import Sidebar from "../components/Sidebar/Sidebar";
import "./MainLayout.css";

export default function Layout({ children }) {
  return (
    <div className="layout">
      <Sidebar />

      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
