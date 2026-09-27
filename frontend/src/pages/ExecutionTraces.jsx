import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Activity,
  ChevronDown,
  ChevronRight,
  Clock,
  FolderGit2
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import apiService from '../services/apiService';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import EmptyState from '../components/common/EmptyState';
import LoadingSpinner from '../components/common/LoadingSpinner';

export const ExecutionTraces = () => {
  const { activeProject } = useApp();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const runIdParam = searchParams.get('runId');

  const [loading, setLoading] = useState(true);
  const [runs, setRuns] = useState([]);
  const [selectedRunId, setSelectedRunId] = useState(runIdParam || '');
  const [traceTree, setTraceTree] = useState(null);
  const [expandedSpans, setExpandedSpans] = useState([]);

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
        if (runsData && runsData.length > 0) {
          const targetId = runIdParam ? Number(runIdParam) : runsData[0].id;
          setSelectedRunId(String(targetId));
          const traceData = await apiService.getTraceTree(targetId);
          setTraceTree(traceData);
          if (traceData && traceData.spans && traceData.spans.length > 0) {
            setExpandedSpans([traceData.spans[0].id]);
          }
        } else {
          setSelectedRunId('');
          setTraceTree(null);
        }
      } catch (err) {
        console.error('Failed to load runs and traces', err);
        setTraceTree(null);
      } finally {
        setLoading(false);
      }
    };
    loadRuns();
  }, [activeProject, runIdParam]);

  const handleRunChange = async (runId) => {
    setSelectedRunId(runId);
    try {
      setLoading(true);
      const traceData = await apiService.getTraceTree(runId);
      setTraceTree(traceData);
      if (traceData && traceData.spans && traceData.spans.length > 0) {
        setExpandedSpans([traceData.spans[0].id]);
      }
    } catch (err) {
      console.error('Failed to load trace for run', runId, err);
      setTraceTree(null);
    } finally {
      setLoading(false);
    }
  };

  const toggleSpan = (spanId) => {
    if (expandedSpans.includes(spanId)) {
      setExpandedSpans(expandedSpans.filter((id) => id !== spanId));
    } else {
      setExpandedSpans([...expandedSpans, spanId]);
    }
  };

  if (!activeProject) {
    return (
      <div>
        <div className="page-header">
          <div>
            <h1 className="page-title">OpenTelemetry Trace Explorer</h1>
            <p className="page-subtitle">Distributed execution spans and decision waterfall</p>
          </div>
        </div>
        <EmptyState
          title="No Project Active"
          description="Select or create an AI agent project to inspect OpenTelemetry traces."
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
    return <LoadingSpinner message="Reconstructing OpenTelemetry distributed trace spans..." />;
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">OpenTelemetry Trace Explorer</h1>
          <p className="page-subtitle">
            Distributed execution spans and decision waterfall for <strong className="text-cyan">{activeProject?.name}</strong>
          </p>
        </div>

        {/* Run Selector */}
        {runs.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-muted" style={{ fontSize: '0.85rem' }}>Select Test Run:</span>
            <select
              className="form-select"
              style={{ width: '240px' }}
              value={selectedRunId}
              onChange={(e) => handleRunChange(e.target.value)}
            >
              {runs.map((r) => (
                <option key={r.id} value={r.id}>
                  #{r.id} ({r.executionMode}) - {(r.testTitle || 'Test Run').substring(0, 20)}...
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {runs.length === 0 ? (
        <Card>
          <EmptyState
            title="No Execution Runs Found"
            description="Execute test scenarios in Test Studio to capture distributed OpenTelemetry spans, latency breakdowns, and token counts."
            action={
              <button className="btn btn-primary" onClick={() => navigate('/studio')}>
                Open Test Studio
              </button>
            }
          />
        </Card>
      ) : !traceTree || !traceTree.spans || traceTree.spans.length === 0 ? (
        <Card>
          <EmptyState
            title="No Spans Captured for this Run"
            description="Trace spans could not be retrieved for the selected execution run."
          />
        </Card>
      ) : (
        <>
          {/* Trace Overview Header Card */}
          <Card className="comparison-summary-card">
            <div className="flex items-center justify-between flex-wrap gap-3">
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>TRACE IDENTIFIER</div>
                <code style={{ color: 'var(--accent-cyan)', fontSize: '0.9rem' }}>{traceTree.traceId}</code>
              </div>
              <div className="flex gap-4">
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>TOTAL DURATION</div>
                  <strong style={{ fontSize: '1.1rem' }}>{traceTree.totalDurationMs} ms</strong>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>TOTAL TOKENS</div>
                  <strong style={{ fontSize: '1.1rem' }}>{traceTree.totalTokens}</strong>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>STATUS</div>
                  <Badge variant={traceTree.status === 'BLOCKED' ? 'danger' : 'success'}>
                    {traceTree.status}
                  </Badge>
                </div>
              </div>
            </div>
          </Card>

          {/* Waterfall Timeline */}
          <div className="trace-timeline">
            {traceTree.spans.map((span) => {
              const isExpanded = expandedSpans.includes(span.id);
              const percentDuration = traceTree.totalDurationMs > 0
                ? Math.max(15, (span.durationMs / traceTree.totalDurationMs) * 100)
                : 100;

              return (
                <div key={span.id} className="trace-step-card">
                  <div className="trace-step-header" onClick={() => toggleSpan(span.id)}>
                    <div className="trace-step-title">
                      {isExpanded ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
                      <span style={{ fontFamily: 'var(--font-mono)' }}>{span.name}</span>
                      <Badge variant={span.type === 'GUARDRAIL_CHECK' ? 'high' : 'low'} style={{ fontSize: '0.65rem' }}>
                        {span.type}
                      </Badge>
                    </div>

                    <div className="flex items-center gap-4">
                      <div className="trace-latency-bar-container">
                        <div className="trace-latency-bar" style={{ width: `${percentDuration}%` }}></div>
                      </div>
                      <span style={{ fontSize: '0.8rem', fontWeight: 600, width: '60px', textAlign: 'right' }}>
                        {span.durationMs} ms
                      </span>
                      <Badge variant={span.status === 'BLOCKED' ? 'danger' : 'success'}>
                        {span.status}
                      </Badge>
                    </div>
                  </div>

                  {isExpanded && (
                    <div className="trace-step-body">
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                        <div>
                          <div className="form-label">Input State / Payload</div>
                          <pre className="code-snippet">
                            {JSON.stringify(span.inputState, null, 2)}
                          </pre>
                        </div>
                        <div>
                          <div className="form-label">Output State / Evaluation</div>
                          <pre className="code-snippet">
                            {JSON.stringify(span.outputState, null, 2)}
                          </pre>
                        </div>
                      </div>

                      <div className="flex items-center justify-between" style={{ marginTop: '0.75rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        <span>Span ID: <code>{span.id}</code></span>
                        <span>Tokens: <strong>{span.tokens}</strong></span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
};

export default ExecutionTraces;
