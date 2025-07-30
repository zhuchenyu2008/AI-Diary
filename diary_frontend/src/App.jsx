import { useState, useEffect } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Button } from '@/components/ui/button.jsx'
import { LogOut, Coffee, Plus, History, Settings } from 'lucide-react'
import Login from './components/Login.jsx'
import DiaryTimeline from './components/DiaryTimeline.jsx'
import DiaryInput from './components/DiaryInput.jsx'
import HistoryView from './components/HistoryView.jsx'
import MCPSettings from './components/MCPSettings.jsx'
import './App.css'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)
  const [entries, setEntries] = useState([])
  const [activeTab, setActiveTab] = useState('today')
  const [showMCPSettings, setShowMCPSettings] = useState(false)

  useEffect(() => {
    checkAuth()
  }, [])

  useEffect(() => {
    if (isAuthenticated && activeTab === 'today') {
      fetchTodayEntries()
    }
  }, [isAuthenticated, activeTab])

  const checkAuth = async () => {
    try {
      const response = await fetch('/api/auth/check')
      const data = await response.json()
      setIsAuthenticated(data.authenticated)
    } catch (error) {
      console.error('检查认证状态失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchTodayEntries = async () => {
    try {
      const today = new Date().toISOString().split('T')[0]
      const response = await fetch(`/api/diary/entries?date=${today}&per_page=50`)
      const data = await response.json()
      
      if (data.success) {
        setEntries(data.entries)
      }
    } catch (error) {
      console.error('获取今日记录失败:', error)
    }
  }

  const handleLogin = () => {
    setIsAuthenticated(true)
  }

  const handleLogout = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' })
      setIsAuthenticated(false)
      setEntries([])
    } catch (error) {
      console.error('登出失败:', error)
    }
  }

  const handleEntryCreated = (newEntry) => {
    setEntries(prev => [newEntry, ...prev])
  }

  const openSettings = () => {
    setShowMCPSettings(true)
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-500">加载中...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />
  }

  return (
    <div className="min-h-screen bg-gray-50 safe-area-top safe-area-bottom">
      {/* MCP设置弹窗 */}
      {showMCPSettings && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-2 sm:p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl mobile-modal overflow-y-auto mobile-scroll settings-modal">
            <div className="p-4 sm:p-6">
              <MCPSettings onClose={() => setShowMCPSettings(false)} />
            </div>
          </div>
        </div>
      )}

      {/* 顶部导航 */}
      <header className="bg-white shadow-sm border-b safe-area-top">
        <div className="max-w-4xl mx-auto px-3 sm:px-4 py-3 sm:py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 sm:space-x-3">
              <Coffee className="h-6 w-6 sm:h-8 sm:w-8 text-indigo-600" />
              <h1 className="mobile-title font-bold text-gray-900">杯子日记</h1>
            </div>
            <div className="flex items-center space-x-1 sm:space-x-2">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={openSettings}
                className="text-gray-600 hover:text-gray-900 touch-button text-xs sm:text-sm px-2 sm:px-3"
              >
                <Settings className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2" />
                <span className="hidden sm:inline">设置</span>
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleLogout}
                className="text-gray-600 hover:text-gray-900 touch-button text-xs sm:text-sm px-2 sm:px-3"
              >
                <LogOut className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2" />
                <span className="hidden sm:inline">登出</span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* 主要内容 */}
      <main className="max-w-4xl mx-auto px-3 sm:px-4 py-4 sm:py-6 safe-area-bottom">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4 sm:space-y-6">
          <TabsList className="grid w-full grid-cols-2 tabs-list">
            <TabsTrigger value="today" className="flex items-center space-x-1 sm:space-x-2 text-xs sm:text-sm">
              <Plus className="h-3 w-3 sm:h-4 sm:w-4" />
              <span>今日记录</span>
            </TabsTrigger>
            <TabsTrigger value="history" className="flex items-center space-x-1 sm:space-x-2 text-xs sm:text-sm">
              <History className="h-3 w-3 sm:h-4 sm:w-4" />
              <span>历史日记</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="today" className="mobile-card-spacing">
            <DiaryInput onEntryCreated={handleEntryCreated} />
            <DiaryTimeline 
              entries={entries} 
              onRefresh={fetchTodayEntries}
            />
          </TabsContent>

          <TabsContent value="history">
            <HistoryView />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}

export default App
