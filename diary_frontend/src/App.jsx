import { useState, useEffect } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Button } from '@/components/ui/button.jsx'
import { LogOut, Coffee, Plus, History, Settings } from 'lucide-react'
import Login from './components/Login.jsx'
import DiaryTimeline from './components/DiaryTimeline.jsx'
import DiaryInput from './components/DiaryInput.jsx'
import HistoryView from './components/HistoryView.jsx'
import './App.css'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)
  const [entries, setEntries] = useState([])
  const [activeTab, setActiveTab] = useState('today')

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
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航 */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Coffee className="h-8 w-8 text-indigo-600" />
              <h1 className="text-2xl font-bold text-gray-900">杯子日记</h1>
            </div>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleLogout}
              className="text-gray-600 hover:text-gray-900"
            >
              <LogOut className="h-4 w-4 mr-2" />
              登出
            </Button>
          </div>
        </div>
      </header>

      {/* 主要内容 */}
      <main className="max-w-4xl mx-auto px-4 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="today" className="flex items-center space-x-2">
              <Plus className="h-4 w-4" />
              <span>今日记录</span>
            </TabsTrigger>
            <TabsTrigger value="history" className="flex items-center space-x-2">
              <History className="h-4 w-4" />
              <span>历史日记</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="today" className="space-y-6">
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
