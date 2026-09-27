import React from 'react';
import { Info, Sparkles } from 'lucide-react';

export const SimulatedBanner = ({ message = "Phase 2 Demonstration Mode: Data and test runs are simulated locally. Real backend persistence and LangGraph execution will connect in Phase 3 & 4." }) => {
  return (
    <div className="sim-banner">
      <div className="flex items-center gap-2">
        <Sparkles size={16} className="text-cyan" />
        <span>{message}</span>
      </div>
      <span className="badge badge-low" style={{ fontSize: '0.65rem' }}>SIMULATED DATA</span>
    </div>
  );
};

export default SimulatedBanner;
