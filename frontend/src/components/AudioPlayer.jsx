import { useState, useRef, useEffect, useCallback } from 'react';
import { Play, Pause, Download, Volume2, VolumeX } from 'lucide-react';
import { getAudioUrl } from '../utils/api';
import './AudioPlayer.css';

function AudioPlayer({ topicId, topicName }) {
  const audioRef = useRef(null);
  const progressRef = useRef(null);

  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);
  const [error, setError] = useState(false);

  const audioUrl = getAudioUrl(topicId);

  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const togglePlay = useCallback(async () => {
    if (!audioRef.current) return;
    try {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        await audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    } catch {
      setError(true);
    }
  }, [isPlaying]);

  const toggleMute = useCallback(() => {
    if (!audioRef.current) return;
    audioRef.current.muted = !isMuted;
    setIsMuted(!isMuted);
  }, [isMuted]);

  const handleProgressClick = useCallback((e) => {
    if (!progressRef.current || !audioRef.current || !duration) return;
    const rect = progressRef.current.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const ratio = clickX / rect.width;
    audioRef.current.currentTime = ratio * duration;
  }, [duration]);

  const handleDownload = useCallback(() => {
    const a = document.createElement('a');
    a.href = audioUrl;
    a.download = `${topicName || topicId}-audio.mp3`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }, [audioUrl, topicName, topicId]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const onLoadedMetadata = () => {
      setDuration(audio.duration);
      setIsLoaded(true);
    };
    const onTimeUpdate = () => setCurrentTime(audio.currentTime);
    const onEnded = () => setIsPlaying(false);
    const onError = () => setError(true);

    audio.addEventListener('loadedmetadata', onLoadedMetadata);
    audio.addEventListener('timeupdate', onTimeUpdate);
    audio.addEventListener('ended', onEnded);
    audio.addEventListener('error', onError);

    return () => {
      audio.removeEventListener('loadedmetadata', onLoadedMetadata);
      audio.removeEventListener('timeupdate', onTimeUpdate);
      audio.removeEventListener('ended', onEnded);
      audio.removeEventListener('error', onError);
    };
  }, []);

  const progress = duration ? (currentTime / duration) * 100 : 0;

  return (
    <div className="audio-player animate-fade-in-up">
      <audio ref={audioRef} src={audioUrl} preload="metadata" />

      <div className="audio-player__header">
        <Volume2 size={18} className="audio-player__header-icon" />
        <h3 className="audio-player__title">Audio Guide</h3>
        {isLoaded && (
          <span className="badge badge-accent">{formatTime(duration)}</span>
        )}
      </div>

      <div className="audio-player__controls">
        {/* Waveform Visualization */}
        <div className="audio-player__waveform">
          {Array.from({ length: 20 }).map((_, i) => (
            <div
              key={i}
              className={`audio-player__wave-bar ${isPlaying ? 'audio-player__wave-bar--active' : ''}`}
              style={{ animationDelay: `${i * 0.07}s` }}
            />
          ))}
        </div>

        <div className="audio-player__main">
          {/* Play / Pause */}
          <button
            className="audio-player__play-btn"
            onClick={togglePlay}
            disabled={error}
            aria-label={isPlaying ? 'Pause' : 'Play'}
          >
            {isPlaying ? <Pause size={22} /> : <Play size={22} />}
          </button>

          {/* Progress */}
          <div className="audio-player__progress-area">
            <span className="audio-player__time">{formatTime(currentTime)}</span>

            <div
              className="audio-player__progress-track"
              ref={progressRef}
              onClick={handleProgressClick}
            >
              <div
                className="audio-player__progress-fill"
                style={{ width: `${progress}%` }}
              />
              <div
                className="audio-player__progress-thumb"
                style={{ left: `${progress}%` }}
              />
            </div>

            <span className="audio-player__time">{formatTime(duration)}</span>
          </div>

          {/* Mute */}
          <button
            className="audio-player__icon-btn"
            onClick={toggleMute}
            aria-label={isMuted ? 'Unmute' : 'Mute'}
          >
            {isMuted ? <VolumeX size={18} /> : <Volume2 size={18} />}
          </button>

          {/* Download */}
          <button
            className="audio-player__icon-btn"
            onClick={handleDownload}
            aria-label="Download audio"
          >
            <Download size={18} />
          </button>
        </div>
      </div>

      {error && (
        <div className="audio-player__error">
          Audio is not available for this topic.
        </div>
      )}
    </div>
  );
}

export default AudioPlayer;
