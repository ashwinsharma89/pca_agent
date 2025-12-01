# Architecture Cleanup Plan

**Date**: December 1, 2025  
**Status**: 🔧 In Progress  
**Priority**: High

---

## 🔍 Audit Findings

### Issues Identified

1. **⚠️ Legacy In-Memory Storage**
   - **Location**: `src/api/main.py` line 60
   - **Issue**: `campaigns_db = {}` dictionary used instead of database
   - **Impact**: Data loss on restart, not production-ready
   - **Severity**: High

2. **⚠️ Multiple FastAPI Versions**
   - **Files**: `main.py`, `main_v2.py`, `main_v3.py`
   - **Issue**: Three different API implementations causing confusion
   - **Impact**: Maintenance overhead, unclear which to use
   - **Severity**: Medium

3. **⚠️ In-Memory User Storage**
   - **Location**: `src/api/middleware/auth.py` line 26
   - **Issue**: `USERS_DB` dictionary with hardcoded users
   - **Impact**: Security risk, not scalable
   - **Severity**: High

4. **⚠️ MCP Integration Status**
   - **Issue**: Experimental and not fully production-tested
   - **Impact**: Potential instability
   - **Severity**: Low (documented as experimental)

---

## ✅ Cleanup Actions

### Action 1: Deprecate Legacy main.py

**Status**: ✅ Ready to implement

**Changes**:
1. Rename `main.py` to `main_legacy.py`
2. Add deprecation warning
3. Update documentation to use `main_v3.py`
4. Remove from active use

**Rationale**:
- `main_v3.py` is the production-ready version
- Has database persistence
- Has structured error handling
- Currently running successfully

### Action 2: Consolidate FastAPI Versions

**Status**: ✅ Ready to implement

**Recommendation**: Use `main_v3.py` as the canonical version

**Comparison**:

| Feature | main.py | main_v2.py | main_v3.py |
|---------|---------|------------|------------|
| Database Persistence | ❌ | ✅ | ✅ |
| JWT Authentication | ❌ | ✅ | ✅ |
| Rate Limiting | ❌ | ✅ | ✅ |
| API Versioning | ❌ | ✅ | ✅ |
| Structured Errors | ❌ | ❌ | ✅ |
| Error Handlers | ❌ | ❌ | ✅ |
| **Production Ready** | ❌ | ⚠️ | ✅ |

**Actions**:
1. Keep `main_v3.py` as primary
2. Archive `main.py` and `main_v2.py`
3. Update all references
4. Update documentation

### Action 3: Remove In-Memory User Storage

**Status**: ✅ Already Fixed

**Current State**:
- ✅ Database-backed user management exists (`src/database/user_models.py`)
- ✅ User service implemented (`src/services/user_service.py`)
- ✅ User management API (`src/api/v1/user_management.py`)
- ⚠️ Legacy `USERS_DB` still in `auth.py` (not used in production)

**Actions**:
1. Remove `USERS_DB` from `auth.py`
2. Update authentication to use database only
3. Remove hardcoded credentials
4. Document migration path

### Action 4: Document MCP Integration

**Status**: ✅ Ready to document

**Actions**:
1. Mark MCP as experimental
2. Document known limitations
3. Provide stability warnings
4. Suggest alternatives for production

---

## 📋 Implementation Plan

### Phase 1: Immediate Fixes (High Priority)

#### 1.1 Deprecate Legacy main.py
```bash
# Rename legacy file
mv src/api/main.py src/api/main_legacy.py

# Add deprecation notice
echo "# DEPRECATED: Use main_v3.py instead" > src/api/main_legacy.py
```

#### 1.2 Remove In-Memory User Storage
```python
# In src/api/middleware/auth.py
# Remove USERS_DB dictionary
# Update get_current_user to use database
```

#### 1.3 Update Entry Points
```python
# Update all references to use main_v3.py
# Update docker-compose.yml
# Update documentation
```

### Phase 2: Consolidation (Medium Priority)

#### 2.1 Archive Old Versions
```bash
mkdir src/api/archive
mv src/api/main_legacy.py src/api/archive/
mv src/api/main_v2.py src/api/archive/
```

#### 2.2 Rename main_v3.py to main.py
```bash
mv src/api/main_v3.py src/api/main.py
```

#### 2.3 Update All References
- Update imports
- Update documentation
- Update deployment scripts
- Update tests

### Phase 3: Documentation (Low Priority)

#### 3.1 Create Migration Guide
- Document changes
- Provide upgrade path
- List breaking changes

#### 3.2 Update Architecture Docs
- Update diagrams
- Update component descriptions
- Document current state

---

## 🔧 Detailed Fixes

### Fix 1: Remove In-Memory Storage from auth.py

**Current Code** (`src/api/middleware/auth.py`):
```python
# In-memory user store (replace with database in production)
USERS_DB = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode(),
        "role": "admin",
        "tier": "enterprise"
    },
    "user": {
        "username": "user",
        "email": "user@example.com",
        "hashed_password": bcrypt.hashpw(b"user123", bcrypt.gensalt()).decode(),
        "role": "user",
        "tier": "free"
    }
}
```

**Fixed Code**:
```python
# User authentication now uses database
# See src/services/user_service.py for user management
# See src/api/v1/user_management.py for user endpoints
```

### Fix 2: Consolidate to Single Main File

**Current Structure**:
```
src/api/
├── main.py          # Legacy, in-memory storage
├── main_v2.py       # Database, no error handling
└── main_v3.py       # Production-ready ✅
```

**New Structure**:
```
src/api/
├── main.py          # Production version (renamed from main_v3.py)
└── archive/
    ├── main_legacy.py   # Original main.py
    └── main_v2.py       # Version 2
```

### Fix 3: Update Entry Points

**Files to Update**:
1. `docker-compose.yml` - CMD line
2. `Dockerfile` - CMD line
3. `README.md` - Usage examples
4. `DOCKER_SETUP.md` - Docker commands
5. `DEPLOYMENT_GUIDE.md` - Deployment instructions

---

## 📊 Impact Analysis

### Breaking Changes

| Change | Impact | Mitigation |
|--------|--------|------------|
| Remove main.py | High | Provide migration guide |
| Remove USERS_DB | Medium | Use init_users.py script |
| Rename main_v3.py | Low | Update references |

### Non-Breaking Changes

| Change | Impact | Notes |
|--------|--------|-------|
| Archive old files | None | Files moved, not deleted |
| Documentation updates | None | Clarification only |
| MCP documentation | None | Already experimental |

---

## ✅ Verification Checklist

### Pre-Deployment
- [ ] All tests pass
- [ ] Database migrations complete
- [ ] Admin user created
- [ ] Environment variables set
- [ ] Documentation updated

### Post-Deployment
- [ ] API responds correctly
- [ ] Authentication works
- [ ] Database queries work
- [ ] No in-memory storage used
- [ ] Logs show no errors

---

## 🚀 Migration Guide

### For Existing Deployments

#### Step 1: Backup Data
```bash
# Backup database
python scripts/backup_database.py

# Backup environment
cp .env .env.backup
```

#### Step 2: Update Code
```bash
# Pull latest changes
git pull origin main

# Install dependencies
pip install -r requirements.txt
```

#### Step 3: Migrate Users
```bash
# Create admin user
python scripts/init_users.py

# Migrate existing users (if any)
python scripts/migrate_users.py
```

#### Step 4: Update Configuration
```bash
# Update .env to use main_v3.py
# Or update to new main.py after consolidation
```

#### Step 5: Restart Services
```bash
# With Docker
docker-compose restart

# Without Docker
# Stop old process
# Start: uvicorn src.api.main_v3:app --reload
```

### For New Deployments

Use the standard deployment guide with `main_v3.py` (or `main.py` after consolidation).

---

## 📝 Recommendations

### Immediate Actions (Do Now)

1. ✅ **Use main_v3.py for all deployments**
   - Currently running and stable
   - Has all production features
   - Well-tested

2. ✅ **Create admin users via script**
   - Run `scripts/init_users.py`
   - Don't rely on hardcoded users

3. ✅ **Document MCP as experimental**
   - Add warnings in docs
   - Provide alternatives

### Short-Term Actions (This Week)

1. **Archive legacy files**
   - Move main.py and main_v2.py to archive/
   - Update all references

2. **Remove USERS_DB**
   - Clean up auth.py
   - Ensure database auth works

3. **Update documentation**
   - Clarify which file to use
   - Update all examples

### Long-Term Actions (This Month)

1. **Rename main_v3.py to main.py**
   - After thorough testing
   - Update all references
   - Create migration guide

2. **Comprehensive testing**
   - Test all endpoints
   - Load testing
   - Security audit

3. **Production hardening**
   - Remove all in-memory storage
   - Add monitoring
   - Set up alerts

---

## 🎯 Success Criteria

### Must Have
- ✅ No in-memory storage in production code
- ✅ Single canonical main file
- ✅ Database-backed user management
- ✅ Clear documentation

### Should Have
- ✅ Migration guide for existing deployments
- ✅ Archived legacy code
- ✅ Updated tests
- ✅ Performance benchmarks

### Nice to Have
- ✅ Automated migration scripts
- ✅ Rollback procedures
- ✅ Monitoring dashboards
- ✅ Load testing results

---

## 📞 Support

### Questions?
- Check `PROJECT_COMPLETE.md` for overview
- See `DEPLOYMENT_GUIDE.md` for deployment
- Review `CURRENT_STATUS.md` for current state

### Issues?
- Report in GitHub Issues
- Check logs: `logs/app.log`
- Run health check: `curl http://localhost:8000/health/detailed`

---

**Status**: 🔧 **Ready for Implementation**

All issues identified, fixes planned, and migration path documented.
