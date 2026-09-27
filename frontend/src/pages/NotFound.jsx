import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, Home } from 'lucide-react';

export const NotFound = () => {
  const navigate = useNavigate();

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '60vh',
        textAlign: 'center',
        gap: '1rem'
      }}
    >
      <ShieldAlert size={56} className="text-cyan" />
      <h1 style={{ fontSize: '2rem', fontWeight: 700 }}>404 - Page Not Found</h1>
      <p className="text-muted" style={{ maxWidth: '420px', fontSize: '0.9rem' }}>
        The requested endpoint or resource does not exist in the SentinelAI routing table.
      </p>
      <button className="btn btn-primary" onClick={() => navigate('/')}>
        <Home size={16} /> Return to Dashboard
      </button>
    </div>
  );
};

export default NotFound;
