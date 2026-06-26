import React, { useState, useEffect } from 'react';
import { Leaf, Award, Shield, User } from 'lucide-react';
import Onboarding from './components/Onboarding';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  const [profile, setProfile] = useState(null);

  // Attempt to auto-load guest profile if it exists (for testing persistency)
  useEffect(() => {
    const fetchGuestProfile = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8000/api/profile/usr_guest');
        if (res.ok) {
          const data = await res.json();
          // If the profile has been assessed (i.e. has a name other than default or level history populated)
          if (data && data.chatHistory && data.chatHistory.length > 0) {
            setProfile(data);
          }
        }
      } catch (e) {
        // Backend not running yet or connection refused; fail silently in UI
      }
    };
    fetchGuestProfile();
  }, []);

  const handleProfileUpdate = (updatedProfile) => {
    setProfile(updatedProfile);
  };

  const handleReset = () => {
    setProfile(null);
  };

  return (
    <div className="app-container">
      {/* Top Navbar */}
      <header className="navbar">
        <div className="logo-container">
          <Leaf className="logo-leaf" fill="var(--color-success)" stroke="none" />
          <div>
            <span className="logo-text">ChillarSeedhi</span>
            <span className="logo-sub">The Adaptive Financial Capability Ladder</span>
          </div>
        </div>
        
        <div className="nav-links">
          <span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Shield size={14} color="var(--color-primary)" /> RBI Guideline Aligned
          </span>
        </div>

        <div className="nav-actions">
          {profile ? (
            <div className="user-badge">
              <User size={14} />
              <span>{profile.persona?.name || 'Guest'} (L{profile.seedhiLevel})</span>
            </div>
          ) : (
            <div className="user-badge" style={{ fontStyle: 'italic', opacity: 0.8 }}>
              Guest Session
            </div>
          )}
        </div>
      </header>

      {/* Main Content Area */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {profile ? (
          <Dashboard 
            profile={profile} 
            onProfileUpdate={handleProfileUpdate} 
            onReset={handleReset} 
          />
        ) : (
          <Onboarding 
            onOnboardComplete={handleProfileUpdate} 
          />
        )}
      </main>

      {/* Footer */}
      <footer style={{ textAlign: 'center', padding: '1rem', borderTop: '1px solid var(--color-border)', backgroundColor: 'var(--color-bg-card)', fontSize: '0.75rem', color: 'var(--color-text-muted)', fontWeight: 500 }}>
        © 2026 ChillarSeedhi. Built by Team Shell (Nomura Kakushin). Bank-grade Security • Made for Bharat.
      </footer>
    </div>
  );
}

export default App;
