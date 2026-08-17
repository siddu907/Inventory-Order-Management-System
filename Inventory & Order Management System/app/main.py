from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.background import scheduler
from app.config import settings
from app.database import engine
from app.models import *  
from app.routers import auth, categories, products, inventory,orders, payments, reviews, notifications,dashboard, uploads, coupons
from app.utils.file_utils import ensure_upload_dir

app = FastAPI(
    title="Inventory & Order Management System",
    description=(
        "Backend API for managing products, inventory, orders, payments, "
        "reviews, and users with role-based access control."
    ),
    version="1.0.0",
    docs_url=None,          # custom Swagger UI below
    redoc_url="/redoc",
    swagger_ui_parameters={"persistAuthorization": True},)

ensure_upload_dir(settings.upload_dir)
app.mount("/uploads/files", StaticFiles(directory=settings.upload_dir), name="uploads")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    html = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>@@TITLE@@ – Docs</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css"/>
  <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png"/>
</head>
<body>
<div id="swagger-ui"></div>
<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script>
  const STORAGE_USERS_KEY = 'swagger_user_tokens';
  const STORAGE_LAST_USER_KEY = 'swagger_last_active_user';
  const SESSION_ACTIVE_USER_KEY = 'swagger_active_user';
  const MAX_RESTORE_MINUTES = 30;

  function loadUserTokens() {
    try {
      return JSON.parse(window.localStorage.getItem(STORAGE_USERS_KEY) || '{}');
    } catch (error) {
      console.warn('Unable to parse stored user tokens', error);
      return {};
    }
  }

  function saveUserTokens(users) {
    window.localStorage.setItem(STORAGE_USERS_KEY, JSON.stringify(users));
  }

  function setUserToken(userId, token, metadata = {}) {
    if (!userId || !token) {
      return;
    }
    const users = loadUserTokens();
    users[userId] = {
      token,
      email: metadata.email || users[userId]?.email || null,
      display_name: metadata.display_name || users[userId]?.display_name || null,
      saved_at: new Date().toISOString(),
    };
    saveUserTokens(users);
  }

  function getUserToken(userId) {
    const users = loadUserTokens();
    return users[userId]?.token;
  }

  function setLastActiveUser(userId) {
    if (!userId) {
      window.localStorage.removeItem(STORAGE_LAST_USER_KEY);
      return;
    }
    window.localStorage.setItem(
      STORAGE_LAST_USER_KEY,
      JSON.stringify({ user_id: userId, saved_at: new Date().toISOString() }),
    );
  }

  function getLastActiveUser() {
    try {
      return JSON.parse(window.localStorage.getItem(STORAGE_LAST_USER_KEY) || 'null');
    } catch (error) {
      console.warn('Unable to parse last active user', error);
      return null;
    }
  }

  function clearLastActiveUser() {
    window.localStorage.removeItem(STORAGE_LAST_USER_KEY);
  }

  function getActiveUserId() {
    return window.sessionStorage.getItem(SESSION_ACTIVE_USER_KEY);
  }

  function setActiveUserId(userId) {
    if (userId) {
      window.sessionStorage.setItem(SESSION_ACTIVE_USER_KEY, userId);
    } else {
      window.sessionStorage.removeItem(SESSION_ACTIVE_USER_KEY);
    }
  }

  function restoreSessionUser() {
    const activeUserId = getActiveUserId();
    if (activeUserId && getUserToken(activeUserId)) {
      return activeUserId;
    }
    const last = getLastActiveUser();
    if (!last || !last.user_id || !last.saved_at) {
      return null;
    }
    const savedAt = new Date(last.saved_at).getTime();
    const now = Date.now();
    if (Number.isNaN(savedAt) || now - savedAt > MAX_RESTORE_MINUTES * 60 * 1000) {
      clearLastActiveUser();
      return null;
    }
    if (!getUserToken(last.user_id)) {
      clearLastActiveUser();
      return null;
    }
    setActiveUserId(last.user_id);
    return last.user_id;
  }

  function applyToken(token) {
    if (!token || !window.ui) {
      return;
    }
    const value = `Bearer ${token}`;
    try {
      if (window.ui.authActions && window.ui.authActions.logout) {
        window.ui.authActions.logout();
      }
      if (window.ui.authActions && window.ui.authActions.authorize) {
        window.ui.authActions.authorize({
          HTTPBearer: {
            name: 'HTTPBearer',
            schema: {
              type: 'http',
              scheme: 'bearer',
              bearerFormat: 'JWT',
            },
            value,
          },
        });
      }
    } catch (error) {
      console.warn('Failed to apply Swagger bearer token', error);
    }
  }

  function injectAuthHeader(req, token) {
    if (!token) {
      return req;
    }
    if (!req.headers) {
      req.headers = {};
    }
    if (typeof req.headers.set === 'function') {
      req.headers.set('Authorization', `Bearer ${token}`);
    } else {
      req.headers = {
        ...req.headers,
        Authorization: `Bearer ${token}`,
      };
    }
    return req;
  }

  function saveLoginSession(userId, token, metadata) {
    setUserToken(userId, token, metadata);
    setActiveUserId(userId);
    setLastActiveUser(userId);
    applyToken(token);
  }

  const originalFetch = window.fetch.bind(window);
  window.fetch = async (...args) => {
    const response = await originalFetch(...args);
    try {
      const target = args[0];
      const url = typeof target === 'string' ? target : target?.url;
      if (typeof url === 'string' && url.includes('/auth/login') && response.ok) {
        const data = await response.clone().json();
        if (data && data.access_token && data.user && data.user.id) {
          saveLoginSession(String(data.user.id), data.access_token, {
            email: data.user.email,
            display_name: data.user.full_name || data.user.email,
          });
        }
      }
      if (typeof url === 'string' && url.includes('/auth/refresh') && response.ok) {
        const data = await response.clone().json();
        const activeUserId = getActiveUserId();
        if (data && data.access_token && activeUserId) {
          const users = loadUserTokens();
          const existing = users[activeUserId] || {};
          setUserToken(activeUserId, data.access_token, {
            email: existing.email,
            display_name: existing.display_name,
          });
          // IMPORTANT: Update last active user to persist the refreshed session
          setLastActiveUser(activeUserId);
          if (window.ui && window.ui.authActions && window.ui.authActions.logout) {
            window.ui.authActions.logout();
          }
          applyToken(data.access_token);
        }
      }
    } catch (error) {
      console.warn('Swagger fetch wrapper error', error);
    }
    return response;
  };

  window.ui = SwaggerUIBundle({
    url: '@@OPENAPI_URL@@',
    dom_id: '#swagger-ui',
    presets: [
      SwaggerUIBundle.presets.apis,
      SwaggerUIBundle.SwaggerUIStandalonePreset,
    ],
    persistAuthorization: true,
    requestInterceptor: (req) => {
      const activeUserId = getActiveUserId();
      const token = activeUserId ? getUserToken(activeUserId) : null;
      return injectAuthHeader(req, token);
    },
  });

  const restoredUserId = restoreSessionUser();
  if (restoredUserId) {
    const restoredToken = getUserToken(restoredUserId);
    applyToken(restoredToken);
  }
</script>
</body>
</html>"""
    html = html.replace("@@TITLE@@", app.title).replace("@@OPENAPI_URL@@", app.openapi_url)
    return HTMLResponse(html)

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.scheduler.start()
    yield
    scheduler.scheduler.shutdown(wait=False)

app.router.lifespan_context = lifespan

app.include_router(auth.router,prefix="/auth",tags=["Authentication"])
app.include_router(categories.router,prefix="/categories",tags=["Categories"])
app.include_router(products.router,prefix="/products",tags=["Products"])
app.include_router(inventory.router,prefix="/inventory",tags=["Inventory"])
app.include_router(orders.router,prefix="/orders",tags=["Orders"])
app.include_router(payments.router,prefix="/payments",tags=["Payments"])
app.include_router(reviews.router,prefix="/reviews",tags=["Reviews"])
app.include_router(notifications.router,prefix="/notifications",tags=["Notifications"])
app.include_router(coupons.router,prefix="/coupons",tags=["Coupons"])
app.include_router(dashboard.router,prefix="/dashboard",tags=["Dashboard"])
app.include_router(uploads.router,prefix="/uploads",tags=["Uploads"])

