from typing import Optional, Callable, Any
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

from src.bot.keyboards import (
    get_main_keyboard,
    get_project_keyboard,
    get_auth_keyboard,
    get_settings_keyboard,
    get_back_keyboard,
)
from src.bot.states import (
    MAIN_MENU,
    PROJECT_LIST,
    PROJECT_DETAIL,
    PROJECT_CREATE,
    PROJECT_EDIT,
    AUTH_LOGIN,
    AUTH_REGISTER,
    SETTINGS_MENU,
    END,
)
from src.bot.decorators import (
    require_auth,
    log_handler,
    error_handler,
    rate_limit,
)
from src.services.project_service import ProjectService
from src.services.auth_service import AuthService
from src.core.logger import get_logger

logger = get_logger(__name__)


@log_handler
@error_handler
async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle /start command - show welcome message and main menu."""
    user = update.effective_user
    await update.message.reply_text(
        f"Welcome {user.first_name}! I'm your project management bot.\n"
        "Use the buttons below to navigate.",
        reply_markup=get_main_keyboard(),
    )
    return MAIN_MENU


@log_handler
@error_handler
async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle /help command - show available commands."""
    help_text = (
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/projects - List your projects\n"
        "/create - Create a new project\n"
        "/settings - Bot settings\n"
        "/cancel - Cancel current operation\n"
        "/login - Login to your account\n"
        "/register - Create a new account"
    )
    await update.message.reply_text(help_text)
    return MAIN_MENU


@log_handler
@error_handler
async def cancel_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle /cancel command - cancel current operation."""
    await update.message.reply_text(
        "Operation cancelled. Returning to main menu.",
        reply_markup=get_main_keyboard(),
    )
    return MAIN_MENU


@log_handler
@error_handler
@require_auth
async def projects_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle /projects command - list user projects."""
    user_id = update.effective_user.id
    project_service = ProjectService()

    try:
        projects = await project_service.get_user_projects(user_id)
        if not projects:
            await update.message.reply_text(
                "You have no projects yet. Create one with /create.",
                reply_markup=get_main_keyboard(),
            )
            return MAIN_MENU

        project_list = "\n".join(
            f"• {p['name']} - {p.get('status', 'active')}"
            for p in projects
        )
        await update.message.reply_text(
            f"Your projects:\n\n{project_list}",
            reply_markup=get_project_keyboard(),
        )
        return PROJECT_LIST

    except Exception as e:
        logger.error(f"Failed to fetch projects: {e}")
        await update.message.reply_text(
            "Failed to fetch projects. Please try again.",
            reply_markup=get_main_keyboard(),
        )
        return MAIN_MENU


@log_handler
@error_handler
@require_auth
async def create_project_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle /create command - start project creation."""
    await update.message.reply_text(
        "Send me the project name:",
        reply_markup=get_back_keyboard(),
    )
    return PROJECT_CREATE


@log_handler
@error_handler
async def login_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle /login command - start login process."""
    await update.message.reply_text(
        "Please enter your email:",
        reply_markup=get_back_keyboard(),
    )
    return AUTH_LOGIN


@log_handler
@error_handler
async def register_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle /register command - start registration process."""
    await update.message.reply_text(
        "Please enter your email:",
        reply_markup=get_back_keyboard(),
    )
    return AUTH_REGISTER


@log_handler
@error_handler
@require_auth
async def settings_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle /settings command - show settings menu."""
    await update.message.reply_text(
        "Settings:",
        reply_markup=get_settings_keyboard(),
    )
    return SETTINGS_MENU


@log_handler
@error_handler
async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle text messages based on current state."""
    state = context.user_data.get("state", MAIN_MENU)
    text = update.message.text

    if state == PROJECT_CREATE:
        return await handle_project_creation(update, context, text)
    elif state == PROJECT_EDIT:
        return await handle_project_edit(update, context, text)
    elif state == AUTH_LOGIN:
        return await handle_login_input(update, context, text)
    elif state == AUTH_REGISTER:
        return await handle_register_input(update, context, text)
    else:
        await update.message.reply_text(
            "I didn't understand that. Use the buttons or /help.",
            reply_markup=get_main_keyboard(),
        )
        return MAIN_MENU


@log_handler
@error_handler
async def handle_project_creation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
) -> int:
    """Handle project name input during creation."""
    if not text or len(text.strip()) < 3:
        await update.message.reply_text(
            "Project name must be at least 3 characters. Try again:",
            reply_markup=get_back_keyboard(),
        )
        return PROJECT_CREATE

    user_id = update.effective_user.id
    project_service = ProjectService()

    try:
        project = await project_service.create_project(
            user_id=user_id,
            name=text.strip(),
        )
        await update.message.reply_text(
            f"Project '{project['name']}' created successfully!",
            reply_markup=get_main_keyboard(),
        )
        return MAIN_MENU

    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        await update.message.reply_text(
            "Failed to create project. Please try again.",
            reply_markup=get_main_keyboard(),
        )
        return MAIN_MENU


@log_handler
@error_handler
async def handle_project_edit(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
) -> int:
    """Handle project edit input."""
    project_id = context.user_data.get("edit_project_id")
    if not project_id:
        await update.message.reply_text(
            "No project selected for editing.",
            reply_markup=get_main_keyboard(),
        )
        return MAIN_MENU

    project_service = ProjectService()

    try:
        await project_service.update_project(
            project_id=project_id,
            name=text.strip(),
        )
        await update.message.reply_text(
            "Project updated successfully!",
            reply_markup=get_main_keyboard(),
        )
        return MAIN_MENU

    except Exception as e:
        logger.error(f"Failed to update project: {e}")
        await update.message.reply_text(
            "Failed to update project. Please try again.",
            reply_markup=get_main_keyboard(),
        )
        return MAIN_MENU


@log_handler
@error_handler
async def handle_login_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
) -> int:
    """Handle login email input."""
    if "@" not in text:
        await update.message.reply_text(
            "Invalid email format. Please enter a valid email:",
            reply_markup=get_back_keyboard(),
        )
        return AUTH_LOGIN

    context.user_data["login_email"] = text.strip()
    await update.message.reply_text(
        "Now enter your password:",
        reply_markup=get_back_keyboard(),
    )
    return AUTH_LOGIN + 1


@log_handler
@error_handler
async def handle_register_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
) -> int:
    """Handle registration email input."""
    if "@" not in text:
        await update.message.reply_text(
            "Invalid email format. Please enter a valid email:",
            reply_markup=get_back_keyboard(),
        )
        return AUTH_REGISTER

    context.user_data["register_email"] = text.strip()
    await update.message.reply_text(
        "Now enter your desired password:",
        reply_markup=get_back_keyboard(),
    )
    return AUTH_REGISTER + 1


@log_handler
@error_handler
async def handle_callback_query(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle callback queries from inline keyboards."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "main_menu":
        await query.edit_message_text(
            "Main menu:",
            reply_markup=get_main_keyboard(),
        )
        return MAIN_MENU

    elif data == "projects":
        return await projects_command(update, context)

    elif data == "create_project":
        return await create_project_command(update, context)

    elif data == "settings":
        return await settings_command(update, context)

    elif data == "logout":
        auth_service = AuthService()
        user_id = update.effective_user.id
        await auth_service.logout(user_id)
        await query.edit_message_text(
            "Logged out successfully.",
            reply_markup=get_main_keyboard(),
        )
        return MAIN_MENU

    elif data.startswith("project_"):
        project_id = data.replace("project_", "")
        context.user_data["selected_project"] = project_id
        project_service = ProjectService()

        try:
            project = await project_service.get_project(project_id)
            if project:
                project_info = (
                    f"Project: {project['name']}\n"
                    f"Status: {project.get('status', 'active')}\n"
                    f"Created: {project.get('created_at', 'unknown')}"
                )
                await query.edit_message_text(
                    project_info,
                    reply_markup=get_project_keyboard(project_id),
                )
                return PROJECT_DETAIL
            else:
                await query.edit_message_text(
                    "Project not found.",
                    reply_markup=get_main_keyboard(),
                )
                return MAIN_MENU

        except Exception as e:
            logger.error(f"Failed to fetch project: {e}")
            await query.edit_message_text(
                "Failed to fetch project details.",
                reply_markup=get_main_keyboard(),
            )
            return MAIN_MENU

    elif data == "back":
        await query.edit_message_text(
            "Main menu:",
            reply_markup=get_main_keyboard(),
        )
        return MAIN_MENU

    else:
        await query.edit_message_text(
            "Unknown action.",
            reply_markup=get_main_keyboard(),
        )
        return MAIN_MENU


@log_handler
@error_handler
async def handle_error(
    update: Optional[Update],
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle errors that occur during handler execution."""
    logger.error(f"Update {update} caused error {context.error}")

    if update and update.effective_message:
        await update.effective_message.reply_text(
            "An error occurred. Please try again later.",
            reply_markup=get_main_keyboard(),
        )


@log_handler
@error_handler
async def unknown_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle unknown commands."""
    await update.message.reply_text(
        "Unknown command. Use /help to see available commands.",
        reply_markup=get_main_keyboard(),
    )
    return MAIN_MENU