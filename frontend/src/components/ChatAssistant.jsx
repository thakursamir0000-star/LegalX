import { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Bot, User, BookOpen, Sparkles } from 'lucide-react';
import { sendChatMessage } from '../utils/api';
import './ChatAssistant.css';

const SUGGESTED_QUESTIONS = [
  'What are the key provisions of this law?',
  'Who are the beneficiaries?',
  'What penalties are defined?',
  'How can I file a complaint?',
];

function ChatAssistant({ topicId, topicName }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping, scrollToBottom]);

  // Reset chat when topic changes
  useEffect(() => {
    setMessages([]);
    setInput('');
    setError(null);
  }, [topicId]);

  const handleSend = useCallback(async (messageText) => {
    const text = messageText || input.trim();
    if (!text || isTyping) return;

    setInput('');
    setError(null);

    const userMsg = { role: 'user', content: text, timestamp: Date.now() };
    setMessages((prev) => [...prev, userMsg]);
    setIsTyping(true);

    try {
      const history = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const response = await sendChatMessage(topicId, text, history);

      const aiMsg = {
        role: 'assistant',
        content: response.answer || response.response || response.message || 'I could not find an answer. Please try a different question.',
        sources: response.sources || [],
        timestamp: Date.now(),
      };

      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      setError('Failed to get a response. Please try again.');
      const errorMsg = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        isError: true,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  }, [input, isTyping, messages, topicId]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestedClick = (question) => {
    handleSend(question);
  };

  return (
    <div className="chat-assistant animate-fade-in-up">
      {/* Header */}
      <div className="chat__header">
        <div className="chat__header-left">
          <div className="chat__header-icon">
            <Sparkles size={18} />
          </div>
          <div>
            <h3 className="chat__header-title">AI Legal Assistant</h3>
            <span className="chat__header-sub">Ask about {topicName || 'this topic'}</span>
          </div>
        </div>
        <span className="badge badge-success">Online</span>
      </div>

      {/* Messages */}
      <div className="chat__messages">
        {messages.length === 0 && !isTyping && (
          <div className="chat__empty">
            <div className="chat__empty-icon">
              <Bot size={36} />
            </div>
            <p className="chat__empty-title">How can I help you?</p>
            <p className="chat__empty-sub">
              Ask any question about {topicName || 'this topic'} and I'll provide an AI-powered answer with relevant sources.
            </p>

            <div className="chat__suggestions">
              {SUGGESTED_QUESTIONS.map((q, i) => (
                <button
                  key={i}
                  className="chat__suggestion-btn"
                  onClick={() => handleSuggestedClick(q)}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`chat__message chat__message--${msg.role} ${msg.isError ? 'chat__message--error' : ''} animate-fade-in-up`}
            style={{ animationDelay: '0ms' }}
          >
            <div className="chat__message-avatar">
              {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
            </div>
            <div className="chat__message-bubble">
              <div className="chat__message-content">
                {msg.content.split('\n').map((line, i) =>
                  line.trim() ? <p key={i}>{line}</p> : null
                )}
              </div>

              {msg.sources && msg.sources.length > 0 && (
                <div className="chat__sources">
                  <BookOpen size={12} />
                  <span>Sources:</span>
                  {msg.sources.map((src, i) => (
                    <span key={i} className="chat__source-tag">
                      {src}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="chat__message chat__message--assistant animate-fade-in">
            <div className="chat__message-avatar">
              <Bot size={16} />
            </div>
            <div className="chat__message-bubble">
              <div className="chat__typing">
                <span className="chat__typing-dot" />
                <span className="chat__typing-dot" />
                <span className="chat__typing-dot" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error */}
      {error && (
        <div className="chat__error">{error}</div>
      )}

      {/* Input */}
      <div className="chat__input-area">
        <div className="chat__input-wrapper">
          <input
            ref={inputRef}
            type="text"
            className="chat__input"
            placeholder="Ask a legal question..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isTyping}
          />
          <button
            className="chat__send-btn"
            onClick={() => handleSend()}
            disabled={!input.trim() || isTyping}
            aria-label="Send message"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatAssistant;
