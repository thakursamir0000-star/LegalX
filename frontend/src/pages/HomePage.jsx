import { useState, useEffect } from 'react';
import {
  Scale, BookOpen, Headphones, MessageSquare, ArrowDown, Check, Search
} from 'lucide-react';
import TopicCard from '../components/TopicCard';
import SearchBar from '../components/SearchBar';
import LoadingSpinner from '../components/LoadingSpinner';
import { getTopics } from '../utils/api';
import './HomePage.css';

const FALLBACK_TOPICS = [
  {
    id: 'pocso_act',
    name: 'POCSO Act',
    description: 'Protection of Children from Sexual Offences Act - safeguarding children with stringent penalties and child-friendly procedures.',
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
    description: 'Goods and Services Tax - covering registration, returns, input credits, and compliance.',
    icon: 'Receipt',
  },
];

const FEATURES = [
  {
    icon: BookOpen,
    title: 'Read the short version',
    description: 'Start with a plain-language overview before going deeper.',
  },
  {
    icon: Search,
    title: 'Find what matters',
    description: 'See rights, provisions, penalties, and who the law protects.',
  },
  {
    icon: Headphones,
    title: 'Listen on the go',
    description: 'Use the audio guide when reading is not convenient.',
  },
  {
    icon: MessageSquare,
    title: 'Ask a follow-up',
    description: 'Use the assistant when your question is more specific.',
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
      <section className="hero">
        <div className="hero__bg">
          <div className="hero__shape hero__shape--one" />
          <div className="hero__shape hero__shape--two" />
        </div>

        <div className="hero__content container">
          <div className="hero__copy">
            <span className="hero__eyebrow animate-fade-in-up">
              A practical guide to Indian law
            </span>

            <h1 className="hero__title animate-fade-in-up">
              Law, without the <span>legal fog.</span>
            </h1>

            <p className="hero__subtitle animate-fade-in-up" style={{ animationDelay: '100ms' }}>
              I built LegalX to make important Indian laws easier to understand.
              Begin with a simple guide, then explore the details at your own pace.
            </p>

            <div className="hero__search animate-fade-in-up" style={{ animationDelay: '200ms' }}>
              <SearchBar variant="hero" placeholder="What law do you want to understand?" />
            </div>

            <a className="hero__browse-link animate-fade-in-up" href="#topics">
              Or browse all guides
              <ArrowDown size={16} />
            </a>
          </div>

          <aside className="hero__note animate-fade-in-up" style={{ animationDelay: '150ms' }}>
            <div className="hero__note-pin" />
            <span className="hero__note-label">The idea behind LegalX</span>
            <h2>Useful legal knowledge should not require a law degree.</h2>
            <p>
              Each guide is organised around the questions people usually ask first.
            </p>
            <ul>
              <li><Check size={15} /> Start with the essentials</li>
              <li><Check size={15} /> Keep the language straightforward</li>
              <li><Check size={15} /> Make room for follow-up questions</li>
            </ul>
            <div className="hero__note-signoff">Read. Listen. Ask.</div>
          </aside>
        </div>

        <div className="hero__features-wrap container">
          <div className="hero__features stagger-children">
            {FEATURES.map((feat, i) => {
              const IconComp = feat.icon;
              return (
                <div key={feat.title} className="hero__feature animate-fade-in-up">
                  <span className="hero__feature-number">0{i + 1}</span>
                  <div className="hero__feature-icon">
                    <IconComp size={18} />
                  </div>
                  <h3 className="hero__feature-title">{feat.title}</h3>
                  <p className="hero__feature-desc">{feat.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="topics-section" id="topics">
        <div className="container">
          <div className="topics-section__header animate-fade-in-up">
            <span className="topics-section__index">01 / Guides</span>
            <h2 className="topics-section__title">Pick a starting point.</h2>
            <p className="topics-section__sub">
              Five useful areas of Indian law, explained one question at a time.
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
              Showing the saved topic list because the local API is unavailable.
            </p>
          )}
        </div>
      </section>

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
                A small project for making Indian laws feel less intimidating and more useful.
              </p>
            </div>
            <div className="home-footer__copy">
              <p>Made for legal awareness, not legal advice.</p>
              <p>© {new Date().getFullYear()} LegalX</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default HomePage;
