import { Link } from 'react-router-dom';
import { ArrowRight, Shield, ShoppingCart, Monitor, FileText, Receipt } from 'lucide-react';
import './TopicCard.css';

const ICON_MAP = {
  Shield: Shield,
  ShoppingCart: ShoppingCart,
  Monitor: Monitor,
  FileText: FileText,
  Receipt: Receipt,
};

const ICON_BY_ID = {
  pocso_act: Shield,
  consumer_protection_act: ShoppingCart,
  cyber_crime_laws: Monitor,
  rti_act: FileText,
  gst_registration: Receipt,
};

const ACCENT_COLORS = {
  pocso_act: '#ef4444',
  consumer_protection_act: '#10b981',
  cyber_crime_laws: '#6366f1',
  rti_act: '#f59e0b',
  gst_registration: '#06b6d4',
};

function TopicCard({ topic, index = 0 }) {
  const IconComponent = ICON_MAP[topic.icon] || ICON_BY_ID[topic.id] || FileText;
  const accentColor = ACCENT_COLORS[topic.id] || '#6366f1';

  return (
    <Link
      to={`/topic/${topic.id}`}
      className="topic-card animate-fade-in-up"
      style={{
        '--card-accent': accentColor,
        animationDelay: `${index * 100}ms`,
      }}
    >
      {/* Accent border */}
      <div className="topic-card__accent" />

      {/* Icon */}
      <div className="topic-card__icon-wrapper">
        <IconComponent size={24} />
      </div>

      {/* Content */}
      <div className="topic-card__content">
        <h3 className="topic-card__title">{topic.name}</h3>
        <p className="topic-card__description line-clamp-2">
          {topic.description}
        </p>
      </div>

      {/* Footer */}
      <div className="topic-card__footer">
        <span className="topic-card__explore">
          Explore
          <ArrowRight size={16} className="topic-card__arrow" />
        </span>
      </div>
    </Link>
  );
}

export default TopicCard;
