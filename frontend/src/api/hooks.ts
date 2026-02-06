// React Query hooks for BrainStream API

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { articlesApi, profileApi, sourcesApi } from './client';
import type { ProfileUpdateRequest } from '../types';

// Query keys
export const queryKeys = {
  feed: (params?: Parameters<typeof articlesApi.getFeed>[0]) => ['feed', params] as const,
  articles: (params?: Parameters<typeof articlesApi.getList>[0]) => ['articles', params] as const,
  article: (id: string) => ['article', id] as const,
  articleRelevance: (id: string) => ['articleRelevance', id] as const,
  profile: ['profile'] as const,
  techStackSuggestions: ['techStackSuggestions'] as const,
  vendors: ['vendors'] as const,
  sources: ['sources'] as const,
};

// Feed hooks
export function useFeed(params?: Parameters<typeof articlesApi.getFeed>[0]) {
  return useQuery({
    queryKey: queryKeys.feed(params),
    queryFn: () => articlesApi.getFeed(params),
  });
}

// Articles hooks
export function useArticles(params?: Parameters<typeof articlesApi.getList>[0]) {
  return useQuery({
    queryKey: queryKeys.articles(params),
    queryFn: () => articlesApi.getList(params),
  });
}

export function useArticle(id: string) {
  return useQuery({
    queryKey: queryKeys.article(id),
    queryFn: () => articlesApi.getById(id),
    enabled: !!id,
  });
}

export function useArticleRelevance(id: string) {
  return useQuery({
    queryKey: queryKeys.articleRelevance(id),
    queryFn: () => articlesApi.getRelevance(id),
    enabled: !!id,
  });
}

// Profile hooks
export function useProfile() {
  return useQuery({
    queryKey: queryKeys.profile,
    queryFn: profileApi.get,
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ProfileUpdateRequest) => profileApi.update(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.profile });
      queryClient.invalidateQueries({ queryKey: ['feed'] });
    },
  });
}

export function useAddTechStack() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (items: string[]) => profileApi.addTechStack(items),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.profile });
      queryClient.invalidateQueries({ queryKey: ['feed'] });
    },
  });
}

export function useRemoveTechStackItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (item: string) => profileApi.removeTechStackItem(item),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.profile });
      queryClient.invalidateQueries({ queryKey: ['feed'] });
    },
  });
}

export function useTechStackSuggestions() {
  return useQuery({
    queryKey: queryKeys.techStackSuggestions,
    queryFn: profileApi.getSuggestions,
  });
}

export function useVendors() {
  return useQuery({
    queryKey: queryKeys.vendors,
    queryFn: profileApi.getVendors,
  });
}

export function useProcessArticle() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => articlesApi.process(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feed'] });
      queryClient.invalidateQueries({ queryKey: ['articles'] });
    },
  });
}

// Sources hooks
export function useSources() {
  return useQuery({
    queryKey: queryKeys.sources,
    queryFn: sourcesApi.getList,
  });
}

export function useFetchSources() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sourceName?: string) => sourcesApi.fetch(sourceName),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.sources });
      queryClient.invalidateQueries({ queryKey: ['feed'] });
      queryClient.invalidateQueries({ queryKey: ['articles'] });
    },
  });
}
