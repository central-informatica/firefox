import React, { useState } from "react";
import Login from "./login";
import Dashboard from "./dashboard";

import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function App() {
  const [isLogged, setIsLogged] = useState(false);

  const handleLogin = () => setIsLogged(true);
  const handleLogout = () => setIsLogged(false);

  return (
    <>
      <div>
        {isLogged ? (
          <Dashboard onLogout={handleLogout} />
        ) : (
          <Login onLogin={handleLogin} />
        )}
      </div>
      <ToastContainer position="top-right" autoClose={3000} />
    </>
  );
}

export default App;
