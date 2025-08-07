// MCP 设置页面 JavaScript

class MCPManager {
    constructor() {
        this.currentMemoryPage = 1;
        this.currentLogsPage = 1;
        this.memorySearchTimeout = null;
        this.init();
    }

    async init() {
        // 检查认证状态
        const isAuthenticated = await this.checkAuthentication();
        if (!isAuthenticated) {
            this.showLoginPrompt();
            return;
        }

        this.bindEvents();
        this.loadServers();
        
        // 根据当前标签页加载数据
        const activeTab = document.querySelector('.tab.active').getAttribute('data-tab');
        if (activeTab === 'memories') {
            this.loadMemoryStats();
            this.loadMemories();
        } else if (activeTab === 'logs') {
            this.loadLogs();
        }
    }

    async checkAuthentication() {
        try {
            const response = await fetch('/api/auth/check');
            const data = await response.json();
            return data.authenticated;
        } catch (error) {
            console.error('检查认证状态失败:', error);
            return false;
        }
    }

    async apiRequest(url, options = {}) {
        try {
            const response = await fetch(url, options);
            
            if (response.status === 401) {
                this.showLoginPrompt();
                return null;
            }

            return await response.json();
        } catch (error) {
            console.error('API请求失败:', error);
            this.showAlert('请求失败: ' + error.message, 'error');
            return null;
        }
    }

    bindEvents() {
        // 标签页切换
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                this.switchTab(tab.getAttribute('data-tab'));
            });
        });

        // 记忆搜索
        const searchInput = document.getElementById('memory-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                clearTimeout(this.memorySearchTimeout);
                this.memorySearchTimeout = setTimeout(() => {
                    this.searchMemories(e.target.value);
                }, 300);
            });
        }

        // 模态框关闭
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.hideAddServerModal();
            }
        });
    }

    switchTab(tabName) {
        // 更新标签页状态
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.toggle('active', tab.getAttribute('data-tab') === tabName);
        });

        // 显示对应内容
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === `${tabName}-tab`);
        });

        // 加载对应数据
        if (tabName === 'memories') {
            this.loadMemoryStats();
            this.loadMemories();
        } else if (tabName === 'logs') {
            this.loadLogs();
        }
    }

    async loadServers() {
        const serverList = document.getElementById('server-list');
        serverList.innerHTML = '<div class="loading"><div class="spinner"></div><div>加载服务器列表...</div></div>';

        const data = await this.apiRequest('/api/mcp/servers');
        if (!data) return;

        if (data.servers.length === 0) {
            serverList.innerHTML = '<div class="empty-state"><div class="empty-state-icon">🔧</div><div>暂无MCP服务器</div></div>';
            return;
        }

        const serversHtml = data.servers.map(server => this.renderServer(server)).join('');
        serverList.innerHTML = serversHtml;
    }

    renderServer(server) {
        const statusClass = server.enabled ? 'status-running' : 'status-stopped';
        const statusText = server.enabled ? '运行中' : '已停止';
        const builtinBadge = server.builtin ? '<span style="background: rgba(255, 149, 0, 0.15); color: var(--warning-color); padding: 0.25rem 0.75rem; border-radius: var(--radius-full); font-size: 0.8rem; font-weight: 600; margin-left: 0.5rem;">内置</span>' : '';
        
        return `
            <div class="server-item card">
                <div class="server-header">
                    <div style="display: flex; align-items: center;">
                        <h3 class="server-name">${server.name}</h3>
                        ${builtinBadge}
                    </div>
                    <span class="server-status ${statusClass}">${statusText}</span>
                </div>
                <div class="server-details">
                    <div><strong>命令:</strong> ${server.command}</div>
                    ${server.args.length > 0 ? `<div><strong>参数:</strong> ${server.args.join(' ')}</div>` : ''}
                    ${Object.keys(server.env).length > 0 ? `<div><strong>环境变量:</strong> ${Object.keys(server.env).length} 个</div>` : ''}
                </div>
                <div class="server-actions">
                    ${!server.builtin ? `
                        <button class="btn btn-secondary" onclick="mcpManager.toggleServer(${server.id})">
                            ${server.enabled ? '停止' : '启动'}
                        </button>
                        <button class="btn btn-danger" onclick="mcpManager.deleteServer(${server.id})">删除</button>
                    ` : ''}
                </div>
            </div>
        `;
    }

    async loadMemoryStats() {
        const statsContainer = document.getElementById('memory-stats');
        statsContainer.innerHTML = '<div class="loading"><div class="spinner"></div><div>加载统计信息...</div></div>';

        const data = await this.apiRequest('/api/mcp/memories/stats');
        if (!data || !data.stats) {
            statsContainer.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📊</div><div>暂无统计数据</div></div>';
            return;
        }

        const stats = data.stats;
        if (!stats.total_count && stats.total_count !== 0) {
            statsContainer.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📊</div><div>统计数据格式错误</div></div>';
            return;
        }

        const statsHtml = `
            <div class="stat-card card">
                <div class="stat-number">${stats.total_count || 0}</div>
                <div class="stat-label">总记忆数</div>
            </div>
            ${(stats.type_stats || []).map(stat => `
                <div class="stat-card card">
                    <div class="stat-number">${stat.count || 0}</div>
                    <div class="stat-label">${this.getMemoryTypeLabel(stat.type)}</div>
                </div>
            `).join('')}
        `;

        statsContainer.innerHTML = statsHtml;
    }

    async loadMemories(page = 1, search = '') {
        this.currentMemoryPage = page;
        const memoryList = document.getElementById('memory-list');
        
        if (page === 1) {
            memoryList.innerHTML = '<div class="loading"><div class="spinner"></div><div>加载记忆列表...</div></div>';
        }

        const params = new URLSearchParams({
            page: page.toString(),
            per_page: '20'
        });

        if (search) {
            params.append('search', search);
        }

        const data = await this.apiRequest(`/api/mcp/memories?${params}`);
        if (!data) {
            memoryList.innerHTML = '<div class="empty-state"><div class="empty-state-icon">🧠</div><div>加载失败，请刷新重试</div></div>';
            document.getElementById('memory-pagination').innerHTML = '';
            return;
        }

        if (!data.memories || data.memories.length === 0) {
            memoryList.innerHTML = '<div class="empty-state"><div class="empty-state-icon">🧠</div><div>暂无记忆数据</div></div>';
            document.getElementById('memory-pagination').innerHTML = '';
            return;
        }

        const memoriesHtml = data.memories.map(memory => this.renderMemory(memory)).join('');
        memoryList.innerHTML = memoriesHtml;

        // 渲染分页
        if (data.pagination) {
            this.renderPagination('memory-pagination', data.pagination, (page) => this.loadMemories(page, search));
        } else {
            document.getElementById('memory-pagination').innerHTML = '';
        }
    }

    renderMemory(memory) {
        const typeLabel = this.getMemoryTypeLabel(memory.memory_type);
        const confidencePercentage = Math.round(memory.confidence * 100);
        
        return `
            <div class="memory-item card">
                <div class="memory-header">
                    <div class="memory-key">${memory.key}</div>
                    <span class="memory-type">${typeLabel}</span>
                </div>
                <div class="memory-value">${memory.value}</div>
                <div class="memory-meta">
                    <span>${new Date(memory.created_at).toLocaleDateString('zh-CN')}</span>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span>置信度: ${confidencePercentage}%</span>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: ${confidencePercentage}%"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async loadLogs(page = 1) {
        this.currentLogsPage = page;
        const logsList = document.getElementById('logs-list');
        
        if (page === 1) {
            logsList.innerHTML = '<div class="loading"><div class="spinner"></div><div>加载执行日志...</div></div>';
        }

        const data = await this.apiRequest(`/api/mcp/logs?page=${page}&per_page=20`);
        if (!data) {
            logsList.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📋</div><div>加载失败，请刷新重试</div></div>';
            document.getElementById('logs-pagination').innerHTML = '';
            return;
        }

        if (!data.logs || data.logs.length === 0) {
            logsList.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📋</div><div>暂无执行日志</div></div>';
            document.getElementById('logs-pagination').innerHTML = '';
            return;
        }

        const logsHtml = data.logs.map(log => this.renderLog(log)).join('');
        logsList.innerHTML = `<div style="padding: 1.5rem;">${logsHtml}</div>`;

        // 渲染分页
        if (data.pagination) {
            this.renderPagination('logs-pagination', data.pagination, (page) => this.loadLogs(page));
        } else {
            document.getElementById('logs-pagination').innerHTML = '';
        }
    }

    renderLog(log) {
        const statusClass = log.status === 'success' ? 'success' : 'error';
        const statusIcon = log.status === 'success' ? '✅' : '❌';
        
        return `
            <div style="border: 1.5px solid var(--glass-border); border-radius: var(--radius-lg); padding: 1rem; margin-bottom: 1rem; background: var(--glass-bg); backdrop-filter: blur(25px) saturate(180%); -webkit-backdrop-filter: blur(25px) saturate(180%);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span>${statusIcon}</span>
                        <strong>${log.tool_name}</strong>
                    </div>
                    <span style="color: var(--text-color-secondary); font-size: 0.8rem;">
                        ${new Date(log.created_at).toLocaleString('zh-CN')}
                    </span>
                </div>
                <div style="color: var(--text-color-secondary); font-size: 0.9rem; margin-bottom: 0.5rem;">
                    服务器: ${log.server_name} | 执行时间: ${log.execution_time.toFixed(3)}s
                </div>
                ${log.error_message ? `
                    <div style="color: var(--error-color); font-size: 0.9rem; background: rgba(255, 59, 48, 0.1); padding: 0.5rem; border-radius: var(--radius-md); border: 1px solid rgba(255, 59, 48, 0.2);">
                        错误: ${log.error_message}
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderPagination(containerId, pagination, onPageChange) {
        const container = document.getElementById(containerId);
        if (!pagination || !pagination.pages || pagination.pages <= 1) {
            container.innerHTML = '';
            return;
        }

        let paginationHtml = '';
        
        // 上一页
        if (pagination.page > 1) {
            paginationHtml += `<button class="page-btn" onclick="mcpManager.loadMemories(${pagination.page - 1})">上一页</button>`;
        }

        // 页码
        const startPage = Math.max(1, pagination.page - 2);
        const endPage = Math.min(pagination.pages, pagination.page + 2);

        for (let i = startPage; i <= endPage; i++) {
            const activeClass = i === pagination.page ? 'active' : '';
            paginationHtml += `<button class="page-btn ${activeClass}" onclick="mcpManager.loadMemories(${i})">${i}</button>`;
        }

        // 下一页
        if (pagination.page < pagination.pages) {
            paginationHtml += `<button class="page-btn" onclick="mcpManager.loadMemories(${pagination.page + 1})">下一页</button>`;
        }

        container.innerHTML = paginationHtml;
    }

    searchMemories(query) {
        this.loadMemories(1, query);
    }

    getMemoryTypeLabel(type) {
        const labels = {
            'preference': '偏好',
            'habit': '习惯', 
            'fact': '事实',
            'emotion': '情感',
            'experience': '经历'
        };
        return labels[type] || type;
    }

    async toggleServer(serverId) {
        const data = await this.apiRequest(`/api/mcp/servers/${serverId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enabled: !server.enabled })
        });
        
        if (data) {
            this.showAlert('服务器状态更新成功', 'success');
            this.loadServers();
        }
    }

    async deleteServer(serverId) {
        if (!confirm('确定要删除这个服务器吗？')) {
            return;
        }

        const data = await this.apiRequest(`/api/mcp/servers/${serverId}`, {
            method: 'DELETE'
        });
        
        if (data) {
            this.showAlert('服务器删除成功', 'success');
            this.loadServers();
        }
    }

    async clearAllMemories() {
        if (!confirm('确定要清空所有记忆吗？此操作不可撤销！')) {
            return;
        }

        // 这里需要实现清空所有记忆的API
        this.showAlert('功能开发中', 'warning');
    }

    showAddServerModal() {
        document.getElementById('add-server-modal').classList.add('active');
    }

    hideAddServerModal() {
        document.getElementById('add-server-modal').classList.remove('active');
        document.getElementById('add-server-form').reset();
    }

    async addServer() {
        const form = document.getElementById('add-server-form');
        
        const serverData = {
            name: document.getElementById('server-name').value,
            command: document.getElementById('server-command').value,
            args: [],
            env: {},
            enabled: true
        };

        // 解析参数
        const argsText = document.getElementById('server-args').value.trim();
        if (argsText) {
            try {
                serverData.args = JSON.parse(argsText);
            } catch (e) {
                this.showAlert('参数格式错误，请使用有效的JSON数组', 'error');
                return;
            }
        }

        // 解析环境变量
        const envText = document.getElementById('server-env').value.trim();
        if (envText) {
            try {
                serverData.env = JSON.parse(envText);
            } catch (e) {
                this.showAlert('环境变量格式错误，请使用有效的JSON对象', 'error');
                return;
            }
        }

        const data = await this.apiRequest('/api/mcp/servers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(serverData)
        });

        if (data) {
            this.showAlert('服务器添加成功', 'success');
            this.hideAddServerModal();
            this.loadServers();
        }
    }

    showAlert(message, type = 'info') {
        const alertClass = type === 'success' ? 'alert-success' : 'alert-error';
        const alertHtml = `
            <div class="alert ${alertClass}" style="position: fixed; top: 2rem; right: 2rem; z-index: 2000; min-width: 300px;">
                ${message}
            </div>
        `;
        
        const alertElement = document.createElement('div');
        alertElement.innerHTML = alertHtml;
        document.body.appendChild(alertElement);
        
        setTimeout(() => {
            alertElement.remove();
        }, 3000);
    }

    showLoginPrompt() {
        this.showAlert('请先登录', 'error');
        setTimeout(() => {
            window.location.href = '/';
        }, 2000);
    }
}

// 全局函数，供HTML中的onclick调用
function showAddServerModal() {
    window.mcpManager.showAddServerModal();
}

function hideAddServerModal() {
    window.mcpManager.hideAddServerModal();
}

function addServer() {
    window.mcpManager.addServer();
}

function clearAllMemories() {
    window.mcpManager.clearAllMemories();
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    window.mcpManager = new MCPManager();
});