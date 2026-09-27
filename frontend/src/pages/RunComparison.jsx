import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  GitCompare,
  ArrowRight,
  ShieldCheck,
  ShieldAlert,
  Clock,
  Coins,
  CheckCircle,
  XCircle,
  FolderGit2
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import apiService from '../services/apiService';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import EmptyState from '../components/common/EmptyState';
import LoadingSpinner from '../components/common/LoadingSpinner';

export const RunComparison = () => {
  const { activeProject } = useApp();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [runs, setRuns] = useState([]);
  const [baselineRunId, setBaselineRunId] = useState('');
  const [securedRunId, setSecuredRunId] = useState('');
  const [diffData, setDiffData] = useState(null);

  useEffect(() => {
    const loadRuns = async () => {
      if (!activeProject) {
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const runsData = await apiService.getRuns(activeProject.id);
        setRuns(runsData || []);

        const baselines = (runsData || []).filter((r) => r.executionMode === 'BASELINE');
        const secureds = (runsData || []).filter((r) => r.executionMode === 'SECURED');

        if (baselines.length > 0 && secureds.length > 0) {
          const bId = String(baselines[0].id);
          const sId = String(secureds[0].id);
          setBaselineRunId(bId);
          setSecuredRunId(sId);
          const comp = await apiService.compareRuns(bId, sId);
          setDiffData(comp);
        } else {
          setDiffData(null);
        }
      } catch (err) {
        console.error('Failed to load comparison data', err);
        setDiffData(null);
      } finally {
        setLoading(false);
      }
    };
    loadRuns();
  }, [activeProject]);

  const handleCompare = async (bId, sId) => {
    if (!bId || !sId) return;
    setBaselineRunId(bId);
    setSecuredRunId(sId);
    try {
      setLoading(true);
      const comp = await apiService.compareRuns(bId, sId);
      setDiffData(comp);
    } catch (err) {
      console.error('Failed to compare runs', err);
      setDiffData(null);
    } finally {
      setLoading(false);
    }
  };

  if (!activeProject) {
    return (
      <div>
        <div className="page-header">
          <div>
            <h1 className="page-title">Run Comparison & Diff Visualizer</h1>
            <p className="page-subtitle">Evaluate safety enforcement against latency and token trade-offs</p>
          </div>
        </div>
        <EmptyState
          title="No Project Active"
          description="Select or create an AI agent project to compare test run executions."
          action={
            <button className="btn btn-primary" onClick={() => navigate('/projects')}>
              <FolderGit2 size={16} />
              Go to Projects
            </button>
          }
        />
      </div>
    );
  }

  if (loading) {
    return <LoadingSpinner message="Generating side-by-side run delta analysis..." />;
  }

  const baselineRuns = runs.filter((r) => r.executionMode === 'BASELINE');
  const securedRuns = runs.filter((r) => r.executionMode === 'SECURED');
  const canCompare = baselineRuns.length > 0 && securedRuns.length > 0;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Run Comparison & Diff Visualizer</h1>
          <p className="page-subtitle">
            Evaluate safety enforcement against latency and token trade-offs for <strong className="text-cyan">{activeProject?.name}</strong>
          </p>
        </div>
      </div>

      {!canCompare || !diffData ? (
        <Card>
          <EmptyState
            title="Insufficient Runs to Compare"
            description={
              runs.length === 0
                ? "No test runs found for this project. Execute both a Baseline and a Secured test run in Test Studio to enable side-by-side comparison."
                : baselineRuns.length === 0
                ? "A Baseline (unprotected) run is required for comparison. Execute a Baseline test run in Test Studio."
                : "A Secured (guarded) run is required for comparison. Execute a Secured test run in Test Studio."
            }
            action={
              <button className="btn btn-primary" onClick={() => navigate('/studio')}>
                Open Test Studio
              </button>
            }
          />
        </Card>
      ) : (
        <>
          {/* Selectors Bar */}
          <Card style={{ marginBottom: '1.5rem' }}>
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-2" style={{ flex: 1, minWidth: '240px' }}>
                <span className="badge badge-baseline">BASELINE RUN</span>
                <select
                  className="form-select"
                  value={baselineRunId}
                  onChange={(e) => handleCompare(e.target.value, securedRunId)}
                >
                  {baselineRuns.map((r) => (
                    <option key={r.id} value={r.id}>
                      #{r.id} - {(r.testTitle || 'Test Run').substring(0, 25)} ({r.latencyMs || 0}ms)
                    </option>
                  ))}
                </select>
              </div>

              <div style={{ fontSize: '1.25rem', color: 'var(--text-muted)' }}>VS</div>

              <div className="flex items-center gap-2" style={{ flex: 1, minWidth: '240px' }}>
                <span className="badge badge-secured">SECURED RUN</span>
                <select
                  className="form-select"
                  value={securedRunId}
                  onChange={(e) => handleCompare(baselineRunId, e.target.value)}
                >
                  {securedRuns.map((r) => (
                    <option key={r.id} value={r.id}>
                      #{r.id} - {(r.testTitle || 'Test Run').substring(0, 25)} ({r.latencyMs || 0}ms)
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </Card>

          {/* Comparative Delta Summary */}
          <div className="stats-grid">
            <Card className="stat-card">
              <div className="stat-header">
                <span>Vulnerability Status</span>
                <ShieldAlert size={16} />
              </div>
              <div style={{ marginTop: '0.25rem' }}>
                {diffData.delta?.vulnerabilityMitigated ? (
                  <span className="badge badge-success" style={{ fontSize: '0.85rem' }}>
                    VULNERABILITY MITIGATED
                  </span>
                ) : (
                  <span className="badge badge-danger">NO MITIGATION</span>
                )}
              </div>
              <span className="text-muted" style={{ fontSize: '0.75rem', marginTop: '0.5rem' }}>
                Baseline: {diffData.baseline?.isVulnerable ? 'Vulnerable' : 'Safe'} → Secured: {diffData.secured?.isVulnerable ? 'Vulnerable' : 'Safe'}
              </span>
            </Card>

            <Card className="stat-card">
              <div className="stat-header">
                <span>Score Delta</span>
                <ShieldCheck size={16} />
              </div>
              <div className="stat-value" style={{ color: 'var(--color-success)' }}>
                {((diffData.secured?.overallScore || 0) - (diffData.baseline?.overallScore || 0)).toFixed(1)}%
              </div>
              <span className="text-muted" style={{ fontSize: '0.75rem' }}>
                {diffData.baseline?.overallScore || 0}% (Baseline) → {diffData.secured?.overallScore || 0}% (Secured)
              </span>
            </Card>

            <Card className="stat-card">
              <div className="stat-header">
                <span>Latency Overhead</span>
                <Clock size={16} />
              </div>
              <div className="stat-value" style={{ color: 'var(--color-warning)' }}>
                +{diffData.delta?.latencyOverheadMs || 0} ms
              </div>
              <span className="text-muted" style={{ fontSize: '0.75rem' }}>
                {diffData.baseline?.latencyMs || 0}ms (Baseline) → {diffData.secured?.latencyMs || 0}ms (Secured)
              </span>
            </Card>

            <Card className="stat-card">
              <div className="stat-header">
                <span>Token Consumption</span>
                <Coins size={16} />
              </div>
              <div className="stat-value" style={{ color: 'var(--accent-cyan)' }}>
                {diffData.delta?.tokenSavings > 0 ? `-${diffData.delta.tokenSavings}` : `+${Math.abs(diffData.delta?.tokenSavings || 0)}`} tokens
              </div>
              <span className="text-muted" style={{ fontSize: '0.75rem' }}>
                {diffData.baseline?.totalTokens || 0} tokens → {diffData.secured?.totalTokens || 0} tokens
              </span>
            </Card>
          </div>

          {/* Side by Side Output Comparison */}
          <div className="diff-container">
            {/* Baseline Panel */}
            <div className="diff-panel baseline">
              <div className="flex items-center justify-between" style={{ marginBottom: '1rem' }}>
                <div>
                  <Badge variant="baseline">BASELINE (UNPROTECTED)</Badge>
                  <h3 style={{ fontSize: '1rem', fontWeight: 600, marginTop: '0.25rem' }}>
                    Run #{diffData.baseline?.runId}
                  </h3>
                </div>
                <Badge variant={diffData.baseline?.isVulnerable ? 'danger' : 'success'}>
                  {diffData.baseline?.isVulnerable ? 'Vulnerable' : 'Safe'}
                </Badge>
              </div>

              <div className="form-group">
                <label className="form-label">Input Prompt</label>
                <div className="code-snippet">{diffData.testCase?.inputPrompt || 'Prompt'}</div>
              </div>

              <div className="form-group">
                <label className="form-label">Agent Final Output Response</label>
                <div
                  className="code-snippet"
                  style={{
                    borderColor: diffData.baseline?.isVulnerable ? 'rgba(239, 68, 68, 0.4)' : 'rgba(255, 255, 255, 0.1)',
                    background: diffData.baseline?.isVulnerable ? 'rgba(239, 68, 68, 0.05)' : 'rgba(15, 23, 42, 0.6)'
                  }}
                >
                  {diffData.baseline?.finalOutput || 'No output recorded'}
                </div>
              </div>

              <div style={{ marginTop: '1rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Latency: <strong>{diffData.baseline?.latencyMs || 0}ms</strong> | Total Tokens: <strong>{diffData.baseline?.totalTokens || 0}</strong>
              </div>
            </div>

            {/* Secured Panel */}
            <div className="diff-panel secured">
              <div className="flex items-center justify-between" style={{ marginBottom: '1rem' }}>
                <div>
                  <Badge variant="secured">SECURED (GUARDRAILS AI)</Badge>
                  <h3 style={{ fontSize: '1rem', fontWeight: 600, marginTop: '0.25rem' }}>
                    Run #{diffData.secured?.runId}
                  </h3>
                </div>
                <Badge variant={diffData.secured?.isVulnerable ? 'danger' : 'success'}>
                  {diffData.secured?.isVulnerable ? 'Vulnerable' : 'Safe'}
                </Badge>
              </div>

              <div className="form-group">
                <label className="form-label">Input Prompt</label>
                <div className="code-snippet">{diffData.testCase?.inputPrompt || 'Prompt'}</div>
              </div>

              <div className="form-group">
                <label className="form-label">Agent Final Output Response</label>
                <div
                  className="code-snippet"
                  style={{
                    borderColor: 'rgba(16, 185, 129, 0.4)',
                    background: 'rgba(16, 185, 129, 0.05)'
                  }}
                >
                  {diffData.secured?.finalOutput || 'No output recorded'}
                </div>
              </div>

              <div style={{ marginTop: '1rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Latency: <strong>{diffData.secured?.latencyMs || 0}ms</strong> | Total Tokens: <strong>{diffData.secured?.totalTokens || 0}</strong>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default RunComparison;
