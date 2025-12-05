import os
import requests
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENSEA_API_KEY = os.getenv("OPENSEA_API_KEY")

# Import protection and monetization
from railway_protection import add_protection
from monetization import NFTBotMonetization

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize protection and monetization
protection = add_protection()
monetization = NFTBotMonetization()

headers = {
    "Accept": "application/json",
    "X-API-KEY": OPENSEA_API_KEY
}

# Popular collections for quick access
POPULAR_COLLECTIONS = {
    "boredapeyachtclub": "Bored Ape Yacht Club",
    "cryptopunks": "CryptoPunks",
    "azuki": "Azuki",
    "doodles-official": "Doodles",
    "moonbirds": "Moonbirds",
    "clonex": "CloneX",
    "murakami-flowers": "Murakami Flowers",
    "proof-moonbirds": "Proof Moonbirds",
    "wassies": "Wassies",
    "goblintown": "GoblinTown",
    "mutant-ape-yacht-club": "Mutant Ape Yacht Club",
    "otherdeed": "Otherdeed"
}

# -------------------------------
# FETCH FUNCTIONS
# -------------------------------

def fetch_collection_stats(collection: str):
    """Fetch collection statistics from OpenSea API."""
    url = f"https://api.opensea.io/api/v2/collections/{collection}/stats"
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        
        if r.status_code != 200:
            return None
        
        data = r.json()
        
        if "total" not in data:
            return None
        
        return data["total"]
        
    except Exception as e:
        logger.error(f"Error fetching {collection}: {e}")
        return None


def format_number(num):
    """Format a number nicely."""
    if num is None:
        return "N/A"
    try:
        num_float = float(num)
        if num_float == 0:
            return "0"
        if num_float < 0.001:
            return f"{num_float:.6f}"
        elif num_float < 1:
            return f"{num_float:.4f}"
        else:
            return f"{num_float:,.2f}"
    except:
        return str(num)


# -------------------------------
# KEYBOARD CREATION FUNCTIONS
# -------------------------------

def create_main_keyboard():
    """Create the main menu keyboard with premium option."""
    keyboard = [
        [InlineKeyboardButton("🏆 Popular Collections", callback_data="show_collections")],
        [
            InlineKeyboardButton("🏷 Get Floor", callback_data="ask_floor"),
            InlineKeyboardButton("📊 Get Stats", callback_data="ask_stats")
        ],
        [
            InlineKeyboardButton("📦 Get Volume", callback_data="ask_volume"),
            InlineKeyboardButton("🧾 Get Sales", callback_data="ask_sales")
        ],
        [
            InlineKeyboardButton("💎 Premium Features", callback_data="premium"),
            InlineKeyboardButton("ℹ️ Bot Info", callback_data="bot_info")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_collections_keyboard():
    """Create keyboard with popular collections."""
    keyboard = []
    row = []
    
    for i, (slug, name) in enumerate(POPULAR_COLLECTIONS.items()):
        # Truncate long names
        display_name = name[:15] + "..." if len(name) > 15 else name
        row.append(InlineKeyboardButton(display_name, callback_data=f"collection_{slug}"))
        
        # Create new row every 2 buttons
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    # Add any remaining buttons
    if row:
        keyboard.append(row)
    
    # Add back button
    keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(keyboard)


def create_collection_options_keyboard(collection_slug):
    """Create keyboard with options for a specific collection."""
    collection_name = POPULAR_COLLECTIONS.get(collection_slug, collection_slug)
    display_name = collection_name[:20] + "..." if len(collection_name) > 20 else collection_name
    
    keyboard = [
        [
            InlineKeyboardButton(f"🏷 {display_name} Floor", callback_data=f"floor_{collection_slug}"),
            InlineKeyboardButton(f"📊 {display_name} Stats", callback_data=f"stats_{collection_slug}")
        ],
        [
            InlineKeyboardButton(f"📦 {display_name} Volume", callback_data=f"volume_{collection_slug}"),
            InlineKeyboardButton(f"🧾 {display_name} Sales", callback_data=f"sales_{collection_slug}")
        ],
        [InlineKeyboardButton("🔙 Back to Collections", callback_data="show_collections")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


# -------------------------------
# MESSAGE FUNCTIONS
# -------------------------------

async def send_collection_stats(update: Update, collection_slug: str, metric_type: str):
    """Send stats for a collection based on metric type."""
    # Get display name
    display_name = POPULAR_COLLECTIONS.get(collection_slug, collection_slug)
    
    # Show loading message
    if update.callback_query:
        await update.callback_query.answer()
        message = update.callback_query.message
    else:
        message = update.message
    
    loading_text = f"🔄 Fetching {metric_type} for {display_name}..."
    await message.edit_text(loading_text)
    
    # Fetch stats
    stats = fetch_collection_stats(collection_slug)
    
    if not stats:
        error_text = f"❌ Could not fetch {metric_type} for {display_name}.\n\nPlease try another collection."
        keyboard = create_collection_options_keyboard(collection_slug)
        await message.edit_text(error_text, reply_markup=keyboard)
        return
    
    # Format response based on metric type
    if metric_type == "floor":
        floor_price = stats.get('floor_price', 'N/A')
        text = (
            f"🏷 *{display_name}*\n"
            f"Floor Price: *{format_number(floor_price)} ETH*\n\n"
            f"📊 Quick Stats:\n"
            f"• Volume: {format_number(stats.get('volume'))} ETH\n"
            f"• Sales: {format_number(stats.get('sales'))}\n"
            f"• Owners: {format_number(stats.get('num_owners'))}\n\n"
            f"🔗 [View on OpenSea](https://opensea.io/collection/{collection_slug})"
        )
    
    elif metric_type == "stats":
        text = (
            f"📊 *{display_name} - Complete Stats*\n\n"
            f"• Floor Price: {format_number(stats.get('floor_price'))} ETH\n"
            f"• Total Volume: {format_number(stats.get('volume'))} ETH\n"
            f"• Total Sales: {format_number(stats.get('sales'))}\n"
            f"• Average Price: {format_number(stats.get('average_price'))} ETH\n"
            f"• Market Cap: {format_number(stats.get('market_cap'))} ETH\n"
            f"• Num Owners: {format_number(stats.get('num_owners'))}\n"
            f"• Total Supply: {format_number(stats.get('total_supply'))}\n\n"
            f"🔗 [View on OpenSea](https://opensea.io/collection/{collection_slug})"
        )
    
    elif metric_type == "volume":
        volume_eth = stats.get('volume', 0)
        text = (
            f"📦 *{display_name}*\n"
            f"Total Volume: *{format_number(volume_eth)} ETH*\n\n"
            f"📈 Other Metrics:\n"
            f"• Floor: {format_number(stats.get('floor_price'))} ETH\n"
            f"• Sales: {format_number(stats.get('sales'))}\n"
            f"• Avg Price: {format_number(stats.get('average_price'))} ETH\n\n"
            f"🔗 [View on OpenSea](https://opensea.io/collection/{collection_slug})"
        )
    
    elif metric_type == "sales":
        sales_count = stats.get('sales', 0)
        text = (
            f"🧾 *{display_name}*\n"
            f"Total Sales: *{format_number(sales_count)}*\n\n"
            f"💰 Trading Stats:\n"
            f"• Volume: {format_number(stats.get('volume'))} ETH\n"
            f"• Avg Price: {format_number(stats.get('average_price'))} ETH\n"
            f"• Floor: {format_number(stats.get('floor_price'))} ETH\n\n"
            f"🔗 [View on OpenSea](https://opensea.io/collection/{collection_slug})"
        )
    
    else:
        text = f"❌ Unknown metric type: {metric_type}"
    
    keyboard = create_collection_options_keyboard(collection_slug)
    await message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown", disable_web_page_preview=True)


# -------------------------------
# COMMAND HANDLERS
# -------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with interactive keyboard."""
    # Get user tier info
    user_tier = monetization.check_user_tier(update.effective_user.id)
    
    text = (
        f"👋 *Welcome to NFT Analytics Bot!*\n\n"
        f"🎯 *How to Use:*\n"
        f"1. Tap '🏆 Popular Collections' to browse\n"
        f"2. Select a collection\n"
        f"3. Choose what data you want\n"
        f"4. View the results instantly!\n\n"
        f"📊 *Your Plan:* {user_tier['tier'].upper()}\n"
        f"Queries remaining today: {user_tier['remaining_queries']}\n\n"
        f"💡 *Commands:*\n"
        f"• /floor <slug> - Get floor price\n"
        f"• /stats <slug> - Get all stats\n"
        f"• /volume <slug> - Get trading volume\n"
        f"• /sales <slug> - Get sales count\n"
        f"• /search <name> - Search for collections\n"
        f"• /premium - Upgrade to premium\n\n"
        f"🔐 *Protected by enterprise-grade security*"
    )
    
    keyboard = create_main_keyboard()
    
    if update.message:
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help information."""
    await start(update, context)


async def floor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /floor command with arguments."""
    if not context.args:
        text = "❌ Please provide a collection slug.\n\nExample: `/floor boredapeyachtclub`\n\nOr use the interactive menu below:"
        keyboard = create_main_keyboard()
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")
        return
    
    collection = context.args[0].lower()
    await send_collection_stats(update, collection, "floor")


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command with arguments."""
    if not context.args:
        text = "❌ Please provide a collection slug.\n\nExample: `/stats cryptopunks`\n\nOr use the interactive menu below:"
        keyboard = create_main_keyboard()
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")
        return
    
    collection = context.args[0].lower()
    await send_collection_stats(update, collection, "stats")


async def volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /volume command with arguments."""
    if not context.args:
        text = "❌ Please provide a collection slug.\n\nExample: `/volume azuki`\n\nOr use the interactive menu below:"
        keyboard = create_main_keyboard()
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")
        return
    
    collection = context.args[0].lower()
    await send_collection_stats(update, collection, "volume")


async def sales(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /sales command with arguments."""
    if not context.args:
        text = "❌ Please provide a collection slug.\n\nExample: `/sales doodles-official`\n\nOr use the interactive menu below:"
        keyboard = create_main_keyboard()
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")
        return
    
    collection = context.args[0].lower()
    await send_collection_stats(update, collection, "sales")


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search for collections by name."""
    if not context.args:
        text = "🔍 *Search for Collections*\n\nUsage: `/search <collection name>`\n\nExample: `/search bored ape`"
        keyboard = create_main_keyboard()
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")
        return
    
    search_term = ' '.join(context.args).lower()
    results = []
    
    # Search in popular collections
    for slug, name in POPULAR_COLLECTIONS.items():
        if search_term in name.lower() or search_term in slug.lower():
            results.append((slug, name))
    
    if not results:
        text = f"❌ No collections found for '{search_term}'.\n\nTry these popular collections:"
        keyboard = create_collections_keyboard()
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")
        return
    
    # Create keyboard with search results
    keyboard = []
    row = []
    
    for i, (slug, name) in enumerate(results[:8]):  # Limit to 8 results
        display_name = name[:15] + "..." if len(name) > 15 else name
        row.append(InlineKeyboardButton(display_name, callback_data=f"collection_{slug}"))
        
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")])
    
    text = f"🔍 *Search Results for '{search_term}':*"
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show premium features and pricing."""
    premium_text = monetization.create_upgrade_message()
    keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]]
    
    if update.callback_query:
        await update.callback_query.message.edit_text(
            premium_text, 
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            premium_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )


async def bot_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot information and stats."""
    bot_stats = protection.generate_stats()
    
    text = (
        f"🤖 *NFT Analytics Bot Information*\n\n"
        f"🔐 *Protection Status:* {'✅ Active' if bot_stats['protected'] else '❌ Inactive'}\n"
        f"⏰ *Uptime:* {bot_stats['uptime']}\n"
        f"🌐 *Environment:* {bot_stats['environment']}\n"
        f"📊 *Collections Tracked:* {len(POPULAR_COLLECTIONS)}\n\n"
        f"*Features:*\n"
        f"• Real-time floor prices\n"
        f"• Volume tracking\n"
        f"• Sales analytics\n"
        f"• 12+ top collections\n"
        f"• Interactive menus\n\n"
        f"🔒 *Enterprise Protection System Active*"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]]
    
    if update.callback_query:
        await update.callback_query.message.edit_text(
            text, 
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )


# -------------------------------
# CALLBACK QUERY HANDLER
# -------------------------------

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries from inline keyboards."""
    query = update.callback_query
    await query.answer()  # Acknowledge the callback
    
    data = query.data
    
    if data == "show_collections":
        text = "🏆 *Popular NFT Collections*\n\nSelect a collection to view its stats:"
        keyboard = create_collections_keyboard()
        await query.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    
    elif data == "back_to_main":
        await start(update, context)
    
    elif data == "ask_floor":
        text = "🏷 *Get Floor Price*\n\nSelect a collection to view its floor price:"
        keyboard = create_collections_keyboard()
        await query.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    
    elif data == "ask_stats":
        text = "📊 *Get Collection Stats*\n\nSelect a collection to view its complete statistics:"
        keyboard = create_collections_keyboard()
        await query.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    
    elif data == "ask_volume":
        text = "📦 *Get Trading Volume*\n\nSelect a collection to view its trading volume:"
        keyboard = create_collections_keyboard()
        await query.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    
    elif data == "ask_sales":
        text = "🧾 *Get Sales Count*\n\nSelect a collection to view its sales count:"
        keyboard = create_collections_keyboard()
        await query.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    
    elif data == "premium":
        await premium(update, context)
    
    elif data == "bot_info":
        await bot_info(update, context)
    
    elif data == "help":
        await start(update, context)
    
    elif data.startswith("collection_"):
        collection_slug = data.replace("collection_", "")
        display_name = POPULAR_COLLECTIONS.get(collection_slug, collection_slug)
        text = f"🎯 *{display_name}*\n\nWhat would you like to see?"
        keyboard = create_collection_options_keyboard(collection_slug)
        await query.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    
    elif data.startswith("floor_"):
        collection_slug = data.replace("floor_", "")
        await send_collection_stats(update, collection_slug, "floor")
    
    elif data.startswith("stats_"):
        collection_slug = data.replace("stats_", "")
        await send_collection_stats(update, collection_slug, "stats")
    
    elif data.startswith("volume_"):
        collection_slug = data.replace("volume_", "")
        await send_collection_stats(update, collection_slug, "volume")
    
    elif data.startswith("sales_"):
        collection_slug = data.replace("sales_", "")
        await send_collection_stats(update, collection_slug, "sales")


# -------------------------------
# MAIN BOT LOOP
# -------------------------------

def main():
    """Start the bot."""
    logger.info("🤖 NFT Analytics Bot starting...")
    
    if not TELEGRAM_TOKEN:
        logger.error("❌ ERROR: TELEGRAM_TOKEN not found in environment variables")
        return
    
    if not OPENSEA_API_KEY:
        logger.warning("⚠️  OPENSEA_API_KEY not found. API calls may be rate-limited.")
    
    try:
        # Create application
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        
        # Add command handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_cmd))
        app.add_handler(CommandHandler("floor", floor))
        app.add_handler(CommandHandler("stats", stats_cmd))
        app.add_handler(CommandHandler("volume", volume))
        app.add_handler(CommandHandler("sales", sales))
        app.add_handler(CommandHandler("search", search))
        app.add_handler(CommandHandler("premium", premium))
        app.add_handler(CommandHandler("info", bot_info))
        
        # Add callback query handler
        app.add_handler(CallbackQueryHandler(handle_callback_query))
        
        logger.info("✅ Bot configured successfully!")
        logger.info("🤖 Bot is now running...")
        
        # Log bot info
        bot_stats = protection.generate_stats()
        logger.info(f"🔐 Protection: {bot_stats['protected']}")
        logger.info(f"📊 Status: {bot_stats['status']}")
        logger.info(f"🏗 Environment: {bot_stats['environment']}")
        
        app.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Error starting bot: {e}")
        raise


if __name__ == "__main__":
    main()