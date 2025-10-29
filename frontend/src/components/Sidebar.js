// frontend/src/components/Sidebar.js
import React from "react";
import { Link } from "react-router-dom";
import { FaKey, FaDatabase, FaFileCsv, FaImage, FaCog } from "react-icons/fa";
import { BsBoxes, BsTools } from "react-icons/bs";
import "./Sidebar.css";

const Sidebar = ({ isOpen }) => {
  return (
    <aside className={`sidebar ${isOpen ? "open" : "collapsed"}`}>
      <div className="sidebar-inner">
        <h1 className="sidebar-title" style={{textAlign: "center" }}yle>AI Toolkit</h1>

        <nav className="sidebar-links">

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
      </div>
    </aside>
  );
};

export default Sidebar;
