import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import UrlField from '$lib/components/fields/UrlField.svelte';

describe('UrlField', () => {
	it('renders a clickable link in view mode', () => {
		render(UrlField, { value: 'https://example.com', onSave: vi.fn() });
		const link = screen.getByRole('link');
		expect(link).toHaveAttribute('href', 'https://example.com');
		expect(link).toHaveAttribute('target', '_blank');
	});

	it('switches to a url input on wrapper click', async () => {
		render(UrlField, { value: 'https://example.com', onSave: vi.fn() });
		await userEvent.click(document.querySelector('.field-view') as HTMLElement);
		const input = screen.getByRole('textbox');
		expect((input as HTMLInputElement).type).toBe('url');
	});

	it('calls onSave on Enter', async () => {
		const onSave = vi.fn();
		render(UrlField, { value: 'https://example.com', onSave });
		await userEvent.click(document.querySelector('.field-view') as HTMLElement);
		await userEvent.clear(screen.getByRole('textbox'));
		await userEvent.type(screen.getByRole('textbox'), 'https://new.com{Enter}');
		expect(onSave).toHaveBeenCalledWith('https://new.com');
	});

	it('cancels on Escape', async () => {
		const onSave = vi.fn();
		render(UrlField, { value: 'https://example.com', onSave });
		await userEvent.click(document.querySelector('.field-view') as HTMLElement);
		await userEvent.keyboard('{Escape}');
		expect(onSave).not.toHaveBeenCalled();
		expect(screen.getByRole('link')).toBeInTheDocument();
	});

	it('does not enter edit mode when readonly', async () => {
		render(UrlField, { value: 'https://example.com', readonly: true, onSave: vi.fn() });
		await userEvent.click(document.querySelector('.field-view') as HTMLElement);
		expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
	});

	it('renders nothing for empty value', () => {
		render(UrlField, { value: '', onSave: vi.fn() });
		expect(screen.queryByRole('link')).not.toBeInTheDocument();
	});
});
