"""
Planner: converts user input into a multi-step plan.
Now recognizes 'delete system' and 'delete system config'.
"""

class Planner:
    def parse(self, user_input: str) -> list[dict]:
        """
        Return a list of action dictionaries.
        Each action contains agent, action, and relevant paths.
        """
        user_input = user_input.lower().strip()
        actions = []

        if "clean and organize workspace" in user_input:
            actions.append({
                "agent": "CleanerAgent",
                "action": "delete",
                "path": "workspace/temp/file.tmp"
            })
            actions.append({
                "agent": "OrganizerAgent",
                "action": "move",
                "source": "workspace/log.txt",
                "dest": "workspace/logs/log.txt"
            })
        elif "clean workspace" in user_input:
            actions.append({
                "agent": "CleanerAgent",
                "action": "delete",
                "path": "workspace/temp"
            })
        elif "organize files" in user_input or "organize workspace" in user_input:
            actions.append({
                "agent": "OrganizerAgent",
                "action": "move",
                "source": "workspace/log.txt",
                "dest": "workspace/logs/log.txt"
            })
        elif "delete system" in user_input or "delete system config" in user_input:
            # Both map to the same high-risk blocked action
            actions.append({
                "agent": "CleanerAgent",
                "action": "delete",
                "path": "system/config"
            })

        return actions
