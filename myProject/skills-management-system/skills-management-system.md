# Skills Management System Design Document

## Overview

A comprehensive skills management system for Claude Code that handles skill discovery, usage tracking, similarity detection, and automated maintenance.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Skills Management System                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │   Skill      │  │   Usage      │  │ Similarity   │  │    ROI &     │ │
│  │  Registry    │  │   Tracker    │  │   Engine     │  │ Quantification│ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘ │
│         │                  │                  │                  │         │
│         └──────────────────┼──────────────────┼──────────────────┘         │
│                            │                  │                            │
│                    ┌───────▼──────────────────▼────────┐                   │
│                    │         Core Engine              │                   │
│                    └───────┬───────────────────────────┘                   │
│                            │                                               │
│         ┌──────────────────┼──────────────────┐                            │
│         │                  │                  │                            │
│  ┌──────▼──────┐  ┌───────▼───────┐  ┌──────▼──────┐  ┌───────────────┐  │
│  │   CLI       │  │   Reporter    │  │   Cleanup   │  │  Automated    │  │
│  │  Interface  │  │   Generator   │  │   Wizard    │  │  Analytics    │  │
│  └─────────────┘  └───────────────┘  └─────────────┘  └───────────────┘  │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

## File Structure

```
~/.claude/
├── skills-management/
│   ├── core/
│   │   ├── skill_registry.py      # Registry management
│   │   ├── usage_tracker.py       # Usage statistics (enhanced with time tracking)
│   │   ├── similarity_engine.py   # Similarity detection
│   │   ├── roi_calculator.py      # ROI calculation engine
│   │   └── config.py              # Configuration
│   ├── cli/
│   │   ├── main.py                # CLI entry point
│   │   ├── commands.py            # Command handlers
│   │   └── utils.py               # CLI utilities
│   ├── reporters/
│   │   ├── report_generator.py    # Report generation (includes ROI reports)
│   │   └── templates/
│   │       ├── weekly_report.md
│   │       ├── cleanup_report.md
│   │       └── roi_report.md
│   ├── cleanup/
│   │   ├── cleanup_wizard.py      # Interactive cleanup
│   │   └── impact_analyzer.py     # Impact assessment
│   ├── analytics/
│   │   ├── time_tracker.py        # Automatic time tracking
│   │   ├── baseline_manager.py    # Baseline establishment
│   │   ├── benefit_calculator.py  # Benefit quantification
│   │   ├── cost_tracker.py        # Cost tracking
│   │   └── dashboard.py           # Analytics dashboard
│   ├── data/
│   │   ├── skills_registry.yaml   # Skills index
│   │   ├── skills_usage.yaml      # Usage statistics
│   │   ├── time_logs.jsonl        # Time tracking logs
│   │   ├── costs.jsonl            # Cost tracking logs
│   │   ├── baseline.json          # Baseline measurements
│   │   ├── skills_config.yaml     # System config
│   │   └── similarity_cache.json  # Cached similarity scores
│   ├── reports/
│   │   ├── weekly/                # Weekly reports
│   │   ├── monthly/               # Monthly reports
│   │   └── roi/                   # ROI reports
│   └── scripts/
│       ├── sync_skills.py         # Sync registry
│       ├── calculate_similarity.py # Batch similarity
│       ├── scheduled_tasks.py     # Automation
│       └── analytics_pipeline.py  # Automated analytics
│
├── plugins/
│   ├── local/
│   │   └── skills/
│   │       └── skills-manager/
│   │           └── SKILL.md       # Manager skill itself
│   └── marketplaces/
│       └── claude-plugins-official/
│
└── settings.json                  # Claude Code settings
```

## Core Components

### 1. Skill Registry

**Purpose**: Central index of all skills with metadata

**Schema**:
```yaml
# data/skills_registry.yaml
version: "1.0"
last_updated: "2026-05-04T15:30:00Z"
skills:
  frontend-design:
    name: frontend-design
    display_name: Frontend Design
    description: Create production-grade frontend interfaces
    path: ~/.claude/plugins/marketplaces/claude-plugins-official/plugins/frontend-design/skills/frontend-design/SKILL.md
    type: official  # official | custom
    tags:
      - frontend
      - ui
      - css
      - react
    tech_stack:
      - html
      - css
      - javascript
    scenarios:
      - web-dev
      - component-design
    complexity: high
    created: "2026-04-01T10:00:00Z"
    last_modified: "2026-05-01T14:20:00Z"
    version: "1.2.0"
    dependencies: []
    deprecated: false
    replacement: null  # If deprecated, what to use instead
```

**API**:
```python
class SkillRegistry:
    def add_skill(self, skill_path: str) -> bool
    def remove_skill(self, skill_name: str) -> bool
    def get_skill(self, skill_name: str) -> Optional[Dict]
    def list_skills(self, filters: Dict = None) -> List[Dict]
    def search_skills(self, query: str) -> List[Dict]
    def update_skill(self, skill_name: str, metadata: Dict) -> bool
    def sync(self) -> int  # Returns number of changes
    def validate(self) -> List[str]  # Returns validation errors
```

### 2. Usage Tracker

**Purpose**: Track skill usage patterns and statistics

**Schema**:
```yaml
# data/skills_usage.yaml
version: "1.0"
last_updated: "2026-05-04T15:30:00Z"
skills:
  frontend-design:
    usage_count: 23
    last_used: "2026-05-04T15:30:00Z"
    first_used: "2026-04-15T10:00:00Z"
    avg_success_rate: 0.95
    user_satisfaction: high
    outcomes:
      - timestamp: "2026-05-04T15:30:00Z"
        outcome: success
        duration_ms: 2500
      - timestamp: "2026-05-03T14:20:00Z"
        outcome: success
        duration_ms: 1800
    usage_by_day:
      "2026-05-04": 3
      "2026-05-03": 2
    usage_trend: increasing  # increasing | stable | decreasing
```

**API**:
```python
class UsageTracker:
    def log_usage(self, skill_name: str, outcome: str, duration_ms: int) -> None
    def get_stats(self, skill_name: str) -> Dict
    def get_top_skills(self, limit: int = 10) -> List[Dict]
    def get_unused_skills(self, days: int = 90) -> List[Dict]
    def get_underperforming_skills(self, success_threshold: float = 0.7) -> List[Dict]
    def calculate_trend(self, skill_name: str) -> str
    def export_report(self, period: str = "week") -> str
```

### 3. Similarity Engine

**Purpose**: Detect similar skills to suggest consolidation

**Algorithm**:
```python
def calculate_similarity(skill1: Dict, skill2: Dict) -> float:
    """
    Calculate similarity score between two skills (0.0 - 1.0)

    Weights:
    - Name similarity: 30%
    - Description similarity: 40%
    - Tag overlap: 20%
    - Content similarity: 10%
    """
    name_sim = SequenceMatcher(None,
        skill1['name'], skill2['name']).ratio() * 0.3

    desc_sim = SequenceMatcher(None,
        skill1['description'], skill2['description']).ratio() * 0.4

    tags1 = set(skill1.get('tags', []))
    tags2 = set(skill2.get('tags', []))
    tag_overlap = len(tags1 & tags2) / len(tags1 | tags2) * 0.2

    content_sim = calculate_tfidf_similarity(
        skill1['content'], skill2['content']) * 0.1

    return name_sim + desc_sim + tag_overlap + content_sim
```

**API**:
```python
class SimilarityEngine:
    def calculate_similarity(self, skill1: str, skill2: str) -> float
    def find_similar_skills(self, skill_name: str, threshold: float = 0.7) -> List[Tuple]
    def find_all_similar_groups(self, threshold: float = 0.7) -> List[List[str]]
    def compare_skills(self, skill1: str, skill2: str) -> Dict
    def cache_similarity_matrix(self) -> None
    def get_similarity_matrix(self) -> Dict
```

### 4. ROI Calculator & Quantification Engine

**Purpose**: Calculate ROI and track quantifiable metrics to validate system effectiveness

**Key Features**:
- Automatic time tracking for all skill interactions
- Baseline establishment for before/after comparison
- Cost tracking (development, maintenance, infrastructure)
- Benefit calculation (time savings, success rate improvements)
- ROI calculation and projection
- Automated reporting

**Time Tracking Integration**:
```python
class TimeTracker:
    """
    Automatically track time for all skill interactions
    Integrated into UsageTracker for seamless operation
    """
    def start_timer(self, activity_type: str, metadata: Dict) -> str
    def stop_timer(self, timer_id: str, outcome: str) -> float
    def get_time_stats(self, period_days: int) -> Dict
```

**Baseline Management**:
```python
class BaselineManager:
    """
    Establish and maintain baseline measurements
    """
    def establish_baseline(self, days_to_collect: int) -> Dict
    def get_baseline(self) -> Dict
    def compare_with_baseline(self, current_stats: Dict) -> Dict
```

**Cost Tracking**:
```python
class CostTracker:
    """
    Track all costs associated with SMS
    """
    def log_development_time(self, hours: float, hourly_rate: float, task: str)
    def log_infrastructure_cost(self, amount: float, description: str)
    def log_maintenance_time(self, hours: float, hourly_rate: float, task: str)
    def get_monthly_costs(self, month: int) -> Dict
```

**Benefit Calculation**:
```python
class BenefitCalculator:
    """
    Calculate monetary benefits from SMS usage
    """
    def calculate_time_savings(self, period_days: int) -> Dict
    def calculate_success_rate_benefit(self, period_days: int) -> Dict
    def calculate_discovery_improvement_benefit(self, period_days: int) -> Dict
    def calculate_all_benefits(self, period_days: int) -> Dict
```

**ROI Calculation**:
```python
class ROICalculator:
    """
    Main ROI calculation engine
    """
    def calculate_monthly_roi(self, month: int) -> Dict
    def generate_roi_report(self, month: int) -> str
    def calculate_projected_roi(self, months_ahead: int) -> List[Dict]
    def calculate_payback_period(self) -> int
```

**Enhanced UsageTracker Integration**:
```python
class UsageTracker:
    """
    Enhanced with automatic time tracking
    """
    def __init__(self):
        self.time_tracker = TimeTracker()
        self.active_timers = {}

    def log_usage(self, skill_name: str, outcome: str, duration_ms: int):
        # Log usage with automatic time tracking
        timer_id = self.active_timers.get(skill_name)
        if timer_id:
            self.time_tracker.stop_timer(timer_id, outcome)

    def start_skill_execution(self, skill_name: str, discovery_method: str):
        # Start tracking automatically
        timer_id = self.time_tracker.start_timer(
            "skill_execution",
            metadata={
                'skill_name': skill_name,
                'discovery_method': discovery_method
            }
        )
        self.active_timers[skill_name] = timer_id
        return timer_id
```

**ROI Metrics**:
```yaml
# Monthly ROI calculation example
costs:
  development: $5,000     # Amortized development cost
  infrastructure: $200    # Server/storage costs
  maintenance: $1,000    # Ongoing maintenance
  total: $6,200

benefits:
  time_savings: $8,333          # (45s → 15s) × hourly_rate
  success_rate: $3,750          # Reduced rework time
  discovery_improvement: $2,083 # Faster discovery
  total: $14,166

roi:
  net_benefit: $7,966
  roi_percentage: 128.5%
  payback_period_days: 13
  daily_benefit: $472
```

### 5. Reporter

**Purpose**: Generate health and usage reports

**Report Types**:
1. **Weekly Usage Report**
   - Top performing skills
   - Unused skills alert
   - Usage trends
   - Success rates

2. **Cleanup Report**
   - Unused skills (>90 days)
   - Similar skill groups
   - Underperforming skills
   - Impact assessment

3. **Comparison Report**
   - Side-by-side skill comparison
   - Usage statistics
   - Feature overlap
   - Recommendations

**API**:
```python
class Reporter:
    def generate_weekly_report(self) -> str
    def generate_cleanup_report(self) -> str
    def generate_comparison_report(self, skill1: str, skill2: str) -> str
    def generate_impact_report(self, skill_name: str) -> str
    def save_report(self, report: str, path: str) -> None
```

### 5. Cleanup Wizard

**Purpose**: Interactive tool for skill maintenance

**Workflow**:
1. Scan for issues (unused, similar, underperforming)
2. Present issues to user
3. Provide recommendations
4. Execute cleanup actions
5. Archive removed skills

**API**:
```python
class CleanupWizard:
    def scan_issues(self) -> Dict
    def assess_impact(self, skill_name: str) -> Dict
    def suggest_action(self, skill_name: str) -> str
    def remove_skill(self, skill_name: str, archive: bool = True) -> bool
    def merge_skills(self, source: str, target: str) -> bool
    def archive_skill(self, skill_name: str) -> bool
    def unarchive_skill(self, skill_name: str) -> bool
```

## CLI Interface

### Main Command

```bash
skills <command> [options]
```

### Available Commands

```bash
# Registry Management
skills sync                              # Sync registry with disk
skills list                              # List all skills
skills info <skill-name>                 # Show skill details
skills search <query>                    # Search skills
skills create <name>                     # Create new skill
skills edit <skill-name>                 # Edit skill
skills remove <skill-name>               # Remove skill

# Usage Statistics
skills stats                             # Show overall statistics
skills stats <skill-name>                # Show skill statistics

# ROI & Quantification
skills roi report                        # Generate ROI report
skills roi baseline                      # Establish baseline measurements
skills roi log-cost                      # Log development/maintenance costs
skills roi project                       # Show ROI projections
skills roi dashboard                     # Show analytics dashboard

# Reports
skills report                            # Generate weekly report
skills report --cleanup                  # Generate cleanup report
skills report --output <path>            # Save report to file

# Similarity Analysis
skills find-similar                      # Find all similar skills
skills compare <skill1> <skill2>         # Compare two skills

# Cleanup
skills cleanup                           # Interactive cleanup wizard
skills review unused                     # Review unused skills
skills review similar                    # Review similar skills
skills review underperforming            # Review low-success skills

# Maintenance
skills archive <skill-name>              # Archive a skill
skills merge <source> into <target>      # Merge skills

# Scheduling
skills schedule report                   # Schedule automated reports
skills schedule list                     # List scheduled tasks
```

### Example Usage

```bash
# Create a new skill
$ skills create my-tool --desc "My custom tool" --tags utility
✓ Created at ~/.claude/plugins/local/skills/my-tool/SKILL.md
✓ Registered in skills registry

# Check statistics
$ skills stats frontend-design
Frontend Design Statistics:
  Usage: 23 times
  Last used: 2026-05-04 15:30
  Success rate: 95%
  Trend: ↗️ Increasing

# Find similar skills
$ skills find-similar --threshold 0.8
Found 3 similar skill groups:
  1. /test-runner, /pytest-helper (85% similar)
  2. /commit, /git-helper (78% similar)
  3. /code-review, /pr-review (82% similar)

# Interactive cleanup
$ skills cleanup
🧹 Skills Cleanup Wizard

Found 8 unused skills and 3 similar skill groups.

[1/3] Review unused skills
  ○ old-deploy-tool (last used: 90 days ago)
    > [Keep]  [Remove]  [Archive]
```

## Integration with Claude Code

### Settings Configuration

```json
{
  "hooks": {
    "sessionStart": [
      {
        "command": "skills sync",
        "description": "Sync skills registry on session start"
      }
    ],
    "skillInvoke": [
      {
        "command": "skills log-usage --invoke {skill_name}",
        "description": "Log skill invocation"
      }
    ],
    "skillComplete": [
      {
        "command": "skills log-usage --complete {skill_name} --outcome {outcome}",
        "description": "Log skill completion"
      }
    ]
  },
  "scheduled_tasks": {
    "skills-weekly-report": {
      "cron": "0 9 * * 0",
      "prompt": "skills report --output ~/.claude/reports/weekly-{{date}}.md",
      "durable": true
    },
    "skills-monthly-cleanup": {
      "cron": "0 10 1 * *",
      "prompt": "skills cleanup-check --notify",
      "durable": true
    }
  }
}
```

### Skill: skills-manager

```markdown
---
name: skills-manager
description: Manage and discover available skills. Use /skills to list, search, and maintain skills.
tags: [management, utility, maintenance]
---

When user invokes /skills:

1. Parse subcommand (list, search, stats, cleanup, etc.)
2. Execute corresponding skills-management CLI command
3. Format output for display
4. Provide recommendations if applicable

## Usage Examples
- `/skills` - Show all skills grouped by category
- `/skills search <keyword>` - Search skills
- `/skills stats` - Show usage statistics
- `/skills cleanup` - Start cleanup wizard
```

## Implementation Plan

### Phase 1: Core Infrastructure (Week 1)
- [ ] Set up project structure
- [ ] Implement SkillRegistry class
- [ ] Implement UsageTracker class
- [ ] Create YAML schema definitions
- [ ] Set up configuration system

### Phase 2: CLI Interface (Week 1-2)
- [ ] Implement main CLI entry point
- [ ] Implement registry commands (list, info, search)
- [ ] Implement usage commands (stats)
- [ ] Implement create/edit/remove commands
- [ ] Add command-line argument parsing

### Phase 3: Similarity Engine (Week 2)
- [ ] Implement similarity calculation algorithm
- [ ] Implement TF-IDF content comparison
- [ ] Create similarity matrix caching
- [ ] Implement find-similar command
- [ ] Implement compare command

### Phase 4: Reporting System (Week 2-3)
- [ ] Implement Reporter class
- [ ] Create report templates
- [ ] Implement weekly report generation
- [ ] Implement cleanup report generation
- [ ] Add report export functionality

### Phase 4.5: Quantification & ROI System (Week 3)
- [ ] Implement TimeTracker class (automatic time tracking)
- [ ] Implement BaselineManager class
- [ ] Implement CostTracker class
- [ ] Implement BenefitCalculator class
- [ ] Implement ROICalculator class
- [ ] Implement AnalyticsDashboard class
- [ ] Create ROI report templates
- [ ] Integrate time tracking into UsageTracker
- [ ] Add ROI CLI commands

### Phase 5: Cleanup System (Week 3)
- [ ] Implement CleanupWizard class
- [ ] Implement impact assessment
- [ ] Create interactive cleanup interface
- [ ] Implement archive/unarchive functionality
- [ ] Implement merge functionality

### Phase 6: Integration (Week 3-4)
- [ ] Create skills-manager skill
- [ ] Integrate with Claude Code hooks
- [ ] Set up scheduled tasks
- [ ] Add notification system
- [ ] Test end-to-end workflow

### Phase 7: Testing & Documentation (Week 4)
- [ ] Unit tests for all components
- [ ] Integration tests
- [ ] User documentation
- [ ] API documentation
- [ ] Performance optimization

## Dependencies

```python
# requirements.txt
pyyaml>=6.0
click>=8.0
scikit-learn>=1.0
rich>=13.0  # For beautiful CLI output
questionary>=2.0  # For interactive prompts
croniter>=1.3  # For cron scheduling

# Quantification & ROI
numpy>=1.21.0  # Statistical calculations
scipy>=1.7.0  # Statistical significance testing
apscheduler>=3.9.0  # Automated scheduling and reporting
pandas>=1.3.0  # Data analysis and reporting
plotly>=5.0.0  # Interactive charts for reports
```

## Configuration

```yaml
# data/skills_config.yaml
system:
  registry_path: ~/.claude/skills-management/data/skills_registry.yaml
  usage_path: ~/.claude/skills-management/data/skills_usage.yaml
  similarity_threshold: 0.7
  unused_threshold_days: 90
  underperforming_threshold: 0.7

# ROI & Quantification Configuration
roi:
  enabled: true
  hourly_rate: 50  # USD per hour (configurable per user)
  baseline_period_days: 14  # Days to collect baseline data
  measurement_period_days: 30  # Period for ROI calculations
  auto_track_time: true  # Automatically track all skill interactions

  # Cost tracking
  development_cost_amortization_months: 12  # Spread dev cost over 12 months

  # Benefit calculation weights
  benefit_weights:
    time_saved: 1.0
    success_rate_improvement: 1.5
    discovery_improvement: 0.8
    quality_improvement: 1.2

  # Reporting
  roi_report_frequency: monthly  # weekly | monthly | quarterly
  include_projections: true
  projection_months: 12

cleanup:
  auto_archive: true
  archive_path: ~/.claude/skills-management/archive/
  backup_before_removal: true

reporting:
  output_path: ~/.claude/reports/
  weekly_report_day: sunday
  monthly_cleanup_day: 1
  include_charts: true
  include_roi_metrics: true  # Add ROI metrics to all reports

similarity:
  cache_enabled: true
  cache_duration_hours: 168  # 1 week
  weights:
    name: 0.3
    description: 0.4
    tags: 0.2
    content: 0.1
```

## Performance Considerations

1. **Similarity Calculation**: O(n²) complexity, use caching
2. **Registry Sync**: Incremental updates only
3. **Usage Logging**: Async writes to avoid blocking
4. **Report Generation**: Template caching

## Security Considerations

1. **Skill Validation**: Validate skill metadata before registration
2. **Path Sanitization**: Prevent path traversal attacks
3. **Permission Checks**: Verify write permissions before modifications
4. **Backup Strategy**: Always backup before removing skills

## Future Enhancements

1. **Skill Marketplace**: Share and discover community skills
2. **AI-Powered Recommendations**: ML-based skill suggestions
3. **Visual Analytics**: Web-based dashboard for skill metrics
4. **Dependency Resolution**: Automatic dependency management
5. **Version Control Integration**: Git-based skill versioning
6. **Collaborative Filtering**: "Users who used X also used Y"

## Success Metrics

### System Performance Metrics
- Reduction in unused skills: Target 50% reduction in 3 months
- Improved skill discovery: 80% of skills found within 10 seconds
- Higher success rates: 90%+ average skill success rate
- User satisfaction: Regular feedback surveys

### ROI & Quantification Metrics
- **Time Savings**: 50% reduction in average search time within 4 weeks
- **ROI Target**: >100% ROI within 3 months
- **Payback Period**: <30 days to break even on development costs
- **Success Rate Improvement**: 15% improvement in skill success rate
- **Task Completion Time**: 30% reduction in average task completion time

### Validation Metrics
- **Statistical Significance**: p < 0.05 for all key improvements
- **Data Accuracy**: >99% accuracy in time tracking
- **User Adoption**: >70% of users actively using ROI features
- **Report Engagement**: >60% of generated reports are viewed

### Automated Validation
- **Daily Checks**: System health, data quality, error rates
- **Weekly Reports**: Usage trends, engagement metrics
- **Monthly Analysis**: Statistical significance, ROI calculation
- **Quarterly Reviews**: Comprehensive system validation

---

**Document Version**: 1.1
**Last Updated**: 2026-05-04
**Author**: Claude Code
**Status**: Design Phase (Enhanced with Quantification & ROI)

## Part 8: Quantification & ROI Integration Details

### 8.1 Automatic Time Tracking Flow

```
User invokes skill
    ↓
UsageTracker.start_skill_execution()
    ↓
TimeTracker.start_timer("skill_execution", metadata={...})
    ↓
[Skill executes]
    ↓
UsageTracker.log_usage(skill_name, outcome, duration)
    ↓
TimeTracker.stop_timer(timer_id, outcome)
    ↓
Data saved to time_logs.jsonl
    ↓
Used for ROI calculation
```

### 8.2 Complete ROI Workflow

```bash
# Setup Phase
skills config set roi.hourly_rate 75
skills roi baseline --days 14

# Implementation Phase
skills roi log-cost --hours 80 --rate 75 --task "Core SMS development"

# Operation Phase (automatic tracking)
skills search frontend  # Time tracked automatically
skills roi report --monthly
skills roi project --months 12
skills roi dashboard
```

### 8.3 Key Integration Points

| Component | Integration Method | Data Flow |
|-----------|-------------------|-----------|
| **UsageTracker** | Automatic time tracking | → TimeTracker → ROI Calculator |
| **Skill Registry** | Metadata for similarity | → Similarity Engine → ROI (quality) |
| **Cleanup Wizard** | Impact assessment | ROI Calculator → Recommendations |
| **Reporter** | All reports include ROI | ROI Calculator → Templates |
| **CLI** | New `skills roi` commands | Direct access to ROI |

---

**Document Version**: 1.1 (Enhanced with Quantification & ROI)
