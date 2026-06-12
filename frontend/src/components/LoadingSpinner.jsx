import './LoadingSpinner.css';

function LoadingSpinner({ size = 'md', text = '' }) {
  return (
    <div className={`loading-spinner loading-spinner--${size}`}>
      <div className="loading-spinner__ring">
        <div className="loading-spinner__ring-inner" />
      </div>
      {text && <p className="loading-spinner__text">{text}</p>}
    </div>
  );
}

export default LoadingSpinner;
