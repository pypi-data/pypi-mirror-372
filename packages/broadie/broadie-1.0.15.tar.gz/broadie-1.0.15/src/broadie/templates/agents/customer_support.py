"""
Example customer_support.py: starter code for a Customer Support Agent with escalation.
"""

from broadie import Agent, SubAgent, tool


@tool
def lookup_customer(customer_id: str) -> str:
    # Simulate lookup
    return f"Customer {customer_id}: Active, last purchase 3/22/2024"


@tool
def create_ticket(issue: str, priority: str = "medium") -> str:
    return f"Ticket for '{issue}' created with priority {priority}"


@tool
def search_knowledge_base(query: str) -> str:
    return f"KB match for '{query}': Reset password via Settings > Security."


@tool
def escalate_issue(ticket_id: str, reason: str) -> str:
    return f"Ticket {ticket_id} escalated: {reason}"


@tool
def access_technical_docs(topic: str) -> str:
    return f"Technical docs for '{topic}' sent."


@tool
def create_follow_up(customer_id: str, notes: str) -> str:
    return f"Follow-up scheduled for customer {customer_id}."


customer_support = SubAgent(
    name="customer_support_agent",
    instruction="Handles escalated customer support cases. Empathy, escalation, access to advanced tooling.",
    tools=["escalate_issue", "access_technical_docs", "create_follow_up"],
)

support_agent = Agent(
    name="support",
    instruction="You are a helpful customer support agent. Handles ordinary inquiries, creates tickets, looks up customers.",
    tools=["lookup_customer", "create_ticket", "search_knowledge_base"],
    subagents=[customer_support],
)

if __name__ == "__main__":
    print("✅ Customer support system ready!")
    support_agent.run()
