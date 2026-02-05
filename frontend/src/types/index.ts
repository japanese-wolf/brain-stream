// API response types

export interface RelevanceScore {
  total_score: number;
  tag_score: number;
  vendor_score: number;
  content_score: number;
  relevance_level: 'high' | 'medium' | 'low' | 'none';
  matched_tags: string[];
  matched_keywords: string[];
}

export interface Article {
  id: string;
  source_id: string | null;
  original_title: string;
  original_content: string;
  primary_source_url: string;
  vendor: string;
  summary_title: string | null;
  summary_content: string | null;
  diff_description: string | null;
  explanation: string | null;
  tags: string[];
  published_at: string | null;
  collected_at: string;
  processed_at: string | null;
  llm_provider: string | null;
  llm_model: string | null;
}

export interface ArticleWithRelevance extends Article {
  relevance: RelevanceScore | null;
}

export interface FeedResponse {
  items: ArticleWithRelevance[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
  tech_stack: string[];
  preferred_vendors: string[];
}

export interface ArticleListResponse {
  items: Article[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface UserProfile {
  id: string;
  tech_stack: string[];
  preferred_vendors: string[];
  llm_provider: string;
  created_at: string;
  updated_at: string;
}

export interface ProfileUpdateRequest {
  tech_stack?: string[];
  preferred_vendors?: string[];
  llm_provider?: string;
}

export interface TechStackSuggestion {
  name: string;
  category: string;
  description: string;
}

export interface DataSource {
  id: string;
  plugin_name: string;
  name: string;
  vendor: string;
  enabled: boolean;
  last_fetched_at: string | null;
  fetch_status: string;
  error_message: string | null;
}

export interface CollectionResult {
  source_name: string;
  fetched: number;
  new: number;
  processed: number;
  errors: string[];
}
