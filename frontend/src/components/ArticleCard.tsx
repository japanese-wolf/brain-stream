import { ExternalLink, Clock, Tag, TrendingUp, Sparkles, Link2, Compass } from 'lucide-react';
import type { ArticleWithRelevance } from '../types';
import { useProcessArticle } from '../api/hooks';

interface ArticleCardProps {
  article: ArticleWithRelevance;
}

export function ArticleCard({ article }: ArticleCardProps) {
  const displayTitle = article.summary_title || article.original_title;
  const displayContent = article.summary_content || article.original_content;
  const processArticle = useProcessArticle();
  const isProcessing = processArticle.isPending;

  // Format date
  const formattedDate = article.published_at
    ? new Date(article.published_at).toLocaleDateString('ja-JP', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    : 'Unknown date';

  // Get vendor class
  const vendorClass = `vendor-${article.vendor.toLowerCase()}`;

  // Get relevance badge class
  const relevanceClass = article.relevance
    ? `badge-${article.relevance.relevance_level}`
    : '';

  return (
    <article className="bg-white rounded-lg border border-gray-200 p-5 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-3">
        <div className="flex items-center gap-2 flex-wrap">
          {/* Vendor badge */}
          <span className={`px-2 py-1 text-xs font-medium rounded ${vendorClass}`}>
            {article.vendor}
          </span>

          {/* Relevance badge */}
          {article.relevance && article.relevance.total_score > 0 && (
            <span className={`px-2 py-1 text-xs font-medium rounded flex items-center gap-1 ${relevanceClass}`}>
              <TrendingUp className="w-3 h-3" />
              {Math.round(article.relevance.total_score * 100)}%
            </span>
          )}

          {/* Processed indicator */}
          {article.processed_at && (
            <span className="px-2 py-1 text-xs font-medium rounded bg-blue-100 text-blue-800">
              AI Summary
            </span>
          )}
        </div>

        {/* Date */}
        <span className="flex items-center gap-1 text-sm text-gray-500 whitespace-nowrap">
          <Clock className="w-3 h-3" />
          {formattedDate}
        </span>
      </div>

      {/* Title */}
      <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
        {displayTitle}
      </h3>

      {/* Content preview */}
      <p className="text-gray-600 text-sm mb-4 line-clamp-3">
        {displayContent.replace(/<[^>]*>/g, '').slice(0, 300)}
      </p>

      {/* Diff description (if available) */}
      {article.diff_description && (
        <div className="bg-blue-50 border border-blue-100 rounded p-3 mb-4">
          <p className="text-sm text-blue-800">
            <strong>What changed:</strong> {article.diff_description}
          </p>
        </div>
      )}

      {/* Technical impact explanation (if available) */}
      {article.explanation && (
        <div className="bg-amber-50 border border-amber-100 rounded p-3 mb-4">
          <p className="text-sm text-amber-800">
            <strong>Impact:</strong> {article.explanation}
          </p>
        </div>
      )}

      {/* Tech Stack Connection (if available) */}
      {article.tech_stack_connection && (
        <div className="bg-green-50 border border-green-100 rounded p-3 mb-4">
          <p className="text-sm text-green-800">
            <Link2 className="w-3.5 h-3.5 inline mr-1" />
            <strong>Your stack:</strong> {article.tech_stack_connection}
          </p>
        </div>
      )}

      {/* Related Technologies (if available) */}
      {article.related_technologies && article.related_technologies.length > 0 && (
        <div className="flex items-center gap-2 mb-4 flex-wrap">
          <Compass className="w-3.5 h-3.5 text-purple-400" />
          <span className="text-xs text-purple-600 font-medium">Explore:</span>
          {article.related_technologies.map((tech, index) => (
            <span
              key={index}
              className="text-xs text-purple-700 bg-purple-50 px-2 py-0.5 rounded border border-purple-200"
            >
              {tech}
            </span>
          ))}
        </div>
      )}

      {/* AI Summarize button (for unprocessed articles) */}
      {!article.processed_at && (
        <button
          onClick={() => processArticle.mutate(article.id)}
          disabled={isProcessing}
          className="flex items-center gap-1.5 px-3 py-1.5 mb-4 text-sm font-medium text-purple-700 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 disabled:opacity-50 transition-colors"
        >
          <Sparkles className={`w-3.5 h-3.5 ${isProcessing ? 'animate-pulse' : ''}`} />
          {isProcessing ? 'Summarizing...' : 'AI Summarize'}
        </button>
      )}

      {/* Tags */}
      {article.tags && article.tags.length > 0 && (
        <div className="flex items-center gap-2 mb-4 flex-wrap">
          <Tag className="w-3 h-3 text-gray-400" />
          {article.tags.slice(0, 5).map((tag, index) => (
            <span
              key={index}
              className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded"
            >
              {tag.split(',')[0].split(':').pop()}
            </span>
          ))}
          {article.tags.length > 5 && (
            <span className="text-xs text-gray-400">
              +{article.tags.length - 5} more
            </span>
          )}
        </div>
      )}

      {/* Matched keywords (if relevant) */}
      {article.relevance && article.relevance.matched_keywords.length > 0 && (
        <div className="flex items-center gap-2 mb-4 flex-wrap text-xs">
          <span className="text-gray-500">Matched:</span>
          {article.relevance.matched_keywords.map((keyword, index) => (
            <span
              key={index}
              className="text-green-700 bg-green-50 px-2 py-0.5 rounded font-medium"
            >
              {keyword}
            </span>
          ))}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-gray-100">
        <a
          href={article.primary_source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          Read original
          <ExternalLink className="w-3 h-3" />
        </a>

        {article.llm_provider && (
          <span className="text-xs text-gray-400">
            Processed by {article.llm_provider}
          </span>
        )}
      </div>
    </article>
  );
}
