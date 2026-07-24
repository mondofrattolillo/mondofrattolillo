# MondoFrattolillo

Blog personale di Marco Frattolillo: racconti di viaggio, vita a Parigi, famiglia e riflessioni sparse, online dal 2007.

Il sito è costruito con [Astro](https://astro.build), integra [Storyblok](https://www.storyblok.com/) come CMS headless per i nuovi contenuti, e mantiene l'archivio storico del blog in formato Markdown/MDX migrato dalla vecchia piattaforma.

## Stack tecnico

- **Astro** — framework per siti statici ad alte performance
- **Storyblok** — CMS headless per gestione contenuti visuale
- **Markdown/MDX** — formato per l'archivio storico degli articoli
- **Vercel** — hosting e deploy continuo

## Struttura del progetto

```text
/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   ├── content/
│   │   └── blog/        # Archivio articoli storici (Markdown)
│   ├── layouts/
│   └── pages/
├── astro.config.mjs
├── package.json
└── tsconfig.json
```

Ogni articolo dell'archivio si trova in `src/content/blog/<slug>/index.md`, con le relative immagini nella stessa cartella.

## Comandi disponibili

Tutti i comandi vanno eseguiti dalla root del progetto, da terminale:

| Comando             | Azione                                           |
| :------------------ | :------------------------------------------------ |
| `npm install`        | Installa le dipendenze                            |
| `npm run dev`         | Avvia il server di sviluppo su `localhost:4321`   |
| `npm run build`       | Compila il sito di produzione in `./dist/`        |
| `npm run preview`     | Anteprima locale della build prima del deploy     |

## Deploy

Il sito è collegato a Vercel per il deploy automatico ad ogni push sul branch `main`.

## Contenuti

Gli articoli storici sono stati migrati dalla piattaforma precedente e coprono oltre 15 anni di pubblicazioni, dal 2007 ad oggi.
