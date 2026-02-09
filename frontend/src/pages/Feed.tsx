import { useState } from 'react';
import { RefreshCw, Filter, AlertCircle } from 'lucide-react';
import { useFeed, useCollect } from '../api/hooks';
import { ArticleCard } from '../components/ArticleCard';

const vendors = ['', 'AWS', 'GCP', 'OpenAI', 'Anthropic', 'GitHub', 'GitHub OSS'];

export function Feed() {
  const [vendorFilter, setVendorFilter] = useState<string>('');
  const [primaryOnly, setPrimaryOnly] = useState(false);
  const [limit] = useState(20);

  const { data: feed, isLoading, error } = useFeed({
    limit,
    vendor: vendorFilter || undefined,
    primary_only: primaryOnly,
  });

  const collect = useCollect();

  const handleRefresh = async () => {
    await collect.mutateAsync();
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Your Feed</h1>
            <p className="text-sm text-gray-600 mt-1">
              Topology-based discovery with Thompson Sampling
            </p>
          </div>

          <button
            onClick={handleRefresh}
            disabled={collect.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${collect.isPending ? 'animate-spin' : ''}`} />
            {collect.isPending ? 'Fetching...' : 'Refresh'}
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-4 bg-white p-4 rounded-lg border border-gray-200">
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

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={primaryOnly}
              onChange={(e) => setPrimaryOnly(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm font-medium text-gray-700">Primary sources only</span>
          </label>

          {feed && (
            <div className="ml-auto text-sm text-gray-600">
              {feed.total} articles
            </div>
          )}
        </div>
      </div>

      {/* Collection result */}
      {collect.isSuccess && collect.data && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-800">
          Collected {collect.data.total_new} new articles from {collect.data.sources.length} sources
          ({collect.data.duration_ms}ms)
        </div>
      )}

      {/* Error state */}
      {(error || collect.isError) && (
        <div className="flex flex-col items-center justify-center py-12">
          <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600">Failed to load feed. Is the backend running on port 3001?</p>
        </div>
      )}

      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
        </div>
      )}

      {/* Empty */}
      {!isLoading && feed && feed.items.length === 0 && (
        <div className="text-center py-12">
          <Filter className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No articles yet</h2>
          <p className="text-gray-600 mb-4">
            Click "Refresh" to fetch articles from data sources.
          </p>
        </div>
      )}

      {/* Articles */}
      {feed && feed.items.length > 0 && (
        <div className="space-y-4">
          {feed.items.map((article) => (
            <ArticleCard key={article.id} article={article} />
          ))}
        </div>
      )}
    </div>
  );
}
