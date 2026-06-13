import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Scale, Menu, X, Home, Info, BookOpen } from 'lucide-react';
import './Navbar.css';

function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMenuOpen(false);
  }, [location]);

  return (
    <nav className={`navbar ${scrolled ? 'navbar--scrolled' : ''}`}>
      <div className="navbar__inner container">
        {/* Logo */}
        <Link to="/" className="navbar__logo">
          <div className="navbar__logo-icon">
            <Scale size={22} />
          </div>
          <span className="navbar__logo-text">
            Legal<span className="navbar__logo-accent">X</span>
          </span>
          <span className="navbar__logo-note">law, made clearer</span>
        </Link>

        {/* Desktop Nav */}
        <div className="navbar__links">
          <Link
            to="/"
            className={`navbar__link ${location.pathname === '/' ? 'navbar__link--active' : ''}`}
          >
            <Home size={16} />
            Home
          </Link>
          <a href="/#topics" className="navbar__link">
            <BookOpen size={16} />
            Guides
          </a>
          <a href="/#about" className="navbar__link">
            <Info size={16} />
            About
          </a>
        </div>

        {/* Mobile Toggle */}
        <button
          className="navbar__toggle"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle menu"
        >
          {menuOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {/* Mobile Menu */}
      <div className={`navbar__mobile ${menuOpen ? 'navbar__mobile--open' : ''}`}>
        <Link
          to="/"
          className={`navbar__mobile-link ${location.pathname === '/' ? 'navbar__mobile-link--active' : ''}`}
        >
          <Home size={18} />
          Home
        </Link>
        <a href="/#topics" className="navbar__mobile-link">
          <BookOpen size={18} />
          Guides
        </a>
        <a href="/#about" className="navbar__mobile-link">
          <Info size={18} />
          About
        </a>
      </div>
    </nav>
  );
}

export default Navbar;
