import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import AppLayout from './layouts/AppLayout';
import OverviewDashboard from './pages/OverviewDashboard';
import TestStudio from './pages/TestStudio';
import SecurityFindings from './pages/SecurityFindings';
import EvaluationHub from './pages/EvaluationHub';
import ExecutionTraces from './pages/ExecutionTraces';
import RunComparison from './pages/RunComparison';
import Projects from './pages/Projects';
import Settings from './pages/Settings';
import AgentDojoStudio from './pages/AgentDojoStudio';
import NotFound from './pages/NotFound';

function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            <Route index element={<OverviewDashboard />} />
            <Route path="studio" element={<TestStudio />} />
            <Route path="agentdojo" element={<AgentDojoStudio />} />
            <Route path="findings" element={<SecurityFindings />} />
            <Route path="evaluation" element={<EvaluationHub />} />
            <Route path="traces" element={<ExecutionTraces />} />
            <Route path="compare" element={<RunComparison />} />
            <Route path="projects" element={<Projects />} />
            <Route path="settings" element={<Settings />} />
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AppProvider>
  );
}

export default App;
