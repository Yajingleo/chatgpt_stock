#!/usr/bin/env python3
"""Quick diagnostic: why is OpenAI not being called?"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

# 1. Is the openai package importable?
try:
    from openai import OpenAI
    print("1. openai package: INSTALLED")
except ImportError as e:
    print(f"1. openai package: NOT INSTALLED  --> {e}")

# 2. Is dotenv loading the .env file?
try:
    from dotenv import load_dotenv
    loaded = load_dotenv()
    print(f"   dotenv load_dotenv(): {loaded}")
except ImportError:
    print("   python-dotenv: NOT installed")

key = os.getenv("OPENAI_API_KEY", "")
print(f"2. OPENAI_API_KEY in env: present={bool(key)}  len={len(key)}")

# 3. Does the settings singleton see the key?
from agent.config import settings
print(f"3. settings.openai.api_key present: {bool(settings.openai.api_key)}")
print(f"   settings.openai.model: {settings.openai.model}")

# 4. Does the sentiment module think OpenAI is available?
from agent.analysis import sentiment as sm
print(f"4. sentiment.OPENAI_AVAILABLE: {sm.OPENAI_AVAILABLE}")

# 5. Would analyze_article_with_llm use OpenAI or simulation?
api_key = settings.openai.api_key or os.getenv("OPENAI_API_KEY")
if not sm.OPENAI_AVAILABLE or not api_key:
    print("5. analyze_article_with_llm --> SIMULATION (openai not usable)")
else:
    print("5. analyze_article_with_llm --> REAL OpenAI calls")
