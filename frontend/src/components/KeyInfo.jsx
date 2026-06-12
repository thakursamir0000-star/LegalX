import { Shield, BookOpen, AlertTriangle, Users } from 'lucide-react';
import './KeyInfo.css';

const CATEGORY_CONFIG = {
  rights: {
    icon: Shield,
    label: 'Rights',
    color: '#6366f1',
    gradient: 'linear-gradient(135deg, rgba(99,102,241,0.15), rgba(99,102,241,0.05))',
  },
  provisions: {
    icon: BookOpen,
    label: 'Key Provisions',
    color: '#06b6d4',
    gradient: 'linear-gradient(135deg, rgba(6,182,212,0.15), rgba(6,182,212,0.05))',
  },
  penalties: {
    icon: AlertTriangle,
    label: 'Penalties',
    color: '#ef4444',
    gradient: 'linear-gradient(135deg, rgba(239,68,68,0.15), rgba(239,68,68,0.05))',
  },
  beneficiaries: {
    icon: Users,
    label: 'Beneficiaries',
    color: '#10b981',
    gradient: 'linear-gradient(135deg, rgba(16,185,129,0.15), rgba(16,185,129,0.05))',
  },
};

function KeyInfo({ keyInfo, loading }) {
  if (loading) {
    return (
      <div className="key-info">
        <div className="key-info__grid">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="key-info-card key-info-card--skeleton">
              <div className="skeleton" style={{ width: 44, height: 44, borderRadius: 'var(--radius-md)' }} />
              <div className="skeleton skeleton-title" style={{ width: '50%' }} />
              <div className="skeleton skeleton-text" />
              <div className="skeleton skeleton-text" />
              <div className="skeleton skeleton-text" style={{ width: '70%' }} />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!keyInfo || Object.keys(keyInfo).length === 0) {
    return (
      <div className="key-info key-info--empty">
        <BookOpen size={48} />
        <p>No key information available for this topic.</p>
      </div>
    );
  }

  const categories = ['rights', 'provisions', 'penalties', 'beneficiaries'];

  return (
    <div className="key-info animate-fade-in-up">
      <div className="key-info__grid stagger-children">
        {categories.map((catKey) => {
          const config = CATEGORY_CONFIG[catKey];
          const items = keyInfo[catKey];
          if (!items || items.length === 0) return null;

          const IconComp = config.icon;

          return (
            <div
              key={catKey}
              className="key-info-card animate-fade-in-up"
              style={{ '--ki-color': config.color }}
            >
              <div
                className="key-info-card__icon"
                style={{ background: config.gradient }}
              >
                <IconComp size={22} />
              </div>

              <h4 className="key-info-card__title">{config.label}</h4>

              <ul className="key-info-card__list">
                {items.map((item, idx) => (
                  <li key={idx} className="key-info-card__item">
                    <span className="key-info-card__bullet" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default KeyInfo;
