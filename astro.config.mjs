// @ts-check
import { defineConfig, fontProviders, envField } from 'astro/config';
import { env } from 'node:process';
import node from '@astrojs/node';
import vercel from '@astrojs/vercel';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import { storyblok } from '@storyblok/astro';
import basicSsl from '@vitejs/plugin-basic-ssl';

const isDev = process.env.NODE_ENV !== 'production';

// https://astro.build/config
export default defineConfig({
  site: 'https://example.com',
  output: isDev ? 'server' : 'static',
  adapter: isDev ? node({ mode: 'standalone' }) : vercel(),
  integrations: [
    mdx(),
    sitemap(),
    storyblok({
      accessToken: env.STORYBLOK_TOKEN,
      apiOptions: {
        region: 'eu',
      },
      livePreview: isDev,
      components: {
        page: 'storyblok/Page',
        articolo: 'storyblok/Articolo',
        feature: 'storyblok/Feature',
        grid: 'storyblok/Grid',
        teaser: 'storyblok/Teaser',
      },
    }),
  ],
  image: { service: { entrypoint: 'astro/assets/services/noop' } },
  markdown: {
    remarkPlugins: [],
    rehypePlugins: [],
  },
  experimental: {
    contentIntellisense: false,
  },
  fonts: [
    {
      provider: fontProviders.local(),
      name: 'Atkinson',
      cssVariable: '--font-atkinson',
      fallbacks: ['sans-serif'],
      options: {
        variants: [
          {
            src: ['./src/assets/fonts/atkinson-regular.woff'],
            weight: 400,
            style: 'normal',
            display: 'swap',
          },
          {
            src: ['./src/assets/fonts/atkinson-bold.woff'],
            weight: 700,
            style: 'normal',
            display: 'swap',
          },
        ],
      },
    },
  ],
  vite: {
    plugins: isDev ? [basicSsl()] : [],
    server: {
      https: isDev,
    },
  },
});
