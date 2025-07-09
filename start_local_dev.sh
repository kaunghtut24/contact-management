#!/bin/bash

# Contact Management System - Local Development Setup
echo "🚀 Starting Contact Management System for Local Development"
echo "=========================================================="

# Set environment variables for local development
export DATABASE_URL="sqlite:///./contact_management_local.sqlite"
export JWT_SECRET_KEY="local-development-secret-key-32-characters-long"
export ADMIN_USERNAME="admin"
export ADMIN_EMAIL="admin@localhost.dev"
export ADMIN_PASSWORD="LocalAdmin123!"
export ENVIRONMENT="development"

echo "✅ Environment variables set:"
echo "   - Database: SQLite (local)"
echo "   - Admin Username: admin"
echo "   - Admin Password: LocalAdmin123!"
echo "   - Admin Email: admin@localhost.dev"
echo ""

# Start backend
echo "🔧 Starting backend API on http://localhost:8000"
cd backend
/home/yuthar/miniconda3/envs/contact-management/bin/python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Create admin user
echo "👤 Creating admin user..."
curl -X POST "http://localhost:8000/auth/create-admin" || echo "Admin user may already exist"

echo ""
echo "🎉 Local development environment ready!"
echo "========================================="
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Frontend: http://localhost:5173 (run 'npm run dev' in frontend folder)"
echo ""
echo "Admin Credentials:"
echo "  Username: admin"
echo "  Password: LocalAdmin123!"
echo ""
echo "Press Ctrl+C to stop the backend server"

# Wait for user to stop
wait $BACKEND_PID
