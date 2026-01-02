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
                    const t = (window.TRANSLATIONS || {});
                    alert(t.passwords_do_not_match || 'Passwords do not match');
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
    
    // 编辑任务按钮
    const editButtons = document.querySelectorAll('.edit-btn-modern');
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const taskId = this.dataset.taskId;
            editTask(taskId);
        });
    });
    
    // 删除任务按钮
    const deleteButtons = document.querySelectorAll('.delete-btn-modern');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const taskId = this.dataset.taskId;
            deleteTask(taskId);
        });
    });
}

// 编辑任务
function editTask(taskId) {
    console.log(`Editing task ${taskId}`);
    
    // 获取任务数据
    const taskCard = document.querySelector(`.task-card-modern[data-task-id="${taskId}"]`);
    if (!taskCard) {
        console.error('Task card not found');
        return;
    }
    
    // 获取任务数据
    const taskTitle = taskCard.querySelector('.task-title-modern').textContent.trim();
    const taskSubject = taskCard.querySelector('.task-subject-modern')?.textContent.trim() || '';
    const taskDueDate = taskCard.querySelector('.due-date-text')?.textContent.trim() || '';
    const taskPriority = taskCard.dataset.priority || 'medium';
    const taskStatus = taskCard.dataset.status || 'pending';
    
    // 填充模态框表单
    const modal = document.getElementById('task-modal');
    const modalTitle = document.getElementById('modal-title');
    const taskForm = document.getElementById('task-form');
    
    if (modal && modalTitle && taskForm) {
        // 设置模态框标题
        modalTitle.textContent = 'Edit Task';
        
        // 填充表单数据
        document.getElementById('task-id').value = taskId;
        document.getElementById('task-title').value = taskTitle;
        document.getElementById('task-course').value = taskSubject;
        document.getElementById('task-priority').value = taskPriority;
        document.getElementById('task-status').value = taskStatus;
        
        // 处理日期格式
        let formattedDueDate = '';
        if (taskDueDate === 'Today') {
            formattedDueDate = new Date().toISOString().split('T')[0];
        } else if (taskDueDate === 'Tomorrow') {
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            formattedDueDate = tomorrow.toISOString().split('T')[0];
        } else if (taskDueDate.includes('days')) {
            const days = parseInt(taskDueDate);
            const futureDate = new Date();
            futureDate.setDate(futureDate.getDate() + days);
            formattedDueDate = futureDate.toISOString().split('T')[0];
        } else {
            // 尝试解析标准日期格式
            try {
                const date = new Date(taskDueDate);
                if (!isNaN(date.getTime())) {
                    formattedDueDate = date.toISOString().split('T')[0];
                }
            } catch (e) {
                console.error('Date parsing error:', e);
            }
        }
        
        document.getElementById('task-due-date').value = formattedDueDate;
        
        // 显示模态框
        modal.style.display = 'block';
    }
}

// 删除任务
function deleteTask(taskId) {
    const t = (window.TRANSLATIONS || {});
    if (confirm(t.confirm_delete_task || 'Are you sure you want to delete this task?')) {
        // 发送删除请求
        fetch(`/tasks/delete/${taskId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            if (response.ok) {
                // 从DOM中移除任务卡片
                const taskCard = document.querySelector(`.task-card-modern[data-task-id="${taskId}"]`);
                if (taskCard) {
                    taskCard.remove();
                    // 更新任务计数
                    updateTaskCounts();
                }
                showNotification(t.task_deleted_success || 'Task deleted successfully!');
            } else {
                showNotification(t.task_delete_failed || 'Failed to delete task. Please try again.');
            }
        })
        .catch(error => {
            console.error('Delete task error:', error);
            showNotification(t.task_delete_failed || 'Error deleting task. Please try again.');
        });
    }
}

// 更新任务计数
function updateTaskCounts() {
    const taskCards = document.querySelectorAll('.task-card-modern');
    const totalTasks = taskCards.length;
    const activeTasks = Array.from(taskCards).filter(card => card.dataset.status !== 'completed').length;
    const completedTasks = Array.from(taskCards).filter(card => card.dataset.status === 'completed').length;
    
    const totalCountElement = document.getElementById('total-tasks-count');
    const activeCountElement = document.getElementById('active-tasks-count');
    const completedCountElement = document.getElementById('completed-tasks-count');
    
    if (totalCountElement) totalCountElement.textContent = totalTasks;
    if (activeCountElement) activeCountElement.textContent = activeTasks;
    if (completedCountElement) completedCountElement.textContent = completedTasks;
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
