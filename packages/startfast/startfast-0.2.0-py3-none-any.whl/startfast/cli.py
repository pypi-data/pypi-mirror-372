"""
StartFast CLI - Instant professional FastAPI projects
The Django-admin startproject for FastAPI developers who value their time
"""

import argparse
import os
import sys
import time
from typing import Optional, Dict, Any, List
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich.live import Live
from rich import box
from rich.padding import Padding
from rich.rule import Rule
from rich.theme import Theme

from .core.config import ProjectConfig, ProjectType, DatabaseType, AuthType
from .generators.project_generator import ProjectGenerator

# Console with developer-friendly theme
from rich.theme import Theme

console = Console(
    theme=Theme({
        "primary": "bright_cyan",
        "success": "bright_green", 
        "warning": "yellow",
        "error": "red",
        "muted": "dim white",
        "accent": "magenta"
    }),
    highlight=False  # Don't auto-highlight, we'll be intentional
)

class StartFastCLI:
    """Professional FastAPI project generator for developers"""
    
    def __init__(self):
        self.console = console
        
    def create_argument_parser(self) -> argparse.ArgumentParser:
        """Argument parser optimized for developer workflow"""
        parser = argparse.ArgumentParser(
            description="StartFast - Instant professional FastAPI projects",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  startfast my-api                          # Production-ready project, PostgreSQL + JWT
  startfast my-api --db sqlite              # Development setup  
  startfast my-api --db mongo --auth oauth # Custom stack
  startfast --interactive                   # Full customization mode
            """
        )

        parser.add_argument("name", nargs='?', help="Project name")
        parser.add_argument("--path", default=".", help="Directory for project")
        
        # Core stack choices (the ones that actually matter)
        parser.add_argument("--db", "--database", 
                          choices=["postgres", "mysql", "sqlite", "mongo"], 
                          default="postgres",
                          help="Database (default: postgres)")
        
        parser.add_argument("--auth", 
                          choices=["jwt", "oauth2", "api-key", "none"],
                          default="jwt", 
                          help="Auth method (default: jwt)")
        
        parser.add_argument("--minimal", action="store_true",
                          help="Minimal setup (no Docker, tests, or extras)")
        
        # Power user options
        parser.add_argument("--celery", action="store_true", help="Add Celery background tasks")
        parser.add_argument("--monitoring", action="store_true", help="Add Prometheus + health checks")
        parser.add_argument("--python", default="3.11", help="Python version")
        
        # Workflow options
        parser.add_argument("-f", "--force", action="store_true", help="Overwrite existing directory")
        parser.add_argument("-q", "--quiet", action="store_true", help="Minimal output")
        parser.add_argument("--interactive", action="store_true", help="Interactive customization")
        parser.add_argument("--dry-run", action="store_true", help="Show what would be created")
        
        return parser

    def show_banner(self):
        """Clean, confident banner"""
        title = Text("StartFast", style="bold bright_cyan")
        subtitle = Text("Professional FastAPI projects, instantly", style="muted")
        
        console.print()
        console.print(Align.center(title))
        console.print(Align.center(subtitle))
        console.print()

    def detect_existing_project(self, path: str) -> Optional[str]:
        """Smart detection of existing projects"""
        if os.path.exists(os.path.join(path, "main.py")):
            return "FastAPI project"
        elif os.path.exists(os.path.join(path, "manage.py")):
            return "Django project"
        elif os.path.exists(os.path.join(path, "app.py")):
            return "Flask project"
        elif os.path.exists(os.path.join(path, "package.json")):
            return "Node.js project"
        return None

    def quick_start_flow(self, name: str, path: str = ".") -> ProjectConfig:
        """Fast path: smart defaults with escape hatch"""
        project_path = os.path.join(path, name)
        
        # Check for existing project
        existing = self.detect_existing_project(project_path)
        if existing:
            console.print(f"[warning]Found {existing} in {project_path}[/]")
            if not Confirm.ask("Replace it?", default=False):
                console.print("[muted]Cancelled[/]")
                sys.exit(0)
        
        console.print(f"[primary]Creating {name}[/] with production defaults...")
        console.print("[muted]PostgreSQL • JWT Auth • Docker • Tests • Async[/]")
        
        # Quick customization offer
        console.print()
        customize = Confirm.ask("[muted]Customize database or auth?[/]", default=False)
        
        if customize:
            return self.minimal_customization(name, project_path)
        
        # Production defaults
        return ProjectConfig(
            name=name,
            path=project_path,
            project_type=ProjectType.CRUD,
            database_type=DatabaseType.POSTGRESQL,
            auth_type=AuthType.JWT,
            include_docker=True,
            include_tests=True,
            include_docs=True,
            include_monitoring=False,
            include_celery=False,
            python_version="3.11"
        )

    def minimal_customization(self, name: str, project_path: str) -> ProjectConfig:
        """Essential choices only"""
        console.print()
        
        # Database choice (the one that actually impacts development)
        db_options = [
            ("postgres", "PostgreSQL", "Production-ready, full features"),
            ("sqlite", "SQLite", "Development, zero setup"),
            ("mysql", "MySQL", "High performance, wide compatibility"),
            ("mongo", "MongoDB", "Document store, flexible schema")
        ]
        
        console.print("[primary]Database:[/]")
        for i, (key, name_db, desc) in enumerate(db_options, 1):
            marker = "•" if key != "postgres" else "• [success](recommended)[/]"
            console.print(f"  {i}. {marker} [bright_white]{name_db}[/] [muted]- {desc}[/]")
        
        db_choice = IntPrompt.ask("", default=1, choices=["1", "2", "3", "4"])
        db_key = db_options[db_choice - 1][0]
        db_mapping = {"postgres": DatabaseType.POSTGRESQL, "sqlite": DatabaseType.SQLITE,
                     "mysql": DatabaseType.MYSQL, "mongo": DatabaseType.MONGODB}
        database_type = db_mapping[db_key]
        
        # Auth choice (the other critical decision)
        auth_options = [
            ("jwt", "JWT tokens", "Standard, stateless auth"),
            ("oauth2", "OAuth2 + scopes", "Enterprise, fine-grained permissions"),
            ("api-key", "API keys", "Simple, service-to-service"),
            ("none", "No auth", "Open API, internal use")
        ]
        
        console.print("\n[primary]Authentication:[/]")
        for i, (key, name_auth, desc) in enumerate(auth_options, 1):
            marker = "•" if key != "jwt" else "• [success](recommended)[/]"
            console.print(f"  {i}. {marker} [bright_white]{name_auth}[/] [muted]- {desc}[/]")
        
        auth_choice = IntPrompt.ask("", default=1, choices=["1", "2", "3", "4"])
        auth_key = auth_options[auth_choice - 1][0]
        auth_mapping = {"jwt": AuthType.JWT, "oauth2": AuthType.OAUTH2,
                       "api-key": AuthType.API_KEY, "none": AuthType.NONE}
        auth_type = auth_mapping[auth_key]
        
        return ProjectConfig(
            name=name,
            path=project_path,
            project_type=ProjectType.CRUD,
            database_type=database_type,
            auth_type=auth_type,
            include_docker=True,
            include_tests=True,
            include_docs=True,
            include_monitoring=False,
            include_celery=False,
            python_version="3.11"
        )

    def power_user_flow(self) -> ProjectConfig:
        """Full customization for when you need it"""
        self.show_banner()
        console.print("[primary]Full customization mode[/]")
        console.print()
        
        # Project name and path
        name = Prompt.ask("[primary]Project name[/]")
        while not name or not name.replace('-', '').replace('_', '').isalnum():
            console.print("[error]Invalid name. Use letters, numbers, hyphens, underscores.[/]")
            name = Prompt.ask("[primary]Project name[/]")
        
        path = Prompt.ask("[primary]Create in[/]", default=".")
        project_path = os.path.join(path, name)
        
        # Project type (business logic matters here)
        console.print("\n[primary]What are you building?[/]")
        type_options = [
            (ProjectType.API, "Simple API", "Basic endpoints, CRUD operations"),
            (ProjectType.CRUD, "Full backend", "User management, complex data models, production-ready")
        ]
        
        for i, (ptype, name_type, desc) in enumerate(type_options, 1):
            console.print(f"  {i}. [bright_white]{name_type}[/] [muted]- {desc}[/]")
        
        type_choice = IntPrompt.ask("", default=2, choices=["1", "2", "3"])
        project_type = type_options[type_choice - 1][0]
        
        # Database
        db_mapping = {"postgres": DatabaseType.POSTGRESQL, "mysql": DatabaseType.MYSQL, 
                     "sqlite": DatabaseType.SQLITE, "mongo": DatabaseType.MONGODB}
        
        console.print(f"\n[primary]Database[/] [muted](current: PostgreSQL)[/]")
        db_input = Prompt.ask("postgres/mysql/sqlite/mongo", default="postgres")
        database_type = db_mapping.get(db_input.lower(), DatabaseType.POSTGRESQL)
        
        # Auth
        auth_mapping = {"jwt": AuthType.JWT, "oauth2": AuthType.OAUTH2,
                       "api-key": AuthType.API_KEY, "none": AuthType.NONE}
        
        console.print(f"\n[primary]Auth method[/] [muted](current: JWT)[/]")
        auth_input = Prompt.ask("jwt/oauth2/api-key/none", default="jwt")
        auth_type = auth_mapping.get(auth_input.lower(), AuthType.JWT)
        
        # Advanced features
        console.print(f"\n[primary]Additional features[/] [muted](optional)[/]")
        include_celery = Confirm.ask("Background tasks (Celery)", default=False)
        include_monitoring = Confirm.ask("Monitoring (Prometheus, health checks)", default=False)
        
        return ProjectConfig(
            name=name,
            path=project_path,
            project_type=project_type,
            database_type=database_type,
            auth_type=auth_type,
            include_docker=True,
            include_tests=True,
            include_docs=True,
            include_monitoring=include_monitoring,
            include_celery=include_celery,
            python_version="3.11"
        )

    def create_config_from_args(self, args) -> ProjectConfig:
        """Convert CLI args to config"""
        if not args.name:
            console.print("[error]Project name required[/]")
            console.print("[muted]Try: startfast my-api[/]")
            sys.exit(1)
            
        project_path = os.path.join(args.path, args.name)
        
        # Handle existing directory
        if os.path.exists(project_path) and not args.force:
            existing = self.detect_existing_project(project_path)
            if existing:
                console.print(f"[warning]Found {existing} in {project_path}[/]")
            if not Confirm.ask("Replace it?", default=False):
                console.print("[muted]Cancelled[/]")
                sys.exit(0)
        
        # Map CLI args to enums
        db_mapping = {"postgres": DatabaseType.POSTGRESQL, "mysql": DatabaseType.MYSQL,
                     "sqlite": DatabaseType.SQLITE, "mongo": DatabaseType.MONGODB}
        auth_mapping = {"jwt": AuthType.JWT, "oauth2": AuthType.OAUTH2, 
                       "api-key": AuthType.API_KEY, "none": AuthType.NONE}
        
        if args.minimal:
            project_type = ProjectType.API
        else:
            project_type = ProjectType.CRUD
            
        return ProjectConfig(
            name=args.name,
            path=project_path,
            project_type=project_type,
            database_type=db_mapping[args.db],
            auth_type=auth_mapping[args.auth],
            include_docker=not args.minimal,
            include_tests=not args.minimal,
            include_docs=not args.minimal,
            include_monitoring=args.monitoring,
            include_celery=args.celery,
            python_version=args.python
        )

    def show_config_preview(self, config: ProjectConfig, dry_run: bool = False):
        """Clean, scannable config summary"""
        action = "Would create" if dry_run else "Creating"
        console.print(f"\n[success]{action}[/] [bright_white]{config.name}[/]")
        
        # Essential info only
        details = [
            f"Database: {config.database_type.value}",
            f"Auth: {config.auth_type.value}",
            f"Python: {config.python_version}"
        ]
        
        if config.include_celery:
            details.append("Celery: Yes")
        if config.include_monitoring:
            details.append("Monitoring: Yes")
            
        console.print("[muted]" + " • ".join(details) + "[/]")
        
        if not dry_run and not Confirm.ask("\nProceed?", default=True):
            console.print("[muted]Cancelled[/]")
            sys.exit(0)

    def generate_with_progress(self, config: ProjectConfig):
        """Efficient progress display"""
        with console.status("[primary]Generating project...[/]", spinner="dots") as status:
            # Actual generation
            generator = ProjectGenerator(config)
            generator.generate()
            time.sleep(0.5)  # Brief pause for perception of completion

    def show_completion(self, config: ProjectConfig, quiet: bool = False):
        """Success message optimized for next action"""
        if quiet:
            console.print(f"[success]✓[/] {config.name}")
            return
            
        console.print(f"\n[success]✓[/] [bright_white]{config.name}[/] ready")
        
        # Immediate next steps (what they actually need)
        console.print(f"\n[primary]cd {config.name}[/]")
        console.print("[primary]pip install -r requirements.txt[/]") 
        console.print("[primary]uvicorn app.main:app --reload[/]")
        
        # Useful endpoints
        console.print(f"\n[muted]API docs: http://localhost:8000/docs[/]")
        if config.auth_type != AuthType.NONE:
            console.print(f"[muted]Auth: POST /auth/login[/]")

    def main(self):
        """Main entry point with intelligent flow detection"""
        try:
            parser = self.create_argument_parser()
            args = parser.parse_args()
            
            # Flow routing based on user intent
            if args.interactive:
                # Power user wants full control
                config = self.power_user_flow()
            elif args.name:
                # CLI user with specific requirements  
                config = self.create_config_from_args(args)
            else:
                # Interactive quick start (most common)
                self.show_banner()
                name = Prompt.ask("[primary]Project name[/]")
                config = self.quick_start_flow(name, args.path)
            
            # Show what we're about to do
            if not args.quiet:
                self.show_config_preview(config, args.dry_run)
            
            if args.dry_run:
                return
                
            # Generate the project
            self.generate_with_progress(config)
            
            # Show completion with next steps
            self.show_completion(config, args.quiet)
            
        except KeyboardInterrupt:
            console.print("\n[muted]Cancelled[/]")
            sys.exit(1)
        except Exception as e:
            console.print(f"\n[error]Error: {e}[/]")
            sys.exit(1)


def main():
    """Entry point"""
    cli = StartFastCLI()
    cli.main()


if __name__ == "__main__":
    main()