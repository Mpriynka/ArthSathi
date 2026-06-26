import React, { useState } from 'react';
import { 
  Plus, Calendar, Flame, Target, Trash2, ArrowUpRight, 
  TrendingUp, ShieldAlert, Award, Calculator, BookOpen, AlertTriangle
} from 'lucide-react';
import VoiceChat from './VoiceChat';

export default function Dashboard({ profile, onProfileUpdate, onReset }) {
  const [trackerInput, setTrackerInput] = useState({ amount: '', type: 'out', category: 'Food', description: '' });
  const [jarDistribution, setJarDistribution] = useState({ school: 0, emergency: 0 });
  const [tempGoal, setTempGoal] = useState({ type: 'emergency', target: 20000, current: 5000 });
  const [loanCalc, setLoanCalc] = useState({ amount: 10000, bankRate: 12, lenderRate: 5 }); // 5% per month
  const [budgetSplit, setBudgetSplit] = useState({ needs: 50, savings: 30, freedom: 20 });
  const [assetAllocation, setAssetAllocation] = useState({ equity: 40, debt: 30, cash: 20, gold: 10 });
  
  const level = profile?.seedhiLevel ?? 0;
  
  // Safe import helper since we are in React client context and config might be deep
  const levelInfo = {
    0: {
      name: "Survival Map",
      description: "Focus on mapping cash flow, logging transactions, and protecting ₹20-₹50 daily.",
      allowed: ["Money tracking", "Daily safety reserves", "Debt trap safety"],
      blocked: ["Mutual funds", "Stock market", "PPF/SIP accounts", "Retirement portfolios"]
    },
    1: {
      name: "First Savings Habit",
      description: "Build consistency, maintain a savings streak, and allocate coins to visual Goal Jars.",
      allowed: ["Daily savings streak", "Goal pockets/jars", "Micro-savings habit"],
      blocked: ["Stock trading", "Equity funds", "Advanced tax planning"]
    },
    2: {
      name: "Safety Net",
      description: "Assemble a liquid cash reserve covering 3 months of essential bills, and review health coverage.",
      allowed: ["Emergency fund building", "Health insurance", "Liquid buffer cash"],
      blocked: ["Long-term locking assets", "Trading", "High-risk index funds"]
    },
    3: {
      name: "Debt Safety & Protection",
      description: "Compare interest costs, reduce EMIs, pay down expensive loans first, and avoid trap apps.",
      allowed: ["Loan cost comparison", "Debt snowball method", "EMI restructuring"],
      blocked: ["Discretionary investments", "Mutual funds", "High-yield locking schemes"]
    },
    4: {
      name: "Formal Savings & Goal Planning",
      description: "Automate Recurring Deposits, open a PPF, configure small SIPs, and plan goal budgets.",
      allowed: ["PPF and RD accounts", "Systematic Investment Plans", "Needs-Savings-Freedom splits"],
      blocked: ["Day trading", "Leveraged products", "Cryptocurrency speculations"]
    },
    5: {
      name: "Financial Stability & Wealth Growth",
      description: "Build retirement corpuses, diversify portfolios across assets, and optimize tax savings.",
      allowed: ["Equity index funds", "Portfolio allocation", "Tax optimization (ELSS)"],
      blocked: ["Speculative margin trading", "High-leverage options"]
    }
  };

  const activeLevel = levelInfo[level] || levelInfo[0];

  // Call Tracker API
  const handleAddTransaction = async (e) => {
    e.preventDefault();
    if (!trackerInput.amount) return;

    try {
      const response = await fetch('http://127.0.0.1:8000/api/tracker', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: profile.userId,
          amount: parseInt(trackerInput.amount, 10),
          type: trackerInput.type,
          category: trackerInput.category,
          description: trackerInput.description
        })
      });
      const data = await response.json();
      onProfileUpdate(data.profile);
      setTrackerInput({ amount: '', type: 'out', category: 'Food', description: '' });
    } catch (err) {
      alert('Error updating transactions');
    }
  };

  // Call Streak API
  const handleStreakCheckIn = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/streaks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: profile.userId,
          amountSavedToday: 20 // Default small micro-saving amount
        })
      });
      const data = await response.json();
      onProfileUpdate(data.profile);
    } catch (err) {
      alert('Error marking streak');
    }
  };

  // Call Goal update API
  const handleSaveGoal = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/goals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: profile.userId,
          type: tempGoal.type,
          target: parseInt(tempGoal.target, 10),
          current: parseInt(tempGoal.current, 10)
        })
      });
      const data = await response.json();
      onProfileUpdate(data.profile);
      alert('Goal saved successfully!');
    } catch (err) {
      alert('Error updating goals');
    }
  };

  // Helper: compute total cash reserve for L0
  const computeCashReserve = () => {
    let total = 0;
    const logs = profile.dailyTrackerLogs || [];
    logs.forEach(log => {
      if (log.type === 'in') total += log.amount;
      else total -= log.amount;
    });
    return total;
  };

  // Render score circle gauge
  const renderGauge = (label, score, color) => {
    const radius = 35;
    const stroke = 6;
    const normalizedRadius = radius - stroke * 2;
    const circumference = normalizedRadius * 2 * Math.PI;
    const strokeDashoffset = circumference - (score / 100) * circumference;

    return (
      <div className="metric-gauge-wrapper">
        <div className="metric-header">
          <span>{label}</span>
          <span style={{ color }}>{score}/100</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginTop: '0.5rem' }}>
          <svg height={radius * 2} width={radius * 2}>
            <circle
              stroke="#e6dfd5"
              fill="transparent"
              strokeWidth={stroke}
              r={normalizedRadius}
              cx={radius}
              cy={radius}
            />
            <circle
              stroke={color}
              fill="transparent"
              strokeWidth={stroke}
              strokeDasharray={circumference + ' ' + circumference}
              style={{ strokeDashoffset, transform: 'rotate(-90deg)', transformOrigin: '50% 50%', transition: 'stroke-dashoffset 0.8s ease' }}
              r={normalizedRadius}
              cx={radius}
              cy={radius}
            />
          </svg>
          <div className="metric-value" style={{ color }}>
            {score >= 70 ? 'Good' : score >= 40 ? 'Moderate' : 'Caution'}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="dashboard-page">
      {/* Banner / Header */}
      <div className="level-header-card">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 600, color: 'var(--color-secondary)' }}>
              Nomura Kakushin • Team Shell
            </span>
          </div>
          <h2 style={{ color: 'white', fontSize: '1.8rem', marginTop: '0.2rem' }}>
            Level {level}: {activeLevel.name}
          </h2>
          <p style={{ color: '#d0dfd8', fontSize: '0.9rem', maxWidth: '600px', marginTop: '0.2rem' }}>
            {activeLevel.description}
          </p>
          
          <div className="level-tag-container">
            <span style={{ color: '#d0dfd8', fontSize: '0.8rem', fontWeight: 600, alignSelf: 'center', marginRight: '0.25rem' }}>Focus Topics:</span>
            {activeLevel.allowed.map((t, i) => (
              <span key={i} className="tag tag-allowed">{t}</span>
            ))}
            <span style={{ color: '#d0dfd8', fontSize: '0.8rem', fontWeight: 600, alignSelf: 'center', marginLeft: '0.5rem', marginRight: '0.25rem' }}>Safety Blocks:</span>
            {activeLevel.blocked.map((t, i) => (
              <span key={i} className="tag tag-blocked">{t}</span>
            ))}
          </div>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', alignItems: 'flex-end' }}>
          <div className="level-badge-large">
            <span className="level-badge-lbl">Seedhi Step</span>
            <span>L{level}</span>
          </div>
          <button className="btn btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.75rem', borderRadius: '4px' }} onClick={onReset}>
            Recalculate Level
          </button>
        </div>
      </div>

      {/* Main Grid */}
      <div className="dashboard-grid">
        {/* Left Side: Score & Persona */}
        <div className="sidebar-card">
          <h3 style={{ fontSize: '1.1rem', borderBottom: '1px solid var(--color-border)', paddingBottom: '0.5rem' }}>
            Financial Readiness Profile
          </h3>
          
          {renderGauge('Readiness Score', profile.readinessScore || 30, 'var(--color-success)')}
          {renderGauge('Accidental Risk', profile.riskScore || 70, '#f57c00')}
          {renderGauge('Urgency Pressure', profile.urgencyScore || 40, 'var(--color-accent)')}

          <div className="metrics-section" style={{ borderTop: '1px solid var(--color-border)', paddingTop: '1rem' }}>
            <h4 style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Extracted Signals</h4>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 500 }}>
              <span style={{ color: 'var(--color-text-muted)' }}>Income Flow:</span>
              <span style={{ color: 'var(--color-primary)', fontWeight: 600 }}>
                {profile.persona?.incomePattern === 'monthly_salaried' ? 'Stable Monthly' : 'Variable/Irregular'}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 500 }}>
              <span style={{ color: 'var(--color-text-muted)' }}>Savings habit:</span>
              <span style={{ color: 'var(--color-primary)', fontWeight: 600 }}>{profile.savingsHabit || 'None'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 500 }}>
              <span style={{ color: 'var(--color-text-muted)' }}>Emergency fund:</span>
              <span style={{ color: 'var(--color-primary)', fontWeight: 600 }}>{profile.emergencyFundStatus || 'None'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 500 }}>
              <span style={{ color: 'var(--color-text-muted)' }}>Debt pressure:</span>
              <span style={{ color: 'var(--color-primary)', fontWeight: 600 }}>{profile.debtStatus || 'None'}</span>
            </div>
          </div>
        </div>

        {/* Middle Side: Adaptable Level Tools */}
        <div className="workspace-card">
          {level === 0 && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h3 style={{ fontSize: '1.4rem' }}>Level 0: Daily Money Tracker</h3>
                <div style={{ backgroundColor: '#e8f5e9', padding: '0.5rem 1rem', borderRadius: '8px', border: '1px solid #c8e6c9' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', display: 'block', fontWeight: 500 }}>Available Cash Envelope</span>
                  <strong style={{ fontSize: '1.2rem', color: 'var(--color-success)', fontFamily: 'var(--font-heading)' }}>
                    ₹{computeCashReserve()}
                  </strong>
                </div>
              </div>
              
              <p style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem', marginBottom: '1rem' }}>
                Rule: Track every single rupee in and out. Secure ₹20 to ₹50 daily. Avoid unverified phone loan apps.
              </p>

              <form onSubmit={handleAddTransaction} className="tracker-form">
                <div className="form-group">
                  <label>Amount (₹)</label>
                  <input 
                    type="number" 
                    value={trackerInput.amount} 
                    onChange={e => setTrackerInput(prev => ({ ...prev, amount: e.target.value }))}
                    placeholder="150" 
                    required 
                  />
                </div>
                <div className="form-group">
                  <label>Type</label>
                  <select value={trackerInput.type} onChange={e => setTrackerInput(prev => ({ ...prev, type: e.target.value }))}>
                    <option value="out">Money Out (Expense)</option>
                    <option value="in">Money In (Income)</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Category</label>
                  <select value={trackerInput.category} onChange={e => setTrackerInput(prev => ({ ...prev, category: e.target.value }))}>
                    <option value="Food">Food / Groceries</option>
                    <option value="Rent">Rent / Room</option>
                    <option value="Travel">Auto / Travel</option>
                    <option value="Salary">Earnings / Wages</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
                <button type="submit" className="btn btn-primary" style={{ padding: '0.8rem 1.2rem' }}>
                  <Plus size={18} />
                </button>
              </form>

              <h4 style={{ fontSize: '1rem', marginBottom: '0.5rem', color: 'var(--color-primary)' }}>Daily Transaction Logs</h4>
              <div className="tracker-list">
                {(!profile.dailyTrackerLogs || profile.dailyTrackerLogs.length === 0) ? (
                  <p style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem', fontStyle: 'italic', textAlign: 'center', padding: '1rem' }}>
                    No logs entered today. Add some transactions above or tell ChillarSaathi to log them!
                  </p>
                ) : (
                  profile.dailyTrackerLogs.map((log, idx) => (
                    <div key={log.id || idx} className="tracker-item">
                      <div>
                        <strong style={{ fontSize: '0.9rem' }}>{log.category}</strong>
                        {log.description && <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginLeft: '0.5rem' }}>({log.description})</span>}
                        <span style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)', display: 'block' }}>{log.date}</span>
                      </div>
                      <span className={`tracker-amount ${log.type === 'in' ? 'amount-in' : 'amount-out'}`}>
                        {log.type === 'in' ? '+' : '-'} ₹{log.amount}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {level === 1 && (
            <div>
              <h3 style={{ fontSize: '1.4rem', marginBottom: '1rem' }}>Level 1: Micro-savings & Streaks</h3>
              
              <div className="streak-header">
                <p style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem', maxWidth: '300px' }}>
                  Save tiny amounts (even ₹10) daily to build a savings streak calendar. Avoid high-risk schemes.
                </p>
                <div className="streak-count-box">
                  <Flame size={20} fill="#ff9100" stroke="none" />
                  <span>{profile.streaks?.streakCount || 0} Day Streak</span>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
                <button className="btn btn-primary" onClick={handleStreakCheckIn}>
                  <Flame size={16} /> I Saved Money Today! (₹20)
                </button>
              </div>

              <h4 style={{ fontSize: '1rem', color: 'var(--color-primary)', marginBottom: '0.5rem' }}>Streak Calendar (June 2026)</h4>
              <div className="calendar-grid">
                {/* Headers */}
                {['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((d, i) => (
                  <div key={i} className="calendar-day-header">{d}</div>
                ))}
                {/* Basic calendar cells representation */}
                {Array.from({ length: 30 }, (_, i) => {
                  const dayNum = i + 1;
                  const dateStr = `2026-06-${dayNum < 10 ? '0' + dayNum : dayNum}`;
                  const saved = profile.streaks?.calendar?.includes(dateStr);
                  return (
                    <div key={i} className={`calendar-cell ${saved ? 'saved' : ''}`}>
                      {dayNum}
                    </div>
                  );
                })}
              </div>

              {/* Goal Jars */}
              <h4 style={{ fontSize: '1.1rem', marginTop: '2rem', color: 'var(--color-primary)' }}>Goal Jars (Allocation)</h4>
              <div className="jars-container">
                <div className="jar-card">
                  <h4>School Fees Jar</h4>
                  <div className="jar-visual">
                    <div className="jar-fluid" style={{ height: '40%' }}></div>
                  </div>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>Target: ₹1,500</span>
                  <div style={{ fontSize: '0.8rem', color: 'var(--color-success)', fontWeight: 700 }}>Saved: ₹600 (40%)</div>
                </div>
                <div className="jar-card">
                  <h4>Emergency Jar</h4>
                  <div className="jar-visual">
                    <div className="jar-fluid" style={{ height: '15%' }}></div>
                  </div>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>Target: ₹2,000</span>
                  <div style={{ fontSize: '0.8rem', color: 'var(--color-success)', fontWeight: 700 }}>Saved: ₹300 (15%)</div>
                </div>
              </div>
            </div>
          )}

          {level === 2 && (
            <div>
              <h3 style={{ fontSize: '1.4rem', marginBottom: '1rem' }}>Level 2: Emergency Buffer & Safety Net</h3>
              <p style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
                Gig workers need 3 months of emergency expenses saved to handle gaps in seasonal work or medical accidents.
              </p>

              {/* Emergency Fund Setup */}
              <div style={{ background: 'var(--color-bg-light)', padding: '1.2rem', borderRadius: '8px', border: '1px solid var(--color-border)', marginBottom: '1.5rem' }}>
                <h4 style={{ fontSize: '1rem', color: 'var(--color-primary)', marginBottom: '1rem' }}>Configure Emergency Pocket</h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: '1rem', alignItems: 'end' }}>
                  <div className="form-group">
                    <label>Target Fund (₹)</label>
                    <input 
                      type="number" 
                      value={tempGoal.target} 
                      onChange={e => setTempGoal(prev => ({ ...prev, target: e.target.value }))}
                    />
                  </div>
                  <div className="form-group">
                    <label>Current Saved (₹)</label>
                    <input 
                      type="number" 
                      value={tempGoal.current} 
                      onChange={e => setTempGoal(prev => ({ ...prev, current: e.target.value }))}
                    />
                  </div>
                  <button type="button" className="btn btn-primary" onClick={handleSaveGoal}>Update Goal</button>
                </div>
              </div>

              {/* Find visual from goals list */}
              {(() => {
                const emergencyGoal = profile.goals?.find(g => g.type === 'emergency') || { target: 20000, current: 4000 };
                const pct = Math.min(100, Math.round((emergencyGoal.current / emergencyGoal.target) * 100)) || 0;
                return (
                  <div style={{ marginBottom: '2rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', fontWeight: 600, marginBottom: '0.25rem' }}>
                      <span>Safety Net Buffer progress</span>
                      <span>₹{emergencyGoal.current} / ₹{emergencyGoal.target} ({pct}%)</span>
                    </div>
                    <div className="progress-bar-bg" style={{ height: '14px' }}>
                      <div className="progress-bar-fill" style={{ width: `${pct}%`, backgroundColor: 'var(--color-success)' }}></div>
                    </div>
                  </div>
                );
              })()}

              <h4 style={{ fontSize: '1.05rem', color: 'var(--color-primary)', marginBottom: '0.5rem' }}>Essential Living Expenses Checklist</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontWeight: 500 }}>
                  <input type="checkbox" defaultChecked /> Food & Groceries (3 months = ₹10,000)
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontWeight: 500 }}>
                  <input type="checkbox" defaultChecked /> Room rent & electricity (3 months = ₹9,000)
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontWeight: 500 }}>
                  <input type="checkbox" /> Low-cost health insurance cover (Ayushman PM-JAY card verified)
                </label>
              </div>
            </div>
          )}

          {level === 3 && (
            <div>
              <h3 style={{ fontSize: '1.4rem', marginBottom: '1rem' }}>Level 3: Debt Safety & Cost Calculator</h3>
              <p style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
                Warning: Avoid taking unverified loans. Let's compare how expensive local lenders are compared to formal banks.
              </p>

              {/* Interest Cost Calculator */}
              <div style={{ background: '#fff8e1', border: '1px solid #ffe082', padding: '1.5rem', borderRadius: '8px', marginBottom: '2rem' }}>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#b78103', fontSize: '1.05rem', marginBottom: '1rem' }}>
                  <AlertTriangle size={18} /> Loan Cost Comparison
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                  <div className="form-group">
                    <label>Loan Amount (₹)</label>
                    <input 
                      type="number" 
                      value={loanCalc.amount} 
                      onChange={e => setLoanCalc(prev => ({ ...prev, amount: parseInt(e.target.value, 10) || 0 }))}
                    />
                  </div>
                  <div className="form-group">
                    <label>Bank Rate (% yearly)</label>
                    <input 
                      type="number" 
                      value={loanCalc.bankRate} 
                      onChange={e => setLoanCalc(prev => ({ ...prev, bankRate: parseInt(e.target.value, 10) || 0 }))}
                    />
                  </div>
                  <div className="form-group">
                    <label>Lender Rate (% monthly)</label>
                    <input 
                      type="number" 
                      value={loanCalc.lenderRate} 
                      onChange={e => setLoanCalc(prev => ({ ...prev, lenderRate: parseInt(e.target.value, 10) || 0 }))}
                    />
                  </div>
                </div>

                {/* Calculation Outputs */}
                {(() => {
                  const amt = loanCalc.amount;
                  const bankYearlyCost = Math.round(amt * (loanCalc.bankRate / 100));
                  const lenderYearlyCost = Math.round(amt * ((loanCalc.lenderRate * 12) / 100));
                  return (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                        <span>Yearly Interest at Bank ({loanCalc.bankRate}%):</span>
                        <strong style={{ color: 'var(--color-success)' }}>₹{bankYearlyCost}</strong>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                        <span>Yearly Interest from Local Lender ({loanCalc.lenderRate}% per month / {loanCalc.lenderRate * 12}% per year):</span>
                        <strong style={{ color: 'var(--color-accent)' }}>₹{lenderYearlyCost}</strong>
                      </div>
                      <div style={{ borderTop: '1px dashed #ffe082', paddingTop: '0.5rem', display: 'flex', justifyContent: 'space-between', fontWeight: 700, fontSize: '0.95rem' }}>
                        <span>Lender Extra Penalty Cost:</span>
                        <span style={{ color: 'var(--color-accent)' }}>+ ₹{lenderYearlyCost - bankYearlyCost} wasted!</span>
                      </div>
                    </div>
                  );
                })()}
              </div>

              <h4 style={{ fontSize: '1.05rem', color: 'var(--color-primary)', marginBottom: '0.5rem' }}>Your Action Plan: Debt Snowball</h4>
              <ol style={{ paddingLeft: '1.2rem', fontSize: '0.85rem', color: 'var(--color-text-main)', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                <li>List all your EMIs and informal borrowing amounts.</li>
                <li>Verify your monthly expenses to find where leaks are happening.</li>
                <li>Pay minimums on everything, and send any extra cash to the smallest debt first for a quick victory.</li>
                <li>Once a debt is paid, roll that money into paying off the next smallest one.</li>
              </ol>
            </div>
          )}

          {level === 4 && (
            <div>
              <h3 style={{ fontSize: '1.4rem', marginBottom: '1rem' }}>Level 4: Formal Goal Allocator</h3>
              
              <p style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
                Split your salary according to the 50/30/20 rule to plan your PPF, RD, and systematic mutual fund SIP accounts.
              </p>

              {/* Sliders for budget splits */}
              <div style={{ background: 'var(--color-bg-light)', padding: '1.5rem', borderRadius: '8px', border: '1px solid var(--color-border)', marginBottom: '2rem' }}>
                <h4 style={{ fontSize: '1.05rem', color: 'var(--color-primary)', marginBottom: '1rem' }}>Income Allocation Calculator</h4>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <div className="form-group">
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                      <label>Needs (Bills, Rent, Groceries): {budgetSplit.needs}%</label>
                      <strong>₹{Math.round(profile.monthlyIncome * (budgetSplit.needs / 100))}</strong>
                    </div>
                    <input 
                      type="range" min="10" max="80" 
                      value={budgetSplit.needs} 
                      onChange={e => setBudgetSplit(prev => ({ ...prev, needs: parseInt(e.target.value, 10) }))}
                    />
                  </div>

                  <div className="form-group">
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                      <label>Savings (PPF, RD, SIP): {budgetSplit.savings}%</label>
                      <strong style={{ color: 'var(--color-success)' }}>
                        ₹{Math.round(profile.monthlyIncome * (budgetSplit.savings / 100))}
                      </strong>
                    </div>
                    <input 
                      type="range" min="10" max="80" 
                      value={budgetSplit.savings} 
                      onChange={e => setBudgetSplit(prev => ({ ...prev, savings: parseInt(e.target.value, 10) }))}
                    />
                  </div>

                  <div className="form-group">
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                      <label>Freedom (Eating out, Clothes, Leisure): {budgetSplit.freedom}%</label>
                      <strong>₹{Math.round(profile.monthlyIncome * (budgetSplit.freedom / 100))}</strong>
                    </div>
                    <input 
                      type="range" min="0" max="50" 
                      value={budgetSplit.freedom} 
                      onChange={e => setBudgetSplit(prev => ({ ...prev, freedom: parseInt(e.target.value, 10) }))}
                    />
                  </div>
                </div>
              </div>

              <h4 style={{ fontSize: '1.05rem', color: 'var(--color-primary)', marginBottom: '0.5rem' }}>Explore Formal Schemes Available to You</h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div style={{ padding: '1rem', border: '1px solid var(--color-border)', borderRadius: '6px' }}>
                  <strong style={{ display: 'block', fontSize: '0.9rem' }}>Public Provident Fund (PPF)</strong>
                  <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>100% government backed safety. Lock-in 15 years, tax free interest returns.</span>
                </div>
                <div style={{ padding: '1rem', border: '1px solid var(--color-border)', borderRadius: '6px' }}>
                  <strong style={{ display: 'block', fontSize: '0.9rem' }}>Recurring Deposit (RD)</strong>
                  <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>Fixed interest rate in a bank. Open starting from ₹100/month. Zero market risk.</span>
                </div>
              </div>
            </div>
          )}

          {level === 5 && (
            <div>
              <h3 style={{ fontSize: '1.4rem', marginBottom: '1rem' }}>Level 5: Wealth Allocation & Projections</h3>
              <p style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
                Review asset allocation limits, optimize tax structures, and projection curve growth for your retirement pool.
              </p>

              {/* Asset Allocation Form */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
                <div style={{ background: 'var(--color-bg-light)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
                  <h4 style={{ fontSize: '0.95rem', marginBottom: '0.75rem' }}>Asset Splits</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.85rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>Equity Mutual Funds:</span>
                      <strong>{assetAllocation.equity}%</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>PPF / Debt:</span>
                      <strong>{assetAllocation.debt}%</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>Liquid Cash Buffer:</span>
                      <strong>{assetAllocation.cash}%</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>Gold Assets:</span>
                      <strong>{assetAllocation.gold}%</strong>
                    </div>
                  </div>
                </div>

                {/* Graph representation */}
                <div style={{ display: 'flex', flexDirection: 'column', justify: 'center' }}>
                  <h4 style={{ fontSize: '0.95rem', marginBottom: '0.5rem' }}>Allocation Visualizer</h4>
                  <div style={{ display: 'flex', height: '24px', borderRadius: '4px', overflow: 'hidden', border: '1px solid var(--color-border)' }}>
                    <div style={{ width: `${assetAllocation.equity}%`, backgroundColor: 'var(--color-primary)' }} title="Equity"></div>
                    <div style={{ width: `${assetAllocation.debt}%`, backgroundColor: 'var(--color-secondary)' }} title="Debt"></div>
                    <div style={{ width: `${assetAllocation.cash}%`, backgroundColor: '#81c784' }} title="Cash"></div>
                    <div style={{ width: `${assetAllocation.gold}%`, backgroundColor: '#ffd54f' }} title="Gold"></div>
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem', fontSize: '0.7rem', fontWeight: 600 }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                      <span style={{ width: '8px', height: '8px', backgroundColor: 'var(--color-primary)', display: 'inline-block' }}></span> Equity
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                      <span style={{ width: '8px', height: '8px', backgroundColor: 'var(--color-secondary)', display: 'inline-block' }}></span> Debt
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                      <span style={{ width: '8px', height: '8px', backgroundColor: '#81c784', display: 'inline-block' }}></span> Cash
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                      <span style={{ width: '8px', height: '8px', backgroundColor: '#ffd54f', display: 'inline-block' }}></span> Gold
                    </span>
                  </div>
                </div>
              </div>

              {/* Wealth Projection visual */}
              <h4 style={{ fontSize: '1.05rem', color: 'var(--color-primary)', marginBottom: '0.5rem' }}>10-Year Compound Growth Projection</h4>
              <div style={{ background: 'var(--color-bg-light)', border: '1px solid var(--color-border)', borderRadius: '6px', padding: '1rem', height: '140px', display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
                {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(yr => {
                  const h = Math.round(15 + Math.pow(1.15, yr) * 20); // compounding height
                  return (
                    <div key={yr} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '8%' }}>
                      <div style={{ height: `${h}px`, backgroundColor: 'var(--color-primary-light)', width: '100%', borderRadius: '2px 2px 0 0' }}></div>
                      <span style={{ fontSize: '0.65rem', marginTop: '0.2rem', color: 'var(--color-text-muted)', fontWeight: 600 }}>Y{yr}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Right Side: Chat assistant */}
        <div>
          <VoiceChat profile={profile} onProfileUpdate={onProfileUpdate} />
        </div>
      </div>
    </div>
  );
}
