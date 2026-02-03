import React, { useState } from 'react';
import Dashboard from './components/Dashboard.jsx';
import PropDetail from './components/PropDetail.jsx';
import EntryBuilder from './components/EntryBuilder.jsx';
import History from './components/History.jsx';
import Settings from './components/Settings.jsx';

export default function App() {
  const [tab, setTab] = useState('dashboard');
  const renderTab = () => {
    switch (tab) {
      case 'dashboard':
        return <Dashboard />;
      case 'entry':
        return <EntryBuilder />;
      case 'history':
        return <History />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };
  return (
    <div style={{ padding: '1rem', fontFamily: 'Arial, sans-serif' }}>
      <h1>NBA Prop Analyzer</h1>
      <nav style={{ marginBottom: '1rem' }}>
      <button onClick={() => setTab('dashboard')}>Dashboard</button>
      <button onClick={() => setTab('entry')}>Entry Builder</button>
      <button onClick={() => setTab('history')}>History</button>
      <button onClick={() => setTab('settings')}>Settings</button>
      </nav>
      {renderTab()}
    </div>
  );
}
