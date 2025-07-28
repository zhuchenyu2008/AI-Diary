import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Calendar, ChevronLeft, ChevronRight, BookOpen, Sparkles } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

const HistoryView = () => {
  const [summaries, setSummaries] = useState([])
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [selectedSummary, setSelectedSummary] = useState(null)

  useEffect(() => {
    fetchSummaries(currentPage)
  }, [currentPage])

  const fetchSummaries = async (page = 1) => {
    setLoading(true)
    try {
      const response = await fetch(`/api/diary/summaries?page=${page}&per_page=10`)
      const data = await response.json()
      
      if (data.success) {
        setSummaries(data.summaries)
        setTotalPages(data.pagination.pages)
      }
    } catch (error) {
      console.error('获取历史记录失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long'
    })
  }

  const formatShortDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN', {
      month: 'short',
      day: 'numeric'
    })
  }

  if (loading && summaries.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-500">加载中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
          <BookOpen className="h-6 w-6 mr-2 text-indigo-600" />
          历史日记
        </h2>
      </div>

      {summaries.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <Calendar className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p className="text-gray-500">还没有历史日记</p>
            <p className="text-sm text-gray-400 mt-2">每天结束后会自动生成日记总结</p>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* 日记列表 */}
          <div className="grid gap-4">
            <AnimatePresence>
              {summaries.map((summary, index) => (
                <motion.div
                  key={summary.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card 
                    className="cursor-pointer hover:shadow-md transition-all duration-200 hover:border-indigo-200"
                    onClick={() => setSelectedSummary(summary)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <Badge variant="outline" className="text-indigo-600 border-indigo-200">
                              {formatShortDate(summary.date)}
                            </Badge>
                            <span className="text-sm text-gray-500">
                              {summary.entry_count} 条记录
                            </span>
                          </div>
                          <p className="text-gray-700 line-clamp-3 leading-relaxed">
                            {summary.summary_content}
                          </p>
                        </div>
                        <ChevronRight className="h-5 w-5 text-gray-400 ml-4 flex-shrink-0" />
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          {/* 分页 */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              
              <span className="text-sm text-gray-600">
                第 {currentPage} 页，共 {totalPages} 页
              </span>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}
        </>
      )}

      {/* 详情弹窗 */}
      <AnimatePresence>
        {selectedSummary && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={() => setSelectedSummary(null)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              <CardHeader className="border-b">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center">
                      <Sparkles className="h-5 w-5 mr-2 text-indigo-600" />
                      {formatDate(selectedSummary.date)}
                    </CardTitle>
                    <p className="text-sm text-gray-500 mt-1">
                      {selectedSummary.entry_count} 条记录
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedSummary(null)}
                  >
                    ×
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="p-6 overflow-y-auto max-h-[60vh]">
                <div className="prose prose-gray max-w-none">
                  <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {selectedSummary.summary_content}
                  </p>
                </div>
              </CardContent>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default HistoryView

