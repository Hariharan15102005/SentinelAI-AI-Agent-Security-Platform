import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldCheck,
  Award,
  TrendingUp,
  HelpCircle,
  BarChart3,
  CheckCircle2,
  AlertCircle,
  FolderGit2
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  Cell
} from 'recharts';
import { useApp } from '../context/AppContext';
import apiService from '../services/apiService';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import EmptyState from '../components/common/EmptyState';
import LoadingSpinner from '../components/common/LoadingSpinner';

export const EvaluationHub = () => {
  const { activeProject } = useApp();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [evalData, setEvalData] = useState(null);

  useEffect(() => {
    const loadEval = async () => {
      if (!activeProject) {
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const data = await apiService.getEvaluationMetrics(activeProject.id);
        setEvalData(data);
      } catch (err) {
        console.error('Failed to load evaluation metrics', err);
        setEvalData(null);
      } finally {
        setLoading(false);
      }
    };
    loadEval();
  }, [activeProject]);

  if (!activeProject) {
    return (
      <div>
        <div className="page-header">
          <div>
            <h1 className="page-title">AI Evaluation & Reliability Hub</h1>
            <p className="page-subtitle">DeepEval metrics and safety thresholds</p>
          </div>
        </div>
        <EmptyState
          title="No Project Active"
          description="Select or create an AI agent project to view DeepEval reliability scoring."
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
    return <LoadingSpinner message="Calculating DeepEval reliability indices..." />;
  }

  const hasMetrics = evalData && evalData.metrics && evalData.metrics.length > 0;
  const hasTrends = evalData && evalData.historyTrends && evalData.historyTrends.length > 0;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">AI Evaluation & Reliability Hub</h1>
          <p className="page-subtitle">
            DeepEval metrics and safety thresholds for <strong className="text-cyan">{activeProject?.name}</strong>
          </p>
        </div>
      </div>

      {!hasMetrics ? (
        <Card>
          <EmptyState
            title="No Evaluation Metrics Recorded"
            description="DeepEval quality scores (Faithfulness, Answer Relevancy, Hallucination Index) will appear here once automated agent tests have executed."
            action={
              <button className="btn btn-primary" onClick={() => navigate('/studio')}>
                Run Agent Test
              </button>
            }
          />
        </Card>
      ) : (
        <>
          {/* Metric Cards Grid */}
          <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))' }}>
            {evalData.metrics.map((m) => {
              const isHallucination = m.key === 'hallucination';
              const scorePercent = (m.score * 100).toFixed(1);
              const thresholdPercent = (m.threshold * 100).toFixed(0);

              return (
                <Card key={m.id} className="stat-card">
                  <div className="flex items-center justify-between">
                    <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>{m.name}</span>
                    <Badge variant={m.passed ? 'success' : 'danger'}>{m.status}</Badge>
                  </div>

                  <div style={{ marginTop: '0.5rem' }}>
                    <div style={{ fontSize: '2rem', fontWeight: 700, color: m.passed ? 'var(--color-success)' : 'var(--color-danger)' }}>
                      {scorePercent}%
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      Threshold: {isHallucination ? `< ${thresholdPercent}%` : `≥ ${thresholdPercent}%`}
                    </div>
                  </div>

                  {/* Progress bar */}
                  <div style={{ width: '100%', height: '6px', background: 'var(--bg-primary)', borderRadius: 'var(--radius-full)', overflow: 'hidden', margin: '0.75rem 0' }}>
                    <div
                      style={{
                        height: '100%',
                        width: `${Math.min(100, Math.max(0, m.score * 100))}%`,
                        background: m.passed ? 'var(--color-success)' : 'var(--color-danger)'
                      }}
                    ></div>
                  </div>

                  <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', lineHeight: '1.4' }}>
                    {m.explanation}
                  </p>
                </Card>
              );
            })}
          </div>

          {/* DeepEval Comparison Chart */}
          {hasTrends && (
            <div style={{ marginTop: '1.5rem' }}>
              <Card title="Historical Faithfulness: Baseline vs. Secured Runs" subtitle="Tracking agent fidelity across consecutive development runs">
                <div style={{ width: '100%', height: '300px', marginTop: '1rem' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={evalData.historyTrends}>
                      <XAxis dataKey="runDate" stroke="#64748b" fontSize={12} tickLine={false} />
                      <YAxis stroke="#64748b" fontSize={12} domain={[0, 1]} tickLine={false} />
                      <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff' }} />
                      <Legend verticalAlign="top" height={36} iconType="circle" />
                      <Bar dataKey="securedFaithfulness" name="Secured Mode (With Guardrails)" fill="#10b981" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="baselineFaithfulness" name="Baseline Mode (Raw Agent)" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </Card>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default EvaluationHub;
