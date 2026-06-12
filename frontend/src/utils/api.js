/**
 * API Base URL - supports environment variable override
 * Development: http://localhost:8000
 * Production: use VITE_API_URL env var from Vercel/Netlify
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Generic fetch wrapper with error handling, timeout, and JSON parsing.
 */
async function request(endpoint, options = {}) {
  const {
    method = 'GET',
    body = null,
    headers = {},
    timeout = 30000,
  } = options;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  const config = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    signal: controller.signal,
  };

  if (body) {
    config.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.detail || errorData.message || `Request failed with status ${response.status}`,
        response.status,
        errorData
      );
    }

    // Handle empty responses
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    return await response.text();
  } catch (error) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new ApiError('Request timed out', 408);
    }
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(error.message || 'Network error', 0);
  }
}

class ApiError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

// ─── API Methods ─────────────────────────────────────────────

/**
 * Get all available topics.
 * GET /api/topics
 */
export async function getTopics() {
  return request('/api/topics');
}

/**
 * Get full topic detail (summary + key info) by ID.
 * GET /api/topics/:topicId
 */
export async function getTopic(topicId) {
  return request(`/api/topics/${topicId}`);
}

/**
 * Get the audio file URL directly (for <audio> src).
 */
export function getAudioUrl(topicId) {
  return `${API_BASE_URL}/api/topics/${topicId}/audio`;
}

/**
 * Send a chat message for a topic.
 * POST /api/topics/:topicId/chat
 * Backend expects: { question: string, history: [{role, content}] }
 */
export async function sendChatMessage(topicId, question, history = []) {
  return request(`/api/topics/${topicId}/chat`, {
    method: 'POST',
    body: { question, history },
    timeout: 60000,
  });
}

/**
 * Health check.
 * GET /api/health
 */
export async function healthCheck() {
  return request('/api/health');
}

export { API_BASE_URL, ApiError as default };
