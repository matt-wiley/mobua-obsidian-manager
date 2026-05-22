const BASE = '/api';

export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
	const res = await fetch(`${BASE}${path}`, {
		headers: { 'Content-Type': 'application/json', ...options?.headers },
		...options
	});

	if (res.status === 204) return undefined as T;

	if (!res.ok) {
		let message = `API ${res.status}`;
		try {
			const body = await res.json();
			message = body.detail ?? message;
		} catch {
			// ignore parse error, use status code message
		}
		throw new Error(message);
	}

	return res.json();
}
