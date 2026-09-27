import React from 'react';

export const Badge = ({ variant = 'default', children, className = '' }) => {
  let badgeClass = 'badge';

  switch (variant.toLowerCase()) {
    case 'baseline':
      badgeClass += ' badge-baseline';
      break;
    case 'secured':
      badgeClass += ' badge-secured';
      break;
    case 'critical':
      badgeClass += ' badge-critical';
      break;
    case 'high':
      badgeClass += ' badge-high';
      break;
    case 'medium':
      badgeClass += ' badge-medium';
      break;
    case 'low':
      badgeClass += ' badge-low';
      break;
    case 'success':
    case 'completed':
    case 'passed':
      badgeClass += ' badge-success';
      break;
    case 'danger':
    case 'failed':
    case 'vulnerable':
      badgeClass += ' badge-danger';
      break;
    default:
      badgeClass += ' badge-low';
      break;
  }

  return <span className={`${badgeClass} ${className}`}>{children}</span>;
};

export default Badge;
