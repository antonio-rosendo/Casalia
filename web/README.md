# Casalia web

Static site that shows the published forecasts, the evaluation results and the method. It has no backend: it reads `public/forecasts.json`, which `ml/publish_forecasts.py` writes.

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # static site in dist/
```

- `src/data/forecasts.ts` loads the forecasts; `src/data/results.ts` holds the frozen evaluation numbers from `ml/reports/`.
- Texts are in `src/locales/en.json` and `src/locales/es.json`.
- `.github/workflows/pages.yml` deploys it to GitHub Pages on every push to `master` that touches `web/`.
