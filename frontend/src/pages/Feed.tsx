import { useState } from 'react';
import { RefreshCw, Filter, AlertCircle, Compass } from 'lucide-react';
import { useFeed, useProfile, useFetchSources } from '../api/hooks';
import { ArticleCard } from '../components/ArticleCard';

export function Feed() {
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState<'relevance' | 'date'>('relevance');
  const [minRelevance, setMinRelevance] = useState(0);
  const [vendorFilter, setVendorFilter] = useState<string>('');
  const perPage = 20;

  const { data: feed, isLoading, error, refetch } = useFeed({
    page,
    per_page: perPage,
    sort_by: sortBy,
    min_relevance: minRelevance,
    vendor: vendorFilter || undefined,
  });

  const { data: profile } = useProfile();
  const fetchSources = useFetchSources();

  const handleRefresh = async () => {
    await fetchSources.mutateAsync(undefined);
    refetch();
  };

  const vendors = ['', 'AWS', 'GCP', 'OpenAI', 'Anthropic', 'GitHub', 'GitHub OSS'];

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Error loading feed</h2>
        <p className="text-gray-600 mb-4">
          {error instanceof Error ? error.message : 'Failed to load articles'}
        </p>
        <button
          onClick={() => refetch()}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Try again
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Your Feed</h1>
            {profile && profile.tech_stack.length > 0 && (
              <p className="text-sm text-gray-600 mt-1">
                Personalized for: {profile.tech_stack.slice(0, 5).join(', ')}
                {profile.tech_stack.length > 5 && ` +${profile.tech_stack.length - 5} more`}
              </p>
            )}
          </div>

          <button
            onClick={handleRefresh}
            disabled={fetchSources.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${fetchSources.isPending ? 'animate-spin' : ''}`} />
            {fetchSources.isPending ? 'Fetching...' : 'Refresh'}
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-4 bg-white p-4 rounded-lg border border-gray-200">
          {/* Sort */}
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Sort:</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'relevance' | 'date')}
              className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="relevance">Relevance</option>
              <option value="date">Date</option>
            </select>
          </div>

          {/* Vendor filter */}
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Vendor:</label>
            <select
              value={vendorFilter}
              onChange={(e) => setVendorFilter(e.target.value)}
              className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All vendors</option>
              {vendors.slice(1).map((vendor) => (
                <option key={vendor} value={vendor}>
                  {vendor}
                </option>
              ))}
            </select>
          </div>

          {/* Minimum relevance */}
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Min relevance:</label>
            <select
              value={minRelevance}
              onChange={(e) => setMinRelevance(Number(e.target.value))}
              className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value={0}>All</option>
              <option value={0.3}>30%+</option>
              <option value={0.5}>50%+</option>
              <option value={0.7}>70%+</option>
            </select>
          </div>

          {/* Results count */}
          {feed && (
            <div className="ml-auto text-sm text-gray-600">
              {feed.total} articles
            </div>
          )}
        </div>
      </div>

      {/* Trending Technologies (Phase 2: Direction A) */}
      {feed && feed.trending_technologies && feed.trending_technologies.length > 0 && (
        <div className="mb-6 bg-indigo-50 border border-indigo-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Compass className="w-4 h-4 text-indigo-600" />
            <h2 className="text-sm font-semibold text-indigo-900">
              Trending in Your Field
            </h2>
          </div>
          <div className="flex flex-wrap gap-2">
            {feed.trending_technologies.map((tech) => (
              <div
                key={tech.name}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-indigo-200 rounded-full text-sm"
              >
                <span className="font-medium text-indigo-800">{tech.name}</span>
                <span className="text-xs text-indigo-500">
                  {tech.count} articles
                </span>
                {tech.related_to.length > 0 && (
                  <span className="text-xs text-gray-400" title={`Related to: ${tech.related_to.join(', ')}`}>
                    via {tech.related_to[0]}{tech.related_to.length > 1 ? ` +${tech.related_to.length - 1}` : ''}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Loading state */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
        </div>
      )}

      {/* Empty state */}
      {!isLoading && feed && feed.items.length === 0 && (
        <div className="text-center py-12">
          <Filter className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No articles found</h2>
          <p className="text-gray-600 mb-4">
            Try adjusting your filters or refreshing the feed.
          </p>
          <button
            onClick={handleRefresh}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Fetch new articles
          </button>
        </div>
      )}

      {/* Articles grid */}
      {feed && feed.items.length > 0 && (
        <div className="space-y-4">
          {feed.items.map((article) => (
            <ArticleCard key={article.id} article={article} />
          ))}
        </div>
      )}

      {/* Pagination */}
      {feed && feed.pages > 1 && (
        <div className="flex items-center justify-center gap-2 mt-8">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>

          <span className="px-4 py-2 text-sm text-gray-600">
            Page {page} of {feed.pages}
          </span>

          <button
            onClick={() => setPage((p) => Math.min(feed.pages, p + 1))}
            disabled={page === feed.pages}
            className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
