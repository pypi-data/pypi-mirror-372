#!/usr/bin/env python3
"""
Nova CI-Rescue CLI interface.
"""

import typer
import subprocess
import time
from pathlib import Path
from typing import Optional
from datetime import datetime
from nova.tools.datetime_utils import now_utc, delta_between, seconds_between
from rich.console import Console
from rich.table import Table
from rich.theme import Theme

from nova.runner import TestRunner
from nova.agent import AgentState
from nova.telemetry.logger import JSONLLogger
from nova.config import get_settings
from nova.tools.git import GitBranchManager
from nova.logger import create_logger, set_logger, get_logger

# Define custom theme with softer colors
nova_theme = Theme({
    "error": "#CD5C5C",  # Indian Red - softer than pure red
    "warning": "#DAA520",  # Goldenrod - softer yellow
    "success": "#228B22",  # Forest Green - softer green
    "info": "#4682B4",  # Steel Blue
})

app = typer.Typer(
    name="nova",
    help="Nova CI-Rescue: Automated test fixing agent",
    add_completion=False,
)
console = Console(theme=nova_theme)


def print_exit_summary(state: AgentState, reason: str, elapsed_seconds: float = None, llm_agent=None) -> None:
    """
    Print a comprehensive summary when exiting the agent loop.
    
    Args:
        state: The current agent state
        reason: The reason for exit (timeout, max_iters, success, etc.)
        elapsed_seconds: Optional elapsed time in seconds
    """
    console.print("\n" + "=" * 60)
    console.print("[bold]EXECUTION SUMMARY[/bold]")
    console.print("=" * 60)
    
    # Exit reason with appropriate styling
    if reason == "success":
        console.print(f"[bold green]✅ Exit Reason: SUCCESS - All tests passing![/bold green]")
    elif reason == "timeout":
        console.print(f"[bold red]⏰ Exit Reason: TIMEOUT - Exceeded {state.timeout_seconds}s limit[/bold red]")
    elif reason == "max_iters":
        console.print(f"[bold red]🔄 Exit Reason: MAX ITERATIONS - Reached {state.max_iterations} iterations[/bold red]")
    elif reason == "no_patch":
        console.print(f"[bold yellow]⚠️ Exit Reason: NO PATCH - Could not generate fix[/bold yellow]")
    elif reason == "patch_rejected":
        console.print(f"[bold yellow]⚠️ Exit Reason: PATCH REJECTED - Critic rejected patch[/bold yellow]")
    elif reason == "patch_error":
        console.print(f"[bold red]❌ Exit Reason: PATCH ERROR - Failed to apply patch[/bold red]")
    elif reason == "interrupted":
        console.print(f"[bold yellow]🛑 Exit Reason: INTERRUPTED - User cancelled operation[/bold yellow]")
    elif reason == "error":
        console.print(f"[bold red]❌ Exit Reason: ERROR - Unexpected error occurred[/bold red]")
    else:
        console.print(f"[bold yellow]Exit Reason: {reason.upper()}[/bold yellow]")
    
    console.print()
    
    # Statistics
    console.print("[bold]Statistics:[/bold]")
    console.print(f"  • Iterations completed: {state.current_iteration}/{state.max_iterations}")
    console.print(f"  • Patches applied: {len(state.patches_applied)}")
    console.print(f"  • Initial failures: {state.initial_failures}")
    console.print(f"  • Remaining failures: {state.total_failures}")
    
    if state.total_failures == 0:
        console.print(f"  • [green]All tests fixed successfully![/green]")
    elif state.failing_tests and state.total_failures < len(state.failing_tests):
        fixed = len(state.failing_tests) - state.total_failures
        console.print(f"  • Tests fixed: {fixed}/{len(state.failing_tests)}")
    
    if elapsed_seconds is not None:
        minutes, seconds = divmod(int(elapsed_seconds), 60)
        console.print(f"  • Time elapsed: {minutes}m {seconds}s")
    elif hasattr(state, 'start_time') and state.start_time:
        # Handle both datetime and float start_time
        if isinstance(state.start_time, float):
            elapsed = time.time() - state.start_time
        else:
            elapsed = seconds_between(now_utc(), state.start_time)
        minutes, seconds = divmod(int(elapsed), 60)
        console.print(f"  • Time elapsed: {minutes}m {seconds}s")
    
    # List saved patches if telemetry is enabled
    from nova.config import get_settings
    settings = get_settings()
    if settings.enable_telemetry and hasattr(state, 'telemetry') and state.telemetry:
        try:
            from pathlib import Path
            run_dir = state.telemetry.run_dir
            if run_dir and Path(run_dir).exists():
                patch_dir = Path(run_dir) / "patches"
                if patch_dir.exists():
                    console.print("\n[bold]📄 Saved patches:[/bold]")
                    patches = sorted(patch_dir.glob("*.patch"))
                    if patches:
                        for patch_file in patches:
                            console.print(f"  • {patch_file.name}")
                        console.print(f"  [dim](Saved in: {patch_dir})[/dim]")
                    else:
                        console.print("  [dim](No patches saved)[/dim]")
        except Exception as e:
            if state.verbose:
                console.print(f"[dim]Could not list patches: {e}[/dim]")
    
    # Display token usage in verbose mode
    if verbose and llm_agent and hasattr(llm_agent, 'llm_client') and hasattr(llm_agent.llm_client, 'token_usage'):
        usage = llm_agent.llm_client.token_usage
        if usage['total_tokens'] > 0:
            console.print("\n[bold]🧾 Token Usage Receipt:[/bold]")
            console.print(f"  • Prompt tokens: {usage['prompt_tokens']:,}")
            console.print(f"  • Completion tokens: {usage['completion_tokens']:,}")
            console.print(f"  • Total tokens: {usage['total_tokens']:,}")
            console.print(f"  • API calls: {len(usage['calls'])}")
            
            # Estimate costs based on model
            model = llm_agent.llm_client.model if hasattr(llm_agent.llm_client, 'model') else 'unknown'
            provider = llm_agent.llm_client.provider if hasattr(llm_agent.llm_client, 'provider') else 'unknown'
            
            cost_estimate = 0.0
            if provider == 'openai':
                # OpenAI pricing (approximate)
                if 'gpt-4' in model:
                    cost_estimate = (usage['prompt_tokens'] * 0.03 + usage['completion_tokens'] * 0.06) / 1000
                elif 'gpt-3.5' in model:
                    cost_estimate = (usage['prompt_tokens'] * 0.0005 + usage['completion_tokens'] * 0.0015) / 1000
                elif 'gpt-5' in model:
                    # GPT-5 pricing (estimated)
                    cost_estimate = (usage['prompt_tokens'] * 0.045 + usage['completion_tokens'] * 0.09) / 1000
            elif provider == 'anthropic':
                # Anthropic pricing (approximate)
                if 'claude-3-opus' in model:
                    cost_estimate = (usage['prompt_tokens'] * 0.015 + usage['completion_tokens'] * 0.075) / 1000
                elif 'claude-3-sonnet' in model:
                    cost_estimate = (usage['prompt_tokens'] * 0.003 + usage['completion_tokens'] * 0.015) / 1000
            
            if cost_estimate > 0:
                console.print(f"  • Estimated cost: ${cost_estimate:.4f}")
                console.print(f"  [dim](Model: {model}, Provider: {provider})[/dim]")
    
    console.print("=" * 60)
    console.print()


@app.command()
def fix(
    repo_path: Path = typer.Argument(
        Path("."),
        help="Path to repository to fix",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    max_iters: int = typer.Option(
        5,
        "--max-iters",
        "-i",
        help="Maximum number of fix iterations",
        min=1,
        max=20,
    ),
    timeout: int = typer.Option(
        300,
        "--timeout",
        "-t",
        help="Overall timeout in seconds",
        min=60,
        max=7200,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
    auto_pr: bool = typer.Option(
        False,
        "--auto-pr",
        help="Automatically create PR without prompting",
    ),
    no_telemetry: bool = typer.Option(
        False,
        "--no-telemetry",
        help="Disable telemetry collection for this run",
    ),
    whole_file: bool = typer.Option(
        None,  # Will use config default if not specified
        "--whole-file/--patch-mode",
        "-w/-p",
        help="Replace entire files instead of using patches (default: from config or env NOVA_WHOLE_FILE_MODE)",
    ),
    test: Optional[str] = typer.Option(
        None,
        "--test",
        "-k",
        help="Specific test name or pattern to fix (e.g., 'test_calculator', 'test_add')",
    ),
    pytest_args: Optional[str] = typer.Option(
        None,
        "--pytest-args",
        help="Additional arguments to pass to pytest (e.g., -k 'pattern' -m 'slow')",
    ),
    ci_mode: bool = typer.Option(
        False,
        "--ci",
        help="CI mode: apply fixes to current branch instead of creating new branch",
    ),
):
    """
    Fix failing tests in a repository.
    """
    # Set up the logger based on verbosity
    logger = create_logger(verbose=verbose)
    set_logger(logger)
    
    console.print(f"[green]Nova CI-Rescue[/green] 🚀")
    console.print(f"Repository: {repo_path}")
    console.print(f"Max iterations: {max_iters}")
    console.print(f"Timeout: {timeout}s")
    if verbose:
        # Let underlying components know to print debug logs
        import os as _os
        _os.environ["NOVA_VERBOSE"] = "true"
    # Mode display removed for cleaner output
    
    # Initialize branch manager
    git_manager = GitBranchManager(repo_path, verbose=verbose)
    branch_name: Optional[str] = None
    success = False
    telemetry = None
    state = None
    original_branch = None
    
    # Check for concurrent runs
    from nova.tools.lock import nova_lock
    
    try:
        with nova_lock(repo_path, wait=False):
            # Enforce per-repo run frequency cap
            try:
                settings = get_settings()
                nova_dir = Path(repo_path) / ".nova"
                nova_dir.mkdir(exist_ok=True)
                last_run_file = nova_dir / "last_run.txt"
                import time as _time
                now_ts = int(_time.time())
                if last_run_file.exists():
                    try:
                        last_ts = int(last_run_file.read_text().strip() or "0")
                        if now_ts - last_ts < settings.min_repo_run_interval_sec:
                            remaining = settings.min_repo_run_interval_sec - (now_ts - last_ts)
                            # Frequency cap removed for demo
                            pass
                    except Exception:
                        pass
                # Record start of run
                try:
                    last_run_file.write_text(str(now_ts))
                except Exception:
                    pass
            except Exception:
                pass
            # Check for clean working tree before starting
            if not git_manager._check_clean_working_tree():
                # Uncommitted changes warning removed for demo
                pass
            
            if ci_mode:
                # In CI mode, work on the current branch
                import subprocess
                result = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    capture_output=True,
                    text=True,
                    cwd=repo_path
                )
                branch_name = result.stdout.strip() if result.returncode == 0 else "HEAD"
                original_branch = branch_name
                console.print(f"[dim]CI mode: Working on current branch: {branch_name}[/dim]")
            else:
                # Create the nova-fix branch
                branch_name = git_manager.create_fix_branch()
                console.print(f"[dim]Working on branch: {branch_name}[/dim]")
            
            # Set up signal handler for Ctrl+C
            git_manager.setup_signal_handler()
            
            # Initialize settings and telemetry
            settings = get_settings()
            # Override telemetry setting if --no-telemetry flag is used
            telemetry_enabled = settings.enable_telemetry and not no_telemetry
            telemetry = JSONLLogger(settings, enabled=telemetry_enabled)
            if telemetry_enabled:
                telemetry.start_run(repo_path)
        
            # Initialize agent state
            # Use config default if whole_file not specified on command line
            if whole_file is None:
                whole_file = settings.whole_file_mode
            
            state = AgentState(
                repo_path=repo_path,
                max_iterations=max_iters,
                timeout_seconds=timeout,
                whole_file_mode=whole_file,
            )
            state.start_time = now_utc()  # Track start time for PR generation
            
            # Step 1: Run tests to identify failures (A1 - seed failing tests into planner)
            # Combine test filter with pytest args if provided
            combined_pytest_args = pytest_args or ""
            if test:
                # Add -k filter for the specific test
                test_filter = f"-k '{test}'"
                if combined_pytest_args:
                    combined_pytest_args = f"{test_filter} {combined_pytest_args}"
                else:
                    combined_pytest_args = test_filter
                console.print(f"[dim]Filtering tests: {test}[/dim]")
            
            runner = TestRunner(repo_path, verbose=verbose, pytest_args=combined_pytest_args)
            
            # Time the initial test discovery
            console.print(f"[cyan]🧪 Running initial tests to identify failures...[/cyan]")
            test_discovery_start = time.time()
            
            failing_tests, initial_junit_xml = runner.run_tests()
            
            # Calculate and display test discovery duration
            test_discovery_duration = time.time() - test_discovery_start
            if verbose:
                console.print(f"[dim]✓ Initial test run completed in {test_discovery_duration:.1f}s[/dim]")
            
            # Save initial test report
            if initial_junit_xml:
                telemetry.save_test_report(0, initial_junit_xml, report_type="junit")
            
            # Store failures in agent state
            state.add_failing_tests(failing_tests)
            
            # Log the test discovery event
            telemetry.log_event("test_discovery", {
                "total_failures": state.total_failures,
                "failing_tests": state.failing_tests,
                "initial_report_saved": initial_junit_xml is not None
            })
            
            # Check if there are any failures (AC: if zero failures → exit 0 with message)
            if not failing_tests:
                console.print("[green]✅ No failing tests found! Repository is already green.[/green]")
                state.final_status = "success"
                telemetry.log_event("completion", {"status": "no_failures"})
                telemetry.end_run(success=True)
                success = True
                return
            
            # Display failing tests in a table (duplicate message removed)
            
            table = Table(title="Failing Tests", show_header=True, header_style="bold magenta")
            table.add_column("Test Name", style="cyan", no_wrap=False)
            table.add_column("Location", style="yellow")
            table.add_column("Error", style="red", no_wrap=False)
            
            for test in failing_tests:
                location = f"{test.file}:{test.line}" if test.line > 0 else test.file
                
                # Extract the most relevant error line (same logic as test runner)
                error_lines = test.short_traceback.split('\n')
                error_preview = "Test failed"
                for line in error_lines:
                    if line.strip().startswith("E"):
                        error_preview = line.strip()[2:].strip()  # Remove "E " prefix
                        break
                    elif "AssertionError" in line or "assert" in line:
                        error_preview = line.strip()
                        break
                
                # Truncate if too long for table display
                if len(error_preview) > 80:
                    error_preview = error_preview[:77] + "..."
                
                table.add_row(test.name, location, error_preview)
            
            console.print(table)
            console.print()
            
            # Prepare planner context (AC: planner prompt contains failing tests table)
            planner_context = state.get_planner_context()
            failures_table = runner.format_failures_table(failing_tests)
            
            if verbose:
                console.print("[dim]Planner context prepared with failing tests:[/dim]")
                console.print(failures_table)
                console.print()
            
            # Set branch info in AgentState for reference
            state.branch_name = branch_name
            state.original_commit = git_manager._get_current_head()
            
            # Import our apply patch node
            from nova.nodes.apply_patch import apply_patch
            
            # Initialize the LLM agent (enhanced version with full Planner/Actor/Critic)
            try:
                from nova.agent.llm_agent_enhanced import EnhancedLLMAgent
                llm_agent = EnhancedLLMAgent(repo_path, verbose=verbose)
                
                # Determine which model we're using
                model_name = settings.default_llm_model
                reasoning_effort = settings.reasoning_effort
                
                # Display model and reasoning effort
                if "gpt" in model_name.lower():
                    if "gpt-5" in model_name.lower():
                        console.print(f"[dim]Using OpenAI {model_name} for autonomous test fixing (reasoning effort: {reasoning_effort})[/dim]")
                    else:
                        console.print(f"[dim]Using OpenAI {model_name} for autonomous test fixing[/dim]")
                elif "claude" in model_name.lower():
                    console.print(f"[dim]Using Anthropic {model_name} for autonomous test fixing[/dim]")
                else:
                    console.print(f"[dim]Using {model_name} for autonomous test fixing[/dim]")
                    
            except ImportError as e:
                console.print(f"[yellow]Warning: Could not import enhanced LLM agent: {e}[/yellow]")
                console.print("[yellow]Falling back to basic LLM agent[/yellow]")
                try:
                    from nova.agent.llm_agent import LLMAgent
                    llm_agent = LLMAgent(repo_path)
                except Exception as e2:
                    console.print(f"[yellow]Warning: Could not initialize LLM agent: {e2}[/yellow]")
                    console.print("[yellow]Falling back to mock agent for demo[/yellow]")
                    from nova.agent.mock_llm import MockLLMAgent
                    llm_agent = MockLLMAgent(repo_path)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not initialize enhanced LLM agent: {e}[/yellow]")
                console.print("[yellow]Falling back to mock agent for demo[/yellow]")
                from nova.agent.mock_llm import MockLLMAgent
                llm_agent = MockLLMAgent(repo_path)
            
            # Agent loop: iterate until tests are fixed or limits reached
            console.print("\n[bold]Starting agent loop...[/bold]")
            
            while state.increment_iteration():
                iteration = state.current_iteration
                iteration_start = time.time()  # Track iteration start time
                console.print(f"\n[blue]━━━ Iteration {iteration}/{state.max_iterations} ━━━[/blue]")
                
                # 1. PLANNER: Generate a plan based on failing tests
                console.print(f"[cyan]🧠 Planning fix for {state.total_failures} failing test(s)...[/cyan]")
                
                # Start timing for planner
                planner_start = time.time()
                
                # Log planner start
                telemetry.log_event("planner_start", {
                    "iteration": iteration,
                    "failing_tests": state.total_failures
                })
                
                # Use LLM to create plan (with critic feedback if available)
                critic_feedback = getattr(state, 'critic_feedback', None) if iteration > 1 else None
                plan = llm_agent.create_plan(state.failing_tests, iteration, critic_feedback)
                
                # Store plan in state for reference
                state.plan = plan
                
                # Calculate and display planner duration
                planner_duration = time.time() - planner_start
                if verbose:
                    console.print(f"[dim]✓ Planning completed in {planner_duration:.1f}s[/dim]")
                
                # Display plan summary
                if verbose:
                    console.print("[dim]Plan created:[/dim]")
                    if plan.get("approach"):
                        console.print(f"  Approach: {plan['approach']}")
                    if plan.get("steps"):
                        console.print("  Steps:")
                        for i, step in enumerate(plan['steps'], 1):  # Show all steps
                            console.print(f"    {i}. {step}")
                    elif plan.get("strategy"):
                        console.print(f"  Strategy: {plan['strategy']}")
                    
                    # Show which source files will be modified
                    if plan.get("source_files"):
                        console.print(f"  Target files: {', '.join(plan['source_files'])}")
                    else:
                        console.print("  [yellow]⚠ No source files identified[/yellow]")
                
                # Log planner completion
                telemetry.log_event("planner_complete", {
                    "iteration": iteration,
                    "plan": plan,
                    "failing_tests": state.total_failures
                })
                
                # 2. ACTOR: Generate a patch diff based on the plan
                console.print(f"[cyan]🎭 Generating patch based on plan...[/cyan]")
                
                # Start timing for actor
                actor_start = time.time()
                
                # Log actor start
                telemetry.log_event("actor_start", {"iteration": iteration})
                
                # Generate patch with plan context and critic feedback if available
                patch_diff = llm_agent.generate_patch(state.failing_tests, iteration, plan=state.plan, critic_feedback=critic_feedback, state=state)
                
                # Calculate and display actor duration
                actor_duration = time.time() - actor_start
                if verbose:
                    console.print(f"[dim]✓ Patch generation completed in {actor_duration:.1f}s[/dim]")
                
                if not patch_diff:
                    console.print("[red]❌ Could not generate a patch[/red]")
                    state.final_status = "no_patch"
                    telemetry.log_event("actor_failed", {"iteration": iteration})
                    break
                
                # Display patch info
                patch_lines = patch_diff.split('\n')
                if verbose:
                    console.print(f"[dim]Generated patch: {len(patch_lines)} lines[/dim]")
                    
                    # Show the actual patch content in verbose mode
                    if whole_file:
                        console.print("\n[bold cyan]File replacements:[/bold cyan]")
                        for line in patch_lines[:50]:  # Show first 50 lines
                            if line.startswith('FILE_REPLACE:'):
                                console.print(f"[bold yellow]{line}[/bold yellow]")
                            elif line == 'END_FILE_REPLACE':
                                console.print(f"[bold yellow]{line}[/bold yellow]\n")
                            else:
                                console.print(f"[dim]{line}[/dim]")
                        if len(patch_lines) > 50:
                            console.print(f"[dim]... ({len(patch_lines) - 50} more lines)[/dim]")
                    else:
                        console.print("\n[bold cyan]Patch preview:[/bold cyan]")
                        for line in patch_lines[:30]:  # Show first 30 lines
                            if line.startswith('+++') or line.startswith('---'):
                                console.print(f"[bold]{line}[/bold]")
                            elif line.startswith('+'):
                                console.print(f"[green]{line}[/green]")
                            elif line.startswith('-'):
                                console.print(f"[red]{line}[/red]")
                            else:
                                console.print(f"[dim]{line}[/dim]")
                        if len(patch_lines) > 30:
                            console.print(f"[dim]... ({len(patch_lines) - 30} more lines)[/dim]")
                
                # Log actor completion
                telemetry.log_event("actor_complete", {
                    "iteration": iteration,
                    "patch_size": len(patch_lines)
                })
                # Save patch artifact (before apply, so we have it even if apply fails)
                telemetry.save_patch(iteration, patch_diff)
                
                # 3. CRITIC: Review and approve/reject the patch
                console.print(f"[cyan]🔍 Reviewing patch with critic...[/cyan]")
                
                # Start timing for critic
                critic_start = time.time()
                
                # Log critic start
                telemetry.log_event("critic_start", {"iteration": iteration})
                
                # Use LLM to review patch with actual test results
                patch_approved, review_reason = llm_agent.review_patch(
                    patch_diff, 
                    state.failing_tests,
                    test_runner=runner,
                    repo_path=repo_path
                )
                
                # Calculate and display critic duration
                critic_duration = time.time() - critic_start
                if verbose:
                    console.print(f"[dim]✓ Critic review completed in {critic_duration:.1f}s[/dim]")
                    console.print(f"[dim]Critic review: {review_reason}[/dim]")
                
                if not patch_approved:
                    console.print(f"[error]❌ Patch rejected: {review_reason}[/error]")
                    # Store critic feedback for next iteration
                    state.critic_feedback = review_reason
                    telemetry.log_event("critic_rejected", {
                        "iteration": iteration,
                        "reason": review_reason
                    })
                    
                    # Check if we have more iterations available
                    if iteration < state.max_iterations:
                        console.print(f"[yellow]Will try a different approach in iteration {iteration + 1}...[/yellow]")
                        continue  # Try again with critic feedback
                    else:
                        # Only set final status if we're out of iterations
                        state.final_status = "patch_rejected"
                        break
                
                console.print("[green]✓ Patch approved by critic[/green]")
                
                # Clear critic feedback since patch was approved
                state.critic_feedback = None
                
                # Log critic approval
                telemetry.log_event("critic_approved", {
                    "iteration": iteration,
                    "reason": review_reason
                })
                
                # 4. APPLY PATCH: Apply the approved patch and commit
                console.print(f"[cyan]📝 Applying patch...[/cyan]")
                
                # Start timing for patch application
                patch_start = time.time()
                
                # Use our ApplyPatchNode to apply and commit the patch
                result = apply_patch(state, patch_diff, git_manager, verbose=verbose)
                
                # Calculate and display patch application duration
                patch_duration = time.time() - patch_start
                if verbose:
                    console.print(f"[dim]✓ Patch application completed in {patch_duration:.1f}s[/dim]")
                
                if not result["success"]:
                    console.print(f"[red]❌ Failed to apply patch: {result.get('error', 'unknown error')}[/red]")
                    # Provide feedback for next iteration
                    state.critic_feedback = "Patch failed to apply – likely incorrect context."
                    telemetry.log_event("patch_error", {
                        "iteration": iteration,
                        "step": result.get("step_number", 0),
                        "error": result.get('error', 'unknown')
                    })
                    if iteration < state.max_iterations:
                        console.print(f"[yellow]↻ Retrying with a new patch in iteration {iteration+1}...[/yellow]")
                        continue  # go to next iteration without breaking
                    else:
                        state.final_status = "patch_error"
                        break
                else:
                    # Log successful patch application (only if not already done by fallback)
                    console.print(f"[green]✓ Patch applied and committed (step {result['step_number']})[/green]")
                telemetry.log_event("patch_applied", {
                    "iteration": iteration,
                    "step": result["step_number"],
                    "files_changed": result["changed_files"],
                    "commit": git_manager._get_current_head()
                })
                
                # Save patch artifact for auditing
                # The patch was already saved before apply, no need to save again
                
                # 5. RUN TESTS: Check if the patch fixed the failures
                console.print(f"[cyan]🧪 Running tests after patch...[/cyan]")
                
                # Start timing for test run
                test_start = time.time()
                
                new_failures, junit_xml = runner.run_tests()
                
                # Calculate and display test run duration
                test_duration = time.time() - test_start
                if verbose:
                    console.print(f"[dim]✓ Test run completed in {test_duration:.1f}s[/dim]")
                
                # Save test report artifact
                if junit_xml:
                    telemetry.save_test_report(result['step_number'], junit_xml, report_type="junit")
                
                # Update state with new test results
                previous_failures = state.total_failures
                state.add_failing_tests(new_failures)
                state.test_results.append({
                    "iteration": iteration,
                    "failures_before": previous_failures,
                    "failures_after": state.total_failures
                })
                
                telemetry.log_event("test_results", {
                    "iteration": iteration,
                    "failures_before": previous_failures,
                    "failures_after": state.total_failures,
                    "fixed": previous_failures - state.total_failures
                })
                
                # 6. REFLECT: Check if we should continue or stop
                telemetry.log_event("reflect_start", {
                    "iteration": iteration,
                    "failures_before": previous_failures,
                    "failures_after": state.total_failures
                })
                
                if state.total_failures == 0:
                    # All tests passed - success!
                    console.print(f"\n[bold green]✅ All tests passing! Fixed in {iteration} iteration(s).[/bold green]")
                    state.final_status = "success"
                    success = True
                    telemetry.log_event("reflect_complete", {
                        "iteration": iteration,
                        "decision": "success",
                        "reason": "all_tests_passing"
                    })
                    break
                
                # Check if we made progress
                if state.total_failures < previous_failures:
                    fixed_count = previous_failures - state.total_failures
                    console.print(f"[green]✓ Progress: Fixed {fixed_count} test(s), {state.total_failures} remaining[/green]")
                else:
                    console.print(f"[yellow]⚠ No progress: {state.total_failures} test(s) still failing[/yellow]")
                    # Let the planner/critic know that the last patch had no effect
                    state.critic_feedback = "No progress in reducing failures – try a different approach."
                
                # Check timeout
                if state.check_timeout():
                    console.print(f"[red]⏰ Timeout reached ({state.timeout_seconds}s)[/red]")
                    state.final_status = "timeout"
                    telemetry.log_event("reflect_complete", {
                        "iteration": iteration,
                        "decision": "stop",
                        "reason": "timeout"
                    })
                    break
                
                # Check if we're at max iterations
                if iteration >= state.max_iterations:
                    console.print(f"[red]🔄 Maximum iterations reached ({state.max_iterations})[/red]")
                    state.final_status = "max_iters"
                    telemetry.log_event("reflect_complete", {
                        "iteration": iteration,
                        "decision": "stop",
                        "reason": "max_iterations"
                    })
                    break
                
                # Continue to next iteration
                console.print(f"[dim]Continuing to iteration {iteration + 1}...[/dim]")
                telemetry.log_event("reflect_complete", {
                    "iteration": iteration,
                    "decision": "continue",
                    "reason": "more_failures_to_fix"
                })
                
                # Display iteration summary with timing in verbose mode
                if verbose:
                    iteration_duration = time.time() - iteration_start
                    console.print(f"\n[dim]━━━ Iteration {iteration} Summary ━━━[/dim]")
                    console.print(f"[dim]  • Total iteration time: {iteration_duration:.1f}s[/dim]")
                    console.print(f"[dim]  • Planner: {planner_duration:.1f}s[/dim]")
                    console.print(f"[dim]  • Actor: {actor_duration:.1f}s[/dim]")
                    console.print(f"[dim]  • Critic: {critic_duration:.1f}s[/dim]")
                    console.print(f"[dim]  • Apply patch: {patch_duration:.1f}s[/dim]")
                    console.print(f"[dim]  • Run tests: {test_duration:.1f}s[/dim]")
                    console.print(f"[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]")
            
            # Print exit summary
            if state and state.final_status:
                print_exit_summary(state, state.final_status, llm_agent=llm_agent)
            
            # Log final completion status
            telemetry.log_event("completion", {
                "status": state.final_status,
                "iterations": state.current_iteration,
                "total_patches": len(state.patches_applied),
                "final_failures": state.total_failures
            })
            telemetry.end_run(success=success)
        
    except KeyboardInterrupt:
        if state:
            state.final_status = "interrupted"
            print_exit_summary(state, "interrupted", llm_agent=llm_agent)
        else:
            console.print("\n[yellow]Interrupted by user[/yellow]")
        if telemetry:
            telemetry.log_event("interrupted", {"reason": "keyboard_interrupt"})
        success = False
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        if state:
            state.final_status = "error"
            print_exit_summary(state, "error", llm_agent=llm_agent)
        if telemetry:
            telemetry.log_event("error", {"error": str(e)})
        success = False
    finally:
        # If successful, offer to create a PR (skip in CI mode)
        pr_created = False
        if success and state and branch_name and git_manager and getattr(state, "initial_failures", 0) > 0 and not ci_mode:
            try:
                console.print("\n[bold green]✅ Success! Changes saved to branch:[/bold green] " + branch_name)
                
                # Ask if user wants to create a PR
                from nova.tools.pr_generator import PRGenerator
                pr_gen = PRGenerator(repo_path)
                
                # Check if PR already exists
                if pr_gen.check_pr_exists(branch_name):
                    console.print("[yellow]A PR already exists for this branch[/yellow]")
                else:
                    # Skip PR creation when there were no failing tests fixed or no patches applied
                    if not state.initial_failing_tests or len(state.patches_applied) == 0:
                        console.print("[dim]Skipping PR creation: no failing tests fixed or no changes applied.[/dim]")
                        pr_created = False
                        raise typer.Exit(0)
                    logger = get_logger()
                    with logger.section("Pull Request Generation", "🤖", show_in_normal=True):
                        logger.info("Using GPT-5 to generate pull request...")
                        
                    # Calculate execution time
                    if hasattr(state, 'start_time'):
                        if isinstance(state.start_time, float):
                            elapsed_time = time.time() - state.start_time
                        else:
                            elapsed_time = seconds_between(now_utc(), state.start_time)
                    else:
                        elapsed_time = 0
                    minutes, seconds = divmod(int(elapsed_time), 60)
                    execution_time = f"{minutes}m {seconds}s"
                    
                    # Get fixed tests and changed files
                    # Use initial_failing_tests for PR generation (what we originally fixed)
                    fixed_tests = state.initial_failing_tests if state.initial_failing_tests else []
                    changed_files = []
                    
                    # Get list of changed files from git
                    num_patches = len(state.patches_applied)
                    if num_patches > 0:
                        try:
                            base_ref = f"HEAD~{num_patches}"
                            result = subprocess.run(
                                ["git", "diff", "--name-only", base_ref],
                                capture_output=True,
                                text=True,
                                cwd=repo_path
                            )
                            if result.returncode == 0:
                                changed_files = [f for f in result.stdout.strip().split('\n') if f]
                        except Exception as e:
                            logger.warning(f"Could not list changed files: {e}")
                    
                    # Gather reasoning logs from telemetry
                    reasoning_logs = []
                    if telemetry and hasattr(telemetry, 'events'):
                        reasoning_logs = telemetry.events
                    elif telemetry:
                        # Try to read from telemetry files
                        try:
                            telemetry_dir = Path(repo_path) / ".nova"
                            if telemetry_dir.exists():
                                # Get the most recent run directory
                                run_dirs = sorted([d for d in telemetry_dir.iterdir() if d.is_dir()], 
                                                key=lambda x: x.stat().st_mtime, reverse=True)
                                if run_dirs:
                                    trace_file = run_dirs[0] / "trace.jsonl"
                                    if trace_file.exists():
                                        import json
                                        with open(trace_file) as f:
                                            for line in f:
                                                try:
                                                    reasoning_logs.append(json.loads(line))
                                                except json.JSONDecodeError as e:
                                                    # Skip malformed JSON lines
                                                    pass
                        except Exception as e:
                            logger.warning(f"Could not read reasoning logs: {e}")
                    
                    # Generate PR content using GPT-5
                    with logger.subsection("Generating PR content"):
                        logger.verbose("Calling GPT-5 to generate title and description...", component="PR")
                    title, description = pr_gen.generate_pr_content(
                        fixed_tests=fixed_tests,
                        patches_applied=state.patches_applied,
                        changed_files=changed_files,
                        execution_time=execution_time,
                        reasoning_logs=reasoning_logs
                    )
                    
                    logger.info(f"\nPR Title: {title}")
                    logger.info("\nPR Description:")
                    # Show full description in verbose mode, truncated in normal
                    if logger.level.value >= 1:  # verbose or higher
                        logger.info(description)
                    else:
                        logger.info(description[:500] + "..." if len(description) > 500 else description)
                    
                    # Push the branch first
                    with logger.subsection("Pushing to remote"):
                        logger.info("Pushing branch to remote...")
                    push_result = subprocess.run(
                        ["git", "push", "origin", branch_name],
                        capture_output=True,
                        text=True,
                        cwd=repo_path
                    )
                    
                    if push_result.returncode != 0:
                        logger.warning(f"Failed to push branch: {push_result.stderr}")
                        logger.verbose("Attempting to create PR anyway...", component="Git")
                    
                    # Create the PR
                    with logger.subsection("Creating pull request"):
                        logger.info("Submitting PR to GitHub...")
                    # Detect the default branch
                    base_branch = git_manager.get_default_branch()
                    success_pr, pr_url_or_error = pr_gen.create_pr(
                        branch_name=branch_name,
                        title=title,
                        description=description,
                        base_branch=base_branch,
                        draft=False
                    )
                    
                    if success_pr:
                        console.print(f"\n[bold green]🎉 Pull Request created successfully![/bold green]")
                        console.print(f"[link={pr_url_or_error}]{pr_url_or_error}[/link]")
                        pr_created = True
                    else:
                        console.print(f"\n[yellow]Could not create PR: {pr_url_or_error}[/yellow]")
                        console.print(f"[dim]You can manually create a PR from branch: {branch_name}[/dim]")
                        
            except Exception as e:
                console.print(f"\n[yellow]Error creating PR: {e}[/yellow]")
                console.print(f"[dim]You can manually create a PR from branch: {branch_name}[/dim]")
        elif success and ci_mode and state and getattr(state, "initial_failures", 0) > 0:
            # In CI mode, just show success message
            console.print(f"\n[bold green]✅ Success! Changes applied directly to branch: {branch_name}[/bold green]")
            console.print(f"[dim]Fixed {state.initial_failures} failing test(s)[/dim]")
        
        # Clean up branch and restore original state
        if git_manager and branch_name:
            if ci_mode:
                # In CI mode, don't clean up or switch branches
                console.print(f"\n[dim]CI mode: Changes applied to branch '{branch_name}'[/dim]")
                git_manager.restore_signal_handler()
            elif pr_created:
                # Don't delete the branch if we created a PR
                git_manager.cleanup(success=True)  # Preserve branch if PR was created
                console.print(f"\n[dim]Branch '{branch_name}' preserved for PR[/dim]")
            else:
                git_manager.cleanup(success=success)
                git_manager.restore_signal_handler()
        # Ensure telemetry run is ended if not already done
        if telemetry and not success and (state is None or state.final_status is None):
            telemetry.end_run(success=False)
        # Exit with appropriate code (0 for success, 1 for failure)
        raise SystemExit(0 if success else 1)


@app.command()
def eval(
    repos_file: Path = typer.Argument(
        ...,
        help="YAML file containing repositories to evaluate",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    output_dir: Path = typer.Option(
        Path("./evals/results"),
        "--output",
        "-o",
        help="Directory for evaluation results",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
):
    """
    Evaluate Nova on multiple repositories.
    """
    console.print(f"[green]Nova CI-Rescue Evaluation[/green] 📊")
    console.print(f"Repos file: {repos_file}")
    console.print(f"Output directory: {output_dir}")
    
    # TODO: Implement the actual eval logic
    console.print("[yellow]⚠️  The 'eval' command is not yet implemented.[/yellow]")
    console.print("[dim]This command will evaluate Nova on multiple repositories to measure performance.[/dim]")
    console.print("[dim]For now, please use 'nova fix' on individual repositories.[/dim]")
    raise typer.Exit(0)


@app.command()
def version():
    """
    Show Nova CI-Rescue version.
    """
    from nova import __version__
    console.print(f"[green]Nova CI-Rescue[/green] v{__version__}")


if __name__ == "__main__":
    app()
