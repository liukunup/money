# Anomaly Detection Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement statistical anomaly detection for transactions with configurable thresholds, showing warnings/anomalies/alerts based on category monthly averages.

**Architecture:** On-the-fly computation using existing transaction data. No database schema changes required. Anomaly detection calculated when transactions are fetched, with results added to response.

**Tech Stack:** 
- Backend: FastAPI, SQLAlchemy, Pydantic
- Frontend: Vue 3, TypeScript, Pinia

---

## Task 1: Create AnomalyDetector Service (Backend)

**Files:**
- Create: `app/services/anomaly_detection.py`
- Test: `tests/services/test_anomaly_detection.py`

**Step 1: Write the failing test**

```python
# tests/services/test_anomaly_detection.py
import pytest
from decimal import Decimal
from app.services.anomaly_detection import AnomalyDetector

def test_detect_warning_level():
    """Transaction > 2x average should be warning"""
    detector = AnomalyDetector(
        warning_threshold=2.0,
        anomaly_threshold=3.0,
        large_transaction_threshold=10000
    )
    # amount=200, average=100 -> 2x = warning
    result = detector.detect(Decimal("200"), Decimal("100"), Decimal("5000"))
    assert result["level"] == "warning"

def test_detect_anomaly_level():
    """Transaction > 3x average should be anomaly"""
    detector = AnomalyDetector()
    # amount=400, average=100 -> 4x = anomaly
    result = detector.detect(Decimal("400"), Decimal("100"), Decimal("5000"))
    assert result["level"] == "anomaly"

def test_detect_alert_level():
    """Transaction > large_transaction_threshold should always be alert"""
    detector = AnomalyDetector()
    # amount=15000 > 10000 = alert
    result = detector.detect(Decimal("15000"), Decimal("100"), Decimal("15000"))
    assert result["level"] == "alert"

def test_no_anomaly():
    """Transaction within normal range should be normal"""
    detector = AnomalyDetector()
    # amount=100, average=100 -> 1x = normal
    result = detector.detect(Decimal("100"), Decimal("100"), Decimal("100"))
    assert result["level"] is None
```

**Step 2: Run test to verify it fails**

```bash
cd /Users/liukunup/Documents/repo/money
python -m pytest tests/services/test_anomaly_detection.py -v
```
Expected: FAIL with "ModuleNotFoundError: No module named 'app.services.anomaly_detection'"

**Step 3: Write minimal implementation**

```python
# app/services/anomaly_detection.py
from decimal import Decimal
from typing import Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.transaction import Transaction


class AnomalyDetector:
    """Service for detecting anomalous transactions."""
    
    def __init__(
        self,
        warning_threshold: float = 2.0,
        anomaly_threshold: float = 3.0,
        large_transaction_threshold: float = 10000.0
    ):
        self.warning_threshold = warning_threshold
        self.anomaly_threshold = anomaly_threshold
        self.large_transaction_threshold = large_transaction_threshold
    
    def detect(
        self,
        amount: Decimal,
        category_average: Decimal,
        absolute_amount: Decimal
    ) -> Dict[str, Any]:
        """
        Detect anomaly level for a transaction.
        
        Returns dict with:
        - level: "warning" | "anomaly" | "alert" | None
        - reason: explanation string
        """
        # Check absolute threshold first (alert)
        if absolute_amount >= Decimal(str(self.large_transaction_threshold)):
            return {
                "level": "alert",
                "reason": f"Large transaction: {absolute_amount} >= {self.large_transaction_threshold}"
            }
        
        # Check category-based thresholds (only for expenses)
        if category_average and category_average > 0:
            ratio = amount / category_average
            
            if ratio >= Decimal(str(self.anomaly_threshold)):
                return {
                    "level": "anomaly",
                    "reason": f"Amount {amount} is {ratio:.1f}x category average ({category_average})"
                }
            elif ratio >= Decimal(str(self.warning_threshold)):
                return {
                    "level": "warning",
                    "reason": f"Amount {amount} is {ratio:.1f}x category average ({category_average})"
                }
        
        return {"level": None, "reason": None}
    
    def calculate_category_average(
        self,
        db: Session,
        category_id: int,
        transaction_date: date,
        transaction_type: str = "expense"
    ) -> Optional[Decimal]:
        """
        Calculate monthly average for a category based on historical data.
        Uses all months except the current month.
        """
        from datetime import datetime
        
        # Get year and month of the transaction
        year = transaction_date.year
        month = transaction_date.month
        
        # Query for all transactions in this category, same type, 
        # excluding the current month
        query = db.query(func.avg(Transaction.amount)).filter(
            Transaction.category_id == category_id,
            Transaction.type == transaction_type,
            Transaction.is_deleted == False
        )
        
        # Exclude current month
        query = query.filter(
            ~(
                (func.extract('year', Transaction.date) == year) &
                (func.extract('month', Transaction.date) == month)
            )
        )
        
        result = query.scalar()
        return Decimal(str(result)) if result else None
```

**Step 4: Run test to verify it passes**

```bash
cd /Users/liukunup/Documents/repo/money
python -m pytest tests/services/test_anomaly_detection.py -v
```
Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add app/services/anomaly_detection.py tests/services/test_anomaly_detection.py
git commit -m "feat: add AnomalyDetector service"
```

---

## Task 2: Add Anomaly Info to Transaction Schema

**Files:**
- Modify: `app/schemas/transaction.py`
- Modify: `app/models/transaction.py`

**Step 1: Add anomaly info schema**

```python
# app/schemas/transaction.py - add these imports and class
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

class TransactionAnomalyInfo(BaseModel):
    """Anomaly detection information for a transaction."""
    anomaly_level: Optional[str] = Field(None, description="warning | anomaly | alert | None")
    category_monthly_average: Optional[Decimal] = Field(None, description="Monthly average for category")
    anomaly_reason: Optional[str] = Field(None, description="Human-readable reason")

class TransactionResponse(BaseModel):
    id: int
    amount: Decimal
    type: str
    category_id: int
    date: date
    note: Optional[str] = None
    created_at: datetime
    anomaly_info: Optional[TransactionAnomalyInfo] = None
    
    model_config = ConfigDict(from_attributes=True)
```

**Step 2: Run type check**

```bash
cd /Users/liukunup/Documents/repo/money
python -m py_compile app/schemas/transaction.py
```
Expected: No errors

**Step 3: Commit**

```bash
git add app/schemas/transaction.py
git commit -m "feat: add TransactionAnomalyInfo to transaction schema"
```

---

## Task 3: Add Anomaly API Endpoints

**Files:**
- Create: `app/api/anomalies.py`
- Modify: `app/main.py`

**Step 1: Create anomalies API**

```python
# app/api/anomalies.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from app.db.database import get_db
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionResponse, TransactionAnomalyInfo
from app.services.anomaly_detection import AnomalyDetector

router = APIRouter()

@router.get("/transactions/anomalies")
def get_anomalous_transactions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    level: Optional[str] = Query(None, regex="^(warning|anomaly|alert)$"),
    db: Session = Depends(get_db)
):
    """Get all transactions with anomaly detection applied."""
    
    detector = AnomalyDetector()
    
    # Build base query
    query = db.query(Transaction).filter(
        Transaction.is_deleted == False,
        Transaction.type == "expense"
    )
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    transactions = query.order_by(Transaction.date.desc()).all()
    
    results = []
    stats = {"warning": 0, "anomaly": 0, "alert": 0, "total_amount": Decimal("0")}
    
    for t in transactions:
        # Calculate category average
        category_avg = detector.calculate_category_average(
            db, t.category_id, t.date, t.type
        )
        
        # Detect anomaly
        anomaly = detector.detect(t.amount, category_avg or Decimal("0"), t.amount)
        
        # Filter by level if requested
        if level and anomaly["level"] != level:
            continue
        
        # Add to results
        if anomaly["level"]:
            stats[anomaly["level"]] += 1
            stats["total_amount"] += t.amount
        
        results.append({
            **{
                "id": t.id,
                "amount": t.amount,
                "type": t.type,
                "category_id": t.category_id,
                "date": t.date,
                "note": t.note,
                "created_at": t.created_at,
            },
            "anomaly_info": TransactionAnomalyInfo(
                anomaly_level=anomaly["level"],
                category_monthly_average=category_avg,
                anomaly_reason=anomaly["reason"]
            )
        })
    
    return {
        "items": results,
        "total": len(results),
        "statistics": stats
    }

@router.get("/anomalies/statistics")
def get_anomaly_statistics(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2020),
    db: Session = Depends(get_db)
):
    """Get anomaly statistics."""
    
    detector = AnomalyDetector()
    
    query = db.query(Transaction).filter(
        Transaction.is_deleted == False,
        Transaction.type == "expense"
    )
    
    if month and year:
        from datetime import date
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
        query = query.filter(Transaction.date >= start_date, Transaction.date < end_date)
    
    transactions = query.all()
    
    stats = {"warning": 0, "anomaly": 0, "alert": 0, "normal": 0}
    
    for t in transactions:
        category_avg = detector.calculate_category_average(db, t.category_id, t.date, t.type)
        anomaly = detector.detect(t.amount, category_avg or Decimal("0"), t.amount)
        
        if anomaly["level"]:
            stats[anomaly["level"]] += 1
        else:
            stats["normal"] += 1
    
    return stats
```

**Step 2: Register router in main.py**

```python
# app/main.py - add to existing imports
from app.api import anomalies

# Add to app.include_router section
app.include_router(anomalies.router, prefix="/api", tags=["anomalies"])
```

**Step 3: Test the endpoint**

```bash
cd /Users/liukunup/Documents/repo/money
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
sleep 3
curl http://localhost:8000/api/anomalies/statistics
```
Expected: JSON with statistics

**Step 4: Commit**

```bash
git add app/api/anomalies.py app/main.py
git commit -m "feat: add anomaly detection API endpoints"
```

---

## Task 4: Add Settings API for Threshold Configuration

**Files:**
- Create: `app/api/settings.py`
- Modify: `app/main.py`

**Step 1: Create settings API**

```python
# app/api/settings.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# In-memory settings (for MVP - could be stored in DB later)
class AnomalySettings(BaseModel):
    warning_threshold: float = 2.0
    anomaly_threshold: float = 3.0
    large_transaction_threshold: float = 10000.0

anomaly_settings = AnomalySettings()

@router.get("/settings/anomaly", response_model=AnomalySettings)
def get_anomaly_settings():
    """Get current anomaly detection settings."""
    return anomaly_settings

@router.put("/settings/anomaly", response_model=AnomalySettings)
def update_anomaly_settings(settings: AnomalySettings):
    """Update anomaly detection settings."""
    global anomaly_settings
    anomaly_settings = settings
    return anomaly_settings
```

**Step 2: Register router**

```python
# app/main.py
from app.api import settings
app.include_router(settings.router, prefix="/api", tags=["settings"])
```

**Step 3: Commit**

```bash
git add app/api/settings.py app/main.py
git commit -m "feat: add anomaly settings API"
```

---

## Task 5: Create Frontend AnomalyMarker Component

**Files:**
- Create: `webui/src/components/anomaly/AnomalyMarker.vue`
- Modify: `webui/src/components/transaction/TransactionItem.vue`

**Step 1: Create AnomalyMarker component**

```vue
<!-- webui/src/components/anomaly/AnomalyMarker.vue -->
<script setup lang="ts">
interface Props {
  level: 'warning' | 'anomaly' | 'alert';
  reason?: string;
}

const props = defineProps<Props>();

const levelConfig = {
  warning: {
    icon: '⚠️',
    color: '#FF9500',
    bgColor: 'rgba(255, 149, 0, 0.1)',
    label: 'Warning'
  },
  anomaly: {
    icon: '🔴',
    color: '#FF3B30',
    bgColor: 'rgba(255, 59, 48, 0.1)',
    label: 'Anomaly'
  },
  alert: {
    icon: '🚨',
    color: '#AF52DE',
    bgColor: 'rgba(175, 82, 222, 0.1)',
    label: 'Alert'
  }
};

const config = computed(() => levelConfig[props.level]);
</script>

<template>
  <div 
    class="anomaly-marker"
    :style="{ 
      color: config.color,
      backgroundColor: config.bgColor 
    }"
    :title="reason || config.label"
  >
    <span class="anomaly-marker__icon">{{ config.icon }}</span>
    <span class="anomaly-marker__label">{{ config.label }}</span>
  </div>
</template>

<style scoped>
.anomaly-marker {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.anomaly-marker__icon {
  font-size: 10px;
}

.anomaly-marker__label {
  text-transform: uppercase;
}
</style>
```

**Step 2: Update TransactionItem to use AnomalyMarker**

```vue
<!-- webui/src/components/transaction/TransactionItem.vue -->
<script setup lang="ts">
// Add import
import AnomalyMarker from '@/components/anomaly/AnomalyMarker.vue';

// In the template, add after the amount div:
// <AnomalyMarker 
//   v-if="transaction.anomaly_info?.anomaly_level"
//   :level="transaction.anomaly_info.anomaly_level"
//   :reason="transaction.anomaly_info.anomaly_reason"
// />
</script>
```

**Step 3: Commit**

```bash
git add webui/src/components/anomaly/AnomalyMarker.vue webui/src/components/transaction/TransactionItem.vue
git commit -m "feat: add AnomalyMarker component"
```

---

## Task 6: Create AnomalyListView

**Files:**
- Create: `webui/src/views/AnomalyListView.vue`

**Step 1: Create the view**

```vue
<!-- webui/src/views/AnomalyListView.vue -->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import Card from '@/components/ui/Card.vue';
import Button from '@/components/ui/Button.vue';
import AnomalyMarker from '@/components/anomaly/AnomalyMarker.vue';
import { useTransactionsStore } from '@/stores/transactions';

const { t } = useI18n();
const transactionsStore = useTransactionsStore();

const filterLevel = ref<string>('all');

onMounted(async () => {
  await transactionsStore.fetchAnomalies();
});

const filteredTransactions = computed(() => {
  if (filterLevel.value === 'all') {
    return transactionsStore.anomalies;
  }
  return transactionsStore.anomalies.filter(
    t => t.anomaly_info?.anomaly_level === filterLevel.value
  );
});

const statistics = computed(() => transactionsStore.anomalyStatistics);
</script>

<template>
  <div class="anomaly-list-view">
    <header class="header">
      <h1>{{ t('anomaly.title') }}</h1>
      <p class="subtitle">{{ t('anomaly.subtitle') }}</p>
    </header>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <Card variant="elevated" class="stat-card warning">
        <div class="stat-icon">⚠️</div>
        <div class="stat-value">{{ statistics.warning }}</div>
        <div class="stat-label">{{ t('anomaly.warning') }}</div>
      </Card>
      <Card variant="elevated" class="stat-card anomaly">
        <div class="stat-icon">🔴</div>
        <div class="stat-value">{{ statistics.anomaly }}</div>
        <div class="stat-label">{{ t('anomaly.anomaly') }}</div>
      </Card>
      <Card variant="elevated" class="stat-card alert">
        <div class="stat-icon">🚨</div>
        <div class="stat-value">{{ statistics.alert }}</div>
        <div class="stat-label">{{ t('anomaly.alert') }}</div>
      </Card>
    </div>

    <!-- Filter -->
    <div class="filter-bar">
      <select v-model="filterLevel" class="filter-select">
        <option value="all">{{ t('anomaly.all') }}</option>
        <option value="warning">{{ t('anomaly.warning') }}</option>
        <option value="anomaly">{{ t('anomaly.anomaly') }}</option>
        <option value="alert">{{ t('anomaly.alert') }}</option>
      </select>
    </div>

    <!-- Transaction List -->
    <div class="transaction-list">
      <div 
        v-for="transaction in filteredTransactions" 
        :key="transaction.id"
        class="transaction-row"
      >
        <div class="transaction-info">
          <div class="transaction-amount">
            -{{ transaction.amount }}
          </div>
          <div class="transaction-note">
            {{ transaction.note || 'Unknown' }}
          </div>
          <div class="transaction-date">
            {{ transaction.date }}
          </div>
        </div>
        <AnomalyMarker 
          v-if="transaction.anomaly_info?.anomaly_level"
          :level="transaction.anomaly_info.anomaly_level"
          :reason="transaction.anomaly_info.anomaly_reason"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.anomaly-list-view {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.header {
  margin-bottom: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
  padding: 20px;
}

.stat-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
}

.stat-label {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.filter-bar {
  margin-bottom: 16px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid var(--color-separator);
  border-radius: 8px;
  font-size: 14px;
}

.transaction-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.transaction-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--color-surface-primary);
  border-radius: 12px;
}

.transaction-amount {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-expense);
}

.transaction-note {
  font-size: 14px;
  color: var(--color-text-primary);
}

.transaction-date {
  font-size: 12px;
  color: var(--color-text-secondary);
}
</style>
```

**Step 2: Add route**

```typescript
// webui/src/router/index.ts - add route
{
  path: '/anomalies',
  name: 'anomalies',
  component: () => import('@/views/AnomalyListView.vue')
}
```

**Step 3: Commit**

```bash
git add webui/src/views/AnomalyListView.vue webui/src/router/index.ts
git commit -m "feat: add AnomalyListView"
```

---

## Task 7: Update Transactions Store

**Files:**
- Modify: `webui/src/stores/transactions.ts`

**Step 1: Add anomaly methods to store**

```typescript
// In webui/src/stores/transactions.ts
// Add these to the store

async fetchAnomalies(filters?: {
  start_date?: string;
  end_date?: string;
  level?: string;
}) {
  this.loading = true;
  try {
    const params = new URLSearchParams();
    if (filters?.start_date) params.append('start_date', filters.start_date);
    if (filters?.end_date) params.append('end_date', filters.end_date);
    if (filters?.level) params.append('level', filters.level);
    
    const response = await fetch(`/api/transactions/anomalies?${params}`);
    const data = await response.json();
    
    this.anomalies = data.items;
    this.anomalyStatistics = data.statistics;
  } catch (error) {
    console.error('Failed to fetch anomalies:', error);
  } finally {
    this.loading = false;
  }
}

// Add to state
anomalies: Transaction[] = [];
anomalyStatistics: { warning: number; anomaly: number; alert: number; normal: number; total_amount: number } = {
  warning: 0,
  anomaly: 0,
  alert: 0,
  normal: 0,
  total_amount: 0
};
```

**Step 2: Commit**

```bash
git add webui/src/stores/transactions.ts
git commit -m "feat: add anomaly methods to transactions store"
```

---

## Task 8: Add Anomaly Section to StatisticsView

**Files:**
- Modify: `webui/src/views/StatisticsView.vue`

**Step 1: Add anomaly statistics section**

```vue
<!-- In StatisticsView.vue, add after the summary-stats section -->

<section v-if="!transactionsStore.loading" class="anomaly-section">
  <h2 class="section-title">{{ t('anomaly.title') }}</h2>
  <div class="anomaly-stats-grid">
    <div class="anomaly-stat-card warning">
      <div class="anomaly-stat-icon">⚠️</div>
      <div class="anomaly-stat-value">{{ anomalyStats.warning }}</div>
      <div class="anomaly-stat-label">{{ t('anomaly.warningCount') }}</div>
    </div>
    <div class="anomaly-stat-card anomaly">
      <div class="anomaly-stat-icon">🔴</div>
      <div class="anomaly-stat-value">{{ anomalyStats.anomaly }}</div>
      <div class="anomaly-stat-label">{{ t('anomaly.anomalyCount') }}</div>
    </div>
    <div class="anomaly-stat-card alert">
      <div class="anomaly-stat-icon">🚨</div>
      <div class="anomaly-stat-value">{{ anomalyStats.alert }}</div>
      <div class="anomaly-stat-label">{{ t('anomaly.alertCount') }}</div>
    </div>
  </div>
  <Button variant="secondary" @click="$router.push('/anomalies')">
    {{ t('anomaly.viewAll') }}
  </Button>
</section>
```

**Step 2: Add script logic**

```typescript
// In the script section
const anomalyStats = computed(() => {
  return {
    warning: transactionsStore.anomalyStatistics?.warning || 0,
    anomaly: transactionsStore.anomalyStatistics?.anomaly || 0,
    alert: transactionsStore.anomalyStatistics?.alert || 0
  };
});

// In onMounted, add:
transactionsStore.fetchAnomalies();
```

**Step 3: Add styles**

```css
/* Add these styles */
.anomaly-section {
  margin-top: 24px;
  padding: 20px;
  background: var(--color-surface-primary);
  border-radius: 16px;
}

.anomaly-stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.anomaly-stat-card {
  text-align: center;
  padding: 16px;
  border-radius: 12px;
}

.anomaly-stat-card.warning {
  background: rgba(255, 149, 0, 0.1);
}

.anomaly-stat-card.anomaly {
  background: rgba(255, 59, 48, 0.1);
}

.anomaly-stat-card.alert {
  background: rgba(175, 82, 222, 0.1);
}

.anomaly-stat-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.anomaly-stat-value {
  font-size: 28px;
  font-weight: 700;
}

.anomaly-stat-label {
  font-size: 12px;
  color: var(--color-text-secondary);
}
```

**Step 4: Commit**

```bash
git add webui/src/views/StatisticsView.vue
git commit -m "feat: add anomaly section to StatisticsView"
```

---

## Task 9: Add Threshold Settings to SettingsView

**Files:**
- Modify: `webui/src/views/SettingsView.vue`

**Step 1: Add threshold configuration UI**

```vue
<!-- In SettingsView.vue, add a new section -->

<section class="settings-section">
  <h2 class="section-title">{{ t('anomaly.settings') }}</h2>
  
  <div class="setting-item">
    <label>{{ t('anomaly.warningThreshold') }}</label>
    <input 
      type="number" 
      v-model.number="anomalySettings.warning_threshold"
      min="1"
      max="10"
      step="0.5"
    />
    <span class="setting-hint">{{ t('anomaly.warningThresholdHint') }}</span>
  </div>
  
  <div class="setting-item">
    <label>{{ t('anomaly.anomalyThreshold') }}</label>
    <input 
      type="number" 
      v-model.number="anomalySettings.anomaly_threshold"
      min="1"
      max="20"
      step="0.5"
    />
    <span class="setting-hint">{{ t('anomaly.anomalyThresholdHint') }}</span>
  </div>
  
  <div class="setting-item">
    <label>{{ t('anomaly.largeTransactionThreshold') }}</label>
    <input 
      type="number" 
      v-model.number="anomalySettings.large_transaction_threshold"
      min="100"
      max="100000"
      step="1000"
    />
    <span class="setting-hint">{{ t('anomaly.largeTransactionThresholdHint') }}</span>
  </div>
  
  <Button @click="saveAnomalySettings">
    {{ t('common.save') }}
  </Button>
</section>
```

**Step 2: Add script logic**

```typescript
// Add to script
const anomalySettings = ref({
  warning_threshold: 2.0,
  anomaly_threshold: 3.0,
  large_transaction_threshold: 10000
});

async function loadAnomalySettings() {
  try {
    const response = await fetch('/api/settings/anomaly');
    const data = await response.json();
    anomalySettings.value = data;
  } catch (error) {
    console.error('Failed to load anomaly settings:', error);
  }
}

async function saveAnomalySettings() {
  try {
    const response = await fetch('/api/settings/anomaly', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(anomalySettings.value)
    });
    alert('Settings saved!');
  } catch (error) {
    console.error('Failed to save anomaly settings:', error);
  }
}

onMounted(() => {
  loadAnomalySettings();
});
```

**Step 3: Commit**

```bash
git add webui/src/views/SettingsView.vue
git commit -m "feat: add anomaly threshold settings"
```

---

## Task 10: Add i18n Translations

**Files:**
- Modify: `webui/src/i18n/locales/zh-CN.json`
- Modify: `webui/src/i18n/locales/en-US.json`

**Step 1: Add translations**

```json
// In zh-CN.json
{
  "anomaly": {
    "title": "异常交易",
    "subtitle": "检测到的不正常交易记录",
    "warning": "警告",
    "anomaly": "异常",
    "alert": "alert",
    "all": "全部",
    "warningCount": "警告次数",
    "anomalyCount": "异常次数",
    "alertCount": "alert次数",
    "viewAll": "查看全部",
    "settings": "异常检测设置",
    "warningThreshold": "警告阈值",
    "warningThresholdHint": "当交易金额超过分类月均值的多少倍时显示警告",
    "anomalyThreshold": "异常阈值",
    "anomalyThresholdHint": "当交易金额超过分类月均值的多少倍时标记为异常",
    "largeTransactionThreshold": "大额交易阈值",
    "largeTransactionThresholdHint": "超过此金额的交易将被标记为alert"
  }
}
```

**Step 2: Commit**

```bash
git add webui/src/i18n/locales/zh-CN.json webui/src/i18n/locales/en-US.json
git commit -m "feat: add anomaly i18n translations"
```

---

## Summary

**Total Tasks:** 10

**Backend Tasks:** 4
1. AnomalyDetector service
2. Transaction schema enhancement
3. Anomaly API endpoints
4. Settings API

**Frontend Tasks:** 6
5. AnomalyMarker component
6. AnomalyListView
7. Transactions store update
8. StatisticsView enhancement
9. SettingsView threshold config
10. i18n translations

**Plan complete and saved to `docs/plans/2026-03-16-anomaly-detection-implementation.md`.** Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?
