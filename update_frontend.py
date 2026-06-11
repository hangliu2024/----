import re

path = r'd:\资产管理\app\templates\ai_assistant\ai_assistant.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Replace title section - add mode switcher
old_title = '''<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;flex-wrap:wrap;gap:12px">
    <div>
        <h1 class="mi-page-title"><i class="bi bi-robot"></i> AI数据问答</h1>
        <p style="font-size:14px;color:var(--text-hint);margin:4px 0 0">用自然语言查询和分析数据</p>
    </div>
</div>'''

new_title = '''<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;flex-wrap:wrap;gap:12px">
    <div>
        <h1 class="mi-page-title"><i class="bi bi-robot"></i> AI助手</h1>
        <p style="font-size:14px;color:var(--text-hint);margin:4px 0 0">切换模式，选择数据问答或一般对话</p>
    </div>
</div>

<div style="display:flex;gap:0;margin-bottom:16px;background:var(--bg);border-radius:var(--radius);padding:4px;border:1px solid var(--border-light);width:fit-content">
    <div id="modeQuery" class="ai-mode-tab active" onclick="switchMode('query')" style="padding:8px 24px;border-radius:8px;cursor:pointer;font-size:14px;font-weight:500;transition:all 0.2s;background:var(--accent);color:white">
        <i class="bi bi-database"></i> 数据问答
    </div>
    <div id="modeChat" class="ai-mode-tab" onclick="switchMode('chat')" style="padding:8px 24px;border-radius:8px;cursor:pointer;font-size:14px;font-weight:500;transition:all 0.2s;color:var(--text-secondary)">
        <i class="bi bi-chat-dots"></i> 一般对话
    </div>
</div>'''

c = c.replace(old_title, new_title)

# 2. Replace welcome message
old_welcome = '''        <div class="message bot">
            <div class="message-avatar">🤖</div>
            <div class="message-body">
                <div class="message-content">
                    <div>👋 您好！我是AI数据问答助手。</div>
                    <div style="margin-top:8px">我可以帮您查询和分析数据，比如：</div>
                    <ul style="margin:8px 0 0 24px">
                        <li>查询员工总数、在职人数</li>
                        <li>统计办公电脑数量</li>
                        <li>分析部门人员结构</li>
                        <li>查看新入职员工信息</li>
                    </ul>
                    <div style="margin-top:8px">请输入您的问题！</div>
                </div>
                <div class="message-time" id="currentTime"></div>
            </div>
        </div>'''

new_welcome = '''        <div class="message bot">
            <div class="message-avatar">🤖</div>
            <div class="message-body">
                <div class="message-content" id="welcomeMessage">
                </div>
                <div class="message-time" id="currentTime"></div>
            </div>
        </div>'''

c = c.replace(old_welcome, new_welcome)

# 3. Replace suggestions with simpler version
old_suggestions = '''    <div class="suggestions">
        <div class="suggestions-title">💡 提问技巧：</div>
        <div style="display:flex;flex-wrap:wrap;gap:6px">
            <span class="suggestion-btn">✓ 具体：说姓名/工号比说"某人"更准</span>
            <span class="suggestion-btn">✓ 明确：指明"在职"或"离职"</span>
            <span class="suggestion-btn">✓ 简洁：一句话表达完整意图</span>
            <span class="suggestion-btn">✓ 直接：问"XX的电话"而非"帮我查一下..."</span>
        </div>
    </div>'''

new_suggestions = '''    <div class="suggestions" id="suggestionBox">
        <div class="suggestions-title" id="suggestionTitle">💡 试试这样问：</div>
        <div id="suggestionContent" style="display:flex;flex-wrap:wrap;gap:6px">
            <span class="suggestion-btn">👥 在职员工总数</span>
            <span class="suggestion-btn">💻 办公电脑数量</span>
            <span class="suggestion-btn">🏢 各部门人数统计</span>
            <span class="suggestion-btn">📅 本月新入职员工</span>
            <span class="suggestion-btn">🔍 查询某个员工的联系方式</span>
        </div>
    </div>'''

c = c.replace(old_suggestions, new_suggestions)

# 4. Add mode switching JS before the closing </script>
old_script_end = '''document.getElementById('chatForm').addEventListener('submit', function(e) {
    e.preventDefault();
    sendMessage();
});

window.addEventListener('DOMContentLoaded', loadChatHistory);'''

new_script_end = '''var currentMode = 'query';

function switchMode(mode) {
    currentMode = mode;
    document.querySelectorAll('.ai-mode-tab').forEach(function(el) {
        el.style.background = 'transparent';
        el.style.color = 'var(--text-secondary)';
    });
    var tab = document.getElementById(mode === 'query' ? 'modeQuery' : 'modeChat');
    tab.style.background = 'var(--accent)';
    tab.style.color = 'white';
    
    var suggestionBox = document.getElementById('suggestionBox');
    var suggestionTitle = document.getElementById('suggestionTitle');
    var suggestionContent = document.getElementById('suggestionContent');
    var input = document.getElementById('questionInput');
    var welcome = document.getElementById('welcomeMessage');
    
    if (mode === 'query') {
        suggestionTitle.textContent = '💡 试试这样问：';
        suggestionContent.innerHTML = '<span class="suggestion-btn">\ud83d\udc65 \u5728\u804c\u5458\u5de5\u603b\u6570</span><span class="suggestion-btn">\ud83d\udcbb \u529e\u516c\u7535\u8111\u6570\u91cf</span><span class="suggestion-btn">\ud83c\udfe2 \u5404\u90e8\u95e8\u4eba\u6570\u7edf\u8ba1</span><span class="suggestion-btn">\ud83d\udcc5 \u672c\u6708\u65b0\u5165\u804c\u5458\u5de5</span><span class="suggestion-btn">\ud83d\udd0d \u67e5\u8be2\u67d0\u4e2a\u5458\u5de5\u7684\u8054\u7cfb\u65b9\u5f0f</span>';
        input.placeholder = '\u8bf7\u8f93\u5165\u60a8\u8981\u67e5\u8be2\u7684\u6570\u636e\u95ee\u9898...';
        welcome.innerHTML = '<div>\ud83d\udc4b \u60a8\u597d\uff01\u6211\u662f\u6570\u636e\u67e5\u8be2\u52a9\u624b\u3002</div><div style="margin-top:8px">\u6211\u53ef\u4ee5\u5e2e\u60a8\u67e5\u8be2\u5206\u6790\u6570\u636e\uff0c\u6bd4\u5982\uff1a</div><ul style="margin:8px 0 0 24px"><li>\u67e5\u8be2\u5458\u5de5\u603b\u6570\u3001\u5728\u804c\u4eba\u6570</li><li>\u7edf\u8ba1\u529e\u516c\u7535\u8111\u6570\u91cf</li><li>\u5206\u6790\u90e8\u95e8\u4eba\u5458\u7ed3\u6784</li><li>\u67e5\u770b\u65b0\u5165\u804c\u5458\u5de5\u4fe1\u606f</li></ul><div style="margin-top:8px">\u8bf7\u8f93\u5165\u60a8\u7684\u95ee\u9898\uff01</div>';
        suggestionBox.style.display = 'block';
    } else {
        suggestionTitle.textContent = '\ud83d\udca1 \u53ef\u4ee5\u8ddf\u6211\u804a\u70b9\u4ec0\u4e48\uff1a';
        suggestionContent.innerHTML = '<span class="suggestion-btn">\ud83d\udc4b \u4f60\u597d\uff01</span><span class="suggestion-btn">\ud83d\udcd6 \u7ed9\u6211\u8bb2\u4e2a\u7b11\u8bdd</span><span class="suggestion-btn">\u2753 \u4eca\u5929\u5929\u6c14\u600e\u4e48\u6837</span><span class="suggestion-btn">\u270d\ufe0f \u5199\u4e00\u6bb5\u5de5\u4f5c\u603b\u7ed3</span>';
        input.placeholder = '\u8f93\u5165\u60a8\u7684\u8bdd\u9898...';
        welcome.innerHTML = '<div>\ud83d\udc4b \u60a8\u597d\uff01\u6211\u662fAI\u804a\u5929\u52a9\u624b\u3002</div><div style="margin-top:8px">\u968f\u4fbf\u8ddf\u6211\u804a\u70b9\u4ec0\u4e48\u5427\uff01</div>';
        suggestionBox.style.display = 'block';
    }
}

document.getElementById('chatForm').addEventListener('submit', function(e) {
    e.preventDefault();
    sendMessage();
});

window.addEventListener('DOMContentLoaded', function() {
    loadChatHistory();
    switchMode('query');
});'''

c = c.replace(old_script_end, new_script_end)

# 5. Update sendMessage to pass mode
old_fetch = '''    fetch('/api/ai/query/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question })
    })'''

new_fetch = '''    fetch('/api/ai/query/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question, mode: currentMode })
    })'''

c = c.replace(old_fetch, new_fetch)

# 6. Simplify the thinking process - hide it for chat mode
# Add mode check in createBotMessage
old_createBot = '''function createBotMessage() {'''
new_createBot = '''function createBotMessage() {
    if (currentMode === 'chat') {
        // 一般对话模式：直接显示简单的机器人消息容器
        var container = document.getElementById('chatMessages');
        var time = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
        var div = document.createElement('div');
        div.className = 'message bot';
        var avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = '🤖';
        var body = document.createElement('div');
        body.className = 'message-body';
        currentContentDiv = document.createElement('div');
        currentContentDiv.className = 'message-content streaming-cursor';
        body.appendChild(currentContentDiv);
        var timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = time;
        body.appendChild(timeDiv);
        div.appendChild(avatar);
        div.appendChild(body);
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
        currentBotMessage = div;
        thinkingSteps = [];
        rawContent = '';
        rawThinkingContent = '';
        isStreaming = true;
        return;
    }'''

c = c.replace(old_createBot, new_createBot)

with open(path, 'w', encoding='utf-8', errors='surrogateescape') as f:
    f.write(c)
print("done")
