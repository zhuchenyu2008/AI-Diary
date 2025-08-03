// AI日记 - 现代React应用
const { useState, useEffect, useRef } = React;

// 添加新图标组件
const Edit = ({ className = '', ...props }) => (
  React.createElement('svg', { className, ...iconProps, ...props },
    React.createElement('path', { d: 'm11.498 12.5.032-.024 1.464 1.464L16 10.936l.037.037.465-.465c.59-.59.59-1.546 0-2.136L14.965 6.83a1.513 1.513 0 0 0-2.136 0l-.465.465L12 7.658v.002l.465.465L11 9.59l1.465 1.464-.967.966-.033-.024M13.8 7.9a.3.3 0 0 1 .425 0l1.541 1.542a.3.3 0 0 1 0 .425l-.465.464L13.335 8.4l.465-.5z' }),
    React.createElement('path', { d: 'm8.12 12.847-.025-.026-1.465-1.465-.964.964.025.026 1.464 1.465.965-.964z' }),
    React.createElement('path', { d: 'M6.75 12h4.95l1.4-1.4-1.6-1.6H7.75a1 1 0 0 0-1 1v1a1 1 0 0 0 1 1h4.11l-1.11 1.11-1.11-1.11H6.75z' })
  )
);

const Trash2 = ({ className = '', ...props }) => (
  React.createElement('svg', { className, ...iconProps, ...props },
    React.createElement('path', { d: 'M3 6h18' }),
    React.createElement('path', { d: 'M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6' }),
    React.createElement('path', { d: 'M8 6V4c0-1 1-2 2-2h4c0 1 1 2 1 2v2' }),
    React.createElement('line', { x1: '10', x2: '10', y1: '11', y2: '17' }),
    React.createElement('line', { x1: '14', x2: '14', y1: '11', y2: '17' })
  )
);

const Filter = ({ className = '', ...props }) => (
  React.createElement('svg', { className, ...iconProps, ...props },
    React.createElement('polygon', { points: '22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3' })
  )
);

const Search = ({ className = '', ...props }) => (
  React.createElement('svg', { className, ...iconProps, ...props },
    React.createElement('circle', { cx: '11', cy: '11', r: '8' }),
    React.createElement('path', { d: 'm21 21-4.35-4.35' })
  )
);

const Heart = ({ className = '', ...props }) => (
  React.createElement('svg', { className, ...iconProps, ...props },
    React.createElement('path', { d: 'M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z' })
  )
);

const Upload = ({ className = '', ...props }) => (
  React.createElement('svg', { className, ...iconProps, ...props },
    React.createElement('path', { d: 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4' }),
    React.createElement('polyline', { points: '7 10 12 15 17 10' }),
    React.createElement('line', { x1: '12', x2: '12', y1: '15', y2: '3' })
  )
);

// 图标组件
const iconProps = {
  width: 24,
  height: 24,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round"
};

const BookOpen = ({ className = '', ...props }) => (
  React.createElement('svg', { className, ...iconProps, ...props }, 
    React.createElement('path', { d: "M12 7v14" }),
    React.createElement('path', { d: "M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z" })
  )
);

const Calendar = ({ className = '', ...props }) => (
  React.createElement('svg', { className, ...iconProps, ...props },
    React.createElement('path', { d: "M8 2v4" }),
    React.createElement('path', { d: "M16 2v4" }),
    React.createElement('rect', { width: "18", height: "18", x: "3", y: "4", rx: "2" }),
    React.createElement('path', { d: "M3 10h18" })
  )
);

const Camera = ({ className = '', ...props }) => (
  React.createElement('svg', { className, ...iconProps, ...props },
    React.createElement('path', { d: "M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z" }),
    React.createElement('circle', { cx: "12", cy: "13", r: "3" })
  )
);

const Clock = ({ className = '', ...props }) => (
  React.createElement('svg', { className, ...iconProps, ...props },
    React.createElement('circle', { cx: "12", cy: "12", r: "10" }),
    React.createElement('polyline', { points: "12 6 12 12 16 14" })
  )
);

// 编辑日记表单组件
const EditEntryForm = ({ entry, onSave, onCancel }) => {
  const [editText, setEditText] = useState(entry.text_content || '');
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    if (!editText.trim()) return;
    
    setIsSaving(true);
    await onSave(entry.id, editText);
    setIsSaving(false);
  };

  return React.createElement('div', {
    className: 'border border-blue-200 rounded-lg p-4 bg-blue-50'
  }, [
    React.createElement('textarea', {
      key: 'edit-textarea',
      value: editText,
      onChange: (e) => setEditText(e.target.value),
      className: 'w-full min-h-24 p-3 border border-blue-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white',
      style: { fontSize: '16px' }
    }),
    React.createElement('div', {
      key: 'edit-buttons',
      className: 'flex items-center gap-2 mt-3'
    }, [
      React.createElement(Button, {
        key: 'save',
        onClick: handleSave,
        disabled: !editText.trim() || isSaving,
        size: 'sm',
        className: 'bg-blue-600 hover:bg-blue-700'
      }, isSaving ? '保存中...' : '保存'),
      React.createElement(Button, {
        key: 'cancel',
        onClick: onCancel,
        variant: 'outline',
        size: 'sm'
      }, '取消')
    ])
  ]);
};
const Button = ({ 
  className = '', 
  variant = 'default', 
  size = 'default', 
  disabled = false,
  children, 
  ...props 
}) => {
  const baseClasses = 'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 outline-none focus-visible:ring-2 focus-visible:ring-blue-500';
  
  const variantClasses = {
    default: 'bg-blue-600 text-white shadow-sm hover:bg-blue-700',
    destructive: 'bg-red-600 text-white shadow-sm hover:bg-red-700',
    outline: 'border border-gray-300 bg-white shadow-sm hover:bg-gray-50 hover:text-gray-900',
    secondary: 'bg-gray-100 text-gray-900 shadow-sm hover:bg-gray-200',
    ghost: 'hover:bg-gray-100 hover:text-gray-900',
    link: 'text-blue-600 underline-offset-4 hover:underline'
  };
  
  const sizeClasses = {
    default: 'h-9 px-4 py-2',
    sm: 'h-8 rounded-md px-3',
    lg: 'h-10 rounded-md px-6',
    icon: 'h-9 w-9'
  };
  
  const classes = [
    baseClasses,
    variantClasses[variant] || variantClasses.default,
    sizeClasses[size] || sizeClasses.default,
    className
  ].filter(Boolean).join(' ');
  
  return React.createElement('button', { 
    className: classes,
    disabled: disabled,
    ...props
  }, children);
};

// Tabs组件
const Tabs = ({ className = '', children, value, onValueChange, ...props }) => {
  return React.createElement('div', {
    className: `flex flex-col gap-2 ${className}`
  }, Array.isArray(children) 
    ? children.map((child, index) => 
        React.isValidElement(child) 
          ? React.cloneElement(child, { key: child.key || index, currentValue: value, onValueChange })
          : child
      )
    : React.Children.map(children, child => 
        React.isValidElement(child) 
          ? React.cloneElement(child, { currentValue: value, onValueChange })
          : child
      )
  );
};

const TabsList = ({ className = '', children, currentValue, onValueChange, ...props }) => {
  return React.createElement('div', {
    className: `bg-gray-100 text-gray-600 inline-flex h-9 w-fit items-center justify-center rounded-lg p-1 ${className}`,
    role: 'tablist'
  }, React.Children.map(children, child => 
    React.isValidElement(child) 
      ? React.cloneElement(child, { currentValue, onValueChange })
      : child
  ));
};

const TabsTrigger = ({ className = '', children, value: triggerValue, onClick, currentValue, onValueChange, ...props }) => {
  const isActive = currentValue === triggerValue;
  
  return React.createElement('button', {
    className: `inline-flex h-7 flex-1 items-center justify-center gap-1.5 rounded-md border border-transparent px-3 py-1 text-sm font-medium whitespace-nowrap transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 disabled:pointer-events-none disabled:opacity-50 ${
      isActive 
        ? 'bg-white text-gray-900 shadow-sm' 
        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
    } ${className}`,
    role: 'tab',
    'data-state': isActive ? 'active' : 'inactive',
    onClick: () => {
      onValueChange && onValueChange(triggerValue);
      onClick && onClick();
    }
  }, children);
};

const TabsContent = ({ className = '', children, value: contentValue, currentValue, ...props }) => {
  const isActive = currentValue === contentValue;
  
  if (!isActive) return null;
  
  return React.createElement('div', {
    className: `flex-1 outline-none ${className}`,
    role: 'tabpanel'
  }, children);
};

// 主应用组件
function App() {
  const [entries, setEntries] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [activeTab, setActiveTab] = useState('timeline');
  const [loading, setLoading] = useState(true);
  const [newEntryText, setNewEntryText] = useState('');
  const [selectedDate, setSelectedDate] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterMood, setFilterMood] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [editingEntry, setEditingEntry] = useState(null);
  const [selectedHistoryDate, setSelectedHistoryDate] = useState(null); // 选中的历史日期
  const [expandedDays, setExpandedDays] = useState(new Set()); // 展开的日期
  const [countdown, setCountdown] = useState({ hours: 0, minutes: 0, seconds: 0 }); // 倒计时
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false); // 生成总结状态
  const [showMoodInHistory, setShowMoodInHistory] = useState(true); // 历史日记中是否显示情绪标签
  const [showFilters, setShowFilters] = useState(false);
  const textareaRef = useRef(null);

  // 获取当前用户信息
  useEffect(() => {
    fetchUserInfo();
  }, []);

  // 获取日记条目
  useEffect(() => {
    if (currentUser) {
      fetchEntries();
    }
  }, [currentUser, selectedDate]);

  // 监听筛选条件变化，重新加载数据
  useEffect(() => {
    if (currentUser) {
      fetchEntries();
    }
  }, [searchQuery, filterMood]);

  const fetchUserInfo = async () => {
    try {
      const response = await fetch('/api/auth/check', {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        if (data.authenticated) {
          setCurrentUser({ authenticated: true });
        }
      }
    } catch (error) {
      console.error('检查认证状态失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchEntries = async () => {
    try {
      // 时间线视图：排除每日总结
      const params = new URLSearchParams();
      
      if (activeTab === 'calendar') {
        params.append('view', 'history');  // 历史日记显示所有包括总结
      }
      
      if (selectedDate) {
        params.append('date', selectedDate);
      }
      
      const baseUrl = '/api/diary/entries';
      const url = params.toString() ? `${baseUrl}?${params.toString()}` : baseUrl;
      
      console.log('正在获取日记条目...', url);
      
      const response = await fetch(url, {
        credentials: 'include'
      });
      
      console.log('获取日记条目响应状态:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('获取到的数据:', data);
        console.log('entries类型:', typeof data.entries);
        console.log('entries是否为数组:', Array.isArray(data.entries));
        if (data.entries && data.entries.length > 0) {
          console.log('第一个条目:', data.entries[0]);
        }
        setEntries(data.entries || []);
        console.log('设置的条目数量:', data.entries ? data.entries.length : 0);
      } else {
        console.error('获取日记条目失败，状态码:', response.status);
      }
    } catch (error) {
      console.error('获取日记条目失败:', error);
    }
  };

  const handleLogin = async () => {
    if (!password.trim()) {
      setLoginError('请输入密码');
      return;
    }

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password }),
        credentials: 'include'
      });

      const data = await response.json();
      
      if (response.ok && data.success) {
        setCurrentUser({ authenticated: true });
        setPassword('');
        setLoginError('');
      } else {
        setLoginError(data.message || '登录失败');
      }
    } catch (error) {
      console.error('登录失败:', error);
      setLoginError('登录失败，请重试');
    }
  };

  const handleSubmitEntry = async () => {
    if (!newEntryText.trim() || isSubmitting) return;

    setIsSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('text_content', newEntryText);
      
      const response = await fetch('/api/diary/entries', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });

      if (response.ok) {
        setNewEntryText('');
        // 立即获取数据显示"AI理解中..."状态
        fetchEntries();
        showNotification('日记保存成功！', 'success');
        
        // 启动轮询检查AI分析是否完成
        const checkAIAnalysis = async () => {
          let attempts = 0;
          const maxAttempts = 30; // 最多检查30次（约30秒）
          
          const pollInterval = setInterval(async () => {
            attempts++;
            try {
              const entriesResponse = await fetch('/api/diary/entries?per_page=1', {
                credentials: 'include'
              });
              
              if (entriesResponse.ok) {
                const data = await entriesResponse.json();
                const latestEntry = data.entries[0];
                
                // 如果AI分析完成（不再是"AI理解中..."），停止轮询并更新数据
                if (latestEntry && latestEntry.ai_analysis && !latestEntry.ai_analysis.includes('AI理解中')) {
                  clearInterval(pollInterval);
                  fetchEntries(); // 最终更新
                  showNotification('AI理解完成！', 'success');
                }
              }
              
              // 超时停止轮询
              if (attempts >= maxAttempts) {
                clearInterval(pollInterval);
              }
            } catch (error) {
              console.error('轮询AI分析状态失败:', error);
            }
          }, 1000); // 每秒检查一次
        };
        
        checkAIAnalysis();
      } else {
        showNotification('保存失败，请重试', 'error');
      }
    } catch (error) {
      console.error('发送日记失败:', error);
      showNotification('保存失败，请重试', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteEntry = async (entryId) => {
    if (!confirm('确定要删除这条日记吗？')) return;

    try {
      const response = await fetch(`/api/diary/entries/${entryId}`, {
        method: 'DELETE',
        credentials: 'include'
      });

      if (response.ok) {
        setEntries(entries.filter(entry => entry.id !== entryId));
        showNotification('日记已删除', 'success');
      } else {
        showNotification('删除失败，请重试', 'error');
      }
    } catch (error) {
      console.error('删除日记失败:', error);
      showNotification('删除失败，请重试', 'error');
    }
  };

  const handleEditEntry = (entry) => {
    setEditingEntry(entry);
  };

  const handleSaveEdit = async (entryId, newText) => {
    try {
      const response = await fetch(`/api/diary/entries/${entryId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text_content: newText }),
        credentials: 'include'
      });

      if (response.ok) {
        setEntries(entries.map(entry => 
          entry.id === entryId ? { ...entry, text_content: newText } : entry
        ));
        setEditingEntry(null);
        showNotification('修改已保存', 'success');
      } else {
        showNotification('修改失败，请重试', 'error');
      }
    } catch (error) {
      console.error('修改日记失败:', error);
      showNotification('修改失败，请重试', 'error');
    }
  };

  // 简单的通知功能
  const showNotification = (message, type = 'info') => {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 px-4 py-2 rounded-lg text-white font-medium transition-all duration-300 transform translate-x-full opacity-0 ${
      type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500'
    }`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // 动画显示
    setTimeout(() => {
      notification.style.transform = 'translateX(0)';
      notification.style.opacity = '1';
    }, 100);
    
    // 自动隐藏
    setTimeout(() => {
      notification.style.transform = 'translateX(full)';
      notification.style.opacity = '0';
      setTimeout(() => document.body.removeChild(notification), 300);
    }, 3000);
  };

  const handleImageUpload = async (file) => {
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('image', file);
      if (newEntryText) {
        formData.append('text_content', newEntryText);
      }

      const response = await fetch('/api/diary/entries', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });

      if (response.ok) {
        setNewEntryText('');
        // 立即获取数据显示"AI理解中..."状态
        fetchEntries();
        showNotification('图片上传成功！', 'success');
        
        // 启动轮询检查AI分析是否完成
        const checkAIAnalysis = async () => {
          let attempts = 0;
          const maxAttempts = 30; // 最多检查30次（约30秒）
          
          const pollInterval = setInterval(async () => {
            attempts++;
            try {
              const entriesResponse = await fetch('/api/diary/entries?per_page=1', {
                credentials: 'include'
              });
              
              if (entriesResponse.ok) {
                const data = await entriesResponse.json();
                const latestEntry = data.entries[0];
                
                // 如果AI分析完成（不再是"AI理解中..."），停止轮询并更新数据
                if (latestEntry && latestEntry.ai_analysis && !latestEntry.ai_analysis.includes('AI理解中')) {
                  clearInterval(pollInterval);
                  fetchEntries(); // 最终更新
                  showNotification('AI理解完成！', 'success');
                }
              }
              
              // 超时停止轮询
              if (attempts >= maxAttempts) {
                clearInterval(pollInterval);
              }
            } catch (error) {
              console.error('轮询AI分析状态失败:', error);
            }
          }, 1000); // 每秒检查一次
        };
        
        checkAIAnalysis();
      } else {
        showNotification('图片上传失败，请重试', 'error');
      }
    } catch (error) {
      console.error('上传图片失败:', error);
      showNotification('图片上传失败，请重试', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCameraCapture = async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert('无法访问摄像头：您的浏览器不支持摄像头功能，或页面未在安全上下文(HTTPS)中加载。');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' }
      });
      
      // 创建拍照界面
      const modal = document.createElement('div');
      modal.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
        background: rgba(0,0,0,0.9); z-index: 10000; display: flex; 
        flex-direction: column; align-items: center; justify-content: center;
      `;
      
      const video = document.createElement('video');
      video.style.cssText = 'max-width: 90%; max-height: 70%; border-radius: 8px;';
      video.srcObject = stream;
      video.autoplay = true;
      video.playsInline = true;
      
      const controls = document.createElement('div');
      controls.style.cssText = 'margin-top: 20px; display: flex; gap: 20px;';
      
      const captureBtn = document.createElement('button');
      captureBtn.textContent = '拍照';
      captureBtn.style.cssText = `
        padding: 12px 24px; background: #4F46E5; color: white; 
        border: none; border-radius: 8px; font-size: 16px; cursor: pointer;
      `;
      
      const cancelBtn = document.createElement('button');
      cancelBtn.textContent = '取消';
      cancelBtn.style.cssText = `
        padding: 12px 24px; background: #6B7280; color: white; 
        border: none; border-radius: 8px; font-size: 16px; cursor: pointer;
      `;
      
      controls.appendChild(captureBtn);
      controls.appendChild(cancelBtn);
      modal.appendChild(video);
      modal.appendChild(controls);
      document.body.appendChild(modal);
      
      captureBtn.onclick = () => {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);
        
        canvas.toBlob(blob => {
          const file = new File([blob], 'camera-photo.jpg', { type: 'image/jpeg' });
          handleImageUpload(file);
          stream.getTracks().forEach(track => track.stop());
          document.body.removeChild(modal);
        }, 'image/jpeg', 0.8);
      };
      
      cancelBtn.onclick = () => {
        stream.getTracks().forEach(track => track.stop());
        document.body.removeChild(modal);
      };
      
    } catch (error) {
      alert('无法访问摄像头：' + error.message);
    }
  };

  const handleFileSelect = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = (e) => {
      const file = e.target.files[0];
      if (file) {
        handleImageUpload(file);
      }
    };
    input.click();
  };

  const handleLogout = async () => {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include'
      });
      window.location.reload();
    } catch (error) {
      console.error('登出失败:', error);
    }
  };

  // 计算距离下次自动总结的时间
  const calculateCountdown = () => {
    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(0, 0, 0, 0); // 设置为明天0点
    
    const diff = tomorrow.getTime() - now.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);
    
    return { hours, minutes, seconds };
  };

  // 更新倒计时
  useEffect(() => {
    const updateCountdown = () => {
      setCountdown(calculateCountdown());
    };
    
    updateCountdown(); // 立即更新一次
    const interval = setInterval(updateCountdown, 1000); // 每秒更新
    
    return () => clearInterval(interval);
  }, []);

  // 手动生成总结
  const handleManualSummary = async () => {
    if (isGeneratingSummary) return;
    
    setIsGeneratingSummary(true);
    try {
      const response = await fetch('/api/diary/generate-daily-summary', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          date: getTodayDateString()
        }),
        credentials: 'include'
      });
      
      if (response.ok) {
        const result = await response.json();
        showNotification('每日总结生成成功！可在"历史日记"查看完整内容', 'success');
        await fetchEntries(); // 刷新数据
        // 自动切换到历史日记标签以便查看新生成的总结
        setActiveTab('calendar');
        // 短暂延时后通知用户
        setTimeout(() => {
          showNotification('每日总结已添加到历史日记 📝', 'success');
        }, 1000);
      } else {
        const error = await response.json();
        showNotification(error.message || '生成总结失败，请重试', 'error');
      }
    } catch (error) {
      console.error('生成总结失败:', error);
      showNotification('生成总结失败，请重试', 'error');
    } finally {
      setIsGeneratingSummary(false);
    }
  };
  const getTodayDateString = () => {
    const today = new Date();
    return today.getFullYear() + '-' + 
           String(today.getMonth() + 1).padStart(2, '0') + '-' + 
           String(today.getDate()).padStart(2, '0');
  };

  // 按日期分组所有日记条目
  const getHistoryEntriesByDate = () => {
    const grouped = {};
    
    // 按日期分组所有条目，包括今天
    entries.forEach(entry => {
      const entryDate = new Date(entry.created_at).toISOString().split('T')[0];
      if (!grouped[entryDate]) {
        grouped[entryDate] = [];
      }
      grouped[entryDate].push(entry);
    });

    // 转换为数组并按日期倒序排列
    return Object.entries(grouped)
      .map(([date, entries]) => ({ date, entries }))
      .sort((a, b) => new Date(b.date) - new Date(a.date));
  };

  // 生成日期的简短摘要
  const generateDaySummary = (dayEntries, date) => {
    if (dayEntries.length === 0) return '';
    
    // 查找当天的每日总结
    const dailySummary = dayEntries.find(entry => entry.is_daily_summary);
    
    if (dailySummary) {
      // 显著展示每日总结已完成
      const summaryText = dailySummary.text_content || '';
      const preview = summaryText.length > 50 ? summaryText.substring(0, 50) + '...' : summaryText;
      return `✅ 每日总结已生成 · ${preview}`;
    }
    
    // 获取今天的日期字符串
    const today = getTodayDateString();
    const regularEntries = dayEntries.filter(entry => !entry.is_daily_summary);
    
    if (regularEntries.length === 0) return '';
    
    // 检查是否有正在分析的条目
    const hasAnalyzingEntries = regularEntries.some(e => 
      e.ai_analysis && ['AI理解中', '分析中', '处理中'].some(keyword => 
        e.ai_analysis.includes(keyword)
      )
    );
    
    if (date === today) {
      // 今天的总结状态
      if (hasAnalyzingEntries) {
        return `${regularEntries.length}条记录 · AI分析中，准备生成总结...`;
      }
      return `${regularEntries.length}条记录 · 可以手动生成每日总结`;
    } else {
      // 历史日期的摘要
      const allText = regularEntries
        .map(entry => entry.text_content || '')
        .filter(text => text.trim())
        .join(' ');
      
      // 如果有AI分析，尝试提取关键信息
      const aiAnalyses = regularEntries
        .map(entry => entry.ai_analysis || '')
        .filter(analysis => analysis && !analysis.includes('AI理解中'));
      
      if (showMoodInHistory && aiAnalyses.length > 0) {
        const combinedAnalysis = aiAnalyses.join(' ');
        const moodMatches = combinedAnalysis.match(/(开心|快乐|高兴|愉快|兴奋|满足|幸福|喜悦|乐观|轻松|平静|安静|放松|悠闲|舒适|宁静|沮丧|难过|伤心|忧郁|失落|孤独|愤怒|生气|烦躁|焦虑|紧张|担心|压力|疲惫|累|无聊|思考|反思|感动|温暖|感激|惊喜|期待|希望)/g);
        
        if (moodMatches && moodMatches.length > 0) {
          const uniqueMoods = [...new Set(moodMatches)];
          return `${regularEntries.length}条记录 · ${uniqueMoods.slice(0, 3).join('、')}的一天`;
        }
      }
      
      const count = regularEntries.length;
      return `${count}条记录 · ${allText.length > 25 ? allText.substring(0, 25) + '...' : allText || '记录生活点滴'}`;
    }
  };

  // 切换日期展开状态
  const toggleDayExpansion = (date) => {
    setExpandedDays(prev => {
      const newSet = new Set(prev);
      if (newSet.has(date)) {
        newSet.delete(date);
      } else {
        newSet.add(date);
      }
      return newSet;
    });
  };
  const filteredEntries = entries.filter(entry => {
    const matchesSearch = !searchQuery || 
      entry.text_content?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      entry.ai_analysis?.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesMood = !filterMood || 
      entry.ai_analysis?.toLowerCase().includes(filterMood.toLowerCase());
    
    return matchesSearch && matchesMood;
  });

  console.log('当前entries数量:', entries.length);
  console.log('过滤后条目数量:', filteredEntries.length);
  console.log('当前activeTab:', activeTab);
  console.log('searchQuery:', searchQuery);
  console.log('filterMood:', filterMood);

  // 获取唯一的情绪标签
  const getMoodTags = () => {
    const moods = new Set();
    entries.forEach(entry => {
      if (entry.ai_analysis) {
        // 简单的情绪提取逻辑
        const moodMatches = entry.ai_analysis.match(/(开心|快乐|高兴|愉快|兴奋|满足|幸福|喜悦|乐观|轻松|平静|安静|放松|悠闲|舒适|宁静|沮丧|难过|伤心|忧郁|失落|孤独|愤怒|生气|烦躁|焦虑|紧张|担心|压力|疲惫|累|无聊|思考|反思|感动|温暖|感激|惊喜|期待|希望|困惑|疑惑|好奇)/g);
        if (moodMatches) {
          moodMatches.forEach(mood => moods.add(mood));
        }
      }
    });
    return Array.from(moods);
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) {
      return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    } else if (days === 1) {
      return '昨天 ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    } else if (days < 7) {
      return `${days}天前`;
    } else {
      return date.toLocaleDateString('zh-CN', { 
        month: 'numeric', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  };

  const formatAnalysis = (analysis) => {
    if (!analysis) return '';
    if (analysis.includes('AI理解中')) return analysis;
    
    // 简单的Markdown渲染
    return analysis
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');
  };

  if (loading) {
    return React.createElement('div', {
      className: 'min-h-screen bg-gray-50 flex items-center justify-center'
    }, React.createElement('div', {
      className: 'text-center'
    }, [
      React.createElement('div', {
        key: 'spinner',
        className: 'animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4'
      }),
      React.createElement('p', {
        key: 'text',
        className: 'text-gray-600'
      }, '加载中...')
    ]));
  }

  if (!currentUser) {
    return React.createElement('div', {
      className: 'min-h-screen bg-gray-50 flex items-center justify-center p-4'
    }, React.createElement('div', {
      className: 'bg-white rounded-lg shadow-lg p-8 w-full max-w-md border border-gray-200'
    }, [
      React.createElement('div', {
        key: 'header',
        className: 'text-center mb-6'
      }, [
        React.createElement(BookOpen, {
          key: 'icon',
          className: 'h-16 w-16 text-blue-600 mx-auto mb-4'
        }),
        React.createElement('h1', {
          key: 'title',
          className: 'text-2xl font-bold text-gray-900 mb-2'
        }, 'AI日记'),
        React.createElement('p', {
          key: 'desc',
          className: 'text-gray-600'
        }, '请输入密码以继续使用')
      ]),
      
      React.createElement('div', {
        key: 'form',
        className: 'space-y-4'
      }, [
        React.createElement('div', {
          key: 'input-group'
        }, [
          React.createElement('label', {
            key: 'label',
            className: 'block text-sm font-medium text-gray-700 mb-2'
          }, '密码'),
          React.createElement('input', {
            key: 'input',
            type: 'password',
            value: password,
            onChange: (e) => setPassword(e.target.value),
            onKeyPress: (e) => e.key === 'Enter' && handleLogin(),
            placeholder: '请输入密码',
            className: 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            style: { fontSize: '16px' }
          })
        ]),
        
        loginError && React.createElement('div', {
          key: 'error',
          className: 'bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm'
        }, loginError),
        
        React.createElement(Button, {
          key: 'login-btn',
          onClick: handleLogin,
          disabled: !password.trim(),
          className: 'w-full bg-blue-600 hover:bg-blue-700'
        }, '登录')
      ]),
      
      React.createElement('div', {
        key: 'hint',
        className: 'mt-6 text-center text-sm text-gray-500'
      }, '默认密码：1234')
    ]));
  }

  return React.createElement('div', {
    className: 'min-h-screen bg-gray-50'
  }, [
    // 顶部导航
    React.createElement('header', {
      key: 'header',
      className: 'bg-white border-b border-gray-200 px-4 py-3'
    }, React.createElement('div', {
      className: 'flex items-center justify-between max-w-4xl mx-auto'
    }, [
      React.createElement('div', {
        key: 'logo',
        className: 'flex items-center gap-3'
      }, [
        React.createElement(BookOpen, {
          key: 'icon',
          className: 'h-8 w-8 text-blue-600'
        }),
        React.createElement('h1', {
          key: 'title',
          className: 'text-xl font-bold text-gray-900'
        }, 'AI日记')
      ]),
      React.createElement('div', {
        key: 'actions',
        className: 'flex items-center gap-3'
      }, [
        React.createElement(Button, {
          key: 'refresh',
          variant: 'outline',
          size: 'sm',
          onClick: () => window.location.reload()
        }, '刷新'),
        React.createElement(Button, {
          key: 'settings',
          variant: 'outline',
          size: 'sm',
          onClick: () => document.getElementById('config-overlay').style.display = 'block'
        }, '设置'),
        React.createElement(Button, {
          key: 'logout',
          variant: 'outline',
          size: 'sm',
          onClick: handleLogout
        }, '登出')
      ])
    ])),

    // 主内容
    React.createElement('main', {
      key: 'main',
      className: 'max-w-4xl mx-auto px-4 py-6'
    }, React.createElement(Tabs, {
      value: activeTab,
      onValueChange: setActiveTab,
      className: 'w-full'
    }, [
      React.createElement(TabsList, {
        key: 'tabs-list',
        className: 'grid w-full grid-cols-2'
      }, [
        React.createElement(TabsTrigger, {
          key: 'timeline-trigger',
          value: 'timeline',
          className: 'flex items-center gap-2'
        }, [
          React.createElement(Clock, {
            key: 'icon',
            className: 'h-4 w-4'
          }),
          '时间线'
        ]),
        React.createElement(TabsTrigger, {
          key: 'calendar-trigger',
          value: 'calendar',
          className: 'flex items-center gap-2'
        }, [
          React.createElement(BookOpen, {
            key: 'icon',
            className: 'h-4 w-4'
          }),
          '历史日记'
        ])
      ]),

      React.createElement(TabsContent, {
        key: 'timeline-content',
        value: 'timeline',
        className: 'space-y-6'
      }, [
        // 每日总结倒计时区域
        React.createElement('div', {
          key: 'summary-countdown',
          className: 'bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200 p-6'
        }, [
          React.createElement('div', {
            key: 'countdown-header',
            className: 'flex items-center justify-between mb-4'
          }, [
            React.createElement('h3', {
              key: 'title',
              className: 'text-lg font-semibold text-blue-900'
            }, '每日总结'),
            React.createElement('div', {
              key: 'countdown-display',
              className: 'text-right'
            }, [
              React.createElement('p', {
                key: 'countdown-label',
                className: 'text-sm text-blue-700 mb-1'
              }, '距离自动总结还有：'),
              React.createElement('div', {
                key: 'countdown-time',
                className: 'text-2xl font-bold text-blue-800 font-mono'
              }, `${countdown.hours.toString().padStart(2, '0')}:${countdown.minutes.toString().padStart(2, '0')}:${countdown.seconds.toString().padStart(2, '0')}`)
            ])
          ]),
          React.createElement('div', {
            key: 'summary-actions',
            className: 'flex items-center justify-between'
          }, [
            React.createElement('p', {
              key: 'description',
              className: 'text-sm text-blue-700'
            }, '系统将在每天0点自动生成当日的总结日记'),
            React.createElement(Button, {
              key: 'manual-summary',
              onClick: handleManualSummary,
              disabled: isGeneratingSummary,
              className: 'bg-blue-600 hover:bg-blue-700 text-white'
            }, isGeneratingSummary ? '生成中...' : '现在总结')
          ])
        ]),

        // 写日记区域
        React.createElement('div', {
          key: 'write-area',
          className: 'bg-white rounded-lg border border-gray-200 p-6'
        }, [
          React.createElement('h2', {
            key: 'title',
            className: 'text-lg font-semibold text-gray-900 mb-4'
          }, '今日记录'),
          
          React.createElement('div', {
            key: 'form',
            className: 'space-y-4'
          }, [
            React.createElement('div', {
              key: 'textarea-wrapper',
              className: 'relative'
            }, [
              React.createElement('textarea', {
                key: 'textarea',
                ref: textareaRef,
                value: newEntryText,
                onChange: (e) => setNewEntryText(e.target.value),
                placeholder: '记录今天发生的事情...',
                className: 'w-full min-h-32 p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                style: { fontSize: '16px' }
              }),
              React.createElement('div', {
                key: 'char-count',
                className: 'absolute bottom-2 right-2 text-xs text-gray-400'
              }, `${newEntryText.length}/1000`)
            ]),
            
            React.createElement('div', {
              key: 'buttons',
              className: 'flex items-center gap-3'
            }, [
              React.createElement(Button, {
                key: 'submit',
                onClick: handleSubmitEntry,
                disabled: !newEntryText.trim() || isSubmitting,
                className: 'bg-blue-600 hover:bg-blue-700'
              }, isSubmitting ? '发送中...' : '发送'),
              
              React.createElement(Button, {
                key: 'camera',
                variant: 'outline',
                onClick: handleCameraCapture,
                disabled: isSubmitting,
                className: 'flex items-center gap-2'
              }, [
                React.createElement(Camera, {
                  key: 'icon',
                  className: 'h-4 w-4'
                }),
                '拍照'
              ]),
              
              React.createElement(Button, {
                key: 'upload',
                variant: 'outline',
                onClick: handleFileSelect,
                disabled: isSubmitting,
                className: 'flex items-center gap-2'
              }, [
                React.createElement(Upload, {
                  key: 'icon',
                  className: 'h-4 w-4'
                }),
                '上传图片'
              ])
            ])
          ])
        ]),

        // 搜索和过滤区域
        React.createElement('div', {
          key: 'search-filters',
          className: 'bg-white rounded-lg border border-gray-200 p-4'
        }, [
          React.createElement('div', {
            key: 'search-bar',
            className: 'flex items-center gap-3 mb-3'
          }, [
            React.createElement('div', {
              key: 'search-wrapper',
              className: 'flex-1 relative'
            }, [
              React.createElement(Search, {
                key: 'search-icon',
                className: 'absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400'
              }),
              React.createElement('input', {
                key: 'search-input',
                type: 'text',
                value: searchQuery,
                onChange: (e) => setSearchQuery(e.target.value),
                placeholder: '搜索日记内容...',
                className: 'w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
              })
            ]),
            React.createElement(Button, {
              key: 'filter-toggle',
              variant: 'outline',
              onClick: () => setShowFilters(!showFilters),
              className: `flex items-center gap-2 ${showFilters ? 'bg-blue-50 border-blue-200' : ''}`
            }, [
              React.createElement(Filter, {
                key: 'filter-icon',
                className: 'h-4 w-4'
              }),
              '筛选'
            ])
          ]),
          
          showFilters && React.createElement('div', {
            key: 'filters',
            className: 'border-t border-gray-200 pt-3 space-y-3'
          }, [
            React.createElement('div', {
              key: 'mood-filter'
            }, [
              React.createElement('label', {
                key: 'mood-label',
                className: 'block text-sm font-medium text-gray-700 mb-2'
              }, '情绪筛选'),
              React.createElement('div', {
                key: 'mood-tags',
                className: 'flex flex-wrap gap-2'
              }, [
                React.createElement('button', {
                  key: 'all-moods',
                  onClick: () => setFilterMood(''),
                  className: `px-3 py-1 rounded-full text-sm ${
                    !filterMood ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`
                }, '全部'),
                ...getMoodTags().map(mood => 
                  React.createElement('button', {
                    key: mood,
                    onClick: () => setFilterMood(filterMood === mood ? '' : mood),
                    className: `px-3 py-1 rounded-full text-sm ${
                      filterMood === mood ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`
                  }, mood)
                )
              ])
            ])
          ])
        ]),

        // 日记条目列表
        React.createElement('div', {
          key: 'entries',
          className: 'space-y-4'
        }, (() => {
          console.log('渲染条目列表，filteredEntries.length:', filteredEntries.length);
          if (filteredEntries.length === 0) {
            console.log('显示空状态');
            return [
              React.createElement('div', {
                key: 'empty',
                className: 'bg-white rounded-lg border border-gray-200 p-8 text-center'
              }, [
                React.createElement(BookOpen, {
                  key: 'icon',
                  className: 'h-12 w-12 text-gray-400 mx-auto mb-4'
                }),
                React.createElement('p', {
                  key: 'text',
                  className: 'text-gray-500 mb-2'
                }, searchQuery || filterMood ? '没有找到匹配的日记' : '还没有日记条目，开始写下第一篇吧！'),
                (searchQuery || filterMood) && React.createElement(Button, {
                  key: 'clear-filters',
                  variant: 'outline',
                  onClick: () => {
                    setSearchQuery('');
                    setFilterMood('');
                  },
                  className: 'mt-2'
                }, '清除筛选')
              ])
            ];
          } else {
            console.log('渲染', filteredEntries.length, '个条目');
            return filteredEntries.map((entry, index) => {
              console.log('渲染条目', index, ':', entry.id);
              return React.createElement('div', {
                key: entry.id,
                className: 'bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow duration-200 group'
              }, [
                React.createElement('div', {
                  key: 'header',
                  className: 'flex items-start justify-between mb-3'
                }, [
                  React.createElement('div', {
                    key: 'time-info',
                    className: 'text-sm text-gray-500 flex items-center gap-2'
                  }, [
                    React.createElement(Clock, {
                      key: 'clock-icon',
                      className: 'h-4 w-4'
                    }),
                    formatTime(entry.timestamp)
                  ]),
                  !entry.is_daily_summary && React.createElement('div', {
                    key: 'actions',
                    className: 'flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200'
                  }, [
                    React.createElement('button', {
                      key: 'edit',
                      title: '编辑这篇日记',
                      onClick: (e) => {
                        e.stopPropagation();
                        handleEditEntry(entry);
                      },
                      className: 'inline-flex items-center text-xs px-2 py-1 border border-gray-300 rounded-md hover:bg-gray-100 hover:border-gray-400 transition-colors duration-200'
                    }, [
                      React.createElement(Edit, {
                        className: 'h-3 w-3 mr-1'
                      }),
                      React.createElement('span', {}, '编辑')
                    ]),
                    React.createElement('button', {
                      key: 'delete',
                      title: '删除这篇日记',
                      onClick: (e) => {
                        e.stopPropagation();
                        handleDeleteEntry(entry.id);
                      },
                      className: 'inline-flex items-center text-xs px-2 py-1 border border-red-300 rounded-md hover:bg-red-50 hover:text-red-600 hover:border-red-400 transition-colors duration-200'
                    }, [
                      React.createElement(Trash2, {
                        className: 'h-3 w-3 mr-1'
                      }),
                      React.createElement('span', {}, '删除')
                    ])
                  ])
                ]),
                
                editingEntry?.id === entry.id ? 
                  React.createElement(EditEntryForm, {
                    key: 'edit-form',
                    entry: entry,
                    onSave: handleSaveEdit,
                    onCancel: () => setEditingEntry(null)
                  }) :
                  [
                    entry.text_content && React.createElement('div', {
                      key: 'text',
                      className: 'mb-4'
                    }, React.createElement('p', {
                      className: 'text-gray-900 whitespace-pre-wrap'
                    }, entry.text_content)),
                    
                    entry.image_path && React.createElement('div', {
                      key: 'image',
                      className: 'mb-4'
                    }, React.createElement('img', {
                      src: entry.image_path,
                      alt: '日记图片',
                      className: 'max-w-full h-auto rounded-lg border border-gray-200 cursor-pointer',
                      onClick: () => window.open(entry.image_path, '_blank')
                    })),
                    
                    entry.ai_analysis && React.createElement('div', {
                      key: 'analysis',
                      className: 'bg-blue-50 rounded-lg p-4 border border-blue-200'
                    }, [
                      React.createElement('h4', {
                        key: 'title',
                        className: 'text-sm font-medium text-blue-900 mb-2'
                      }, 'AI理解'),
                      React.createElement('div', {
                        key: 'content',
                        className: 'text-sm text-blue-800 ai-analysis-content',
                        dangerouslySetInnerHTML: { __html: formatAnalysis(entry.ai_analysis) }
                      })
                    ])
                  ]
              ]);
            });
          }
        })())
      ]),

      React.createElement(TabsContent, {
        key: 'calendar-content',
        value: 'calendar',
        className: 'space-y-6'
      }, [
        // 历史日记标题
        React.createElement('div', {
          key: 'history-header',
          className: 'bg-white rounded-lg border border-gray-200 p-6'
        }, [
          React.createElement('div', {
            key: 'header-content',
            className: 'flex items-center justify-between mb-2'
          }, [
            React.createElement('h2', {
              key: 'title',
              className: 'text-lg font-semibold text-gray-900'
            }, '历史日记'),
            React.createElement('div', {
              key: 'settings',
              className: 'flex items-center gap-2'
            }, [
              React.createElement('label', {
                key: 'mood-toggle-label',
                className: 'flex items-center gap-2 text-sm text-gray-600 cursor-pointer'
              }, [
                React.createElement('input', {
                  key: 'mood-toggle',
                  type: 'checkbox',
                  checked: showMoodInHistory,
                  onChange: (e) => setShowMoodInHistory(e.target.checked),
                  className: 'rounded border-gray-300 text-blue-600 focus:ring-blue-500'
                }),
                '显示情绪标签'
              ])
            ])
          ]),
          React.createElement('p', {
            key: 'description',
            className: 'text-sm text-gray-600'
          }, '按日期浏览过往的日记记录，点击展开查看详细内容')
        ]),

        // 历史日记列表
        React.createElement('div', {
          key: 'history-entries',
          className: 'space-y-4'
        }, (() => {
          const historyDays = getHistoryEntriesByDate();
          
          if (historyDays.length === 0) {
            return React.createElement('div', {
              key: 'empty',
              className: 'bg-white rounded-lg border border-gray-200 p-8 text-center'
            }, [
              React.createElement(BookOpen, {
                key: 'icon',
                className: 'h-12 w-12 text-gray-400 mx-auto mb-4'
              }),
              React.createElement('p', {
                key: 'text',
                className: 'text-gray-500'
              }, '还没有历史日记记录')
            ]);
          }

          return historyDays.map(({ date, entries: dayEntries }) => {
            const isExpanded = expandedDays.has(date);
            const dateObj = new Date(date);
            const formattedDate = dateObj.toLocaleDateString('zh-CN', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
              weekday: 'long'
            });

            return React.createElement('div', {
              key: date,
              className: 'bg-white rounded-lg border border-gray-200 overflow-hidden'
            }, [
              // 日期摘要卡片
              React.createElement('div', {
                key: 'day-summary',
                className: 'p-6 cursor-pointer hover:bg-gray-50 transition-colors duration-200',
                onClick: () => toggleDayExpansion(date)
              }, [
                React.createElement('div', {
                  key: 'header',
                  className: 'flex items-center justify-between'
                }, [
                  React.createElement('div', {
                    key: 'date-info'
                  }, [
                    React.createElement('h3', {
                      key: 'date',
                      className: 'text-lg font-semibold text-gray-900'
                    }, formattedDate),
                    React.createElement('p', {
                      key: 'summary',
                      className: 'text-sm text-gray-600 mt-1'
                    }, generateDaySummary(dayEntries, date))
                  ]),
                  React.createElement('div', {
                    key: 'expand-icon',
                    className: `transform transition-transform duration-200 ${isExpanded ? 'rotate-90' : ''}`
                  }, React.createElement('svg', {
                    className: 'h-5 w-5 text-gray-400',
                    fill: 'none',
                    stroke: 'currentColor',
                    viewBox: '0 0 24 24'
                  }, React.createElement('path', {
                    strokeLinecap: 'round',
                    strokeLinejoin: 'round',
                    strokeWidth: 2,
                    d: 'M9 5l7 7-7 7'
                  })))
                ])
              ]),

              // 展开的详细条目
              isExpanded && React.createElement('div', {
                key: 'day-details',
                className: 'border-t border-gray-200 bg-gray-50'
              }, [
                React.createElement('div', {
                  key: 'entries-list',
                  className: 'p-4 space-y-4'
                }, (() => {
                  // 将每日总结和普通条目分开，每日总结在前
                  const summaryEntries = dayEntries.filter(entry => entry.is_daily_summary);
                  const regularEntries = dayEntries.filter(entry => !entry.is_daily_summary);
                  const orderedEntries = [...summaryEntries, ...regularEntries];
                  
                  return orderedEntries.map((entry, index) => 
                    React.createElement('div', {
                      key: entry.id,
                      className: `${entry.is_daily_summary ? 'bg-gradient-to-r from-amber-50 to-yellow-50 border-amber-200' : 'bg-white border-gray-200'} rounded-lg border p-4`
                    }, [
                      React.createElement('div', {
                        key: 'entry-header',
                        className: 'flex items-start justify-between mb-3'
                      }, [
                        React.createElement('div', {
                          key: 'time-info',
                          className: 'text-sm text-gray-500 flex items-center gap-2'
                        }, [
                          React.createElement(entry.is_daily_summary ? BookOpen : Clock, {
                            key: 'icon',
                            className: 'h-4 w-4'
                          }),
                          entry.is_daily_summary ? '每日总结' : formatTime(entry.created_at)
                        ]),
                        !entry.is_daily_summary && React.createElement('div', {
                          key: 'actions',
                          className: 'flex items-center gap-2'
                        }, [
                          React.createElement('button', {
                            key: 'edit',
                            title: '编辑这篇日记',
                            onClick: (e) => {
                              e.stopPropagation();
                              handleEditEntry(entry);
                            },
                            className: 'inline-flex items-center text-xs px-2 py-1 border border-gray-300 rounded-md hover:bg-gray-100 hover:border-gray-400 transition-colors duration-200'
                          }, [
                            React.createElement(Edit, {
                              className: 'h-3 w-3 mr-1'
                            }),
                            React.createElement('span', {}, '编辑')
                          ]),
                          React.createElement('button', {
                            key: 'delete',
                            title: '删除这篇日记',
                            onClick: (e) => {
                              e.stopPropagation();
                              handleDeleteEntry(entry.id);
                            },
                            className: 'inline-flex items-center text-xs px-2 py-1 border border-red-300 rounded-md hover:bg-red-50 hover:text-red-600 hover:border-red-400 transition-colors duration-200'
                          }, [
                            React.createElement(Trash2, {
                              className: 'h-3 w-3 mr-1'
                            }),
                            React.createElement('span', {}, '删除')
                          ])
                        ])
                      ]),
                      
                      editingEntry?.id === entry.id ? 
                        React.createElement(EditEntryForm, {
                          key: 'edit-form',
                          entry: entry,
                          onSave: handleSaveEdit,
                          onCancel: () => setEditingEntry(null)
                        }) :
                        [
                          entry.text_content && React.createElement('div', {
                            key: 'text',
                            className: 'mb-4'
                          }, React.createElement('p', {
                            className: 'text-gray-900 whitespace-pre-wrap'
                          }, entry.text_content)),
                          
                          entry.image_path && React.createElement('div', {
                            key: 'image',
                            className: 'mb-4'
                          }, React.createElement('img', {
                            src: entry.image_path,
                            alt: '日记图片',
                            className: 'max-w-full h-auto rounded-lg border border-gray-200 cursor-pointer',
                            onClick: () => window.open(entry.image_path, '_blank')
                          })),
                          
                          entry.ai_analysis && React.createElement('div', {
                            key: 'analysis',
                            className: 'bg-blue-50 rounded-lg p-4 border border-blue-200'
                          }, [
                            React.createElement('h4', {
                              key: 'title',
                              className: 'text-sm font-medium text-blue-900 mb-2'
                            }, 'AI理解'),
                            React.createElement('div', {
                              key: 'content',
                              className: 'text-sm text-blue-800 ai-analysis-content',
                              dangerouslySetInnerHTML: { __html: formatAnalysis(entry.ai_analysis) }
                            })
                          ])
                        ]
                    ])
                  );
                })())
              ])
            ]);
          });
        })())
      ])
    ]))
  ]);
}

// 渲染应用
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('root');
  if (container) {
    const root = ReactDOM.createRoot(container);
    root.render(React.createElement(App));
  }
});

// 保持原有的设置功能
function openSettings() {
  document.getElementById('config-overlay').style.display = 'block';
}

function closeSettings() {
  document.getElementById('config-overlay').style.display = 'none';
}

// 导出给全局使用
window.openSettings = openSettings;
window.closeSettings = closeSettings;