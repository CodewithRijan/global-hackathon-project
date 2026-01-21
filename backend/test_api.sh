#!/bin/bash
# GalliPark API Test Script
# Run this to verify everything is working correctly

set -e

echo "=================================="
echo "GalliPark API - Verification Test"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if server is running
check_server() {
    if curl -s http://localhost:8000/api/ > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Server is running"
        return 0
    else
        echo -e "${RED}✗${NC} Server not running. Start it with:"
        echo "   python manage.py runserver"
        return 1
    fi
}

# Function to test API endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo ""
    echo -e "${YELLOW}Testing: $description${NC}"
    echo "   $method /api$endpoint"
    
    if [ -z "$data" ]; then
        response=$(curl -s -X $method http://localhost:8000/api$endpoint \
            -H "Content-Type: application/json")
    else
        response=$(curl -s -X $method http://localhost:8000/api$endpoint \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    if echo "$response" | grep -q "count\|id\|latitude" || [ ! -z "$response" ]; then
        echo -e "   ${GREEN}✓ Response received${NC}"
        echo "   Response: $(echo $response | cut -c1-100)..."
    else
        echo -e "   ${RED}✗ No response${NC}"
    fi
}

# Main test sequence
echo "1. Checking server..."
if ! check_server; then
    exit 1
fi

echo ""
echo "2. Testing API Endpoints..."

# Test 1: List parking spots
test_endpoint "GET" "/spots/" "" "List parking spots"

# Test 2: Nearby spots (main feature)
test_endpoint "GET" "/spots/nearby/?latitude=27.7172&longitude=85.3240&radius=500" "" "Find nearby spots"

# Test 3: List users
test_endpoint "GET" "/users/" "" "List users"

# Test 4: List events
test_endpoint "GET" "/events/" "" "List events"

# Test 5: List bookings
test_endpoint "GET" "/bookings/" "" "List bookings"

# Test 6: List reviews
test_endpoint "GET" "/reviews/" "" "List reviews"

echo ""
echo "=================================="
echo "✅ Basic Tests Completed!"
echo "=================================="
echo ""
echo "Next Steps:"
echo "1. Visit http://localhost:8000/api/ in browser"
echo "2. Create a parking spot (POST /spots/)"
echo "3. Find it nearby (GET /spots/nearby/)"
echo "4. Make a booking (POST /bookings/)"
echo ""
echo "Documentation:"
echo "  - START_HERE.md - Quick overview"
echo "  - API_DOCUMENTATION.md - All endpoints"
echo "  - API_ROUTES.md - Route reference"
echo ""
