"""Selection service for choosing from lists of items."""

from typing import List, Optional
from ..models import ProjectInfo, EpicInfo, BoardInfo, SprintInfo, IssueInfo
from ..constants import MANUAL_ENTRY_OPTION, CREATE_NEW_OPTION, NONE_OPTION
from .prompts import PromptService


class SelectorService:
    """Service for selecting items from lists."""
    
    def __init__(self, prompt_service: PromptService):
        """Initialize the selector service."""
        self.prompt_service = prompt_service
    
    def select_project(
        self, 
        projects: List[ProjectInfo], 
        latest_project: Optional[str] = None
    ) -> str:
        """Select project from available projects."""
        # Create choices with project key and name
        if projects:
            choices = [f"{p.key} - {p.name}" for p in projects]
        else:
            choices = []
            if latest_project:
                choices.append(latest_project)
        
        # Add manual entry option
        choices.append(MANUAL_ENTRY_OPTION.format(item="project"))
        
        # Find default choice based on latest project
        default_choice = None
        if latest_project:
            for choice in choices:
                if choice.startswith(f"{latest_project} -"):
                    default_choice = choice
                    break
        
        selected = self.prompt_service.get_fuzzy_selection(
            "Select project (type to search):",
            choices=choices,
            default=default_choice,
            instruction="Use arrows to navigate, type to filter"
        )
        
        # Handle manual entry
        if selected == MANUAL_ENTRY_OPTION.format(item="project"):
            return self.prompt_service.get_text_input("Enter project key:")
        
        # Extract project key from selection
        return selected.split(" - ")[0]
    
    def select_epic(
        self, 
        epics: List[EpicInfo], 
        allow_manual: bool = True
    ) -> str:
        """Select epic from available epics."""
        if not epics and not allow_manual:
            raise ValueError("No epics available and manual entry not allowed")
        
        # Sort by epic key (assuming higher numbers are more recent)
        epics_sorted = sorted(
            epics, 
            key=lambda x: int(x.key.split('-')[-1]) if x.key.split('-')[-1].isdigit() else 0, 
            reverse=True
        )
        
        # Create choices
        choices = [epic.display for epic in epics_sorted]
        if allow_manual:
            choices.append(MANUAL_ENTRY_OPTION.format(item="epic"))
        
        if not choices:
            return self.prompt_service.get_text_input("Enter epic key:")
        
        selected = self.prompt_service.get_fuzzy_selection(
            "Select epic (required) - type to search:",
            choices=choices,
            instruction="Use arrows to navigate, type to filter"
        )
        
        # Handle manual entry
        if selected == MANUAL_ENTRY_OPTION.format(item="epic"):
            return self.prompt_service.get_text_input("Enter epic key:")
        
        # Extract epic key from selection
        return selected.split(" - ")[0]
    
    def select_board(
        self, 
        boards: List[BoardInfo], 
        latest_board_id: Optional[int] = None,
        allow_none: bool = True
    ) -> Optional[int]:
        """Select board from available boards."""
        if not boards:
            return None
        
        # Create choices
        choices = [board.display for board in boards]
        if allow_none:
            choices.append(NONE_OPTION.format(description="skip board/sprint selection"))
        
        # Find default choice based on latest board
        default_choice = None
        if latest_board_id:
            for choice in choices:
                if f"(ID: {latest_board_id})" in choice:
                    default_choice = choice
                    break
        
        selected = self.prompt_service.get_fuzzy_selection(
            "Select sprint-enabled board (type to search):",
            choices=choices,
            default=default_choice,
            instruction="Use arrows to navigate, type to filter (Scrum boards only)"
        )
        
        # Handle none selection
        if selected == NONE_OPTION.format(description="skip board/sprint selection"):
            return None
        
        # Find the board ID for the selected board
        for board in boards:
            if board.display == selected:
                return board.id
        
        return None
    
    def select_sprint(
        self, 
        sprints: List[SprintInfo], 
        allow_none: bool = True
    ) -> Optional[int]:
        """Select sprint from available sprints."""
        if not sprints:
            return None
        
        # Create choices
        choices = [sprint.display for sprint in sprints]
        if allow_none:
            choices.append(NONE_OPTION.format(description="no sprint"))
        
        selected = self.prompt_service.get_fuzzy_selection(
            "Select sprint (type to search):",
            choices=choices,
            instruction="Use arrows to navigate, type to filter"
        )
        
        # Handle none selection
        if selected == NONE_OPTION.format(description="no sprint"):
            return None
        
        # Find the sprint ID for the selected sprint
        for sprint in sprints:
            if sprint.display == selected:
                return sprint.id
        
        return None
    
    def select_issue_or_create_new(
        self, 
        issues: List[IssueInfo]
    ) -> Optional[IssueInfo]:
        """Select an issue or choose to create a new one."""
        # Create choices with option to create new issue first
        choices = [CREATE_NEW_OPTION]
        if issues:
            choices.extend([issue.display for issue in issues])
        
        selected = self.prompt_service.get_fuzzy_selection(
            "Select issue for Git checkout:",
            choices=choices,
            instruction="Use arrows to navigate, type to filter"
        )
        
        if selected == CREATE_NEW_OPTION:
            return None  # Signal to create new issue
        
        # Find the selected issue
        for issue in issues:
            if issue.display == selected:
                return issue
        
        return None
