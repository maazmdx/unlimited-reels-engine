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
echo "======================================================================"

echo ""
echo "Choose your primary automation runner:"
echo "  [1] GitHub Actions Cloud Runner (Recommended: 100% Free, Zero Local Machine Downtime)"
echo "  [2] Local Linux System Cron (Runs daily at 09:00 AM on this machine)"
echo "  [3] Test Single Pipeline Run Now"
echo ""

read -p "Select option (1-3): " opt

case "$opt" in
  1)
    echo ""
    echo "--- Option 1: GitHub Actions Cloud Runner ---"
    echo "1. Creating remote private GitHub repository 'maazmdx/unlimited-reels-engine'..."
    gh repo create maazmdx/unlimited-reels-engine --private --source=. --remote=origin --push || echo "Repository already linked or pushed."
    echo ""
    echo "✅ Cloud Automation Activated!"
    echo "Daily schedule: 06:00 UTC (11:30 AM IST) via .github/workflows/daily_ai_reel.yml"
    echo "To configure automated Google Drive upload on GitHub Actions:"
    echo "  Add 'GDRIVE_CREDENTIALS' and 'GDRIVE_FOLDER_ID' to your GitHub Repository Secrets."
    ;;

  2)
    echo ""
    echo "--- Option 2: Local Linux Machine Cron ---"
    CRON_CMD="0 9 * * * cd $SCRIPT_DIR && $SCRIPT_DIR/.venv/bin/python3 engine/master_orchestrator.py >> $SCRIPT_DIR/out/daily_cron.log 2>&1"
    (crontab -l 2>/dev/null | grep -v "master_orchestrator.py"; echo "$CRON_CMD") | crontab -
    echo "✅ Local cron scheduled for 09:00 AM daily."
    echo "Crontab entry: $CRON_CMD"
    ;;

  3)
    echo ""
    echo "--- Option 3: Manual Execution ---"
    "$SCRIPT_DIR/.venv/bin/python3" "$SCRIPT_DIR/engine/master_orchestrator.py"
    ;;

  *)
    echo "Invalid option. Exiting."
    exit 1
    ;;
esac
