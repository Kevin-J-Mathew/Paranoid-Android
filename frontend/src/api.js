import axios from 'axios';

const API_BASE = '/api';

export const api = {
  // Health
  health: () => axios.get(`${API_BASE}/health`),

  // Stories
  getStories: () => axios.get(`${API_BASE}/stories`),

  // Runs
  startRun: (story) => axios.post(`${API_BASE}/runs/start`, { story }),
  getRun: (runId) => axios.get(`${API_BASE}/runs/${runId}`),
  listRuns: () => axios.get(`${API_BASE}/runs`),

  // Reports
  listReports: () => axios.get(`${API_BASE}/reports`),
  getReportUrl: (filename) => `${API_BASE}/reports/${filename}`,

  // Knowledge Base
  getKnowledgeStats: () => axios.get(`${API_BASE}/knowledge/stats`),
  querySimilarTests: (query, n = 5) => axios.get(`${API_BASE}/knowledge/similar-tests`, { params: { query, n } }),

  // Feedback
  submitFeedback: (runId, testName, isFalsePositive) =>
    axios.post(`${API_BASE}/feedback`, {
      run_id: runId,
      test_name: testName,
      is_false_positive: isFalsePositive
    }),
};

export function createSSEConnection(runId, onStep, onComplete, onError) {
  const eventSource = new EventSource(`${API_BASE}/runs/${runId}/stream`);

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.type === 'step') {
        onStep(data.step);
      } else if (data.type === 'completed') {
        onComplete(data);
        eventSource.close();
      } else if (data.type === 'end') {
        eventSource.close();
      }
    } catch (e) {
      console.error('SSE parse error:', e);
    }
  };

  eventSource.onerror = (err) => {
    console.error('SSE error:', err);
    eventSource.close();
    if (onError) onError(err);
  };

  return eventSource;
}
