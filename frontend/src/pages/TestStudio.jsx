import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FlaskConical,
  Play,
  Shield,
  ShieldAlert,
  Sliders,
  CheckSquare,
  Square,
  AlertTriangle,
  Zap,
  Plus,
  Info,
  FolderGit2,
  CheckCircle2,
  XCircle,
  AlertCircle
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import apiService from '../services/apiService';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import EmptyState from '../components/common/EmptyState';
import Modal from '../components/common/Modal';
import LoadingSpinner from '../components/common/LoadingSpinner';

export const TestStudio = () => {
  const { activeProject } = useApp();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [testCases, setTestCases] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [selectedTests, setSelectedTests] = useState([]);
  const [executionMode, setExecutionMode] = useState('SECURED'); // BASELINE or SECURED
  const [selectedGuardrails, setSelectedGuardrails] = useState([
    'PromptInjectionDetector',
    'PIIAnonymizer',
    'SQLInjectionGuard'
  ]);

  const [executing, setExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState(null);

  // New Test Case Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newCategory, setNewCategory] = useState('SECURITY_PROMPT_INJECTION');
  const [newPrompt, setNewPrompt] = useState('');
  const [newExpected, setNewExpected] = useState('');
  const [newSeverity, setNewSeverity] = useState('HIGH');
  const [creatingTC, setCreatingTC] = useState(false);
  const [saveError, setSaveError] = useState(null);
  const [saveSuccess, setSaveSuccess] = useState(null);
  const [formSubmitted, setFormSubmitted] = useState(false);

  const availableGuardrails = [
    { id: 'PromptInjectionDetector', name: 'Prompt Injection Detector', desc: 'Blocks directive override and jailbreak syntax' },
    { id: 'PIIAnonymizer', name: 'PII Data Anonymizer', desc: 'Masks emails, phone numbers, and secrets in input/output' },
    { id: 'SQLInjectionGuard', name: 'SQL & Tool Injection Guard', desc: 'Sanitizes tool parameter strings against SQL syntax' },
    { id: 'ToxicityFilter', name: 'Toxic Output Filter', desc: 'Intercepts offensive, biased, or harmful responses' }
  ];

  const fetchTests = async (newlyCreatedId = null) => {
    if (!activeProject) {
      setLoading(false);
      return;
    }
    try {
      setLoading(true);
      const data = await apiService.getTestCases(activeProject.id);
      const tests = Array.isArray(data) ? data : [];
      setTestCases(tests);
      if (newlyCreatedId) {
        setSelectedTests([newlyCreatedId]);
      } else if (tests.length > 0 && selectedTests.length === 0) {
        setSelectedTests([tests[0].id]);
      }
    } catch (err) {
      console.error('Failed to load test cases', err);
      setTestCases([]);
      setSelectedTests([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTests();
  }, [activeProject]);

  const toggleSelectTest = (id) => {
    if (selectedTests.includes(id)) {
      setSelectedTests(selectedTests.filter((t) => t !== id));
    } else {
      setSelectedTests([...selectedTests, id]);
    }
  };

  const selectAll = () => {
    if (selectedTests.length === filteredTests.length) {
      setSelectedTests([]);
    } else {
      setSelectedTests(filteredTests.map((t) => t.id));
    }
  };

  const toggleGuardrail = (id) => {
    if (selectedGuardrails.includes(id)) {
      setSelectedGuardrails(selectedGuardrails.filter((g) => g !== id));
    } else {
      setSelectedGuardrails([...selectedGuardrails, id]);
    }
  };

  const openCreateModal = () => {
    setNewTitle('');
    setNewPrompt('');
    setNewExpected('');
    setNewCategory('SECURITY_PROMPT_INJECTION');
    setNewSeverity('HIGH');
    setSaveError(null);
    setFormSubmitted(false);
    setIsModalOpen(true);
  };

  const handleCreateTestCase = async (e) => {
    e.preventDefault();
    setFormSubmitted(true);
    setSaveError(null);

    if (!newTitle.trim() || !newPrompt.trim()) {
      setSaveError('Please fill in all required fields (Scenario Title and Input Prompt).');
      return;
    }

    if (!activeProject) {
      setSaveError('No active project selected. Please select a project first.');
      return;
    }

    setCreatingTC(true);
    try {
      const created = await apiService.createTestCase({
        projectId: activeProject.id,
        title: newTitle.trim(),
        category: newCategory,
        inputPrompt: newPrompt.trim(),
        expectedBehavior: newExpected.trim() || 'Agent maintains safe boundaries',
        severity: newSeverity,
        contextDocuments: []
      });

      setSaveSuccess(`Scenario "${newTitle.trim()}" created successfully!`);
      setTimeout(() => setSaveSuccess(null), 5000);

      setIsModalOpen(false);
      setNewTitle('');
      setNewPrompt('');
      setNewExpected('');
      setFormSubmitted(false);

      await fetchTests(created?.id);
    } catch (err) {
      console.error('Failed to create test case', err);
      setSaveError(err.message || 'Failed to save test scenario. Please check backend connection.');
    } finally {
      setCreatingTC(false);
    }
  };

  const handleRunExecution = async () => {
    if (selectedTests.length === 0 || !activeProject) return;
    setExecuting(true);
    setExecutionResult(null);

    try {
      const runs = await apiService.executeRun({
        projectId: activeProject.id,
        testCaseIds: selectedTests,
        executionMode,
        guardrails: executionMode === 'SECURED' ? selectedGuardrails : []
      });
      setExecutionResult(Array.isArray(runs) ? runs : [runs]);
    } catch (err) {
      console.error('Execution failed', err);
    } finally {
      setExecuting(false);
    }
  };

  const filteredTests = testCases.filter((t) => {
    if (selectedCategory === 'ALL') return true;
    return (t.category || '').includes(selectedCategory);
  });

  if (!activeProject) {
    return (
      <div>
        <div className="page-header">
          <div>
            <h1 className="page-title">AI Test Studio</h1>
            <p className="page-subtitle">Configure attack scenarios and execute agent runs</p>
          </div>
        </div>
        <EmptyState
          title="No Project Active"
          description="Select or create a project first before running test suites."
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

  if (loading && testCases.length === 0) {
    return <LoadingSpinner message="Loading test suites and guardrail policies..." />;
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">AI Test Studio</h1>
          <p className="page-subtitle">
            Configure attack scenarios, select security guardrails, and execute agent runs for <strong className="text-cyan">{activeProject?.name}</strong>
          </p>
        </div>
        <button className="btn btn-primary" onClick={openCreateModal}>
          <Plus size={16} />
          Add Test Scenario
        </button>
      </div>

      {/* Global Success Notification */}
      {saveSuccess && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          padding: '0.85rem 1.25rem',
          background: 'rgba(16, 185, 129, 0.15)',
          border: '1px solid #10b981',
          borderRadius: '8px',
          color: '#a7f3d0',
          marginBottom: '1.25rem',
          fontSize: '0.88rem'
        }}>
          <CheckCircle2 size={18} color="#10b981" />
          <span>{saveSuccess}</span>
        </div>
      )}

      <div className="studio-layout">
        {/* Left Column: Test Cases Browser */}
        <div>
          <Card
            title="Available Test Scenarios"
            subtitle={`${filteredTests.length} scenarios configured`}
            action={
              filteredTests.length > 0 && (
                <button className="btn btn-secondary btn-sm" onClick={selectAll}>
                  {selectedTests.length === filteredTests.length ? 'Deselect All' : 'Select All Filtered'}
                </button>
              )
            }
          >
            {/* Category Filter Pills */}
            <div className="filter-pills">
              {[
                { id: 'ALL', label: 'All' },
                { id: 'SECURITY_PROMPT_INJECTION', label: 'Prompt Injection' },
                { id: 'SECURITY_JAILBREAK', label: 'Jailbreak' },
                { id: 'SECURITY_AGENTDOJO_INDIRECT_INJECTION', label: 'Indirect Injection' },
                { id: 'RELIABILITY_HALLUCINATION', label: 'Hallucination' },
                { id: 'RELIABILITY_RELEVANCE', label: 'Relevance' }
              ].map((cat) => (
                <button
                  key={cat.id}
                  className={`filter-pill ${selectedCategory === cat.id ? 'active' : ''}`}
                  onClick={() => setSelectedCategory(cat.id)}
                >
                  {cat.label}
                </button>
              ))}
            </div>

            {/* Test Case List or Empty State */}
            {filteredTests.length === 0 ? (
              <EmptyState
                title="No Test Scenarios Found"
                description="Create a test scenario with an attack prompt or evaluation query to execute against your agent."
                action={
                  <button className="btn btn-primary btn-sm" onClick={openCreateModal}>
                    <Plus size={14} /> Add Scenario
                  </button>
                }
              />
            ) : (
              <div>
                {filteredTests.map((tc) => {
                  const isSelected = selectedTests.includes(tc.id);
                  return (
                    <div
                      key={tc.id}
                      className={`test-case-item ${isSelected ? 'selected' : ''}`}
                      onClick={() => toggleSelectTest(tc.id)}
                    >
                      <input
                        type="checkbox"
                        className="test-checkbox"
                        checked={isSelected}
                        onChange={() => {}}
                      />
                      <div style={{ flex: 1 }}>
                        <div className="flex items-center justify-between">
                          <span style={{ fontWeight: 600, fontSize: '0.9rem', color: isSelected ? 'var(--text-primary)' : 'var(--text-secondary)' }}>
                            {tc.title}
                          </span>
                          <Badge variant={tc.severity}>{tc.severity}</Badge>
                        </div>
                        <div className="code-snippet" style={{ margin: '0.5rem 0 0 0', padding: '0.5rem 0.75rem', fontSize: '0.75rem' }}>
                          {tc.inputPrompt}
                        </div>
                        <div className="test-meta">
                          <Badge variant="low" style={{ fontSize: '0.65rem' }}>{tc.category}</Badge>
                          <span>• Expected: {tc.expectedBehavior}</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </Card>
        </div>

        {/* Right Column: Execution Configuration */}
        <div>
          <Card title="Execution Controls" subtitle="Select agent mode and active guardrails">
            <div className="form-group">
              <label className="form-label">Execution Mode</label>
              <div className="mode-toggle-group">
                <button
                  type="button"
                  className={`mode-btn ${executionMode === 'BASELINE' ? 'active-baseline' : ''}`}
                  onClick={() => setExecutionMode('BASELINE')}
                >
                  Baseline (Raw)
                </button>
                <button
                  type="button"
                  className={`mode-btn ${executionMode === 'SECURED' ? 'active-secured' : ''}`}
                  onClick={() => setExecutionMode('SECURED')}
                >
                  Secured (Guarded)
                </button>
              </div>
            </div>

            {executionMode === 'SECURED' ? (
              <div className="form-group">
                <label className="form-label">Active Guardrails AI Rules</label>
                {availableGuardrails.map((g) => {
                  const isChecked = selectedGuardrails.includes(g.id);
                  return (
                    <div key={g.id} className="rule-check-item">
                      <div>
                        <div style={{ fontWeight: 600 }}>{g.name}</div>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{g.desc}</div>
                      </div>
                      <input
                        type="checkbox"
                        className="test-checkbox"
                        checked={isChecked}
                        onChange={() => toggleGuardrail(g.id)}
                      />
                    </div>
                  );
                })}
              </div>
            ) : (
              <div style={{ padding: '0.75rem', background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.25)', borderRadius: 'var(--radius-md)', marginBottom: '1rem', fontSize: '0.8rem', color: 'var(--mode-baseline)' }}>
                <AlertTriangle size={16} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'text-bottom' }} />
                <strong>Baseline Mode</strong> executes the agent without pre- or post-execution guardrail interception.
              </div>
            )}

            <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
              <div className="flex items-center justify-between" style={{ marginBottom: '0.75rem', fontSize: '0.85rem' }}>
                <span className="text-muted">Selected Tests:</span>
                <strong className="text-cyan">{selectedTests.length}</strong>
              </div>

              <button
                className="btn btn-primary"
                style={{ width: '100%' }}
                disabled={executing || selectedTests.length === 0}
                onClick={handleRunExecution}
              >
                {executing ? (
                  <>Executing Agent Run...</>
                ) : (
                  <>
                    <Play size={16} fill="#fff" />
                    Execute Test Run ({selectedTests.length})
                  </>
                )}
              </button>
            </div>
          </Card>

          {/* Execution Output Preview */}
          {executionResult && (
            <Card title="Latest Run Results" subtitle={`${executionResult.length} tests completed`} style={{ marginTop: '1.25rem' }}>
              {executionResult.map((res) => (
                <div key={res.id} style={{ padding: '0.75rem', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', marginBottom: '0.5rem' }}>
                  <div className="flex items-center justify-between">
                    <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>#{res.id} - {res.testTitle || 'Test Run'}</span>
                    {res.isVulnerable ? <Badge variant="danger">Vulnerable</Badge> : <Badge variant="success">Secured</Badge>}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                    Score: <strong>{res.overallScore != null ? `${res.overallScore}%` : 'N/A'}</strong> | Latency: <strong>{res.latencyMs != null ? `${res.latencyMs}ms` : 'N/A'}</strong>
                  </div>
                  <button
                    className="btn btn-secondary btn-sm"
                    style={{ width: '100%', marginTop: '0.5rem' }}
                    onClick={() => navigate(`/traces?runId=${res.id}`)}
                  >
                    Inspect OTel Trace
                  </button>
                </div>
              ))}
            </Card>
          )}
        </div>
      </div>

      {/* Create Test Case Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Add Test Scenario">
        <form onSubmit={handleCreateTestCase}>
          {saveError && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.75rem 1rem',
              background: 'rgba(239, 68, 68, 0.15)',
              border: '1px solid #ef4444',
              borderRadius: '6px',
              color: '#fca5a5',
              marginBottom: '1rem',
              fontSize: '0.82rem'
            }}>
              <AlertCircle size={16} color="#ef4444" />
              <span>{saveError}</span>
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Scenario Title *</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Prompt Extraction Attack"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              style={{
                borderColor: formSubmitted && !newTitle.trim() ? '#ef4444' : undefined
              }}
            />
            {formSubmitted && !newTitle.trim() && (
              <span style={{ fontSize: '0.72rem', color: '#ef4444', marginTop: '4px', display: 'block' }}>
                Scenario title is required.
              </span>
            )}
          </div>

          <div className="form-group">
            <label className="form-label">Category</label>
            <select
              className="form-select"
              value={newCategory}
              onChange={(e) => setNewCategory(e.target.value)}
            >
              <option value="SECURITY_PROMPT_INJECTION">Security: Prompt Injection</option>
              <option value="SECURITY_JAILBREAK">Security: Jailbreak</option>
              <option value="SECURITY_AGENTDOJO_INDIRECT_INJECTION">Security: Indirect Prompt Injection (AgentDojo)</option>
              <option value="RELIABILITY_HALLUCINATION">Reliability: Hallucination Benchmark</option>
              <option value="RELIABILITY_RELEVANCE">Reliability: Answer Relevancy</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Severity Level</label>
            <select
              className="form-select"
              value={newSeverity}
              onChange={(e) => setNewSeverity(e.target.value)}
            >
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Input Payload / Attack Prompt *</label>
            <textarea
              className="form-textarea"
              placeholder="Enter the attack payload prompt to test against the agent..."
              rows={4}
              value={newPrompt}
              onChange={(e) => setNewPrompt(e.target.value)}
              style={{
                borderColor: formSubmitted && !newPrompt.trim() ? '#ef4444' : undefined
              }}
            />
            {formSubmitted && !newPrompt.trim() && (
              <span style={{ fontSize: '0.72rem', color: '#ef4444', marginTop: '4px', display: 'block' }}>
                Input attack prompt is required.
              </span>
            )}
          </div>

          <div className="form-group">
            <label className="form-label">Expected Behavior</label>
            <textarea
              className="form-textarea"
              placeholder="e.g. Agent must refuse unauthorized command and maintain safety guardrails."
              rows={2}
              value={newExpected}
              onChange={(e) => setNewExpected(e.target.value)}
            />
          </div>

          <div className="flex justify-between items-center" style={{ marginTop: '1.5rem' }}>
            <button type="button" className="btn btn-secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={creatingTC}
              style={{ minWidth: '130px', justifyContent: 'center' }}
            >
              {creatingTC ? (
                <>
                  <LoadingSpinner size="small" />
                  <span style={{ marginLeft: '6px' }}>Saving...</span>
                </>
              ) : (
                'Save Scenario'
              )}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default TestStudio;
