import asyncio
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User, Roadmap, RoadmapStep
from app.rag import adapt_roadmap_preview

# Use the actual db path which is probably ./backend.db or similar? Wait, what is SQLALCHEMY_DATABASE_URL? Let's check app/db.py.
