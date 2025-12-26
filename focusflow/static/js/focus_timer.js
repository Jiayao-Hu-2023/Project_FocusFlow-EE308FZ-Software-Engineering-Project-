class FocusTimer {
    constructor() {
        this.focusDuration = 25 * 60; // 默认25分钟（秒）
        this.breakDuration = 5 * 60; // 默认5分钟（秒）
        this.remainingTime = this.focusDuration;
        this.isRunning = false;
        this.isFocusMode = true;
        this.timerInterval = null;
        
        this.init();
    }
    
    init() {
        // 获取DOM元素
        this.timerDisplay = document.getElementById('timerDisplay');
        this.startButton = document.getElementById('startBtn');
        this.pauseButton = document.getElementById('pauseBtn');
        this.resetButton = document.getElementById('resetBtn');
        this.skipButton = document.getElementById('skipBtn');
        
        // 绑定事件 - 确保只绑定一次
        this.bindEvents();
        
        // 更新显示
        this.updateDisplay();
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
        
        // 移除Reset按钮的事件绑定，让focus.html中的事件处理生效
        // if (this.resetButton) {
        //     this.resetButton.removeEventListener('click', this.reset.bind(this));
        //     this.resetButton.addEventListener('click', () => this.reset());
        // }
        
        if (this.skipButton) {
            this.skipButton.removeEventListener('click', this.skip.bind(this));
            this.skipButton.addEventListener('click', () => this.skip());
        }
    }
    
    start() {
        if (!this.isRunning) {
            this.isRunning = true;
            this.timerInterval = setInterval(() => {
                if (this.isRunning) { // 添加检查，确保只在运行状态下更新
                    this.remainingTime--;
                    this.updateDisplay();
                    
                    if (this.remainingTime <= 0) {
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
            console.log('Timer paused');
        }
    }
    
    reset() {
        this.pause();
        this.remainingTime = this.isFocusMode ? this.focusDuration : this.breakDuration;
        this.updateDisplay();
    }
    
    skip() {
        this.pause();
        this.isFocusMode = !this.isFocusMode;
        this.remainingTime = this.isFocusMode ? this.focusDuration : this.breakDuration;
        this.updateDisplay();
    }
    
    updateDisplay() {
        const minutes = Math.floor(this.remainingTime / 60);
        const seconds = this.remainingTime % 60;
        const displayText = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        if (this.timerDisplay) {
            this.timerDisplay.textContent = displayText;
        }

        // 更新页面标题，以便用户在其他标签页也能看到倒计时
        document.title = `${displayText} - ${this.isFocusMode ? '专注中' : '休息中'}`;
    }

    
    handleTimerComplete() {
        this.pause();
        
        // 播放提示音
        this.playNotificationSound();
        
        // 保存专注会话到数据库（只在专注模式完成时保存）
        if (this.isFocusMode) {
            this.saveFocusSession();
        }
        
        // 自动切换到下一个模式
        this.isFocusMode = !this.isFocusMode;
        this.remainingTime = this.isFocusMode ? this.focusDuration : this.breakDuration;
        this.updateDisplay();
        
        // 自动退出全屏（如果支持）
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
        
        // 显示通知
        showNotification(this.isFocusMode ? '休息时间结束，开始专注！' : '专注时间结束，该休息了！');
    }

        // 添加全局按键监听
    addKeyListener() {
        if (!this.keyListenerAdded) {
            this.keyListenerAdded = true;
            document.addEventListener('keydown', this.handleKeyPress.bind(this));
        }
    }

    // 移除全局按键监听
    removeKeyListener() {
        if (this.keyListenerAdded) {
            this.keyListenerAdded = false;
            document.removeEventListener('keydown', this.handleKeyPress.bind(this));
        }
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

    // 显示警告对话框
    showWarningDialog() {
        const warningMessage = "Are you sure to proceed? If so, the duration of your current study will not be included in the records.";

        if (confirm(warningMessage)) {
            // 用户确认继续，暂停计时器
            this.pause();
        }
    }
    
    // 保存专注会话到数据库
    saveFocusSession() {
        const duration = this.focusDuration / 60; // 转换为分钟
        const taskId = document.getElementById('task-select') ? document.getElementById('task-select').value : null;
        
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
                console.log('专注会话保存成功');
                // 更新专注统计
                this.updateFocusStats();
            } else {
                console.error('专注会话保存失败');
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
                // 更新页面上的统计信息
                const statItems = document.querySelectorAll('.stat-item .stat-value');
                if (statItems.length >= 3) {
                    statItems[0].textContent = data.completed_sessions + '个';
                    statItems[1].textContent = data.today_duration + '分钟';
                    statItems[2].textContent = data.completion_rate + '%';
                }
            })
            .catch(error => {
                console.error('获取专注统计时出错:', error);
            });
    }
    
    // 设置自定义时长
    setDuration(focusMinutes, breakMinutes) {
        this.focusDuration = focusMinutes * 60;
        this.breakDuration = breakMinutes * 60;
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
                    console.log(`全屏请求错误: ${err.message}`);
                });
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                }
            }
        });
    }
    
    // 自定义时长设置
    const focusDurationInput = document.querySelector('#focus-duration');
    const breakDurationInput = document.querySelector('#break-duration');
    const applyDurationButton = document.querySelector('#apply-duration');
    
    if (focusDurationInput && breakDurationInput && applyDurationButton) {
        applyDurationButton.addEventListener('click', function() {
            const focusMinutes = parseInt(focusDurationInput.value);
            const breakMinutes = parseInt(breakDurationInput.value);
            
            if (focusMinutes > 0 && breakMinutes > 0) {
                window.focusTimer.setDuration(focusMinutes, breakMinutes);
            }
        });
    }
});