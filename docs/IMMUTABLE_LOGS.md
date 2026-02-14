# Immutable Logs & Hash Chaining Guide

> **Why this exists:** To mathematically prove that no one (not even a database admin) has deleted or modified an audit log entry.
> **Concept:** This is a simplified "blockchain" (Merkle Chain) stored in a relational database.

---

## 1. The Concept

In a standard log table, rows are independent.
Row A: `User logged in`
Row B: `User viewed payroll`

If I delete Row B, Row A and Row C generally don't care.

In **Sentinel**, every row depends on the row before it.
Row B's hash includes Row A's hash.
Row C's hash includes Row B's hash.

**Formula:**
`Current_Hash = SHA256( Previous_Hash + Timestamp + Actor + Action + Resource )`

If you change Row A, its hash changes.
This invalidates Row B's `Previous_Hash` check.
This invalidates Row C... and the whole chain breaks.

---

## 2. The Implementation Logic

### Step 1: Genesis Block (The First Log)
When a Tenant is created, we insert a "Genesis Log".
- `prev_hash`: "00000000000000000000000000000000" (32 zeros)
- `curr_hash`: SHA256(...)

### Step 2: Inserting a New Log
1.  **Lock** the table (or use serializable isolation) to get the *latest* log for this `org_id`.
2.  Read the `curr_hash` of that latest log.
3.  Set that value as the `prev_hash` for the new log.
4.  Calculate the new `curr_hash`.
5.  Insert.

---

## 3. How to Debug & Verify (The Guide)

You asked: *"Teach me or provide me guide for debugging."*

### Scenario: The "Tamper" Test
You suspect a DB admin deleted a log entry between ID `100` and `102`.

**Manual Verification Script (Pseudo-code):**

```python
def verify_chain(logs):
    for i in range(1, len(logs)):
        previous_log = logs[i-1]
        current_log = logs[i]
        
        # 1. Check Linkage
        if current_log.prev_hash != previous_log.curr_hash:
            print(f"🚨 BROKEN CHAIN DETECTED at ID {current_log.id}!")
            print(f"Expected prev_hash: {previous_log.curr_hash}")
            print(f"Found prev_hash:    {current_log.prev_hash}")
            return False
            
        # 2. Check Integrity (Did someone edit the data in place?)
        recalculated_hash = sha256(
            current_log.prev_hash + 
            current_log.timestamp + 
            current_log.actor + 
            ...
        )
        
        if recalculated_hash != current_log.curr_hash:
             print(f"🚨 DATA TAMPERING DETECTED at ID {current_log.id}!")
             return False
             
    print("✅ Chain is valid.")
    return True
```

### Visual Debugging in SQL
If you look at the DB, you should see the chain visually:

| ID | Action | Prev_Hash | Curr_Hash |
| :--- | :--- | :--- | :--- |
| 1 | Init | `0000...` | `abc123...` |
| 2 | Login | `abc123...` | `def456...` |
| 3 | View | `def456...` | `ghi789...` |

**The Bug:**
If Row 2 is deleted:
Row 3's `prev_hash` is `def456...`
But Row 1's `curr_hash` is `abc123...`
**Mismatch!** The gap is detected.

---

## 4. Concurrency Challenges (The Hard Part)

**Problem:** Two users generate logs at the exact same millisecond.
They both read the same "latest" hash.
They both try to insert with the same `prev_hash`.
This forks the chain (bad).

**Solution:**
1.  **Optimistic Locking:** The database constraint `UNIQUE(org_id, prev_hash)` prevents forks.
2.  **Retries:** If the insert fails because the `prev_hash` was already used (someone beat us to it), we:
    - Read the *new* latest hash.
    - Re-calculate.
    - Retry.

This ensures strict ordering even under load.

---

## 5. Archival Strategy

We can't keep logs in Postgres forever.
When we move logs to S3 (Cold Storage), we verify the chain **one last time**, zip it, and sign the zip file.
The last hash of the archived batch becomes the `prev_hash` for the first log of the new active batch.
