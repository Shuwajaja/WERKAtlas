import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  site: 'https://wbs-edu.github.io',
  base: '/WERKAtlas/',
  output: 'static',
  integrations: [tailwind()],
  vite: {
    server: {
      fs: {
        allow: ['..']
      }
    }
  }
});
