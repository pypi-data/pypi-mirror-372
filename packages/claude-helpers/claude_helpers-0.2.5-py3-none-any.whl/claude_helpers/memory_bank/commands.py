"""CLI commands for Memory-Bank module."""

import click
import json
import sys
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from ..config import get_global_config, save_global_config, check_config, MemoryBankProject, MemoryBankConfig
from .models import ProjectBinding
from .structure import create_release_based_structure

console = Console()


@click.group()
def memory_bank():
    """Memory-Bank management for structured development workflows."""
    pass


@memory_bank.command()
def spawn_structure():
    """Create/recreate Memory-Bank directory structure."""
    
    if not check_config():
        console.print(Panel.fit(
            "Global configuration required first.\nRun: claude-helpers setup",
            style="red"
        ))
        return
    
    # Check if memory-bank already exists
    current_dir = Path.cwd()
    
    # Check for existing structure
    if any((current_dir / folder).exists() for folder in ["product", "architecture", "implementation", "progress"]):
        console.print(Panel.fit(
            "Memory-Bank structure already exists in current directory",
            style="yellow"
        ))
        if not Confirm.ask("Do you want to recreate it?"):
            return
    
    # Interactive dialog for project setup
    console.print("\n[bold cyan]Memory-Bank Initialization[/bold cyan]")
    
    # Get project name
    project_name = Prompt.ask(
        "Enter project name (no spaces, English letters)",
        default=current_dir.name.replace(" ", "-").lower()
    )
    
    # Validate project name
    if " " in project_name or not project_name.replace("-", "").replace("_", "").isalnum():
        console.print("[red]Invalid project name. Use only letters, numbers, hyphens and underscores.[/red]")
        return
    
    # Create new release-based structure
    try:
        create_release_based_structure(current_dir, project_name)
        console.print(f"[green]✅ Created Memory-Bank structure in {current_dir}[/green]")
    except Exception as e:
        console.print(f"[red]Failed to create structure: {e}[/red]")
        return
    
    
    # Save to global config
    config = get_global_config()
    
    # Initialize memory_bank config if not exists
    if not hasattr(config, 'memory_bank'):
        config.memory_bank = MemoryBankConfig()
    
    # Add project to config
    config.memory_bank.projects[project_name] = MemoryBankProject(
        name=project_name,
        path=current_dir,
        created_at=datetime.now()
    )
    
    save_global_config(config)
    console.print(f"[green]✅ Registered Memory-Bank '{project_name}' in global config[/green]")
    
    console.print(Panel.fit(
        f"Memory-Bank structure created successfully!\n\n"
        f"Next steps:\n"
        f"1. Run: claude-helpers memory-bank spawn-templates\n"
        f"2. (Optional) Run: claude-helpers memory-bank setup-mcp (for MCP server)\n"
        f"3. Navigate to dev project and run: claude-helpers memory-bank init",
        style="green"
    ))


@memory_bank.command()
def spawn_templates():
    """Create/update Memory-Bank templates from built-in sources."""
    
    # Try to get memory bank path from environment variable or use current directory
    import os
    memory_bank_path_env = os.environ.get('MEMORY_BANK_PATH')
    if memory_bank_path_env:
        current_dir = Path(memory_bank_path_env)
    else:
        current_dir = Path.cwd()
    
    # Check if we're in a Memory-Bank directory
    if not any((current_dir / folder).exists() for folder in ["product", "architecture", "implementation", "progress"]):
        console.print(Panel.fit(
            "Not in a Memory-Bank directory.\nRun: claude-helpers memory-bank spawn-structure first\nOr set MEMORY_BANK_PATH environment variable",
            style="red"
        ))
        return
    
    templates_dir = current_dir / "templates"
    
    if templates_dir.exists():
        console.print(f"[yellow]Templates directory already exists: {templates_dir}[/yellow]")
        if not Confirm.ask("Update templates with latest versions?"):
            return
    
    console.print("\n[bold cyan]Synchronizing Memory-Bank Templates[/bold cyan]")
    
    # Copy templates from template_sources
    import shutil
    templates_src = Path(__file__).parent / "template_sources"
    
    if not templates_src.exists():
        console.print("[red]Template sources not found in claude-helpers installation[/red]")
        return
    
    try:
        created_files = []
        updated_files = []
        
        # Copy all template files from template_sources
        for src_file in templates_src.rglob("*.md"):
            if src_file.is_file():
                rel_path = src_file.relative_to(templates_src)
                dst_file = templates_dir / rel_path
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Track if creating or updating
                if dst_file.exists():
                    updated_files.append(rel_path)
                else:
                    created_files.append(rel_path)
                
                shutil.copy2(src_file, dst_file)
        
        # Report results
        console.print(f"[green]✅ Templates synchronized to {templates_dir}[/green]")
        
        if created_files:
            console.print(f"\n[cyan]Created {len(created_files)} new templates[/cyan]")
        
        if updated_files:
            console.print(f"[yellow]Updated {len(updated_files)} existing templates[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Failed to synchronize templates: {e}[/red]")
        return
    
    console.print(Panel.fit(
        "Templates synchronized successfully!\n\n"
        "Template categories:\n"
        "• workflow/memory-bank - Memory Bank prompts\n"
        "• workflow/pm - PM workflow and agents\n" 
        "• progress - Progress tracking templates\n"
        "• sub-agents - Dev and tech-lead agents",
        style="green"
    ))


# spawn_prompts command removed - functionality merged into spawn_templates


@memory_bank.command()
def setup_mcp():
    """Setup MCP server configuration for current project."""
    
    if not check_config():
        console.print(Panel.fit(
            "Global configuration required first.\nRun: claude-helpers setup",
            style="red"
        ))
        return
    
    current_dir = Path.cwd()
    
    # Check if current directory is a valid Memory-Bank
    required_dirs = ["product", "architecture", "implementation", "progress"]
    is_memory_bank = all((current_dir / d).exists() for d in required_dirs)
    
    if not is_memory_bank:
        console.print(Panel.fit(
            "Not in a Memory-Bank directory.\n"
            f"Required directories: {', '.join(required_dirs)}\n\n"
            "Options:\n"
            "1. Run: claude-helpers memory-bank spawn (to create structure here)\n"
            "2. Navigate to existing Memory-Bank directory",
            style="red"
        ))
        
        if Confirm.ask("Create Memory-Bank structure in current directory?"):
            # Get project name for structure creation
            project_name = Prompt.ask(
                "Enter project name",
                default=current_dir.name.replace(" ", "-").lower()
            )
            
            # Validate project name
            if " " in project_name or not project_name.replace("-", "").replace("_", "").isalnum():
                console.print("[red]Invalid project name. Use only letters, numbers, hyphens and underscores.[/red]")
                return
            
            # Create Memory-Bank structure
            try:
                create_release_based_structure(current_dir, project_name)
                console.print(f"[green]✅ Created Memory-Bank structure in {current_dir}[/green]")
                is_memory_bank = True
            except Exception as e:
                console.print(f"[red]Failed to create structure: {e}[/red]")
                return
        else:
            return
    else:
        # If already a Memory-Bank, try to detect project name from vision.md
        project_name = None
        vision_file = current_dir / "product" / "vision.md"
        if vision_file.exists():
            import re
            content = vision_file.read_text()
            match = re.search(r'Project:\s*(.+)', content)
            if match:
                project_name = match.group(1).strip()
        
        if not project_name:
            project_name = Prompt.ask(
                "Enter project name for MCP server",
                default=current_dir.name.replace(" ", "-").lower()
            )
    
    # Validate project name
    if " " in project_name or not project_name.replace("-", "").replace("_", "").isalnum():
        console.print("[red]Invalid project name. Use only letters, numbers, hyphens and underscores.[/red]")
        return
    
    console.print(f"\n[bold cyan]Setting up MCP server for '{project_name}'[/bold cyan]")
    
    server_name = f"memory-bank-{project_name}"
    
    # Load current config
    config = get_global_config()
    if not hasattr(config, 'memory_bank'):
        config.memory_bank = MemoryBankConfig()
    
    # CRITICAL FIX: Register Memory-Bank project if not already registered
    if project_name not in config.memory_bank.projects:
        console.print(f"[cyan]Registering Memory-Bank '{project_name}' in global config[/cyan]")
        config.memory_bank.projects[project_name] = MemoryBankProject(
            name=project_name,
            path=current_dir,
            created_at=datetime.now()
        )
        save_global_config(config)
        console.print(f"[green]✅ Registered Memory-Bank '{project_name}'[/green]")
    
    # Check if MCP server already exists
    import subprocess
    server_exists = False
    try:
        result = subprocess.run(['claude', 'mcp', 'list'], capture_output=True, text=True)
        server_exists = server_name in result.stdout
    except Exception:
        pass
    
    if server_exists:
        console.print(f"[yellow]MCP server '{server_name}' already exists[/yellow]")
        if not Confirm.ask("Update MCP server configuration?"):
            return
        
        # Remove existing server
        try:
            subprocess.run(['claude', 'mcp', 'remove', server_name], check=True)
            console.print(f"[green]Removed existing server '{server_name}'[/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Failed to remove existing server: {e}[/red]")
            return
    
    # Save MCP server info to config
    config.memory_bank.mcp_servers[server_name] = project_name
    save_global_config(config)
    
    console.print(Panel.fit(
        f"Memory Bank setup complete!\n\n"
        f"Project: {project_name}\n"
        f"Path: {current_dir}\n\n"
        f"Next steps:\n"
        f"1. Navigate to your development project\n"
        f"2. Run: claude-helpers memory-bank init\n"
        f"3. Choose this Memory Bank when prompted",
        style="green"
    ))


@memory_bank.command()
def init():
    """Bind current project to Memory-Bank with release-based structure."""
    
    if not check_config():
        console.print(Panel.fit(
            "Global configuration required first.\nRun: claude-helpers setup",
            style="red"
        ))
        return
    
    config = get_global_config()
    
    # Check if memory_bank config exists
    if not hasattr(config, 'memory_bank') or not config.memory_bank.projects:
        console.print(Panel.fit(
            "No Memory-Banks found.\nRun: claude-helpers memory-bank spawn",
            style="yellow"
        ))
        return
    
    # Check if .helpers exists
    helpers_dir = Path.cwd() / ".helpers"
    if not helpers_dir.exists():
        console.print(Panel.fit(
            "Project not initialized.\nRun: claude-helpers init",
            style="yellow"
        ))
        return
    
    # Interactive binding
    console.print("\n[bold cyan]Memory-Bank Binding[/bold cyan]")
    
    if not Confirm.ask("Bind/rebind Memory-Bank to this project?"):
        console.print("Cancelled")
        return
    
    # List available Memory-Banks
    console.print("\n[bold]Available Memory-Banks:[/bold]")
    projects = list(config.memory_bank.projects.keys())
    
    for i, name in enumerate(projects, 1):
        project = config.memory_bank.projects[name]
        console.print(f"{i}. {name} - {project.path}")
    
    # Choose Memory-Bank
    choice = Prompt.ask(
        "Select Memory-Bank number",
        choices=[str(i) for i in range(1, len(projects) + 1)]
    )
    
    selected_name = projects[int(choice) - 1]
    selected_project = config.memory_bank.projects[selected_name]
    
    # Validate Memory-Bank path exists with new structure
    memory_bank_path = Path(selected_project.path)
    required_dirs = ["product", "architecture", "implementation", "progress"]
    
    if not all((memory_bank_path / d).exists() for d in required_dirs):
        console.print(f"[red]Memory-Bank at {memory_bank_path} has invalid release-based structure[/red]")
        console.print(f"Required directories: {', '.join(required_dirs)}")
        return
    
    # Save binding to .helpers
    binding_file = helpers_dir / "memory_bank.json"
    binding = ProjectBinding(
        memory_bank_name=selected_name,
        memory_bank_path=selected_project.path,
        bound_at=datetime.now()
    )
    
    with open(binding_file, 'w') as f:
        json.dump(binding.model_dump(mode='json'), f, indent=2, default=str)
    
    console.print(f"[green]✅ Bound to Memory-Bank '{selected_name}'[/green]")
    
    # MCP server setup - check if Claude MCP server actually exists
    expected_server_name = f"memory-bank-{selected_name}"
    
    # Check if MCP server exists in Claude (not just our config tracking)
    import subprocess
    claude_server_exists = False
    try:
        result = subprocess.run(['claude', 'mcp', 'list'], capture_output=True, text=True)
        claude_server_exists = expected_server_name in result.stdout
    except Exception:
        pass
    
    if claude_server_exists:
        console.print(f"[green]✅ MCP server '{expected_server_name}' already exists in Claude[/green]")
        
        # Update our tracking if needed
        if expected_server_name not in config.memory_bank.mcp_servers:
            config.memory_bank.mcp_servers[expected_server_name] = selected_name
            save_global_config(config)
            console.print(f"[green]✅ Updated MCP server tracking in global config[/green]")
    else:
        console.print(f"[yellow]⚠️  No MCP server found for project '{selected_name}'[/yellow]")
        if Confirm.ask(f"Create MCP server '{expected_server_name}' in Claude?"):
            mcp_config_obj = {
                "type": "stdio",
                "command": "claude-helpers", 
                "args": ["memory-bank-mcp"]
            }
            
            try:
                subprocess.run([
                    'claude', 'mcp', 'add-json', 
                    expected_server_name,
                    json.dumps(mcp_config_obj)
                ], check=True)
                
                # Save to config
                config.memory_bank.mcp_servers[expected_server_name] = selected_name
                save_global_config(config)
                
                console.print(f"[green]✅ Created MCP server '{expected_server_name}' in Claude[/green]")
            except subprocess.CalledProcessError as e:
                console.print(f"[red]Failed to create MCP server: {e}[/red]")
                console.print(f"[yellow]Manual setup: claude mcp add-json {expected_server_name} '{json.dumps(mcp_config_obj)}'[/yellow]")
                console.print(f"[yellow]Or run: claude-helpers memory-bank setup-mcp[/yellow]")
    
    # Sub-agents Setup from Memory-Bank templates
    console.print("\n[bold cyan]Agent Configuration[/bold cyan]")
    
    # Check if Memory-Bank has templates
    templates_dir = memory_bank_path / "templates"
    if not templates_dir.exists():
        console.print(f"[yellow]No templates found in Memory-Bank.\nRun: claude-helpers memory-bank spawn-templates in {memory_bank_path}[/yellow]")
    else:
        # Ask about copying sub-agents
        if Confirm.ask("Add sub-agents (dev, tech-lead) from Memory Bank?"):
            # Copy sub-agents to project
            import shutil
            # Create .claude/agents directory
            claude_dir = Path.cwd() / ".claude"
            claude_dir.mkdir(exist_ok=True)
            agents_dst = claude_dir / "agents"
            
            # Try multiple locations for sub-agents
            possible_sources = [
                templates_dir / "workflow" / "pm" / "agents",  # New correct location
                templates_dir / "sub-agents",  # Legacy location
            ]
            
            agents_src = None
            for src in possible_sources:
                if src.exists():
                    agents_src = src
                    break
            
            if agents_src:
                agents_dst.mkdir(exist_ok=True)
                
                # Server name for MCP tools replacement
                server_name = f"memory-bank-{selected_name}"
                
                # Copy and update dev.md or dev-specialist.md
                dev_files = [agents_src / "dev.md", agents_src / "dev-specialist.md"]
                for dev_file in dev_files:
                    if dev_file.exists():
                        content = dev_file.read_text()
                        # Replace placeholder with actual server name
                        content = content.replace("{mcp_server_name}", server_name)
                        (agents_dst / "dev-specialist.md").write_text(content)
                        console.print("[green]✅ Created dev-specialist.md[/green]")
                        break
                
                # Copy and update tech-lead.md or tech-lead-specialist.md
                tech_files = [agents_src / "tech-lead.md", agents_src / "tech-lead-specialist.md"]
                for tech_file in tech_files:
                    if tech_file.exists():
                        content = tech_file.read_text()
                        # Replace placeholder with actual server name
                        content = content.replace("{mcp_server_name}", server_name)
                        (agents_dst / "tech-lead-specialist.md").write_text(content)
                        console.print("[green]✅ Created tech-lead-specialist.md[/green]")
                        break
            else:
                # Fallback to built-in templates from claude-helpers
                console.print("[yellow]No Memory Bank templates found, using built-in defaults[/yellow]")
                from pathlib import Path as PathLib
                builtin_src = PathLib(__file__).parent / "template_sources" / "workflow" / "pm" / "agents"
                
                if builtin_src.exists():
                    agents_dst.mkdir(exist_ok=True)
                    
                    # Server name for MCP tools replacement
                    server_name = f"memory-bank-{selected_name}"
                    
                    # Copy built-in dev.md
                    builtin_dev = builtin_src / "dev.md"
                    if builtin_dev.exists():
                        content = builtin_dev.read_text()
                        content = content.replace("{mcp_server_name}", server_name)
                        (agents_dst / "dev-specialist.md").write_text(content)
                        console.print("[green]✅ Created dev-specialist.md (built-in)[/green]")
                    
                    # Copy built-in tech-lead.md
                    builtin_tech = builtin_src / "tech-lead.md"
                    if builtin_tech.exists():
                        content = builtin_tech.read_text()
                        content = content.replace("{mcp_server_name}", server_name)
                        (agents_dst / "tech-lead-specialist.md").write_text(content)
                        console.print("[green]✅ Created tech-lead-specialist.md (built-in)[/green]")
                else:
                    console.print("[red]Failed to find any sub-agent templates[/red]")
        
        # Ask about adding Memory Bank MCP server
        if Confirm.ask("Add Memory Bank MCP server to project?"):
            # Create/update .mcp.json in project
            mcp_file = Path.cwd() / ".mcp.json"
            mcp_config = {}
            
            if mcp_file.exists():
                with open(mcp_file, 'r') as f:
                    mcp_config = json.load(f)
            
            if "servers" not in mcp_config:
                mcp_config["servers"] = {}
            
            mcp_config["servers"][f"memory-bank-{selected_name}"] = {
                "type": "stdio",
                "command": "claude-helpers",
                "args": ["memory-bank-mcp"],
                "cwd": str(Path.cwd())  # Set working directory to current project
            }
            
            with open(mcp_file, 'w') as f:
                json.dump(mcp_config, f, indent=2)
            
            console.print("[green]✅ Added Memory Bank MCP server to .mcp.json[/green]")
    
    console.print(Panel.fit(
        f"Memory-Bank binding complete!\n\n"
        f"Bound to: {memory_bank_path}\n"
        f"Project: {selected_name}\n\n"
        f"Available MCP tools:\n"
        f"• get-pm-focus, get-dev-focus, get-tech-lead-focus\n"
        f"• journal-note, next-increment\n"
        f"• ask-memory-bank\n\n"
        f"Available MCP prompt:\n"
        f"• implement-component\n\n"
        f"Start with MCP prompt: implement-component",
        style="green"
    ))


@memory_bank.command()
def remove_mcp():
    """Remove MCP server configuration."""
    
    if not check_config():
        console.print(Panel.fit(
            "Global configuration required first.\nRun: claude-helpers setup",
            style="red"
        ))
        return
    
    config = get_global_config()
    if not hasattr(config, 'memory_bank') or not config.memory_bank.mcp_servers:
        console.print("[yellow]No MCP servers configured[/yellow]")
        return
    
    console.print("\n[bold cyan]Remove MCP Server[/bold cyan]")
    
    # List configured MCP servers
    servers = list(config.memory_bank.mcp_servers.keys())
    console.print("\n[bold]Configured MCP servers:[/bold]")
    for i, server_name in enumerate(servers, 1):
        project_name = config.memory_bank.mcp_servers[server_name]
        console.print(f"{i}. {server_name} -> {project_name}")
    
    # Choose server to remove
    choice = Prompt.ask(
        "Select server number to remove",
        choices=[str(i) for i in range(1, len(servers) + 1)]
    )
    
    server_to_remove = servers[int(choice) - 1]
    project_name = config.memory_bank.mcp_servers[server_to_remove]
    
    if not Confirm.ask(f"Remove MCP server '{server_to_remove}' for project '{project_name}'?"):
        console.print("Cancelled")
        return
    
    # Remove from Claude MCP
    import subprocess
    try:
        subprocess.run(['claude', 'mcp', 'remove', server_to_remove], check=True)
        console.print(f"[green]✅ Removed MCP server '{server_to_remove}' from Claude[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed to remove from Claude: {e}[/red]")
        console.print("[yellow]You may need to remove manually[/yellow]")
    
    # Remove from config
    del config.memory_bank.mcp_servers[server_to_remove]
    save_global_config(config)
    console.print(f"[green]✅ Removed '{server_to_remove}' from global config[/green]")
    
    console.print(Panel.fit(
        f"MCP server '{server_to_remove}' removed successfully!\n\n"
        f"Project '{project_name}' is no longer configured for MCP access.\n"
        f"You can recreate it with: claude-helpers memory-bank setup-mcp",
        style="green"
    ))


@memory_bank.command(name="list")
def list_projects():
    """List all Memory-Bank projects and their MCP servers."""
    
    if not check_config():
        console.print(Panel.fit(
            "Global configuration required first.\nRun: claude-helpers setup",
            style="red"
        ))
        return
    
    config = get_global_config()
    
    # Check if we have any projects
    if not hasattr(config, 'memory_bank') or not config.memory_bank.projects:
        console.print(Panel.fit(
            "No Memory-Bank projects configured.\n\n"
            "To create a Memory-Bank:\n"
            "1. Navigate to desired directory\n"
            "2. Run: claude-helpers memory-bank spawn\n"
            "   OR: claude-helpers memory-bank setup-mcp",
            style="yellow"
        ))
        return
    
    console.print("\n[bold cyan]Memory-Bank Projects[/bold cyan]")
    console.print("=" * 50)
    
    # Get current binding if exists
    current_binding = None
    helpers_dir = Path.cwd() / ".helpers"
    binding_file = helpers_dir / "memory_bank.json"
    if binding_file.exists():
        try:
            with open(binding_file, 'r') as f:
                binding_data = json.load(f)
                current_binding = binding_data.get('memory_bank_name')
        except Exception:
            pass
    
    # Get actual Claude MCP status
    import subprocess
    claude_servers = set()
    try:
        result = subprocess.run(['claude', 'mcp', 'list'], capture_output=True, text=True)
        claude_servers = set(line.split(':')[0].strip() for line in result.stdout.split('\n') if ':' in line)
    except Exception:
        pass
    
    # Reverse mapping: project_name -> list of server_names
    project_servers = {}
    for server_name, project_name in config.memory_bank.mcp_servers.items():
        if project_name not in project_servers:
            project_servers[project_name] = []
        project_servers[project_name].append(server_name)
    
    # Display each project
    total_servers = 0
    active_servers = 0
    
    for i, (project_name, project) in enumerate(config.memory_bank.projects.items(), 1):
        # Check if this is the current binding
        is_current = project_name == current_binding
        current_marker = " [CURRENT]" if is_current else ""
        
        # Project header
        console.print(f"\n[bold]{i}. {project_name}{current_marker}[/bold]")
        
        # Project details
        console.print(f"   Path: {project.path}")
        console.print(f"   Created: {project.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Check if path exists
        if not Path(project.path).exists():
            console.print("   [red]⚠️  Directory not found[/red]")
        
        # MCP servers for this project
        servers = project_servers.get(project_name, [])
        if servers:
            console.print("   MCP Servers:")
            for server_name in servers:
                total_servers += 1
                if server_name in claude_servers:
                    console.print(f"   - {server_name} [green]✓ Active[/green]")
                    active_servers += 1
                else:
                    console.print(f"   - {server_name} [red]✗ Missing in Claude[/red]")
        else:
            console.print("   MCP Servers: [yellow]None configured[/yellow]")
    
    # Summary
    console.print("\n" + "=" * 50)
    console.print(f"[bold]Total:[/bold] {len(config.memory_bank.projects)} projects, "
                  f"{total_servers} MCP servers ({active_servers} active)")
    
    if total_servers > active_servers:
        console.print("\n[yellow]Some MCP servers are missing from Claude.[/yellow]")
        console.print("To fix: Navigate to project and run: claude-helpers memory-bank setup-mcp")
    
    if current_binding:
        console.print(f"\n[green]Current directory is bound to: {current_binding}[/green]")


@memory_bank.command()
def list_mcp():
    """List only MCP servers (use 'list' for full project view)."""
    
    if not check_config():
        console.print(Panel.fit(
            "Global configuration required first.\nRun: claude-helpers setup",
            style="red"
        ))
        return
    
    config = get_global_config()
    if not hasattr(config, 'memory_bank') or not config.memory_bank.mcp_servers:
        console.print("[yellow]No MCP servers configured[/yellow]")
        console.print("Run: claude-helpers memory-bank setup-mcp")
        return
    
    console.print("\n[bold cyan]MCP Servers Only[/bold cyan]\n")
    console.print("[dim]For full project view, use: claude-helpers memory-bank list[/dim]\n")
    
    import subprocess
    # Get actual Claude MCP status
    claude_servers = set()
    try:
        result = subprocess.run(['claude', 'mcp', 'list'], capture_output=True, text=True)
        claude_servers = set(line.split(':')[0].strip() for line in result.stdout.split('\n') if ':' in line)
    except Exception:
        pass
    
    for server_name, project_name in config.memory_bank.mcp_servers.items():
        status = "✓ Active" if server_name in claude_servers else "✗ Missing"
        status_color = "green" if server_name in claude_servers else "red"
        
        console.print(f"[bold]{server_name}[/bold] -> {project_name}")
        console.print(f"  Status: [{status_color}]{status}[/{status_color}]")
        console.print()
    
    if any(server not in claude_servers for server in config.memory_bank.mcp_servers.keys()):
        console.print("[yellow]Some servers are missing from Claude configuration.[/yellow]")
        console.print("Run: claude-helpers memory-bank setup-mcp to recreate missing servers")


@memory_bank.command()
def remove_project():
    """Remove Memory-Bank project from configuration."""
    
    if not check_config():
        console.print(Panel.fit(
            "Global configuration required first.\nRun: claude-helpers setup",
            style="red"
        ))
        return
    
    config = get_global_config()
    
    if not hasattr(config, 'memory_bank') or not config.memory_bank.projects:
        console.print("[yellow]No Memory-Bank projects configured[/yellow]")
        return
    
    console.print("\n[bold cyan]Remove Memory-Bank Project[/bold cyan]")
    
    # List configured projects
    projects = list(config.memory_bank.projects.keys())
    console.print("\n[bold]Configured Memory-Bank projects:[/bold]")
    for i, project_name in enumerate(projects, 1):
        project = config.memory_bank.projects[project_name]
        console.print(f"{i}. {project_name} -> {project.path}")
    
    # Choose project to remove
    choice = Prompt.ask(
        "Select project number to remove",
        choices=[str(i) for i in range(1, len(projects) + 1)]
    )
    
    project_to_remove = projects[int(choice) - 1]
    project_path = config.memory_bank.projects[project_to_remove].path
    
    if not Confirm.ask(f"Remove Memory-Bank project '{project_to_remove}' from configuration?"):
        console.print("Cancelled")
        return
    
    # Check for associated MCP servers
    associated_servers = [
        server_name for server_name, proj_name in config.memory_bank.mcp_servers.items()
        if proj_name == project_to_remove
    ]
    
    if associated_servers:
        console.print(f"\n[yellow]Found {len(associated_servers)} associated MCP server(s):[/yellow]")
        for server_name in associated_servers:
            console.print(f"  - {server_name}")
        
        if Confirm.ask("Remove associated MCP servers as well?"):
            import subprocess
            for server_name in associated_servers:
                try:
                    subprocess.run(['claude', 'mcp', 'remove', server_name], check=True)
                    console.print(f"[green]✅ Removed MCP server '{server_name}' from Claude[/green]")
                except subprocess.CalledProcessError:
                    console.print(f"[yellow]Could not remove '{server_name}' from Claude (may not exist)[/yellow]")
                
                # Remove from config
                del config.memory_bank.mcp_servers[server_name]
                console.print(f"[green]✅ Removed '{server_name}' from config[/green]")
    
    # Remove project from config
    del config.memory_bank.projects[project_to_remove]
    save_global_config(config)
    
    console.print(f"[green]✅ Removed Memory-Bank project '{project_to_remove}' from configuration[/green]")
    
    console.print(Panel.fit(
        f"Memory-Bank project '{project_to_remove}' removed from configuration.\n\n"
        f"Note: The actual Memory-Bank directory at {project_path}\n"
        f"has NOT been deleted (only removed from config).\n\n"
        f"To re-add it, navigate to the directory and run:\n"
        f"claude-helpers memory-bank setup-mcp",
        style="green"
    ))


@memory_bank.command()
def agent_mcp():
    """Run MCP server for Memory-Bank agent operations."""
    
    if not check_config():
        console.print("[red]Global configuration required[/red]")
        sys.exit(1)
    
    # Check if Memory-Bank is bound to current project
    helpers_dir = Path.cwd() / ".helpers"
    binding_file = helpers_dir / "memory_bank.json"
    
    if not binding_file.exists():
        console.print("[red]Memory-Bank not bound to current project. Run: claude-helpers memory-bank init[/red]")
        sys.exit(1)
    
    # Import and run MCP server
    from .mcp_main import run_mcp_server
    run_mcp_server()


@memory_bank.command()
@click.argument('project_name')
@click.argument('operation', type=click.Choice(['rebuild-progress', 'rebuild-focus', 'validate-structure']))
@click.option('--release', help='Release name for rebuild-focus operation')
@click.option('--component', help='Component name for rebuild-focus operation')
@click.option('--path', help='Path for validate-structure operation')
def helper(project_name: str, operation: str, release: str = None, component: str = None, path: str = None):
    """Memory-Bank helper using Claude Code SDK."""
    
    if not check_config():
        console.print("[red]Global configuration required[/red]")
        return
    
    config = get_global_config()
    
    # Find Memory-Bank
    if not hasattr(config, 'memory_bank') or project_name not in config.memory_bank.projects:
        console.print(f"[red]Memory-Bank '{project_name}' not found[/red]")
        return
    
    project = config.memory_bank.projects[project_name]
    
    # Validate Memory-Bank path with new structure
    memory_bank_path = Path(project.path)
    required_dirs = ["product", "architecture", "implementation", "progress"]
    
    if not all((memory_bank_path / d).exists() for d in required_dirs):
        console.print(f"[red]Memory-Bank at {memory_bank_path} has invalid release-based structure[/red]")
        return
    
    # TODO: Implement operations using Task tool for Claude Code SDK
    console.print(f"[yellow]Operation '{operation}' not yet implemented with new SDK[/yellow]")
    console.print("Available operations will be implemented using Claude Code Task tool")
    
    # Show which parameters were provided (for future implementation)
    if operation == 'rebuild-focus' and (release or component):
        console.print(f"Parameters provided: release={release}, component={component}")
    elif operation == 'validate-structure' and path:
        console.print(f"Parameter provided: path={path}")
    
    return