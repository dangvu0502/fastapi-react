import createClient from 'openapi-fetch';
import type { paths } from './schema';

export const apiClient = createClient<paths>({
  baseUrl: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  // Include cookies with all requests
  credentials: 'include',
});

// Response interceptor for handling auth errors
apiClient.use({
  onResponse: async (options) => {
    const response = options as Response;
    if (response.status === 401) {
      // Redirect to login on unauthorized
      window.location.href = '/login';
    }
    return response;
  },
});