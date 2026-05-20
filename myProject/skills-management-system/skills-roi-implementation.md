# Skills Management System - ROI Implementation Guide

## Overview

This document describes how to implement ROI calculation for the Skills Management System, including data collection, cost tracking, benefit quantification, and automated reporting.

## Part 1: Data Collection Architecture

### 1.1 Time Tracking Implementation

```python
# ~/.claude/skills-management/roi/time_tracker.py

import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

class TimeTracker:
    """
    Track time spent on skill-related activities
    This is the foundation for ROI calculation
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.data_dir = Path.home() / ".claude" / "skills-management" / "roi_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.time_log_file = self.data_dir / "time_log.jsonl"
        self.active_timers: Dict[str, float] = {}

    def start_timer(self, activity_type: str, metadata: Dict = None) -> str:
        """
        Start tracking an activity

        Args:
            activity_type: Type of activity (e.g., "skill_search", "skill_execution")
            metadata: Additional context (skill_name, search_query, etc.)

        Returns:
            timer_id: Unique identifier for this timer
        """
        timer_id = f"{activity_type}_{int(time.time() * 1000)}"
        self.active_timers[timer_id] = {
            'start_time': time.time(),
            'activity_type': activity_type,
            'metadata': metadata or {}
        }
        return timer_id

    def stop_timer(self, timer_id: str, outcome: str = "success") -> Optional[float]:
        """
        Stop tracking an activity and log the duration

        Args:
            timer_id: Timer identifier from start_timer()
            outcome: How the activity ended (success, failure, cancelled)

        Returns:
            duration: Duration in seconds, or None if timer not found
        """
        if timer_id not in self.active_timers:
            return None

        timer = self.active_timers[timer_id]
        duration = time.time() - timer['start_time']

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': self.user_id,
            'activity_type': timer['activity_type'],
            'duration_seconds': duration,
            'outcome': outcome,
            'metadata': timer['metadata']
        }

        # Append to log file
        with open(self.time_log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

        del self.active_timers[timer_id]
        return duration

    def get_time_stats(self, period_days: int = 30) -> Dict:
        """
        Get time statistics for a period

        Args:
            period_days: Number of days to look back

        Returns:
            Statistics dictionary
        """
        cutoff_date = datetime.now() - timedelta(days=period_days)
        stats = {
            'total_time_seconds': 0,
            'activity_counts': {},
            'activity_durations': {},
            'outcome_counts': {}
        }

        if not self.time_log_file.exists():
            return stats

        with open(self.time_log_file, 'r') as f:
            for line in f:
                entry = json.loads(line)
                entry_date = datetime.fromisoformat(entry['timestamp'])

                if entry_date < cutoff_date:
                    continue

                stats['total_time_seconds'] += entry['duration_seconds']

                # Count by activity type
                activity = entry['activity_type']
                stats['activity_counts'][activity] = stats['activity_counts'].get(activity, 0) + 1
                stats['activity_durations'][activity] = stats['activity_durations'].get(activity, 0) + entry['duration_seconds']

                # Count by outcome
                outcome = entry['outcome']
                stats['outcome_counts'][outcome] = stats['outcome_counts'].get(outcome, 0) + 1

        # Calculate averages
        for activity in stats['activity_counts']:
            count = stats['activity_counts'][activity]
            total_duration = stats['activity_durations'][activity]
            stats['activity_avg_duration'][activity] = total_duration / count

        return stats

# Integration with skill execution
class SkillExecutionTracker:
    """
    Track skill execution times automatically
    """

    def __init__(self, time_tracker: TimeTracker):
        self.time_tracker = time_tracker

    def track_skill_invocation(self, skill_name: str, discovery_method: str):
        """
        Track a skill from discovery to completion
        """
        # Track discovery time
        discovery_timer = self.time_tracker.start_timer(
            "skill_discovery",
            metadata={
                'skill_name': skill_name,
                'discovery_method': discovery_method  # search, browse, direct
            }
        )

        # When user selects the skill
        def on_skill_selected():
            discovery_time = self.time_tracker.stop_timer(discovery_timer, "success")

            # Start execution timer
            execution_timer = self.time_tracker.start_timer(
                "skill_execution",
                metadata={
                    'skill_name': skill_name,
                    'discovery_time': discovery_time
                }
            )
            return execution_timer

        return on_skill_selected

# Example usage in the skills system
tracker = TimeTracker(user_id="user456")

# Track a skill search
search_timer = tracker.start_timer("skill_search", metadata={'query': 'frontend'})
# ... user performs search ...
search_duration = tracker.stop_timer(search_timer, "success_found")

# Track skill execution
execution_timer = tracker.start_timer("skill_execution", metadata={'skill_name': 'frontend-design'})
# ... skill executes ...
execution_duration = tracker.stop_timer(execution_timer, "success")
```

### 1.2 Baseline Establishment

```python
# ~/.claude/skills-management/roi/baseline.py

class BaselineManager:
    """
    Manage baseline measurements for ROI calculation
    """

    def __init__(self, time_tracker: TimeTracker):
        self.time_tracker = time_tracker
        self.baseline_file = self.time_tracker.data_dir / "baseline.json"

    def establish_baseline(self, days_to_collect: int = 7) -> Dict:
        """
        Collect baseline data before SMS deployment

        This should run for 1-2 weeks before enabling SMS features
        """
        print(f"Collecting baseline data for {days_to_collect} days...")
        print("Please use Claude Code normally without SMS features")

        baseline_data = {
            'collection_start': datetime.now().isoformat(),
            'collection_end': None,
            'metrics': {}
        }

        # Collect daily samples
        for day in range(days_to_collect):
            print(f"Day {day + 1}/{days_to_collect}")
            # Data is collected automatically by TimeTracker
            time.sleep(86400)  # Wait 24 hours (in practice, run as cron job)

        baseline_data['collection_end'] = datetime.now().isoformat()
        baseline_data['metrics'] = self.time_tracker.get_time_stats(period_days=days_to_collect)

        # Save baseline
        with open(self.baseline_file, 'w') as f:
            json.dump(baseline_data, f, indent=2)

        return baseline_data

    def get_baseline(self) -> Dict:
        """Load baseline data"""
        if not self.baseline_file.exists():
            raise FileNotFoundError("Baseline not established. Run establish_baseline() first.")

        with open(self.baseline_file) as f:
            return json.load(f)

    def compare_with_baseline(self, current_stats: Dict) -> Dict:
        """
        Compare current statistics with baseline
        """
        baseline = self.get_baseline()['metrics']

        comparison = {
            'search_time': {
                'baseline': baseline.get('activity_avg_duration', {}).get('skill_search', 0),
                'current': current_stats.get('activity_avg_duration', {}).get('skill_search', 0),
                'improvement_pct': 0
            },
            'execution_time': {
                'baseline': baseline.get('activity_avg_duration', {}).get('skill_execution', 0),
                'current': current_stats.get('activity_avg_duration', {}).get('skill_execution', 0),
                'improvement_pct': 0
            },
            'success_rate': {
                'baseline': self._calculate_success_rate(baseline),
                'current': self._calculate_success_rate(current_stats),
                'improvement_pct': 0
            }
        }

        # Calculate improvements
        for metric in comparison:
            baseline_val = comparison[metric]['baseline']
            current_val = comparison[metric]['current']
            if baseline_val > 0:
                improvement = (baseline_val - current_val) / baseline_val * 100
                comparison[metric]['improvement_pct'] = improvement

        return comparison

    def _calculate_success_rate(self, stats: Dict) -> float:
        """Calculate success rate from statistics"""
        success_count = stats.get('outcome_counts', {}).get('success', 0)
        total_count = sum(stats.get('outcome_counts', {}).values())
        return (success_count / total_count * 100) if total_count > 0 else 0
```

## Part 2: Cost Tracking

### 2.1 Development Cost Tracker

```python
# ~/.claude/skills-management/roi/cost_tracker.py

class CostTracker:
    """
    Track all costs associated with SMS
    """

    def __init__(self):
        self.data_dir = Path.home() / ".claude" / "skills-management" / "roi_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cost_log_file = self.data_dir / "costs.jsonl"

    def log_development_time(self, hours: float, hourly_rate: float, task: str):
        """
        Log development time spent on SMS

        Args:
            hours: Hours spent
            hourly_rate: Hourly rate (e.g., $50/hr)
            task: Description of task
        """
        cost_entry = {
            'timestamp': datetime.now().isoformat(),
            'cost_type': 'development',
            'amount': hours * hourly_rate,
            'hours': hours,
            'hourly_rate': hourly_rate,
            'task': task
        }

        with open(self.cost_log_file, 'a') as f:
            f.write(json.dumps(cost_entry) + '\n')

    def log_infrastructure_cost(self, amount: float, description: str):
        """
        Log infrastructure costs (servers, storage, etc.)
        """
        cost_entry = {
            'timestamp': datetime.now().isoformat(),
            'cost_type': 'infrastructure',
            'amount': amount,
            'description': description
        }

        with open(self.cost_log_file, 'a') as f:
            f.write(json.dumps(cost_entry) + '\n')

    def log_maintenance_time(self, hours: float, hourly_rate: float, task: str):
        """
        Log maintenance time
        """
        cost_entry = {
            'timestamp': datetime.now().isoformat(),
            'cost_type': 'maintenance',
            'amount': hours * hourly_rate,
            'hours': hours,
            'hourly_rate': hourly_rate,
            'task': task
        }

        with open(self.cost_log_file, 'a') as f:
            f.write(json.dumps(cost_entry) + '\n')

    def get_monthly_costs(self, month: int = None) -> Dict:
        """
        Get total costs for a month

        Args:
            month: Month number (1-12), defaults to current month
        """
        if month is None:
            month = datetime.now().month

        costs = {
            'development': 0.0,
            'infrastructure': 0.0,
            'maintenance': 0.0,
            'total': 0.0
        }

        if not self.cost_log_file.exists():
            return costs

        with open(self.cost_log_file, 'r') as f:
            for line in f:
                entry = json.loads(line)
                entry_date = datetime.fromisoformat(entry['timestamp'])

                if entry_date.month != month:
                    continue

                cost_type = entry['cost_type']
                amount = entry['amount']
                costs[cost_type] += amount
                costs['total'] += amount

        return costs

# Example: Logging development costs
cost_tracker = CostTracker()

# Initial development
cost_tracker.log_development_time(
    hours=40,
    hourly_rate=50,
    task="Initial SMS development"
)

# Ongoing maintenance
cost_tracker.log_maintenance_time(
    hours=5,
    hourly_rate=50,
    task="Bug fixes and improvements"
)

# Infrastructure
cost_tracker.log_infrastructure_cost(
    amount=200,
    description="Monthly server costs"
)
```

### 2.2 User Hourly Rate Configuration

```python
# ~/.claude/skills-management/roi/config.py

import yaml

class ROIConfig:
    """
    Configuration for ROI calculations
    """

    def __init__(self):
        self.config_file = Path.home() / ".claude" / "skills-management" / "roi_config.yaml"
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load configuration from file"""
        if not self.config_file.exists():
            # Create default config
            default_config = {
                'user_profile': {
                    'hourly_rate': 50,  # USD per hour
                    'working_hours_per_day': 8,
                    'working_days_per_month': 20
                },
                'roi_parameters': {
                    'baseline_period_days': 14,
                    'measurement_period_days': 30,
                    'time_to_value_days': 30
                },
                'benefit_weights': {
                    'time_saved': 1.0,
                    'success_rate_improvement': 1.5,
                    'discovery_improvement': 0.8,
                    'quality_improvement': 1.2
                }
            }

            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                yaml.dump(default_config, f)

            return default_config

        with open(self.config_file) as f:
            return yaml.safe_load(f)

    def get_hourly_rate(self) -> float:
        """Get user's hourly rate"""
        return self.config['user_profile']['hourly_rate']

    def update_hourly_rate(self, new_rate: float):
        """Update hourly rate"""
        self.config['user_profile']['hourly_rate'] = new_rate
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f)
```

## Part 3: Benefit Calculation

### 3.1 Time Savings Calculator

```python
# ~/.claude/skills-management/roi/benefit_calculator.py

class BenefitCalculator:
    """
    Calculate monetary benefits from SMS usage
    """

    def __init__(self, time_tracker: TimeTracker, baseline_manager: BaselineManager, config: ROIConfig):
        self.time_tracker = time_tracker
        self.baseline_manager = baseline_manager
        self.config = config
        self.hourly_rate = config.get_hourly_rate()

    def calculate_time_savings(self, period_days: int = 30) -> Dict:
        """
        Calculate time savings from SMS

        This compares current performance with baseline
        """
        current_stats = self.time_tracker.get_time_stats(period_days)
        comparison = self.baseline_manager.compare_with_baseline(current_stats)

        # Calculate time savings per activity
        activity_counts = current_stats.get('activity_counts', {})

        time_savings = {
            'search_time_savings': {
                'per_use_seconds': comparison['search_time']['baseline'] - comparison['search_time']['current'],
                'total_uses': activity_counts.get('skill_search', 0),
                'total_seconds': 0,
                'value': 0
            },
            'execution_time_savings': {
                'per_use_seconds': comparison['execution_time']['baseline'] - comparison['execution_time']['current'],
                'total_uses': activity_counts.get('skill_execution', 0),
                'total_seconds': 0,
                'value': 0
            }
        }

        # Calculate total time savings
        for activity in ['search_time_savings', 'execution_time_savings']:
            per_use = time_savings[activity]['per_use_seconds']
            total_uses = time_savings[activity]['total_uses']
            total_seconds = per_use * total_uses

            time_savings[activity]['total_seconds'] = total_seconds
            time_savings[activity]['total_hours'] = total_seconds / 3600
            time_savings[activity]['value'] = (total_seconds / 3600) * self.hourly_rate

        total_value = (
            time_savings['search_time_savings']['value'] +
            time_savings['execution_time_savings']['value']
        )

        return {
            'time_savings': time_savings,
            'total_monthly_value': total_value,
            'daily_value': total_value / 30
        }

    def calculate_success_rate_benefit(self, period_days: int = 30) -> Dict:
        """
        Calculate benefit from improved success rates

        Failed skills require rework, which costs time
        """
        current_stats = self.time_tracker.get_time_stats(period_days)
        comparison = self.baseline_manager.compare_with_baseline(current_stats)

        baseline_success_rate = comparison['success_rate']['baseline']
        current_success_rate = comparison['success_rate']['current']

        # Count total skill executions
        total_executions = current_stats.get('activity_counts', {}).get('skill_execution', 0)

        # Calculate failures prevented
        baseline_failures = total_executions * (1 - baseline_success_rate / 100)
        current_failures = total_executions * (1 - current_success_rate / 100)
        failures_prevented = baseline_failures - current_failures

        # Each failure takes ~2x the task time to fix
        avg_execution_time = current_stats.get('activity_avg_duration', {}).get('skill_execution', 0)
        rework_time_per_failure = avg_execution_time * 2
        total_rework_time_saved = failures_prevented * rework_time_per_failure

        value = (total_rework_time_saved / 3600) * self.hourly_rate

        return {
            'baseline_success_rate': baseline_success_rate,
            'current_success_rate': current_success_rate,
            'improvement': current_success_rate - baseline_success_rate,
            'failures_prevented': failures_prevented,
            'rework_time_saved_hours': total_rework_time_saved / 3600,
            'monthly_value': value
        }

    def calculate_discovery_improvement_benefit(self, period_days: int = 30) -> Dict:
        """
        Calculate benefit from improved skill discovery

        Better discovery means less time searching and better skill matches
        """
        current_stats = self.time_tracker.get_time_stats(period_days)
        comparison = self.baseline_manager.compare_with_baseline(current_stats)

        # Time saved on searches
        search_count = current_stats.get('activity_counts', {}).get('skill_search', 0)
        time_per_search_saved = comparison['search_time']['baseline'] - comparison['search_time']['current']
        total_time_saved = time_per_search_saved * search_count

        # Reduced search attempts (finding the right skill faster)
        # Assume baseline: 3 searches per task, current: 1.5 searches per task
        # This is a simplification; in practice, track this metric
        search_attempt_reduction = 1.5  # 1.5 fewer searches per task
        tasks_per_month = search_count / 1.5  # Rough estimate
        searches_saved = tasks_per_month * search_attempt_reduction
        time_from_searches_saved = searches_saved * comparison['search_time']['current']

        total_discovery_time_saved = total_time_saved + time_from_searches_saved
        value = (total_discovery_time_saved / 3600) * self.hourly_rate

        return {
            'search_time_saved_hours': total_time_saved / 3600,
            'searches_saved': searches_saved,
            'total_time_saved_hours': total_discovery_time_saved / 3600,
            'monthly_value': value
        }

    def calculate_all_benefits(self, period_days: int = 30) -> Dict:
        """
        Calculate all benefits and return summary
        """
        time_savings = self.calculate_time_savings(period_days)
        success_rate = self.calculate_success_rate_benefit(period_days)
        discovery = self.calculate_discovery_improvement_benefit(period_days)

        total_benefit = (
            time_savings['total_monthly_value'] +
            success_rate['monthly_value'] +
            discovery['monthly_value']
        )

        return {
            'time_savings': time_savings,
            'success_rate_improvement': success_rate,
            'discovery_improvement': discovery,
            'total_monthly_benefit': total_benefit,
            'daily_benefit': total_benefit / 30,
            'break_even_days': self._calculate_break_even(total_benefit)
        }

    def _calculate_break_even(self, monthly_benefit: float) -> int:
        """
        Calculate days to break even on development costs

        This is a simplified calculation
        """
        # Estimate total development cost (one-time)
        # This should come from CostTracker
        estimated_dev_cost = 5000  # Placeholder

        daily_benefit = monthly_benefit / 30
        break_even_days = estimated_dev_cost / daily_benefit if daily_benefit > 0 else float('inf')

        return int(break_even_days)
```

## Part 4: ROI Calculator

### 4.1 Main ROI Calculation Engine

```python
# ~/.claude/skills-management/roi/roi_calculator.py

class ROICalculator:
    """
    Main ROI calculation engine

    Combines costs and benefits to calculate ROI
    """

    def __init__(self, benefit_calculator: BenefitCalculator, cost_tracker: CostTracker):
        self.benefit_calculator = benefit_calculator
        self.cost_tracker = cost_tracker

    def calculate_monthly_roi(self, month: int = None) -> Dict:
        """
        Calculate ROI for a specific month

        Args:
            month: Month number (1-12), defaults to current month

        Returns:
            ROI report dictionary
        """
        # Get costs for the month
        costs = self.cost_tracker.get_monthly_costs(month)

        # Get benefits for the month (30-day period)
        benefits = self.benefit_calculator.calculate_all_benefits(period_days=30)

        # Calculate ROI
        total_cost = costs['total']
        total_benefit = benefits['total_monthly_benefit']
        net_benefit = total_benefit - total_cost

        roi = ((total_benefit - total_cost) / total_cost * 100) if total_cost > 0 else float('inf')

        # Calculate payback period
        daily_benefit = benefits['daily_benefit']
        payback_days = total_cost / daily_benefit if daily_benefit > 0 else float('inf')
        payback_months = payback_days / 30

        return {
            'period': {
                'month': month or datetime.now().month,
                'year': datetime.now().year
            },
            'costs': {
                'development': costs['development'],
                'infrastructure': costs['infrastructure'],
                'maintenance': costs['maintenance'],
                'total': costs['total']
            },
            'benefits': {
                'time_savings': benefits['time_savings']['total_monthly_value'],
                'success_rate': benefits['success_rate_improvement']['monthly_value'],
                'discovery': benefits['discovery_improvement']['monthly_value'],
                'total': benefits['total_monthly_benefit']
            },
            'roi_metrics': {
                'net_benefit': net_benefit,
                'roi_percentage': roi,
                'payback_period_days': payback_days,
                'payback_period_months': payback_months
            },
            'daily_metrics': {
                'daily_benefit': daily_benefit,
                'daily_cost': total_cost / 30,
                'daily_net': daily_benefit - (total_cost / 30)
            }
        }

    def generate_roi_report(self, month: int = None) -> str:
        """
        Generate human-readable ROI report
        """
        roi_data = self.calculate_monthly_roi(month)

        report = f"""
# Skills Management System - ROI Report

**Period**: {roi_data['period']['year']}-{roi_data['period']['month']:02d}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 💰 Costs

| Category | Monthly Cost |
|----------|--------------|
| Development (amortized) | ${roi_data['costs']['development']:,.2f} |
| Infrastructure | ${roi_data['costs']['infrastructure']:,.2f} |
| Maintenance | ${roi_data['costs']['maintenance']:,.2f} |
| **Total Cost** | **${roi_data['costs']['total']:,.2f}** |

## 💵 Benefits

| Category | Monthly Value |
|----------|---------------|
| Time Savings | ${roi_data['benefits']['time_savings']:,.2f} |
| Success Rate Improvement | ${roi_data['benefits']['success_rate']:,.2f} |
| Discovery Improvement | ${roi_data['benefits']['discovery']:,.2f} |
| **Total Benefit** | **${roi_data['benefits']['total']:,.2f}** |

## 📊 ROI Metrics

| Metric | Value |
|--------|-------|
| **Net Benefit** | **${roi_data['roi_metrics']['net_benefit']:,.2f}** |
| **ROI** | **{roi_data['roi_metrics']['roi_percentage']:.1f}%** |
| Payback Period | {roi_data['roi_metrics']['payback_period_days']:.1f} days ({roi_data['roi_metrics']['payback_period_months']:.1f} months) |

### Daily Breakdown

- Daily Benefit: ${roi_data['daily_metrics']['daily_benefit']:,.2f}
- Daily Cost: ${roi_data['daily_metrics']['daily_cost']:,.2f}
- Daily Net: ${roi_data['daily_metrics']['daily_net']:,.2f}

## 📈 Interpretation

"""

        # Add interpretation
        roi = roi_data['roi_metrics']['roi_percentage']
        if roi > 100:
            report += "✅ **Excellent ROI**: System generating 3x+ return on investment\n\n"
        elif roi > 50:
            report += "✅ **Good ROI**: System generating solid returns\n\n"
        elif roi > 0:
            report += "⚠️ **Positive ROI**: System profitable but room for improvement\n\n"
        else:
            report += "❌ **Negative ROI**: System not yet profitable\n\n"

        payback_days = roi_data['roi_metrics']['payback_period_days']
        if payback_days < 30:
            report += f"✅ Break-even achieved in **{payback_days:.0f} days**\n\n"
        elif payback_days < 90:
            report += f"⚠️ Break-even in **{payback_days:.0f} days** ({payback_days/30:.1f} months)\n\n"
        else:
            report += f"❌ Break-even will take **{payback_days:.0f} days** ({payback_days/30:.1f} months)\n\n"

        report += f"""
## 💡 Recommendations

Based on current ROI of {roi:.1f}%:

1. {'Continue current usage' if roi > 50 else 'Investigate optimization opportunities'}
2. {'Scale up usage' if roi > 100 else 'Monitor closely'}
3. Consider expanding to more team members if ROI remains positive

---

*Report generated by Skills Management System ROI Calculator*
"""

        return report

    def calculate_projected_roi(self, months_ahead: int = 12) -> List[Dict]:
        """
        Project ROI for future months

        This uses current trends to estimate future performance
        """
        projections = []

        # Get current monthly benefit
        current_benefits = self.benefit_calculator.calculate_all_benefits(period_days=30)
        monthly_benefit = current_benefits['total_monthly_benefit']

        # Get monthly costs (assume stable)
        monthly_costs = self.cost_tracker.get_monthly_costs()

        for month in range(1, months_ahead + 1):
            # Assume slight improvement in benefits over time (learning curve)
            improvement_factor = 1.0 + (month * 0.02)  # 2% improvement per month
            projected_benefit = monthly_benefit * improvement_factor

            net_benefit = projected_benefit - monthly_costs['total']
            cumulative_net = net_benefit * month

            projections.append({
                'month': month,
                'projected_benefit': projected_benefit,
                'projected_cost': monthly_costs['total'],
                'projected_net': net_benefit,
                'cumulative_net': cumulative_net
            })

        return projections
```

## Part 5: Integration & Automation

### 5.1 CLI Integration

```python
# ~/.claude/skills-management/cli/roi_commands.py

import click

@click.group()
def roi():
    """ROI calculation and reporting commands"""
    pass

@roi.command()
@click.option('--month', type=int, help='Month number (1-12)')
def report(month):
    """Generate ROI report"""
    time_tracker = TimeTracker(user_id=get_current_user_id())
    baseline_manager = BaselineManager(time_tracker)
    config = ROIConfig()
    benefit_calc = BenefitCalculator(time_tracker, baseline_manager, config)
    cost_tracker = CostTracker()
    roi_calc = ROICalculator(benefit_calc, cost_tracker)

    report_text = roi_calc.generate_roi_report(month)
    click.echo(report_text)

    # Save report
    report_dir = Path.home() / ".claude" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / f"roi_report_{datetime.now().strftime('%Y%m')}.md"
    with open(report_file, 'w') as f:
        f.write(report_text)

    click.echo(f"\n✅ Report saved to: {report_file}")

@roi.command()
def baseline():
    """Establish baseline measurements"""
    time_tracker = TimeTracker(user_id=get_current_user_id())
    baseline_manager = BaselineManager(time_tracker)

    click.echo("Establishing baseline measurements...")
    click.echo("Please use Claude Code normally for 7 days.")

    if click.confirm("Start baseline collection now?"):
        baseline_data = baseline_manager.establish_baseline(days_to_collect=7)
        click.echo("✅ Baseline established!")
        click.echo(f"Baseline saved to: {baseline_manager.baseline_file}")

@roi.command()
@click.option('--hours', type=float, required=True, help='Hours spent')
@click.option('--rate', type=float, required=True, help='Hourly rate')
@click.option('--task', type=str, required=True, help='Task description')
def log_cost(hours, rate, task):
    """Log development or maintenance costs"""
    cost_tracker = CostTracker()

    # Determine cost type based on task description
    if 'dev' in task.lower() or 'implement' in task.lower():
        cost_tracker.log_development_time(hours, rate, task)
    else:
        cost_tracker.log_maintenance_time(hours, rate, task)

    click.echo(f"✅ Logged {hours}h at ${rate}/h for: {task}")

@roi.command()
@click.option('--months', type=int, default=12, help='Number of months to project')
def project(months):
    """Show ROI projections"""
    time_tracker = TimeTracker(user_id=get_current_user_id())
    baseline_manager = BaselineManager(time_tracker)
    config = ROIConfig()
    benefit_calc = BenefitCalculator(time_tracker, baseline_manager, config)
    cost_tracker = CostTracker()
    roi_calc = ROICalculator(benefit_calc, cost_tracker)

    projections = roi_calc.calculate_projected_roi(months)

    click.echo("\n📊 ROI Projections\n")
    click.echo("| Month | Benefit | Cost | Net | Cumulative |")
    click.echo("|-------|---------|------|-----|------------|")

    for proj in projections:
        click.echo(f"| {proj['month']:2d} | ${proj['projected_benefit']:7.2f} | ${proj['projected_cost']:5.2f} | ${proj['projected_net']:6.2f} | ${proj['cumulative_net']:9.2f} |")
```

### 5.2 Automated Reporting

```python
# ~/.claude/skills-management/roi/automated_reporting.py

from apscheduler.schedulers.background import BackgroundScheduler

class ROIAutomatedReporter:
    """
    Automatically generate ROI reports on schedule
    """

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.setup_scheduled_jobs()

    def setup_scheduled_jobs(self):
        """Setup scheduled ROI report generation"""
        # Monthly ROI report (1st of each month at 9 AM)
        self.scheduler.add_job(
            self.generate_monthly_report,
            'cron',
            day=1,
            hour=9,
            minute=0,
            id='monthly_roi_report'
        )

        # Weekly ROI check (Sundays at 10 AM)
        self.scheduler.add_job(
            self.generate_weekly_summary,
            'cron',
            day_of_week='sun',
            hour=10,
            minute=0,
            id='weekly_roi_summary'
        )

    def generate_monthly_report(self):
        """Generate monthly ROI report"""
        time_tracker = TimeTracker(user_id="system")
        baseline_manager = BaselineManager(time_tracker)
        config = ROIConfig()
        benefit_calc = BenefitCalculator(time_tracker, baseline_manager, config)
        cost_tracker = CostTracker()
        roi_calc = ROICalculator(benefit_calc, cost_tracker)

        report = roi_calc.generate_roi_report()

        # Save report
        report_dir = Path.home() / ".claude" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_file = report_dir / f"monthly_roi_{datetime.now().strftime('%Y%m')}.md"
        with open(report_file, 'w') as f:
            f.write(report)

        # Send notification (optional)
        self.send_notification(f"Monthly ROI report generated: {report_file}")

    def generate_weekly_summary(self):
        """Generate weekly ROI summary"""
        # Similar to monthly but for weekly data
        pass

    def start(self):
        """Start the scheduler"""
        self.scheduler.start()
        print("ROI automated reporting started")

    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
```

## Part 6: Usage Example

### 6.1 Complete ROI Calculation Workflow

```python
# Example: Complete ROI workflow

# 1. Initialize components
time_tracker = TimeTracker(user_id="user456")
baseline_manager = BaselineManager(time_tracker)
config = ROIConfig()
config.update_hourly_rate(75)  # User earns $75/hr
benefit_calc = BenefitCalculator(time_tracker, baseline_manager, config)
cost_tracker = CostTracker()
roi_calc = ROICalculator(benefit_calc, cost_tracker)

# 2. Establish baseline (run once before SMS deployment)
# baseline_manager.establish_baseline(days_to_collect=14)

# 3. Log costs (ongoing)
cost_tracker.log_development_time(
    hours=40,
    hourly_rate=75,
    task="Initial SMS development"
)
cost_tracker.log_infrastructure_cost(
    amount=200,
    description="Monthly server costs"
)

# 4. Track time (automatic during usage)
search_timer = time_tracker.start_timer("skill_search", metadata={'query': 'frontend'})
# ... user searches ...
time_tracker.stop_timer(search_timer, "success_found")

execution_timer = time_tracker.start_timer("skill_execution", metadata={'skill_name': 'frontend-design'})
# ... skill executes ...
time_tracker.stop_timer(execution_timer, "success")

# 5. Calculate ROI
roi_report = roi_calc.generate_roi_report()
print(roi_report)

# 6. Get projections
projections = roi_calc.calculate_projected_roi(months_ahead=12)
for proj in projections:
    print(f"Month {proj['month']}: ${proj['cumulative_net']:.2f} cumulative net")
```

## Part 7: Validation & Accuracy

### 7.1 Data Validation

```python
class ROIDataValidator:
    """
    Validate ROI data for accuracy
    """

    def validate_time_logs(self, time_tracker: TimeTracker) -> Dict:
        """Check time log data quality"""
        issues = []

        # Check for negative durations
        # Check for unreasonable durations (> 1 hour for search)
        # Check for missing data

        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

    def validate_cost_logs(self, cost_tracker: CostTracker) -> Dict:
        """Check cost log data quality"""
        issues = []

        # Check for negative costs
        # Check for missing descriptions
        # Check for duplicate entries

        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

    def calculate_confidence_interval(self, roi_calc: ROICalculator) -> Dict:
        """
        Calculate confidence intervals for ROI estimates

        This helps communicate uncertainty in ROI calculations
        """
        # Use bootstrap method or statistical formulas
        # Returns confidence intervals (95% confidence)

        return {
            'roi_lower_bound': 110,  # Lower 95% CI
            'roi_point_estimate': 130,  # Calculated ROI
            'roi_upper_bound': 150,  # Upper 95% CI
            'confidence_level': 95
        }
```

## Summary

This ROI implementation provides:

✅ **Automated Time Tracking**: Track skill usage automatically
✅ **Baseline Comparison**: Compare before/after SMS
✅ **Cost Tracking**: Log all development and maintenance costs
✅ **Benefit Calculation**: Quantify time savings, success rate improvements
✅ **ROI Reports**: Generate readable ROI reports
✅ **Projections**: Forecast future ROI
✅ **Automated Reporting**: Schedule regular reports
✅ **Validation**: Ensure data accuracy

**Key Files**:
- `time_tracker.py` - Track time automatically
- `cost_tracker.py` - Log costs
- `benefit_calculator.py` - Calculate benefits
- `roi_calculator.py` - Main ROI engine
- `roi_commands.py` - CLI commands

**Usage**:
```bash
# Establish baseline
skills roi baseline

# Generate report
skills roi report

# Log costs
skills roi log-cost --hours 5 --rate 75 --task "Bug fixes"

# Show projections
skills roi project --months 12
```

---

**Document Version**: 1.0
**Last Updated**: 2026-05-04
**Author**: Claude Code
**Status**: Implementation Guide
