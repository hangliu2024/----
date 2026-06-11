import os

path = r'd:\资产管理\app\templates\ai_assistant\ai_assistant.html'

# Read file
with open(path, 'rb') as f:
    raw = f.read()
content = raw.decode('utf-8', errors='replace').replace('\r\n', '\n')
print(f'Read {len(content)} chars')

# 1. Title + mode switch
old1 = '    <div>\n        <h1 class="mi-page-title"><i class="bi bi-robot"></i> AI\u6570\u636e\u95ee\u7b54</h1>\n        <p style="font-size:14px;color:var(--text-hint);margin:4px 0 0">\u7528\u81ea\u7136\u8bed\u8a00\u67e5\u8be2\u548c\u5206\u6790\u6570\u636e</p>\n    </div>\n</div>'

new1 = '    <div>\n        <h1 class="mi-page-title"><i class="bi bi-robot"></i> AI\u5c0f\u52a9\u624b</h1>\n        <p style="font-size:14px;color:var(--text-hint);margin:4px 0 0">\u5207\u6362\u6a21\u5f0f\uff0c\u9009\u62e9\u6570\u636e\u95ee\u7b54\u6216\u4e00\u822c\u5bf9\u8bdd</p>\n    </div>\n</div>\n\n<div style="display:flex;gap:0;margin-bottom:12px;background:var(--bg);border-radius:var(--radius);padding:4px;border:1px solid var(--border-light);width:fit-content">\n    <div id="modeQuery" class="ai-mode-tab" onclick="switchMode(\'query\')" style="padding:8px 24px;border-radius:8px;cursor:pointer;font-size:14px;font-weight:500;transition:all 0.2s;background:var(--accent);color:white">\n        <i class="bi bi-database"></i> \u6570\u636e\u95ee\u7b54\n    </div>\n    <div id="modeChat" class="ai-mode-tab" onclick="switchMode(\'chat\')" style="padding:8px 24px;border-radius:8px;cursor:pointer;font-size:14px;font-weight:500;transition:all 0.2s;color:var(--text-secondary)">\n        <i class="bi bi-chat-dots"></i> \u4e00\u822c\u5bf9\u8bdd\n    </div>\n</div>'

if old1 in content:
    content = content.replace(old1, new1)
    print('Title replaced')
else:
    print('Title NOT found')

# 2. Welcome message
old2 = '        <div class="message bot">\n            <div class="message-avatar">\U0001f916</div>\n            <div class="message-body">\n                <div class="message-content">\n                    <div>\U0001f44b \u60a8\u597d\uff01\u6211\u662fAI\u6570\u636e\u95ee\u7b54\u52a9\u624b\u3002</div>\n                    <div style="margin-top:8px">\u6211\u53ef\u4ee5\u5e2e\u60a8\u67e5\u8be2\u548c\u5206\u6790\u6570\u636e\uff0c\u6bd4\u5982\uff1a</div>\n                    <ul style="margin:8px 0 0 24px">\n                        <li>\u67e5\u8be2\u5458\u5de5\u603b\u6570\u3001\u5728\u804c\u4eba\u6570</li>\n                        <li>\u7edf\u8ba1\u529e\u516c\u7535\u8111\u6570\u91cf</li>\n                        <li>\u5206\u6790\u90e8\u95e8\u4eba\u5458\u7ed3\u6784</li>\n                        <li>\u67e5\u770b\u65b0\u5165\u804c\u5458\u5de5\u4fe1\u606f</li>\n                    </ul>\n                    <div style="margin-top:8px">\u8bf7\u8f93\u5165\u60a8\u7684\u95ee\u9898\uff01</div>\n                </div>\n                <div class="message-time" id="currentTime"></div>\n            </div>\n        </div>'

new2 = '        <div class="message bot">\n            <div class="message-avatar">\U0001f916</div>\n            <div class="message-body">\n                <div class="message-content" id="welcomeMessage">\n                    <div>\U0001f44b \u60a8\u597d\uff01\u8bf7\u5728\u4e0a\u65b9\u9009\u62e9\u6a21\u5f0f\uff1a</div>\n                    <div style="margin-top:8px"><strong>\u6570\u636e\u95ee\u7b54</strong> - \u67e5\u8be2\u5458\u5de5\u3001\u8d44\u4ea7\u7b49\u6570\u636e</div>\n                    <div style="margin-top:4px"><strong>\u4e00\u822c\u5bf9\u8bdd</strong> - \u804a\u5929\u3001\u54a8\u8be2\u3001\u5199\u4f5c\u7b49</div>\n                </div>\n                <div class="message-time" id="currentTime"></div>\n            </div>\n        </div>'

if old2 in content:
    content = content.replace(old2, new2)
    print('Welcome replaced')
else:
    print('Welcome NOT found')
    idx = content.find('message-avatar')
    if idx >= 0:
        print('Found avatar context:', content[idx:idx+100].replace('\n', '|'))

# 3. Fetch - add mode
old3 = 'body: JSON.stringify({ question: question })\n    })'
new3 = 'body: JSON.stringify({ question: question, mode: currentMode })\n    })'

if old3 in content:
    content = content.replace(old3, new3)
    print('Fetch updated')
else:
    print('Fetch NOT found')
    idx = content.find('JSON.stringify({ question')
    if idx >= 0:
        print('Fetch context:', repr(content[idx:idx+60]))

# 4. switchMode before createBotMessage
old4 = 'function createBotMessage() {'
new4 = '''var currentMode = 'query';

function switchMode(mode) {
    currentMode = mode;
    document.querySelectorAll('.ai-mode-tab').forEach(function(el) {
        el.style.background = 'transparent';
        el.style.color = 'var(--text-secondary)';
    });
    var tab = document.getElementById(mode === 'query' ? 'modeQuery' : 'modeChat');
    tab.style.background = 'var(--accent)';
    tab.style.color = 'white';
    var welcome = document.getElementById('welcomeMessage');
    var input = document.getElementById('questionInput');
    if (!welcome) return;
    if (mode === 'query') {
        welcome.innerHTML = '<div>\U0001f44b \u60a8\u597d\uff01\u6211\u662f\u6570\u636e\u67e5\u8be2\u52a9\u624b\u3002</div><div style="margin-top:8px">\u6211\u53ef\u4ee5\u5e2e\u60a8\u67e5\u8be2\u5206\u6790\u6570\u636e\uff0c\u6bd4\u5982\uff1a</div><ul style="margin:8px 0 0 24px"><li>\u67e5\u8be2\u5458\u5de5\u603b\u6570\u3001\u5728\u804c\u4eba\u6570</li><li>\u7edf\u8ba1\u529e\u516c\u7535\u8111\u6570\u91cf</li><li>\u5206\u6790\u90e8\u95e8\u4eba\u5458\u7ed3\u6784</li><li>\u67e5\u770b\u65b0\u5165\u804c\u5458\u5de5\u4fe1\u606f</li></ul>';
        input.placeholder = '\u8bf7\u8f93\u5165\u60a8\u8981\u67e5\u8be2\u7684\u6570\u636e\u95ee\u9898...';
    } else {
        welcome.innerHTML = '<div>\U0001f44b \u60a8\u597d\uff01\u6211\u662f\u804a\u5929\u52a9\u624b\u3002</div><div style="margin-top:8px">\u968f\u4fbf\u8ddf\u6211\u804a\u70b9\u4ec0\u4e48\u5427\uff01</div>';
        input.placeholder = '\u8f93\u5165\u60a8\u7684\u8bdd\u9898...';
    }
}

function createBotMessage() {'''

if old4 in content:
    content = content.replace(old4, new4)
    print('switchMode added')
else:
    print('createBotMessage NOT found')

# Write back with CRLF
content = content.replace('\n', '\r\n')
with open(path, 'wb') as f:
    f.write(content.encode('utf-8'))
print('Written OK')
