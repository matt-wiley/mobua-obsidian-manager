const HLJS_THEME_KEY = 'hljs-theme';
const DEFAULT_THEME = 'github';

let _hljsTheme = $state(localStorage.getItem(HLJS_THEME_KEY) ?? DEFAULT_THEME);

export const settingsStore = {
	get hljsTheme() { return _hljsTheme; },
	setHljsTheme(theme: string) {
		_hljsTheme = theme;
		localStorage.setItem(HLJS_THEME_KEY, theme);
	}
};

export const HLJS_THEMES: { value: string; label: string; dark: boolean }[] = [
	{ value: 'github',           label: 'GitHub',            dark: false },
	{ value: 'atom-one-light',   label: 'Atom One Light',    dark: false },
	{ value: 'vs',               label: 'Visual Studio',     dark: false },
	{ value: 'tokyo-night-light',label: 'Tokyo Night Light', dark: false },
	{ value: 'github-dark',      label: 'GitHub Dark',       dark: true  },
	{ value: 'atom-one-dark',    label: 'Atom One Dark',     dark: true  },
	{ value: 'monokai',          label: 'Monokai',           dark: true  },
	{ value: 'vs2015',           label: 'VS 2015',           dark: true  },
	{ value: 'tokyo-night-dark', label: 'Tokyo Night Dark',  dark: true  },
];
