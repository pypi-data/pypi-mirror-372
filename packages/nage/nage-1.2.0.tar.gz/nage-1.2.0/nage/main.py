import click
import pyperclip
from .ai_client import AIClient
from .setting import Setting
from .parse import JsonParser
from . import __version__


def copy_to_clipboard(text):
    """Copy the content to clipboard."""
    try:
        pyperclip.copy(text)
        return True
    except Exception as e:
        print(f"[nage] Warning: Failed to copy to clipboard: {e}")
        return False


def setup():
    sett = Setting()
    loaded = sett.load()
    if not loaded or not sett.key:
        print("[nage] First time setup. Please enter the following information (press Enter to use default):")
        model = input("Model name (default: deepseek-chat): ").strip() or "deepseek-chat"
        endpoint = input("API endpoint (default: https://api.deepseek.com/v1): ").strip() or "https://api.deepseek.com/v1"
        api_key = input("API key (required): ").strip()
        if not api_key:
            print("[nage] API key cannot be empty. Exiting.")
            return None
        sett.change_model(model)
        sett.change_endpoint(endpoint)
        sett.change_key(api_key)
        sett.save()
        print("[nage] Setup complete. You can now use the tool.")
        return sett
    return sett


@click.command(add_help_option=False)
@click.argument('query', nargs=-1)
def cli(query):
    """Nage: Conversational AI assistant. Just type your request."""
    sett = setup()
    if sett is None:
        return
    
    if not query:
        docs_url = "https://github.com/0x3st/nage"
        print("This is a free tool by 0x3st. You can start by just ask.")
        print(f"Go to {docs_url} for further information.")
        print(f"nage-{__version__}-{sett.model}")
        return
    
    question = " ".join(query)
    if not question.strip():
        print("[nage] Please enter a question or command.")
        return
    
    ai = AIClient()
    response = ai.request(question)
    parsed = JsonParser(response)
    t = parsed.read_type()
    
    # Check if AI determines current question is unrelated to history, clear if so
    if parsed.read_clear_history():
        sett.save_history([])
        print("[nage] 📝 History cleared for new topic.")
    
    # Check if AI determines memory should be cleared
    if parsed.read_clear_memory():
        sett.clear_memo()
        print("[nage] 🧠 Memory cleared by User.")
    
    # Add user question and AI reply to history
    sett.add_history(f"User: {question}")
    sett.add_history(f"AI: {parsed.read_msg()}")
    
    if t == "sett_api":
        sett.change_key(parsed.read_content())
        sett.save()
        print(f"[nage] {parsed.read_msg()}")
    elif t == "sett_ep":
        sett.change_endpoint(parsed.read_content())
        sett.save()
        print(f"[nage] {parsed.read_msg()}")
    elif t == "sett_md":
        sett.change_model(parsed.read_content())
        sett.save()
        print(f"[nage] {parsed.read_msg()}")
    elif t == "memo":
        sett.add_memo(parsed.read_content())
        print(f"[nage] {parsed.read_msg()}")
    elif t == "ask":
        content = parsed.read_content()
        message = parsed.read_msg()
        # Message was already displayed during streaming, no need to print again
        
        if content and content.strip():  # Copy to clipboard if has any content
            if copy_to_clipboard(content):
                print(f"[nage] 💾 Copied to clipboard")
            else:
                print(f"[nage] Failed to copy command to clipboard")
    elif t == "continue":
        # Handle cases that need more information
        message = parsed.read_msg()
        # Message was already displayed during streaming, no need to print again
        print(f"[nage] 💬 Please tell me more information ...")
        # continue type clear should always be false to maintain context
    elif t == "error":
        print(f"[nage] Error: {parsed.read_msg()}")
    else:
        print(f"[nage] Unknown response type: {t}")


if __name__ == "__main__":
    cli()
