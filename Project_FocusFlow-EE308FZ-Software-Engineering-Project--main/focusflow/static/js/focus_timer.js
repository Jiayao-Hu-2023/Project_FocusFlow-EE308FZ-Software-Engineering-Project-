class FocusTimer {
    constructor() {
        this.focusDuration = 45 * 60; // 默认45分钟（秒）
        this.breakDuration = 15 * 60; // 默认15分钟（秒）
        this.remainingTime = this.focusDuration;
        this.isRunning = false;
        this.isFocusMode = true;
        this.timerInterval = null;
        
        this.init();
    }
    
    init() {
        // 获取DOM元素
        this.timerDisplay = document.querySelector('.focus-timer');
        this.startButton = document.querySelector('.start-btn');
        this.pauseButton = document.querySelector('.pause-btn');
        this.resetButton = document.querySelector('.reset-btn');
        this.skipButton = document.querySelector('.skip-btn');
        
        // 绑定事件
        if (this.startButton) {
            this.startButton.addEventListener('click', () => this.start());
        }
        
        if (this.pauseButton) {
            this.pauseButton.addEventListener('click', () => this.pause());
        }
        
        if (this.resetButton) {
            this.resetButton.addEventListener('click', () => this.reset());
        }
        
        if (this.skipButton) {
            this.skipButton.addEventListener('click', () => this.skip());
        }
        
        // 更新显示
        this.updateDisplay();
    }
    
    start() {
        if (!this.isRunning) {
            this.isRunning = true;
            this.timerInterval = setInterval(() => {
                this.remainingTime--;
                this.updateDisplay();
                
                if (this.remainingTime <= 0) {
                    this.handleTimerComplete();
                }
            }, 1000);
        }
    }
    
    pause() {
        if (this.isRunning) {
            this.isRunning = false;
            clearInterval(this.timerInterval);
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
    
    playNotificationSound() {
        // 创建音频元素并播放
        const audio = new Audio('/static/sounds/notification.mp3');
        audio.play().catch(error => {
            console.log('无法播放提示音:', error);
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
    const focusTimer = new FocusTimer();
    
    // 存储在全局，以便其他脚本可以访问
    window.focusTimer = focusTimer;
    
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
                focusTimer.setDuration(focusMinutes, breakMinutes);
            }
        });
    }
});