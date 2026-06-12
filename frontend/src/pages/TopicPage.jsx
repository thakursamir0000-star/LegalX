import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ChevronRight, Home, Shield, ShoppingCart, Monitor, FileText, Receipt,
  BookOpen, ListChecks
} from 'lucide-react';
import Summary from '../components/Summary';
import KeyInfo from '../components/KeyInfo';
import AudioPlayer from '../components/AudioPlayer';
import ChatAssistant from '../components/ChatAssistant';
import LoadingSpinner from '../components/LoadingSpinner';
import { getTopic } from '../utils/api';
import './TopicPage.css';

const ICON_MAP = {
  pocso_act: Shield,
  consumer_protection_act: ShoppingCart,
  cyber_crime_laws: Monitor,
  rti_act: FileText,
  gst_registration: Receipt,
};

const TOPIC_NAMES = {
  pocso_act: 'POCSO Act',
  consumer_protection_act: 'Consumer Protection Act',
  cyber_crime_laws: 'Cyber Crime Laws',
  rti_act: 'Right to Information (RTI) Act',
  gst_registration: 'GST Registration',
};

const ACCENT_COLORS = {
  pocso_act: '#ef4444',
  consumer_protection_act: '#10b981',
  cyber_crime_laws: '#6366f1',
  rti_act: '#f59e0b',
  gst_registration: '#06b6d4',
};

function TopicPage() {
  const { topicId } = useParams();
  const [topic, setTopic] = useState(null);
  const [activeTab, setActiveTab] = useState('summary');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const IconComponent = ICON_MAP[topicId] || FileText;
  const topicName = topic?.name || TOPIC_NAMES[topicId] || topicId;
  const accentColor = ACCENT_COLORS[topicId] || '#6366f1';

  useEffect(() => {
    let cancelled = false;

    async function loadTopic() {
      setLoading(true);
      setError(null);

      try {
        const data = await getTopic(topicId);
        if (!cancelled) {
          setTopic(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
          // Use fallback
          setTopic({ id: topicId, name: TOPIC_NAMES[topicId] || topicId });
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadTopic();
    return () => { cancelled = true; };
  }, [topicId]);

  // Reset tab when topic changes
  useEffect(() => {
    setActiveTab('summary');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [topicId]);

  if (loading) {
    return (
      <div className="topic-page">
        <div className="container">
          <LoadingSpinner size="lg" text="Loading topic..." />
        </div>
      </div>
    );
  }

  return (
    <div className="topic-page" style={{ '--topic-accent': accentColor }}>
      {/* Background accent glow */}
      <div className="topic-page__bg-glow" />

      <div className="container">
        {/* Breadcrumb */}
        <nav className="breadcrumb animate-fade-in-down">
          <Link to="/" className="breadcrumb__link">
            <Home size={14} />
            Home
          </Link>
          <ChevronRight size={14} className="breadcrumb__sep" />
          <span className="breadcrumb__current">{topicName}</span>
        </nav>

        {/* Topic Header */}
        <header className="topic-header animate-fade-in-up">
          <div
            className="topic-header__icon"
            style={{ background: `linear-gradient(135deg, ${accentColor}22, ${accentColor}08)` }}
          >
            <IconComponent size={32} style={{ color: accentColor }} />
          </div>
          <div>
            <h1 className="topic-header__title">{topicName}</h1>
            {topic?.description && (
              <p className="topic-header__desc">{topic.description}</p>
            )}
          </div>
        </header>

        {/* Tab Navigation */}
        <div className="topic-tabs animate-fade-in-up" style={{ animationDelay: '100ms' }}>
          <button
            className={`topic-tab ${activeTab === 'summary' ? 'topic-tab--active' : ''}`}
            onClick={() => setActiveTab('summary')}
          >
            <BookOpen size={16} />
            Summary
          </button>
          <button
            className={`topic-tab ${activeTab === 'keyinfo' ? 'topic-tab--active' : ''}`}
            onClick={() => setActiveTab('keyinfo')}
          >
            <ListChecks size={16} />
            Key Information
          </button>
        </div>

        {/* Tab Content */}
        <div className="topic-content animate-fade-in-up" style={{ animationDelay: '150ms' }}>
          {activeTab === 'summary' && (
            <Summary summary={topic?.summary} loading={false} />
          )}
          {activeTab === 'keyinfo' && (
            <KeyInfo keyInfo={topic?.key_info} loading={false} />
          )}
        </div>

        {/* Audio Player */}
        <section className="topic-section" style={{ animationDelay: '200ms' }}>
          <AudioPlayer topicId={topicId} topicName={topicName} />
        </section>

        {/* Chat Assistant */}
        <section className="topic-section" style={{ animationDelay: '250ms' }}>
          <ChatAssistant topicId={topicId} topicName={topicName} />
        </section>
      </div>
    </div>
  );
}

export default TopicPage;
