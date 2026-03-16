# Anomaly Detection Feature Design

**Date:** 2026-03-16  
**Author:** Claude  
**Status:** Draft

## 1. Overview

This document describes the design for adding anomaly detection to the Money app. The feature identifies unusual transactions based on statistical analysis of spending patterns within each category.

## 2. Requirements

### 2.1 Detection Rules

| Level | Condition | Default Threshold |
|-------|-----------|------------------|
| Warning | Amount > 2x category monthly average | 2.0x |
| Anomaly | Amount > 3x category monthly average | 3.0x |
| Alert | Very large single transaction | 10,000 |

### 2.2 Backend Requirements

- Add anomaly detection logic (statistical approach)
- Add anomalies API endpoint
- Mark transactions with anomaly information in list responses
- Support configurable thresholds via settings

### 2.3 Frontend Requirements

- Add AnomalyMarker component to highlight unusual transactions
- Add AnomalyListView or section in Statistics
- Show warning for transactions > 2x category average
- Configurable threshold in settings

## 3. Architecture

### 3.1 Backend Design

```
┌─────────────────────────────────────────────────────────┐
│                      API Layer                          │
│  GET /api/transactions/anomalies    (new endpoint)     │
│  GET /api/transactions/              (enhanced)         │
│  GET /api/anomalies/statistics       (new endpoint)    │
│  PUT /api/settings/anomaly           (new endpoint)     │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   Service Layer                         │
│              AnomalyDetector Service                    │
│  - calculate_category_average()                         │
│  - detect_anomaly()                                     │
│  - get_transactions_with_anomalies()                   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    Model Layer                          │
│  Transaction (enhanced response with anomaly fields)    │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Frontend Design

```
┌─────────────────────────────────────────────────────────┐
│                      Views                             │
│  - TransactionListView (enhanced with AnomalyMarker)   │
│  - AnomalyListView (new)                               │
│  - StatisticsView (new Anomaly section)               │
│  - SettingsView (threshold configuration)               │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    Components                          │
│  - AnomalyMarker (new)                                 │
│  - TransactionItem (enhanced)                          │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                     Services                           │
│  - anomaly.service.ts (new)                            │
│  - transactions.service.ts (enhanced)                  │
└─────────────────────────────────────────────────────────┘
```

## 4. API Specification

### 4.1 Enhanced Transaction Response

```python
class TransactionAnomalyInfo(BaseModel):
    anomaly_level: Optional[str] = None  # "warning" | "anomaly" | "alert" | None
    category_monthly_average: Optional[Decimal] = None
    anomaly_reason: Optional[str] = None

class TransactionResponse(TransactionBase):
    id: int
    created_at: datetime
    anomaly_info: Optional[TransactionAnomalyInfo] = None
```

### 4.2 New Endpoints

#### GET /api/transactions/anomalies

Returns all transactions with anomaly detection applied.

**Query Parameters:**
- `start_date`: Optional date filter
- `end_date`: Optional date filter
- `level`: Filter by anomaly level ("warning", "anomaly", "alert")

**Response:**
```json
{
  "items": [...],
  "total": 100,
  "statistics": {
    "warning_count": 50,
    "anomaly_count": 20,
    "alert_count": 5,
    "total_amount_anomalous": 50000
  }
}
```

#### GET /api/anomalies/statistics

Returns anomaly statistics for dashboard.

#### PUT /api/settings/anomaly

Update anomaly thresholds.

**Request:**
```json
{
  "warning_threshold": 2.0,
  "anomaly_threshold": 3.0,
  "large_transaction_threshold": 10000
}
```

## 5. Database Schema Changes

No database schema changes required. Anomaly detection is computed on-the-fly using existing transaction data.

## 6. Implementation Plan

### Phase 1: Backend
1. Create `AnomalyDetector` service class
2. Add anomaly detection logic to transaction service
3. Add new API endpoints
4. Update transaction response schema

### Phase 2: Frontend
1. Create `AnomalyMarker` component
2. Update `TransactionItem` to show markers
3. Create `AnomalyListView`
4. Add anomaly section to `StatisticsView`
5. Add threshold configuration to `SettingsView`

## 7. Configuration

Default thresholds (stored in settings):

| Setting | Default | Description |
|---------|---------|-------------|
| warning_threshold | 2.0 | Multiplier for warning level |
| anomaly_threshold | 3.0 | Multiplier for anomaly level |
| large_transaction_threshold | 10000 | Absolute threshold for alert |

## 8. Acceptance Criteria

1. ✅ Transactions > 2x category monthly average show warning marker
2. ✅ Transactions > 3x category monthly average show anomaly marker  
3. ✅ Transactions > 10000 show alert marker
4. ✅ AnomalyListView shows all anomalous transactions
5. ✅ Statistics shows anomaly overview
6. ✅ Thresholds are configurable in settings
7. ✅ Anomaly detection works correctly for both expense and income transactions

## 9. Edge Cases

1. **No historical data:** If category has no previous transactions, skip anomaly detection
2. **Single transaction:** If only one transaction exists, use that as average (triggers all as anomaly - should be handled)
3. **Zero average:** If category average is 0, treat as no anomaly
4. **New category:** Newly created categories have no average - skip detection
5. **Mixed income/expense:** Only analyze expenses for anomaly (income typically varies more)
