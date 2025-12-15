// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化侧边栏
    initSidebar();
    
    // 初始化导航菜单
    initNavigation();
    
    // 初始化表单验证
    initFormValidation();
    
    // 初始化日期选择器
    initDatePickers();
    
    // 初始化任务管理功能
    initTaskManagement();
    
    // 初始化语言切换
    initLanguageSwitcher();
});

// 初始化侧边栏
function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    
    if (sidebar && sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            
            // 更新图标方向
            const icon = this.querySelector('i');
            if (sidebar.classList.contains('collapsed')) {
                icon.classList.remove('fa-chevron-left');
                icon.classList.add('fa-chevron-right');
            } else {
                icon.classList.remove('fa-chevron-right');
                icon.classList.add('fa-chevron-left');
            }
        });
    }
    
    // 移动端菜单切换
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    if (mobileMenuToggle && sidebar) {
        mobileMenuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
    }
}

// 初始化导航菜单
function initNavigation() {
    // 移动端菜单切换
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', function() {
            navLinks.classList.toggle('show');
        });
    }
}

// 初始化表单验证
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        // 跳过任务表单，因为任务表单有专门的提交处理逻辑
        if (form.id === 'task-form') {
            console.log('跳过任务表单的通用验证');
            return;
        }
        
        form.addEventListener('submit', function(e) {
            // 基本表单验证
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                } else {
                    field.classList.remove('error');
                }
            });
            
            // 密码匹配验证
            const password = form.querySelector('input[name="password"]');
            const confirmPassword = form.querySelector('input[name="confirm_password"]');
            
            if (password && confirmPassword) {
                if (password.value !== confirmPassword.value) {
                    isValid = false;
                    password.classList.add('error');
                    confirmPassword.classList.add('error');
                    alert('两次输入的密码不一致');
                }
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });
        
        // 输入时移除错误状态
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                this.classList.remove('error');
            });
        });
    });
}

// 初始化日期选择器
function initDatePickers() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
//        // 设置最大日期为今天
//        const today = new Date().toISOString().split('T')[0];
//        input.max = today;
    });
}

// 初始化任务管理功能
function initTaskManagement() {
    // 任务状态切换
    const taskStatusToggles = document.querySelectorAll('.task-status-toggle');
    taskStatusToggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const taskId = this.dataset.taskId;
            const status = this.checked ? 'completed' : 'pending';
            updateTaskStatus(taskId, status);
        });
    });
    
    // 子任务状态切换
    const subtaskToggles = document.querySelectorAll('.subtask-toggle');
    subtaskToggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const subtaskId = this.dataset.subtaskId;
            const completed = this.checked ? 1 : 0;
            updateSubtaskStatus(subtaskId, completed);
        });
    });
}

// 更新任务状态
function updateTaskStatus(taskId, status) {
    // 这里可以添加AJAX请求来更新服务器上的任务状态
    console.log(`Updating task ${taskId} status to ${status}`);
}

// 更新子任务状态
function updateSubtaskStatus(subtaskId, completed) {
    // 这里可以添加AJAX请求来更新服务器上的子任务状态
    console.log(`Updating subtask ${subtaskId} completed status to ${completed}`);
}

// 初始化语言切换
function initLanguageSwitcher() {
    const languageSelect = document.querySelector('#language-select');
    if (languageSelect) {
        languageSelect.addEventListener('change', function() {
            const lang = this.value;
            // 获取当前URL，替换语言参数
            const url = new URL(window.location);
            url.searchParams.set('lang', lang);
            window.location.href = url.toString();
        });
    }
}

// 在文件末尾添加以下内容

// 显示通知功能
function showNotification(message) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(message);
    } else if ('Notification' in window && Notification.permission !== 'denied') {
        Notification.requestPermission().then(function(permission) {
            if (permission === 'granted') {
                new Notification(message);
            }
        });
    }
    
    // 显示网页内通知
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(function() {
        notification.remove();
    }, 3000);
}

// 导出到全局窗口对象，以便在其他脚本中使用
window.showNotification = showNotification;