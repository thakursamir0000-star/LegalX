import { FileText } from 'lucide-react';
import './Summary.css';

function Summary({ summary, loading }) {
  if (loading) {
    return (
      <div className="summary">
        <div className="summary__header">
          <div className="skeleton skeleton-title" style={{ width: '200px' }} />
        </div>
        <div className="summary__body">
          <div className="skeleton skeleton-text" />
          <div className="skeleton skeleton-text" />
          <div className="skeleton skeleton-text" />
          <div className="skeleton skeleton-text" style={{ width: '85%' }} />
          <div className="skeleton skeleton-text" />
          <div className="skeleton skeleton-text" style={{ width: '60%' }} />
        </div>
      </div>
    );
  }

  const summaryText = typeof summary === 'string' ? summary : summary?.content || '';

  if (!summaryText) {
    return (
      <div className="summary summary--empty">
        <FileText size={48} />
        <p>No summary available for this topic.</p>
      </div>
    );
  }

  const wordCount = summaryText.split(/\s+/).filter(Boolean).length;

  return (
    <div className="summary animate-fade-in-up">
      <div className="summary__header">
        <div className="summary__title-row">
          <FileText size={20} className="summary__icon" />
          <h3 className="summary__title">Summary</h3>
        </div>
        {wordCount > 0 && (
          <span className="badge badge-primary">
            {wordCount} words
          </span>
        )}
      </div>

      <div className="summary__body">
        {summaryText.split('\n').map((paragraph, i) =>
          paragraph.trim() ? (
            <p key={i} className="summary__paragraph">
              {paragraph}
            </p>
          ) : null
        )}
      </div>

      <div className="summary__footer">
        <span className="summary__meta">
          AI-assisted summary - always check official sources for legal decisions
        </span>
      </div>
    </div>
  );
}

export default Summary;
