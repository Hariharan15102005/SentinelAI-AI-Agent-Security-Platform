import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import apiService from '../services/apiService';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [projects, setProjects] = useState([]);
  const [activeProject, setActiveProject] = useState(null);
  const [loadingProjects, setLoadingProjects] = useState(true);
  const [notificationCount, setNotificationCount] = useState(0);
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);

  const fetchProjects = useCallback(async () => {
    try {
      setLoadingProjects(true);
      const data = await apiService.getProjects();
      setProjects(data || []);
      if (data && data.length > 0) {
        setActiveProject((prev) => {
          if (prev && data.some((p) => p.id === prev.id)) {
            return data.find((p) => p.id === prev.id);
          }
          return data[0];
        });
      } else {
        setActiveProject(null);
      }
    } catch (err) {
      console.error('Failed to fetch projects', err);
      setProjects([]);
      setActiveProject(null);
    } finally {
      setLoadingProjects(false);
    }
  }, []);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const changeProject = (projectId) => {
    const selected = projects.find((p) => p.id === Number(projectId));
    if (selected) {
      setActiveProject(selected);
    }
  };

  const addProject = async (projectData) => {
    const created = await apiService.createProject(projectData);
    if (created) {
      setProjects((prev) => [created, ...prev]);
      setActiveProject(created);
    }
    return created;
  };

  return (
    <AppContext.Provider
      value={{
        projects,
        activeProject,
        loadingProjects,
        notificationCount,
        setNotificationCount,
        isMobileNavOpen,
        setIsMobileNavOpen,
        changeProject,
        addProject,
        refreshProjects: fetchProjects
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

export default AppContext;
