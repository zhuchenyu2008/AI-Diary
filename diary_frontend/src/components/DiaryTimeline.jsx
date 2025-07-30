import { useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Clock, Image as ImageIcon, MessageSquare, Sparkles, Loader2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

const DiaryTimeline = ({ entries, onRefresh }) => {
  const [countdown, setCountdown] = useState({ hours: 0, minutes: 0, seconds: 0 })
  const [analyzingEntries, setAnalyzingEntries] = useState(new Set())

  useEffect(() => {
    const updateCountdown = async () => {
      try {
        const response = await fetch('/api/diary/today-countdown')
        const data = await response.json()
        if (data.success) {
          setCountdown(data.countdown)
        }
      } catch (error) {
        console.error('获取倒计时失败:', error)
      }
    }

    updateCountdown()
    const interval = setInterval(updateCountdown, 1000)
    return () => clearInterval(interval)
  }, [])

  // 监控AI分析状态
  useEffect(() => {
    const checkAnalysisStatus = async () => {
      const entriesNeedingAnalysis = entries.filter(entry => 
        !entry.ai_analysis && (entry.text_content || entry.image_path)
      )

      if (entriesNeedingAnalysis.length === 0) return

      for (const entry of entriesNeedingAnalysis) {
        if (!analyzingEntries.has(entry.id)) {
          setAnalyzingEntries(prev => new Set([...prev, entry.id]))
          
          // 开始轮询检查分析状态
          const pollAnalysis = async () => {
            try {
              const response = await fetch(`/api/diary/entries/${entry.id}/analysis-status`)
              const data = await response.json()
              
              if (data.success && data.has_analysis) {
                // AI分析完成，刷新条目列表
                setAnalyzingEntries(prev => {
                  const newSet = new Set(prev)
                  newSet.delete(entry.id)
                  return newSet
                })
                onRefresh()
              } else {
                // 继续轮询
                setTimeout(pollAnalysis, 2000)
              }
            } catch (error) {
              console.error('检查AI分析状态失败:', error)
              setAnalyzingEntries(prev => {
                const newSet = new Set(prev)
                newSet.delete(entry.id)
                return newSet
              })
            }
          }
          
          // 延迟开始轮询，给AI分析一些时间
          setTimeout(pollAnalysis, 3000)
        }
      }
    }

    checkAnalysisStatus()
  }, [entries, analyzingEntries, onRefresh])

  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('zh-CN', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    })
  }

  const formatDate = (timestamp) => {
    const date = new Date(timestamp)
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)

    if (date.toDateString() === today.toDateString()) {
      return '今天'
    } else if (date.toDateString() === yesterday.toDateString()) {
      return '昨天'
    } else {
      return date.toLocaleDateString('zh-CN', { 
        month: 'long', 
        day: 'numeric' 
      })
    }
  }

  const isAnalyzing = (entryId) => {
    return analyzingEntries.has(entryId)
  }

  return (
    <div className="timeline-mobile">
      {/* 倒计时卡片 */}
      <Card className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white card-mobile">
        <CardContent className="p-4 sm:p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base sm:text-lg font-semibold mb-2">距离日记总结还有</h3>
              <div className="flex items-center space-x-2 sm:space-x-4 text-lg sm:text-2xl font-bold">
                <span className="mobile-text">{countdown.hours.toString().padStart(2, '0')}小时</span>
                <span className="mobile-text">{countdown.minutes.toString().padStart(2, '0')}分钟</span>
                <span className="mobile-text">{countdown.seconds.toString().padStart(2, '0')}秒</span>
              </div>
            </div>
            <Clock className="h-8 w-8 sm:h-12 sm:w-12 opacity-80" />
          </div>
        </CardContent>
      </Card>

      {/* 日记条目列表 */}
      <div className="mobile-card-spacing">
        <div className="flex items-center justify-between">
          <h2 className="mobile-title font-semibold text-gray-900">今日记录</h2>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={onRefresh}
            className="text-indigo-600 border-indigo-200 hover:bg-indigo-50 touch-button"
          >
            <span className="mobile-text">刷新</span>
          </Button>
        </div>

        <AnimatePresence>
          {entries.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center py-8 sm:py-12 text-gray-500"
            >
              <MessageSquare className="h-8 w-8 sm:h-12 sm:w-12 mx-auto mb-3 sm:mb-4 opacity-50" />
              <p className="mobile-text">还没有记录，开始记录你的第一个瞬间吧！</p>
            </motion.div>
          ) : (
            <div className="mobile-card-spacing">
              {entries.map((entry, index) => (
                <motion.div
                  key={entry.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="hover:shadow-md transition-shadow duration-200 card-mobile">
                    <CardContent className="p-3 sm:p-4">
                      <div className="flex items-start space-x-3 sm:space-x-4">
                        {/* 时间线 */}
                        <div className="flex flex-col items-center">
                          <div className="w-2 h-2 sm:w-3 sm:h-3 bg-indigo-500 rounded-full"></div>
                          <div className="w-0.5 h-full bg-gray-200 mt-2"></div>
                        </div>

                        {/* 内容 */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center space-x-1 sm:space-x-2">
                              <Badge variant="secondary" className="text-xs">
                                {formatDate(entry.timestamp)}
                              </Badge>
                              <span className="text-xs sm:text-sm text-gray-500">
                                {formatTime(entry.timestamp)}
                              </span>
                            </div>
                            <div className="flex items-center space-x-1">
                              {entry.text_content && (
                                <MessageSquare className="h-3 w-3 sm:h-4 sm:w-4 text-gray-400" />
                              )}
                              {entry.image_path && (
                                <ImageIcon className="h-3 w-3 sm:h-4 sm:w-4 text-gray-400" />
                              )}
                            </div>
                          </div>

                          {/* 文字内容 */}
                          {entry.text_content && (
                            <p className="text-gray-700 mb-3 leading-relaxed mobile-text">
                              {entry.text_content}
                            </p>
                          )}

                          {/* 图片 */}
                          {entry.image_path && (
                            <div className="mb-3">
                              <img
                                src={`/${entry.image_path}`}
                                alt="日记图片"
                                className="max-w-full h-auto rounded-lg shadow-sm max-h-48 sm:max-h-64 object-cover image-mobile"
                              />
                            </div>
                          )}

                          {/* AI分析 */}
                          {entry.ai_analysis ? (
                            <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg p-2 sm:p-3 border border-purple-100">
                              <div className="flex items-center space-x-1 sm:space-x-2 mb-1 sm:mb-2">
                                <Sparkles className="h-3 w-3 sm:h-4 sm:w-4 text-purple-500" />
                                <span className="text-xs sm:text-sm font-medium text-purple-700">AI理解</span>
                              </div>
                              <div className="text-xs sm:text-sm text-purple-600 leading-relaxed ai-analysis-content">
                                {entry.ai_analysis}
                              </div>
                            </div>
                          ) : (entry.text_content || entry.image_path) && (
                            <div className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-lg p-2 sm:p-3 border border-gray-200">
                              <div className="flex items-center space-x-1 sm:space-x-2">
                                {isAnalyzing(entry.id) ? (
                                  <>
                                    <Loader2 className="h-3 w-3 sm:h-4 sm:w-4 text-blue-500 animate-spin" />
                                    <span className="text-xs sm:text-sm font-medium text-blue-700">AI理解中...</span>
                                  </>
                                ) : (
                                  <>
                                    <Sparkles className="h-3 w-3 sm:h-4 sm:w-4 text-gray-400" />
                                    <span className="text-xs sm:text-sm font-medium text-gray-500">等待AI分析</span>
                                  </>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

export default DiaryTimeline

