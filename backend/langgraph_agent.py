# backend/langgraph_agent.py

import os
import operator
from datetime import datetime, timezone
from typing import TypedDict, Annotated, List, Dict, Any

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain.tools import tool
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


# -------------------------------------------------------------------
# LangGraph state
# -------------------------------------------------------------------

class AgentState(TypedDict):
    """State passed between LangGraph nodes."""
    messages: Annotated[List[BaseMessage], operator.add]


# -------------------------------------------------------------------
# MCP Calendar proxy tool
# -------------------------------------------------------------------

@tool
def mcp_calendar_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    """
    Proxy tool that forwards calendar operations to the MCP Calendar Server.

    Parameters
    ----------
    tool_name:
        Logical tool name chosen by the LLM, for example:
        - "create_calendar_event_tool"
        - "send_calendar_reminder_tool"
        - "sync_google_calendar_tool"
        - "import_google_calendar_tool"

    **kwargs:
        Arguments for the underlying MCP tool. LangChain / LangGraph will often
        wrap these under an inner "kwargs" key, so this function normalizes
        both of the following shapes:

        {"tool_name": "create_calendar_event_tool", "kwargs": {...}}
        {"tool_name": "create_calendar_event_tool", "start_time": "...", ...}
    """

    # 1) Normalize arguments coming from the model / LangGraph
    if "kwargs" in kwargs and isinstance(kwargs["kwargs"], dict):
        params: Dict[str, Any] = kwargs["kwargs"]
    else:
        params = dict(kwargs)

    # 2) Map LLM-facing names to MCP server tool IDs
    TOOL_NAME_MAP = {
        "create_calendar_event_tool": "calendar_create_event",
        "send_calendar_reminder_tool": "calendar_send_reminder",
        "sync_google_calendar_tool": "calendar_sync_google",
        "import_google_calendar_tool": "calendar_import_google",
        # Allow direct use of MCP IDs as well:
        "calendar_create_event": "calendar_create_event",
        "calendar_send_reminder": "calendar_send_reminder",
        "calendar_sync_google": "calendar_sync_google",
        "calendar_import_google": "calendar_import_google",
    }

    mcp_tool_id = TOOL_NAME_MAP.get(tool_name, tool_name)

    print(f"⚙️ Calling MCP Tool: {mcp_tool_id} (from tool_name='{tool_name}')")
    print(f"   Parameters: {params}")

    # 3) Call MCP server
    try:
        resp = requests.post(
            f"{MCP_SERVER_URL}/mcp/call",
            json={"tool": mcp_tool_id, "parameters": params},
            timeout=15,
        )
    except requests.RequestException as e:
        print(f"❌ Error communicating with MCP Server: {e}")
        return {
            "success": False,
            "error": f"Error communicating with MCP Server: {e}",
        }

    if not resp.ok:
        print(f"❌ MCP server HTTP {resp.status_code}: {resp.text}")
        return {
            "success": False,
            "error": f"MCP server returned {resp.status_code}: {resp.text}",
        }

    try:
        data = resp.json()
    except ValueError:
        text = resp.text
        print(f"⚠️ MCP server returned non-JSON: {text}")
        return {
            "success": False,
            "error": f"MCP server returned non-JSON response: {text[:200]}",
        }

    print(f"   ✅ MCP response: {data}")
    return data


# -------------------------------------------------------------------
# LLM + Prompt setup
# -------------------------------------------------------------------

try:
    llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
    llm_with_tools = llm.bind_tools([mcp_calendar_tool])
except Exception as e:  # dev-time logging
    print(f"❌ Failed to initialize Ollama: {e}. Is 'ollama serve' running and is '{OLLAMA_MODEL}' pulled?")
    print("   Falling back to a disabled LLM (only health check will work).")
    llm = None
    llm_with_tools = None

system_prompt = f"""
You are an expert AI Calendar Assistant.

Your job is to help the user manage their schedule using the `mcp_calendar_tool`.
You can create events, send reminders, sync with Google Calendar, and import events.

- Always convert natural language dates/times to **ISO 8601 UTC** timestamps.
- When the user does not specify duration, default to a 1-hour meeting.
- When in doubt about timezone, assume the user is in America/Chicago and
  convert that local time to UTC for the tool parameters.
- After calling a tool, summarize what happened in clear, friendly language.

Current UTC time: {datetime.now(timezone.utc).isoformat()}
""".strip()

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ]
)


# -------------------------------------------------------------------
# LangGraph nodes
# -------------------------------------------------------------------

def run_llm(state: AgentState) -> AgentState:
    """Main LLM node. Decides whether to answer directly or call tools."""
    if not llm_with_tools:
        # Fallback when the LLM backend is unavailable
        return {
            "messages": [
                AIMessage(
                    content="The AI agent backend is currently unavailable. Please check the Ollama server."
                )
            ]
        }

    messages = state["messages"]
    chain = prompt | llm_with_tools
    result = chain.invoke({"messages": messages})
    return {"messages": [result]}


def execute_tools(state: AgentState) -> AgentState:
    """Execute any tool calls requested by the last AI message."""
    messages = state["messages"]
    last_message = messages[-1]

    tool_calls_raw = getattr(last_message, "tool_calls", None)
    tool_messages: List[ToolMessage] = []

    if not tool_calls_raw:
        # No tools requested; just return the existing messages
        return {"messages": messages}

    # Tool calls can be a list or a dict (id -> ToolCall); normalize to a list
    if isinstance(tool_calls_raw, dict):
        iterable = list(tool_calls_raw.values())
    else:
        iterable = list(tool_calls_raw)

    print(f"🔨 Executing {len(iterable)} tool call(s)")

    for raw_call in iterable:
        # Normalize a ToolCall object or dict into a common shape
        if isinstance(raw_call, dict):
            name = raw_call.get("name")
            args = raw_call.get("args", {}) or {}
            tool_call_id = raw_call.get("id")
        else:
            # LangChain ToolCall object
            name = getattr(raw_call, "name", None)
            args = getattr(raw_call, "args", {}) or {}
            tool_call_id = getattr(raw_call, "id", None)

        print(f"   Tool: {name}")
        print(f"   Args: {args}")

        if name == mcp_calendar_tool.name:
            try:
                # Pass the model-produced args directly into the LangChain tool
                output = mcp_calendar_tool.invoke(args)
            except Exception as e:
                print(f"❌ Error executing mcp_calendar_tool: {e}")
                output = {
                    "success": False,
                    "error": f"Error executing mcp_calendar_tool: {e}",
                }
        else:
            output = {
                "success": False,
                "error": f"Unknown tool '{name}' requested.",
            }

        tool_messages.append(
            ToolMessage(content=output, tool_call_id=tool_call_id)
        )

    # Append tool messages to the running conversation
    return {"messages": messages + tool_messages}


def should_continue(state: AgentState) -> str:
    """Decide whether to continue to tools or end the graph."""
    messages = state["messages"]
    last_message = messages[-1]

    tool_calls = getattr(last_message, "tool_calls", None)
    if tool_calls:
        print("➡️  Continuing to tools")
        return "continue_to_tools"

    print("➡️  Ending conversation")
    return "end_graph"


# -------------------------------------------------------------------
# Build and compile LangGraph workflow
# -------------------------------------------------------------------

workflow = StateGraph(AgentState)
workflow.add_node("agent", run_llm)
workflow.add_node("action", execute_tools)

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue_to_tools": "action",
        "end_graph": END,
    },
)

workflow.add_edge("action", "agent")

graph = workflow.compile()


# -------------------------------------------------------------------
# FastAPI app
# -------------------------------------------------------------------

app = FastAPI(title="LangGraph Calendar Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    status = "ok" if llm_with_tools else "error"
    return {"status": status, "model": OLLAMA_MODEL}


@app.post("/chat")
async def chat_with_agent(request: ChatRequest):
    """
    Single-turn chat endpoint.

    The frontend sends a single message string; the agent decides what to do.
    """
    if not llm_with_tools:
        raise HTTPException(
            status_code=503,
            detail="LLM backend is unavailable. Please ensure Ollama is running.",
        )

    try:
        print(f"\n💬 User: {request.message}")

        initial_messages: List[BaseMessage] = [HumanMessage(content=request.message)]

        final_state = graph.invoke({"messages": initial_messages})
        messages = final_state["messages"]
        final_message = messages[-1]

        if isinstance(final_message, AIMessage):
            response_text = final_message.content
        else:
            response_text = str(final_message)

        return {"response": response_text}

    except Exception as e:
        print(f"❌ LangGraph execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI Agent Error: {e}")


# -------------------------------------------------------------------
# Main runner
# -------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
