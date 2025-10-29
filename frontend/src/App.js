// frontend/src/App.js
import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import ModelManagementPage from "./pages/ModelManagementPage";
import SettingsPage from "./pages/SettingsPage";
import CustomModelTraining from "./pages/TrainingPage";
import SqlTrainer from "./pages/SqlTrainingPage";
import OcrPage from "./pages/OcrPage";
import FileAnalyticsPage from "./pages/DataAnalysisPage";
import "./App.css";
import { Auth0Provider, useAuth0, withAuthenticationRequired } from "@auth0/auth0-react";

// ✅ Helper: Protected route wrapper
const ProtectedRoute = ({ component: Component }) => {
  const ComponentWithAuth = withAuthenticationRequired(Component, {
    onRedirecting: () => <div className="loading-screen">🔒 Checking Authentication...</div>,
  });
  return <ComponentWithAuth />;
};

// ✅ Header component
function Header({ userName, isAuthenticated, loginWithRedirect, logout, theme, setTheme, toggleSidebar }) {
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good Morning";
    if (hour < 18) return "Good Afternoon";
    return "Good Evening";
  };

  return (
    <header className="app-header">
      <button className="header-toggle-btn" onClick={toggleSidebar} aria-label="Toggle Sidebar">
        ☰
      </button>

      <div className="header-center">
        <h2>Imaginarium AI</h2>
      </div>

      <div className="header-right">
        {isAuthenticated ? (
          <>
            <span className="welcome-text">
              {getGreeting()}, {userName || "User"}
            </span>
            <button
              className="logout-btn"
              onClick={() =>
                logout({ logoutParams: { returnTo: window.location.origin } })
              }
            >
              Logout
            </button>
          </>
        ) : (
          <button className="login-btn" onClick={() => loginWithRedirect()}>
            Login
          </button>
        )}
      </div>
    </header>
  );
}

// ✅ Main App content
function AppContent() {
  const { user, loginWithRedirect, logout, isAuthenticated, isLoading } = useAuth0();
  const [theme, setTheme] = useState(() => localStorage.getItem("theme") || "dark");
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // Manage theme persistence
  useEffect(() => {
    document.body.classList.toggle("light-theme", theme === "light");
    localStorage.setItem("theme", theme);
  }, [theme]);

  if (isLoading) {
    return <div className="loading-screen">Loading user session...</div>;
  }

  return (
    <div className={`app-container ${theme}`}>
      <Header
        userName={user?.name}
        isAuthenticated={isAuthenticated}
        loginWithRedirect={loginWithRedirect}
        logout={logout}
        theme={theme}
        setTheme={setTheme}
        toggleSidebar={() => setIsSidebarOpen((prev) => !prev)}
      />

      <div className="main-layout">
        <Sidebar isOpen={isSidebarOpen} />
        <main className="main-content">
          <Routes>
            {/* ✅ Protected Routes */}
            <Route path="/" element={<ProtectedRoute component={ModelManagementPage} />} />
            <Route path="/models" element={<ProtectedRoute component={ModelManagementPage} />} />
            <Route path="/training" element={<ProtectedRoute component={CustomModelTraining} />} />
            <Route path="/sql-trainer" element={<ProtectedRoute component={SqlTrainer} />} />
            <Route path="/ocr" element={<ProtectedRoute component={OcrPage} />} />
            <Route path="/analysis" element={<ProtectedRoute component={FileAnalyticsPage} />} />
            <Route
              path="/settings"
              element={<ProtectedRoute component={() => <SettingsPage setTheme={setTheme} theme={theme} />} />}
            />
          </Routes>

          <footer className="app-footer">
            <p>
              © {new Date().getFullYear()} Custom AI Toolkit |{" "}
              <a href="/privacy">Privacy Policy</a> |{" "}
              <a href="/terms">Terms</a>
            </p>
          </footer>
        </main>
      </div>
    </div>
  );
}

// ✅ Wrap App in Auth0Provider
function App() {
  return (
    <Auth0Provider
      domain={process.env.REACT_APP_AUTH0_DOMAIN}
      clientId={process.env.REACT_APP_AUTH0_CLIENT_ID}
      authorizationParams={{
        redirect_uri: window.location.origin,
        audience: process.env.REACT_APP_AUTH0_AUDIENCE,
      }}
    >
      <Router>
        <AppContent />
      </Router>
    </Auth0Provider>
  );
}

export default App;
