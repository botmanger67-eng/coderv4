from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Optional, Dict, Any


def build_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Build the main menu inline keyboard.

    Returns:
        InlineKeyboardMarkup: Keyboard with main menu options.
    """
    keyboard: List[List[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton("📊 Repositories", callback_data="menu_repos"),
            InlineKeyboardButton("📝 Issues", callback_data="menu_issues"),
        ],
        [
            InlineKeyboardButton("🔍 Search", callback_data="menu_search"),
            InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings"),
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="menu_help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_repository_keyboard(
    repo_names: List[str], page: int = 0, total_pages: int = 1
) -> InlineKeyboardMarkup:
    """
    Build a keyboard for listing repositories with pagination.

    Args:
        repo_names: List of repository names.
        page: Current page number (0-indexed).
        total_pages: Total number of pages.

    Returns:
        InlineKeyboardMarkup: Keyboard with repository buttons and pagination.
    """
    keyboard: List[List[InlineKeyboardButton]] = []

    for name in repo_names:
        keyboard.append(
            [InlineKeyboardButton(name, callback_data=f"repo_{name}")]
        )

    pagination_row: List[InlineKeyboardButton] = []
    if page > 0:
        pagination_row.append(
            InlineKeyboardButton("⬅️ Previous", callback_data=f"repos_page_{page - 1}")
        )
    if page < total_pages - 1:
        pagination_row.append(
            InlineKeyboardButton("Next ➡️", callback_data=f"repos_page_{page + 1}")
        )
    if pagination_row:
        keyboard.append(pagination_row)

    keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")])

    return InlineKeyboardMarkup(keyboard)


def build_issues_keyboard(
    issue_numbers: List[int], repo_name: str, page: int = 0, total_pages: int = 1
) -> InlineKeyboardMarkup:
    """
    Build a keyboard for listing issues with pagination.

    Args:
        issue_numbers: List of issue numbers.
        repo_name: Repository name.
        page: Current page number (0-indexed).
        total_pages: Total number of pages.

    Returns:
        InlineKeyboardMarkup: Keyboard with issue buttons and pagination.
    """
    keyboard: List[List[InlineKeyboardButton]] = []

    for number in issue_numbers:
        keyboard.append(
            [InlineKeyboardButton(f"#{number}", callback_data=f"issue_{repo_name}_{number}")]
        )

    pagination_row: List[InlineKeyboardButton] = []
    if page > 0:
        pagination_row.append(
            InlineKeyboardButton("⬅️ Previous", callback_data=f"issues_page_{repo_name}_{page - 1}")
        )
    if page < total_pages - 1:
        pagination_row.append(
            InlineKeyboardButton("Next ➡️", callback_data=f"issues_page_{repo_name}_{page + 1}")
        )
    if pagination_row:
        keyboard.append(pagination_row)

    keyboard.append([InlineKeyboardButton("🔙 Back to Repos", callback_data="back_to_repos")])

    return InlineKeyboardMarkup(keyboard)


def build_issue_detail_keyboard(
    repo_name: str, issue_number: int
) -> InlineKeyboardMarkup:
    """
    Build a keyboard for issue detail actions.

    Args:
        repo_name: Repository name.
        issue_number: Issue number.

    Returns:
        InlineKeyboardMarkup: Keyboard with issue action buttons.
    """
    keyboard: List[List[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton("💬 Comment", callback_data=f"comment_{repo_name}_{issue_number}"),
            InlineKeyboardButton("🔒 Close", callback_data=f"close_{repo_name}_{issue_number}"),
        ],
        [
            InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh_{repo_name}_{issue_number}"),
            InlineKeyboardButton("🔙 Back to Issues", callback_data=f"back_to_issues_{repo_name}"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_search_keyboard() -> InlineKeyboardMarkup:
    """
    Build a keyboard for search options.

    Returns:
        InlineKeyboardMarkup: Keyboard with search type buttons.
    """
    keyboard: List[List[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton("🔍 Search Repos", callback_data="search_repos"),
            InlineKeyboardButton("🔍 Search Issues", callback_data="search_issues"),
        ],
        [
            InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_settings_keyboard(current_settings: Optional[Dict[str, Any]] = None) -> InlineKeyboardMarkup:
    """
    Build a keyboard for settings options.

    Args:
        current_settings: Optional dictionary of current settings.

    Returns:
        InlineKeyboardMarkup: Keyboard with settings buttons.
    """
    keyboard: List[List[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton("🌐 Language", callback_data="setting_language"),
            InlineKeyboardButton("🔔 Notifications", callback_data="setting_notifications"),
        ],
        [
            InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_help_keyboard() -> InlineKeyboardMarkup:
    """
    Build a keyboard for help options.

    Returns:
        InlineKeyboardMarkup: Keyboard with help buttons.
    """
    keyboard: List[List[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton("📖 Commands", callback_data="help_commands"),
            InlineKeyboardButton("❓ FAQ", callback_data="help_faq"),
        ],
        [
            InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_confirmation_keyboard(
    confirm_callback: str, cancel_callback: str
) -> InlineKeyboardMarkup:
    """
    Build a confirmation keyboard with Yes/No buttons.

    Args:
        confirm_callback: Callback data for confirmation.
        cancel_callback: Callback data for cancellation.

    Returns:
        InlineKeyboardMarkup: Keyboard with confirm and cancel buttons.
    """
    keyboard: List[List[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton("✅ Yes", callback_data=confirm_callback),
            InlineKeyboardButton("❌ No", callback_data=cancel_callback),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def build_back_keyboard(callback_data: str = "back_to_menu") -> InlineKeyboardMarkup:
    """
    Build a simple back button keyboard.

    Args:
        callback_data: Callback data for the back button.

    Returns:
        InlineKeyboardMarkup: Keyboard with a single back button.
    """
    keyboard: List[List[InlineKeyboardButton]] = [
        [InlineKeyboardButton("🔙 Back", callback_data=callback_data)]
    ]
    return InlineKeyboardMarkup(keyboard)