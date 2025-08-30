import secrets
import typer
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from rich.console import Console
from rich.panel import Panel

# --- Setup ---
app = typer.Typer()
console = Console()
try:
    TEMPLATE_DIR = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), trim_blocks=True, lstrip_blocks=True)
except Exception:
    console.print("[bold red]Error: 'templates' directory not found.[/bold red]")
    raise typer.Exit()

# --- Helper Functions ---
def render_template(template_name: str, context: dict) -> str:
    """Renders a Jinja2 template with the given context."""
    return env.get_template(template_name).render(context)

def create_resource_files(name: str, base_path: Path, context: dict):
    """
    Helper function to create all files for a new resource.
    It intelligently selects specialized templates for the 'user' resource when auth is enabled.
    """
    context["name"] = name
    context["ClassName"] = name.capitalize()
    context["plural_name"] = name + "s"
    
    # --- Start of new logic ---
    # Default to generic templates
    model_template = "models/model.py.j2"
    schema_template = "schemas/schema.py.j2"

    # If we are creating the 'user' resource AND auth is enabled,
    # swap in the specialized auth templates instead.
    if name == "user" and context.get("use_auth", False):
        model_template = "models/user_auth_model.py.j2"
        schema_template = "schemas/user_auth_schema.py.j2"
    # --- End of new logic ---

    template_map = {
        model_template: f"models/{name}_model.py",
        schema_template: f"schemas/{name}_schema.py",
        "repositories/repo.py.j2": f"repositories/{name}_repo.py",
        "services/service.py.j2": f"services/{name}_service.py",
        "controllers/controller.py.j2": f"controllers/{name}_controller.py",
    }
    
    # Create shared files only if they don't exist
    if not (base_path / "repositories/base_repo.py").exists():
        (base_path / "repositories/base_repo.py").write_text(render_template("repositories/base_repo.py.j2", context))
    if not (base_path / "controllers/dependencies.py").exists():
        (base_path / "controllers/dependencies.py").write_text(render_template("controllers/dependencies.py.j2", context))

    for template, output_file in template_map.items():
        (base_path / output_file).write_text(render_template(template, context))


def inject_line(file_path: Path, new_line: str, marker: str):
    """Injects a new line of code next to a marker if it doesn't already exist."""
    if not file_path.exists():
        return
    
    content = file_path.read_text()
    
    if new_line in content:
        console.print(f"  [yellow]Skipped:[/yellow] '{new_line.strip()}' already exists in {file_path.name}.")
        return

    # Inject the new line before the marker
    new_content = content.replace(marker, f"{new_line}\n{marker}")
    file_path.write_text(new_content)
    console.print(f"  [green]Updated:[/green]  Added '{new_line.strip()}' to {file_path.name}.")

# --- CLI Commands ---
@app.command()
def init():
    # --- This part is mostly the same ---
    console.print(Panel.fit("🚀 [bold green]Fast Boiler: Project Initialization[/bold green]"))
    project_name = typer.prompt("What is the name of your project?")
    context = {"project_name": project_name}
    console.print("\n[bold cyan]Project Configuration:[/bold cyan]")
    context["is_async"] = typer.confirm("▶ Use asynchronous (async/await) code?", default=True)

    # 👇 NEW: Add interactive questions for authentication
    console.print("\n[bold cyan]Core Features:[/bold cyan]")
    context["use_auth"] = typer.confirm("▶ Include FastAPI Users for authentication? (Recommended)", default=True)
    if context["use_auth"]:
        context["use_oauth"] = typer.confirm("  ▶ Add social OAuth login (e.g., Google)?", default=False)
    else:
        context["use_oauth"] = False

    # 👇 MODIFIED: The database choice now intelligently defaults to PostgreSQL if auth is selected
    db_choice = "postgresql" if context["use_auth"] else "sqlite"
    context["db_choice"] = db_choice
    
    if context["is_async"]:
        context["db_driver"] = "asyncpg" if db_choice == "postgresql" else "aiosqlite"
        context["db_url"] = f"postgresql+asyncpg://user:password@host:port/{project_name}" if db_choice == "postgresql" else f"sqlite+aiosqlite:///./app.db"
    else: # Sync
        context["db_driver"] = "psycopg2-binary" if db_choice == "postgresql" else ""
        context["db_url"] = f"postgresql://user:password@host:port/{project_name}" if db_choice == "postgresql" else f"sqlite:///./app.db"

    # 👇 NEW: Generate secrets and OAuth placeholders for the context dictionary
    if context["use_auth"]:
        context["secret_key"] = secrets.token_hex(32)
        if context["use_oauth"]:
            context["google_client_id"] = "your-google-client-id"
            context["google_client_secret"] = "your-google-client-secret"

    console.print(f"\n✅ Configuration complete. Generating project '[bold]{project_name}[/bold]'...")
    
    root_path = Path(project_name)
    app_path = root_path / "app"
    
    # --- Directory generation is now smarter ---
    dirs_to_create = ["controllers", "models", "repositories", "schemas", "services"]
    for dir_name in dirs_to_create:
        (app_path / dir_name).mkdir(parents=True, exist_ok=True)
        (app_path / dir_name / "__init__.py").touch()
    (app_path / "__init__.py").touch()

    # 👇 NEW: Create the auth directory if the user selected it
    if context["use_auth"]:
        (app_path / "auth").mkdir(exist_ok=True)
        (app_path / "auth" / "__init__.py").touch()

    # --- File generation now includes new files ---
    (app_path / "database.py").write_text(render_template("database.py.j2", context))
    (root_path / ".gitignore").write_text(render_template("gitignore.j2", {}))
    (root_path / "requirements.txt").write_text(render_template("requirements.txt.j2", context))
    (root_path / "README.md").write_text(f"# {project_name}\n\nProject generated by fast-boiler.")

    # 👇 NEW: Generate .env files if auth is selected
    if context["use_auth"]:
        (root_path / ".env").write_text(render_template(".env.j2", context))
        (root_path / ".env.example").write_text(render_template(".env.example.j2", context))

    # The user resource is generated (it will be transformed by the templates if auth is on)
    context["default_resource"] = "user"
    (app_path / "models" / "__init__.py").write_text(render_template("models/__init__.py.j2", context))
    create_resource_files("user", base_path=app_path, context=context)

    # 👇 NEW: Generate the specific auth module files
    if context["use_auth"]:
        auth_template_map = {
            "auth/backend.py.j2": "auth/backend.py",
            "auth/database.py.j2": "auth/database.py",
            "auth/manager.py.j2": "auth/manager.py",
            "auth/routers.py.j2": "auth/routers.py",
        }
        if context["use_oauth"]:
            auth_template_map["auth/oauth.py.j2"] = "auth/oauth.py"
        
        for template, output_file in auth_template_map.items():
            (app_path / output_file).write_text(render_template(template, context))

    # This part is the same as before
    (app_path / "main.py").write_text(render_template("main.py.j2", context))
    console.print("\n[bold green]✓ Project generation complete![/bold green]")
    console.print("\nTo get started:")
    console.print(f"  [cyan]cd {project_name}[/cyan]")
    console.print("  [cyan]python3 -m venv venv[/cyan]")
    console.print("  [cyan]source venv/bin/activate[/cyan]")
    console.print("  [cyan]pip install -r requirements.txt[/cyan]")
    console.print("  [cyan]uvicorn app.main:app --reload[/cyan]\n")

@app.command()
def generate(name: str):
    """
    Generates and integrates the files for a new resource.
    """
    console.print(Panel.fit(f"📦 [bold green]Generating new resource: {name}[/bold green]"))
    name = name.lower()
    app_path = Path("app")

    # 1. Sanity Check
    if not app_path.exists() or not (app_path / "main.py").exists():
        console.print("[bold red]Error:[/bold red] This command must be run from the root of a fast-boiler generated project.")
        raise typer.Exit()
    
    # 2. Infer Project State
    database_py = (app_path / "database.py").read_text()
    is_async = "create_async_engine" in database_py
    context = {"is_async": is_async}
    
    # 3. Generate the new resource files
    console.print(f"\n▶ Creating files for '{name}'...")
    create_resource_files(name, base_path=app_path, context=context)
    
    # 4. Auto-include the new resource
    console.print(f"\n▶ Integrating '{name}' into the application...")
    
    # Inject model import
    model_init_path = app_path / "models" / "__init__.py"
    model_import_line = f"from .{name}_model import {name.capitalize()}"
    inject_line(model_init_path, model_import_line, "# V-- Auto-include new models here --V")
    
    # Inject controller import and router
    main_py_path = app_path / "main.py"
    controller_import_line = f"from app.controllers import {name}_controller"
    router_include_line = f"app.include_router({name}_controller.router)"
    inject_line(main_py_path, controller_import_line, "# V-- Auto-include new controllers here --V")
    inject_line(main_py_path, router_include_line, "# V-- Auto-include new routers here --V")
    
    console.print(f"\n[bold green]✓ Resource '{name}' generated and integrated successfully![/bold green]\n")

if __name__ == "__main__":
    app()