# UniVote

A sophisticated electronic voting system.

## Deployment

### Backend (Railway)
1. Link your GitHub repository to Railway.
2. Railway will automatically detect the `Procfile` and use it to start the service.
3. Configure the following Environment Variables:
   - `SUPABASE_URL`: Your Supabase Project URL.
   - `SUPABASE_KEY`: Your Supabase Service Role Key or API Key.
   - `ALLOWED_ORIGINS`: Comma-separated list of your frontend URLs (e.g., `https://your-app.vercel.app`).
4. The backend includes a `/health` endpoint for monitoring.

### Frontend (Vercel)
1. Import your repository to Vercel.
2. Vercel will detect SvelteKit and use the `@sveltejs/adapter-vercel`.
3. Configure the following Environment Variable:
   - `VITE_API_BASE_URL`: The URL of your deployed Railway backend (e.g., `https://univote-api.up.railway.app`).
4. Deploy!

## Local Development
...
 online voting system
