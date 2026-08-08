# Where to paste GITHUB_TOKEN

**I cannot paste the token for you.** Anything put in this chat or in the git repo is public to anyone with access. You paste it only into Cloudflare’s secret store.

## Before you start

1. **Revoke** any token you already pasted in chat.
2. Create a **new** fine-grained PAT with **Issues: Read and write** on one results repo only.
3. Edit [`wrangler.toml`](wrangler.toml): set `GITHUB_OWNER` and `GITHUB_REPO` to that repo.

## Option A — Terminal (recommended)

**Node.js:** current Wrangler (`latest`) needs **Node ≥ 22**. This folder pins **wrangler@4.86.0**, which still runs on **Node 20**. Prefer upgrading Node when you can (`nvm install 22 && nvm use 22`).

From this folder (`backend/`):

```bash
npm install
npx wrangler login
npx wrangler secret put GITHUB_TOKEN
```

When the terminal prompts **“Enter a secret value”**, paste the token **there** (in your own terminal), press Enter.  
You should not see the token committed to any file.

Then deploy **only the results worker** (not the static site):

```bash
npm run deploy
# or: npx wrangler deploy --config wrangler.toml
```

If you skip `npm install` and call bare `npx wrangler`, npm may pull `latest` and fail on Node 20 — use the pinned install above, or:

```bash
npx wrangler@4.86.0 deploy --config wrangler.toml
```

Use `--config wrangler.toml` so Wrangler does not pick up the parent [`../wrangler.jsonc`](../wrangler.jsonc), which bundles the whole site as static assets (and will fail on `node_modules`).

Copy the printed `https://….workers.dev` URL into [`../config/site.json`](../config/site.json):

```json
"results": {
  "endpoint": "https://quiz-challenge-results.YOUR_SUBDOMAIN.workers.dev",
  "auto_submit": true
}
```

## Option B — Cloudflare Dashboard (no CLI paste in chat)

1. Open [Cloudflare Dashboard](https://dash.cloudflare.com/) → **Workers & Pages**
2. Create / open worker `quiz-challenge-results`
3. **Settings** → **Variables and Secrets** → **Add** → type **Secret**
4. Name: `GITHUB_TOKEN`
5. Value: paste the new token → Save
6. Also add plain text vars: `GITHUB_OWNER`, `GITHUB_REPO`
7. Deploy, then put the worker URL in `config/site.json` as above

## Deploy targets

| What | Where | Command |
|------|--------|---------|
| **Results API** (leaderboard, GitHub) | `backend/` | `wrangler deploy --config wrangler.toml` |
| **Static site** (HTML/JS/content) | repo root | `wrangler deploy` (uses `wrangler.jsonc`; excludes `node_modules` via `.assetsignore`) |

- Edit `GITHUB_OWNER` / `GITHUB_REPO` in `wrangler.toml` if you tell me the repo name  
- Wire `site.json` once you give me the **worker URL** (not the token)

## What I will not do

- Accept or store your PAT in chat  
- Write the token into any project file  
