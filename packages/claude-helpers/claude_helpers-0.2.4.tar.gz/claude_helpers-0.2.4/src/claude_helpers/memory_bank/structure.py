"""Memory-Bank structure management."""

from pathlib import Path
from datetime import datetime
from typing import List
import yaml


# Memory-Bank structure definition with validation criteria
MEMORY_BANK_STRUCTURE = {
    'project/product-context.md': {
        'validation': [
            'Has YAML header with datetime?',
            'Contains business intent section?',
            'Defines target audience?',
            'Lists constraints?'
        ]
    },
    'project/project-brief.md': {
        'validation': [
            'Has YAML header with datetime?',
            'Defines project goals?',
            'Sets boundaries?',
            'Contains KPIs?'
        ]
    },
    'design/design-context.md': {
        'validation': [
            'Maps features and boundaries?',
            'Defines components and interfaces?',
            'Shows dependencies graph?',
            'Each feature has clear context boundary?'
        ]
    },
    'design/design-validation.md': {
        'validation': [
            'Lists E2E criteria for features?',
            'All criteria measurable?',
            'DoD clearly defined?'
        ]
    },
    'design/TechContext/code-style.md': {
        'validation': [
            'Has YAML header with datetime?',
            'Defines coding standards?',
            'Lists naming conventions?',
            'Specifies formatting rules?'
        ]
    },
    'design/TechContext/system-patterns.md': {
        'validation': [
            'Has YAML header with datetime?',
            'Documents architectural patterns?',
            'Lists design principles?',
            'Defines integration patterns?'
        ]
    },
    'work/progress.md': {
        'validation': [
            'Aggregates all milestone timestamps?',
            'Shows completion percentage?',
            'Current state accurate?'
        ]
    },
    'work/project-changes-log.md': {
        'validation': [
            'All changes have datetime?',
            'Changes linked to features/epics?',
            'Author role specified?'
        ]
    }
}

# Directories to create (without files)
MEMORY_BANK_DIRS = [
    'project',
    'design',
    'design/TechContext',
    'design/features',
    'work',
    'work/Sessions'
]


def create_memory_bank_structure(base_path: Path, project_name: str) -> None:
    """Create Memory-Bank directory structure with empty files."""
    
    # Create base directory
    memory_bank_path = base_path / "memory-bank"
    memory_bank_path.mkdir(exist_ok=True)
    
    # Create metadata file
    meta_file = memory_bank_path / ".memory-bank-meta.yaml"
    meta_data = {
        'version': '1.0',
        'created_at': datetime.now().isoformat(),
        'project_name': project_name,
        'description': f'Memory-Bank repository for {project_name}'
    }
    
    with open(meta_file, 'w') as f:
        yaml.dump(meta_data, f, default_flow_style=False)
    
    # Create directories
    for dir_path in MEMORY_BANK_DIRS:
        (memory_bank_path / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Create empty files with minimal YAML headers
    for file_path in MEMORY_BANK_STRUCTURE.keys():
        full_path = memory_bank_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file with minimal YAML header
        yaml_header = f"""---
datetime: {datetime.now().isoformat()}
type: {file_path.split('/')[-1].replace('.md', '')}
---

"""
        full_path.write_text(yaml_header)


def validate_memory_bank_path(path: Path) -> bool:
    """Check if path contains valid Memory-Bank structure."""
    
    # Check for metadata file
    meta_file = path / ".memory-bank-meta.yaml"
    if not meta_file.exists():
        return False
    
    # Check for required directories
    for dir_path in ['project', 'design', 'work']:
        if not (path / dir_path).is_dir():
            return False
    
    return True


def get_validation_criteria(artifact_path: str) -> List[str]:
    """Get validation criteria for specific artifact."""
    
    if artifact_path in MEMORY_BANK_STRUCTURE:
        return MEMORY_BANK_STRUCTURE[artifact_path]['validation']
    return []


def create_release_based_structure(base_path: Path, project_name: str) -> None:
    """Create new increment-based Memory-Bank structure."""
    
    # Create main directories for increment-based structure
    directories = [
        "product",
        "product/releases",
        "architecture",
        "architecture/tech-context",
        "architecture/decisions",
        "implementation",
        "implementation/releases",
        "progress",
        "progress/releases",
        "progress/project-changelog",
        "templates",
        "templates/workflow",
        "templates/workflow/memory-bank",
        "templates/workflow/pm",
        "templates/workflow/pm/agents",
        "templates/progress",
        "templates/implementation",
    ]
    
    for dir_path in directories:
        (base_path / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Templates directory structure is created by spawn-templates command
    
    # Create README.md
    readme_content = f"""# Memory Bank Repository

## Structure Index

```
{project_name}/
├── README.md
├── CLAUDE.md
│
├── product/
│   ├── vision.md
│   └── releases/
│       └── {{01-release-name}}.md
│
├── architecture/
│   ├── current.md
│   ├── tech-context/
│   │   ├── code-style.md
│   │   └── system-patterns.md
│   └── releases/
│       └── {{01-release-name}}/
│           ├── overview.md
│           └── components/
│               └── {{component-name-01}}.md
│
├── implementation/
│   └── releases/
│       └── {{01-release-name}}/
│           ├── index.md
│           └── components/
│               └── {{01-component-name}}/
│                   ├── component.md
│                   ├── decomposition.md
│                   ├── initial-state.md
│                   └── increments/
│                       ├── 01-initial-setup.md
│                       ├── 02-core-logic.md
│                       └── 03-integration.md
│
├── progress/
│   ├── project-changelog/
│   │   └── {{001-change-description}}.md
│   └── releases/
│       └── {{01-release-name}}/
│           └── components/
│               └── {{01-component-name}}/
│                   ├── progress-state.md
│                   └── increments/
│                       ├── 01-initial-setup/
│                       │   ├── journal.md
│                       │   ├── pm-focus.md
│                       │   ├── dev-focus.md
│                       │   └── tech-lead-focus.md
│                       └── 02-core-logic/
│                           └── ...
│
└── templates/
    ├── workflow/
    │   ├── memory-bank/
    │   │   ├── ask-memory-bank.md
    │   │   ├── increment-implementation-overview.md
    │   │   └── product-distillation.md
    │   └── pm/
    │       └── implement-component.md
    ├── progress/
    │   ├── pm-focus.md
    │   ├── dev-focus.md
    │   ├── tech-lead-focus.md
    │   ├── journal-template.md
    │   └── progress-state-template.md
    └── sub-agents/
        ├── dev-specialist.md
        └── tech-lead-specialist.md
```

## Naming Conventions

| Type | Format | Example |
|------|--------|---------|
| Release | `01-{{name}}` | `01-pre-alpha` |
| Increment | `{{nn}}-{{name}}.md` | `01-initial-setup.md`, `02-core-logic.md` |
| Component | `{{nn}}-{{name}}` | `01-core-api` |
| Changelog | `{{nnn}}-{{desc}}` | `001-initial-setup` |
"""
    
    (base_path / "README.md").write_text(readme_content)
