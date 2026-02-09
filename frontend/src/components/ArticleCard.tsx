import { ExternalLink, Clock, Tag, BookmarkPlus, FileCheck } from 'lucide-react';
import type { Article } from '../types';
import { useRecordAction } from '../api/hooks';

interface ArticleCardProps {
  article: Article;
}

export function ArticleCard({ article }: ArticleCardProps) {
  const recordAction = useRecordAction();

  const formattedDate = article.published_at
    ? new Date(article.published_at).toLocaleDateString('ja-JP', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    : 'Unknown date';

  const vendorClass = `vendor-${article.vendor.toLowerCase().replace(/\s+/g, '-')}`;

  const handleClick = () => {
    recordAction.mutate({ articleId: article.id, action: 'click' });
  };

  const handleBookmark = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    recordAction.mutate({ articleId: article.id, action: 'bookmark' });
  };

  return (
    <article className="bg-white rounded-lg border border-gray-200 p-5 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-3">
        <div className="flex items-center gap-2 flex-wrap">
          {/* Vendor badge */}
          <span className={`px-2 py-1 text-xs font-medium rounded ${vendorClass}`}>
            {article.vendor}
          </span>

          {/* Primary source badge */}
          {article.is_primary_source && (
            <span className="px-2 py-1 text-xs font-medium rounded bg-emerald-100 text-emerald-800 flex items-center gap-1">
              <FileCheck className="w-3 h-3" />
              Primary
            </span>
          )}
        </div>

        {/* Date + Bookmark */}
        <div className="flex items-center gap-3">
          <button
            onClick={handleBookmark}
            className="text-gray-400 hover:text-blue-600 transition-colors"
            title="Bookmark"
          >
            <BookmarkPlus className="w-4 h-4" />
          </button>
          <span className="flex items-center gap-1 text-sm text-gray-500 whitespace-nowrap">
            <Clock className="w-3 h-3" />
            {formattedDate}
          </span>
        </div>
      </div>

      {/* Title */}
      <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
        {article.title}
      </h3>

      {/* Summary */}
      <p className="text-gray-600 text-sm mb-4 line-clamp-3">
        {article.summary.replace(/<[^>]*>/g, '').slice(0, 300)}
      </p>

      {/* Tags */}
      {article.tags && article.tags.length > 0 && (
        <div className="flex items-center gap-2 mb-4 flex-wrap">
          <Tag className="w-3 h-3 text-gray-400" />
          {article.tags.slice(0, 5).map((tag, index) => (
            <span
              key={index}
              className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded"
            >
              {tag}
            </span>
          ))}
          {article.tags.length > 5 && (
            <span className="text-xs text-gray-400">
              +{article.tags.length - 5} more
            </span>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-gray-100">
        <a
          href={article.url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={handleClick}
          className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          Read original
          <ExternalLink className="w-3 h-3" />
        </a>

        {article.source_plugin && (
          <span className="text-xs text-gray-400">
            via {article.source_plugin}
          </span>
        )}
      </div>
    </article>
  );
}
