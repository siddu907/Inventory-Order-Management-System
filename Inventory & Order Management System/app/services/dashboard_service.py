from sqlalchemy.orm import Session

from app.config import settings
from app.repositories.dashboard_repository import DashboardRepository
from app.services.cache_service import CacheService


class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DashboardRepository(db)
        self.cache = CacheService() if settings.redis_enabled else None

    def admin_dashboard(self) -> dict:
        # Try cache first
        if self.cache:
            cache_key = "dashboard:admin"
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached
        
        stats = self.repo.admin_stats()
        
        # Cache for shorter duration (dashboard data changes frequently)
        if self.cache:
            self.cache.set(cache_key, stats, ttl=settings.cache_ttl)  
        
        return stats

    def staff_dashboard(self) -> dict:
        # Try cache first
        if self.cache:
            cache_key = "dashboard:staff"
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached
        
        stats = self.repo.staff_stats()
        
        # Cache for shorter duration
        if self.cache:
            self.cache.set(cache_key, stats, ttl=settings.cache_ttl) 
        
        return stats

    def customer_dashboard(self, customer_id: int) -> dict:
        # Try cache first
        if self.cache:
            cache_key = f"dashboard:customer:{customer_id}"
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached
        
        stats = self.repo.customer_stats(customer_id)
        
        # Cache for shorter duration
        if self.cache:
            self.cache.set(cache_key, stats, ttl=settings.cache_ttl)  
        
        return stats
