from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update


from app.backend.db_depends import get_dbs