#!/bin/bash
set -e

echo "Setting up enhanced terminal environment..."

# Check and configure Git user information
echo "Verificando configuração do Git..."
git_name=$(git config --global user.name 2>/dev/null || echo "")
git_email=$(git config --global user.email 2>/dev/null || echo "")

if [[ -z "$git_name" || -z "$git_email" ]]; then
    echo ""
    echo "🔧 Configuração de usuário do Git necessária!"
    echo "----------------------------------------"
    
    if [[ -z "$git_name" ]]; then
        echo -n "Por favor, digite seu nome completo: "
        read git_name
        git config --global user.name "$git_name"
        echo "✅ Git user.name configurado para: $git_name"
    fi
    
    if [[ -z "$git_email" ]]; then
        echo -n "Por favor, digite seu endereço de email: "
        read git_email
        git config --global user.email "$git_email"
        echo "✅ Git user.email configurado para: $git_email"
    fi
    
    echo "----------------------------------------"
    echo ""
else
    echo "✅ Git já configurado:"
    echo "   Nome: $git_name"
    echo "   Email: $git_email"
    echo ""
fi

# Create the p10k config file for a better-looking prompt
cp -f .devcontainer/p10k.zsh /root/.p10k.zsh

# Add source for p10k to zshrc
echo '[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh' >> /root/.zshrc

# Create Python development shortcuts
cat > /root/.pythondev_shortcuts << 'EOF'
#!/bin/bash

# Format code
format() {
  uvx ruff format .
}

# Run linting
lint() {
  uvx ruff check . && uvx mypy .
}

# Setup pre-commit
setup_hooks() {
  pip install pre-commit
  pre-commit install
}

# Update Siga MCP CLI with latest changes
sigamcp-update() {
  echo "🔄 Updating Siga MCP CLI..."
  cd /workspace
  bash .devcontainer/install-commands-cli.sh
  echo "✅ Siga MCP CLI updated! You can run 'sigamcp' to use the latest version."
}

alias f=format
alias l=lint
alias hooks=setup_hooks
alias update-sigamcp=sigamcp-update
EOF

# Source shortcuts in profile
echo 'source /root/.pythondev_shortcuts' >> /root/.zshrc
echo 'source /root/.pythondev_shortcuts' >> /root/.bashrc

# Create welcome message
cat > /root/.welcome_message << 'EOF'
#######################################################
#                                                     #
#              Welcome to Siga MCP Dev!              #
#                                                     #
#######################################################

Python Environment:
- Format code: 'f'
- Lint code: 'l'

Siga MCP CLI:
- Run CLI: 'sigamcp'
- Update CLI: 'sigamcp-update' or 'update-sigamcp'

Container Information:
- Name: sigamcp-dev
- Package Manager: UV disponível

EOF

# Display welcome message on startup
echo 'cat /root/.welcome_message' >> /root/.zshrc

# Build and install the commands CLI if commands.go exists
if [[ -f "commands.go" ]]; then
    echo "Installing Siga MCP CLI..."
    bash .devcontainer/install-commands-cli.sh
fi
