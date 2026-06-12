import { useState, useEffect, useRef, useCallback } from 'react';
import { Search, X, ArrowRight, Shield, ShoppingCart, Monitor, FileText, Receipt } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { getTopics } from '../utils/api';
import './SearchBar.css';

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

// Local search: filter topics by query matching name or description
function filterTopics(topics, query) {
  const q = query.toLowerCase().trim();
  if (!q) return [];
  return topics.filter(
    (t) =>
      t.name.toLowerCase().includes(q) ||
      t.description.toLowerCase().includes(q) ||
      t.id.toLowerCase().replace(/_/g, ' ').includes(q)
  );
}

function SearchBar({ variant = 'hero', placeholder = 'Search laws, acts, and legal topics...' }) {
  const [query, setQuery] = useState('');
  const [allTopics, setAllTopics] = useState([]);
  const [results, setResults] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const wrapperRef = useRef(null);
  const inputRef = useRef(null);
  const navigate = useNavigate();

  // Load all topics once for local search
  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const data = await getTopics();
        if (!cancelled) {
          setAllTopics(Array.isArray(data) ? data : []);
        }
      } catch {
        // silently fail – search just won't work
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  const handleChange = (e) => {
    const val = e.target.value;
    setQuery(val);

    if (!val.trim()) {
      setResults([]);
      setIsOpen(false);
      return;
    }

    const filtered = filterTopics(allTopics, val);
    setResults(filtered);
    setIsOpen(true);
  };

  const handleClear = () => {
    setQuery('');
    setResults([]);
    setIsOpen(false);
    inputRef.current?.focus();
  };

  const handleResultClick = (topicId) => {
    setQuery('');
    setResults([]);
    setIsOpen(false);
    navigate(`/topic/${topicId}`);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      setIsOpen(false);
      inputRef.current?.blur();
    }
  };

  // Close on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div
      className={`search-bar search-bar--${variant}`}
      ref={wrapperRef}
    >
      <div className={`search-bar__input-wrapper ${isOpen && results.length > 0 ? 'search-bar__input-wrapper--open' : ''}`}>
        <Search size={20} className="search-bar__icon" />
        <input
          ref={inputRef}
          type="text"
          className="search-bar__input"
          placeholder={placeholder}
          value={query}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          onFocus={() => results.length > 0 && setIsOpen(true)}
        />
        {query && (
          <button className="search-bar__clear" onClick={handleClear} aria-label="Clear search">
            <X size={16} />
          </button>
        )}
      </div>

      {/* Results Dropdown */}
      {isOpen && results.length > 0 && (
        <div className="search-bar__dropdown animate-fade-in-down">
          {results.map((result) => {
            const IconComp = ICON_MAP[result.icon] || ICON_BY_ID[result.id] || FileText;
            return (
              <button
                key={result.id}
                className="search-bar__result"
                onClick={() => handleResultClick(result.id)}
              >
                <div className="search-bar__result-icon">
                  <IconComp size={16} />
                </div>
                <div className="search-bar__result-content">
                  <span className="search-bar__result-name">{result.name}</span>
                  {result.description && (
                    <span className="search-bar__result-desc truncate">{result.description}</span>
                  )}
                </div>
                <ArrowRight size={14} className="search-bar__result-arrow" />
              </button>
            );
          })}
        </div>
      )}

      {isOpen && query && results.length === 0 && (
        <div className="search-bar__dropdown animate-fade-in-down">
          <div className="search-bar__no-results">
            No results found for "{query}"
          </div>
        </div>
      )}
    </div>
  );
}

export default SearchBar;
