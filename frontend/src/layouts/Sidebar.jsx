import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  ShieldAlert,
  LayoutDashboard,
  FlaskConical,
  Bug,
  Activity,
  GitCompare,
  FolderGit2,
  Settings,
  ShieldCheck,
  X
} from 'lucide-react';
import { useApp } from '../context/AppContext';

export const Sidebar = () => {
  const { isMobileNavOpen, setIsMobileNavOpen, notificationCount } = useApp();

  const navItems = [
    { section: "Core Platform" },
    { path: "/", label: "Overview", icon: LayoutDashboard },
    { path: "/studio", label: "Test Studio", icon: FlaskConical },
    { path: "/findings", label: "Security Findings", icon: Bug, badge: notificationCount },
    { section: "Observability & Analysis" },
    { path: "/evaluation", label: "Evaluation Hub", icon: ShieldCheck },
    { path: "/traces", label: "Execution Traces", icon: Activity },
    { path: "/compare", label: "Run Comparison", icon: GitCompare },
    { section: "Management" },
    { path: "/projects", label: "Projects", icon: FolderGit2 },
    { path: "/settings", label: "Settings", icon: Settings }
  ];

  return (
    <>
      {isMobileNavOpen && (
        <div className="sidebar-backdrop" onClick={() => setIsMobileNavOpen(false)} />
      )}
      <aside className={`sidebar ${isMobileNavOpen ? 'open' : ''}`}>
        <div className="sidebar-brand">
          <div className="brand-icon">
            <ShieldAlert size={22} />
          </div>
          <div className="brand-text">
            <span>Sentinel</span><span className="text-cyan">AI</span>
            <span className="brand-badge">SEC</span>
          </div>
          {isMobileNavOpen && (
            <button
              className="topbar-icon-btn"
              style={{ marginLeft: 'auto' }}
              onClick={() => setIsMobileNavOpen(false)}
            >
              <X size={18} />
            </button>
          )}
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item, idx) => {
            if (item.section) {
              return (
                <div key={idx} className="nav-section-title">
                  {item.section}
                </div>
              );
            }
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                onClick={() => setIsMobileNavOpen(false)}
              >
                <Icon size={18} />
                <span>{item.label}</span>
                {item.badge > 0 && <span className="nav-badge">{item.badge}</span>}
              </NavLink>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <div className="user-profile">
            <div className="user-avatar">SA</div>
            <div className="user-info">
              <span className="user-name">Lead Architect</span>
              <span className="user-role">SecOps Engineer</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
