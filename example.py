# Install if needed
# %pip install langgraph langchain

from langgraph.types import interrupt, Command
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Define the state schema
from typing import TypedDict, Literal

class State(TypedDict):
    draft: str
    status: Literal["pending", "approved", "rejected"]


# Step 1: Node to generate a product description
def generate_description(state: State):
    return {
        "draft": "This is a sleek modern chair, made from oak wood.",
        "status": "pending"
    }


# Step 2: Human approval node (pause here!)
def human_approval(state: State):
    decision = interrupt({
        "message": f"Review Draft:\n\n{state['draft']}\n\nApprove? (yes/no)"
    })
    return {"status": decision}


# Step 3: Handle the decision
def finalize(state: State):
    if state["status"] == "approved":
        print("✅ Draft approved! Publishing to store...")
    else:
        print("❌ Draft rejected. Sending back for revision...")
    return state


# --- Build Graph ---
builder = StateGraph(State)
builder.add_node("generator", generate_description)
builder.add_node("human", human_approval)
builder.add_node("finalize", finalize)

builder.set_entry_point("generator")
builder.add_edge("generator", "human")
builder.add_edge("human", "finalize")
builder.add_edge("finalize", END)

# Add memory checkpointer (so thread_id works)
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)


# Thread/session identifier
config = {"configurable": {"thread_id": "demo-1"}}

# First run: will stop at human approval interrupt
step = graph.invoke({}, config=config)

print("Graph paused, waiting for human input...")
print("Interrupt output:", step)


# # Approve case
resume_command = Command(resume="approved")
step = graph.invoke(resume_command, config=config)

# Reject case (try this instead)
resume_command = Command(resume="rejected")
step = graph.invoke(resume_command, config=config)
