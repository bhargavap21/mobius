#!/bin/bash
# Script to replace hardcoded API URLs with config import

echo "Updating frontend files to use API_URL from config..."

# Files to update
files=(
  "frontend/frontend/src/App.jsx"
  "frontend/frontend/src/main.jsx"
  "frontend/frontend/src/context/AuthContext.jsx"
  "frontend/frontend/src/components/EmailConfirmation.jsx"
  "frontend/frontend/src/components/StrategySidebar.jsx"
  "frontend/frontend/src/components/BotLibrary.jsx"
  "frontend/frontend/src/components/ChatHistorySidebar.jsx"
  "frontend/frontend/src/components/DeploymentMonitor.jsx"
  "frontend/frontend/src/components/DeploymentPage.jsx"
  "frontend/frontend/src/components/AgentActivityLogWS.jsx"
  "frontend/frontend/src/pages/CommunityPage.jsx"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "Processing $file..."

    # Replace http://localhost:8000 with \${API_URL}
    sed -i.bak "s|'http://localhost:8000|'\${API_URL}|g" "$file"
    sed -i.bak 's|"http://localhost:8000|"${API_URL}|g' "$file"
    sed -i.bak 's|`http://localhost:8000|`${API_URL}|g' "$file"

    # Replace ws://localhost:8000 with \${WS_URL}
    sed -i.bak "s|'ws://localhost:8000|'\${WS_URL}|g" "$file"
    sed -i.bak 's|"ws://localhost:8000|"${WS_URL}|g' "$file"
    sed -i.bak 's|`ws://localhost:8000|`${WS_URL}|g' "$file"

    # Remove backup files
    rm -f "$file.bak"
  fi
done

echo "Done! Files updated to use config variables."
echo "Next: Add import { API_URL, WS_URL } from './config' or '../config' to each file"
