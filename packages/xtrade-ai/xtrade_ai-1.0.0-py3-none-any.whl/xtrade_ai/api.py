"""
XTrade-AI API Server

This module provides a FastAPI-based REST API for the XTrade-AI framework,
enabling remote access to trading functionality, model management, and monitoring.
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

import psycopg2
import redis
from fastapi import (
    Depends, FastAPI, HTTPException, Request, Response, status
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn

from . import XTradeAIConfig, XTradeAIFramework, get_info, get_version
from .utils.logger import get_logger

# Configure logging
logger = get_logger(__name__)

# Security
security = HTTPBearer()

# Pydantic models for API requests/responses
class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
    services: Dict[str, str]

class ModelInfo(BaseModel):
    id: Optional[str] = None
    name: str
    type: str
    version: str
    status: str
    file_path: Optional[str] = None
    url: Optional[str] = None
    is_encrypted: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ModelLoadRequest(BaseModel):
    path: str
    model_name: str = "all"
    password: Optional[str] = None

class ModelLoadResponse(BaseModel):
    success: bool
    message: str
    model_info: Optional[ModelInfo] = None

class PredictionRequest(BaseModel):
    symbol: str
    model_name: str
    data: Dict[str, Any]

class PredictionResponse(BaseModel):
    symbol: str
    prediction: float
    confidence: float
    timestamp: datetime

class PositionInfo(BaseModel):
    id: str
    symbol: str
    side: str
    quantity: float
    entry_price: float
    current_price: Optional[float] = None
    pnl: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    strategy_name: Optional[str] = None
    status: str
    created_at: datetime

class OrderInfo(BaseModel):
    id: str
    symbol: str
    order_type: str
    side: str
    quantity: float
    price: Optional[float] = None
    status: str
    created_at: datetime

class PortfolioInfo(BaseModel):
    balance: float
    equity: float
    margin: float
    free_margin: float
    timestamp: datetime

class UserInfo(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime

class ApiKeyInfo(BaseModel):
    id: str
    key_name: str
    permissions: List[str]
    is_active: bool
    last_used: Optional[datetime] = None
    created_at: datetime
    expires_at: Optional[datetime] = None

# Database connection
class DatabaseManager:
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'xtrade_ai'),
            'user': os.getenv('POSTGRES_USER', 'xtrade_user'),
            'password': os.getenv('POSTGRES_PASSWORD', 'xtrade_password')
        }
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', '6379')),
            db=0,
            decode_responses=True
        )

    def get_connection(self):
        return psycopg2.connect(**self.connection_params)

    def get_redis(self):
        return self.redis_client

# Initialize database manager
db_manager = DatabaseManager()

# Initialize XTrade-AI framework
def get_framework() -> XTradeAIFramework:
    """Get XTrade-AI framework instance."""
    try:
        config = XTradeAIConfig()
        return XTradeAIFramework(config)
    except Exception as e:
        logger.error(f"Failed to initialize framework: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Framework initialization failed"
        )

# Authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Authenticate user using API key."""
    api_key = credentials.credentials
    
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Check if API key exists and is active
        cursor.execute("""
            SELECT u.id, u.username, u.email, u.is_admin, ak.permissions
            FROM api.users u
            JOIN api.api_keys ak ON u.id = ak.user_id
            WHERE ak.api_key = %s AND ak.is_active = TRUE AND u.is_active = TRUE
            AND (ak.expires_at IS NULL OR ak.expires_at > NOW())
        """, (api_key,))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired API key"
            )
        
        user_id, username, email, is_admin, permissions = result
        
        # Update last used timestamp
        cursor.execute("""
            UPDATE api.api_keys 
            SET last_used = NOW() 
            WHERE api_key = %s
        """, (api_key,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "id": user_id,
            "username": username,
            "email": email,
            "is_admin": is_admin,
            "permissions": permissions or []
        }
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

# Create FastAPI app
app = FastAPI(
    title="XTrade-AI API",
    description="REST API for XTrade-AI Trading Framework",
    version=get_version(),
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    # Store API request in database
    try:
        user_id = None
        api_key_id = None
        
        # Extract user info if authenticated
        if "authorization" in request.headers:
            auth_header = request.headers["authorization"]
            if auth_header.startswith("Bearer "):
                api_key = auth_header[7:]
                conn = db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_id, id FROM api.api_keys WHERE api_key = %s
                """, (api_key,))
                result = cursor.fetchone()
                if result:
                    user_id, api_key_id = result
                cursor.close()
                conn.close()
        
        # Store request
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO api.api_requests 
            (user_id, api_key_id, endpoint, method, status_code, response_time_ms, ip_address, user_agent)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            api_key_id,
            str(request.url.path),
            request.method,
            response.status_code,
            int(process_time * 1000),
            request.client.host if request.client else None,
            request.headers.get("user-agent")
        ))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to log API request: {e}")
    
    return response

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health and dependencies."""
    services = {}
    
    # Check database
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        services["database"] = "healthy"
    except Exception as e:
        services["database"] = f"error: {str(e)}"
    
    # Check Redis
    try:
        redis_client = db_manager.get_redis()
        redis_client.ping()
        services["redis"] = "healthy"
    except Exception as e:
        services["redis"] = f"error: {str(e)}"
    
    # Check framework
    try:
        framework = get_framework()
        services["framework"] = "healthy"
    except Exception as e:
        services["framework"] = f"error: {str(e)}"
    
    overall_status = "healthy" if all("healthy" in status for status in services.values()) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        version=get_version(),
        timestamp=datetime.now(),
        services=services
    )

# Model management endpoints
@app.get("/models", response_model=List[ModelInfo])
async def list_models(current_user: Dict[str, Any] = Depends(get_current_user)):
    """List all available models."""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, model_name, model_type, version, status, file_path, url, 
                   is_encrypted, created_at, updated_at
            FROM models.model_metadata
            ORDER BY created_at DESC
        """)
        
        models = []
        for row in cursor.fetchall():
            models.append(ModelInfo(
                id=str(row[0]),
                name=row[1],
                type=row[2],
                version=row[3],
                status=row[4],
                file_path=row[5],
                url=row[6],
                is_encrypted=row[7],
                created_at=row[8],
                updated_at=row[9]
            ))
        
        cursor.close()
        conn.close()
        
        return models
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list models"
        )

@app.post("/models/load", response_model=ModelLoadResponse)
async def load_model(
    request: ModelLoadRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Load a model from path or URL."""
    try:
        framework = get_framework()
        
        # Load model
        success = framework.load_model(
            path=request.path,
            model_name=request.model_name,
            password=request.password
        )
        
        if success:
            # Get model info
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, model_name, model_type, version, status, file_path, url, 
                       is_encrypted, created_at, updated_at
                FROM models.model_metadata
                WHERE model_name = %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (request.model_name,))
            
            row = cursor.fetchone()
            model_info = None
            if row:
                model_info = ModelInfo(
                    id=str(row[0]),
                    name=row[1],
                    type=row[2],
                    version=row[3],
                    status=row[4],
                    file_path=row[5],
                    url=row[6],
                    is_encrypted=row[7],
                    created_at=row[8],
                    updated_at=row[9]
                )
            
            cursor.close()
            conn.close()
            
            return ModelLoadResponse(
                success=True,
                message="Model loaded successfully",
                model_info=model_info
            )
        else:
            return ModelLoadResponse(
                success=False,
                message="Failed to load model"
            )
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load model: {str(e)}"
        )

@app.post("/predict", response_model=PredictionResponse)
async def predict(
    request: PredictionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Make a prediction using a loaded model."""
    try:
        framework = get_framework()
        
        # Make prediction (this would need to be implemented in the framework)
        # For now, return a mock prediction
        prediction = 0.65  # Mock prediction value
        confidence = 0.85  # Mock confidence
        
        return PredictionResponse(
            symbol=request.symbol,
            prediction=prediction,
            confidence=confidence,
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Failed to make prediction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to make prediction: {str(e)}"
        )

# Trading endpoints
@app.get("/positions", response_model=List[PositionInfo])
async def list_positions(current_user: Dict[str, Any] = Depends(get_current_user)):
    """List all trading positions."""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, symbol, side, quantity, entry_price, current_price, pnl,
                   stop_loss, take_profit, strategy_name, status, created_at
            FROM trading.positions
            ORDER BY created_at DESC
        """)
        
        positions = []
        for row in cursor.fetchall():
            positions.append(PositionInfo(
                id=str(row[0]),
                symbol=row[1],
                side=row[2],
                quantity=float(row[3]),
                entry_price=float(row[4]),
                current_price=float(row[5]) if row[5] else None,
                pnl=float(row[6]),
                stop_loss=float(row[7]) if row[7] else None,
                take_profit=float(row[8]) if row[8] else None,
                strategy_name=row[9],
                status=row[10],
                created_at=row[11]
            ))
        
        cursor.close()
        conn.close()
        
        return positions
    except Exception as e:
        logger.error(f"Failed to list positions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list positions"
        )

@app.get("/orders", response_model=List[OrderInfo])
async def list_orders(current_user: Dict[str, Any] = Depends(get_current_user)):
    """List all trading orders."""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, symbol, order_type, side, quantity, price, status, created_at
            FROM trading.orders
            ORDER BY created_at DESC
        """)
        
        orders = []
        for row in cursor.fetchall():
            orders.append(OrderInfo(
                id=str(row[0]),
                symbol=row[1],
                order_type=row[2],
                side=row[3],
                quantity=float(row[4]),
                price=float(row[5]) if row[5] else None,
                status=row[6],
                created_at=row[7]
            ))
        
        cursor.close()
        conn.close()
        
        return orders
    except Exception as e:
        logger.error(f"Failed to list orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list orders"
        )

@app.get("/portfolio", response_model=PortfolioInfo)
async def get_portfolio(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current portfolio information."""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT balance, equity, margin, free_margin, timestamp
            FROM trading.portfolio
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio information not found"
            )
        
        portfolio = PortfolioInfo(
            balance=float(row[0]),
            equity=float(row[1]),
            margin=float(row[2]),
            free_margin=float(row[3]),
            timestamp=row[4]
        )
        
        cursor.close()
        conn.close()
        
        return portfolio
    except Exception as e:
        logger.error(f"Failed to get portfolio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get portfolio"
        )

# User management endpoints (admin only)
@app.get("/users", response_model=List[UserInfo])
async def list_users(current_user: Dict[str, Any] = Depends(get_current_user)):
    """List all users (admin only)."""
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, is_active, is_admin, created_at
            FROM api.users
            ORDER BY created_at DESC
        """)
        
        users = []
        for row in cursor.fetchall():
            users.append(UserInfo(
                id=str(row[0]),
                username=row[1],
                email=row[2],
                is_active=row[3],
                is_admin=row[4],
                created_at=row[5]
            ))
        
        cursor.close()
        conn.close()
        
        return users
    except Exception as e:
        logger.error(f"Failed to list users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users"
        )

@app.get("/api-keys", response_model=List[ApiKeyInfo])
async def list_api_keys(current_user: Dict[str, Any] = Depends(get_current_user)):
    """List API keys for current user."""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, key_name, permissions, is_active, last_used, created_at, expires_at
            FROM api.api_keys
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (current_user["id"],))
        
        api_keys = []
        for row in cursor.fetchall():
            api_keys.append(ApiKeyInfo(
                id=str(row[0]),
                key_name=row[1],
                permissions=row[2] or [],
                is_active=row[3],
                last_used=row[4],
                created_at=row[5],
                expires_at=row[6]
            ))
        
        cursor.close()
        conn.close()
        
        return api_keys
    except Exception as e:
        logger.error(f"Failed to list API keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list API keys"
        )

# Root endpoint
@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "XTrade-AI API",
        "version": get_version(),
        "docs": "/docs",
        "health": "/health"
    }

def start_api_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    workers: int = 1
):
    """Start the API server."""
    logger.info(f"Starting XTrade-AI API server on {host}:{port}")
    
    uvicorn.run(
        "xtrade_ai.api:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        log_level="info"
    )

if __name__ == "__main__":
    start_api_server()
