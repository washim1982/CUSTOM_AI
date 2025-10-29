// frontend/src/pages/SettingsPage.js
import React, { useState, useEffect } from 'react';
import { listLoras, uploadLora, downloadLora } from '../services/api';

// Reusable Section Component
const SettingsSection = ({ title, children }) => (
  <div style={{
    marginBottom: '30px',
    padding: '20px',
    border: '1px solid var(--box-border)',
    borderRadius: '8px',
    background: 'var(--box-background)'
  }}>
    <h3 style={{
      marginTop: '0',
      borderBottom: '1px solid var(--sidebar-border)',
      paddingBottom: '10px',
      marginBottom: '20px'
    }}>
      {title}
    </h3>
    {children}
  </div>
);

function SettingsPage() {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [loras, setLoras] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState({ message: '', type: '' });
  const [theme, setTheme] = useState(localStorage.getItem('appTheme') || 'light'); 
  
  useEffect(() => {
    document.body.classList.remove('light-theme', 'dark-theme');
    document.body.classList.add(theme === 'dark' ? 'dark-theme' : 'light-theme');
    document.body.classList.toggle('light-theme', theme === 'light');
    localStorage.setItem('appTheme', theme);
    fetchLoras();
  }, [theme]);

  const fetchLoras = () => {
    listLoras()
      .then(res => setLoras(res.data))
      .catch(err => console.error("Error fetching LoRAs:", err));
  };

  const handlePasswordChange = (event) => {
    event.preventDefault();
    console.log('Changing password...');
    alert('Password change functionality not yet implemented.');
  };

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = () => {
    if (!selectedFile) {
      alert("Please select a LoRA file to upload.");
      return;
    }
    setIsUploading(true);
    setUploadStatus({ message: '', type: '' });

    const formData = new FormData();
    formData.append('file', selectedFile);

    uploadLora(formData)
      .then(res => {
        setUploadStatus({ message: `Successfully uploaded ${res.data.filename}`, type: 'success' });
        fetchLoras();
        setSelectedFile(null);
      })
      .catch(err => {
        setUploadStatus({ message: `Upload failed: ${err.response?.data?.detail || 'Server error'}`, type: 'error' });
      })
      .finally(() => setIsUploading(false));
  };

  return (
    <div className="page-content" style={{ maxWidth: '700px' }}>
      <h2>Settings</h2>

      <SettingsSection title="User Profile">
        <form onSubmit={handlePasswordChange} className="form-layout">
          <div className="form-group">
            <label htmlFor="current-password">Current Password:</label>
            <input
              id="current-password"
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              className="form-input"
              placeholder="Enter current password"
            />
          </div>
          <div className="form-group">
            <label htmlFor="new-password">New Password:</label>
            <input
              id="new-password"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="form-input"
              placeholder="Enter new password"
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ alignSelf: 'flex-start' }}>Update Password</button>
        </form>
      </SettingsSection>

      <SettingsSection title="Appearance">
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          <label className="form-label">Theme:</label>
          <div style={{ display: 'flex', gap: '10px' }}>
            <input
              type="radio"
              id="light-theme"
              name="theme"
              value="light"
              checked={theme === 'light'}
              onChange={() => setTheme('light')}
            />
            <label htmlFor="light-theme">Light</label>
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <input
              type="radio"
              id="dark-theme"
              name="theme"
              value="dark"
              checked={theme === 'dark'}
              onChange={() => setTheme('dark')}
            />
            <label htmlFor="dark-theme">Dark</label>
          </div>
        </div>
      </SettingsSection>
    
      <SettingsSection title="LoRA Adapters">
        <h4>Available Adapters</h4>
        {loras.length > 0 ? (
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {loras.map(lora => (
              <li key={lora} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid var(--sidebar-border)' }}>
                <span>{lora}</span>
                <a href={downloadLora(lora)} download className="footer-link">Download</a>
              </li>
            ))}
          </ul>
        ) : (
          <p>No LoRA adapters found.</p>
        )}

        <h4 style={{ marginTop: '30px' }}>Upload New Adapter</h4>
         <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <input type="file" onChange={handleFileChange} accept=".safetensors,.bin,.pt" className="form-input" style={{ flex: 1 }} />
            <button onClick={handleUpload} disabled={isUploading || !selectedFile} className="btn btn-primary">
                {isUploading ? 'Uploading...' : 'Upload'}
            </button>
         </div>
         {uploadStatus.message && (
            <p className={`status-message ${uploadStatus.type === 'success' ? 'status-success' : 'status-error'}`}>
              {uploadStatus.message}
            </p>
         )}
      </SettingsSection>
    </div>
  );
}

export default SettingsPage;