// frontend/src/App.js
import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import ModelManagementPage from "./pages/ModelManagementPage";
import SettingsPage from "./pages/SettingsPage";
import AuthPage from "./pages/LoginPage";
import CustomModelTraining from "./pages/TrainingPage";
import SqlTrainer from "./pages/SqlTrainingPage";
import OcrPage from "./pages/OcrPage";
import FileAnalyticsPage from "./pages/DataAnalysisPage";
import "./App.css";

function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [userName, setUserName] = useState("Guest"); // You can dynamically fetch this from auth later

  // Load saved theme from localStorage
  useEffect(() => {
    const savedTheme = localStorage.getItem("theme") || "dark";
    setTheme(savedTheme);
    document.body.classList.toggle("light-theme", savedTheme === "light");
  }, []);

  // Save theme change
  useEffect(() => {
    localStorage.setItem("theme", theme);
    document.body.classList.toggle("light-theme", theme === "light");
  }, [theme]);


  //const YourWelcomeComponent = ({ userName }) => {

  // --- Add this logic ---
  const getGreeting = () => {
    const currentHour = new Date().getHours();

    if (currentHour < 12) {
      return "Good Morning"; // ☀️ Before 12 PM
    } else if (currentHour < 18) {
      return "Good Afternoon"; // 🌇 12 PM to 6 PM
    } else {
      return "Good Evening"; // 🌙 After 6 PM
    }
  };

  const greeting = getGreeting();

  return (
    <Router>
      <div className={`app-container ${theme}`}>
        {/* === HEADER SECTION === */}
        <header className="app-header">
          <button
            className="header-toggle-btn"
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            aria-label="Toggle Sidebar"
          >
            ☰
          </button>

          {/* <div className="header-right">
            <span className="welcome-text">Welcome, {userName}</span>
            <button className="logout-btn">Logout</button>
          </div> */}
          <div className="header-center">
            <h2>Imaginarium AI</h2>
          </div>
          <div className="header-right">
            <span className="welcome-text">{greeting}, {userName}</span>
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

        {/* === MAIN LAYOUT === */}
        <div className="main-layout">
          <Sidebar isOpen={isSidebarOpen} />

          <main className="main-content">
            <Routes>
              <Route path="/" element={<ModelManagementPage />} />
              <Route path="/models" element={<ModelManagementPage />} />
              <Route path="/settings" element={<SettingsPage setTheme={setTheme} theme={theme} />} />
              <Route path="/auth" element={<AuthPage  />} />
              <Route path="/training" element={<CustomModelTraining />} />
              <Route path="/sql-trainer" element={<SqlTrainer />} />
              <Route path="/ocr" element={<OcrPage />} />
              <Route path="/analysis" element={<FileAnalyticsPage />} />
            </Routes>

            {/* === GLOBAL FOOTER === */}
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

export default App;



        