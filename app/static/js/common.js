// 22306订票系统 - 通用JavaScript函数

// API基础URL
const API_BASE = '/api';

// 显示消息提示
function showMessage(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '80px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    alertDiv.style.animation = 'slideIn 0.3s';
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.style.animation = 'slideOut 0.3s';
        setTimeout(() => {
            document.body.removeChild(alertDiv);
        }, 300);
    }, 3000);
}

// 添加动画样式
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// AJAX请求封装
async function apiRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include'  // 包含cookie
    };
    
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('API请求失败:', error);
        return { success: false, message: '网络请求失败' };
    }
}

// 检查登录状态
async function checkLoginStatus() {
    const result = await apiRequest(`${API_BASE}/auth/check_session`);
    return result.logged_in;
}

// 获取当前用户信息
async function getCurrentUser() {
    const result = await apiRequest(`${API_BASE}/auth/check_session`);
    if (result.logged_in) {
        return result.user;
    }
    return null;
}

// 退出登录
async function logout() {
    const result = await apiRequest(`${API_BASE}/auth/logout`, 'POST');
    if (result.success) {
        showMessage('退出成功', 'success');
        setTimeout(() => {
            window.location.href = '/';
        }, 1000);
    }
}

// 格式化日期
function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN');
}

// 格式化时间
function formatTime(timeStr) {
    if (!timeStr) return '';
    return timeStr.substring(0, 5);  // HH:MM
}

// 格式化日期时间
function formatDateTime(datetimeStr) {
    if (!datetimeStr) return '';
    const date = new Date(datetimeStr);
    return date.toLocaleString('zh-CN');
}

// 状态徽章映射
const STATUS_BADGES = {
    'normal': { text: '正常', class: 'badge-success' },
    'delayed': { text: '延误', class: 'badge-warning' },
    'cancelled': { text: '取消', class: 'badge-danger' },
    'confirmed': { text: '已确认', class: 'badge-success' },
    'pending': { text: '待确认', class: 'badge-warning' },
    'refunded': { text: '已退票', class: 'badge-secondary' },
    'valid': { text: '有效', class: 'badge-success' },
    'individual': { text: '个人', class: 'badge-info' },
    'group': { text: '团体', class: 'badge-warning' }
};

// 获取状态徽章HTML
function getStatusBadge(status) {
    const badge = STATUS_BADGES[status] || { text: status, class: 'badge-secondary' };
    return `<span class="badge ${badge.class}">${badge.text}</span>`;
}

// 初始化导航栏
async function initNavbar() {
    const user = await getCurrentUser();
    const userInfoDiv = document.getElementById('user-info');
    
    // 如果页面没有user-info元素，直接返回
    if (!userInfoDiv) {
        return;
    }
    
    if (user) {
        userInfoDiv.innerHTML = `
            <span>欢迎，${user.username}</span>
            <button class="btn-logout" onclick="logout()">退出</button>
        `;
        
        // 如果是管理员，显示管理员菜单
        if (user.is_admin) {
            const adminLink = document.querySelector('a[href="/admin"]');
            if (adminLink) {
                adminLink.style.display = 'inline-block';
            }
        }
    } else {
        userInfoDiv.innerHTML = `
            <a href="/login" class="btn-logout">登录</a>
            <a href="/register" class="btn-logout">注册</a>
        `;
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
});

// 验证身份证号
function validateIdCard(idCard) {
    const pattern = /^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/;
    return pattern.test(idCard);
}

// 验证表单
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const inputs = form.querySelectorAll('input[required], select[required]');
    for (let input of inputs) {
        if (!input.value.trim()) {
            showMessage('请填写所有必填项', 'warning');
            input.focus();
            return false;
        }
    }
    return true;
}

// 导出函数
window.showMessage = showMessage;
window.apiRequest = apiRequest;
window.checkLoginStatus = checkLoginStatus;
window.getCurrentUser = getCurrentUser;
window.logout = logout;
window.formatDate = formatDate;
window.formatTime = formatTime;
window.formatDateTime = formatDateTime;
window.getStatusBadge = getStatusBadge;
window.validateIdCard = validateIdCard;
window.validateForm = validateForm;
window.API_BASE = API_BASE;

