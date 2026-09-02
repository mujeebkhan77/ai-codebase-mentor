import json
from typing import Dict, List, Any, Optional, Callable

from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage

from agent.state import InvestigationState
from agent.prompts import SYSTEM_PROMPT
from utils.errors import LLMQuotaExhaustedError, CodebaseMentorError


class AgentController:
    """
    Controller for the AI Codebase Mentor manual agent loop.
    Enforces strict iteration/tool call limits, prevents duplicate tool calls,
    manages evidence context, and handles Gemini API quota/network errors gracefully.
    """

    def __init__(
        self,
        llm: Any = None,
        tools_dict: Optional[Dict[str, Callable]] = None,
        max_iterations: int = 10,
        max_tool_calls: int = 15,
        max_evidence_items: int = 20,
        max_context_size: int = 12000
    ):
        self.llm = llm
        self.tools_dict = tools_dict or {}
        self.max_iterations = max_iterations
        self.max_tool_calls = max_tool_calls
        self.max_evidence_items = max_evidence_items
        self.max_context_size = max_context_size

    def run_investigation(
        self,
        user_question: str,
        repo_path: Optional[str] = None,
        custom_system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute an evidence-based investigation loop for user_question.
        Returns a dictionary containing final answer, evidence, state, and status.
        """
        state = InvestigationState(question=user_question, repo_path=repo_path)
        system_text = custom_system_prompt or SYSTEM_PROMPT

        # Pre-load deterministic evidence from RetrievalEngine to give LLM immediate context on Iteration 1
        if repo_path:
            try:
                from retrieval.engine import RetrievalEngine
                engine = RetrievalEngine(repo_path=repo_path)
                pre_evidence = engine.search(query=user_question, limit=8)
                for ev_item in pre_evidence:
                    state.evidence_manager.add_item(ev_item)

                if len(state.evidence_manager.evidence_items) < 3:
                    more_evidence = engine.search(query="ingestion loader splitting embeddings vectorstore", limit=5)
                    for ev_item in more_evidence:
                        state.evidence_manager.add_item(ev_item)
            except Exception:
                pass

        formatted_initial_ev = state.evidence_manager.format_for_llm(max_items=5)
        prompt_content = user_question
        if repo_path:
            prompt_content = (
                f"Investigating codebase repository at path '{repo_path}'.\n\n"
                f"User Question: {user_question}\n\n"
                f"Initial Retrieved Repository Evidence:\n{formatted_initial_ev}\n\n"
                f"Instruction: Review the retrieved evidence above. If it contains sufficient information to answer the user's question, provide your final grounded answer directly now without calling tools."
            )

        messages = [
            SystemMessage(content=system_text),
            HumanMessage(content=prompt_content)
        ]

        if not self.llm:
            return {
                "status": "error",
                "error": "LLM instance is not configured.",
                "state": state.get_summary(),
                "answer": None,
                "evidence": []
            }

        # Bind tools to LLM if tools exist
        llm_with_tools = self.llm.bind_tools(list(self.tools_dict.values())) if self.tools_dict else self.llm

        # Finalization helper: Synthesize answer from evidence if limit reached or model needs final prompt
        def synthesize_final_answer(reason_status: str, warning_msg: Optional[str] = None) -> Dict[str, Any]:
            prioritized_evidence = state.evidence_manager.get_prioritized_evidence(max_items=self.max_evidence_items)
            if not prioritized_evidence:
                return {
                    "status": reason_status,
                    "warning": warning_msg or "No evidence collected.",
                    "answer": "Investigation completed, but no relevant code evidence could be retrieved from the repository.",
                    "state": state.get_summary(),
                    "evidence": []
                }

            formatted_evidence = state.evidence_manager.format_for_llm(max_items=self.max_evidence_items)
            synthesis_prompt = (
                "Synthesize the following retrieved codebase evidence to answer the user's technical question clearly and accurately.\n\n"
                f"USER QUESTION:\n{user_question}\n\n"
                "COLLECTED CODEBASE EVIDENCE (STRICTLY ISOLATED TO REPOSITORY UNDER INVESTIGATION):\n"
                f"{formatted_evidence}\n\n"
                "ANSWER STRUCTURE:\n"
                "1. **Direct Answer**: Provide a clear, immediate technical answer to the user's question.\n"
                "2. **Execution Flow**: Explain the step-by-step technical execution flow connecting relevant functions, classes, and modules in order.\n"
                "3. **Implementation Details**: Explain key algorithms, parameters, storage mechanisms, and APIs used.\n"
                "4. **Uncertainty & Boundaries**: Explicitly state if any detail requested is not covered by the retrieved code evidence. Do not invent unverified behavior.\n\n"
                "CRITICAL ACCURACY INSTRUCTIONS:\n"
                "- Distinguish strictly between:\n"
                "  1. Module import (top-level code run when module is loaded).\n"
                "  2. Application startup initialization (explicit server/app startup handlers).\n"
                "  3. Runtime function invocation (calls made inside function bodies during user request processing).\n"
                "- DO NOT claim a function or object (such as get_embeddings) is initialized at application startup unless retrieved code explicitly proves top-level/startup execution.\n"
            )
            try:
                final_msg = self.llm.invoke([
                    SystemMessage(content=system_text),
                    HumanMessage(content=synthesis_prompt)
                ])
                final_text = getattr(final_msg, "content", str(final_msg))
            except Exception as synth_err:
                err_text = str(synth_err)
                if "429" in err_text or "quota" in err_text.lower():
                    return {
                        "status": "quota_exhausted",
                        "error": "Gemini LLM quota exhausted (429).",
                        "state": state.get_summary(),
                        "answer": "LLM Quota exhausted during final synthesis. Collected evidence is preserved.",
                        "evidence": prioritized_evidence
                    }
                final_text = f"Collected evidence from repository:\n\n{formatted_evidence}"

            return {
                "status": reason_status,
                "warning": warning_msg,
                "answer": final_text,
                "state": state.get_summary(),
                "evidence": prioritized_evidence
            }

        while state.iteration_count < self.max_iterations and state.tool_call_count < self.max_tool_calls:
            state.increment_iteration()

            try:
                # Invoke LLM
                response = llm_with_tools.invoke(messages)

            except Exception as e:
                err_msg = str(e)
                # Check for 429 RESOURCE_EXHAUSTED or Quota error
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "quota" in err_msg.lower():
                    return {
                        "status": "quota_exhausted",
                        "error": "Gemini LLM quota exhausted (429). Unable to proceed with further LLM calls.",
                        "state": state.get_summary(),
                        "answer": "LLM Quota exhausted. Collected evidence is preserved.",
                        "evidence": state.evidence_manager.get_prioritized_evidence(max_items=self.max_evidence_items)
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"LLM error: {err_msg}",
                        "state": state.get_summary(),
                        "answer": None,
                        "evidence": state.evidence_manager.get_prioritized_evidence(max_items=self.max_evidence_items)
                    }

            # Check if LLM requested tool calls
            if getattr(response, "tool_calls", None):
                messages.append(response)

                for tool_call in response.tool_calls:
                    if state.tool_call_count >= self.max_tool_calls:
                        tool_content = json.dumps({
                            "warning": f"MAX_TOOL_CALLS limit ({self.max_tool_calls}) reached. Please summarize your final answer now."
                        })
                        messages.append(ToolMessage(content=tool_content, tool_call_id=tool_call["id"]))
                        continue

                    tool_name = tool_call.get("name")
                    tool_args = tool_call.get("args", {})

                    # Inject active repo_path if missing
                    if repo_path and "repo_path" not in tool_args and tool_name in {"semantic_code_search", "find_symbol", "find_relationships", "search_code"}:
                        tool_args["repo_path"] = repo_path

                    # Check for unknown tool
                    if tool_name not in self.tools_dict:
                        tool_content = json.dumps({
                            "error": f"Tool '{tool_name}' is not recognized.",
                            "available_tools": list(self.tools_dict.keys())
                        })
                        messages.append(ToolMessage(content=tool_content, tool_call_id=tool_call["id"]))
                        state.record_tool_call(tool_name, tool_args, tool_content, status="unknown_tool")
                        continue

                    # Check for duplicate tool call
                    if state.is_duplicate_tool_call(tool_name, tool_args):
                        tool_content = json.dumps({
                            "notice": f"Tool '{tool_name}' with these exact arguments was already executed. Use the results already obtained or try different parameters."
                        })
                        messages.append(ToolMessage(content=tool_content, tool_call_id=tool_call["id"]))
                        state.record_tool_call(tool_name, tool_args, tool_content, status="skipped_duplicate")
                        continue

                    # Execute tool safely
                    try:
                        tool_func = self.tools_dict[tool_name]
                        tool_result = tool_func(**tool_args)

                        # Format result for model
                        if isinstance(tool_result, (dict, list)):
                            tool_content = json.dumps(tool_result, indent=2, default=str)
                        else:
                            tool_content = str(tool_result)

                        state.record_tool_call(tool_name, tool_args, tool_result, status="success")

                    except Exception as tool_err:
                        tool_content = json.dumps({
                            "error": f"Error executing tool '{tool_name}': {str(tool_err)}"
                        })
                        state.record_tool_call(tool_name, tool_args, tool_content, status="error")

                    # Add stopping notice if sufficient evidence gathered
                    if len(state.evidence_manager.evidence_items) >= 4 or state.tool_call_count >= 2:
                        tool_content += "\n\n[SYSTEM NOTICE: Sufficient repository evidence has been collected in EvidenceManager. Synthesize and provide your final grounded answer now without calling more tools.]"

                    messages.append(ToolMessage(content=tool_content, tool_call_id=tool_call["id"]))

            else:
                # LLM provided a final answer without requesting more tool calls
                final_text = getattr(response, "content", str(response))
                return {
                    "status": "completed",
                    "answer": final_text,
                    "state": state.get_summary(),
                    "evidence": state.evidence_manager.get_prioritized_evidence(max_items=self.max_evidence_items)
                }

        # Loop finished due to MAX_ITERATIONS or MAX_TOOL_CALLS -> Synthesize answer from evidence!
        return synthesize_final_answer(
            reason_status="limit_reached",
            warning_msg=f"Investigation reached safety limit (iterations={state.iteration_count}, tool_calls={state.tool_call_count}). Answer generated from collected evidence."
        )


def run_agent(question: str, repo_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Helper function to run an agent investigation session.
    """
    import os
    from tools import (
        clone_repository,
        get_repository_structure,
        read_file,
        search_code,
        semantic_code_search,
        find_symbol,
        find_relationships,
        get_repository_manifest,
    )

    tools_dict = {
        "clone_repository": clone_repository,
        "get_repository_structure": get_repository_structure,
        "read_file": read_file,
        "search_code": search_code,
        "find_symbol": find_symbol,
        "semantic_code_search": semantic_code_search,
        "find_relationships": find_relationships,
        "get_repository_manifest": get_repository_manifest,
    }

    import os
    import dotenv
    dotenv.load_dotenv()

    llm = None
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        except Exception:
            llm = None

    controller = AgentController(llm=llm, tools_dict=tools_dict)
    return controller.run_investigation(question, repo_path=repo_path)

