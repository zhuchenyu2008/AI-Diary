import { useState, useRef } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Card, CardContent } from '@/components/ui/card.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Camera, Send, X, Loader2, Upload } from 'lucide-react'
import { motion } from 'framer-motion'

const DiaryInput = ({ onEntryCreated }) => {
  const [textContent, setTextContent] = useState('')
  const [selectedImage, setSelectedImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const fileInputRef = useRef(null)
  const cameraInputRef = useRef(null)

  const handleImageSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      processImageFile(file)
    }
  }

  const handleCameraCapture = (e) => {
    const file = e.target.files[0]
    if (file) {
      processImageFile(file)
    }
  }

  const processImageFile = (file) => {
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

  const removeImage = () => {
    setSelectedImage(null)
    setImagePreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
    if (cameraInputRef.current) {
      cameraInputRef.current.value = ''
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
    <Card className="sticky top-4 z-10 shadow-lg card-mobile">
      <CardContent className="p-3 sm:p-4">
        <form onSubmit={handleSubmit} className="input-group">
          {/* 文字输入 */}
          <Textarea
            value={textContent}
            onChange={(e) => setTextContent(e.target.value)}
            placeholder="记录此刻的想法..."
            className="min-h-[80px] sm:min-h-[100px] resize-none border-gray-200 focus:border-indigo-300 focus:ring-indigo-200 mobile-input"
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
                className="w-full max-h-48 sm:max-h-64 object-cover rounded-lg border border-gray-200 image-mobile"
              />
              <Button
                type="button"
                variant="destructive"
                size="sm"
                className="absolute top-2 right-2 touch-button"
                onClick={removeImage}
              >
                <X className="h-3 w-3 sm:h-4 sm:w-4" />
              </Button>
            </motion.div>
          )}

          {/* 错误提示 */}
          {error && (
            <Alert variant="destructive">
              <AlertDescription className="mobile-text">{error}</AlertDescription>
            </Alert>
          )}

          {/* 操作按钮 */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
            <div className="mobile-button-group">
              {/* 文件上传输入 */}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageSelect}
                className="hidden"
              />
              
              {/* 拍照输入 */}
              <input
                ref={cameraInputRef}
                type="file"
                accept="image/*"
                capture="environment"
                onChange={handleCameraCapture}
                className="hidden"
              />
              
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => cameraInputRef.current?.click()}
                disabled={loading}
                className="text-indigo-600 border-indigo-200 hover:bg-indigo-50 touch-button flex-1 sm:flex-none"
              >
                <Camera className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2" />
                <span className="mobile-text">拍照</span>
              </Button>
              
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => fileInputRef.current?.click()}
                disabled={loading}
                className="text-indigo-600 border-indigo-200 hover:bg-indigo-50 touch-button flex-1 sm:flex-none"
              >
                <Upload className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2" />
                <span className="mobile-text">上传图片</span>
              </Button>
              
              {textContent && (
                <span className="text-xs text-gray-500 self-center sm:ml-2">
                  {textContent.length}/1000
                </span>
              )}
            </div>

            <Button
              type="submit"
              disabled={loading || (!textContent.trim() && !selectedImage)}
              className="bg-indigo-600 hover:bg-indigo-700 touch-button button-mobile"
            >
              {loading ? (
                <>
                  <Loader2 className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2 animate-spin" />
                  <span className="mobile-text">发送中...</span>
                </>
              ) : (
                <>
                  <Send className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2" />
                  <span className="mobile-text">发送</span>
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

