from __future__ import annotations
import asyncio
import json

from ai_infra.llm.agents.custom.planner.states import PlannerState
from ai_infra.llm.agents.custom.planner.utils import (
    _gather_msgs,
    _render_presentation_md,
    _call_planner,
    _summarize_tool,
)


async def analyze(state: PlannerState) -> PlannerState:
    """Build a token-lean summary: one line per tool with name | desc | req= | opt=."""
    lines: list[str] = [_summarize_tool(t) for t in state.get("tools", [])]
    state["tool_summary"] = "\n".join(lines)
    return state


async def draft_plan(state: PlannerState) -> PlannerState:
    """Ask the LLM to produce a concise tool-using plan and open questions."""
    base_sys = (
        "ROLE=Planner\n"
        "Plan ONLY using the provided tools. Each step must include:\n"
        "- `tool` (string)\n"
        "- `args` (object with exact fields)\n"
        "- `rationale` (brief string)\n"
        "If configuration is needed, add explicit `questions`.\n"
        "Use concise steps."
    )

    user_msg = _gather_msgs(state)
    tools_md = state.get("tool_summary") or ""
    user = (
        f"{user_msg}\n\n"
        f"Available tools:\n{tools_md}\n\n"
    )

    draft = await _call_planner(state, base_sys=base_sys, user=user)

    state["plan"] = [s.model_dump() for s in draft.plan]
    state["questions"] = draft.questions
    return state


async def present_for_hitl(state: PlannerState) -> PlannerState:
    """Render a presentation and either return (API) or prompt for approval (terminal)."""
    mode = state.get("io_mode") or "terminal"

    # Always prepare a presentation block
    presentation_md = _render_presentation_md(state)
    state["presentation_md"] = presentation_md

    if mode == "api":
        # Non-blocking: return summary and mark awaiting input
        state["awaiting_approval"] = True
        state["approved"] = False
        state["aborted"] = False
        state["feedback"] = state.get("feedback", "")
        return state

    # ---- Terminal (interactive) ----
    print("\n" + presentation_md)
    print("\nPlease review the plan. You may:")
    print("- type 'y' to approve,")
    print("- type 'r: <feedback>' to request changes or add configs,")
    print("- type anything else to reject without feedback.")
    ans = (await asyncio.to_thread(input, "\nApprove plan? [y / r:<feedback> / n]: ")).strip()
    ans_l = ans.lower()

    if ans_l == "y":
        state["approved"] = True
        state["feedback"] = ""
        state["aborted"] = False
        state["awaiting_approval"] = False
        return state

    if ans_l.startswith("r:"):
        state["approved"] = False
        state["feedback"] = ans[2:].strip()
        state["aborted"] = False
        state["awaiting_approval"] = False
        return state

    state["approved"] = False
    state["feedback"] = ""
    state["aborted"] = True
    state["awaiting_approval"] = False
    return state


async def replan(state: PlannerState) -> PlannerState:
    """Revise the plan using feedback while keeping format constraints."""
    base_sys = (
        "ROLE=Planner-Revision\n"
        "Revise the plan based on feedback.\n"
        "Each plan step MUST be an object with fields:\n"
        "- `tool` (string)\n"
        "- `args` (object)\n"
        "- `rationale` (string)\n"
        "(`title` is optional.)\n"
        "Use concise steps."
    )

    user_msg = _gather_msgs(state)
    tools_md = state.get("tool_summary") or ""
    feedback = state.get("feedback", "")

    user = (
        f"Original request:\n{user_msg}\n\n"
        f"Available tools:\n{tools_md}\n\n"
        f"Current plan:\n{json.dumps(state.get('plan', []), ensure_ascii=False)}\n\n"
        f"Feedback:\n{feedback}."
    )

    draft = await _call_planner(state, base_sys=base_sys, user=user)

    state["plan"] = [s.model_dump() for s in draft.plan]
    state["questions"] = draft.questions
    return state
