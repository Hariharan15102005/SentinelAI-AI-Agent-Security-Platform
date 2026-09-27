import React from 'react';
import Card from './Card';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';

export const MetricCard = ({
  title,
  value,
  subtitle,
  trend,
  trendType = 'up', // 'up', 'down', 'neutral'
  icon: Icon,
  iconColor = 'var(--accent-cyan)',
  iconBg = 'rgba(6, 182, 212, 0.12)'
}) => {
  return (
    <Card className="stat-card">
      <div className="stat-header">
        <span>{title}</span>
        {Icon && (
          <div className="stat-icon-wrapper" style={{ background: iconBg, color: iconColor }}>
            <Icon size={18} />
          </div>
        )}
      </div>
      <div className="stat-value">{value}</div>
      {(subtitle || trend) && (
        <div className="flex items-center justify-between">
          {trend && (
            <div className={`stat-trend ${trendType === 'up' ? 'trend-up' : trendType === 'down' ? 'trend-down' : 'trend-neutral'}`}>
              {trendType === 'up' && <ArrowUpRight size={14} />}
              {trendType === 'down' && <ArrowDownRight size={14} />}
              {trendType === 'neutral' && <Minus size={14} />}
              <span>{trend}</span>
            </div>
          )}
          {subtitle && <span className="text-muted" style={{ fontSize: '0.75rem' }}>{subtitle}</span>}
        </div>
      )}
    </Card>
  );
};

export default MetricCard;
