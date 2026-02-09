// React Query hooks for BrainStream API

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { feedApi } from './client';

// Query keys
export const queryKeys = {
  feed: (params?: Parameters<typeof feedApi.getFeed>[0]) => ['feed', params] as const,
  article: (id: string) => ['article', id] as const,
  topology: ['topology'] as const,
  sources: ['sources'] as const,
};

export function useFeed(params?: Parameters<typeof feedApi.getFeed>[0]) {
  return useQuery({
    queryKey: queryKeys.feed(params),
    queryFn: () => feedApi.getFeed(params),
  });
}

export function useArticle(id: string) {
  return useQuery({
    queryKey: queryKeys.article(id),
    queryFn: () => feedApi.getArticle(id),
    enabled: !!id,
  });
}

export function useTopology() {
  return useQuery({
    queryKey: queryKeys.topology,
    queryFn: feedApi.getTopology,
  });
}

export function useSources() {
  return useQuery({
    queryKey: queryKeys.sources,
    queryFn: feedApi.getSources,
  });
}

export function useRecordAction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ articleId, action }: { articleId: string; action: 'click' | 'bookmark' | 'skip' }) =>
      feedApi.recordAction(articleId, action),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feed'] });
    },
  });
}

export function useCollect() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => feedApi.collect(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feed'] });
      queryClient.invalidateQueries({ queryKey: queryKeys.topology });
      queryClient.invalidateQueries({ queryKey: queryKeys.sources });
    },
  });
}
