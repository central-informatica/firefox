import React from "react";
import Sidebar from "../components/sidebar/Sidebar.jsx";
import { useSidebar } from "../contexts/SidebarContext";

export default function Layout({ children }) {
  const { expanded } = useSidebar();

  return (
    <div className="flex min-h-screen">
      <Sidebar />

      <main
        className={`
          flex-1 min-h-screen bg-gradient-to-br from-gray-50 to-gray-100
          transition-all duration-300 ease-in-out
          ${expanded ? 'md:ml-64' : 'md:ml-20'}
          ml-0
          p-5
          flex flex-col items-center
        `}
      >
        <div className="w-full max-w-[1400px]">
          {children}
        </div>
      </main>
    </div>
  );
}
