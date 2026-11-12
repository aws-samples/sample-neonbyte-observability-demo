#!/usr/bin/env bash
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

# Compile every hand-written requirements .in into a hash-pinned lock. Images and local setup
# install only the locks, so builds are reproducible and scanners see exactly what ships.
#
#   deploy/scripts/lock.sh                                   # re-lock everything
#   LOCK_DATE=2026-12-01T00:00:00Z deploy/scripts/lock.sh    # move the agent stack forward deliberately
#
# Agent images are resolved "as of" LOCK_DATE: unpinned rebuilds once pulled a new OpenTelemetry/ADOT
# stack, so agent upgrades are explicit (bump, redeploy, verify GenAI traces). Services and the
# traffic generator resolve current releases, with CVE floors in their .in files.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LOCK_DATE="${LOCK_DATE:-2026-11-12T00:00:00Z}"  # bumped from 2026-10-30 for CVE fixes (traces verified after bump)
UV="${UV:-uv}"
IMAGE=(--python-version 3.13 --python-platform aarch64-unknown-linux-gnu)   # Graviton containers
cd "$ROOT"

lock() { local in="$1" out="$2"; shift 2
  "$UV" pip compile --quiet --generate-hashes "$@" "$in" -o "$out"
  echo "  $out ($(grep -c '==' "$out") packages)"
}

echo "Agent images (as of $LOCK_DATE):"
for agent in orchestrator advisor orderdesk support concierge; do
  lock "agents/deploy/requirements.$agent.in" "agents/deploy/requirements.$agent.lock" --exclude-newer "$LOCK_DATE" "${IMAGE[@]}"
done
echo "Service and traffic images:"
lock services/requirements.in services/requirements.txt "${IMAGE[@]}"
lock traffic/requirements.in traffic/requirements.txt "${IMAGE[@]}"
echo "Local, any OS (agents as of $LOCK_DATE + services):"
lock agents/requirements.in agents/requirements.txt --universal --python-version 3.12 --exclude-newer "$LOCK_DATE"
lock local/requirements.in local/requirements.txt --universal --python-version 3.12 --exclude-newer "$LOCK_DATE"
