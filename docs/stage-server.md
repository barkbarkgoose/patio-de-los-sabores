# Stage server

A stage server runs a copy of the app at its own address (e.g. `https://stage.example.com`) so you can try changes before they go to production. Every push to the `staging` branch deploys automatically: GitHub Actions asks the server to deploy that commit, and the server tests it, builds it and puts it live. Nobody needs to be at a computer, so an agent on your phone can put changes on stage for you to review.

This page is the whole procedure. You can follow it yourself, or point an agent at it. Production is set up by hand instead: [`vps-hosting.md`](vps-hosting.md), which is also the reference for how the hosting scripts work.

## Before you start

Four things, each done once. The setup script checks all of them and tells you which one is missing.

1. **A server set up with vpshome as a stage box.** Create an Ubuntu server with your SSH key at your provider, then from your vpshome folder:
   ```bash
   ./init-server.sh root@SERVER_IP --stage
   ```
   vpshome's README walks through this, including making an SSH key if you don't have one. `--stage` lets scripts use `sudo` without a password, which the setup script and the automatic deploys need.

2. **A domain name for stage, pointing at the server.** At your DNS provider, add an **A record**: name `stage` (for `stage.example.com`), value `SERVER_IP`. Check it from your Mac; it should print the server's IP (new records can take a few minutes):
   ```bash
   dig +short stage.example.com
   ```

3. **The GitHub CLI, logged in as the repo's owner.** It adds the server's read-only deploy key to the repo and saves the key GitHub Actions deploys with as a repo secret.
   ```bash
   brew install gh        # if `gh --version` says "command not found"
   gh auth login          # GitHub.com, then "Login with a web browser"
   gh auth status         # should say "Logged in to github.com account YOU"
   ```

4. **The repo on GitHub, with your git name and email set.** `git remote -v` should show `origin  git@github.com:YOU/REPO.git`, and `git config user.email` should print your email: it's used for the certificate notices and for your admin account on the site. If either is missing:
   ```bash
   git remote add origin git@github.com:YOU/REPO.git && git push -u origin main
   git config --global user.name "Your Name" && git config --global user.email you@example.com
   ```

## Set it up

From the project folder:

```bash
./hosting/setup-stage.sh https://stage.example.com
```

The first run writes `hosting/.env.stage` (the stage server's settings). Later runs read it, so after that it's just `./hosting/setup-stage.sh`. It takes 10–20 minutes the first time on a small server, most of it installing packages and the first build.

**It stops whenever it needs you.** Each stop prints `✗`, what's wrong and the exact commands to fix it. Do that and run the same command again; everything already done is skipped. On a first run it always stops at least once, asking you to commit two files and push them to `staging` (step 7 below). That's expected.

In order, it:

1. checks that `gh` is logged in and can manage the repo
2. checks that you can log in to the server and use `sudo` without a password
3. provisions the server (`hosting/provision.sh`): packages, Python, Node, PostgreSQL, nginx, a Let's Encrypt certificate, backups, the app's service
4. adds the server's read-only deploy key to the GitHub repo, so the server can fetch the code
5. saves the server's SSH host key in `hosting/.env.stage`, so GitHub Actions can check it's talking to the right server
6. makes the key GitHub Actions deploys with: it's installed on the server where it can run only the deploy, and saved in GitHub as the `STAGE_SSH_KEY` secret
7. checks that the `staging` branch on GitHub has the workflow (`.github/workflows/deploy-stage.yml`) and the current `hosting/.env.stage`. The first time, it stops and gives you the commands to commit them and push them to `staging`; that push also starts the first deploy, in GitHub Actions
8. deploys, if nothing is deployed yet
9. creates your admin account on the site, with a generated password

| When it stops with | Do this |
|---|---|
| the GitHub CLI is not installed / not logged in | `brew install gh`, then `gh auth login` (see "Before you start", item 3) |
| your GitHub login can't manage the repo | `gh auth status`: log in as the repo's owner (`gh auth switch`, or `gh auth login` again) |
| `STAGE.DOMAIN` doesn't resolve to an address | add the DNS A record (item 2) and wait until `dig +short STAGE.DOMAIN` prints the IP |
| can't log in to `YOU@STAGE.DOMAIN` with your SSH key | the server isn't set up yet: run vpshome's `init-server.sh` (item 1). If you're sure it is, `ssh -v YOU@STAGE.DOMAIN` shows why |
| sudo asks for a password | the server was set up without `--stage`: run `./init-server.sh root@SERVER_IP --stage` again from vpshome |
| the `staging` branch on GitHub needs `.github/workflows/deploy-stage.yml` / `hosting/.env.stage` | commit both and push them to `staging` (the exact commands are printed). Wait for the deploy it starts to go green in the Actions tab, then run the script again |
| the first deploy failed … another deploy is running | GitHub Actions is doing the first deploy: wait for it to finish, then run the script again |

At the end it prints the site's address, the Django admin's address, and **your admin email and password. The password is shown only once**, so save it in your password manager straight away.

## Sign in for the first time

1. Open the stage address in Chrome or Safari and sign in with the email and password the script printed.
2. The site asks you to add a passkey (admin accounts must have one). Follow your browser's or password manager's prompt.
3. From then on you sign in with the passkey. The Django admin (address printed by the script, and **Admin** in the account menu) opens only after a passkey sign-in.

The site is private: every page needs a sign-in. To let someone else in, make them an account:

```bash
ssh YOU@STAGE.DOMAIN 'sudo -u NAME /srv/NAME/bin/manage add_user their@email.com --name "Their Name"'
```

`NAME` is `DEPLOY_NAME` in `hosting/.env.stage`. It asks for their password twice.

## Deploying changes

**Push to `staging`.** The `staging` branch is only a pointer to whatever should be on stage, so it's normal to overwrite it with the branch you want to see:

```bash
git push --force origin HEAD:staging     # put the current branch on stage
```

Then watch it in GitHub: the repo's **Actions** tab → **Deploy to stage**, or `gh run watch` in the terminal. A deploy takes a few minutes on a small server.

- **Green:** the commit is live on stage.
- **Red:** open the run to see why. If the tests or the build failed, nothing on the server changed and the previous version is still running. Fix it and push again.

Other ways to deploy:

- **Another branch, without touching `staging`:** Actions tab → **Deploy to stage** → **Run workflow** → pick the branch → **Run workflow**. The branch must contain the workflow file and `hosting/.env.stage` (any branch made from `main` after setup does).
- **From your Mac:** `./hosting/deploy.sh --env hosting/.env.stage` deploys the tip of `staging`; add a branch name or commit to deploy that instead.
- **From an agent:** ask it to "deploy to stage". [`AGENTS.md`](../AGENTS.md) tells it how.

**What's live:** `ssh YOU@STAGE.DOMAIN cat /srv/NAME/REVISION` prints the commit, branch, time and who deployed it.

**Going back to an earlier version:** `./hosting/deploy.sh --env hosting/.env.stage COMMIT`, or `git push --force origin COMMIT:staging`.

## How it works

```
git push origin HEAD:staging
        │
        ▼
GitHub Actions (.github/workflows/deploy-stage.yml)
  reads the server's address and host key from hosting/.env.stage
  ssh YOU@STAGE.DOMAIN <commit>         with the STAGE_SSH_KEY secret: it can run only bin/ci-deploy
        │
        ▼
/srv/NAME/bin/ci-deploy  ──▶  /srv/NAME/bin/deploy <commit>
  fetch into staging/ → tests → frontend build → back up the DB → copy live → migrate → restart → health check
```

- **Only one deploy runs at a time.** A push that arrives during a deploy waits for it.
- **A deploy is never cut off halfway.** It runs on the server in its own session: if the connection to GitHub drops or the run is cancelled, it still finishes (or is stopped after 25 minutes). Its output is in `/srv/NAME/staging/ci-deploy.log`.
- **Production is out of reach:** its address isn't in the repo, and the Actions key exists only on the stage server.
- **Cost:** private repos pay for Actions by the minute, and a run lasts as long as the deploy (a few minutes). The minutes included with a GitHub account cover hundreds of deploys a month; see your GitHub billing page.

Where everything lives:

| What | Where |
|---|---|
| stage server settings (address, app name, domain, branch, host key) | `hosting/.env.stage`, committed |
| the deploy workflow | `.github/workflows/deploy-stage.yml` |
| the key Actions deploys with | GitHub: repo → Settings → Secrets and variables → Actions → `STAGE_SSH_KEY`; on the server, the line ending `ci-deploy-NAME` in `~/.ssh/authorized_keys` |
| the key the server fetches code with | GitHub: repo → Settings → Deploy keys (read-only) |
| the app on the server | `/srv/NAME` (layout: [`vps-hosting.md`](vps-hosting.md#server-layout)) |
| app secrets and settings (`REQUIRE_LOGIN`, email, …) | `/srv/NAME/.env` on the server; after editing, `sudo systemctl restart NAME` |

## Changing things

- **Replace the CI key** (e.g. if it leaked): `gh secret delete STAGE_SSH_KEY`, then `./hosting/setup-stage.sh`. It makes a new key and removes the old one from the server.
- **A new server for stage:** set it up with vpshome, point the A record at it, then run `ssh-keygen -R STAGE.DOMAIN` (your Mac remembers the old server's fingerprint) and `./hosting/setup-stage.sh`. It saves the new host key in `hosting/.env.stage` and stops to ask you to commit and push it.
- **Pause automatic deploys:** Actions tab → **Deploy to stage** → **⋯** → **Disable workflow** (and **Enable** to resume).
- **Remove stage completely:** delete the server at your provider; `gh secret delete STAGE_SSH_KEY`; remove the deploy key under repo → Settings → Deploy keys; delete `hosting/.env.stage` and `.github/workflows/deploy-stage.yml` and commit.
