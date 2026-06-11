import re
path = r'd:\资产管理\app\templates\ai_assistant\ai_assistant.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    "    isStreaming = false;\n}",
    "    isStreaming = false;\n    saveChatHistory();\n}"
)

save_func = '''
function saveChatHistory() {
    try {
        var msgs = [];
        document.querySelectorAll('#chatMessages .message').forEach(function(el) {
            var role = el.classList.contains('user') ? 'user' : 'assistant';
            var cd = el.querySelector('.message-content');
            var t = cd ? cd.textContent.trim() : '';
            if (t) msgs.push({role: role, content: t});
        });
        if (msgs.length > 0) {
            localStorage.setItem('ai_chat_history', JSON.stringify(msgs));
        }
    } catch(e) {}
}

function loadChatHistory() {
    try {
        var saved = localStorage.getItem('ai_chat_history');
        if (!saved) return;
        var msgs = JSON.parse(saved);
        if (!msgs || !msgs.length) return;
        var container = document.getElementById('chatMessages');
        container.innerHTML = '';
        msgs.forEach(function(msg) {
            var div = document.createElement('div');
            div.className = 'message ' + msg.role;
            var icon = msg.role === 'user' ? 'bi-person-circle' : 'bi-robot';
            var bg = msg.role === 'user' ? 'linear-gradient(135deg,#e8f5e9,#fce4ec)' : 'linear-gradient(135deg,var(--accent),#5a3e9e)';
            var c = msg.role === 'user' ? escapeHtml(msg.content) : (typeof marked !== 'undefined' ? marked.parse(msg.content) : msg.content);
            div.innerHTML = '<div class="message-avatar" style="background:' + bg + '"><i class="bi ' + icon + '" style="font-size:20px;color:' + (msg.role === 'user' ? '#333' : '#fff') + '"></i></div><div class="message-body"><div class="message-content">' + c + '</div></div>';
            container.appendChild(div);
        });
        container.scrollTop = container.scrollHeight;
    } catch(e) {}
}

function escapeHtml(text) {
    var d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
}

'''

# Insert before event listener
old = "document.getElementById('chatForm').addEventListener('submit', function(e) {\n    e.preventDefault();\n    sendMessage();\n});\n</script>"
new_s = save_func + "document.getElementById('chatForm').addEventListener('submit', function(e) {\n    e.preventDefault();\n    sendMessage();\n});\n\nwindow.addEventListener('DOMContentLoaded', loadChatHistory);\n</script>"
c = c.replace(old, new_s)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('done')
