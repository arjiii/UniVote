import { writable } from 'svelte/store';
import { browser } from '$app/environment';

const initialTheme = browser ? (localStorage.getItem('univote_theme') || 'light') : 'light';
export const theme = writable(initialTheme);

if (browser) {
  theme.subscribe((val) => {
    localStorage.setItem('univote_theme', val);
    if (val === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  });
}

export function toggleTheme() {
  theme.update((current) => (current === 'light' ? 'dark' : 'light'));
}
