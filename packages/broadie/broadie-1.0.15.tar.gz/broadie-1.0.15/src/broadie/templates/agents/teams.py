"""
Template subagent implementation for team management behaviors.
This file provides the Python (technical) template for the 'teams' subagent - extend as needed.
"""

from broadie import SubAgent, tool


@tool(description="List all team names and their leads in the organization")
def list_teams() -> str:
    # Placeholder implementation: Replace with team data lookup
    # In production: load teams from org JSON or db and format into readable string
    return (
        "Teams: Backend Team (lead: john_doe), Frontend Team (lead: emily_davis), ..."
    )


@tool(
    description="Show full details about a specific team, including members, projects, and meeting schedule"
)
def get_team_info(team_name: str) -> str:
    # Placeholder implementation: Replace lookup with org/team data source
    return f"Team '{team_name}':\nLead: ...\nMembers: ...\nProjects: ...\nSchedule: ..."


@tool(
    description="Suggest optimal team composition for a new project, given a list of required skills"
)
def suggest_team_composition(skills: str) -> str:
    # Placeholder logic: parse skills and suggest based on data
    return f"Suggested team(s) for project with skills {skills}: Backend Team, Product Team"


@tool(description="Check team availability for a specific meeting time and date")
def check_team_availability(team_name: str, meeting_time: str) -> str:
    # Placeholder logic; lookup calendars in a real integration
    return f"Team '{team_name}' is available at {meeting_time}: Yes (example)"


# Only export allowed tools for .py API users; in .json configs, tools must exist in the Python registry


class TeamsAgent(SubAgent):
    def build_config(self):
        """
        Provide the configuration for this sub-agent programmatically.
        """
        return {
            "name": "teams_agent",
            "description": "Teams Agent focused on coordination and project management",
            "instruction": (
                "You are the Teams Agent, focused on team coordination, project management, "
                "and cross-functional collaboration."
            ),
            "tools": [
                "list_teams",
                "get_team_info",
                "suggest_team_composition",
                "check_team_availability",
            ],
            "model_settings": {"model": "gemini-2.0-flash", "temperature": 0.3},
        }


# Usage example (for technical users):
if __name__ == "__main__":
    agent = TeamsAgent()
    # Start an interactive session
    agent.run()
