// frontend/src/components/Sidebar.js
import React from "react";
import { Link } from "react-router-dom";
import { FaKey, FaDatabase, FaFileCsv, FaImage, FaCog } from "react-icons/fa";
import { BsBoxes, BsTools } from "react-icons/bs";
import "./Sidebar.css";
import { NavLink } from 'react-router-dom';
import { useAuth0 } from "@auth0/auth0-react";

const Sidebar = ({ isOpen }) => {
  const { isAuthenticated } = useAuth0();

// const Sidebar = ({ isOpen }) => {
  return (
    <aside className={`sidebar ${isOpen ? "open" : "collapsed"}`}>
      <div className="sidebar-content">
        <h1 className="sidebar-title" style={{textAlign: "center" }}>AI Toolkit</h1>

        <NavLink to="/models">🧠 Model Hub</NavLink>
        {isAuthenticated && (
          <>
            <NavLink to="/training">⚙️ Custom Model Training</NavLink>
            <NavLink to="/sql-trainer">🗃 SQL Trainer</NavLink>
            <NavLink to="/analysis">📊 File Analytics</NavLink>
            <NavLink to="/ocr">🖼 Image OCR</NavLink>
            <NavLink to="/settings">⚙️ Settings</NavLink>
          </>
        )}
      </div>
    </aside>
  );
};

export default Sidebar;
