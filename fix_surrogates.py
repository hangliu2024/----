# Fix surrogate pairs in the update script
import re

# Fix the Python script
script_path = r'd:\资产管理\update_frontend.py'
with open(script_path, 'r', encoding='utf-8', errors='surrogateescape') as f:
    c = f.read()

# Replace surrogate pairs with safe chars
c = c.encode('utf-8', errors='replace').decode('utf-8')

with open(script_path, 'w', encoding='utf-8') as f:
    f.write(c)

print("Fixed script")

# Fix the HTML file
html_path = r'd:\资产管理\app\templates\ai_assistant\ai_assistant.html'
with open(html_path, 'r', encoding='utf-8', errors='surrogateescape') as f:
    h = f.read()
h = h.encode('utf-8', errors='replace').decode('utf-8')
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(h)

print("Fixed HTML")
