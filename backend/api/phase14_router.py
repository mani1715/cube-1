"""
Phase 14 - Scalability, Backup & Infrastructure Router
API endpoints for scalability monitoring, backup management, and infrastructure
"""
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
import logging

from api.admin.permissions import get_current_admin, require_super_admin
from api.phase14_scalability import (
    DatabaseConnectionPool,
    CacheStrategy,
    CacheWarmer,
    BackgroundTasks as Phase14BackgroundTasks,
    PerformanceMonitor,
    performance_monitor,
    get_database_stats
)
from api.phase14_backup import BackupManager
from cache import cache

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/phase14", tags=["Phase 14 - Scalability & Backup"])

# Get MongoDB connection from environment
from motor.motor_asyncio import AsyncIOMotorClient

mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

# Initialize connection pool (will be used by dependency injection)
db_pool = DatabaseConnectionPool(mongo_url, db_name, max_pool_size=50, min_pool_size=10)

# Initialize backup manager
backup_manager = None


def get_db():
    """Dependency to get database instance"""
    return db_pool.get_db()


def get_backup_manager():
    """Dependency to get backup manager instance"""
    global backup_manager
    if backup_manager is None:
        db = db_pool.get_db()
        backup_manager = BackupManager(db)
    return backup_manager


# ============= CONNECTION POOL HEALTH =============

@router.get("/scalability/connection-pool/health")
async def check_connection_pool_health(
    admin = Depends(require_super_admin)
):
    """
    Check MongoDB connection pool health
    Returns connection statistics and health status
    """
    try:
        health = await db_pool.health_check()
        return health
    except Exception as e:
        logger.error(f"Connection pool health check error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check connection pool health")


# ============= CACHE MANAGEMENT =============

@router.get("/scalability/cache/stats")
async def get_cache_statistics(
    admin = Depends(require_super_admin)
):
    """
    Get detailed cache statistics
    Returns hit rate, size, and usage metrics
    """
    try:
        stats = cache.get_stats()
        return {
            "cache_stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Cache stats error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get cache statistics")


@router.post("/scalability/cache/warm")
async def warm_cache(
    background_tasks: BackgroundTasks,
    admin = Depends(require_super_admin),
    db = Depends(get_db)
):
    """
    Trigger cache warming for critical endpoints
    Pre-populates cache with frequently accessed data
    """
    try:
        # Run cache warming in background
        background_tasks.add_task(CacheWarmer.warm_critical_caches, db)
        
        return {
            "message": "Cache warming initiated",
            "status": "in_progress"
        }
    except Exception as e:
        logger.error(f"Cache warming error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initiate cache warming")


@router.post("/scalability/cache/clear/{entity_type}")
async def clear_entity_cache(
    entity_type: str,
    admin = Depends(require_super_admin)
):
    """
    Clear cache for specific entity type
    Useful after bulk updates or data imports
    """
    try:
        CacheStrategy.invalidate_related_caches(entity_type)
        
        return {
            "message": f"Cache cleared for entity type: {entity_type}",
            "entity_type": entity_type
        }
    except Exception as e:
        logger.error(f"Cache clear error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")


@router.delete("/scalability/cache/cleanup")
async def cleanup_expired_cache(
    background_tasks: BackgroundTasks,
    admin = Depends(require_super_admin)
):
    """
    Remove expired cache entries
    Frees up memory from stale cached data
    """
    try:
        # Run cleanup in background
        background_tasks.add_task(Phase14BackgroundTasks.cleanup_expired_cache)
        
        return {
            "message": "Cache cleanup initiated",
            "status": "in_progress"
        }
    except Exception as e:
        logger.error(f"Cache cleanup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cleanup cache")


# ============= DATABASE OPTIMIZATION =============

@router.get("/scalability/database/stats")
async def get_database_statistics(
    admin = Depends(require_super_admin),
    db = Depends(get_db)
):
    """
    Get comprehensive database statistics
    Returns size, collection stats, and index information
    """
    try:
        stats = await get_database_stats(db)
        return stats
    except Exception as e:
        logger.error(f"Database stats error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get database statistics")


@router.post("/scalability/database/cleanup-sessions")
async def cleanup_old_sessions(
    background_tasks: BackgroundTasks,
    days: int = 90,
    admin = Depends(require_super_admin),
    db = Depends(get_db)
):
    """
    Cleanup old completed sessions
    Removes sessions older than specified days
    """
    try:
        if days < 30:
            raise HTTPException(status_code=400, detail="Days must be at least 30")
        
        # Run cleanup in background
        background_tasks.add_task(
            Phase14BackgroundTasks.cleanup_old_sessions,
            db,
            days
        )
        
        return {
            "message": f"Session cleanup initiated (older than {days} days)",
            "days": days,
            "status": "in_progress"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session cleanup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cleanup sessions")


@router.post("/scalability/database/optimize-indexes")
async def optimize_database_indexes(
    background_tasks: BackgroundTasks,
    admin = Depends(require_super_admin),
    db = Depends(get_db)
):
    """
    Optimize database indexes
    Checks and optimizes indexes for better query performance
    """
    try:
        # Run optimization in background
        background_tasks.add_task(Phase14BackgroundTasks.optimize_indexes, db)
        
        return {
            "message": "Index optimization initiated",
            "status": "in_progress"
        }
    except Exception as e:
        logger.error(f"Index optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to optimize indexes")


# ============= PERFORMANCE MONITORING =============

@router.get("/scalability/performance/metrics")
async def get_performance_metrics(
    admin = Depends(require_super_admin)
):
    """
    Get application performance metrics
    Returns request stats, response times, and error rates
    """
    try:
        metrics = performance_monitor.get_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Performance metrics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get performance metrics")


# ============= SCALABILITY OVERVIEW =============

@router.get("/scalability/overview")
async def get_scalability_overview(
    admin = Depends(require_super_admin),
    db = Depends(get_db)
):
    """
    Get comprehensive scalability overview
    Combines cache, database, and performance metrics
    """
    try:
        # Get all metrics
        cache_stats = cache.get_stats()
        db_health = await db_pool.health_check()
        performance_metrics = performance_monitor.get_metrics()
        
        return {
            "connection_pool": {
                "status": db_health.get("status"),
                "response_time_ms": db_health.get("response_time_ms"),
                "max_pool_size": 50,
                "min_pool_size": 10
            },
            "cache": {
                "hit_rate": cache_stats.get("hit_rate", 0),
                "total_entries": cache_stats.get("cache_size", 0),
                "total_requests": cache_stats.get("total_requests", 0)
            },
            "performance": {
                "total_requests": performance_metrics.get("total_requests", 0),
                "avg_response_time": round(performance_metrics.get("avg_response_time", 0), 3),
                "error_rate": round(performance_metrics.get("error_rate", 0) * 100, 2)
            },
            "optimizations_enabled": [
                "Connection Pooling (10-50 connections)",
                "In-Memory Caching with TTL",
                "GZip Compression (>500 bytes)",
                "Query Result Caching",
                "Batch Operations Support",
                "Background Task Processing"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Scalability overview error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get scalability overview")


# ============= SCALABILITY CONFIGURATION =============

@router.get("/scalability/config")
async def get_scalability_configuration(
    admin = Depends(require_super_admin)
):
    """
    Get current scalability configuration
    Shows cache TTLs, pool sizes, and optimization settings
    """
    try:
        return {
            "connection_pool": {
                "max_pool_size": 50,
                "min_pool_size": 10,
                "max_idle_time_ms": 45000,
                "server_selection_timeout_ms": 5000,
                "connection_timeout_ms": 10000,
                "socket_timeout_ms": 20000
            },
            "cache_ttl_seconds": {
                "events": CacheStrategy.CACHE_CONFIGS.get("events", 3600),
                "blogs": CacheStrategy.CACHE_CONFIGS.get("blogs", 3600),
                "careers": CacheStrategy.CACHE_CONFIGS.get("careers", 3600),
                "psychologists": CacheStrategy.CACHE_CONFIGS.get("psychologists", 3600),
                "sessions": CacheStrategy.CACHE_CONFIGS.get("sessions", 600),
                "volunteers": CacheStrategy.CACHE_CONFIGS.get("volunteers", 600),
                "analytics": CacheStrategy.CACHE_CONFIGS.get("analytics", 300),
                "dashboard": CacheStrategy.CACHE_CONFIGS.get("dashboard", 300),
                "stats": CacheStrategy.CACHE_CONFIGS.get("stats", 120)
            },
            "compression": {
                "enabled": True,
                "minimum_size_bytes": 500,
                "algorithm": "gzip"
            },
            "batch_operations": {
                "insert_batch_size": 100,
                "update_batch_size": 50
            },
            "background_tasks": {
                "enabled": True,
                "cache_cleanup_enabled": True,
                "session_cleanup_days": 90
            }
        }
    except Exception as e:
        logger.error(f"Config fetch error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get configuration")


# ============= HEALTH CHECK =============

@router.get("/scalability/health")
async def scalability_health_check(
    db = Depends(get_db)
):
    """
    Comprehensive health check for scalability components
    Public endpoint for monitoring tools
    """
    try:
        health_status = {
            "status": "healthy",
            "components": {}
        }
        
        # Check database connection
        try:
            db_health = await db_pool.health_check()
            health_status["components"]["database"] = {
                "status": db_health.get("status"),
                "response_time_ms": db_health.get("response_time_ms")
            }
        except Exception as e:
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        # Check cache
        try:
            cache_stats = cache.get_stats()
            health_status["components"]["cache"] = {
                "status": "healthy",
                "size": cache_stats.get("cache_size", 0),
                "hit_rate": cache_stats.get("hit_rate", 0)
            }
        except Exception as e:
            health_status["components"]["cache"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        health_status["timestamp"] = datetime.utcnow().isoformat()
        
        return health_status
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
