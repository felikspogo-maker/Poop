#!/bin/bash
set -e

echo "================================================"
echo "Production Database Migration Script"
echo "================================================"

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL environment variable is not set"
    exit 1
fi

echo "Database URL: ${DATABASE_URL%%:*}://****"

# Navigate to backend directory
cd "$(dirname "$0")/../backend"

echo ""
echo "Step 1: Generating Prisma Client..."
npx prisma generate

echo ""
echo "Step 2: Running database migrations..."
npx prisma migrate deploy

echo ""
echo "Step 3: Checking migration status..."
npx prisma migrate status

echo ""
echo "================================================"
echo "Migration completed successfully!"
echo "================================================"
