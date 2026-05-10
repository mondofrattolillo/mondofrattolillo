import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
	loader: glob({ base: './src/content/blog', pattern: '**/*.{md,mdx}' }),
	schema: z.object({
		title: z.string(),
		description: z.string().optional(),
		pubDate: z.coerce.date().optional(),
		date: z.coerce.date().optional(),
		updatedDate: z.coerce.date().optional(),
		heroImage: z.string().optional(),
		coverImage: z.string().optional(),
		categories: z.array(z.string()).optional(),
		tags: z.array(z.string()).optional(),
	}),
});

export const collections = { blog };
