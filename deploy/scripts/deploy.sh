#!/bin/bash
# Detect deployment entry points and run guarded direct deploys.
set -euo pipefail

PROJECT_NAME=$(basename "$PWD")
COMMAND="${1:-auto}"

PRIMARY_ENTRY="unknown"
PRIMARY_REASON=""
BRANCH_NAME="N/A"
REMOTE_NAME="N/A"
WORKTREE_STATE="not-git"

WORKFLOW_FILES=()
WORKFLOW_CANDIDATES=()
DIRECT_SIGNALS=()
PRIMARY_EVIDENCE=()
RISK_FLAGS=()
FALLBACK_PATHS=()

usage() {
    cat <<'EOF'
Usage:
  deploy.sh detect
  deploy.sh --detect-only
  deploy.sh auto
  deploy.sh deploy <cloudflare|cloudrun|docker|gce>

Behavior:
  detect / --detect-only  Print the deployment entry decision and evidence.
  auto                    Direct deploy only when GitHub Actions is not the primary entry.
  deploy <target>         Run a direct deployment intentionally.

Legacy compatibility:
  deploy.sh <target>      Equivalent to: deploy.sh deploy <target>
EOF
}

log() {
    printf '[INFO] %s\n' "$1"
}

warn() {
    printf '[WARN] %s\n' "$1" >&2
}

fail() {
    printf '[ERROR] %s\n' "$1" >&2
    exit 1
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

add_unique() {
    local array_name="$1"
    local value="$2"
    local existing

    eval "existing=(\"\${${array_name}[@]:-}\")"
    for item in "${existing[@]}"; do
        if [ "$item" = "$value" ]; then
            return 0
        fi
    done

    eval "${array_name}+=(\"\$value\")"
}

print_array() {
    local prefix="$1"
    local array_name="$2"
    local values=()

    eval "values=(\"\${${array_name}[@]-}\")"

    if [ "${#values[@]}" -eq 0 ] || [ -z "${values[0]}" ]; then
        printf '%s none\n' "$prefix"
        return
    fi

    printf '%s\n' "${values[@]}" | awk 'NF && !seen[$0]++ { print "'"$prefix"' " $0 }'
}

collect_repo_state() {
    if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        WORKTREE_STATE="clean"
        BRANCH_NAME=$(git branch --show-current 2>/dev/null || true)
        [ -n "$BRANCH_NAME" ] || BRANCH_NAME="HEAD"
        REMOTE_NAME=$(git remote get-url origin 2>/dev/null || printf 'none')

        if [ -n "$(git status --short 2>/dev/null)" ]; then
            WORKTREE_STATE="dirty"
            add_unique RISK_FLAGS "working tree is dirty"
        fi

        if [ "$REMOTE_NAME" = "none" ]; then
            add_unique RISK_FLAGS "origin remote is missing"
        fi
    else
        add_unique RISK_FLAGS "not inside a git repository"
    fi
}

collect_workflow_files() {
    if [ -d ".github/workflows" ]; then
        while IFS= read -r file; do
            WORKFLOW_FILES+=("$file")
        done < <(find .github/workflows -maxdepth 1 -type f \( -name '*.yml' -o -name '*.yaml' \) | sort)
    fi
}

file_contains_pattern() {
    local pattern="$1"
    shift
    local file

    for file in "$@"; do
        if [ -f "$file" ] && grep -Eiq "$pattern" "$file"; then
            return 0
        fi
    done

    return 1
}

collect_workflow_signals() {
    local workflow

    collect_workflow_files

    if [ "${#WORKFLOW_FILES[@]}" -eq 0 ]; then
        return
    fi

    for workflow in "${WORKFLOW_FILES[@]}"; do
        if grep -Eiq '(deploy|release|publish|production|workflow_dispatch|wrangler|cloudflare|gcloud|cloud run|app engine|docker buildx|docker push|artifact registry|gcr\.io|pkg\.dev)' "$workflow"; then
            add_unique WORKFLOW_CANDIDATES "$workflow"
            add_unique PRIMARY_EVIDENCE "workflow: $workflow"

            if grep -Eiq '(wrangler|cloudflare)' "$workflow"; then
                add_unique FALLBACK_PATHS "cloudflare"
            fi

            if grep -Eiq '(gcloud|cloud run|app engine|cloudbuild)' "$workflow"; then
                add_unique FALLBACK_PATHS "cloudrun"
            fi

            if grep -Eiq '(docker buildx|docker push|artifact registry|gcr\.io|pkg\.dev)' "$workflow"; then
                add_unique FALLBACK_PATHS "docker"
            fi
        fi
    done
}

collect_direct_signals() {
    if [ -f "wrangler.toml" ]; then
        add_unique DIRECT_SIGNALS "cloudflare"
        add_unique PRIMARY_EVIDENCE "file: wrangler.toml"
    fi

    if [ -f "wrangler.json" ]; then
        add_unique DIRECT_SIGNALS "cloudflare"
        add_unique PRIMARY_EVIDENCE "file: wrangler.json"
    fi

    if [ -f "wrangler.jsonc" ]; then
        add_unique DIRECT_SIGNALS "cloudflare"
        add_unique PRIMARY_EVIDENCE "file: wrangler.jsonc"
    fi

    if [ -f "cloudbuild.yaml" ]; then
        add_unique DIRECT_SIGNALS "cloudrun"
        add_unique PRIMARY_EVIDENCE "file: cloudbuild.yaml"
    fi

    if [ -f "app.yaml" ]; then
        add_unique DIRECT_SIGNALS "cloudrun"
        add_unique PRIMARY_EVIDENCE "file: app.yaml"
    fi

    if [ -f "Dockerfile" ]; then
        add_unique DIRECT_SIGNALS "docker"
        add_unique PRIMARY_EVIDENCE "file: Dockerfile"
    fi

    if file_contains_pattern '"(deploy|release|publish)"[[:space:]]*:' "package.json"; then
        add_unique PRIMARY_EVIDENCE "package.json: deploy or release script"
    fi

    if file_contains_pattern 'wrangler|cloudflare' "package.json" "Makefile" "justfile"; then
        add_unique DIRECT_SIGNALS "cloudflare"
        add_unique PRIMARY_EVIDENCE "script: wrangler or cloudflare command"
    fi

    if file_contains_pattern 'gcloud|cloud run|app deploy' "package.json" "Makefile" "justfile" "service.yaml"; then
        add_unique DIRECT_SIGNALS "cloudrun"
        add_unique PRIMARY_EVIDENCE "script: gcloud or Cloud Run command"
    fi

    if file_contains_pattern 'docker (build|push)|docker buildx|artifact registry|gcr\.io|pkg\.dev' "package.json" "Makefile" "justfile"; then
        add_unique DIRECT_SIGNALS "docker"
        add_unique PRIMARY_EVIDENCE "script: docker build or push command"
    fi
}

decide_primary_entry() {
    collect_repo_state
    collect_workflow_signals
    collect_direct_signals

    if [ "${#WORKFLOW_CANDIDATES[@]}" -gt 0 ]; then
        PRIMARY_ENTRY="github-actions"
        PRIMARY_REASON="workflow evidence indicates that GitHub Actions is the deployment entry point"
        return
    fi

    local has_cloudflare=0
    local has_cloudrun=0
    local has_docker=0
    local signal

    if [ "${#DIRECT_SIGNALS[@]}" -gt 0 ]; then
        for signal in "${DIRECT_SIGNALS[@]}"; do
            case "$signal" in
                cloudflare) has_cloudflare=1 ;;
                cloudrun) has_cloudrun=1 ;;
                docker) has_docker=1 ;;
            esac
        done
    fi

    if [ "$has_cloudflare" -eq 1 ] && [ "$has_cloudrun" -eq 1 ]; then
        PRIMARY_ENTRY="ambiguous"
        PRIMARY_REASON="conflicting Cloudflare and GCP deployment signals were found"
        add_unique RISK_FLAGS "multiple direct deployment targets conflict"
        return
    fi

    if [ "$has_cloudflare" -eq 1 ] && [ "$has_docker" -eq 1 ]; then
        PRIMARY_ENTRY="ambiguous"
        PRIMARY_REASON="Cloudflare and Docker signals both exist without workflow guidance"
        add_unique RISK_FLAGS "multiple direct deployment targets conflict"
        return
    fi

    if [ "$has_cloudflare" -eq 1 ]; then
        PRIMARY_ENTRY="cloudflare"
        PRIMARY_REASON="Cloudflare configuration is the strongest direct deployment signal"
        return
    fi

    if [ "$has_cloudrun" -eq 1 ]; then
        PRIMARY_ENTRY="cloudrun"
        PRIMARY_REASON="GCP deployment configuration is the strongest direct deployment signal"
        if [ "$has_docker" -eq 1 ]; then
            add_unique FALLBACK_PATHS "docker"
        fi
        return
    fi

    if [ "$has_docker" -eq 1 ]; then
        PRIMARY_ENTRY="docker"
        PRIMARY_REASON="container build and registry signals exist without a stronger deployment path"
        return
    fi

    PRIMARY_ENTRY="unknown"
    PRIMARY_REASON="no recognizable deployment entry point was found"
    add_unique RISK_FLAGS "deployment entry point is unknown"
}

print_decision_report() {
    echo "Deployment Entry Decision"
    echo "  project: ${PROJECT_NAME}"
    echo "  git_branch: ${BRANCH_NAME}"
    echo "  origin_remote: ${REMOTE_NAME}"
    echo "  worktree_state: ${WORKTREE_STATE}"
    echo "  primary_entry: ${PRIMARY_ENTRY}"
    echo "  reason: ${PRIMARY_REASON}"

    echo "  workflow_files:"
    print_array "   - " WORKFLOW_FILES

    echo "  workflow_candidates:"
    print_array "   - " WORKFLOW_CANDIDATES

    echo "  evidence:"
    print_array "   - " PRIMARY_EVIDENCE

    echo "  fallback_paths:"
    print_array "   - " FALLBACK_PATHS

    echo "  risks:"
    print_array "   - " RISK_FLAGS
}

require_npx() {
    command_exists npx || fail "npx is required for Cloudflare deployment"
}

require_gcloud_auth() {
    command_exists gcloud || fail "gcloud is required for GCP deployment"

    local active_account
    active_account=$(gcloud auth list --filter=status:ACTIVE --format='value(account)' 2>/dev/null | head -n 1 || true)
    [ -n "$active_account" ] || fail "No active gcloud account found. Run 'gcloud auth login' first."
}

require_docker_access() {
    command_exists docker || fail "docker is required for container deployment"
    docker info >/dev/null 2>&1 || fail "docker daemon is not available"

    local docker_config
    docker_config="${DOCKER_CONFIG:-$HOME/.docker}/config.json"
    [ -f "$docker_config" ] || fail "Docker config not found at ${docker_config}. Run 'docker login' first."

    if [ -n "${DOCKER_REGISTRY:-}" ] && [ "${DOCKER_REGISTRY}" != "docker.io" ]; then
        grep -Fq "${DOCKER_REGISTRY}" "$docker_config" || fail "Registry ${DOCKER_REGISTRY} is not present in ${docker_config}"
    fi
}

deploy_docker() {
    require_docker_access

    local image_name
    image_name="${DOCKER_REGISTRY:-docker.io}/${PROJECT_NAME}:${TAG:-latest}"

    log "Building container image ${image_name}"
    docker build -t "$image_name" .

    log "Pushing container image ${image_name}"
    docker push "$image_name"

    echo "Docker deployment completed"
    echo "  image: ${image_name}"
}

deploy_cloudrun() {
    require_gcloud_auth

    log "Deploying ${PROJECT_NAME} to Cloud Run"
    gcloud run deploy "$PROJECT_NAME" \
        --source . \
        --region "${REGION:-asia-east1}" \
        --allow-unauthenticated \
        --quiet

    echo "Cloud Run deployment completed"
    echo "  service: ${PROJECT_NAME}"
    echo "  region: ${REGION:-asia-east1}"
}

deploy_cloudflare() {
    require_npx

    log "Checking Wrangler authentication"
    npx wrangler whoami >/dev/null

    log "Deploying ${PROJECT_NAME} with Wrangler"
    npx wrangler deploy

    echo "Cloudflare deployment completed"
    echo "  project: ${PROJECT_NAME}"
}

deploy_gce() {
    require_gcloud_auth
    require_docker_access

    local image_name
    image_name="${DOCKER_REGISTRY:-docker.io}/${PROJECT_NAME}:${TAG:-latest}"

    log "Building container image ${image_name}"
    docker build -t "$image_name" .

    log "Pushing container image ${image_name}"
    docker push "$image_name"

    log "Updating GCE instance ${PROJECT_NAME}"
    gcloud compute instances update-container "$PROJECT_NAME" \
        --container-image "$image_name" \
        --zone "${ZONE:-asia-east1-b}"

    echo "GCE deployment completed"
    echo "  instance: ${PROJECT_NAME}"
    echo "  zone: ${ZONE:-asia-east1-b}"
}

run_direct_deploy() {
    local target="$1"

    case "$target" in
        cloudflare) deploy_cloudflare ;;
        cloudrun) deploy_cloudrun ;;
        docker) deploy_docker ;;
        gce) deploy_gce ;;
        *) fail "Unknown direct deployment target: ${target}" ;;
    esac
}

handle_auto() {
    decide_primary_entry
    print_decision_report

    case "$PRIMARY_ENTRY" in
        github-actions)
            fail "Primary deployment entry is GitHub Actions. Review changes, commit, and push instead of bypassing CI."
            ;;
        cloudflare|cloudrun|docker)
            run_direct_deploy "$PRIMARY_ENTRY"
            ;;
        ambiguous)
            fail "Deployment entry is ambiguous. Confirm the target with the user before deploying."
            ;;
        *)
            fail "Cannot auto-deploy because no deployment entry point was detected."
            ;;
    esac
}

main() {
    case "$COMMAND" in
        detect|--detect-only)
            decide_primary_entry
            print_decision_report
            ;;
        auto)
            handle_auto
            ;;
        deploy)
            [ "${2:-}" ] || fail "Missing target. Use: deploy.sh deploy <cloudflare|cloudrun|docker|gce>"
            decide_primary_entry
            print_decision_report
            if [ "$PRIMARY_ENTRY" = "github-actions" ]; then
                warn "Bypassing the detected GitHub Actions deployment entry because an explicit direct target was requested."
            fi
            run_direct_deploy "$2"
            ;;
        cloudflare|cloudrun|docker|gce)
            warn "Legacy target-only invocation detected. Prefer 'deploy.sh deploy $COMMAND'."
            decide_primary_entry
            print_decision_report
            run_direct_deploy "$COMMAND"
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

main "$@"
