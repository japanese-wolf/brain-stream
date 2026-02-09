// API response types

export interface Article {
  id: string;
  url: string;
  title: string;
  summary: string;
  tags: string[];
  vendor: string;
  is_primary_source: boolean;
  cluster_id: number;
  published_at: string;
  collected_at: string;
  source_plugin: string;
}

export interface FeedResponse {
  items: Article[];
  total: number;
}

export interface TopologyCluster {
  cluster_id: number;
  article_count: number;
  density: number;
  label: string;
  alpha: number;
  beta: number;
  sample_titles: string[];
}

export interface TopologyResponse {
  total_articles: number;
  clusters: TopologyCluster[];
}

export interface Source {
  name: string;
  display_name: string;
  vendor: string;
  description: string;
  source_type: string;
}

export interface CollectResponse {
  total_fetched: number;
  total_new: number;
  total_processed: number;
  duration_ms: number;
  sources: {
    name: string;
    fetched: number;
    new: number;
    processed: number;
    errors: string[];
  }[];
}
