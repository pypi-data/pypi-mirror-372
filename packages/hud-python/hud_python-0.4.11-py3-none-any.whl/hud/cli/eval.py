"""HUD evaluation command for running tasks and datasets."""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import typer

import hud
from hud.utils.design import HUDDesign

if TYPE_CHECKING:
    from datasets import Dataset
    from hud.agents import ClaudeAgent, OperatorAgent
    from hud.agents.misc.response_agent import ResponseAgent

logger = logging.getLogger(__name__)
design = HUDDesign()


def build_agent(
    agent_type: Literal["claude", "openai"],
    *,
    model: str | None = None,
    allowed_tools: list[str] | None = None,
) -> Any:
    """Create and return the requested agent type."""
    
    # Import agents lazily to avoid dependency issues
    try:
        from hud.agents.misc.response_agent import ResponseAgent
    except ImportError as e:
        design.error(
            "Agent dependencies are not installed. "
            "Please install with: pip install 'hud-python[agent]'"
        )
        raise typer.Exit(1) from e
    
    if agent_type == "openai":
        try:
            from hud.agents import OperatorAgent
        except ImportError as e:
            design.error(
                "OpenAI agent dependencies are not installed. "
                "Please install with: pip install 'hud-python[agent]'"
            )
            raise typer.Exit(1) from e
            
        allowed_tools = allowed_tools or ["openai_computer"]
        
        return OperatorAgent(
            allowed_tools=allowed_tools,
            response_agent=ResponseAgent(),
        )
    
    # Fallback Claude agent (Anthropic)
    try:
        from hud.agents import ClaudeAgent
    except ImportError as e:
        design.error(
            "Claude agent dependencies are not installed. "
            "Please install with: pip install 'hud-python[agent]'"
        )
        raise typer.Exit(1) from e
        
    model = model or "claude-sonnet-4-20250514"
    allowed_tools = allowed_tools or ["anthropic_computer"]
    
    return ClaudeAgent(
        model=model,
        allowed_tools=allowed_tools,
        response_agent=ResponseAgent(),
    )


async def run_single_task(
    source: str,
    *,
    agent_type: Literal["claude", "openai"] = "claude",
    model: str | None = None,
    allowed_tools: list[str] | None = None,
    max_steps: int = 10,
) -> None:
    """Load one task and execute it."""
    
    design.info("📊 Loading dataset…")
    
    # Import Task lazily
    try:
        from hud.datasets import Task
    except ImportError as e:
        design.error(
            "Dataset dependencies are not installed. "
            "Please install with: pip install 'hud-python[agent]'"
        )
        raise typer.Exit(1) from e
    
    # Check if it's a single task JSON file
    path = Path(source)
    if path.exists() and path.suffix == ".json":
        with open(path, "r") as f:
            task_data = json.load(f)
        task = Task(**task_data)
    else:
        # Load from HuggingFace dataset
        try:
            from datasets import load_dataset
        except ImportError as e:
            design.error(
                "Datasets library is not installed. "
                "Please install with: pip install 'hud-python[agent]'"
            )
            raise typer.Exit(1) from e
            
        dataset = load_dataset(source, split="train")
        
        # Get first task from dataset
        sample_task = dataset[0]  # type: ignore[index]
        task = Task(**sample_task)  # type: ignore[arg-type]
    
    task_prompt = task.prompt[:50] + "..." if len(task.prompt) > 50 else task.prompt
    
    with hud.trace(name=task_prompt):
        agent = build_agent(
            agent_type,
            model=model,
            allowed_tools=allowed_tools,
        )
        design.info(task.prompt)
        result = await agent.run(task, max_steps=max_steps)
        design.success(f"Reward: {result.reward}")


async def run_full_dataset(
    source: str,
    *,
    agent_type: Literal["claude", "openai"] = "claude",
    model: str | None = None,
    allowed_tools: list[str] | None = None,
    max_concurrent: int = 30,
    max_steps: int = 50,
) -> list[Any]:
    """Run evaluation across the entire dataset using hud.datasets.run_dataset."""
    
    # Import run_dataset lazily
    try:
        from hud.datasets import run_dataset
    except ImportError as e:
        design.error(
            "Dataset dependencies are not installed. "
            "Please install with: pip install 'hud-python[agent]'"
        )
        raise typer.Exit(1) from e
    
    # Build agent class + config for run_dataset
    if agent_type == "openai":
        try:
            from hud.agents import OperatorAgent
            agent_class = OperatorAgent
        except ImportError as e:
            design.error(
                "OpenAI agent dependencies are not installed. "
                "Please install with: pip install 'hud-python[agent]'"
            )
            raise typer.Exit(1) from e
            
        agent_config: dict[str, Any] = {
            "allowed_tools": allowed_tools or ["openai_computer"],
        }
    else:
        try:
            from hud.agents import ClaudeAgent
            agent_class = ClaudeAgent
        except ImportError as e:
            design.error(
                "Claude agent dependencies are not installed. "
                "Please install with: pip install 'hud-python[agent]'"
            )
            raise typer.Exit(1) from e
            
        agent_config = {
            "model": model or "claude-sonnet-4-20250514",
            "allowed_tools": allowed_tools or ["anthropic_computer"],
        }
    
    design.info("🚀 Running evaluation…")
    return await run_dataset(
        name=f"Evaluation {source.split('/')[-1]}",
        dataset=source,
        agent_class=agent_class,
        agent_config=agent_config,
        max_concurrent=max_concurrent,
        metadata={"dataset": source},
        max_steps=max_steps,
        auto_respond=True,
    )


def eval_command(
    source: str = typer.Argument(
        ...,
        help="HuggingFace dataset identifier (e.g. 'hud-evals/SheetBench-50') or task JSON file",
    ),
    full: bool = typer.Option(
        False,
        "--full",
        help="Run the entire dataset (omit for single-task debug mode)",
    ),
    agent: Literal["claude", "openai"] = typer.Option(
        "claude",
        "--agent",
        help="Agent backend to use",
    ),
    model: str | None = typer.Option(
        None,
        "--model",
        help="Model name for the chosen agent",
    ),
    allowed_tools: str | None = typer.Option(
        None,
        "--allowed-tools",
        help="Comma-separated list of allowed tools",
    ),
    max_concurrent: int = typer.Option(
        50,
        "--max-concurrent",
        help="Concurrency level for full-dataset mode",
    ),
    max_steps: int = typer.Option(
        None,
        "--max-steps",
        help="Maximum steps per task (default: 10 for single, 50 for full)",
    ),
) -> None:
    """🚀 Run evaluation on datasets or individual tasks with agents.
    
    Examples:
        # Evaluate a single task from SheetBench
        hud eval hud-evals/SheetBench-50
        
        # Evaluate the FULL SheetBench dataset with Claude
        hud eval hud-evals/SheetBench-50 --full --agent claude
        
        # Run a single task from a JSON file
        hud eval task.json
        
        # Run with OpenAI Operator agent
        hud eval hud-evals/OSWorld-Gold-Beta --agent openai
    """
    from hud.settings import settings
    import os
    
    # Check for required API keys
    if agent == "claude":
        if not settings.anthropic_api_key or not os.environ.get("ANTHROPIC_API_KEY"):
            design.error("ANTHROPIC_API_KEY is required for Claude agent")
            design.info("Set it in your environment or .env file: ANTHROPIC_API_KEY=your-key-here")
            raise typer.Exit(1)
    elif agent == "openai":
        if not settings.openai_api_key or not os.environ.get("OPENAI_API_KEY"):
            design.error("OPENAI_API_KEY is required for OpenAI agent")
            design.info("Set it in your environment or .env file: OPENAI_API_KEY=your-key-here")
            raise typer.Exit(1)
    
    # Check for HUD_API_KEY if using HUD services
    if not settings.api_key or not os.environ.get("HUD_API_KEY"):
        design.warning("HUD_API_KEY not set. Some features may be limited.")
        design.info("Get your API key at: https://app.hud.so")
    
    # Parse allowed tools
    allowed_tools_list = (
        [t.strip() for t in allowed_tools.split(",") if t.strip()]
        if allowed_tools
        else None
    )
    
    # Set default max_steps if not provided
    if max_steps is None:
        max_steps = 50 if full else 10
    
    # Run evaluation
    if full:
        asyncio.run(run_full_dataset(
            source,
            agent_type=agent,
            model=model,
            allowed_tools=allowed_tools_list,
            max_concurrent=max_concurrent,
            max_steps=max_steps,
        ))
    else:
        asyncio.run(run_single_task(
            source,
            agent_type=agent,
            model=model,
            allowed_tools=allowed_tools_list,
            max_steps=max_steps,
        ))