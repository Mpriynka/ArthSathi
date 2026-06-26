import React, { useState } from 'react';
import { Sparkles, ArrowRight, CheckCircle2 } from 'lucide-react';

export default function Onboarding({ onOnboardComplete }) {
  const [formData, setFormData] = useState({
    userId: 'usr_' + Math.random().toString(36).substring(2, 9),
    name: '',
    language: 'Hindi',
    primaryIncome: 'Salaried',
    incomeFrequency: 'Monthly',
    monthlyIncome: '',
    urgentExpenses: '',
    savingsHabit: 'Sometimes',
    hasEmergencyFund: 'No',
    hasDebt: 'No',
    primaryGoal: 'Build emergency fund',
    selfRating: 3
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name || !formData.monthlyIncome || !formData.urgentExpenses) {
      setError('Please fill in all required fields.');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('http://127.0.0.1:8000/api/onboard', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          monthlyIncome: parseInt(formData.monthlyIncome, 10),
          urgentExpenses: parseInt(formData.urgentExpenses, 10),
          selfRating: parseInt(formData.selfRating, 10)
        }),
      });
      
      if (!response.ok) {
        throw new Error('Onboarding failed. Please make sure the backend is running.');
      }
      
      const data = await response.json();
      if (data.status === 'success') {
        onOnboardComplete(data.profile);
      } else {
        setError('Error completing onboarding.');
      }
    } catch (err) {
      setError(err.message || 'Server error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="onboard-page">
      <div className="onboard-card">
        <div className="onboard-header">
          <h1 className="onboard-title">Welcome to ChillarSeedhi</h1>
          <p className="onboard-subtitle">Different lives, different starting points. Tell us about your journey, and let's find your step to stability.</p>
        </div>
        
        {error && (
          <div style={{ backgroundColor: '#ffebee', color: '#c62828', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem', fontWeight: '500', border: '1px solid #ffcdd2' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <label>Your Name *</label>
              <input 
                type="text" 
                name="name" 
                value={formData.name} 
                onChange={handleChange} 
                placeholder="Ramesh K." 
                required 
              />
            </div>
            
            <div className="form-group">
              <label>Preferred Language *</label>
              <select name="language" value={formData.language} onChange={handleChange}>
                <option value="Hindi">हिंदी (Hindi)</option>
                <option value="Hinglish">Hinglish (Hindi with English text)</option>
                <option value="English">English</option>
                <option value="Kannada">ಕನ್ನಡ (Kannada)</option>
                <option value="Tamil">தமிழ் (Tamil)</option>
                <option value="Marathi">मराठी (Marathi)</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>What is your primary income source? *</label>
              <select name="primaryIncome" value={formData.primaryIncome} onChange={handleChange}>
                <option value="Salaried">Salaried (nurses, office staff, teachers)</option>
                <option value="Gig Worker">Gig Worker (delivery, drivers, freelancers)</option>
                <option value="Daily Wager">Daily Wager (laborers, helpers, cleaners)</option>
                <option value="Shop Owner">Small Business / Shop Owner</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>How often do you get paid? *</label>
              <select name="incomeFrequency" value={formData.incomeFrequency} onChange={handleChange}>
                <option value="Monthly">Monthly</option>
                <option value="Weekly">Weekly</option>
                <option value="Daily">Daily / Irregular</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>Total Monthly Income (₹) *</label>
              <input 
                type="number" 
                name="monthlyIncome" 
                value={formData.monthlyIncome} 
                onChange={handleChange} 
                placeholder="25000" 
                required 
              />
            </div>
            
            <div className="form-group">
              <label>Urgent Monthly Expenses (₹) *</label>
              <input 
                type="number" 
                name="urgentExpenses" 
                value={formData.urgentExpenses} 
                onChange={handleChange} 
                placeholder="15000" 
                required 
              />
            </div>
            
            <div className="form-group">
              <label>Do you save money? *</label>
              <select name="savingsHabit" value={formData.savingsHabit} onChange={handleChange}>
                <option value="Regularly">Yes, regularly every week/month</option>
                <option value="Sometimes">Sometimes, when there is extra cash</option>
                <option value="Never">No, it is hard to save anything</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>Do you have an emergency fund? *</label>
              <select name="hasEmergencyFund" value={formData.hasEmergencyFund} onChange={handleChange}>
                <option value="No">No emergency savings</option>
                <option value="Partial">Yes, equivalent to 1 month of expense</option>
                <option value="Complete">Yes, equivalent to 3+ months of expense</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>Do you have active loans or EMI pressure? *</label>
              <select name="hasDebt" value={formData.hasDebt} onChange={handleChange}>
                <option value="No">No active loans</option>
                <option value="Low pressure">Yes, small EMIs that I pay comfortably</option>
                <option value="Stressed">Yes, high debt pressure or loan apps stress</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>What is your primary financial goal? *</label>
              <select name="primaryGoal" value={formData.primaryGoal} onChange={handleChange}>
                <option value="Daily survival mapping">Track money in vs out (Survival Map)</option>
                <option value="Build emergency fund">Build emergency fund (Safety Net)</option>
                <option value="Clear active loans">Pay off active loans & EMIs</option>
                <option value="Start saving habits">Start micro-savings habit</option>
                <option value="Invest in formal schemes">Invest in PPF, SIP, RD</option>
                <option value="Retirement & wealth">Retirement & wealth growth</option>
              </select>
            </div>
            
            <div className="form-group full-width">
              <label>How confidently do you manage your money? (1 = Struggling, 5 = Very Confident) *</label>
              <input 
                type="range" 
                name="selfRating" 
                min="1" 
                max="5" 
                value={formData.selfRating} 
                onChange={handleChange} 
                style={{ cursor: 'pointer' }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--color-text-muted)', fontWeight: '500' }}>
                <span>1 (Struggling daily)</span>
                <span>3 (Somewhat okay)</span>
                <span>5 (Very confident)</span>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
            <button 
              type="submit" 
              className="btn btn-primary" 
              disabled={loading}
            >
              {loading ? 'Analyzing Profile...' : 'Begin Financial Assessment'}
              {!loading && <ArrowRight size={18} />}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
