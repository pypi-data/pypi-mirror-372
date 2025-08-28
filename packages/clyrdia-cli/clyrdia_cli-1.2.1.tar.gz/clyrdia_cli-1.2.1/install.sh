#!/bin/bash

# Clyrdia CLI Installation Script
# This script helps users install Clyrdia CLI from various sources

set -e

echo "🚀 Clyrdia CLI - Zero-Knowledge AI Benchmarking Platform"
echo "========================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_success "Python $PYTHON_VERSION found"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    # Check Python version
    PYTHON_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
    PYTHON_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_error "Python 3.8 or higher is required. Current version: $PYTHON_VERSION"
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    print_status "Checking pip installation..."
    
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
        print_success "pip3 found"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
        print_success "pip found"
    else
        print_error "pip is not installed. Please install pip first."
        exit 1
    fi
}

# Install from Test PyPI
install_from_testpypi() {
    print_status "Installing from Test PyPI..."
    
    $PIP_CMD install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ clyrdia-cli
    
    if [ $? -eq 0 ]; then
        print_success "Clyrdia CLI installed successfully from Test PyPI!"
    else
        print_error "Installation from Test PyPI failed"
        exit 1
    fi
}

# Install from PyPI (production)
install_from_pypi() {
    print_status "Installing from PyPI (production)..."
    
    $PIP_CMD install clyrdia-cli
    
    if [ $? -eq 0 ]; then
        print_success "Clyrdia CLI installed successfully from PyPI!"
    else
        print_error "Installation from PyPI failed"
        exit 1
    fi
}

# Install from local source
install_from_source() {
    print_status "Installing from local source..."
    
    if [ ! -f "pyproject.toml" ]; then
        print_error "pyproject.toml not found. Please run this script from the project root."
        exit 1
    fi
    
    $PIP_CMD install -e .
    
    if [ $? -eq 0 ]; then
        print_success "Clyrdia CLI installed successfully from source!"
    else
        print_error "Installation from source failed"
        exit 1
    fi
}

# Verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    if command -v clyrdia-cli &> /dev/null; then
        print_success "Clyrdia CLI command is available"
        
        # Test the help command
        if clyrdia-cli --help &> /dev/null; then
            print_success "Clyrdia CLI is working correctly"
        else
            print_warning "Clyrdia CLI installed but may have issues"
        fi
    else
        print_error "Clyrdia CLI command not found in PATH"
        exit 1
    fi
}

# Setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env file template..."
        cat > .env << EOF
# Clyrdia CLI Configuration
# Add your API keys here

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Configuration  
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Custom configuration path
CLYRIDIA_CONFIG_PATH=./production_benchmark.yaml
EOF
        print_success ".env file created. Please add your API keys."
    else
        print_status ".env file already exists"
    fi
    
    # Check if production benchmark YAML exists
    if [ -f "production_benchmark.yaml" ]; then
        print_success "Production benchmark configuration found"
    else
        print_warning "Production benchmark configuration not found. You may need to create one."
    fi
}

# Show next steps
show_next_steps() {
    echo ""
    echo "🎉 Installation completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Add your API keys to the .env file:"
    echo "   - OPENAI_API_KEY for GPT models"
    echo "   - ANTHROPIC_API_KEY for Claude models"
    echo ""
    echo "2. Test the installation:"
    echo "   clyrdia-cli --help"
    echo ""
    echo "3. Run your first benchmark:"
    echo "   clyrdia-cli run --config production_benchmark.yaml"
    echo ""
    echo "4. View the dashboard:"
    echo "   clyrdia-cli dashboard"
    echo ""
    echo "📚 For more information, visit: https://docs.clyrdia.com"
    echo ""
}

# Main installation flow
main() {
    echo "Welcome to Clyrdia CLI installation!"
    echo ""
    
    # Check prerequisites
    check_python
    check_pip
    
    echo ""
    echo "🎯 Choose installation method:"
    echo "1. Install from Test PyPI (recommended for testing)"
    echo "2. Install from PyPI (production)"
    echo "3. Install from local source (development)"
    echo ""
    
    while true; do
        read -p "Enter your choice (1-3): " choice
        case $choice in
            1)
                install_from_testpypi
                break
                ;;
            2)
                install_from_pypi
                break
                ;;
            3)
                install_from_source
                break
                ;;
            *)
                echo "Invalid choice. Please enter 1, 2, or 3."
                ;;
        esac
    done
    
    # Verify and setup
    verify_installation
    setup_environment
    show_next_steps
}

# Run main function
main "$@"
