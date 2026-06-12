import { useState, useEffect } from 'react';
import { Scale, Zap, BookOpen, Headphones, MessageSquare } from 'lucide-react';
import TopicCard from '../components/TopicCard';
import SearchBar from '../components/SearchBar';
import LoadingSpinner from '../components/LoadingSpinner';
import { getTopics } from '../utils/api';
import './HomePage.css';

// Fallback topics for when API is unavailable
const FALLBACK_TOPICS = [
  {
    id: 'pocso_act',
    name: 'POCSO Act',
    description: 'Protection of Children from Sexual Offences Act — safeguarding children with stringent penalties and child-friendly procedures.',
    icon: 'Shield',
  },
  {
    id: 'consumer_protection_act',
    name: 'Consumer Protection Act',
    description: 'Empowering consumers with rights to safety, information, choice, and redressal through consumer courts and commissions.',
    icon: 'ShoppingCart',
  },
  {
    id: 'cyber_crime_laws',
    name: 'Cyber Crime Laws',
    description: 'Information Technology Act provisions covering hacking, identity theft, cyber fraud, and digital evidence handling.',
    icon: 'Monitor',
  },
  {
    id: 'rti_act',
    name: 'Right to Information (RTI) Act',
    description: 'RTI Act empowering citizens to access government information, promoting transparency and accountability.',
    icon: 'FileText',
  },
  {
    id: 'gst_registration',
    name: 'GST Registration',
    description: 'Goods and Services Tax — unified indirect tax regime covering registration, returns, input credits, and compliance.',
    icon: 'Receipt',
  },
];

const FEATURES = [
  {
    icon: Zap,
    title: 'AI Summaries',
    description: 'Instant, easy-to-understand summaries of complex laws',
  },
  {
    icon: BookOpen,
    title: 'Key Information',
    description: 'Rights, provisions, penalties & beneficiaries at a glance',
  },
  {
    icon: Headphones,
    title: 'Audio Guides',
    description: 'Listen to legal knowledge with AI-generated audio',
  },
  {
    icon: MessageSquare,
    title: 'AI Assistant',
    description: 'Ask questions and get instant, sourced answers',
  },
];

function HomePage() {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchTopics() {
      try {
        setLoading(true);
        const data = await getTopics();
        if (!cancelled) {
          setTopics(Array.isArray(data) ? data : data.topics || FALLBACK_TOPICS);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
          setTopics(FALLBACK_TOPICS);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchTopics();
    return () => { cancelled = true; };
  }, []);

  return (
    <div className="home-page">
      {/* ── Hero Section ─────────────────────────────────── */}
      <section className="hero">
        {/* Animated background */}
        <div className="hero__bg">
          <div className="hero__orb hero__orb--1" />
          <div className="hero__orb hero__orb--2" />
          <div className="hero__orb hero__orb--3" />
          <div className="hero__grid-overlay" />
        </div>

        <div className="hero__content container">

          <h1 className="hero__title animate-fade-in-up">
            AI Legal{' '}
            <span className="text-gradient-hero">Knowledge Centre</span>
          </h1>

          <p className="hero__subtitle animate-fade-in-up" style={{ animationDelay: '100ms' }}>
            Understand Indian laws simplified. Get AI-powered summaries, key information,
            audio guides, and ask an intelligent legal assistant — all in one place.
          </p>

          <div className="hero__search animate-fade-in-up" style={{ animationDelay: '200ms' }}>
            <SearchBar variant="hero" />
          </div>

          {/* Features */}
          <div className="hero__features stagger-children">
            {FEATURES.map((feat, i) => {
              const IconComp = feat.icon;
              return (
                <div key={i} className="hero__feature animate-fade-in-up">
                  <div className="hero__feature-icon">
                    <IconComp size={18} />
                  </div>
                  <div>
                    <h4 className="hero__feature-title">{feat.title}</h4>
                    <p className="hero__feature-desc">{feat.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── Topics Section ───────────────────────────────── */}
      <section className="topics-section" id="topics">
        <div className="container">
          <div className="topics-section__header animate-fade-in-up">
            <span className="badge badge-primary">Explore Topics</span>
            <h2 className="topics-section__title">Legal Topics</h2>
            <p className="topics-section__sub">
              Dive into key Indian laws and regulations with AI-powered insights
            </p>
          </div>

          {loading ? (
            <LoadingSpinner size="lg" text="Loading topics..." />
          ) : (
            <div className="topics-grid stagger-children">
              {topics.map((topic, i) => (
                <TopicCard key={topic.id} topic={topic} index={i} />
              ))}
            </div>
          )}

          {error && !loading && (
            <p className="topics-section__error">
              Using offline data — the API server may be unavailable.
            </p>
          )}
        </div>
      </section>

      {/* ── Footer ───────────────────────────────────────── */}
      <footer className="home-footer" id="about">
        <div className="container">
          <div className="home-footer__inner">
            <div className="home-footer__brand">
              <div className="home-footer__logo">
                <Scale size={20} />
                <span>
                  Legal<span className="home-footer__accent">X</span>
                </span>
              </div>
              <p className="home-footer__desc">
                AI-powered legal knowledge platform making Indian laws accessible, understandable, and actionable for everyone.
              </p>
            </div>
            <div className="home-footer__copy">
              <p>© {new Date().getFullYear()} LegalX. For legal awareness.</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default HomePage;
