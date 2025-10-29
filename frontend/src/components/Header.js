import React from 'react';
import './Header.css';

const Header = () => {
  const userEmail = localStorage.getItem('userEmail') || 'guest@example.com';

  const handleLogout = () => {
    //localStorage.clear();
    // Clear local storage and session data
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    sessionStorage.clear();

    // Optional: Clear cookies if used
    document.cookie.split(";").forEach((c) => {
      document.cookie = c
        .replace(/^ +/, "")
        .replace(/=.*/, `=;expires=${new Date().toUTCString()};path=/`);
    });
    window.location.href = '/auth';
  };
  
  return (
    <header className="app-header">
      <aside className={`sidebar-container ${isOpen ? "expanded" : "collapsed"}`}></aside>
      <div className="header-left">
        {/* Toggle Button - always visible */}
        <button
          className={`toggle-btn ${isOpen ? "open" : ""}`}
          onClick={() => setIsOpen(!isOpen)}
          title={isOpen ? "Collapse" : "Expand"}
        >
          <FaBars />
        </button>
        <h2>good morning, {userEmail}</h2>
      </div>
       <div className="header-center">
        <h2>Imaginarium AI</h2>
      </div>
      <div className="header-right">
        <button
          className="logout-btn"
          onClick={() => {
            // Clear local storage and session data
            localStorage.removeItem("token");
            localStorage.removeItem("user");
            sessionStorage.clear();

            // Optional: Clear cookies if used
            document.cookie.split(";").forEach((c) => {
              document.cookie = c
                .replace(/^ +/, "")
                .replace(/=.*/, `=;expires=${new Date().toUTCString()};path=/`);
            });

            // Redirect to login page
            window.location.href = "/auth";
          }}
        >
          Logout
        </button>
      </div>
    </header>
  );
};

export default Header;
