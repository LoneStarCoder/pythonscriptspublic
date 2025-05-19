import requests
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
import socket
import ssl
import json
from datetime import datetime

LOOKUP_DESCRIPTIONS = {
    "IP Information": "Retrieves geographical location, ISP, organization, and other details about an IP address.",
    "DNS Lookup": "Queries DNS records for a domain name, showing A, AAAA, MX, TXT, and other DNS records.",
    "SSL Certificate": "Checks SSL/TLS certificate information including expiry date, issuer, and validity period.",
    "Website Status": "Tests website availability, response time, HTTP status code, and server headers."
}

def fetch_dns_info(domain: str):
    """Fetches DNS information using Google's DNS API."""
    try:
        url = f"https://dns.google/resolve?name={domain}"
        response = requests.get(url, timeout=5)
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

def fetch_ssl_info(domain: str):
    """Fetches SSL certificate information."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                return {
                    "subject": dict(x[0] for x in cert['subject']),
                    "issuer": dict(x[0] for x in cert['issuer']),
                    "version": cert['version'],
                    "expires": cert['notAfter'],
                    "valid_from": cert['notBefore']
                }
    except Exception as e:
        return f"Error: {e}"

def check_website_status(url: str):
    """Checks website status and response time."""
    try:
        response = requests.get(url, timeout=5)
        return {
            "status_code": response.status_code,
            "response_time": f"{response.elapsed.total_seconds():.2f}s",
            "headers": dict(response.headers)
        }
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

def fetch_ip_info(ip: str):
    """Fetches IP information from ipinfo.io."""
    try:
        url = f"https://ipinfo.io/{ip}/json"
        response = requests.get(url, timeout=5)  # Add a timeout
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

def update_description(*args):
    """Updates the description text when lookup type changes."""
    selected = lookup_var.get()
    description_label.config(text=LOOKUP_DESCRIPTIONS[selected])

def perform_lookup():
    """Performs the selected lookup type."""
    query = input_entry.get()
    if not query:
        messagebox.showerror("Error", "Please enter a value to lookup.")
        return

    lookup_type = lookup_var.get()
    result = None

    if lookup_type == "IP Information":
        result = fetch_ip_info(query)
    elif lookup_type == "DNS Lookup":
        result = fetch_dns_info(query)
    elif lookup_type == "SSL Certificate":
        result = fetch_ssl_info(query)
    elif lookup_type == "Website Status":
        result = check_website_status(query)

    result_text.delete("1.0", tk.END)
    if isinstance(result, str):
        result_text.insert(tk.END, result)
    else:
        result_text.insert(tk.END, json.dumps(result, indent=2))

# Create the main window
root = tk.Tk()
root.title("IP Information Lookup")
root.configure(bg='#f0f0f0')

# Configure style
style = ttk.Style()
style.configure('Custom.TFrame', background='#f0f0f0')
style.configure('Custom.TButton', 
    padding=10, 
    font=('Segoe UI', 10),
    background='#0078D7'
)
style.configure('Custom.TLabel', 
    font=('Segoe UI', 11),
    background='#f0f0f0'
)

# Create main frame
main_frame = ttk.Frame(root, style='Custom.TFrame', padding="20")
main_frame.pack(fill=tk.BOTH, expand=True)

# Title
title_font = Font(family='Segoe UI', size=16, weight='bold')
title_label = tk.Label(
    main_frame,
    text="IP Information Lookup",
    font=title_font,
    background='#f0f0f0',
    foreground='#2C3E50'
)
title_label.pack(pady=(0, 20))

# IP Address Frame
input_frame = ttk.Frame(main_frame, style='Custom.TFrame')
input_frame.pack(fill=tk.X, pady=(0, 15))

# Add lookup type dropdown
lookup_types = ["IP Information", "DNS Lookup", "SSL Certificate", "Website Status"]
lookup_var = tk.StringVar(value=lookup_types[0])
lookup_dropdown = ttk.Combobox(
    input_frame,
    textvariable=lookup_var,
    values=lookup_types,
    state="readonly",
    width=15,
    font=('Segoe UI', 10)
)
lookup_dropdown.pack(side=tk.LEFT, padx=(0, 10))

input_label = ttk.Label(
    input_frame,
    text="Enter value:",
    style='Custom.TLabel'
)
input_label.pack(side=tk.LEFT, padx=(0, 10))

input_entry = ttk.Entry(
    input_frame,
    width=30,
    font=('Segoe UI', 10)
)
input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

# Add description frame after input frame
description_frame = ttk.Frame(main_frame, style='Custom.TFrame')
description_frame.pack(fill=tk.X, pady=(0, 15))

description_label = ttk.Label(
    description_frame,
    text=LOOKUP_DESCRIPTIONS["IP Information"],  # Default description
    style='Custom.TLabel',
    wraplength=400,  # Wrap text at 400 pixels
    justify=tk.LEFT
)
description_label.pack(fill=tk.X, padx=5)

# Bind the dropdown change to update description
lookup_var.trace('w', update_description)

# Fetch Button
fetch_button = ttk.Button(
    main_frame,
    text="Lookup Information",
    command=perform_lookup,
    style='Custom.TButton'
)
fetch_button.pack(pady=15)

# Result Text Area
result_frame = ttk.Frame(main_frame, style='Custom.TFrame')
result_frame.pack(fill=tk.BOTH, expand=True)

result_text = tk.Text(
    result_frame,
    height=15,
    width=50,
    font=('Consolas', 10),
    bg='white',
    relief=tk.SOLID,
    padx=10,
    pady=10
)
result_text.pack(fill=tk.BOTH, expand=True)

# Center window on screen
root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry(f'{width}x{height}+{x}+{y}')

# Run the main loop
root.mainloop()
