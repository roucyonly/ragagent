# Skills Management System - 自动发现与注册机制

## 问题

用户创建新技能的方式多种多样，如何确保所有新技能都能被 SMS 系统自动发现和管理？

## 技能安装方式分析

### 常见安装方式

```bash
# 1. 全局安装（npm）
npm install -g @your-org/your-skill

# 2. 项目本地安装（npm）
npm install @your-org/your-skill

# 3. 手动创建
mkdir -p ~/.claude/plugins/local/skills/my-skill
echo "content" > SKILL.md

# 4. 从插件市场安装
claude plugin install official-plugin-name

# 5. 克隆 GitHub 仓库
git clone https://github.com/user/skill-repo.git ~/.claude/plugins/local/skills/

# 6. 符号链接
ln -s /path/to/skill ~/.claude/plugins/local/skills/my-skill
```

### 技能可能存在的位置

```
~/.claude/
├── plugins/
│   ├── marketplaces/
│   │   └── claude-plugins-official/      # 官方插件
│   │       └── plugins/
│   │           └── skill-name/
│   │               └── skills/
│   │                   └── SKILL.md
│   │
│   └── local/                             # 本地插件
│       └── skills/
│           ├── my-skill-1/                # 手动创建
│           │   └── SKILL.md
│           ├── my-skill-2/                # npm 全局安装
│           │   └── SKILL.md
│           └── my-skill-3 -> /other/path  # 符号链接
│
└── node_modules/                          # npm 全局安装
    └── @your-org/
        └── your-skill/
            └── SKILL.md

# 项目本地
~/my-project/
├── .claude/
│   └── skills/                            # 项目特定技能
│       └── project-skill/
│           └── SKILL.md
│
└── node_modules/                          # 项目本地安装
    └── @your-org/
        └── your-skill/
            └── SKILL.md
```

## 解决方案：多层自动发现机制

### 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│              Skills Auto-Discovery System                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           1. 扫描引擎 (Scanner)                      │    │
│  │   - 文件系统监控                                     │    │
│  │   - 定时扫描                                        │    │
│  │   - 事件触发                                        │    │
│  └────────────┬────────────────────────────────────────┘    │
│               │                                              │
│               ↓                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         2. 发现器 (Discoverers)                      │    │
│  │   ┌──────────────┐  ┌──────────────┐               │    │
│  │   │ 文件扫描器   │  │ NPM扫描器    │               │    │
│  │   │ File Scanner │  │ NPM Scanner  │               │    │
│  │   └──────────────┘  └──────────────┘               │    │
│  │   ┌──────────────┐  ┌──────────────┐               │    │
│  │   │ Git扫描器    │  │ 市场扫描器    │               │    │
│  │   │ Git Scanner  │  │Market Scanner│               │    │
│  │   └──────────────┘  └──────────────┘               │    │
│  └────────────┬────────────────────────────────────────┘    │
│               │                                              │
│               ↓                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │        3. 验证器 (Validator)                         │    │
│  │   - 检查 SKILL.md 格式                               │    │
│  │   - 验证 frontmatter                                 │    │
│  │   - 提取元数据                                       │    │
│  └────────────┬────────────────────────────────────────┘    │
│               │                                              │
│               ↓                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │        4. 注册器 (Registrar)                          │    │
│  │   - 添加到注册表                                     │    │
│  │   - 去重处理                                        │    │
│  │   - 版本管理                                         │    │
│  └────────────┬────────────────────────────────────────┘    │
│               │                                              │
│               ↓                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │        5. 通知器 (Notifier)                           │    │
│  │   - 用户通知                                         │    │
│  │   - 日志记录                                         │    │
│  │   - 统计更新                                         │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 实现方案

### 1. 配置文件：定义扫描路径

```yaml
# ~/.claude/skills-management/data/discovery_config.yaml
discovery:
  enabled: true

  # 扫描频率
  scan_frequency: automatic  # automatic | manual | scheduled
  scan_interval_minutes: 5

  # 扫描路径
  scan_paths:
    # 全局插件路径
    - path: ~/.claude/plugins/marketplaces/claude-plugins-official
      type: official
      recursive: true
      skill_pattern: "**/skills/*/SKILL.md"

    # 本地插件路径
    - path: ~/.claude/plugins/local/skills
      type: local
      recursive: true
      skill_pattern: "*/SKILL.md"

    # 项目特定路径
    - path: ./.claude/skills
      type: project
      recursive: true
      skill_pattern: "*/SKILL.md"

    # NPM 全局安装
    - path: ~/.claude/node_modules
      type: npm_global
      recursive: true
      skill_pattern: "*/SKILL.md"

    # NPM 项目本地安装
    - path: ./node_modules
      type: npm_local
      recursive: true
      skill_pattern: "*/SKILL.md"

  # 忽略路径
  ignore_paths:
    - "**/node_modules/**/test/**"
    - "**/node_modules/**/examples/**"
    - "**/.git/**"

  # 自动注册
  auto_register: true
  require_validation: true

  # 通知设置
  notifications:
    on_new_skill: true
    on_skill_update: true
    on_skill_removed: true
```

### 2. 扫描引擎实现

```python
# ~/.claude/skills-management/core/scanner.py

import os
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SkillScanner:
    """
    技能扫描引擎
    支持定时扫描和实时监控
    """

    def __init__(self, config: Dict, registrar):
        self.config = config
        self.registrar = registrar
        self.scan_cache = {}
        self.observer = None

    def start_monitoring(self):
        """启动实时文件监控"""
        if self.config['scan_frequency'] != 'automatic':
            return

        event_handler = SkillFileChangeHandler(self)
        self.observer = Observer()

        # 监控所有配置的路径
        for scan_config in self.config['scan_paths']:
            path = Path(scan_config['path']).expanduser()
            if path.exists():
                self.observer.schedule(
                    event_handler,
                    str(path),
                    recursive=scan_config.get('recursive', True)
                )

        self.observer.start()
        print("✓ 文件监控已启动")

    def stop_monitoring(self):
        """停止文件监控"""
        if self.observer:
            self.observer.stop()
            self.observer.join()

    def scan_all(self) -> Dict:
        """扫描所有配置的路径"""
        results = {
            'scanned': 0,
            'found': 0,
            'registered': 0,
            'updated': 0,
            'errors': []
        }

        for scan_config in self.config['scan_paths']:
            try:
                path_results = self._scan_path(scan_config)
                results['scanned'] += path_results['scanned']
                results['found'] += path_results['found']
                results['registered'] += path_results['registered']
                results['updated'] += path_results['updated']
                results['errors'].extend(path_results['errors'])
            except Exception as e:
                results['errors'].append({
                    'path': scan_config['path'],
                    'error': str(e)
                })

        return results

    def _scan_path(self, scan_config: Dict) -> Dict:
        """扫描单个路径"""
        results = {
            'scanned': 0,
            'found': 0,
            'registered': 0,
            'updated': 0,
            'errors': []
        }

        path = Path(scan_config['path']).expanduser()
        if not path.exists():
            return results

        pattern = scan_config.get('skill_pattern', '**/SKILL.md')
        skill_files = list(path.glob(pattern))

        # 应用忽略规则
        skill_files = self._apply_ignore_rules(skill_files, self.config.get('ignore_paths', []))

        results['scanned'] = len(skill_files)

        for skill_file in skill_files:
            try:
                result = self._process_skill_file(skill_file, scan_config)
                if result['action'] == 'registered':
                    results['registered'] += 1
                elif result['action'] == 'updated':
                    results['updated'] += 1
                results['found'] += 1
            except Exception as e:
                results['errors'].append({
                    'file': str(skill_file),
                    'error': str(e)
                })

        return results

    def _process_skill_file(self, skill_file: Path, scan_config: Dict) -> Dict:
        """处理单个技能文件"""
        # 计算文件哈希，检测变更
        file_hash = self._calculate_hash(skill_file)

        # 检查是否已存在
        existing_skill = self.registrar.get_skill_by_path(skill_file)

        if existing_skill:
            # 检查是否有更新
            if existing_skill.get('file_hash') != file_hash:
                # 技能已更新
                skill_data = self._extract_skill_data(skill_file)
                skill_data['file_hash'] = file_hash
                skill_data['last_scanned'] = datetime.now().isoformat()

                self.registrar.update_skill(existing_skill['name'], skill_data)
                return {'action': 'updated', 'skill': skill_data}
            else:
                return {'action': 'skipped', 'reason': 'unchanged'}
        else:
            # 新技能
            skill_data = self._extract_skill_data(skill_file)
            skill_data['file_hash'] = file_hash
            skill_data['last_scanned'] = datetime.now().isoformat()
            skill_data['source_type'] = scan_config['type']
            skill_data['source_path'] = str(scan_config['path'])

            self.registrar.add_skill_from_discovery(skill_data)
            return {'action': 'registered', 'skill': skill_data}

    def _extract_skill_data(self, skill_file: Path) -> Dict:
        """从 SKILL.md 提取数据"""
        import yaml

        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 分离 frontmatter 和内容
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter_text = parts[1]
                skill_content = parts[2]
                frontmatter = yaml.safe_load(frontmatter_text)
            else:
                frontmatter = {}
                skill_content = content
        else:
            frontmatter = {}
            skill_content = content

        # 生成技能名称（从路径或frontmatter）
        skill_name = frontmatter.get('name')
        if not skill_name:
            # 从路径推断名称
            skill_name = skill_file.parent.name

        return {
            'name': skill_name,
            'display_name': frontmatter.get('description', skill_name),
            'description': frontmatter.get('description', ''),
            'path': str(skill_file),
            'tags': frontmatter.get('tags', []),
            'tech_stack': frontmatter.get('tech_stack', []),
            'scenarios': frontmatter.get('scenarios', []),
            'complexity': frontmatter.get('complexity', 'medium'),
            'version': frontmatter.get('version', '1.0.0'),
            'frontmatter': frontmatter,
            'content': skill_content
        }

    def _calculate_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()

    def _apply_ignore_rules(self, files: List[Path], ignore_patterns: List[str]) -> List[Path]:
        """应用忽略规则"""
        import fnmatch

        filtered = []
        for file_path in files:
            ignored = False
            for pattern in ignore_patterns:
                if fnmatch.fnmatch(str(file_path), pattern):
                    ignored = True
                    break
            if not ignored:
                filtered.append(file_path)

        return filtered


class SkillFileChangeHandler(FileSystemEventHandler):
    """
    文件变化处理器
    当 SKILL.md 文件发生变化时触发
    """

    def __init__(self, scanner: SkillScanner):
        self.scanner = scanner

    def on_created(self, event):
        """文件创建"""
        if event.src_path.endswith('SKILL.md'):
            print(f"🆕 检测到新技能: {event.src_path}")
            self.scanner._process_skill_file(
                Path(event.src_path),
                {'type': 'auto_detected'}
            )

    def on_modified(self, event):
        """文件修改"""
        if event.src_path.endswith('SKILL.md'):
            print(f"📝 技能已更新: {event.src_path}")
            self.scanner._process_skill_file(
                Path(event.src_path),
                {'type': 'auto_detected'}
            )

    def on_deleted(self, event):
        """文件删除"""
        if event.src_path.endswith('SKILL.md'):
            print(f"🗑️  技能已删除: {event.src_path}")
            # 标记技能为缺失
            self.scanner.registrar.mark_skill_missing(event.src_path)

    def on_moved(self, event):
        """文件移动"""
        if event.src_path.endswith('SKILL.md') or event.dest_path.endswith('SKILL.md'):
            print(f"📦 技能已移动: {event.src_path} -> {event.dest_path}")
            # 更新路径
            self.scanner.registrar.update_skill_path(event.src_path, event.dest_path)
```

### 3. 注册器扩展

```python
# ~/.claude/skills-management/core/skill_registry.py

class SkillRegistry:
    # ... 现有方法 ...

    def add_skill_from_discovery(self, skill_data: Dict) -> bool:
        """从自动发现添加技能"""
        # 验证技能数据
        if not self._validate_skill_data(skill_data):
            return False

        # 检查是否已存在
        if skill_data['name'] in self.skills:
            # 技能已存在，更新而不是添加
            return self.update_skill(skill_data['name'], skill_data)

        # 添加到注册表
        self.skills[skill_data['name']] = {
            **skill_data,
            'discovered_at': datetime.now().isoformat(),
            'registration_method': 'auto_discovery'
        }

        # 通知用户
        self._notify_new_skill(skill_data)

        # 保存注册表
        self._save_registry()

        return True

    def get_skill_by_path(self, path: Path) -> Optional[Dict]:
        """通过路径查找技能"""
        path_str = str(path)
        for skill_name, skill_data in self.skills.items():
            if skill_data.get('path') == path_str:
                return skill_data
        return None

    def mark_skill_missing(self, path: str):
        """标记技能为缺失"""
        skill = self.get_skill_by_path(Path(path))
        if skill:
            skill['status'] = 'missing'
            skill['missing_since'] = datetime.now().isoformat()
            self._save_registry()
            print(f"⚠️  技能 '{skill['name']}' 标记为缺失")

    def update_skill_path(self, old_path: str, new_path: str):
        """更新技能路径"""
        skill = self.get_skill_by_path(Path(old_path))
        if skill:
            skill['path'] = new_path
            skill['last_updated'] = datetime.now().isoformat()
            self._save_registry()

    def _notify_new_skill(self, skill_data: Dict):
        """通知用户新技能"""
        if not self.config.get('notifications', {}).get('on_new_skill', True):
            return

        print(f"""
╔════════════════════════════════════════════════════════════╗
║  🎉 发现新技能                                              ║
╚════════════════════════════════════════════════════════════╝

名称: {skill_data['name']}
描述: {skill_data.get('description', 'N/A')}
路径: {skill_data['path']}
来源: {skill_data.get('source_type', 'unknown')}

已自动注册到技能管理系统

使用 'skills info {skill_data['name']}' 查看详情
""")

    def _validate_skill_data(self, skill_data: Dict) -> bool:
        """验证技能数据"""
        # 必需字段
        required_fields = ['name', 'path']
        for field in required_fields:
            if field not in skill_data:
                print(f"❌ 技能缺少必需字段: {field}")
                return False

        # 验证路径存在
        if not Path(skill_data['path']).exists():
            print(f"❌ 技能文件不存在: {skill_data['path']}")
            return False

        return True
```

### 4. CLI 集成

```python
# ~/.claude/skills-management/cli/commands.py

@click.group()
def discovery():
    """技能自动发现命令"""
    pass

@discovery.command()
def scan():
    """手动扫描所有路径"""
    scanner = SkillScanner(config, registrar)
    results = scanner.scan_all()

    click.echo(f"""
扫描完成:
  扫描路径: {results['scanned']}
  发现技能: {results['found']}
  新注册: {results['registered']}
  更新: {results['updated']}
  错误: {len(results['errors'])}
""")

    if results['errors']:
        click.echo("\n错误:")
        for error in results['errors']:
            click.echo(f"  - {error}")

@discovery.command()
@click.option('--daemon', is_flag=True, help='后台运行')
def monitor(daemon):
    """启动文件监控"""
    scanner = SkillScanner(config, registrar)
    scanner.start_monitoring()

    if daemon:
        click.echo("文件监控已在后台启动")
        # 保持运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            scanner.stop_monitoring()
    else:
        click.echo("文件监控已启动，按 Ctrl+C 停止")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            scanner.stop_monitoring()

@discovery.command()
def status():
    """查看发现状态"""
    scanner = SkillScanner(config, registrar)

    click.echo("""
技能发现状态:

配置的扫描路径:
""")

    for scan_config in config['scan_paths']:
        path = Path(scan_config['path']).expanduser()
        exists = "✓" if path.exists() else "✗"
        click.echo(f"  {exists} {scan_config['path']} ({scan_config['type']})")

    click.echo(f"""
注册表统计:
  总技能数: {len(registry.skills)}
  自动发现: {sum(1 for s in registry.skills.values() if s.get('registration_method') == 'auto_discovery')}
  手动添加: {sum(1 for s in registry.skills.values() if s.get('registration_method') != 'auto_discovery')}
""")
```

### 5. 定时任务集成

```yaml
# settings.json
{
  "hooks": {
    "sessionStart": [
      {
        "command": "skills discovery scan",
        "description": "会话开始时扫描新技能"
      }
    ]
  },

  "scheduled_tasks": {
    "hourly-skill-scan": {
      "cron": "0 * * * *",
      "prompt": "skills discovery scan",
      "durable": true
    }
  }
}
```

### 6. NPM 集成（特殊处理）

```python
# ~/.claude/skills-management/core/npm_scanner.py

import subprocess
import json
from pathlib import Path

class NPMSkillScanner:
    """
    NPM 技能扫描器
    处理通过 npm 安装的技能
    """

    def scan_global_packages(self) -> List[Dict]:
        """扫描全局安装的 npm 包"""
        try:
            result = subprocess.run(
                ['npm', 'list', '-g', '--depth=0', '--json'],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return []

            packages = json.loads(result.stdout)
            return self._find_skills_in_packages(packages, global=True)

        except Exception as e:
            print(f"❌ 扫描全局 npm 包失败: {e}")
            return []

    def scan_local_packages(self, project_path: Path = None) -> List[Dict]:
        """扫描项目本地安装的 npm 包"""
        if project_path is None:
            project_path = Path.cwd()

        try:
            result = subprocess.run(
                ['npm', 'list', '--depth=0', '--json'],
                cwd=project_path,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return []

            packages = json.loads(result.stdout)
            return self._find_skills_in_packages(packages, global=False, project_path=project_path)

        except Exception as e:
            print(f"❌ 扫描本地 npm 包失败: {e}")
            return []

    def _find_skills_in_packages(self, packages: Dict, global: bool = False, project_path: Path = None) -> List[Dict]:
        """在 npm 包中查找技能"""
        skills = []

        if 'dependencies' not in packages:
            return skills

        for package_name, package_info in packages['dependencies'].items():
            # 检查包是否包含 SKILL.md
            skill_path = self._find_skill_in_package(package_name, global, project_path)

            if skill_path:
                skills.append({
                    'name': package_name,
                    'path': str(skill_path),
                    'source_type': 'npm_global' if global else 'npm_local',
                    'version': package_info.get('version', 'unknown')
                })

        return skills

    def _find_skill_in_package(self, package_name: str, global: bool, project_path: Path = None) -> Optional[Path]:
        """在 npm 包中查找 SKILL.md"""
        if global:
            base_path = Path.home() / 'node_modules' / package_name
        else:
            base_path = (project_path or Path.cwd()) / 'node_modules' / package_name

        # 常见的位置
        possible_paths = [
            base_path / 'SKILL.md',
            base_path / 'skills' / 'SKILL.md',
            base_path / 'lib' / 'SKILL.md',
        ]

        for path in possible_paths:
            if path.exists():
                return path

        return None
```

## 使用场景

### 场景 1：手动创建技能

```bash
# 用户手动创建技能
mkdir -p ~/.claude/plugins/local/skills/my-new-skill
cat > ~/.claude/plugins/local/skills/my-new-skill/SKILL.md << 'EOF'
---
name: my-new-skill
description: 我的新技能
tags: [utility]
---

这是一个新技能
EOF

# 系统自动检测（如果文件监控在运行）
# 🆕 检测到新技能: ~/.claude/plugins/local/skills/my-new-skill/SKILL.md
# ╔════════════════════════════════════════════════════════════╗
# ║  🎉 发现新技能                                              ║
# ╚════════════════════════════════════════════════════════════╝
# 名称: my-new-skill
# 描述: 我的新技能
# 路径: ~/.claude/plugins/local/skills/my-new-skill/SKILL.md
# 来源: local
# 已自动注册到技能管理系统

# 或者手动触发扫描
$ skills discovery scan

扫描完成:
  扫描路径: 5
  发现技能: 1
  新注册: 1
  更新: 0
```

### 场景 2：NPM 全局安装

```bash
# 用户通过 npm 全局安装技能
$ npm install -g @my-org/my-skill

# 系统自动检测
$ skills discovery scan

扫描完成:
  扫描路径: 8
  发现技能: 1
  新注册: 1
  更新: 0

# 查看详情
$ skills info my-skill

@my-org/my-skill
  描述: 通过 npm 安装的技能
  来源: npm_global
  版本: 1.0.0
  路径: ~/node_modules/@my-org/my-skill/SKILL.md
```

### 场景 3：项目本地技能

```bash
# 用户在项目中创建本地技能
$ cd ~/my-project
$ mkdir -p .claude/skills/project-tool
$ cat > .claude/skills/project-tool/SKILL.md << 'EOF'
---
name: project-tool
description: 项目特定工具
tags: [project]
---

项目特定工具
EOF

# 切换到项目目录时自动扫描
$ cd ~/my-project
$ skills discovery scan

扫描完成:
  发现技能: 1
  新注册: 1
  来源: project
```

### 场景 4：更新技能

```bash
# 用户修改技能文件
$ vim ~/.claude/plugins/local/skills/my-skill/SKILL.md

# 系统自动检测变更
# 📝 技能已更新: ~/.claude/plugins/local/skills/my-skill/SKILL.md

# 查看变更
$ skills info my-skill

my-skill
  最后更新: 2026-05-04 18:30
  版本: 2.0.0
```

## 最佳实践

### 1. 技能创建规范

```markdown
---
# 必需字段
name: skill-name              # 技能名称（必需）
description: 技能描述        # 简短描述（必需）

# 推荐字段
tags: [category, subcategory] # 标签（推荐）
version: "1.0.0"             # 版本号（推荐）
tech_stack: [python, js]     # 技术栈（可选）
scenarios: [use-case]        # 使用场景（可选）
complexity: medium           # 复杂度（可选）

# 自动管理字段（系统添加）
path: /path/to/SKILL.md     # 系统自动添加
file_hash: abc123           # 系统自动添加
last_scanned: 2026-05-04    # 系统自动添加
---

技能内容...
```

### 2. 定期扫描

```yaml
# 推荐配置
discovery:
  scan_frequency: automatic  # 实时监控
  scan_interval_minutes: 5   # 备用定时扫描

  # 定时任务
  scheduled_tasks:
    hourly-skill-scan:
      cron: "0 * * * *"      # 每小时扫描一次
      prompt: "skills discovery scan"
```

### 3. 路径配置

```yaml
# 推荐的扫描路径配置
scan_paths:
  # 官方插件（只读）
  - path: ~/.claude/plugins/marketplaces/claude-plugins-official
    type: official
    recursive: true

  # 本地插件（可编辑）
  - path: ~/.claude/plugins/local/skills
    type: local
    recursive: true

  # 项目特定
  - path: ./.claude/skills
    type: project
    recursive: true

  # NPM 全局
  - path: ~/.claude/node_modules
    type: npm_global
    recursive: true

  # NPM 本地
  - path: ./node_modules
    type: npm_local
    recursive: true
```

## 故障排查

### 问题：技能没有被发现

```bash
# 检查路径配置
$ skills discovery status

# 手动扫描
$ skills discovery scan --verbose

# 检查文件权限
$ ls -la ~/.claude/plugins/local/skills/my-skill/SKILL.md

# 验证技能格式
$ skills validate ~/.claude/plugins/local/skills/my-skill/SKILL.md
```

### 问题：文件监控不工作

```bash
# 检查依赖
$ pip install watchdog

# 重启监控
$ skills discovery monitor restart

# 查看日志
$ tail -f ~/.claude/skills-management/logs/scanner.log
```

### 问题：重复技能

```bash
# 查看重复技能
$ skills discovery duplicates

# 自动去重
$ skills discovery dedupe
```

## 总结

通过这个自动发现机制：

✅ **全面覆盖** - 支持所有安装方式
✅ **实时监控** - 文件变化即时响应
✅ **自动注册** - 无需手动添加
✅ **智能更新** - 检测变更自动更新
✅ **多源管理** - 统一管理不同来源的技能

无论用户如何创建或安装技能，都能被系统自动发现和管理！

---

**文档版本**: 1.0
**最后更新**: 2026-05-04
**作者**: Claude Code
