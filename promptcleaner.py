import re
import string
from transformers import pipeline

# Load a lightweight local LLM for text analysis (e.g., DistilBERT)
# Ensure you have transformers and torch installed: pip install transformers torch
sanitizer = pipeline("text-classification", model="distilbert-base-uncased", device=0)  # Use GPU if available

def sanitize_employee_prompt(prompt):
    # Step 1: Remove sensitive PII patterns
    pii_patterns = {
        'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'PHONE': r'\b(\+\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b',
        'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
        'CREDIT_CARD': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
        'IP_ADDRESS': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    }
    
    for key, pattern in pii_patterns.items():
        prompt = re.sub(pattern, f'[REDACTED_{key}]', prompt)

    # Step 2: Remove potentially harmful code patterns
    dangerous_patterns = [
        r'<\s*script\b[^>]*>.*?</\s*script\s*>',  # HTML scripts
        r'<\?php.*?\?>',  # PHP code
        r'<%.*?%>',  # ASP code
        r'exec\s*\(',  # Python exec
        r'os\.system\s*\(',  # System calls
        r'subprocess\.',  # Subprocess
        r'eval\s*\(',  # Python eval
        r'import\s+os',  # OS imports
        r'import\s+subprocess'  # Subprocess imports
    ]
    
    for pattern in dangerous_patterns:
        prompt = re.sub(pattern, '[REDACTED_CODE]', prompt, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 3: Use LLM to flag potentially sensitive content
    result = sanitizer(prompt)
    if result[0]['label'] == 'NEGATIVE' and result[0]['score'] > 0.9:
        prompt = '[FLAGGED_SENSITIVE_CONTENT]'

    # Step 4: Clean formatting and limit length
    prompt = re.sub(r'\s+', ' ', prompt).strip()
    prompt = ''.join(char for char in prompt if char in string.printable)
    prompt = prompt[:1000]  # Limit to 1000 characters

    # Step 5: Basic profanity filter
    profanity_list = ['badword1', 'badword2']  # Customize as needed
    for word in profanity_list:
        prompt = re.sub(rf'\b{word}\b', '***', prompt, flags=re.IGNORECASE)
    
    return prompt

def main():
    # Example usage
    test_prompt = """
    Contact: john.doe@example.com, 555-123-4567
    Run this: exec('rm -rf /')
    This is a badword1 test
    """
    cleaned = sanitize_employee_prompt(test_prompt)
    print("Original:", test_prompt)
    print("Cleaned:", cleaned)

if __name__ == "__main__":
    main()
