import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { fileURLToPath } from 'url';
import { resolve } from 'path';

const __dirname = fileURLToPath(new URL('.', import.meta.url));

export default defineConfig({
	plugins: [svelte({ hot: false })],
	resolve: {
		alias: {
			$lib: resolve(__dirname, 'src/lib'),
			'$app/navigation': resolve(__dirname, 'src/tests/mocks/app-navigation.ts'),
			'$app/stores': resolve(__dirname, 'src/tests/mocks/app-stores.ts')
		},
		conditions: ['browser']
	},
	test: {
		environment: 'jsdom',
		setupFiles: ['src/tests/setup.ts'],
		include: ['src/tests/**/*.test.ts'],
		globals: true
	}
});
