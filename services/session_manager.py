import os
import json
import time

SESSIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sessions")

def ensure_sessions_dir():
    """Ensure the sessions directory exists on disk."""
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR)

def save_session(session_data):
    """
    Saves a completed boardroom session to a JSON file on disk.
    Returns the filename of the saved session.
    """
    ensure_sessions_dir()
    
    company = session_data.get("company", "Unknown").replace(" ", "_").lower()
    timestamp = int(session_data.get("timestamp", time.time()))
    filename = f"session_{timestamp}_{company}.json"
    filepath = os.path.join(SESSIONS_DIR, filename)
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        print(f"Session saved successfully to: {filepath}")
        return filename
    except Exception as e:
        print(f"Failed to save session to disk: {e}")
        return None

def load_session(filename):
    """
    Loads a specific boardroom session JSON file by name.
    """
    ensure_sessions_dir()
    filepath = os.path.join(SESSIONS_DIR, filename)
    
    if not os.path.exists(filepath):
        print(f"Session file not found: {filepath}")
        return None
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            session_data = json.load(f)
        return session_data
    except Exception as e:
        print(f"Failed to load session from disk: {e}")
        return None

def list_sessions():
    """
    Lists all saved boardroom sessions, sorted by timestamp descending.
    Returns a list of dicts with file metadata.
    """
    ensure_sessions_dir()
    sessions = []
    
    for filename in os.listdir(SESSIONS_DIR):
        if filename.endswith(".json") and filename.startswith("session_"):
            filepath = os.path.join(SESSIONS_DIR, filename)
            try:
                # Quickly inspect file modified time or read the header metadata
                stat_info = os.stat(filepath)
                mod_time = stat_info.st_mtime
                
                with open(filepath, "r", encoding="utf-8") as f:
                    # Just read the first few fields for quick meta listing
                    data = json.load(f)
                    sessions.append({
                        "filename": filename,
                        "company": data.get("company", "Unknown"),
                        "market": data.get("market", "Unknown"),
                        "budget": data.get("budget", 0),
                        "timeline": data.get("timeline", "Unknown"),
                        "decision": data.get("ceo_decision", "DELAY ENTRY"),
                        "confidence": data.get("ceo_confidence", 0),
                        "timestamp": data.get("timestamp", mod_time)
                    })
            except Exception as e:
                print(f"Error reading session file {filename}: {e}")
                
    # Sort sessions by timestamp descending (newest first)
    sessions.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    return sessions
