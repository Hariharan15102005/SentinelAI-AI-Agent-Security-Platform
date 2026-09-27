import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingSpinner = ({ message = "Loading data..." }) => {
  return (
    <div className="flex flex-col items-center justify-center gap-3" style={{ padding: '3rem 1rem' }}>
      <Loader2 size={32} className="text-cyan" style={{ animation: 'spin 1s linear infinite' }} />
      <span className="text-secondary" style={{ fontSize: '0.875rem' }}>{message}</span>
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default LoadingSpinner;
