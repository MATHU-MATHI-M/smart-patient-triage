# Main Backend Queue Routing - Issues & Fixes

## 🔴 PROBLEMS IDENTIFIED

### Problem 1: Flawed Local Fallback Logic
**Location:** `run_ml_engine()` function

**Issue:** Uses basic keyword matching instead of comprehensive medical rules:
```python
# WRONG - Too simplistic
if any(k in history_text for k in ["heart", "cardiac", ...]):
    dept_scores["Cardiology"] += 0.3
```

**Why it fails:**
- Doesn't analyze symptom severity
- Doesn't combine multiple factors
- Keyword matching is unreliable
- Scores are too low (0.3 max)

### Problem 2: API Timeout Too Short
**Location:** External ML API call

```python
ml_response = await client.post(
    "https://ml-backend-engine-kanini.onrender.com/api/v1/process_visit",
    json={"visit_id": visit_id},
    timeout=5.0  # ❌ TOO SHORT for cold start
)
```

**Why it fails:**
- Render free tier has cold starts (10-30 seconds)
- 5 second timeout causes immediate fallback to local logic
- Local logic is wrong → incorrect queues

---

## ✅ FIXES REQUIRED

### Fix 1: Increase API Timeout
```python
timeout=30.0  # Allow for cold start
```

### Fix 2: Remove/Fix Local Fallback
**Option A (Recommended):** Return error if API fails
```python
except Exception as e:
    raise HTTPException(
        status_code=503, 
        detail="ML Engine unavailable. Please try again."
    )
```

**Option B:** Use proper rule-based logic in fallback (copy from your ML backend)

### Fix 3: Verify API Response Structure
The external API returns:
```json
{
  "primary_department": "Cardiology",
  "department_scores": {...}
}
```

But local fallback returns:
```json
{
  "recommended_department": "Cardiology",  // Different key!
  "department_scores": {...}
}
```

**Fix:** Standardize to `primary_department`

---

## 📋 CORRECTED CODE

See `main_backend_fixed.py` for complete corrected version.

**Key Changes:**
1. ✅ Increased timeout to 30 seconds
2. ✅ Removed flawed local fallback
3. ✅ Standardized response keys
4. ✅ Better error handling
5. ✅ Proper multi-queue routing (already correct)
