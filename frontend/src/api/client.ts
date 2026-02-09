// API client for BrainStream backend

const API_BASE = '/api/v1';

class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ApiError(response.status, error.detail || 'Request failed');
  }

  return response.json();
}

export const feedApi = {
  getFeed: (params: {
    limit?: number;
    offset?: number;
    vendor?: string;
    primary_only?: boolean;
  } = {}) => {
    const searchParams = new URLSearchParams();
    if (params.limit) searchParams.set('limit', params.limit.toString());
    if (params.offset) searchParams.set('offset', params.offset.toString());
    if (params.vendor) searchParams.set('vendor', params.vendor);
    if (params.primary_only) searchParams.set('primary_only', 'true');

    const query = searchParams.toString();
    return fetchApi<import('../types').FeedResponse>(
      `/feed${query ? `?${query}` : ''}`
    );
  },

  getArticle: (id: string) => {
    return fetchApi<import('../types').Article>(`/articles/${id}`);
  },

  recordAction: (articleId: string, action: 'click' | 'bookmark' | 'skip') => {
    return fetchApi<{ success: boolean; message: string }>(
      `/articles/${articleId}/action`,
      {
        method: 'POST',
        body: JSON.stringify({ action }),
      }
    );
  },

  getTopology: () => {
    return fetchApi<import('../types').TopologyResponse>('/topology');
  },

  getSources: () => {
    return fetchApi<{ sources: import('../types').Source[] }>('/sources');
  },

  collect: () => {
    return fetchApi<import('../types').CollectResponse>('/collect', {
      method: 'POST',
    });
  },
};

export { ApiError };
