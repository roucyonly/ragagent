# Skills Management System - Data Retention & Archival Policy

## Overview

**Strategy**: Keep all data, but only process recent 2 months in memory

**Benefits**:
- ✅ Fast startup (only load 2 months)
- ✅ Low memory footprint
- ✅ Complete historical data available
- ✅ On-demand access to old data
- ✅ Efficient long-term analytics

## Data Architecture

### Data Temperature Model

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Lifecycle                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  🔥 HOT DATA (0-2 months)                                   │
│     - Loaded in memory on startup                          │
│     - Real-time updates                                     │
│     - Fast queries (< 1ms)                                  │
│     - Size: ~1-2 MB                                         │
│                                                               │
│  ♨️ WARM DATA (2-6 months)                                 │
│     - Archived to separate files                           │
│     - Loaded on demand                                     │
│     - Queries take ~50-100ms                                │
│     - Size: ~2-3 MB                                         │
│                                                               │
│  ❄️ COLD DATA (6+ months)                                  │
│     - Compressed archives                                  │
│     - Loaded only for historical analysis                  │
│     - Queries take ~200-500ms                               │
│     - Size: ~5+ MB (cumulative)                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## File Structure

```
~/.claude/skills-management/
├── data/
│   ├── hot/                             # Active data (0-2 months)
│   │   ├── skills_registry.yaml
│   │   ├── skills_usage.yaml
│   │   └── time_logs.jsonl
│   │
│   ├── warm/                            # Warm data (2-6 months)
│   │   ├── 2026-03/
│   │   │   ├── skills_usage.yaml
│   │   │   └── time_logs.jsonl
│   │   └── 2026-04/
│   │       ├── skills_usage.yaml
│   │       └── time_logs.jsonl
│   │
│   ├── cold/                            # Cold data (6+ months)
│   │   ├── 2026-01.tar.gz              # Compressed
│   │   ├── 2026-02.tar.gz
│   │   └── archive_index.yaml          # Index of all archives
│   │
│   └── config.yaml                      # Data retention config
│
└── archive/
    └── exports/                         # Optional: Export for analysis
        ├── quarterly_reports/
        └── yearly_summaries/
```

## Configuration

```yaml
# data/config.yaml
data_retention:
  # Hot data: Always in memory
  hot_period_months: 2

  # Warm data: Archived, accessible on demand
  warm_period_months: 6

  # Cold data: Compressed, accessible for analysis
  compress_after_months: 6

  # Automatic archival
  auto_archive: true
  archive_check_frequency: daily  # Check daily for data to archive

  # Compression
  compression_method: gzip
  compression_level: 9

  # Archive cleanup (optional)
  delete_after_years: 5  # Never delete if set to null

# Performance tuning
performance:
  preload_archives: false  # Don't preload warm data
  cache_warm_queries: true  # Cache results from warm data
  max_memory_mb: 10  # Maximum memory for hot data
```

## Implementation

### 1. Data Manager

```python
# ~/.claude/skills-management/core/data_manager.py

import os
import json
import gzip
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

class DataManager:
    """
    Manage hot/warm/cold data with automatic archival
    """

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.hot_data = {}  # In-memory hot data
        self.warm_cache = {}  # Cache for warm data
        self._load_hot_data()
        self._check_archival()  # Check if data needs archiving

    def _load_hot_data(self):
        """Load only recent 2 months into memory"""
        hot_dir = Path(self.config['data_dir']) / 'hot'

        # Load registry (always needed)
        self.hot_data['registry'] = self._load_yaml(
            hot_dir / 'skills_registry.yaml'
        )

        # Load recent usage data
        self.hot_data['usage'] = self._load_yaml(
            hot_dir / 'skills_usage.yaml'
        )

        # Load recent time logs
        cutoff_date = datetime.now() - timedelta(days=60)
        self.hot_data['time_logs'] = self._load_jsonl(
            hot_dir / 'time_logs.jsonl',
            after_date=cutoff_date
        )

        print(f"✓ Loaded hot data: ~{self._estimate_size()} MB")

    def _estimate_size(self) -> float:
        """Estimate memory usage of hot data"""
        import sys
        return sum(sys.getsizeof(v) for v in self.hot_data.values()) / (1024 * 1024)

    def query_hot(self, query_type: str, **kwargs) -> List[Dict]:
        """Query hot data (fast, in-memory)"""
        if query_type == 'search':
            return self._search_hot(kwargs['query'])
        elif query_type == 'filter_by_tag':
            return self._filter_by_tag_hot(kwargs['tag'])
        elif query_type == 'recent_usage':
            return self._get_recent_usage(kwargs.get('days', 30))
        else:
            raise ValueError(f"Unknown query type: {query_type}")

    def query_warm(self, query_type: str, **kwargs) -> List[Dict]:
        """Query warm data (slower, loads from disk)"""
        # Check cache first
        cache_key = f"{query_type}_{kwargs}"
        if cache_key in self.warm_cache:
            return self.warm_cache[cache_key]

        # Load warm data on demand
        results = self._load_and_query_warm(query_type, kwargs)

        # Cache results
        if self.config['performance']['cache_warm_queries']:
            self.warm_cache[cache_key] = results

        return results

    def query_cold(self, query_type: str, **kwargs) -> List[Dict]:
        """Query cold data (slowest, decompresses archives)"""
        # Load archive index
        index = self._load_archive_index()

        # Find relevant archives
        relevant_archives = self._find_relevant_archives(kwargs, index)

        # Decompress and query
        results = []
        for archive_path in relevant_archives:
            archive_data = self._decompress_archive(archive_path)
            results.extend(self._query_archive_data(archive_data, query_type, kwargs))

        return results

    def query_all(self, query_type: str, **kwargs) -> Dict:
        """Query all data (hot + warm + cold)"""
        return {
            'hot': self.query_hot(query_type, **kwargs),
            'warm': self.query_warm(query_type, **kwargs),
            'cold': self.query_cold(query_type, **kwargs),
            'summary': self._summarize_results(query_type, kwargs)
        }

    def _check_archival(self):
        """Check if data needs to be archived"""
        if not self.config['data_retention']['auto_archive']:
            return

        last_check = self._get_last_archival_check()
        if self._should_run_archival(last_check):
            self._archive_old_data()

    def _archive_old_data(self):
        """Archive data older than 2 months"""
        hot_dir = Path(self.config['data_dir']) / 'hot'
        warm_dir = Path(self.config['data_dir']) / 'warm'
        cold_dir = Path(self.config['data_dir']) / 'cold'

        cutoff_date = datetime.now() - timedelta(days=60)

        # Archive old time logs
        time_logs = self._load_jsonl(hot_dir / 'time_logs.jsonl')
        hot_logs = []
        warm_logs = []

        for log in time_logs:
            log_date = datetime.fromisoformat(log['timestamp'])
            if log_date < cutoff_date:
                warm_logs.append(log)
            else:
                hot_logs.append(log)

        # Save warm data
        if warm_logs:
            month_str = cutoff_date.strftime('%Y-%m')
            month_dir = warm_dir / month_str
            month_dir.mkdir(parents=True, exist_ok=True)

            self._save_jsonl(month_dir / 'time_logs.jsonl', warm_logs)
            self._save_jsonl(hot_dir / 'time_logs.jsonl', hot_logs)

            print(f"✓ Archived {len(warm_logs)} old logs to {month_dir}/")

        # Compress data older than 6 months
        self._compress_old_archives()

        # Update last check timestamp
        self._update_archival_check()

    def _compress_old_archives(self):
        """Compress archives older than 6 months"""
        warm_dir = Path(self.config['data_dir']) / 'warm'
        cold_dir = Path(self.config['data_dir']) / 'cold'

        cutoff_date = datetime.now() - timedelta(days=180)

        for month_dir in warm_dir.iterdir():
            if not month_dir.is_dir():
                continue

            # Parse month from directory name
            try:
                month_date = datetime.strptime(month_dir.name, '%Y-%m')
            except ValueError:
                continue

            if month_date < cutoff_date:
                # Compress this month
                archive_name = f"{month_dir.name}.tar.gz"
                archive_path = cold_dir / archive_name

                self._create_archive(month_dir, archive_path)
                self._remove_directory(month_dir)

                print(f"✓ Compressed {month_dir.name} to {archive_name}")

    def _load_and_query_warm(self, query_type: str, kwargs: Dict) -> List[Dict]:
        """Load warm data and execute query"""
        warm_dir = Path(self.config['data_dir']) / 'warm'

        results = []
        for month_dir in sorted(warm_dir.iterdir(), reverse=True):
            if not month_dir.is_dir():
                continue

            # Load month's data
            time_logs = self._load_jsonl(month_dir / 'time_logs.jsonl')

            # Query this month
            if query_type == 'search':
                month_results = [log for log in time_logs
                                if kwargs['query'].lower() in str(log).lower()]
            elif query_type == 'usage_by_period':
                month_results = self._filter_by_period(time_logs, kwargs)
            else:
                month_results = time_logs

            results.extend(month_results)

        return results

    def _decompress_archive(self, archive_path: Path) -> Dict:
        """Decompress and load archive"""
        import tarfile

        temp_dir = Path(self.config['data_dir']) / 'temp'
        temp_dir.mkdir(exist_ok=True)

        # Extract
        with tarfile.open(archive_path, 'r:gz') as tar:
            tar.extractall(temp_dir)

        # Load data
        data = {}
        for file_path in temp_dir.iterdir():
            if file_path.suffix == '.yaml':
                data[file_path.stem] = self._load_yaml(file_path)
            elif file_path.suffix == '.jsonl':
                data[file_path.stem] = self._load_jsonl(file_path)

        # Cleanup
        for file_path in temp_dir.iterdir():
            if file_path.is_file():
                file_path.unlink()
        temp_dir.rmdir()

        return data

    # Helper methods
    def _load_yaml(self, path: Path) -> Dict:
        if not path.exists():
            return {}
        with open(path) as f:
            return yaml.safe_load(f) or {}

    def _save_yaml(self, path: Path, data: Dict):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            yaml.dump(data, f)

    def _load_jsonl(self, path: Path, after_date: datetime = None) -> List[Dict]:
        if not path.exists():
            return []

        data = []
        with open(path) as f:
            for line in f:
                record = json.loads(line)
                if after_date:
                    record_date = datetime.fromisoformat(record['timestamp'])
                    if record_date >= after_date:
                        data.append(record)
                else:
                    data.append(record)

        return data

    def _save_jsonl(self, path: Path, data: List[Dict]):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            for record in data:
                f.write(json.dumps(record) + '\n')

    def _search_hot(self, query: str) -> List[Dict]:
        """Search hot data (fast)"""
        results = []
        query_lower = query.lower()

        for skill_name, skill_data in self.hot_data['registry'].items():
            if (query_lower in skill_name.lower() or
                query_lower in skill_data.get('description', '').lower()):
                results.append(skill_data)

        return results

    def _get_recent_usage(self, days: int) -> Dict:
        """Get usage statistics for recent period"""
        cutoff_date = datetime.now() - timedelta(days=days)

        recent_logs = [
            log for log in self.hot_data['time_logs']
            if datetime.fromisoformat(log['timestamp']) >= cutoff_date
        ]

        return {
            'period_days': days,
            'total_invocations': len(recent_logs),
            'by_skill': self._count_by_skill(recent_logs),
            'by_outcome': self._count_by_outcome(recent_logs)
        }

    def _count_by_skill(self, logs: List[Dict]) -> Dict[str, int]:
        counts = {}
        for log in logs:
            skill = log.get('metadata', {}).get('skill_name', 'unknown')
            counts[skill] = counts.get(skill, 0) + 1
        return counts

    def _count_by_outcome(self, logs: List[Dict]) -> Dict[str, int]:
        counts = {}
        for log in logs:
            outcome = log.get('outcome', 'unknown')
            counts[outcome] = counts.get(outcome, 0) + 1
        return counts

    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        stats = {
            'hot': self._get_dir_size(Path(self.config['data_dir']) / 'hot'),
            'warm': self._get_dir_size(Path(self.config['data_dir']) / 'warm'),
            'cold': self._get_dir_size(Path(self.config['data_dir']) / 'cold'),
            'total': 0
        }
        stats['total'] = stats['hot'] + stats['warm'] + stats['cold']
        return stats

    def _get_dir_size(self, path: Path) -> int:
        """Get directory size in bytes"""
        total = 0
        for item in path.rglob('*'):
            if item.is_file():
                total += item.stat().st_size
        return total

    def _get_last_archival_check(self) -> datetime:
        """Get timestamp of last archival check"""
        check_file = Path(self.config['data_dir']) / '.last_archival_check'
        if not check_file.exists():
            return datetime.min

        with open(check_file) as f:
            return datetime.fromisoformat(f.read().strip())

    def _should_run_archival(self, last_check: datetime) -> bool:
        """Check if archival should run"""
        frequency = self.config['data_retention']['archive_check_frequency']
        now = datetime.now()

        if frequency == 'daily':
            return (now - last_check).days >= 1
        elif frequency == 'weekly':
            return (now - last_check).days >= 7
        else:
            return False

    def _update_archival_check(self):
        """Update last archival check timestamp"""
        check_file = Path(self.config['data_dir']) / '.last_archival_check'
        with open(check_file, 'w') as f:
            f.write(datetime.now().isoformat())
```

### 2. Usage Examples

```python
# Initialize data manager
dm = DataManager()

# Query hot data (fast, in-memory)
recent_usage = dm.query_hot('recent_usage', days=30)
print(f"Recent usage: {recent_usage['total_invocations']} invocations")

# Query warm data (slower, loads from disk)
march_usage = dm.query_warm('usage_by_period', month='2026-03')

# Query cold data (slowest, decompresses archives)
historical_usage = dm.query_cold('usage_by_period', year='2025')

# Query all data (combines all sources)
all_usage = dm.query_all('usage_by_period', year='2026')

# Get storage statistics
stats = dm.get_storage_stats()
print(f"Storage: Hot={stats['hot']/1024/1024:.1f}MB, "
      f"Warm={stats['warm']/1024/1024:.1f}MB, "
      f"Cold={stats['cold']/1024/1024:.1f}MB")
```

### 3. CLI Integration

```bash
# Query recent data (default: hot only)
skills stats --period 30d

# Query specific period
skills stats --period 2026-03  # Loads warm data

# Query historical data
skills stats --period 2025-01  # Decompresses cold data

# Query all time
skills stats --period all

# Show storage stats
skills storage stats
# Output:
# Hot data: 1.2 MB (0-2 months)
# Warm data: 2.8 MB (2-6 months)
# Cold data: 5.1 MB (6+ months)
# Total: 9.1 MB

# Manual archival
skills archive run

# Export historical data
skills archive export --period 2025 --format csv
```

### 4. Automatic Archival Schedule

```yaml
# Scheduled in settings.json
{
  "scheduled_tasks": {
    "daily-archive-check": {
      "cron": "0 2 * * *",  # 2 AM daily
      "prompt": "skills archive auto",
      "durable": true
    }
  }
}
```

## Performance Characteristics

### Memory Usage

| State | Memory | Notes |
|-------|--------|-------|
| Startup | ~2 MB | Only hot data loaded |
| Query hot | ~2 MB | No change |
| Query warm | ~5 MB | Temporary spike |
| Query cold | ~10 MB | Temporary spike |
| Steady state | ~2 MB | Returns to baseline |

### Query Performance

| Query Type | Response Time | Notes |
|------------|---------------|-------|
| Hot data | < 1ms | In-memory |
| Warm data | 50-100ms | Disk I/O |
| Cold data | 200-500ms | Decompression |
| All data | 300-600ms | Combined |

### Storage Over Time

```
Month 1:  Hot = 1 MB
Month 2:  Hot = 2 MB
Month 3:  Hot = 1 MB, Warm = 1 MB
Month 4:  Hot = 1 MB, Warm = 2 MB
Month 6:  Hot = 1 MB, Warm = 4 MB
Month 7:  Hot = 1 MB, Warm = 3 MB, Cold = 2 MB
Year 1:  Hot = 1-2 MB, Warm = 4-5 MB, Cold = 8-10 MB
```

## Benefits

### ✅ Fast Startup
- Only load 2 months of data (~2 MB)
- Startup time: ~50ms
- Minimal memory footprint

### ✅ Complete History
- All data preserved indefinitely
- Can query any time period
- Historical analysis available

### ✅ Efficient Storage
- Old data compressed (saves ~70% space)
- Automatic cleanup after 5 years (optional)
- Organized by month for easy management

### ✅ Flexible Queries
- Default: Fast hot data queries
- On-demand: Load warm/cold data as needed
- Caching: Repeated warm queries cached

### ✅ Low Maintenance
- Automatic archival
- No manual intervention needed
- Self-managing storage

## Migration Path

### Existing Data Migration

```bash
# One-time migration script
python migrate_to_archival_system.py

# Output:
# ✓ Organized data into hot/warm/cold
# ✓ Compressed old data
# ✓ Created archive index
# ✓ Migration complete!
```

### Backward Compatibility

```python
# Old code still works
usage_data = load_yaml('skills_usage.yaml')  # Loads hot data by default

# New code can access all data
all_usage = query_all_time('skills_usage.yaml')
```

## Monitoring & Alerts

```bash
# Check archival status
skills archive status

# Output:
# Last archival: 2026-05-04 02:00
# Hot data: 1.2 MB (0-2 months)
# Warm data: 2.8 MB (2-6 months)
# Cold data: 5.1 MB (6+ months)
# Next archival: 2026-05-05 02:00
# Status: ✓ OK

# Storage warnings
skills storage check

# Output:
# ⚠️ Warning: Warm data exceeds 5 MB
# ℹ️ Consider running archival
# Run: skills archive run
```

## Summary

**Strategy**: Keep all data, process only recent 2 months

**Implementation**:
- Hot data (0-2 months): In-memory, fast
- Warm data (2-6 months): Archived, on-demand
- Cold data (6+ months): Compressed, available

**Benefits**:
- ✅ Fast startup (~50ms)
- ✅ Low memory (~2 MB)
- ✅ Complete history
- ✅ Automatic management
- ✅ Efficient storage

**Next**: Implement DataManager class and integrate with existing system

---

**Document Version**: 1.0
**Last Updated**: 2026-05-04
**Author**: Claude Code
**Status**: Data Retention Design
