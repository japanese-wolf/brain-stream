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

// Articles API
export const articlesApi = {
  getFeed: (params: {
    page?: number;
    per_page?: number;
    min_relevance?: number;
    sort_by?: 'relevance' | 'date';
    vendor?: string;
  } = {}) => {
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.set('page', params.page.toString());
    if (params.per_page) searchParams.set('per_page', params.per_page.toString());
    if (params.min_relevance) searchParams.set('min_relevance', params.min_relevance.toString());
    if (params.sort_by) searchParams.set('sort_by', params.sort_by);
    if (params.vendor) searchParams.set('vendor', params.vendor);

    const query = searchParams.toString();
    return fetchApi<import('../types').FeedResponse>(
      `/articles/feed${query ? `?${query}` : ''}`
    );
  },

  getList: (params: {
    page?: number;
    per_page?: number;
    vendor?: string;
    processed_only?: boolean;
  } = {}) => {
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.set('page', params.page.toString());
    if (params.per_page) searchParams.set('per_page', params.per_page.toString());
    if (params.vendor) searchParams.set('vendor', params.vendor);
    if (params.processed_only) searchParams.set('processed_only', 'true');

    const query = searchParams.toString();
    return fetchApi<import('../types').ArticleListResponse>(
      `/articles${query ? `?${query}` : ''}`
    );
  },

  getById: (id: string) => {
    return fetchApi<import('../types').Article>(`/articles/${id}`);
  },

  getRelevance: (id: string) => {
    return fetchApi<import('../types').RelevanceScore>(`/articles/${id}/relevance`);
  },

  process: (id: string) => {
    return fetchApi<import('../types').Article>(`/articles/${id}/process`, {
      method: 'POST',
    });
  },
};

// Profile API
export const profileApi = {
  get: () => {
    return fetchApi<import('../types').UserProfile>('/profile');
  },

  update: (data: import('../types').ProfileUpdateRequest) => {
    return fetchApi<import('../types').UserProfile>('/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  addTechStack: (items: string[]) => {
    return fetchApi<import('../types').UserProfile>('/profile/tech-stack', {
      method: 'POST',
      body: JSON.stringify(items),
    });
  },

  removeTechStackItem: (item: string) => {
    return fetchApi<import('../types').UserProfile>(`/profile/tech-stack/${encodeURIComponent(item)}`, {
      method: 'DELETE',
    });
  },

  getSuggestions: () => {
    return fetchApi<Record<string, import('../types').TechStackSuggestion[]>>('/profile/suggestions');
  },

  getVendors: () => {
    return fetchApi<string[]>('/profile/vendors');
  },
};

// Sources API
export const sourcesApi = {
  getList: () => {
    return fetchApi<import('../types').DataSource[]>('/sources');
  },

  fetch: (sourceName?: string) => {
    const endpoint = sourceName ? `/sources/${sourceName}/fetch` : '/sources/fetch';
    return fetchApi<import('../types').CollectionResult | import('../types').CollectionResult[]>(
      endpoint,
      { method: 'POST' }
    );
  },
};

export { ApiError };
