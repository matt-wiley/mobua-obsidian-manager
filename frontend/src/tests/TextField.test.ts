import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import TextField from '$lib/components/fields/TextField.svelte';

describe('TextField', () => {
	it('renders the value in view mode', () => {
		render(TextField, { value: 'hello', onSave: vi.fn() });
		expect(screen.getByText('hello')).toBeInTheDocument();
	});

	it('switches to edit mode on click', async () => {
		render(TextField, { value: 'hello', onSave: vi.fn() });
		await userEvent.click(screen.getByText('hello'));
		expect(screen.getByRole('textbox')).toBeInTheDocument();
		expect(screen.getByRole('textbox')).toHaveValue('hello');
	});

	it('calls onSave with new value on Enter', async () => {
		const onSave = vi.fn();
		render(TextField, { value: 'hello', onSave });
		await userEvent.click(screen.getByText('hello'));
		await userEvent.clear(screen.getByRole('textbox'));
		await userEvent.type(screen.getByRole('textbox'), 'world{Enter}');
		expect(onSave).toHaveBeenCalledWith('world');
	});

	it('calls onSave on blur', async () => {
		const onSave = vi.fn();
		render(TextField, { value: 'hello', onSave });
		await userEvent.click(screen.getByText('hello'));
		await userEvent.clear(screen.getByRole('textbox'));
		await userEvent.type(screen.getByRole('textbox'), 'world');
		await userEvent.tab();
		expect(onSave).toHaveBeenCalledWith('world');
	});

	it('cancels on Escape without saving', async () => {
		const onSave = vi.fn();
		render(TextField, { value: 'hello', onSave });
		await userEvent.click(screen.getByText('hello'));
		await userEvent.type(screen.getByRole('textbox'), 'changed{Escape}');
		expect(onSave).not.toHaveBeenCalled();
		expect(screen.getByText('hello')).toBeInTheDocument();
	});

	it('does not call onSave when value is unchanged', async () => {
		const onSave = vi.fn();
		render(TextField, { value: 'hello', onSave });
		await userEvent.click(screen.getByText('hello'));
		await userEvent.tab();
		expect(onSave).not.toHaveBeenCalled();
	});

	it('does not enter edit mode when readonly', async () => {
		render(TextField, { value: 'hello', readonly: true, onSave: vi.fn() });
		await userEvent.click(screen.getByText('hello'));
		expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
	});
});
