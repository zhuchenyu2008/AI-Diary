import { useState, useRef } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Card, CardContent } from '@/components/ui/card.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Camera, Send, X, Loader2 } from 'lucide-react'
import { motion } from 'framer-motion'

const DiaryInput = ({ onEntryCreated }) => {
  const [textContent, setTextContent] = useState('')
  const [selectedImage, setSelectedImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const fileInputRef = useRef(null)

  const handleImageSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      // 检查文件类型
      if (!file.type.startsWith('image/')) {
        setError('请选择图片文件')
        return
      }
      
      // 检查文件大小 (16MB)
      if (file.size > 16 * 1024 * 1024) {
        setError('图片文件不能超过16MB')
        return
      }

      setSelectedImage(file)
      
      // 创建预览
      const reader = new FileReader()
      reader.onload = (e) => {
        setImagePreview(e.target.result)
      }
      reader.readAsDataURL(file)
      setError('')
    }
  }

  const removeImage = () => {
    setSelectedImage(null)
    setImagePreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!textContent.trim() && !selectedImage) {
      setError('请输入文字或选择图片')
      return
    }

    setLoading(true)
    setError('')

    try {
      const formData = new FormData()
      if (textContent.trim()) {
        formData.append('text_content', textContent.trim())
      }
      if (selectedImage) {
        formData.append('image', selectedImage)
      }

      const response = await fetch('/api/diary/entries', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (data.success) {
        // 清空表单
        setTextContent('')
        removeImage()
        
        // 通知父组件刷新
        if (onEntryCreated) {
          onEntryCreated(data.entry)
        }
      } else {
        setError(data.message || '创建失败')
      }
    } catch (err) {
      setError('网络错误，请重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="sticky top-4 z-10 shadow-lg">
      <CardContent className="p-4">
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 文字输入 */}
          <Textarea
            value={textContent}
            onChange={(e) => setTextContent(e.target.value)}
            placeholder="记录此刻的想法..."
            className="min-h-[100px] resize-none border-gray-200 focus:border-indigo-300 focus:ring-indigo-200"
            maxLength={1000}
          />

          {/* 图片预览 */}
          {imagePreview && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="relative"
            >
              <img
                src={imagePreview}
                alt="预览"
                className="w-full max-h-64 object-cover rounded-lg border border-gray-200"
              />
              <Button
                type="button"
                variant="destructive"
                size="sm"
                className="absolute top-2 right-2"
                onClick={removeImage}
              >
                <X className="h-4 w-4" />
              </Button>
            </motion.div>
          )}

          {/* 错误提示 */}
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* 操作按钮 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageSelect}
                className="hidden"
              />
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => fileInputRef.current?.click()}
                disabled={loading}
                className="text-indigo-600 border-indigo-200 hover:bg-indigo-50"
              >
                <Camera className="h-4 w-4 mr-2" />
                {selectedImage ? '更换图片' : '添加图片'}
              </Button>
              
              {textContent && (
                <span className="text-xs text-gray-500">
                  {textContent.length}/1000
                </span>
              )}
            </div>

            <Button
              type="submit"
              disabled={loading || (!textContent.trim() && !selectedImage)}
              className="bg-indigo-600 hover:bg-indigo-700"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  发送中...
                </>
              ) : (
                <>
                  <Send className="h-4 w-4 mr-2" />
                  发送
                </>
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}

export default DiaryInput

