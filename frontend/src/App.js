// frontend/src/App.js
import React, { useState , useEffect} from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

// --- Import Icons ---
import { 
  FaKey, 
  FaDatabase, 
  FaFileCsv, 
  FaImage, 
  FaCog 
} from 'react-icons/fa';
import { BsBoxes, BsTools } from 'react-icons/bs';

// --- Import Pages ---
import LoginPage from './pages/LoginPage';
import ModelManagementPage from './pages/ModelManagementPage';
import TrainingPage from './pages/TrainingPage';
import SqlTrainingPage from './pages/SqlTrainingPage';
import DataAnalysisPage from './pages/DataAnalysisPage';
import OcrPage from './pages/OcrPage';
import SettingsPage from './pages/SettingsPage';
import ContactPage from './pages/ContactPage';
import PrivacyPage from './pages/PrivacyPage';
import DmcaPage from './pages/DmcaPage';
import TermsPage from './pages/TermsPage';
import FaqPage from './pages/FaqPage';
import CopyrightPage from './pages/CopyrightPage';
// --- Import Components ---
import ChatBubble from './components/ChatBubble';
import ChatWindow from './components/ChatWindow';
import Footer from './components/Footer';

// This component contains the main layout and uses hooks
function MainApp() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const { userEmail, logout } = useAuth();
  const navigate = useNavigate();

  // --- Styles ---
  // All styles are now in index.css except for these layout styles
  const appContainerStyles = { display: 'flex', flexDirection: 'column', minHeight: '100vh', fontFamily: 'sans-serif' };
  const mainLayoutStyles = { display: 'flex', flexGrow: 1, overflow: 'hidden' };
  const sidebarStyles = { width: '240px', background: 'var(--sidebar-background)', padding: '20px', borderRight: '1px solid var(--sidebar-border)', flexShrink: 0, overflowY: 'auto' };
  const contentStyles = { flexGrow: 1, padding: '20px 40px', overflowY: 'auto' };
  const headerStyles = { display: 'flex', justifyContent: 'flex-end', alignItems: 'center', padding: '10px 20px', background: 'var(--header-background)', borderBottom: '1px solid var(--header-border)', height: '40px' };
  const welcomeTextStyles = { marginRight: '15px', fontSize: '0.9em' };
  const logoutButtonStyles = { padding: '5px 10px', fontSize: '0.8em', cursor: 'pointer', background: '#dc3545', color: 'white', border: 'none', borderRadius: '4px' };
  
  // Apply theme on initial load
  useEffect(() => {
    const savedTheme = localStorage.getItem('appTheme') || 'light';
    document.body.classList.remove('light-theme', 'dark-theme');
    document.body.classList.add(savedTheme === 'dark' ? 'dark-theme' : 'light-theme');
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/auth');
  };

  return (
    <div style={appContainerStyles}>
      <div className="main-layout">
        <nav className="sidebar">
          <h1 style={{ marginBottom: '40px' }}>AI Toolkit</h1>
          
          {/* --- Sidebar Links CHANGED to include icons --- */}
          <Link to="/auth" className="sidebar-link">
            <FaKey /> <span>Authentication</span>
          </Link>
          <Link to="/models" className="sidebar-link">
            <BsBoxes /> <span>Model Hub</span>
          </Link>
          <Link to="/training" className="sidebar-link">
            <BsTools /> <span>Custom Model Training</span>
          </Link>
          <Link to="/sql-trainer" className="sidebar-link">
            <FaDatabase /> <span>SQL Trainer</span>
          </Link>
          <Link to="/analysis" className="sidebar-link">
            <FaFileCsv /> <span>File Analytics</span>
          </Link>
          <Link to="/ocr" className="sidebar-link">
            <FaImage /> <span>Image OCR</span>
          </Link>
          <Link to="/settings" className="sidebar-link">
            <FaCog /> <span>Settings</span>
          </Link>
        </nav>

        {/* Wrapper for Header + Main Content */}
        <div style={{ display: 'flex', flexDirection: 'column', flexGrow: 1, overflow: 'hidden' }}>
          {userEmail && (
            <div style={headerStyles}>
              <span style={welcomeTextStyles}>Welcome, {userEmail}!</span>
              <button onClick={handleLogout} style={logoutButtonStyles}>Logout</button>
            </div>
          )}
          <main className="content-area"> {/* Content Area */}
            <Routes>
              {/* Routes */}
              <Route path="/" element={<Navigate replace to="/auth" />} />
              <Route path="/auth" element={<LoginPage />} />
              <Route path="/models" element={<ModelManagementPage />} />
              <Route path="/training" element={<TrainingPage />} />
              <Route path="/sql-trainer" element={<SqlTrainingPage />} />
              <Route path="/analysis" element={<DataAnalysisPage />} />
              <Route path="/ocr" element={<OcrPage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/contact" element={<ContactPage />} />
              <Route path="/privacy" element={<PrivacyPage />} />
              <Route path="/dmca" element={<DmcaPage />} />
              <Route path="/terms" element={<TermsPage />} />
              <Route path="/faq" element={<FaqPage />} />
              <Route path="/copyright" element={<CopyrightPage />} />
              <Route path="*" element={<Navigate replace to="/auth" />} />
            </Routes>
          </main>
        </div>
      </div>

      {/* Chat Bubble & Window */}
      <ChatBubble onClick={() => setIsChatOpen(true)} />
      {isChatOpen && <ChatWindow onClose={() => setIsChatOpen(false)} />}

      <Footer />
    </div>
  );
}

// This is the main exported component that provides the Router context
function App() {
  return (
    <Router>
      <MainApp />
    </Router>
  );
}

export default App;