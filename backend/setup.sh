#!/bin/bash

echo "Setting up Face Recognition Backend..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create virtual environment using uv
uv venv

# Install dependencies using uv
uv pip install -r requirements.txt

# Create database folder
mkdir -p database

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
DATABASE_URL=postgresql://user:password@localhost:5432/face_recognition
SECRET_KEY=$(openssl rand -hex 32)
EOF
    echo "Please update .env with your PostgreSQL credentials"
fi

echo "Backend setup complete!"
echo "Don't forget to:"
echo "1. Create PostgreSQL database: createdb face_recognition"
echo "2. Update .env with your database credentials"
echo "3. Run: source venv/bin/activate && uvicorn main:app --reload"

