import { apiFetch } from './client';

export interface VaultInfo {
	id: string;
	name: string;
	path: string;
}

export interface Config {
	vault_configured: boolean;
	vaults: VaultInfo[];
}

export function getConfig(): Promise<Config> {
	return apiFetch('/config');
}

export function addVault(name: string, path: string): Promise<VaultInfo> {
	return apiFetch('/config/vault', {
		method: 'POST',
		body: JSON.stringify({ name, path })
	});
}

export function removeVault(id: string): Promise<void> {
	return apiFetch(`/config/vaults/${encodeURIComponent(id)}`, { method: 'DELETE' });
}
