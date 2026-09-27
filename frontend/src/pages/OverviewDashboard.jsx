import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldAlert,
  Bug,
  Activity,
  CheckCircle2,
  Clock,
  ArrowRight,
  ShieldCheck,
  Zap,
  FolderGit2
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
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
import MetricCard from '../components/common/MetricCard';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import EmptyState from '../components/common/EmptyState';
import LoadingSpinner from '../components/common/LoadingSpinner';

export const OverviewDashboard = () => {
  const { activeProject } = useApp();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [metricsData, setMetricsData] = useState(null);

  useEffect(() => {
    const loadDashboard = async () => {
      if (!activeProject) {
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const [dashData, evalData] = await Promise.all([
          apiService.getDashboardSummary(activeProject.id),
          apiService.getEvaluationMetrics(activeProject.id)
        ]);
        setSummary(dashData);
        setMetricsData(evalData);
      } catch (err) {
        console.error('Failed to load dashboard data', err);
      } finally {
        setLoading(false);
      }
    };
    loadDashboard();
  }, [activeProject]);

  if (!activeProject) {
    return (
      <div>
        <div className="page-header">
          <div>
            <h1 className="page-title">Security & Reliability Overview</h1>
            <p className="page-subtitle">Live telemetry and vulnerability posture</p>
          </div>
        </div>
        <EmptyState
          title="No Project Active"
          description="Create or select an AI agent project to view real-time security findings, test runs, and DeepEval metrics."
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

  if (loading || !summary) {
    return <LoadingSpinner message="Aggregating security telemetry and evaluation metrics..." />;
  }

  const hasRuns = summary.totalRuns > 0;

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Security & Reliability Overview</h1>
          <p className="page-subtitle">
            Live telemetry and vulnerability posture for <strong className="text-cyan">{activeProject?.name}</strong>
          </p>
        </div>
        <div className="flex gap-2">
          <button className="btn btn-secondary" onClick={() => navigate('/compare')}>
            Compare Runs
          </button>
          <button className="btn btn-primary" onClick={() => navigate('/studio')}>
            <Zap size={16} />
            Launch Test Run
          </button>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="stats-grid">
        <MetricCard
          title="Total Test Runs"
          value={summary.totalRuns}
          subtitle="All execution suites"
          icon={Activity}
          iconColor="var(--accent-blue)"
          iconBg="rgba(59, 130, 246, 0.12)"
        />
        <MetricCard
          title="Security Findings"
          value={summary.securityFindingsTotal}
          subtitle="Threats identified"
          icon={Bug}
          iconColor="var(--severity-critical)"
          iconBg="rgba(220, 38, 38, 0.12)"
        />
        <MetricCard
          title="Security Pass Rate"
          value={`${summary.securityTestPassRate}%`}
          subtitle="Target >= 85%"
          icon={ShieldCheck}
          iconColor="var(--color-success)"
          iconBg="rgba(16, 185, 129, 0.12)"
        />
        <MetricCard
          title="Task Success Rate"
          value={`${summary.taskSuccessRate}%`}
          subtitle="Autonomous completion"
          icon={CheckCircle2}
          iconColor="var(--accent-cyan)"
          iconBg="rgba(6, 182, 212, 0.12)"
        />
        <MetricCard
          title="Average Latency"
          value={`${summary.averageLatencyMs} ms`}
          subtitle="Full graph execution"
          icon={Clock}
          iconColor="var(--color-warning)"
          iconBg="rgba(245, 158, 11, 0.12)"
        />
      </div>

      {!hasRuns ? (
        <Card style={{ marginTop: '1.5rem' }}>
          <EmptyState
            title="No Test Runs Recorded Yet"
            description="Execute automated security attacks and reliability benchmarks in Test Studio to populate charts, metrics, and trace telemetry."
            action={
              <button className="btn btn-primary" onClick={() => navigate('/studio')}>
                <Zap size={16} />
                Open Test Studio
              </button>
            }
          />
        </Card>
      ) : (
        <>
          {/* Visual Charts Grid */}
          <div className="charts-grid">
            {/* Faithfulness & Reliability Historical Trends */}
            <Card title="Reliability & Faithfulness Progression" subtitle="DeepEval Faithfulness over time">
              <div className="chart-wrapper">
                {metricsData?.historyTrends && metricsData.historyTrends.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={metricsData.historyTrends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <defs>
                        <linearGradient id="securedColor" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                          <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                        </linearGradient>
                        <linearGradient id="baselineColor" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.0} />
                        </linearGradient>
                      </defs>
                      <XAxis dataKey="runDate" stroke="#64748b" fontSize={12} tickLine={false} />
                      <YAxis stroke="#64748b" fontSize={12} domain={[0, 1]} tickLine={false} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
                      />
                      <Legend verticalAlign="top" height={36} iconType="circle" />
                      <Area type="monotone" dataKey="securedFaithfulness" name="Secured Mode (Guardrails)" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#securedColor)" />
                      <Area type="monotone" dataKey="baselineFaithfulness" name="Baseline (Unprotected)" stroke="#f59e0b" strokeWidth={2} fillOpacity={1} fill="url(#baselineColor)" />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex flex-col items-center justify-center h-full text-center">
                    <p className="text-muted" style={{ fontSize: '0.85rem' }}>
                      Historical evaluation trend points will appear after consecutive evaluation runs.
                    </p>
                  </div>
                )}
              </div>
            </Card>

            {/* Security Findings by Severity */}
            <Card title="Findings by Severity" subtitle="Threat classification count">
              <div className="chart-wrapper">
                {summary.findingsBySeverity && summary.findingsBySeverity.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={summary.findingsBySeverity} layout="vertical" margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
                      <XAxis type="number" stroke="#64748b" fontSize={12} tickLine={false} />
                      <YAxis dataKey="name" type="category" stroke="#64748b" fontSize={12} tickLine={false} width={70} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
                      />
                      <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                        {summary.findingsBySeverity.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color || '#06b6d4'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex flex-col items-center justify-center h-full text-center">
                    <p className="text-muted" style={{ fontSize: '0.85rem' }}>
                      No security findings recorded for this project.
                    </p>
                  </div>
                )}
              </div>
            </Card>
          </div>

          {/* Recent Test Runs Table */}
          <Card
            title="Recent Test Executions"
            subtitle="Latest automated attack simulations and benchmarks"
            action={
              <button className="btn btn-secondary btn-sm" onClick={() => navigate('/traces')}>
                View All Traces
              </button>
            }
          >
            {summary.recentRuns && summary.recentRuns.length > 0 ? (
              <div className="table-container">
                <table className="custom-table">
                  <thead>
                    <tr>
                      <th>Run ID</th>
                      <th>Test Scenario</th>
                      <th>Mode</th>
                      <th>Score</th>
                      <th>Latency</th>
                      <th>Security Status</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {summary.recentRuns.map((run) => (
                      <tr key={run.id || run.runId}>
                        <td>
                          <code style={{ color: 'var(--accent-cyan)' }}>#{run.id || run.runId}</code>
                        </td>
                        <td style={{ fontWeight: 500 }}>{run.testTitle}</td>
                        <td>
                          <Badge variant={run.executionMode}>{run.executionMode}</Badge>
                        </td>
                        <td>
                          <span style={{ fontWeight: 600, color: (run.overallScore || 0) > 75 ? 'var(--color-success)' : 'var(--color-danger)' }}>
                            {run.overallScore != null ? `${run.overallScore}%` : 'N/A'}
                          </span>
                        </td>
                        <td>{run.latencyMs != null ? `${run.latencyMs} ms` : 'N/A'}</td>
                        <td>
                          {run.isVulnerable ? (
                            <Badge variant="danger">Vulnerable</Badge>
                          ) : (
                            <Badge variant="success">Secured</Badge>
                          )}
                        </td>
                        <td>
                          <button
                            className="btn btn-secondary btn-sm"
                            onClick={() => navigate(`/traces?runId=${run.id || run.runId}`)}
                          >
                            Trace
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <EmptyState
                title="No Recent Runs"
                description="Execute test scenarios to see recent execution details here."
              />
            )}
          </Card>
        </>
      )}
    </div>
  );
};

export default OverviewDashboard;
