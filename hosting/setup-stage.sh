#!/usr/bin/env bash
# setup-stage.sh: put this project on a stage server and deploy it on every push to the stage
# branch (.github/workflows/deploy-stage.yml). Guide: docs/stage-server.md
#
#   ./hosting/setup-stage.sh https://stage.example.com     the first time: writes hosting/.env.stage
#   ./hosting/setup-stage.sh                               after that (reads hosting/.env.stage)
#
# Options: --user NAME   your admin user on the server (default: your Mac user name, $USER)
#
# It checks what it needs first and stops with exactly what to do when something is missing; fix
# that and run it again. Every step is safe to repeat. With everything in place it:
#   provisions the server (hosting/provision.sh), adds the server's read-only deploy key to GitHub,
#   deploys, installs the key GitHub Actions deploys with (as the STAGE_SSH_KEY secret), and creates
#   your admin account on the site.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=hosting/provision.sh
. "$HERE/provision.sh"

ENV_FILE="$HERE/.env.stage"
ENV_REL=hosting/.env.stage
WORKFLOW=.github/workflows/deploy-stage.yml
URL="" ADMIN_USER=$(id -un)
while [ $# -gt 0 ]; do
  case $1 in
    --user) ADMIN_USER=${2:?--user needs a name}; shift 2 ;;
    -h|--help) sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) die "unknown option: $1 (see ./hosting/setup-stage.sh --help)" ;;
    *) URL=$1; shift ;;
  esac
done
cd "$HERE/.."

stop() { # stop "what's wrong" "what to do" ...: explain the manual step, then exit
  local line
  printf '\n✗ %s\n\nTo do:\n' "$1" >&2; shift
  for line in "$@"; do printf '  %s\n' "$line" >&2; done
  printf '\nThen run ./hosting/setup-stage.sh again.\n' >&2
  exit 1
}
step() { printf '\n== %s\n' "$*"; }
get() { envfile_get "$1" "$ENV_FILE"; }
remote() { ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 "$HOST" "$@"; }

# ---------------------------------------------------------------- settings
step "Settings ($ENV_REL)"
if [ -n "$URL" ]; then
  domain=$(printf '%s' "$URL" | sed -e 's|^https\{0,1\}://||' -e 's|/.*$||' | tr 'A-Z' 'a-z')
  [[ $domain =~ $RE_DOMAIN ]] || die "'$URL' is not a web address like https://stage.example.com"
  if [ -f "$ENV_FILE" ]; then
    [ "$(get DEPLOY_DOMAIN)" = "$domain" ] ||
      die "$ENV_REL is for $(get DEPLOY_DOMAIN), not $domain. Edit or delete it, then run this again."
  else
    email=$(local_default_for EMAIL)
    [ -n "$email" ] || stop "git has no email address (Let's Encrypt sends certificate notices to it)" \
      "git config --global user.email you@example.com"
    repo=$(local_default_for REPO)
    [ "$repo" != none ] || stop "this repo has no 'origin' remote with an SSH URL for the server to deploy from" \
      "git remote add origin git@github.com:OWNER/REPO.git   (or: git remote set-url origin ...)"
    cat > "$ENV_FILE" <<EOF
# The stage server. Committed: GitHub Actions reads DEPLOY_HOST and STAGE_HOST_KEY from it.
# Written by hosting/setup-stage.sh; see hosting/.env.example for every setting.
DEPLOY_HOST=$ADMIN_USER@$domain
DEPLOY_NAME=$(local_default_for NAME)
DEPLOY_DOMAIN=$domain
DEPLOY_EMAIL=$email
DEPLOY_DB=postgres
DEPLOY_REPO=$repo
DEPLOY_BRANCH=staging
EOF
    say "wrote $ENV_REL"
  fi
fi
[ -f "$ENV_FILE" ] || die "no $ENV_REL yet: run ./hosting/setup-stage.sh https://YOUR-STAGE-DOMAIN"
HOST=$(get DEPLOY_HOST) NAME=$(get DEPLOY_NAME) DOMAIN=$(get DEPLOY_DOMAIN)
REPO=$(get DEPLOY_REPO) BRANCH=$(get DEPLOY_BRANCH)
BRANCH=${BRANCH:-staging}
[ -n "$REPO" ] && [ "$REPO" != none ] || die "DEPLOY_REPO in $ENV_REL must be the git URL the server deploys from (stage deploys from git)"
SERVER=${HOST#*@}
say "server $HOST, site https://$DOMAIN, app $NAME, deploys branch $BRANCH"

ON_GITHUB=0
if [ "$(repo_host)" = github.com ]; then ON_GITHUB=1; GH_REPO=$(repo_path); GH_REPO=${GH_REPO%.git}; fi

# ---------------------------------------------------------------- checks
step "Checks"
if [ $ON_GITHUB = 1 ]; then
  command -v gh >/dev/null || stop "the GitHub CLI (gh) is not installed" "brew install gh" "gh auth login"
  gh auth status >/dev/null 2>&1 || stop "the GitHub CLI is not logged in (it adds the deploy key and the Actions secret)" \
    "gh auth login      (choose GitHub.com, then log in with a web browser)"
  perm=$(gh repo view "$GH_REPO" --json viewerPermission -q .viewerPermission 2>/dev/null || true)
  [ "$perm" = ADMIN ] || stop "your GitHub login can't manage $GH_REPO (needs admin: it adds a deploy key and a secret)" \
    "gh auth status     (check which account is logged in; switch with gh auth switch)"
  say "gh is logged in and can manage $GH_REPO"
fi

if ! remote true 2>/dev/null; then
  ip=$(dig +short A "$SERVER" 2>/dev/null | tail -n 1 || true)
  if [[ $SERVER =~ ^[0-9.]+$ ]] || [ -n "$ip" ]; then
    stop "can't log in to $HOST with your SSH key" \
      "If the server is new, set it up with vpshome (README: \"New server\"):" \
      "  cd ~/dev/common/vpshome && ./init-server.sh root@$SERVER --stage --user $ADMIN_USER" \
      "Otherwise see what ssh says: ssh -v $HOST"
  else
    stop "$SERVER doesn't resolve to an address" \
      "At your DNS provider, add an A record: $SERVER -> the server's IP address." \
      "Check it with: dig +short $SERVER   (it should print the IP; new records can take a few minutes)"
  fi
fi
say "$HOST logs in"
remote 'sudo -n true' 2>/dev/null || stop "sudo on $SERVER asks for a password, so this script (and an agent) can't run it" \
  "Set the server up as a stage box with vpshome (it re-runs safely):" \
  "  cd ~/dev/common/vpshome && ./init-server.sh root@$SERVER --stage --user $ADMIN_USER" \
  "  (if root login is already off, run it anyway: it carries on as $ADMIN_USER and asks for your sudo password)"
say "sudo works without a password"

# ---------------------------------------------------------------- server
step "Provision (hosting/provision.sh)"
"$HERE/provision.sh" --env "$ENV_FILE" -y

step "Deploy key"
alias_url="$(repo_user)@deploy-$NAME:$(repo_path)"
if remote "timeout 20 git ls-remote '$alias_url' HEAD" >/dev/null 2>&1; then
  say "the server can read $REPO"
elif [ $ON_GITHUB = 1 ]; then
  pub=$(remote "cat ~/.ssh/deploy_$NAME.pub")
  printf '%s\n' "$pub" | gh repo deploy-key add - --repo "$GH_REPO" --title "$NAME on $SERVER (read-only)" >/dev/null
  remote "timeout 20 git ls-remote '$alias_url' HEAD" >/dev/null 2>&1 ||
    die "added the deploy key to $GH_REPO, but the server still can't read it: ssh $HOST 'git ls-remote $alias_url'"
  say "added the server's read-only deploy key to $GH_REPO"
else
  stop "the server's deploy key can't read $REPO" \
    "Let this key read the repo (read-only): $(remote "cat ~/.ssh/deploy_$NAME.pub")"
fi

step "Server host key"
hostkey=$(remote 'cat /etc/ssh/ssh_host_ed25519_key.pub' | awk '{print $1, $2}')
[ -n "$hostkey" ] || die "couldn't read the server's host key"
if [ "$(get STAGE_HOST_KEY)" != "$hostkey" ]; then
  tmp=$(mktemp)
  grep -v '^STAGE_HOST_KEY=' "$ENV_FILE" > "$tmp" || true
  printf 'STAGE_HOST_KEY=%s\n' "$hostkey" >> "$tmp"
  cat "$tmp" > "$ENV_FILE"; rm -f "$tmp"
  say "saved in $ENV_REL (GitHub Actions checks the server against it)"
else
  say "already in $ENV_REL"
fi

# ---------------------------------------------------------------- GitHub Actions key
if [ $ON_GITHUB = 1 ]; then
  step "GitHub Actions deploy key"
  tag="ci-deploy-$NAME"
  if remote "grep -q ' $tag\$' ~/.ssh/authorized_keys" && gh secret list --repo "$GH_REPO" | grep -q '^STAGE_SSH_KEY[[:space:]]'; then
    say "installed on the server and saved as the STAGE_SSH_KEY secret"
  else
    tmpd=$(mktemp -d)
    ssh-keygen -q -t ed25519 -N '' -C "$tag" -f "$tmpd/key"
    pub=$(cut -d' ' -f1,2 "$tmpd/key.pub")
    # replace this app's earlier CI key (lines ending in the tag), keep every other key
    remote "set -e; f=~/.ssh/authorized_keys; touch \$f; chmod 600 \$f
      { grep -v ' $tag\$' \$f || true; printf '%s\n' 'restrict,command=\"/srv/$NAME/bin/ci-deploy\" $pub $tag'; } > \$f.new
      mv \$f.new \$f"
    gh secret set STAGE_SSH_KEY --repo "$GH_REPO" < "$tmpd/key"
    rm -rf "$tmpd"
    say "new key: it can only run /srv/$NAME/bin/ci-deploy; private half saved as the STAGE_SSH_KEY secret"
  fi
fi

# ---------------------------------------------------------------- the stage branch
step "The $BRANCH branch"
if [ $ON_GITHUB = 1 ]; then
  missing=()
  if git fetch -q origin "$BRANCH" 2>/dev/null; then
    git cat-file -e "FETCH_HEAD:$WORKFLOW" 2>/dev/null || missing+=("$WORKFLOW")
    [ "$(git show "FETCH_HEAD:$ENV_REL" 2>/dev/null | sed -n 's/^STAGE_HOST_KEY=//p')" = "$hostkey" ] || missing+=("$ENV_REL")
  else
    missing=("$WORKFLOW" "$ENV_REL")
  fi
  if [ ${#missing[@]} -gt 0 ]; then
    stop "the $BRANCH branch on GitHub needs ${missing[*]} (the deploy workflow reads both)" \
      "git add $WORKFLOW $ENV_REL" \
      "git commit -m 'Deploy to stage on push'" \
      "git push origin HEAD:$BRANCH" \
      "The push to $BRANCH also starts a deploy: watch it in the repo's Actions tab, or with gh run watch."
  fi
  say "$WORKFLOW and $ENV_REL are on $BRANCH"
else
  remote "timeout 20 git ls-remote --exit-code '$alias_url' 'refs/heads/$BRANCH'" >/dev/null 2>&1 ||
    stop "there's no '$BRANCH' branch in $REPO yet (stage deploys it)" \
      "git push origin main:$BRANCH      (or whichever branch should go on stage first)"
  say "$BRANCH exists"
fi

step "First deploy"
if remote "test -f /srv/$NAME/REVISION"; then
  say "already deployed: $(remote "cut -c1-12 /srv/$NAME/REVISION") (pushes to $BRANCH deploy from now on)"
else
  "$HERE/deploy.sh" --env "$ENV_FILE" "$BRANCH" ||
    die "the first deploy failed (above). If it says another deploy is running, GitHub Actions is deploying: wait for it, then run this again"
fi

# ---------------------------------------------------------------- admin account
step "Admin account"
users=$(remote "sudo -u $NAME /srv/$NAME/bin/manage shell -c 'from django.contrib.auth import get_user_model as g; print(g().objects.count())' 2>/dev/null | tail -n 1" || true)
if [ "$users" = 0 ]; then
  email=$(git config user.email || true) name=$(git config user.name || true)
  password=$(openssl rand -base64 18 | tr -d '/+=' | cut -c1-20)
  printf '%s\n' "$password" | remote "sudo -u $NAME /srv/$NAME/bin/manage add_user $(printf '%q' "$email") --name $(printf '%q' "${name:-Admin}") --admin --password-stdin" >/dev/null
  say "created $email with password: $password"
  say "(shown only once: save it in your password manager now)"
else
  say "${users:-some} account(s) already exist"
fi

admin=$(remote "sed -n 's/^ADMIN_URL=//p' /srv/$NAME/.env" | tail -n 1)
how="./hosting/deploy.sh --env $ENV_REL"
[ $ON_GITHUB = 0 ] || how="push to $BRANCH (GitHub: Actions tab, \"Deploy to stage\"), or $how"
cat <<EOF

Stage is ready: https://$DOMAIN/
  Django admin:  https://$DOMAIN/$admin (opens after a passkey sign-in)
  Deploy:        $how
  What's live:   ssh $HOST cat /srv/$NAME/REVISION
EOF
