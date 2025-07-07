#!/bin/bash

# Contact Management System Setup Script

echo "🚀 Setting up Contact Management System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.9+ and try again."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 16+ and try again."
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    print_warning "PostgreSQL is not installed. You'll need to install it manually or use Docker."
fi

print_status "Setting up backend..."

# Create virtual environment
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Created Python virtual environment"
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
print_status "Installed Python dependencies"

# Create necessary directories
mkdir -p uploads logs
print_status "Created upload and log directories"

# Copy environment file
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_status "Created .env file from template"
    print_warning "Please update the .env file with your database credentials"
fi

cd ..

print_status "Setting up frontend..."

# Install Node.js dependencies
cd frontend
npm install
print_status "Installed Node.js dependencies"

cd ..

print_status "Setup completed successfully! 🎉"

echo ""
echo "Next steps:"
echo "1. Update backend/.env with your PostgreSQL database credentials"
echo "2. Create the PostgreSQL database 'contact_db'"
echo "3. Start the backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "4. Start the frontend: cd frontend && npm run dev"
echo ""
echo "Or use Docker Compose: docker-compose up -d"
echo ""
echo "Access the application at: http://localhost:5173"
echo "API documentation at: http://localhost:8000/docs"
