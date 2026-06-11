import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

export function formatDriverName(driver) {
  if (!driver) return 'Unknown driver';
  return driver.driver_name || `${driver.given_name || ''} ${driver.family_name || ''}`.trim() || driver.code || driver.driver_id;
}

export function formatDateTime(date, time) {
  if (!date) return 'TBA';
  const iso = time ? `${date}T${time.replace('Z', '+00:00')}` : `${date}T12:00:00`;
  const value = new Date(iso);
  if (Number.isNaN(value.getTime())) return date;
  return value.toLocaleString(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: time ? '2-digit' : undefined,
    minute: time ? '2-digit' : undefined,
  });
}

export function getRaceStatus(race) {
  if (!race?.date) return 'Upcoming';
  const startsAt = new Date(race.time ? `${race.date}T${race.time.replace('Z', '+00:00')}` : `${race.date}T23:59:59`);
  const now = new Date();
  if (Number.isNaN(startsAt.getTime())) return 'Upcoming';
  if (startsAt.toDateString() === now.toDateString()) return 'Race day';
  return startsAt < now ? 'Completed' : 'Upcoming';
}

export function getNextRace(races = []) {
  const now = new Date();
  return races.find((race) => {
    const startsAt = new Date(race.time ? `${race.date}T${race.time.replace('Z', '+00:00')}` : `${race.date}T23:59:59`);
    return startsAt >= now;
  }) || races[races.length - 1] || null;
}

export async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    let message = `API error ${response.status}`;
    try {
      const payload = await response.json();
      message = payload.detail || message;
    } catch {
      // Keep the status-based message when the response is not JSON.
    }
    throw new Error(message);
  }
  return response.json();
}

export function useLiveResource(fetcher, deps = [], options = {}) {
  const { intervalMs = 60000, enabled = true } = options;
  const [state, setState] = useState({
    data: null,
    loading: true,
    error: null,
    updatedAt: null,
    refreshing: false,
  });
  const mounted = useRef(true);

  const load = useCallback(async (mode = 'initial') => {
    if (!enabled) return;
    setState((prev) => ({
      ...prev,
      loading: mode === 'initial' && !prev.data,
      refreshing: mode !== 'initial',
      error: null,
    }));

    try {
      const data = await fetcher();
      if (!mounted.current) return;
      setState({
        data,
        loading: false,
        error: null,
        updatedAt: new Date(),
        refreshing: false,
      });
    } catch (error) {
      if (!mounted.current) return;
      setState((prev) => ({
        ...prev,
        loading: false,
        refreshing: false,
        error: error.message || 'Could not load live data',
      }));
    }
  }, [enabled, fetcher]);

  useEffect(() => {
    mounted.current = true;
    load('initial');
    if (!enabled || !intervalMs) {
      return () => {
        mounted.current = false;
      };
    }

    const timer = window.setInterval(() => load('refresh'), intervalMs);
    return () => {
      mounted.current = false;
      window.clearInterval(timer);
    };
  }, [load, intervalMs, enabled, ...deps]);

  return useMemo(() => ({ ...state, refresh: () => load('manual') }), [state, load]);
}
