import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Bug,
  Search,
  FolderGit2
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import apiService from '../services/apiService';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import Modal from '../components/common/Modal';
import LoadingSpinner from '../components/common/LoadingSpinner';
import EmptyState from '../components/common/EmptyState';

export const SecurityFindings = () => {
  const { activeProject } = useApp();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [findings, setFindings] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [activeFinding, setActiveFinding] = useState(null);

  useEffect(() => {
    const fetchFindings = async () => {
      if (!activeProject) {
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const data = await apiService.getSecurityFindings(activeProject.id);
        setFindings(data || []);
      } catch (err) {
        console.error('Failed to load findings', err);
        setFindings([]);
      } finally {
        setLoading(false);
      }
    };
    fetchFindings();
  }, [activeProject]);

  if (!activeProject) {
    return (
      <div>
        <div className="page-header">
          <div>
            <h1 className="page-title">Security Findings Explorer</h1>
            <p className="page-subtitle">Audited vulnerability events and runtime policy breaches</p>
          </div>
        </div>
        <EmptyState
          title="No Project Active"
          description="Select or create an AI agent project to view detected security findings and vulnerabilities."
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

  const filteredFindings = findings.filter((f) => {
    const titleMatch = (f.title || '').toLowerCase().includes(searchQuery.toLowerCase());
    const threatMatch = (f.threatType || '').toLowerCase().includes(searchQuery.toLowerCase());
    const idMatch = String(f.id || '').toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSearch = titleMatch || threatMatch || idMatch;

    const matchesSeverity = severityFilter === 'ALL' || f.severity === severityFilter;
    const matchesStatus = statusFilter === 'ALL' || f.status === statusFilter;

    return matchesSearch && matchesSeverity && matchesStatus;
  });

  if (loading) {
    return <LoadingSpinner message="Scanning security findings database..." />;
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Security Findings Explorer</h1>
          <p className="page-subtitle">
            Audited vulnerability events and runtime policy breaches for <strong className="text-cyan">{activeProject?.name}</strong>
          </p>
        </div>
      </div>

      {findings.length === 0 ? (
        <Card>
          <EmptyState
            title="No Security Findings Recorded"
            description="No vulnerabilities or policy violations have been detected for this project yet. Run security attack scenarios in Test Studio to analyze agent defenses."
            action={
              <button className="btn btn-primary" onClick={() => navigate('/studio')}>
                Open Test Studio
              </button>
            }
          />
        </Card>
      ) : (
        <>
          {/* Toolbar */}
          <div className="findings-toolbar">
            <div className="search-input-wrapper">
              <Search size={16} className="search-icon" />
              <input
                type="text"
                className="form-input search-input"
                placeholder="Search by ID, threat type, title..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            <div className="flex gap-2">
              <select
                className="form-select"
                style={{ width: '150px' }}
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
              >
                <option value="ALL">All Severities</option>
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
              </select>

              <select
                className="form-select"
                style={{ width: '150px' }}
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="ALL">All Actions</option>
                <option value="BLOCKED">Blocked</option>
                <option value="MASKED">Masked</option>
                <option value="FLAGGED_ONLY">Flagged</option>
              </select>
            </div>
          </div>

          {/* Findings Table */}
          <Card>
            {filteredFindings.length === 0 ? (
              <EmptyState
                title="No findings match your criteria"
                description="Clear search or severity filters to view all recorded threats."
              />
            ) : (
              <div className="table-container">
                <table className="custom-table">
                  <thead>
                    <tr>
                      <th>Finding ID</th>
                      <th>Title & Threat Type</th>
                      <th>Severity</th>
                      <th>Guardrail Rule</th>
                      <th>Action Taken</th>
                      <th>Test Run</th>
                      <th>Timestamp</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredFindings.map((f) => (
                      <tr key={f.id} style={{ cursor: 'pointer' }} onClick={() => setActiveFinding(f)}>
                        <td>
                          <code style={{ color: 'var(--accent-cyan)' }}>#{f.id}</code>
                        </td>
                        <td>
                          <div style={{ fontWeight: 600 }}>{f.title}</div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{f.threatType}</div>
                        </td>
                        <td>
                          <Badge variant={f.severity}>{f.severity}</Badge>
                        </td>
                        <td>
                          <span style={{ fontSize: '0.8rem', fontFamily: 'var(--font-mono)' }}>{f.guardrailRule || 'Policy'}</span>
                        </td>
                        <td>
                          <Badge
                            variant={
                              f.status === 'BLOCKED' ? 'danger' : f.status === 'MASKED' ? 'high' : 'medium'
                            }
                          >
                            {f.status}
                          </Badge>
                        </td>
                        <td>
                          <code style={{ color: 'var(--accent-blue)' }}>#{f.testRunId}</code>
                        </td>
                        <td style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {f.timestamp ? new Date(f.timestamp).toLocaleTimeString() : 'N/A'}
                        </td>
                        <td>
                          <button
                            className="btn btn-secondary btn-sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              setActiveFinding(f);
                            }}
                          >
                            Details
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </>
      )}

      {/* Finding Detail Modal */}
      <Modal
        isOpen={Boolean(activeFinding)}
        onClose={() => setActiveFinding(null)}
        title={activeFinding ? `Security Finding: #${activeFinding.id}` : ''}
      >
        {activeFinding && (
          <div>
            <div className="flex items-center justify-between" style={{ marginBottom: '1rem' }}>
              <Badge variant={activeFinding.severity}>{activeFinding.severity} SEVERITY</Badge>
              <Badge variant="low">{activeFinding.threatType}</Badge>
            </div>

            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
              {activeFinding.title}
            </h3>

            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              {activeFinding.description || 'No description provided.'}
            </p>

            {activeFinding.flaggedContent && (
              <div className="form-group">
                <label className="form-label">Flagged Content Evidence</label>
                <div className="code-snippet" style={{ color: 'var(--severity-high)' }}>
                  {activeFinding.flaggedContent}
                </div>
              </div>
            )}

            <div className="grid-2 gap-3" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', margin: '1rem 0' }}>
              <div style={{ padding: '0.75rem', background: 'var(--bg-primary)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
                <span className="text-muted" style={{ fontSize: '0.75rem' }}>Triggered Policy</span>
                <div style={{ fontWeight: 600, fontSize: '0.85rem', fontFamily: 'var(--font-mono)' }}>
                  {activeFinding.guardrailRule || 'N/A'}
                </div>
              </div>
              <div style={{ padding: '0.75rem', background: 'var(--bg-primary)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
                <span className="text-muted" style={{ fontSize: '0.75rem' }}>Enforced Action</span>
                <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--color-success)' }}>
                  {activeFinding.actionTaken || activeFinding.status || 'N/A'}
                </div>
              </div>
            </div>

            {activeFinding.remediationNotes && (
              <div className="form-group">
                <label className="form-label">Architectural Remediation Guidance</label>
                <div style={{ padding: '0.85rem', background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.25)', borderRadius: 'var(--radius-md)', fontSize: '0.85rem', color: 'var(--text-primary)' }}>
                  {activeFinding.remediationNotes}
                </div>
              </div>
            )}

            <div className="flex justify-between items-center" style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
              <span className="text-muted" style={{ fontSize: '0.75rem' }}>
                Affected Node: <code>{activeFinding.affectedNode || 'Agent Execution Graph'}</code>
              </span>
              <button className="btn btn-secondary" onClick={() => setActiveFinding(null)}>
                Close
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default SecurityFindings;
