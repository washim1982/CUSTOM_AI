// frontend/src/App.js
import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Auth0Provider, useAuth0 } from "@auth0/auth0-react";
import Sidebar from "./components/Sidebar";
import ModelManagementPage from "./pages/ModelManagementPage";
import SettingsPage from "./pages/SettingsPage";
import AuthPage from "./pages/LoginPage";
import CustomModelTraining from "./pages/TrainingPage";
import SqlTrainer from "./pages/SqlTrainingPage";
import OcrPage from "./pages/OcrPage";
import FileAnalyticsPage from "./pages/DataAnalysisPage";
import "./App.css";
import { setAuthInterceptor } from "./services/api";

function AppContent() {
  const [theme, setTheme] = useState(() => localStorage.getItem("theme") || "dark");
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [userName, setUserName] = useState("Guest");

  const { user, isAuthenticated, logout, getAccessTokenSilently, loginWithRedirect } = useAuth0();

  // Setup token interceptor for API calls
  useEffect(() => {
    setAuthInterceptor(() => getAccessTokenSilently());
  }, [getAccessTokenSilently]);

  // Theme management
  useEffect(() => {
    const savedTheme = localStorage.getItem("theme") || "dark";
    setTheme(savedTheme);
    document.body.classList.toggle("light-theme", savedTheme === "light");
  }, []);

  useEffect(() => {
    localStorage.setItem("theme", theme);
    document.body.classList.toggle("light-theme", theme === "light");
  }, [theme]);

  // Greeting logic
  const getGreeting = () => {
    const currentHour = new Date().getHours();
    if (currentHour < 12) return "Good Morning";
    if (currentHour < 18) return "Good Afternoon";
    return "Good Evening";
  };

  const greeting = getGreeting();

  useEffect(() => {
    if (isAuthenticated && user) {
      setUserName(user.name || user.email || "User");
    } else {
      setUserName("Guest");
    }
  }, [isAuthenticated, user]);

  return (
    <Router>
      <div className={`app-container ${theme}`}>
        {/* === HEADER === */}
        <header className="app-header">
          <button
            className="header-toggle-btn"
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            aria-label="Toggle Sidebar"
          >
            ☰
          </button>

          <div className="header-center">
            <h2>Imaginarium AI</h2>
          </div>

          <div className="header-right">
            <span className="welcome-text">
              {greeting}, {userName}
            </span>

            {isAuthenticated ? (
              <button
                className="logout-btn"
                onClick={() =>
                  logout({ returnTo: window.location.origin })
                }
              >
                Logout
              </button>
            ) : (
              <button
                className="logout-btn"
                onClick={() => loginWithRedirect()}
              >
                Login
              </button>
            )}
          </div>
        </header>

        {/* === MAIN CONTENT === */}
        <div className="main-layout">
          <Sidebar isOpen={isSidebarOpen} />

          <main className="main-content">
            <Routes>
              <Route path="/" element={<ModelManagementPage />} />
              <Route path="/models" element={<ModelManagementPage />} />
              <Route
                path="/settings"
                element={<SettingsPage setTheme={setTheme} theme={theme} />}
              />
              <Route path="/auth" element={<AuthPage />} />
              <Route path="/training" element={<CustomModelTraining />} />
              <Route path="/sql-trainer" element={<SqlTrainer />} />
              <Route path="/ocr" element={<OcrPage />} />
              <Route path="/analysis" element={<FileAnalyticsPage />} />
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
    </Router>
  );
}

// === Root with Auth0Provider ===
function App() {
  const onRedirectCallback = (appState) => {
    window.history.replaceState(
      {},
      document.title,
      appState?.returnTo || window.location.pathname
    );
  };

  return (
    <Auth0Provider
      domain={process.env.REACT_APP_AUTH0_DOMAIN}
      clientId={process.env.REACT_APP_AUTH0_CLIENT_ID}
      authorizationParams={{
        redirect_uri: window.location.origin,
        audience: process.env.REACT_APP_AUTH0_AUDIENCE,
      }}
      onRedirectCallback={onRedirectCallback}
    >
      <AppContent />
    </Auth0Provider>
  );
}

export default App;
