import re 
#made by AI, need to check again later

def clean_ai_text_for_tts(text: str) -> str:
    """Strip out markdown/HTML artifacts so that text-to-speech reads clean prose."""
    if not isinstance(text, str):
            raise TypeError("Text must be str type.")
    
    # 1. Remove fenced code blocks (```…```)
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'```[\s\S]*?', '', text)
    
    # 2. Remove inline code (`…`)
    text = re.sub(r'`([^`\n]+)`', r'\1', text)
    
    # 3. Remove Markdown images (![alt](url)) entirely
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    
    # 4. Convert Markdown links [text](url) → text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # 5. Remove raw URLs
    text = re.sub(r'https?://\S+', '', text)
    
    # 6. Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # 7. Strip Markdown bold/italic markers
    text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)
    text = re.sub(r'(\*|_)(.*?)\1',   r'\2', text)
    
    # 8. Remove Markdown headings (lines starting with one-or-more #)
    text = re.sub(r'^\s{0,3}#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # 9. Remove list bullets or numbered lists
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+',  '', text, flags=re.MULTILINE)
    
    # 10. Remove Python comments (lines starting with #)
    text = re.sub(r'^\s*#.*$', '', text, flags=re.MULTILINE)
    
    # 11. Collapse multiple blank lines to a single one
    text = re.sub(r'\n{2,}', '\n\n', text)
    
    # 12. Trim leading/trailing whitespace
    return text.strip()

if __name__=="__main__":
    _raw = """
        # Summary

        Heres what you need to do:

        1. Clone the repo: `git clone https://github.com/example/project.git`
        2. Install deps via `pip install -r requirements.txt`
        3. Run `<script>.py`

        ```python
        # this code block will be removed entirely
        print("hello world")
        """
    print(clean_ai_text_for_tts(_raw))