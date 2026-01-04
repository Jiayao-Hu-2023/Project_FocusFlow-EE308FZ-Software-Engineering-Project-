class FocusTimer {
    constructor() {
        this.focusDuration = 25 * 60; // 默认25分钟（秒）
        this.remainingTime = this.focusDuration;
        this.isRunning = false;
        this.isFocusMode = true; // 专注模式
        this.timerInterval = null;
        this.keyListenerAdded = false;

        // 延迟初始化，确保DOM完全加载
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            setTimeout(() => this.init(), 100);
        }
    }

    init() {
        // 获取DOM元素 - 使用更可靠的选择器
        this.timerDisplay = document.getElementById('timerDisplay');
        this.startButton = document.getElementById('startBtn');
        this.pauseButton = document.getElementById('pauseBtn');
        this.resetButton = document.getElementById('resetBtn');
        this.skipButton = document.getElementById('skipBtn');

        console.log('Timer initialized with buttons:', {
            start: !!this.startButton,
            pause: !!this.pauseButton,
            reset: !!this.resetButton,
            skip: !!this.skipButton
        });

        // 确保按钮初始状态正确
        this.updateButtonState();

        // 绑定事件
        this.bindEvents();

        // 更新显示
        this.updateDisplay();
    }

    // 更新按钮状态
    updateButtonState() {
        if (this.startButton && this.pauseButton) {
            if (this.isRunning) {
                // 计时器运行中：显示Pause按钮，隐藏Start按钮
                this.startButton.style.display = 'none';
                this.pauseButton.style.display = 'inline-block';
            } else {
                // 计时器停止：显示Start按钮，隐藏Pause按钮
                this.startButton.style.display = 'inline-block';
                this.pauseButton.style.display = 'none';
            }
        }
    }

    bindEvents() {
        // 移除之前的事件监听器（如果存在）
        if (this.startButton) {
            this.startButton.removeEventListener('click', this.start.bind(this));
            this.startButton.addEventListener('click', () => this.start());
        }

        if (this.pauseButton) {
            this.pauseButton.removeEventListener('click', this.pause.bind(this));
            this.pauseButton.addEventListener('click', () => this.pause());
        }

        if (this.resetButton) {
            // 移除Reset按钮的直接事件绑定，让全局点击事件处理
            this.resetButton.removeEventListener('click', this.reset.bind(this));
            // 不添加任何事件监听，让全局的handleClick方法处理
        }

        // 删除skip按钮的事件绑定
        if (this.skipButton) {
            this.skipButton.style.display = 'none'; // 隐藏skip按钮
        }
    }

    start() {
        if (!this.isRunning) {
            this.isRunning = true;
            this.updateButtonState(); // 更新按钮状态

            this.timerInterval = setInterval(() => {
                if (this.isRunning) {
                    this.remainingTime--;
                    this.updateDisplay();

                    if (this.remainingTime <= 0) {
                        // 先停止计时器，再处理完成逻辑
                        this.pause();
                        this.handleTimerComplete();
                    }
                }
            }, 1000);
        }
    }

    pause() {
        if (this.isRunning) {
            this.isRunning = false;
            clearInterval(this.timerInterval);
            this.timerInterval = null; // 清除计时器引用
            this.updateButtonState(); // 更新按钮状态
            console.log('Timer paused');
        }
    }

    // 显示警告对话框（支持重置操作）
    showWarningDialog(onConfirmCallback) {
        const t = (window.TRANSLATIONS || {});
        const warningMessage = t.focus_mode_warning_message || "Are you sure to proceed? If so, the duration of your current study will not be included in the records.";

        if (confirm(warningMessage)) {
            // 用户确认继续，执行回调函数
            if (onConfirmCallback) {
                onConfirmCallback();
            } else {
                // 默认行为：暂停计时器
                this.pause();
            }
        }
    }

    // 显示自定义确认对话框
    showCustomConfirmDialog(title, message, onConfirm) {
        // 创建模态框HTML
        const modalId = 'custom-confirm-dialog';
        let modal = document.getElementById(modalId);

        // 如果模态框已存在，先移除
        if (modal) {
            modal.remove();
        }

        // 创建新的模态框
        modal = document.createElement('div');
        modal.id = modalId;
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-overlay"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h2>${title}</h2>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <p>${message}</p>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" id="cancel-btn">${window.TRANSLATIONS?.cancel || 'Cancel'}</button>
                    <button class="btn btn-primary" id="confirm-btn">${window.TRANSLATIONS?.confirm || 'Confirm'}</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // 显示模态框
        modal.style.display = 'block';

        // 保存当前的事件监听器引用
        const originalKeyHandler = this.handleKeyPress;
        const originalClickHandler = this.handleClick;

        // 暂时移除全局事件监听器，避免对话框内的按键触发警告
        document.removeEventListener('keydown', this.handleKeyPress);
        document.removeEventListener('click', this.handleClick);

        // 添加事件监听器
        const closeModal = () => {
            modal.style.display = 'none';
            document.body.removeChild(modal);
            
            // 恢复全局事件监听器
            document.addEventListener('keydown', this.handleKeyPress);
            document.addEventListener('click', this.handleClick);
        };

        // 关闭按钮
        modal.querySelector('.close-btn').addEventListener('click', closeModal);

        // 取消按钮
        modal.querySelector('#cancel-btn').addEventListener('click', closeModal);

        // 确认按钮
        modal.querySelector('#confirm-btn').addEventListener('click', () => {
            closeModal();
            if (onConfirm) {
                onConfirm();
            }
        });

        // 点击遮罩层关闭
        modal.querySelector('.modal-overlay').addEventListener('click', closeModal);

        // ESC键关闭
        const handleEscKey = (event) => {
            if (event.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', handleEscKey);
            }
        };
        document.addEventListener('keydown', handleEscKey);
    }

    // 设置自定义时长（只设置专注时间）
    setDuration(focusMinutes) {
        this.focusDuration = focusMinutes * 60;
        this.reset();
    }

    // 显示警告对话框
    showWarningDialog() {
        const t = (window.TRANSLATIONS || {});
        const warningMessage = t.focus_mode_warning_message || "Are you sure to proceed? If so, the duration of your current study will not be included in the records.";

        if (confirm(warningMessage)) {
            // 用户确认继续，暂停计时器
            this.pause();
        }
    }

    // 显示自定义确认对话框
    showCustomConfirmDialog(title, message, onConfirm) {
        // 创建模态框HTML
        const modalId = 'custom-confirm-dialog';
        let modal = document.getElementById(modalId);

        // 如果模态框已存在，先移除
        if (modal) {
            modal.remove();
        }

        // 创建新的模态框
        modal = document.createElement('div');
        modal.id = modalId;
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-overlay"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h2>${title}</h2>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <p>${message}</p>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" id="cancel-btn">${window.TRANSLATIONS?.cancel || 'Cancel'}</button>
                    <button class="btn btn-primary" id="confirm-btn">${window.TRANSLATIONS?.confirm || 'Confirm'}</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // 显示模态框
        modal.style.display = 'block';

        // 添加事件监听器
        const closeModal = () => {
            modal.style.display = 'none';
            document.body.removeChild(modal);
        };

        // 关闭按钮
        modal.querySelector('.close-btn').addEventListener('click', closeModal);

        // 取消按钮
        modal.querySelector('#cancel-btn').addEventListener('click', closeModal);

        // 确认按钮
        modal.querySelector('#confirm-btn').addEventListener('click', () => {
            closeModal();
            if (onConfirm) {
                onConfirm();
            }
        });

        // 点击遮罩层关闭
        modal.querySelector('.modal-overlay').addEventListener('click', closeModal);

        // ESC键关闭
        const handleEscKey = (event) => {
            if (event.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', handleEscKey);
            }
        };
        document.addEventListener('keydown', handleEscKey);
    }

    reset() {
        // 直接重置，不需要额外的确认对话框
        this.pause();
        this.remainingTime = this.focusDuration; // 始终重置为专注时间
        this.updateDisplay();
        this.updateButtonState(); // 更新按钮状态
        console.log('Timer reset by user');
    }

    // 删除skip方法
    updateDisplay() {
        const minutes = Math.floor(this.remainingTime / 60);
        const seconds = this.remainingTime % 60;
        const displayText = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

        if (this.timerDisplay) {
            this.timerDisplay.textContent = displayText;
        }

        // 更新页面标题，只显示专注模式
        const t = (window.TRANSLATIONS || {});
        const focusLabel = t.focus_in_progress || 'Focusing';
        document.title = `${displayText} - ${focusLabel}`;
    }

    handleTimerComplete() {
        // 立即显示专注完成通知（在倒计时一结束就推送）
        const t = (window.TRANSLATIONS || {});
        const msg = t.focus_over_take_break || 'Focus time is over — Take a break now!';

        // 检查showNotification函数是否存在
        if (typeof showNotification === 'function') {
            showNotification(msg);
        } else {
            // 如果showNotification不存在，使用简单的alert作为回退
            console.log('专注完成通知:', msg);
            // 或者使用浏览器通知API
            if ('Notification' in window && Notification.permission === 'granted') {
                new Notification(msg);
            } else if ('Notification' in window && Notification.permission !== 'denied') {
                Notification.requestPermission().then(function(permission) {
                    if (permission === 'granted') {
                        new Notification(msg);
                    }
                });
            }
        }

        // 先停止计时器
        this.pause();

        // 播放提示音
        this.playNotificationSound();

        // 保存专注会话到数据库
        this.saveFocusSession();

        // 确保按钮状态正确更新
        this.updateButtonState();

        // 移除全局监听
        document.removeEventListener('keydown', this.handleKeyPress);
        document.removeEventListener('click', this.handleClick);

        // 自动退出全屏（如果支持）
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }

        // 倒计时结束后延迟1 s自动刷新界面（给用户足够时间看到通知）
        setTimeout(() => {
            console.log('专注会话结束，自动刷新界面...');
            window.location.reload();
        }, 1000);
    }

    // 播放提示音
    playNotificationSound() {
        // 简单的提示音实现
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            oscillator.frequency.value = 800;
            oscillator.type = 'sine';

            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (error) {
            console.log('无法播放提示音:', error);
        }
    }

    // 保存专注会话到数据库
    saveFocusSession() {
        // 计算实际专注时长（预设时长 - 剩余时间）
        const actualDuration = (this.focusDuration - this.remainingTime) / 60; // 转换为分钟
        const taskId = document.getElementById('task-select') ? document.getElementById('task-select').value : null;

        // 确保时长至少为1分钟
        const duration = Math.max(1, Math.round(actualDuration));

        console.log(`保存专注会话: 时长 ${duration} 分钟, 任务ID: ${taskId}`);

        fetch('/focus/save_session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                duration: duration,
                task_id: taskId
            })
        }).then(response => {
            if (response.ok) {
                console.log('专注会话保存成功，时长:', duration, '分钟');
                // 更新专注统计
                this.updateFocusStats();
            } else {
                console.error('保存专注会话失败');
                response.json().then(data => {
                    console.error('错误信息:', data.message);
                });
            }
        }).catch(error => {
            console.error('保存专注会话时出错:', error);
        });
    }

    // 更新专注统计
    updateFocusStats() {
        fetch('/focus/stats')
            .then(response => response.json())
            .then(data => {
                console.log('更新专注统计:', data);
                // 更新页面上的统计信息
                const statItems = document.querySelectorAll('.stat-item .stat-value');
                if (statItems.length >= 3) {
                    const t = (window.TRANSLATIONS || {});
                    statItems[0].textContent = data.completed_sessions;
                    statItems[1].textContent = `${data.today_duration} ${t.min || 'min'}`;
                    statItems[2].textContent = data.completion_rate + '%';
                }
            })
            .catch(error => {
                console.error('获取专注统计时出错:', error);
            });
    }

    // 处理按键事件
    handleKeyPress(event) {
        // 允许的功能键：空格（暂停/继续）、ESC（退出全屏）、F11（全屏）
        const allowedKeys = [' ', 'Escape', 'F11'];

        if (!allowedKeys.includes(event.key) && !event.ctrlKey && !event.metaKey) {
            event.preventDefault();
            this.showWarningDialog();
        }
    }

    // 处理点击事件
    handleClick(event) {
        // 检查是否点击了允许的元素
        const allowedElements = [
            'startBtn', 'pauseBtn', 'setCustomTime',
            'customMinutes', 'subject-select'
        ];

        // 检查是否是预设时间按钮
        const isPresetBtn = event.target.classList.contains('preset-btn') &&
                           event.target.id !== 'setCustomTime';

        // 如果点击的是Reset按钮，显示警告并执行重置
        if (event.target.id === 'resetBtn' || event.target.parentElement?.id === 'resetBtn') {
            event.preventDefault();
            event.stopPropagation(); // 阻止事件冒泡，避免重复处理
            this.showWarningDialog(() => {
                this.reset();
            });
            return;
        }

        // 如果点击的不是允许的元素，显示警告
        if (!allowedElements.includes(event.target.id) &&
            !allowedElements.includes(event.target.parentElement?.id) &&
            !isPresetBtn) {
            event.preventDefault();
            this.showWarningDialog();
        }
    }

    // 设置自定义时长（只设置专注时间）
    setDuration(focusMinutes) {
        this.focusDuration = focusMinutes * 60;
        this.reset();
    }
}

// 页面加载完成后初始化计时器
document.addEventListener('DOMContentLoaded', function() {
    // 确保只创建一个计时器实例
    if (!window.focusTimer) {
        window.focusTimer = new FocusTimer();
    }

    // 初始化全屏功能
    const fullscreenButton = document.querySelector('.fullscreen-btn');
    if (fullscreenButton) {
        fullscreenButton.addEventListener('click', function() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(err => {
                    console.log(`Fullscreen request error: ${err.message}`);
                });
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                }
            }
        });
    }

    // 自定义时长设置（只设置专注时间）
    const focusDurationInput = document.querySelector('#focus-duration');
    const applyDurationButton = document.querySelector('#apply-duration');

    if (focusDurationInput && applyDurationButton) {
        applyDurationButton.addEventListener('click', function() {
            const focusMinutes = parseInt(focusDurationInput.value);

            if (focusMinutes > 0) {
                window.focusTimer.setDuration(focusMinutes);
            }
        });
    }

    // 隐藏休息时长输入框
    const breakDurationInput = document.querySelector('#break-duration');
    const breakDurationLabel = document.querySelector('label[for="break-duration"]');
    if (breakDurationInput) {
        breakDurationInput.style.display = 'none';
    }
    if (breakDurationLabel) {
        breakDurationLabel.style.display = 'none';
    }
});