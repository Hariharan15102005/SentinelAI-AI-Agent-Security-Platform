import React from 'react';
import { Menu, Shield, Bell, ChevronDown } from 'lucide-react';
import { useApp } from '../context/AppContext';

export const Topbar = () => {
  const {
    projects,
    activeProject,
    changeProject,
    notificationCount,
    setIsMobileNavOpen
  } = useApp();

  return (
    <header className="topbar">
      <div className="topbar-left">
        <button
          className="mobile-menu-btn"
          onClick={() => setIsMobileNavOpen(true)}
          aria-label="Open mobile navigation"
        >
          <Menu size={20} />
        </button>

        <div className="project-selector">
          <Shield size={16} className="text-cyan" />
          <select
            value={activeProject?.id || ''}
            onChange={(e) => changeProject(e.target.value)}
            disabled={projects.length === 0}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-primary)',
              outline: 'none',
              fontWeight: 600,
              cursor: projects.length > 0 ? 'pointer' : 'default'
            }}
          >
            {projects.length === 0 ? (
              <option value="" style={{ background: '#0f172a', color: '#94a3b8' }}>
                No Projects Configured
              </option>
            ) : (
              projects.map((proj) => (
                <option key={proj.id} value={proj.id} style={{ background: '#0f172a', color: '#fff' }}>
                  {proj.name}
                </option>
              ))
            )}
          </select>
          {projects.length > 0 && <ChevronDown size={14} className="text-muted" />}
        </div>
      </div>

      <div className="topbar-right">
        <div className="status-pill">
          <span className="pulse-dot"></span>
          <span>FastAPI Engine: Active</span>
        </div>

        <button className="topbar-icon-btn" title="System Notifications" aria-label="Notifications">
          <Bell size={18} />
          {notificationCount > 0 && <span className="notification-badge">{notificationCount}</span>}
        </button>
      </div>
    </header>
  );
};

export default Topbar;
