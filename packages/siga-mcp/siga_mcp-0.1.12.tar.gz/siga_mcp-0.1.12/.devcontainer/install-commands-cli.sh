#!/bin/bash
set -e

echo "Building and installing Siga MCP CLI..."

# Check if we're in the right directory
if [[ ! -f "commands.go" ]]; then
    echo "Error: commands.go not found. Please run this script from the project root."
    exit 1
fi

# Initialize Go module if go.mod doesn't exist
if [[ ! -f "go.mod" ]]; then
    echo "Initializing Go module..."
    go mod init commands-cli
    go mod tidy
fi

# Build the binary
echo "Building Siga MCP CLI..."
go build -o /usr/local/bin/sigamcp commands.go

# Make it executable
chmod +x /usr/local/bin/sigamcp

echo "✅ Siga MCP CLI installed successfully!"
echo "You can now run 'sigamcp' from anywhere in your terminal." 