#!/bin/bash

echo "🔧 Setting up .env file..."
echo ""

# Check if .env already exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists"
    read -p "Do you want to overwrite it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted. Keeping existing .env file."
        exit 0
    fi
fi

# Create .env from example
cp .env.example .env

# Add the CoinGecko API key
echo "Adding CoinGecko API key to .env..."
sed -i '' 's/your_coingecko_api_key_here/CG-D8KTuE34nPVqfj2NfaDdgred/g' .env

echo ""
echo "✅ .env file created successfully!"
echo ""
echo "Configuration:"
echo "  MongoDB: mongodb://localhost:27017"
echo "  Database: vibewater_db"
echo "  CoinGecko API: ✓ Configured (Pro API)"
echo "  CORS Origins: http://localhost:3000"
echo ""
echo "You can now run:"
echo "  uv run test_vectorbt.py"
echo "  uv run uvicorn app.main:app --reload"
echo ""
