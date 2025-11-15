import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/Navbar.css';

const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          Social Network
        </Link>

        {isAuthenticated ? (
          <div className="navbar-menu">
            <Link to="/" className="navbar-link">Home</Link>
            <Link to="/create" className="navbar-link">Create Post</Link>
            <Link to="/profile" className="navbar-link">Profile</Link>
            <div className="navbar-user">
              <span className="user-name">{user?.username}</span>
              <button onClick={handleLogout} className="logout-btn">
                Logout
              </button>
            </div>
          </div>
        ) : (
          <div className="navbar-menu">
            <Link to="/login" className="navbar-link">Login</Link>
            <Link to="/register" className="navbar-link">Register</Link>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
