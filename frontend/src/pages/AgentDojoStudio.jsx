import React, { useState, useEffect } from 'react';
import {
  Shield,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Play,
  CheckCircle2,
  XCircle,
  Clock,
  Layers,
  Terminal,
  Activity,
  Server,
  Mail,
  DollarSign,
  MessageSquare,
  Plane,
  RefreshCw,
  Sliders,
  Eye,
  Lock,
  Unlock,
  ChevronRight,
  ExternalLink
} from 'lucide-react';
import apiService from '../services/apiService';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import LoadingSpinner from '../components/common/LoadingSpinner';

export const AgentDojoStudio = () => {
  const [suites, setSuites] = useState([]);
  const [selectedSuite, setSelectedSuite] = useState('ALL');
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [executionMode, setExecutionMode] = useState('SECURED');
  const [selectedGuardrails, setSelectedGuardrails] = useState([
    'PromptInjectionDetector',
    'PIIAnonymizer',
    'SQLInjectionGuard'
  ]);
  const [modelName, setModelName] = useState('gemini-1.5-flash');
  const [runResult, setRunResult] = useState(null);
  const [expandedTrace, setExpandedTrace] = useState(null);

  const suiteIcons = {
    workspace: Mail,
    banking: DollarSign,
    slack: MessageSquare,
    travel: Plane
  };

  const availableGuardrails = [
    { id: 'PromptInjectionDetector', name: 'Indirect & Direct Injection Guard', desc: 'Scans prompt and tool returns for embedded overrides' },
    { id: 'PIIAnonymizer', name: 'PII & Secrets Anonymizer', desc: 'Masks emails, IBANs, and credit card numbers' },
    { id: 'SQLInjectionGuard', name: 'Tool Parameter Validator', desc: 'Blocks SQL syntax and unauthorized shell params' },
    { id: 'ToxicityFilter', name: 'Harmful Content Filter', desc: 'Intercepts toxic, phishing, and defamatory payloads' }
  ];

  useEffect(() => {
    loadSuitesAndScenarios();
  }, []);

  const loadSuitesAndScenarios = async () => {
    try {
      setLoading(true);
      const [suitesData, scenariosData] = await Promise.all([
        apiService.getAgentDojoSuites(),
        apiService.getAgentDojoScenarios()
      ]);
      setSuites(suitesData || []);
      setScenarios(scenariosData || []);
      if (scenariosData && scenariosData.length > 0) {
        setSelectedScenario(scenariosData[0]);
      }
    } catch (err) {
      console.error('Failed to load AgentDojo data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSuiteSelect = async (suiteId) => {
    setSelectedSuite(suiteId);
    try {
      const data = await apiService.getAgentDojoScenarios(suiteId);
      setScenarios(data || []);
      if (data && data.length > 0) {
        setSelectedScenario(data[0]);
      }
    } catch (err) {
      console.error(`Failed to load scenarios for suite ${suiteId}`, err);
    }
  };

  const toggleGuardrail = (id) => {
    if (selectedGuardrails.includes(id)) {
      setSelectedGuardrails(selectedGuardrails.filter((g) => g !== id));
    } else {
      setSelectedGuardrails([...selectedGuardrails, id]);
    }
  };

  const handleExecuteBenchmark = async () => {
    if (!selectedScenario) return;
    try {
      setExecuting(true);
      setRunResult(null);
      const payload = {
        scenarioId: selectedScenario.id,
        executionMode: executionMode,
        guardrails: executionMode === 'SECURED' ? selectedGuardrails : [],
        modelName: modelName
      };
      const result = await apiService.runAgentDojoBenchmark(payload);
      setRunResult(result);
    } catch (err) {
      console.error('Execution failed', err);
    } finally {
      setExecuting(false);
    }
  };

  if (loading) {
    return (
      <div className="page-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="page-container">
      {/* Header Banner */}
      <div className="page-header" style={{ marginBottom: '1.5rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
            <h1 className="page-title" style={{ margin: 0 }}>AgentDojo Benchmark Studio</h1>
            <Badge variant="info">ETH Zurich SPY Lab</Badge>
            <Badge variant="cyan">Dual-Verdict Evaluation</Badge>
          </div>
          <p className="page-subtitle" style={{ margin: 0 }}>
            Dynamic evaluation framework for autonomous AI agent tool security against indirect prompt injections & untrusted data flows.
          </p>
        </div>
        <button
          className="btn btn-secondary"
          onClick={loadSuitesAndScenarios}
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
        >
          <RefreshCw size={16} />
          <span>Refresh Suites</span>
        </button>
      </div>

      {/* Suite Selector Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        <div
          onClick={() => handleSuiteSelect('ALL')}
          style={{
            padding: '1rem',
            borderRadius: '10px',
            cursor: 'pointer',
            border: selectedSuite === 'ALL' ? '2px solid var(--primary-cyan, #06b6d4)' : '1px solid var(--border-color, #222e3e)',
            backgroundColor: selectedSuite === 'ALL' ? 'rgba(6, 182, 212, 0.08)' : 'var(--card-bg, #111a28)',
            transition: 'all 0.2s ease'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>All Suites</span>
            <Layers size={18} color="#06b6d4" />
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted, #94a3b8)' }}>
            {scenarios.length} Total Scenarios
          </div>
        </div>

        {suites.map((st) => {
          const IconComp = suiteIcons[st.id] || Server;
          const isSelected = selectedSuite === st.id;
          return (
            <div
              key={st.id}
              onClick={() => handleSuiteSelect(st.id)}
              style={{
                padding: '1rem',
                borderRadius: '10px',
                cursor: 'pointer',
                border: isSelected ? '2px solid var(--primary-cyan, #06b6d4)' : '1px solid var(--border-color, #222e3e)',
                backgroundColor: isSelected ? 'rgba(6, 182, 212, 0.08)' : 'var(--card-bg, #111a28)',
                transition: 'all 0.2s ease'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>{st.name}</span>
                <IconComp size={18} color={isSelected ? '#06b6d4' : '#64748b'} />
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted, #94a3b8)' }}>
                <span>{st.userTaskCount} Tasks</span>
                <span>•</span>
                <span style={{ color: '#ef4444' }}>{st.injectionTaskCount} Injections</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Studio Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '380px 1fr', gap: '1.5rem', alignItems: 'start' }}>
        
        {/* Left Column: Scenario Catalog & Runner Config */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Scenario Picker */}
          <Card title="Adversarial Scenarios">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '360px', overflowY: 'auto', paddingRight: '4px' }}>
              {scenarios.map((sc) => {
                const isSelected = selectedScenario && selectedScenario.id === sc.id;
                return (
                  <div
                    key={sc.id}
                    onClick={() => setSelectedScenario(sc)}
                    style={{
                      padding: '0.85rem',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      border: isSelected ? '1px solid var(--primary-cyan, #06b6d4)' : '1px solid var(--border-color, #222e3e)',
                      backgroundColor: isSelected ? 'rgba(6, 182, 212, 0.12)' : 'var(--bg-secondary, #0c1421)',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                      <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>{sc.name}</span>
                      <Badge variant={sc.severity === 'CRITICAL' ? 'danger' : 'warning'}>{sc.severity}</Badge>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted, #94a3b8)', marginBottom: '0.25rem' }}>
                      Suite: <strong style={{ color: '#e2e8f0' }}>{sc.suite}</strong>
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted, #64748b)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {sc.attackType}
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>

          {/* Execution Configuration Card */}
          <Card title="Execution Parameters">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {/* Execution Mode Toggle */}
              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted, #94a3b8)', display: 'block', marginBottom: '0.5rem' }}>
                  Execution Mode
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                  <button
                    className={`btn ${executionMode === 'SECURED' ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ justifyContent: 'center', fontSize: '0.8rem', padding: '0.5rem' }}
                    onClick={() => setExecutionMode('SECURED')}
                  >
                    <Lock size={14} style={{ marginRight: '4px' }} />
                    SECURED
                  </button>
                  <button
                    className={`btn ${executionMode === 'BASELINE' ? 'btn-danger' : 'btn-secondary'}`}
                    style={{ justifyContent: 'center', fontSize: '0.8rem', padding: '0.5rem' }}
                    onClick={() => setExecutionMode('BASELINE')}
                  >
                    <Unlock size={14} style={{ marginRight: '4px' }} />
                    BASELINE
                  </button>
                </div>
              </div>

              {/* Model Picker */}
              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted, #94a3b8)', display: 'block', marginBottom: '0.35rem' }}>
                  Target LLM
                </label>
                <select
                  className="form-control"
                  value={modelName}
                  onChange={(e) => setModelName(e.target.value)}
                  style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: 'var(--bg-secondary, #0c1421)', color: '#fff', border: '1px solid #222e3e' }}
                >
                  <option value="gemini-1.5-flash">Google Gemini 1.5 Flash (Default)</option>
                  <option value="gemini-1.5-pro">Google Gemini 1.5 Pro</option>
                  <option value="gpt-4o-mini">OpenAI GPT-4o Mini</option>
                  <option value="claude-3-5-sonnet">Anthropic Claude 3.5 Sonnet</option>
                </select>
              </div>

              {/* Guardrails (Only enabled if SECURED) */}
              {executionMode === 'SECURED' && (
                <div>
                  <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted, #94a3b8)', display: 'block', marginBottom: '0.5rem' }}>
                    Active SentinelAI Guardrails
                  </label>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {availableGuardrails.map((g) => {
                      const isChecked = selectedGuardrails.includes(g.id);
                      return (
                        <div
                          key={g.id}
                          onClick={() => toggleGuardrail(g.id)}
                          style={{
                            display: 'flex',
                            alignItems: 'flex-start',
                            gap: '0.5rem',
                            padding: '0.5rem',
                            borderRadius: '6px',
                            background: isChecked ? 'rgba(6, 182, 212, 0.06)' : 'transparent',
                            border: '1px solid #1e293b',
                            cursor: 'pointer'
                          }}
                        >
                          <input type="checkbox" checked={isChecked} onChange={() => {}} style={{ marginTop: '2px' }} />
                          <div>
                            <div style={{ fontSize: '0.78rem', fontWeight: 600, color: '#e2e8f0' }}>{g.name}</div>
                            <div style={{ fontSize: '0.7rem', color: '#64748b' }}>{g.desc}</div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Action Button */}
              <button
                className="btn btn-primary"
                onClick={handleExecuteBenchmark}
                disabled={executing || !selectedScenario}
                style={{ marginTop: '0.5rem', justifyContent: 'center', width: '100%', padding: '0.75rem', fontWeight: 600 }}
              >
                {executing ? (
                  <>
                    <LoadingSpinner size="small" />
                    <span style={{ marginLeft: '0.5rem' }}>Evaluating Benchmark...</span>
                  </>
                ) : (
                  <>
                    <Play size={16} style={{ marginRight: '0.5rem' }} />
                    <span>Run AgentDojo Scenario</span>
                  </>
                )}
              </button>
            </div>
          </Card>
        </div>

        {/* Right Column: Scenario Details & Execution Dual-Verdicts */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          
          {/* Selected Scenario Preview */}
          {selectedScenario && (
            <Card title={`Scenario Specification: ${selectedScenario.name}`}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem' }}>
                  <div style={{ padding: '0.6rem', borderRadius: '6px', background: 'var(--bg-secondary, #0c1421)', border: '1px solid #1e293b' }}>
                    <div style={{ fontSize: '0.72rem', color: '#94a3b8' }}>Suite & Category</div>
                    <div style={{ fontSize: '0.82rem', fontWeight: 600, color: '#06b6d4' }}>
                      {selectedScenario.suite.toUpperCase()} • {selectedScenario.category}
                    </div>
                  </div>
                  <div style={{ padding: '0.6rem', borderRadius: '6px', background: 'var(--bg-secondary, #0c1421)', border: '1px solid #1e293b' }}>
                    <div style={{ fontSize: '0.72rem', color: '#94a3b8' }}>Attack Classification</div>
                    <div style={{ fontSize: '0.82rem', fontWeight: 600, color: '#f59e0b' }}>
                      {selectedScenario.attackType}
                    </div>
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.78rem', fontWeight: 600, color: '#94a3b8', marginBottom: '0.25rem' }}>
                    Legitimate User Task Prompt:
                  </div>
                  <div style={{ padding: '0.6rem 0.8rem', borderRadius: '6px', background: 'var(--bg-secondary, #0c1421)', fontSize: '0.82rem', color: '#f1f5f9', borderLeft: '3px solid #10b981' }}>
                    "{selectedScenario.userTaskPrompt}"
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.78rem', fontWeight: 600, color: '#94a3b8', marginBottom: '0.25rem' }}>
                    Attacker Indirect Injection Goal:
                  </div>
                  <div style={{ padding: '0.6rem 0.8rem', borderRadius: '6px', background: 'var(--bg-secondary, #0c1421)', fontSize: '0.82rem', color: '#fca5a5', borderLeft: '3px solid #ef4444' }}>
                    "{selectedScenario.injectionTaskGoal}"
                  </div>
                </div>

                {selectedScenario.attackPayload && (
                  <div>
                    <div style={{ fontSize: '0.78rem', fontWeight: 600, color: '#94a3b8', marginBottom: '0.25rem' }}>
                      Embedded Poison Payload (Untrusted Tool Response):
                    </div>
                    <div style={{ padding: '0.5rem 0.75rem', borderRadius: '6px', background: '#1c1917', fontSize: '0.78rem', color: '#fb923c', fontFamily: 'monospace' }}>
                      {selectedScenario.attackPayload}
                    </div>
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* Benchmark Execution Results & Dual Verdicts */}
          {runResult && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              
              {/* Dual Verdict Cards Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                
                {/* 1. AgentDojo Native Benchmark Verdict */}
                <div
                  style={{
                    padding: '1.25rem',
                    borderRadius: '10px',
                    border: runResult.benchmarkVerdict?.attackSuccessful ? '1px solid #ef4444' : '1px solid #10b981',
                    background: runResult.benchmarkVerdict?.attackSuccessful ? 'rgba(239, 68, 68, 0.08)' : 'rgba(16, 185, 129, 0.08)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Activity size={20} color={runResult.benchmarkVerdict?.attackSuccessful ? '#ef4444' : '#10b981'} />
                      <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>AgentDojo Native Verdict</span>
                    </div>
                    <Badge variant={runResult.benchmarkVerdict?.attackSuccessful ? 'danger' : 'success'}>
                      {runResult.benchmarkVerdict?.attackSuccessful ? 'ATTACK SUCCEEDED' : 'ATTACK PREVENTED'}
                    </Badge>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.8rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#94a3b8' }}>User Task Completed:</span>
                      <strong style={{ color: runResult.benchmarkVerdict?.userTaskCompleted ? '#10b981' : '#f59e0b' }}>
                        {runResult.benchmarkVerdict?.userTaskCompleted ? 'YES (Preserved)' : 'NO (Disrupted)'}
                      </strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#94a3b8' }}>Adversarial Exploit Executed:</span>
                      <strong style={{ color: runResult.benchmarkVerdict?.attackSuccessful ? '#ef4444' : '#10b981' }}>
                        {runResult.benchmarkVerdict?.attackSuccessful ? 'YES (VULNERABLE)' : 'NO (BLOCKED)'}
                      </strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#94a3b8' }}>Native Defense Layer:</span>
                      <span style={{ color: '#e2e8f0' }}>{runResult.benchmarkVerdict?.agentdojoNativeDefense}</span>
                    </div>
                  </div>
                </div>

                {/* 2. SentinelAI Security Containment Verdict */}
                <div
                  style={{
                    padding: '1.25rem',
                    borderRadius: '10px',
                    border: runResult.sentinelaiVerdict?.blocked ? '1px solid #06b6d4' : (runResult.isVulnerable ? '1px solid #ef4444' : '1px solid #10b981'),
                    background: 'rgba(6, 182, 212, 0.08)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <ShieldCheck size={20} color="#06b6d4" />
                      <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>SentinelAI Defense Verdict</span>
                    </div>
                    <Badge variant={runResult.sentinelaiVerdict?.containmentRate === 1.0 ? 'cyan' : 'danger'}>
                      {runResult.sentinelaiVerdict?.containmentRate === 1.0 ? '100% CONTAINED' : '0% CONTAINED'}
                    </Badge>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.8rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#94a3b8' }}>Guardrails Engine Status:</span>
                      <strong style={{ color: runResult.sentinelaiVerdict?.guardrailsActive ? '#06b6d4' : '#94a3b8' }}>
                        {runResult.sentinelaiVerdict?.guardrailsActive ? 'ACTIVE & ENFORCING' : 'BYPASS (BASELINE)'}
                      </strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#94a3b8' }}>Security Threats Neutralized:</span>
                      <strong style={{ color: runResult.sentinelaiVerdict?.findingsCount > 0 ? '#10b981' : '#94a3b8' }}>
                        {runResult.sentinelaiVerdict?.findingsCount || 0} Threat Findings
                      </strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#94a3b8' }}>Execution Latency:</span>
                      <span style={{ color: '#e2e8f0' }}>{runResult.latencyMs} ms</span>
                    </div>
                  </div>
                </div>

              </div>

              {/* Tool Execution Interception Timeline */}
              <Card title="Tool Execution Trace & Interception Waterfall">
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {runResult.toolTraces && runResult.toolTraces.map((trace, idx) => {
                    const isBlocked = trace.guardrail_status === 'BLOCKED';
                    const isBypassed = trace.guardrail_status === 'BYPASSED_BASELINE';
                    const isExpanded = expandedTrace === idx;
                    return (
                      <div
                        key={idx}
                        style={{
                          borderRadius: '8px',
                          border: isBlocked ? '1px solid #ef4444' : (isBypassed ? '1px solid #f59e0b' : '1px solid #1e293b'),
                          background: 'var(--bg-secondary, #0c1421)',
                          overflow: 'hidden'
                        }}
                      >
                        <div
                          onClick={() => setExpandedTrace(isExpanded ? null : idx)}
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            padding: '0.75rem 1rem',
                            cursor: 'pointer'
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#64748b' }}>#{idx + 1}</span>
                            <Terminal size={16} color="#06b6d4" />
                            <strong style={{ fontSize: '0.85rem', color: '#f8fafc' }}>{trace.tool_name}</strong>
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{trace.latency_ms} ms</span>
                            <Badge variant={isBlocked ? 'danger' : (isBypassed ? 'warning' : 'success')}>
                              {trace.guardrail_status}
                            </Badge>
                            <ChevronRight size={14} style={{ transform: isExpanded ? 'rotate(90deg)' : 'none', transition: 'transform 0.2s' }} />
                          </div>
                        </div>

                        {isExpanded && (
                          <div style={{ padding: '0.75rem 1rem', borderTop: '1px solid #1e293b', background: '#080d14', fontSize: '0.75rem' }}>
                            <div style={{ marginBottom: '0.5rem' }}>
                              <strong style={{ color: '#94a3b8' }}>Arguments:</strong>
                              <pre style={{ margin: '0.25rem 0', color: '#38bdf8', fontFamily: 'monospace' }}>
                                {JSON.stringify(trace.arguments, null, 2)}
                              </pre>
                            </div>
                            <div>
                              <strong style={{ color: '#94a3b8' }}>Raw Tool Output / Payload:</strong>
                              <pre style={{ margin: '0.25rem 0', color: isBlocked ? '#fca5a5' : '#a7f3d0', fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                                {trace.raw_output}
                              </pre>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </Card>

              {/* Security Findings List */}
              {runResult.securityFindings && runResult.securityFindings.length > 0 && (
                <Card title="Neutralized Security Findings">
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {runResult.securityFindings.map((f, idx) => (
                      <div
                        key={idx}
                        style={{
                          padding: '0.75rem 1rem',
                          borderRadius: '8px',
                          borderLeft: '4px solid #ef4444',
                          background: 'var(--bg-secondary, #0c1421)',
                          border: '1px solid #1e293b',
                          borderLeftColor: '#ef4444'
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                          <span style={{ fontWeight: 600, fontSize: '0.85rem', color: '#f8fafc' }}>{f.guardrailRule}</span>
                          <Badge variant="danger">{f.threatType}</Badge>
                        </div>
                        <div style={{ fontSize: '0.78rem', color: '#94a3b8', marginBottom: '0.35rem' }}>
                          {f.remediationNotes}
                        </div>
                        <div style={{ fontSize: '0.72rem', color: '#fca5a5', fontFamily: 'monospace', background: '#1c1917', padding: '0.35rem 0.5rem', borderRadius: '4px' }}>
                          Flagged: {f.flaggedContent}
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              )}

              {/* Agent Final Output */}
              <Card title="Agent Final Output">
                <div style={{ padding: '0.85rem', borderRadius: '8px', background: 'var(--bg-secondary, #0c1421)', fontSize: '0.85rem', color: '#f1f5f9', whiteSpace: 'pre-wrap', border: '1px solid #1e293b' }}>
                  {runResult.finalOutput}
                </div>
              </Card>

            </div>
          )}

        </div>

      </div>
    </div>
  );
};

export default AgentDojoStudio;
