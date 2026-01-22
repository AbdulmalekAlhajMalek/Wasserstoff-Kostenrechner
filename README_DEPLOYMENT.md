# Deployment auf Vercel

## Voraussetzungen

1. Ein Vercel-Konto (kostenlos): https://vercel.com/signup
2. Vercel CLI installiert (optional, für Command Line Deployment)

## Option 1: Deployment über Vercel Website (Empfohlen)

1. **Projekt auf GitHub hochladen** (falls noch nicht geschehen):
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Auf Vercel deployen**:
   - Gehe zu https://vercel.com
   - Klicke auf "Add New Project"
   - Verbinde dein GitHub Repository
   - Vercel erkennt automatisch die statische HTML-Datei
   - Klicke auf "Deploy"

3. **Konfiguration** (falls nötig):
   - Framework Preset: "Other"
   - Build Command: (leer lassen)
   - Output Directory: (leer lassen)
   - Root Directory: (leer lassen)

## Option 2: Deployment über Vercel CLI

1. **Vercel CLI installieren**:
   ```bash
   npm i -g vercel
   ```

2. **Login**:
   ```bash
   vercel login
   ```

3. **Deployen**:
   ```bash
   vercel
   ```

4. **Production Deployment**:
   ```bash
   vercel --prod
   ```

## Wichtige Dateien

- `wasserstoff_simulation.html` - Hauptdatei der Anwendung
- `vercel.json` - Vercel Konfiguration
- `.vercelignore` - Dateien die nicht deployed werden sollen

## Nach dem Deployment

Die Anwendung ist unter einer URL wie `https://your-project.vercel.app` verfügbar.

## Hinweise

- Die Anwendung verwendet Chart.js von CDN, daher keine zusätzlichen Dependencies nötig
- Alle Berechnungen laufen clientseitig (JavaScript)
- Kein Backend-Server erforderlich
