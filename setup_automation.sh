#!/usr/bin/env bash
# ======================================================================
# Antigravity Daily Video Automation Setup
# Configures 100% automated daily video rendering and cloud dispatch.
# ======================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================================================"
echo "  🎬 ANTIGRAVITY DAILY VIDEO AUTOMATION SETUP"
echo "  Supports: Morning Batch (2-3 Daily Reels) | Instagram Recreation"
echo "======================================================================"

echo ""
echo "Choose your automation workflow:"
echo "  [1] Schedule Daily Morning Batch (2-3 videos every morning at 08:30 AM via Local Cron)"
echo "  [2] Run Morning Batch Immediately (Generates 2-3 reels into out/morning_YYYY_MM_DD/)"
echo "  [3] Recreate a Specific Instagram Reel / Video URL"
echo "  [4] Run Single Standard Daily Video Pipeline"
echo "  [5] Setup GitHub Actions Cloud Runner (06:00 UTC / 11:30 AM IST)"
echo ""

read -p "Select option (1-5): " opt

case "$opt" in
  1)
    echo ""
    echo "--- Option 1: Schedule Morning Batch via System Cron ---"
    "$SCRIPT_DIR/.venv/bin/python3" "$SCRIPT_DIR/engine/morning_batch_runner.py" --schedule --hour 8 --minute 30
    ;;

  2)
    echo ""
    echo "--- Option 2: Executing Morning Batch (2-3 Reels) ---"
    "$SCRIPT_DIR/.venv/bin/python3" "$SCRIPT_DIR/engine/morning_batch_runner.py" --count 3
    ;;

  3)
    echo ""
    read -p "Enter Instagram Reel / Video URL: " insta_url
    if [ -n "$insta_url" ]; then
      echo "--- Option 3: Ingesting & Recreating Reel ---"
      "$SCRIPT_DIR/.venv/bin/python3" "$SCRIPT_DIR/engine/master_orchestrator.py" --insta "$insta_url"
    else
      echo "No URL entered. Aborting."
    fi
    ;;

  4)
    echo ""
    echo "--- Option 4: Single Daily Video Pipeline ---"
    "$SCRIPT_DIR/.venv/bin/python3" "$SCRIPT_DIR/engine/master_orchestrator.py"
    ;;

  5)
    echo ""
    echo "--- Option 5: GitHub Actions Cloud Runner ---"
    gh repo create maazmdx/unlimited-reels-engine --private --source=. --remote=origin --push || echo "Repository already linked or pushed."
    echo "✅ Cloud Automation Activated via .github/workflows/daily_ai_reel.yml"
    ;;

  *)
    echo "Invalid option. Exiting."
    exit 1
    ;;
esac
