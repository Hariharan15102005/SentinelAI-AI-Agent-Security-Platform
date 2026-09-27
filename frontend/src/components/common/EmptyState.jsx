import React from 'react';

export const EmptyState = ({
  title = "No items found",
  description = "Try adjusting your filters or create a new test run.",
  action
}) => {
  return (
    <div
      className="flex flex-col items-center justify-center text-center gap-2"
      style={{
        padding: '3rem 1.5rem',
        background: 'var(--bg-secondary)',
        borderRadius: 'var(--radius-lg)',
        border: '1px dashed var(--border-color)'
      }}
    >
      <h4 style={{ color: 'var(--text-primary)', fontSize: '1rem', fontWeight: 600 }}>{title}</h4>
      <p className="text-muted" style={{ fontSize: '0.85rem', maxWidth: '400px' }}>
        {description}
      </p>
      {action && <div style={{ marginTop: '0.75rem' }}>{action}</div>}
    </div>
  );
};

export default EmptyState;
