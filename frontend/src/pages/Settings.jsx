import React, { useState } from 'react';
import {
  Settings as SettingsIcon,
  Shield,
  Key,
  Cpu,
  Server,
  Lock,
  CheckCircle2,
  Info
} from 'lucide-react';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';

export const Settings = () => {
  const [model, setModel] = useState('gemini-1.5-flash');
  const [guardrailsEnabled, setGuardrailsEnabled] = useState(true);
  const [deepEvalEnabled, setDeepEvalEnabled] = useState(true);
  const [otelTracingEnabled, setOtelTracingEnabled] = useState(true);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Platform Settings</h1>
          <p className="page-subtitle">
            Configure LLM endpoints, security policies, and observability integrations
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '850px' }}>
        {/* AI Provider Status */}
        <Card title="AI Provider & Model Configuration" subtitle="Primary LLM backend for agent reasoning and judge evaluations">
          <div className="form-group">
            <label className="form-label">Active LLM Provider</label>
            <div className="flex items-center justify-between" style={{ padding: '0.85rem', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
              <div className="flex items-center gap-3">
                <div style={{ width: '32px', height: '32px', borderRadius: 'var(--radius-md)', background: 'linear-gradient(135deg, #4285F4, #34A853)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: 700 }}>
                  G
                </div>
                <div>
                  <strong>Google Gemini API</strong>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Status: Active (Configured via backend .env)</div>
                </div>
              </div>
              <Badge variant="success">CONNECTED</Badge>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Default Evaluation Model</label>
            <select
              className="form-select"
              value={model}
              onChange={(e) => setModel(e.target.value)}
            >
              <option value="gemini-1.5-flash">gemini-1.5-flash (Fast & Cost Efficient)</option>
              <option value="gemini-1.5-pro">gemini-1.5-pro (High Reasoning Depth)</option>
            </select>
          </div>

          <div style={{ padding: '0.75rem', background: 'rgba(6, 182, 212, 0.08)', border: '1px solid rgba(6, 182, 212, 0.2)', borderRadius: 'var(--radius-md)', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            <Lock size={14} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'text-bottom' }} />
            <strong>Security Notice:</strong> API keys are securely managed through environment variables (`GEMINI_API_KEY`) and are never exposed to the frontend browser context.
          </div>
        </Card>

        {/* Guardrails AI Controls */}
        <Card title="Guardrails AI Security Engine" subtitle="Real-time input and output safety policy enforcement">
          <div className="flex items-center justify-between" style={{ padding: '0.85rem 0', borderBottom: '1px solid var(--border-color)' }}>
            <div>
              <strong>Prompt Injection Guardrail</strong>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Intercepts directive overrides, DAN variants, and system extraction</div>
            </div>
            <input
              type="checkbox"
              className="test-checkbox"
              checked={guardrailsEnabled}
              onChange={(e) => setGuardrailsEnabled(e.target.checked)}
            />
          </div>

          <div className="flex items-center justify-between" style={{ padding: '0.85rem 0', borderBottom: '1px solid var(--border-color)' }}>
            <div>
              <strong>PII Redaction & Masking</strong>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Automatically anonymizes credit cards, emails, and SSNs</div>
            </div>
            <input
              type="checkbox"
              className="test-checkbox"
              checked={guardrailsEnabled}
              onChange={(e) => setGuardrailsEnabled(e.target.checked)}
            />
          </div>

          <div className="flex items-center justify-between" style={{ padding: '0.85rem 0' }}>
            <div>
              <strong>SQL & Code Injection Interceptor</strong>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Validates dynamic tool arguments against command execution payloads</div>
            </div>
            <input
              type="checkbox"
              className="test-checkbox"
              checked={guardrailsEnabled}
              onChange={(e) => setGuardrailsEnabled(e.target.checked)}
            />
          </div>
        </Card>

        {/* Observability Settings */}
        <Card title="Observability & DeepEval Configuration" subtitle="Telemetry collection and reliability judge thresholds">
          <div className="flex items-center justify-between" style={{ padding: '0.85rem 0', borderBottom: '1px solid var(--border-color)' }}>
            <div>
              <strong>OpenTelemetry Distributed Tracing</strong>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Capture span latencies, tokens, and node hierarchies</div>
            </div>
            <Badge variant="success">ENABLED</Badge>
          </div>

          <div className="flex items-center justify-between" style={{ padding: '0.85rem 0' }}>
            <div>
              <strong>DeepEval Faithfulness Minimum Threshold</strong>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Flags runs scoring under 85% on faithfulness criteria</div>
            </div>
            <span style={{ fontWeight: 600, color: 'var(--accent-cyan)' }}>0.85 (85%)</span>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Settings;
