#!/bin/bash

# OCR Microservice Setup Script
# This script helps you set up and deploy the OCR microservice

set -e

echo "🚀 OCR Microservice Setup Script"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "ocr-service/app.py" ]; then
    print_error "Please run this script from the contact-management-system root directory"
    exit 1
fi

print_info "Setting up OCR microservice..."

# Step 1: Create OCR service repository
echo ""
echo "📁 Step 1: Preparing OCR service repository"
cd ocr-service

# Check if git is initialized
if [ ! -d ".git" ]; then
    print_info "Initializing git repository..."
    git init
    print_status "Git repository initialized"
else
    print_status "Git repository already exists"
fi

# Add files
git add .
git status

echo ""
read -p "🤔 Do you want to commit the OCR service files? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git commit -m "Initial OCR microservice with multi-LLM support" || print_warning "Nothing to commit or already committed"
    print_status "Files committed"
fi

# Step 2: GitHub repository setup
echo ""
echo "🐙 Step 2: GitHub repository setup"
print_info "You need to create a new GitHub repository for the OCR service"
print_info "1. Go to https://github.com/new"
print_info "2. Create a repository named: ocr-microservice"
print_info "3. Make it public or private (your choice)"
print_info "4. Don't initialize with README (we already have files)"

echo ""
read -p "📝 Enter your GitHub username: " github_username
read -p "📝 Enter your repository name (default: ocr-microservice): " repo_name
repo_name=${repo_name:-ocr-microservice}

# Add remote origin
git_url="https://github.com/${github_username}/${repo_name}.git"
print_info "Setting up remote origin: $git_url"

# Remove existing origin if it exists
git remote remove origin 2>/dev/null || true
git remote add origin "$git_url"

echo ""
read -p "🚀 Do you want to push to GitHub now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git branch -M main
    git push -u origin main
    print_status "Code pushed to GitHub"
else
    print_warning "Remember to push your code: git push -u origin main"
fi

# Step 3: LLM Provider setup
echo ""
echo "🤖 Step 3: LLM Provider Configuration"
print_info "Choose your LLM provider for intelligent contact extraction:"
echo ""
echo "1. Groq (Free tier, fast) - Recommended for testing"
echo "2. OpenAI (GPT-3.5/4) - Recommended for production"
echo "3. Anthropic (Claude) - High quality alternative"
echo "4. Google (Gemini) - Good balance of cost and quality"
echo "5. Skip for now"

echo ""
read -p "🤔 Choose your provider (1-5): " -n 1 -r provider_choice
echo

case $provider_choice in
    1)
        print_info "Groq selected - Get your API key from: https://console.groq.com/keys"
        echo "Set these environment variables in Render:"
        echo "GROQ_API_KEY=gsk_your-groq-api-key-here"
        echo "GROQ_MODEL=mixtral-8x7b-32768"
        ;;
    2)
        print_info "OpenAI selected - Get your API key from: https://platform.openai.com/api-keys"
        echo "Set these environment variables in Render:"
        echo "OPENAI_API_KEY=sk-your-openai-api-key-here"
        echo "OPENAI_MODEL=gpt-3.5-turbo"
        ;;
    3)
        print_info "Anthropic selected - Get your API key from: https://console.anthropic.com/"
        echo "Set these environment variables in Render:"
        echo "ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here"
        echo "ANTHROPIC_MODEL=claude-3-haiku-20240307"
        ;;
    4)
        print_info "Google Gemini selected - Get your API key from: https://makersuite.google.com/app/apikey"
        echo "Set these environment variables in Render:"
        echo "GEMINI_API_KEY=your-gemini-api-key-here"
        echo "GEMINI_MODEL=gemini-pro"
        ;;
    5)
        print_warning "Skipping LLM configuration - you can set it up later"
        ;;
    *)
        print_warning "Invalid choice - you can configure LLM provider later"
        ;;
esac

# Step 4: Render deployment instructions
echo ""
echo "☁️  Step 4: Render Deployment Instructions"
print_info "Now deploy your OCR service on Render:"
echo ""
echo "1. Go to https://dashboard.render.com"
echo "2. Click 'New' → 'Web Service'"
echo "3. Connect your GitHub repository: $git_url"
echo "4. Configure the service:"
echo "   - Name: ocr-microservice"
echo "   - Environment: Docker"
echo "   - Region: Same as your main backend"
echo "   - Branch: main"
echo ""
echo "5. Set these environment variables:"
echo "   ALLOWED_ORIGINS=https://contact-management-six-alpha.vercel.app,https://contact-management-ffsl.onrender.com"
echo "   PORT=8002"
echo "   [Your LLM provider variables from above]"
echo ""
echo "6. Click 'Create Web Service'"
echo "7. Wait for deployment (5-10 minutes)"
echo "8. Note your service URL: https://your-ocr-service.onrender.com"

# Step 5: Main backend configuration
echo ""
echo "🔧 Step 5: Main Backend Configuration"
print_info "After your OCR service is deployed, update your main backend:"
echo ""
echo "1. Go to your main backend service in Render"
echo "2. Add this environment variable:"
echo "   OCR_SERVICE_URL=https://your-ocr-service.onrender.com"
echo "3. Your main backend will automatically use the OCR microservice"

# Step 6: Testing
echo ""
echo "🧪 Step 6: Testing"
print_info "Test your deployment:"
echo ""
echo "1. Health check: curl https://your-ocr-service.onrender.com/health"
echo "2. Upload a business card image through your frontend"
echo "3. Check that processing completes without timeout"
echo "4. Verify contacts are extracted with proper categorization"

# Summary
echo ""
echo "📋 Summary"
echo "=========="
print_status "OCR microservice code prepared and committed"
print_status "GitHub repository configured: $git_url"
print_info "Next steps:"
echo "1. Deploy OCR service on Render using the instructions above"
echo "2. Configure your chosen LLM provider"
echo "3. Update main backend with OCR_SERVICE_URL"
echo "4. Test the integration"

echo ""
print_status "Setup complete! 🎉"
print_info "See COMPLETE_DEPLOYMENT_GUIDE.md for detailed instructions"

cd ..  # Return to original directory
