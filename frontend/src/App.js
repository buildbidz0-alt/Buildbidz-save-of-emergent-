import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import "./App.css";

// Components
import LandingPage from "./components/LandingPage";
import AuthPage from "./components/AuthPage";
import Dashboard from "./components/Dashboard";
import JobsPage from "./components/JobsPage";
import BidsPage from "./components/BidsPage";
import SubscriptionPage from "./components/SubscriptionPage";
import SettingsPage from "./components/SettingsPage";
import AboutPage from "./components/AboutPage";
import AdminDashboard from "./components/AdminDashboard";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
export const AuthContext = React.createContext();

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('buildbidzToken');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchProfile();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await axios.get(`${API}/profile`);
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      localStorage.removeItem('buildbidzToken');
      delete axios.defaults.headers.common['Authorization'];
    } finally {
      setLoading(false);
    }
  };

  const login = (token, userData) => {
    localStorage.setItem('buildbidzToken', token);
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('buildbidzToken');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  };

  const updateUser = (updatedUser) => {
    setUser(updatedUser);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, updateUser, API }}>
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={!user ? <LandingPage /> : <Navigate to="/dashboard" />} />
            <Route path="/auth" element={!user ? <AuthPage /> : <Navigate to="/dashboard" />} />
            <Route path="/about-us" element={<AboutPage />} />
            <Route path="/dashboard" element={user ? (
              user.role === 'admin' ? <AdminDashboard /> : <Dashboard />
            ) : <Navigate to="/" />} />
            <Route path="/jobs" element={user ? <JobsPage /> : <Navigate to="/" />} />
            <Route path="/bids" element={user ? <BidsPage /> : <Navigate to="/" />} />
            <Route path="/settings" element={user ? <SettingsPage /> : <Navigate to="/" />} />
            <Route 
              path="/subscription" 
              element={user && user.role === 'buyer' ? <SubscriptionPage /> : <Navigate to="/" />} 
            />
          </Routes>
        </BrowserRouter>
      </div>
    </AuthContext.Provider>
  );
}

export default App;