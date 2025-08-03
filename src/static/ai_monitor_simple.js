// 简化的AI分析监控脚本
function initSimpleAIMonitor() {
  console.log('初始化简化AI分析监控');
  
  // 检查是否有正在分析的内容
  function checkForAnalyzingContent() {
    const analyzingElements = document.querySelectorAll('.ai-analysis-content');
    let hasAnalyzing = false;
    
    analyzingElements.forEach(el => {
      if (el.textContent) {
        const analyzingKeywords = ['AI理解中', 'AI理解中...', '分析中', '处理中'];
        hasAnalyzing = hasAnalyzing || analyzingKeywords.some(keyword => el.textContent.includes(keyword));
      }
    });
    
    return hasAnalyzing;
  }
  
  // 监控AI分析状态
  function monitorAIAnalysis() {
    console.log('开始监控AI分析状态');
    
    const checkInterval = setInterval(async () => {
      try {
        const response = await fetch('/api/diary/entries/today/analysis-status', {
          method: 'GET',
          credentials: 'include'
        });
        
        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            const hasAnalyzing = data.entries.some(entry => entry.is_analyzing);
            
            if (!hasAnalyzing) {
              console.log('AI分析完成，触发页面更新');
              clearInterval(checkInterval);
              
              // 触发数据更新
              const refreshBtn = [...document.querySelectorAll('button')].find(btn => 
                btn.textContent && btn.textContent.includes('刷新')
              );
              if (refreshBtn) {
                refreshBtn.click();
              } else {
                window.location.reload();
              }
            }
          }
        }
      } catch (error) {
        console.error('AI分析状态检查失败:', error);
        clearInterval(checkInterval);
      }
    }, 3000);
    
    // 60秒后自动停止
    setTimeout(() => {
      clearInterval(checkInterval);
    }, 60000);
  }
  
  // 监听页面变化
  const observer = new MutationObserver(() => {
    setTimeout(() => {
      if (checkForAnalyzingContent()) {
        monitorAIAnalysis();
      }
    }, 500);
  });
  
  observer.observe(document.getElementById('root'), { childList: true, subtree: true });
  
  // 监听发送按钮点击
  document.addEventListener('click', (e) => {
    if (e.target.textContent && e.target.textContent.includes('发送')) {
      setTimeout(monitorAIAnalysis, 1000);
    }
  });
  
  // 初始检查
  if (checkForAnalyzingContent()) {
    monitorAIAnalysis();
  }
}

// 页面加载后启动
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initSimpleAIMonitor);
} else {
  initSimpleAIMonitor();
}