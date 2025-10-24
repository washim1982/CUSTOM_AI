// frontend/src/components/Footer.js
import React from 'react';
import { Link } from 'react-router-dom'; // Import Link for navigation

function Footer() {
  return (
    <footer className="app-footer">
      <Link to="/contact" className="footer-link">Contact Us</Link>
      <span className="footer-separator">|</span>
      <Link to="/privacy" className="footer-link">Privacy Policy</Link>
      <span className="footer-separator">|</span>
      <Link to="/dmca" className="footer-link">DMCA</Link>
      <span className="footer-separator">|</span>
      <Link to="/terms" className="footer-link">Terms and Conditions</Link>
      <span className="footer-separator">|</span>
      <Link to="/settings" className="footer-link">Settings</Link>
      <span className="footer-separator">|</span>
      <Link to="/faq" className="footer-link">Questions</Link>
      <span className="footer-separator">|</span>
      {/* Link to Auth page for registration */}
      <Link to="/auth" className="footer-link">No account? Create one for free!</Link>
      <span className="footer-separator">|</span>
      {/* Link to training page */}
      <Link to="/training" className="footer-link">Download/Create Models</Link>
      <span className="footer-separator">|</span>
      <Link to="/copyright" className="footer-link">Copyright</Link>
    </footer>
  );
}

export default Footer;