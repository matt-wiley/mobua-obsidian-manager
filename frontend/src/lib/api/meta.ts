import { apiFetch } from './client';

export interface BuildInfo {
	version: string;
	commit: string;
	build_date: string | null;
}

export function getBuildInfo(): Promise<BuildInfo> {
	return apiFetch<BuildInfo>('/meta');
}
