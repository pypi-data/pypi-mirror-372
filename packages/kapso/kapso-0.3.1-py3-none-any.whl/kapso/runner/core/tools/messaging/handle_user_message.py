from langchain_core.tools import tool

@tool
async def handle_user_message():
    """
    ⚠️ SYSTEM INTERNAL TOOL - DO NOT USE ⚠️
    
    This tool is automatically injected by the system during user message interrupts.
    Direct usage by agents will cause errors and should be avoided.
    
    If you see this tool being called, it indicates a system bug that needs fixing.
    """
    return {
        "error": "Invalid tool usage", 
        "message": "handle_user_message should not be called directly by agents"
    }
