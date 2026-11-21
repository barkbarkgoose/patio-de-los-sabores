# Notes for coding agents

## Deploying to stage

The stage server's address is `DEPLOY_DOMAIN` in `hosting/.env.stage`. Pushing to the `staging` branch deploys it: GitHub Actions ("Deploy to stage") has the server test, build and deploy that commit. If the tests or build fail, nothing on the server changes.

When asked to "deploy to stage" or "put this on stage":

1. Commit your work and push your branch as usual.
2. Point `staging` at it. `staging` only marks what's on stage, so overwriting it is expected:
   ```bash
   git push --force origin HEAD:staging
   ```
3. Tell the user it's deploying and takes a few minutes. If `gh` works, follow it with `gh run watch` (or `gh run list --workflow deploy-stage.yml`) and report green or red; on red, `gh run view --log-failed` shows why.

If pushing to `staging` is refused (some cloud sessions may only push their own branches), don't work around it: tell the user to open the repo's **Actions** tab → **Deploy to stage** → **Run workflow**, choose your branch, and press **Run workflow**.

Never run `hosting/provision.sh` or `hosting/deploy.sh` without `--env hosting/.env.stage`: without it they target production. Setting up or repairing stage: [`docs/stage-server.md`](docs/stage-server.md).
