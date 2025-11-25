import React from "react";
import Sidebar from "../components/Sidebar/Sidebar";
import "./MainLayout.css";

export default function MainLayout({ children }) {
  return (
    <div className="layout-container">
      <Sidebar />
      <main className="layout-content">{children}</main>
    </div>
  );
}
