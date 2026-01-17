#!/usr/bin/env python3
"""
Helper script to update .env file with all credentials.
Run this script to create/update your .env file.
"""

import os
from pathlib import Path

# Complete .env content with all your credentials
ENV_CONTENT = """# LifeMemory AI - Environment Variables
# ⚠️ SECURITY WARNING: This file contains sensitive credentials
# NEVER commit this file to version control

# ============================================================================
# ENVIRONMENT
# ============================================================================
ENV=production
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# ============================================================================
# SUPABASE CONFIGURATION
# ============================================================================
SUPABASE_URL=https://brcfzyyvgotqvgjwqkov.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJyY2Z6eXl2Z290cXZnandxa292Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg2Mjk3NTcsImV4cCI6MjA4NDIwNTc1N30.XBF0XtzTm4k40az4dzM4-0Uu1ehXDduwkEhdQODVuh4
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJyY2Z6eXl2Z290cXZnandxa292Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODYyOTc1NywiZXhwIjoyMDg0MjA1NzU3fQ.tYRulZCYc8tQjeTpw_Z5eQ_ad_QxRbvrgrgqkRzBl6M
SUPABASE_JWT_SECRET=EYADi8iEGsrLm6zfzv/fejMsWIwY32+q4JNajHwdw/Y6iVvLVRcFAmRBOLiJEQj+fF2kbCL+uo5eMemGJM1vRg==

# Database connection (using pooler)
DATABASE_URL=postgresql://postgres.brcfzyyvgotqvgjwqkov:MuKaMbIkA2005@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres

# ============================================================================
# EMBEDDING CONFIGURATION (Cohere default)
# ============================================================================
USE_COHERE=true
COHERE_API_KEY=5rJLG5DNb98pOx8Nh1WflxtHb8Y6tnMOh1kqme3k

# OpenAI fallback (if needed)
OPENAI_API_KEY=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
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIMENSION=3072

# ============================================================================
# LLM CONFIGURATION (with fallback support)
# ============================================================================
# Primary: OpenAI
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.3

# Fallback 1: Groq
GROQ_API_KEY=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

# Fallback 2: Gemini
GEMINI_API_KEY=AIzaSyB7aaWjSnBiC7ejU1-F2qylxhGGp26z5H8

# ============================================================================
# LANGGRAPH CONFIGURATION
# ============================================================================
MAX_RETRIEVED_MEMORIES=15
MAX_CONTEXT_TOKENS=4000
MIN_EVIDENCE_THRESHOLD=1
MIN_RELEVANCE_SCORE=0.3

# ============================================================================
# MLOps CONFIGURATION (Optional)
# ============================================================================
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=life-memory-ai
LANGCHAIN_TRACING_V2=false
LANGCHAIN_PROJECT=life-memory-ai

# ============================================================================
# REDIS CONFIGURATION (Optional)
# ============================================================================
REDIS_URL=redis://localhost:6379/0
"""

def main():
    """Create or update .env file."""
    script_dir = Path(__file__).parent
    env_file = script_dir / ".env"
    
    # Check if .env already exists
    if env_file.exists():
        response = input(f".env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled. .env file not updated.")
            return
    
    # Write .env file
    try:
        env_file.write_text(ENV_CONTENT, encoding='utf-8')
        print(f"✅ Successfully created/updated .env file at: {env_file}")
        print("✅ All credentials are now configured!")
        print("\nNext steps:")
        print("1. Run database schema in Supabase SQL Editor")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Start server: python main.py")
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return

if __name__ == "__main__":
    main()

