# Deprecated API Files

**Date**: December 1, 2025  
**Status**: ⚠️ DEPRECATED

---

## ⚠️ Important Notice

The following files are **DEPRECATED** and should NOT be used for new deployments:

### 1. `main.py` (Original)
- **Status**: ❌ DEPRECATED
- **Reason**: Uses in-memory storage (`campaigns_db = {}`), not production-ready
- **Replace with**: `main_v3.py`
- **Issues**:
  - Line 60: In-memory storage dictionary
  - No database persistence
  - No authentication
  - No rate limiting
  - Data loss on restart

### 2. `main_v2.py`
- **Status**: ⚠️ DEPRECATED
- **Reason**: Lacks structured error handling
- **Replace with**: `main_v3.py`
- **Issues**:
  - No structured error codes
  - No custom exception handlers
  - Missing error handling middleware

---

## ✅ Use This Instead

### Production-Ready Version: `main_v3.py`

**Features**:
- ✅ Database persistence (PostgreSQL/SQLite)
- ✅ JWT authentication
- ✅ Rate limiting
- ✅ API versioning (/api/v1/)
- ✅ Structured error handling
- ✅ Custom exception handlers
- ✅ Health checks
- ✅ Proper logging

**Usage**:
```bash
# Start API
uvicorn src.api.main_v3:app --reload

# With Docker
docker-compose up -d
```

---

## 📋 Migration Guide

### From main.py to main_v3.py

#### Step 1: Update Entry Point
```bash
# Old
uvicorn src.api.main:app --reload

# New
uvicorn src.api.main_v3:app --reload
```

#### Step 2: Initialize Database
```bash
# Create database schema
python scripts/init_database.py

# Create admin user
python scripts/init_users.py
```

#### Step 3: Update Configuration
```bash
# Copy environment template
cp .env.docker .env

# Edit .env with your settings
```

#### Step 4: Migrate Data (if any)
```bash
# If you have data in memory, it's lost
# Start fresh with database
```

### From main_v2.py to main_v3.py

#### Step 1: Update Entry Point
```bash
# Old
uvicorn src.api.main_v2:app --reload

# New
uvicorn src.api.main_v3:app --reload
```

#### Step 2: Update Error Handling
- main_v3.py includes structured error codes
- Custom exception handlers
- Better error responses

#### Step 3: Test Endpoints
- All endpoints remain the same
- Error responses now include error codes
- Better error messages

---

## 🔍 Comparison

| Feature | main.py | main_v2.py | main_v3.py |
|---------|---------|------------|------------|
| **Database** | ❌ In-memory | ✅ PostgreSQL/SQLite | ✅ PostgreSQL/SQLite |
| **Authentication** | ❌ None | ✅ JWT | ✅ JWT |
| **Rate Limiting** | ❌ None | ✅ Yes | ✅ Yes |
| **API Versioning** | ❌ No | ✅ /api/v1/ | ✅ /api/v1/ |
| **Error Handling** | ❌ Basic | ⚠️ Basic | ✅ Structured |
| **Error Codes** | ❌ No | ❌ No | ✅ Yes |
| **Exception Handlers** | ❌ No | ❌ No | ✅ Yes |
| **Health Checks** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Production Ready** | ❌ No | ⚠️ Partial | ✅ Yes |

---

## 🚫 Do Not Use

### main.py Issues

```python
# Line 60 - IN-MEMORY STORAGE (NOT PRODUCTION-READY)
campaigns_db = {}  # ❌ Data lost on restart!

# No authentication
# No database
# No rate limiting
```

### Why It's Deprecated

1. **Data Loss**: All data lost on restart
2. **No Security**: No authentication or authorization
3. **No Scalability**: Can't scale horizontally
4. **No Persistence**: Can't recover from crashes
5. **Not Production-Ready**: Missing critical features

---

## ✅ Recommended Action

**Immediately switch to `main_v3.py` for all deployments!**

### Quick Switch

```bash
# 1. Stop old API
# Ctrl+C to stop

# 2. Initialize database
python scripts/init_database.py
python scripts/init_users.py

# 3. Start new API
uvicorn src.api.main_v3:app --reload

# 4. Test
curl http://localhost:8000/health
```

---

## 📞 Support

### Questions?
- See `ARCHITECTURE_CLEANUP.md` for details
- See `PROJECT_COMPLETE.md` for overview
- See `CURRENT_STATUS.md` for current state

### Issues?
- Check logs: `logs/app.log`
- Run health check: `curl http://localhost:8000/health/detailed`
- Review documentation

---

**Status**: ⚠️ **DO NOT USE DEPRECATED FILES**

Always use `main_v3.py` for production deployments!
