"""
Main CLI entry point for strataregula.
"""

import sys
import warnings

# Early compatibility check before heavy imports
def check_basic_compatibility():
    """Basic compatibility check before importing heavy dependencies."""
    if sys.version_info < (3, 8):
        print(f"❌ Error: Python {sys.version_info[0]}.{sys.version_info[1]} is not supported.")
        print("   Strataregula requires Python 3.8 or newer.")
        if "pyenv" in sys.executable:
            print("   💡 Detected pyenv. Try:")
            print("      pyenv install 3.9.16")
            print("      pyenv global 3.9.16")
            print("      pip install --upgrade strataregula")
        sys.exit(1)

check_basic_compatibility()

# Now safe to import dependencies
import click

# Safe imports with fallbacks
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    warnings.warn("Rich not available. Using basic console output.", RuntimeWarning)
    RICH_AVAILABLE = False
    # Fallback console class
    class Console:
        def print(self, *args, **kwargs):
            print(*args)
        def print_exception(self):
            import traceback
            traceback.print_exc()

from .compile_command import compile_cmd
from ..core.compatibility import check_environment_compatibility

console = Console()


@click.group()
@click.version_option(version="0.2.0", prog_name="strataregula")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--quiet', '-q', is_flag=True, help='Suppress output')
@click.pass_context
def cli(ctx, verbose, quiet):
    """Strataregula - Layered Configuration Management with Strata Rules Architecture.
    
    A powerful tool for hierarchical configuration pattern expansion,
    supporting wildcard patterns and regional mapping.
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['quiet'] = quiet
    
    if verbose:
        console.print("[bold blue]Verbose mode enabled[/bold blue]")
    
    if not quiet:
        console.print(Panel(
            Text("Strataregula", style="bold blue"),
            subtitle="Layered Configuration Management with Strata Rules Architecture",
            border_style="blue"
        ))


# @cli.command()
# @click.argument('input_file', required=False)
# @click.option('--stdin', '-i', is_flag=True, help='Read from STDIN')
# @click.option('--format', '-f', default='auto', 
#               type=click.Choice(['yaml', 'yml', 'json', 'text', 'auto']),
#               help='Input format (auto-detect if not specified)')
# @click.option('--output', '-o', help='Output file (default: STDOUT)')
# @click.option('--output-format', '-of', default='yaml',
#               type=click.Choice(['yaml', 'yml', 'json', 'text']),
#               help='Output format')
# @click.option('--pipeline', '-p', help='Pipeline configuration file')
# @click.option('--command', '-c', multiple=True, help='Command to execute')
# @click.pass_context
# def process(ctx, input_file, stdin, format, output, output_format, pipeline, command):
#     """Process input data through commands or pipeline."""
#     # Temporarily disabled - requires missing commands module
#     pass


# @cli.command()
# @click.argument('name')
# @click.option('--description', '-d', help='Pipeline description')
# @click.option('--input-format', '-if', default='auto',
#               type=click.Choice(['yaml', 'yml', 'json', 'text', 'auto']),
#               help='Input format')
# @click.option('--output-format', '-of', default='yaml',
#               type=click.Choice(['yaml', 'yml', 'json', 'text']),
#               help='Output format')
# @click.option('--command', '-c', multiple=True, help='Command to add')
# @click.option('--save', '-s', help='Save pipeline to file')
# @click.pass_context
# def create(ctx, name, description, input_format, output_format, command, save):
#     """Create a new pipeline."""
#     # Temporarily disabled - requires missing commands module
#     pass


# @cli.command()
# @click.option('--category', '-c', help='Filter by category')
# @click.option('--search', '-s', help='Search commands')
# @click.pass_context
# def list(ctx, category, search):
#     """List available commands and pipelines."""
#     # Temporarily disabled - requires missing commands module
#     pass


# @cli.command()
# @click.argument('pipeline_name')
# @click.argument('input_file', required=False)
# @click.option('--stdin', '-i', is_flag=True, help='Read from STDIN')
# @click.option('--output', '-o', help='Output file')
# @click.pass_context
# def run(ctx, pipeline_name, input_file, stdin, output):
#     """Run a saved pipeline."""
#     # Temporarily disabled - requires missing commands module
#     pass


@cli.command()
def examples():
    """Show usage examples."""
    examples_text = """
[bold]Basic Usage:[/bold]

[blue]Process YAML file:[/blue]
  strataregula process config.yaml

[blue]Process from STDIN:[/blue]
  cat config.yaml | strataregula process --stdin

[blue]Apply commands:[/blue]
  strataregula process config.yaml -c "filter:condition='item.active'" -c "transform:expression='data.items'"

[blue]Create pipeline:[/blue]
  strataregula create my-pipeline -d "Process user configs" -c "filter:condition='user.enabled'" -s pipeline.yaml

[blue]Run pipeline:[/blue]
  strataregula run my-pipeline config.yaml

[bold]Advanced Usage:[/bold]

[blue]Chain multiple commands:[/blue]
  strataregula process input.yaml \\
    -c "filter:condition='item.type == \"user\"'" \\
    -c "transform:expression='[u for u in data if u.get(\"active\")]'" \\
    -c "echo"

[blue]Use with other tools:[/blue]
  cat data.yaml | strataregula process --stdin | jq '.items[] | select(.active)'
    """
    
    if RICH_AVAILABLE:
        console.print(Panel(examples_text, title="Usage Examples", border_style="blue"))
    else:
        print("Usage Examples:")
        print("=" * 50)
        print(examples_text.replace("[bold]", "").replace("[/bold]", "").replace("[blue]", "").replace("[/blue]", ""))


@cli.command()
@click.option('--fix-suggestions', '-f', is_flag=True, help='Show fix suggestions for issues')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed diagnostic information')
def doctor(fix_suggestions, verbose):
    """Check environment compatibility and diagnose issues."""
    if RICH_AVAILABLE:
        console.print("[bold blue]🔍 Running Strataregula Environment Check...[/bold blue]\n")
    else:
        print("🔍 Running Strataregula Environment Check...\n")
    
    try:
        from ..core.compatibility import print_compatibility_report, check_environment_compatibility
        
        if verbose:
            # Show detailed report
            is_compatible = print_compatibility_report()
        else:
            # Show basic compatibility info
            report = check_environment_compatibility()
            is_compatible = report['compatible']
            
            if is_compatible:
                console.print("✅ [bold green]Environment is compatible![/bold green]")
            else:
                console.print("❌ [bold red]Environment issues detected[/bold red]")
                for issue in report['issues'][:3]:  # Show first 3 issues
                    console.print(f"   • {issue}")
                if len(report['issues']) > 3:
                    console.print(f"   • ... and {len(report['issues']) - 3} more issues")
        
        if not is_compatible and (fix_suggestions or click.confirm('\n❓ Would you like to see detailed fix suggestions?')):
            show_fix_suggestions()
        elif is_compatible and verbose:
            console.print("\n[green]All checks passed! Your environment is ready for StrataRegula.[/green]")
            
    except ImportError as e:
        console.print(f"[red]Could not run full compatibility check: {e}[/red]")
        console.print("[yellow]Basic check passed, but some features may be unavailable.[/yellow]")


def show_fix_suggestions():
    """Show detailed fix suggestions for common issues."""
    suggestions = """
🛠️  FIX SUGGESTIONS:

For pyenv users:
1. Update to a newer Python version:
   pyenv install 3.9.16
   pyenv global 3.9.16

2. Recreate your environment:
   pyenv virtualenv 3.9.16 strataregula-clean
   pyenv activate strataregula-clean
   pip install --upgrade pip
   pip install strataregula

3. If using an older pyenv Python:
   pip install --upgrade --force-reinstall strataregula

For conda users:
   conda update python
   pip install --upgrade strataregula

For system Python:
   python -m pip install --upgrade pip
   python -m pip install --upgrade strataregula

If problems persist:
   pip uninstall strataregula
   pip install strataregula --no-cache-dir
    """
    
    if RICH_AVAILABLE:
        console.print(Panel(suggestions, title="Fix Suggestions", border_style="yellow"))
    else:
        print(suggestions)


# Add compile command to CLI
cli.add_command(compile_cmd, name='compile')


def main():
    """Main entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        console.print_exception()
        sys.exit(1)


if __name__ == '__main__':
    main()
