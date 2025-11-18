#!/bin/bash
# scripts/preflight_check.sh

set -e

echo "🔍 Running preflight checks..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check dependencies
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 installed"
        return 0
    else
        echo -e "${RED}✗${NC} $1 not found"
        return 1
    fi
}

# Required tools
MISSING=0
echo "Checking required tools..."
check_command "docker" || MISSING=1
check_command "supabase" || MISSING=1
check_command "pnpm" || MISSING=1
check_command "uv" || MISSING=1
check_command "just" || MISSING=1

if [ $MISSING -eq 1 ]; then
    echo ""
    echo -e "${YELLOW}Missing dependencies. Install with:${NC}"
    echo "  brew install docker supabase/tap/supabase just"
    echo "  curl -fsSL https://get.pnpm.io/install.sh | sh -"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check ports
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠${NC}  Port $1 in use"
        return 1
    else
        echo -e "${GREEN}✓${NC} Port $1 available"
        return 0
    fi
}

echo ""
echo "Checking ports..."
check_port 54322  # Supabase Postgres
check_port 54323  # Supabase Studio
check_port 5678   # n8n
check_port 6379   # Redis
check_port 8000   # FastAPI
check_port 3000   # Next.js
check_port 3001   # Langfuse

# Check system resources
echo ""
echo "Checking system resources..."

# Check RAM (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    TOTAL_RAM=$(sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)}')
    if [ $TOTAL_RAM -lt 8 ]; then
        echo -e "${YELLOW}⚠${NC}  Low RAM detected (< 8GB). System may be slow."
    else
        echo -e "${GREEN}✓${NC} RAM: ${TOTAL_RAM}GB"
    fi
fi

# Check disk space
AVAILABLE_DISK=$(df -h . | awk 'NR==2 {print $4}' | sed 's/[^0-9]//g')
if [ -z "$AVAILABLE_DISK" ] || [ "$AVAILABLE_DISK" -lt 10 ]; then
    echo -e "${YELLOW}⚠${NC}  Low disk space detected (< 10GB available)"
else
    echo -e "${GREEN}✓${NC} Disk space adequate"
fi

# Check API keys
echo ""
echo "Checking environment variables..."
if [ -f .env.local ]; then
    source .env.local
    if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your_google_api_key_here" ]; then
        echo -e "${RED}✗${NC} GOOGLE_API_KEY not set in .env.local"
    else
        echo -e "${GREEN}✓${NC} GOOGLE_API_KEY configured"
    fi
    
    if [ -z "$LANGFUSE_PUBLIC_KEY" ] || [ "$LANGFUSE_PUBLIC_KEY" = "your_langfuse_public_key_here" ]; then
        echo -e "${YELLOW}⚠${NC}  LANGFUSE_PUBLIC_KEY not set (optional)"
    else
        echo -e "${GREEN}✓${NC} LANGFUSE_PUBLIC_KEY configured"
    fi
else
    echo -e "${YELLOW}⚠${NC}  .env.local not found. Copying from .env.example"
    if [ -f .env.example ]; then
        cp .env.example .env.local
        echo -e "${YELLOW}→${NC} Please update .env.local with your API keys"
    else
        echo -e "${RED}✗${NC} .env.example not found. Please create it first."
    fi
fi

echo ""
echo -e "${GREEN}✅ Preflight checks complete!${NC}"

