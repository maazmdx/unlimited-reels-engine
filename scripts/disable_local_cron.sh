#!/bin/bash
# ==============================================================================
# Safely Disable Local Laptop Morning Crontab for Unlimited Reels Engine
# Removes ONLY the morning_batch_runner.py job, keeping all other user cron jobs intact.
# ==============================================================================

set -euo pipefail

echo "🔍 Inspecting current user crontab..."
if ! crontab -l &>/dev/null; then
  echo "ℹ️ No crontab found for current user. Nothing to disable."
  exit 0
fi

# Create backup
BACKUP_FILE="/tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt"
crontab -l > "$BACKUP_FILE"
echo "💾 Backed up existing crontab to: $BACKUP_FILE"

# Check if morning_batch_runner exists in crontab
if crontab -l | grep -q "morning_batch_runner.py"; then
  echo "🧹 Removing 'morning_batch_runner.py' line from crontab..."
  crontab -l | grep -v "morning_batch_runner.py" | crontab -
  echo "✅ Unlimited Reels Engine cron job successfully removed!"
else
  echo "ℹ️ 'morning_batch_runner.py' was not found in crontab."
fi

echo ""
echo "📋 Active user crontab after update:"
crontab -l || echo "(crontab is empty)"
echo ""
echo "🎉 Laptop rendering is now fully disabled. GitHub Actions cloud runner will handle daily generations!"
