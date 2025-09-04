import os
import logging
import yaml
from typing import Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

USER_STATE: Dict[int, Dict[str, Any]] = {}

class Flow:
    def __init__(self, data: Dict[str, Any]):
        self.start_node: str = data.get("start_node", "welcome")
        self.nodes: Dict[str, Dict[str, Any]] = {n["id"]: n for n in data.get("nodes", [])}

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        return self.nodes.get(node_id)

    def build_keyboard(self, node: Dict[str, Any]) -> InlineKeyboardMarkup:
        buttons = []
        for opt in node.get("options", []):
            label = str(opt.get("label", ""))
            if "url" in opt:
                buttons.append([InlineKeyboardButton(label, url=opt["url"])])
            elif "target" in opt:
                buttons.append([InlineKeyboardButton(label, callback_data=f"go:{opt['target']}")])
        return InlineKeyboardMarkup(buttons) if buttons else InlineKeyboardMarkup([])

def load_flow(path: str = "flow.yaml") -> Flow:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return Flow(data)
    except Exception as e:
        logger.error("cannot load flow.yaml: %s", e)
        raise

FLOW = load_flow(os.getenv("FLOW_PATH", "flow.yaml"))

def set_user_node(user_id: int, node_id: str, push_history: bool = True):
    st = USER_STATE.setdefault(user_id, {"history": []})
    if push_history and st.get("current"):
        st["history"].append(st["current"])
    st["current"] = node_id

def pop_history(user_id: int) -> Optional[str]:
    st = USER_STATE.setdefault(user_id, {"history": []})
    if st["history"]:
        return st["history"].pop()
    return None

async def show_node(update: Update, context: ContextTypes.DEFAULT_TYPE, node_id: str, push_history: bool = True):
    node = FLOW.get_node(node_id)
    if not node:
        await update.effective_chat.send_message("вибач, ця гілка тимчасово недоступна.")
        return
    set_user_node(update.effective_user.id, node_id, push_history=push_history)
    keyboard = FLOW.build_keyboard(node)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=node.get("text", ""),
        reply_markup=keyboard,
        disable_web_page_preview=True
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    USER_STATE[update.effective_user.id] = {"history": []}
    await show_node(update, context, FLOW.start_node, push_history=False)

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data or ""
    if data.startswith("go:"):
        target = data.split(":", 1)[1]
        if target == "__back":
            prev = pop_history(update.effective_user.id)
            if prev:
                node = FLOW.get_node(prev)
                kb = FLOW.build_keyboard(node) if node else None
                await query.edit_message_text(node.get("text", ""), reply_markup=kb, disable_web_page_preview=True)
                set_user_node(update.effective_user.id, prev, push_history=False)
                return
        node = FLOW.get_node(target)
        if node:
            kb = FLOW.build_keyboard(node)
            await query.edit_message_text(node.get("text", ""), reply_markup=kb, disable_web_page_preview=True)
            set_user_node(update.effective_user.id, target)
        else:
            await query.edit_message_text("вибач, ця гілка тимчасово недоступна.")
    else:
        await query.edit_message_text("незнайома дія.")

async def fallback_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    st = USER_STATE.get(update.effective_user.id, {})
    current = st.get("current", FLOW.start_node)
    await show_node(update, context, current, push_history=False)

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("set TELEGRAM_BOT_TOKEN environment variable")

    # створюємо додаток PTB 20.x, сумісний із Python 3.13
    app = ApplicationBuilder().token(token).build()

    # додаємо хендлери
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_text))

    logger.info("бот запущено...")
    app.run_polling()

if __name__ == "__main__":
    main()