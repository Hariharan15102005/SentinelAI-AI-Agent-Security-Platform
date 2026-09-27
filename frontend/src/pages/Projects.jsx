import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Plus,
  ArrowRight,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import Modal from '../components/common/Modal';
import EmptyState from '../components/common/EmptyState';

export const Projects = () => {
  const { projects, activeProject, changeProject, addProject, refreshProjects } = useApp();
  const navigate = useNavigate();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [agentType, setAgentType] = useState('LANGGRAPH');
  const [submitting, setSubmitting] = useState(false);
  const [modalError, setModalError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  const handleOpenModal = () => {
    setModalError(null);
    setName('');
    setDescription('');
    setSystemPrompt('');
    setAgentType('LANGGRAPH');
    setIsModalOpen(true);
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setModalError(null);

    const trimmedName = name.trim();
    if (!trimmedName) {
      setModalError('Project name is required.');
      return;
    }

    if (trimmedName.length > 100) {
      setModalError('Project name cannot exceed 100 characters.');
      return;
    }

    setSubmitting(true);
    try {
      const created = await addProject({
        name: trimmedName,
        description: description.trim() || undefined,
        systemPrompt: systemPrompt.trim() || undefined,
        agentType
      });

      if (created && created.id) {
        setIsModalOpen(false);
        setName('');
        setDescription('');
        setSystemPrompt('');
        setModalError(null);
        setSuccessMessage(`Project "${created.name}" created successfully.`);
        setTimeout(() => {
          setSuccessMessage(null);
        }, 4000);
        if (refreshProjects) {
          await refreshProjects();
        }
      } else {
        setModalError('Failed to create project. Please verify backend service.');
      }
    } catch (err) {
      console.error('Failed to create project', err);
      setModalError(err.message || 'An error occurred while creating the project.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      {/* Success Notification Banner */}
      {successMessage && (
        <div
          className="flex items-center gap-2"
          style={{
            padding: '0.85rem 1.25rem',
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.4)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--color-success)',
            marginBottom: '1.25rem',
            fontSize: '0.9rem',
            fontWeight: 500
          }}
        >
          <CheckCircle2 size={18} />
          <span>{successMessage}</span>
        </div>
      )}

      <div className="page-header">
        <div>
          <h1 className="page-title">Agent Projects</h1>
          <p className="page-subtitle">
            Configure agent architectures, test suites, and security posture scopes
          </p>
        </div>
        <button className="btn btn-primary" onClick={handleOpenModal}>
          <Plus size={16} />
          Create Project
        </button>
      </div>

      {projects.length === 0 ? (
        <EmptyState
          title="No Agent Projects Found"
          description="Register your first AI agent or system prompt to start evaluating vulnerabilities, execution traces, and reliability."
          action={
            <button className="btn btn-primary" onClick={handleOpenModal}>
              <Plus size={16} />
              Create Your First Project
            </button>
          }
        />
      ) : (
        /* Projects Grid */
        <div className="projects-grid">
          {projects.map((p) => {
            const isActive = activeProject?.id === p.id;

            return (
              <Card key={p.id} className="project-card">
                <div>
                  <div className="flex items-center justify-between" style={{ marginBottom: '0.75rem' }}>
                    <Badge variant={isActive ? 'success' : 'low'}>
                      {isActive ? 'ACTIVE SCOPE' : p.agentType}
                    </Badge>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {p.createdAt ? new Date(p.createdAt).toLocaleDateString() : 'Active'}
                    </span>
                  </div>

                  <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
                    {p.name}
                  </h3>

                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.25rem', lineHeight: '1.5' }}>
                    {p.description || 'No description provided.'}
                  </p>

                  <div className="flex gap-4" style={{ padding: '0.75rem', background: 'var(--bg-primary)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', marginBottom: '1.25rem' }}>
                    <div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>TEST CASES</div>
                      <strong style={{ fontSize: '0.95rem' }}>{p.testCaseCount != null ? p.testCaseCount : 0} Scenarios</strong>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>LAST RUN</div>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                        {p.lastRunAt ? new Date(p.lastRunAt).toLocaleDateString() : 'Never'}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between" style={{ paddingTop: '0.75rem', borderTop: '1px solid var(--border-color)' }}>
                  {isActive ? (
                    <span className="text-green" style={{ fontSize: '0.8rem', fontWeight: 600 }}>
                      Currently Selected
                    </span>
                  ) : (
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => changeProject(p.id)}
                    >
                      Select Project
                    </button>
                  )}

                  <button
                    className="btn btn-primary btn-sm"
                    onClick={() => {
                      changeProject(p.id);
                      navigate('/studio');
                    }}
                  >
                    Open Studio <ArrowRight size={14} />
                  </button>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Create Project Modal */}
      <Modal isOpen={isModalOpen} onClose={() => !submitting && setIsModalOpen(false)} title="Register New Agent Project">
        <form onSubmit={handleCreate}>
          {modalError && (
            <div
              className="flex items-center gap-2"
              style={{
                padding: '0.75rem 1rem',
                background: 'rgba(239, 68, 68, 0.15)',
                border: '1px solid rgba(239, 68, 68, 0.4)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--color-danger)',
                marginBottom: '1rem',
                fontSize: '0.85rem'
              }}
            >
              <AlertCircle size={16} />
              <span>{modalError}</span>
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Project / Agent Name *</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Sales Recommendation LangGraph Bot"
              required
              maxLength={100}
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={submitting}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Agent Architecture Framework</label>
            <select
              className="form-select"
              value={agentType}
              onChange={(e) => setAgentType(e.target.value)}
              disabled={submitting}
            >
              <option value="LANGGRAPH">LangGraph StateGraph (Python)</option>
              <option value="LANGCHAIN">LangChain Agent Executor</option>
              <option value="AUTOGEN">Microsoft AutoGen (Planned)</option>
              <option value="CREWAI">CrewAI (Planned)</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea
              className="form-textarea"
              placeholder="Brief description of the agent's target tools and responsibilities..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={submitting}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Base System Prompt</label>
            <textarea
              className="form-textarea"
              placeholder="You are an autonomous AI agent..."
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              disabled={submitting}
            />
          </div>

          <div className="flex justify-between items-center" style={{ marginTop: '1.5rem' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setIsModalOpen(false)}
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={submitting || !name.trim()}
            >
              {submitting ? 'Creating Project...' : 'Create Agent Project'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Projects;
