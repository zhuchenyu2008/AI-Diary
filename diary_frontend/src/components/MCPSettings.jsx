import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Switch } from '@/components/ui/switch.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Loader2, MapPin, Cloud, Clock, Monitor, Settings, TestTube } from 'lucide-react'
import { motion } from 'framer-motion'

const MCPSettings = ({ onClose }) => {
  const [config, setConfig] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState({})
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [weatherApiKey, setWeatherApiKey] = useState('')

  useEffect(() => {
    loadConfig()
  }, [])

  const loadConfig = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/mcp/servers')
      const data = await response.json()
      
      if (data.success) {
        setConfig(data.config)
        // 查找天气服务器的API密钥状态
        const weatherServer = data.config.servers.find(s => s.name === 'weather')
        if (weatherServer && !weatherServer.api_key_configured) {
          setWeatherApiKey('')
        }
      } else {
        setError(data.message || '加载MCP配置失败')
      }
    } catch (err) {
      setError('网络错误，请重试')
    } finally {
      setLoading(false)
    }
  }

  const updateServerEnabled = async (serverName, enabled) => {
    try {
      const newConfig = {
        enabled_servers: {
          ...Object.fromEntries(config.servers.map(s => [s.name, s.enabled])),
          [serverName]: enabled
        }
      }

      const response = await fetch('/api/mcp/servers/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newConfig)
      })

      const data = await response.json()
      if (data.success) {
        setConfig(data.config)
        setSuccess('配置更新成功')
        setTimeout(() => setSuccess(''), 3000)
      } else {
        setError(data.message || '更新配置失败')
      }
    } catch (err) {
      setError('网络错误，请重试')
    }
  }

  const requestLocationPermission = async () => {
    try {
      if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
          async (position) => {
            // 位置权限获取成功
            const response = await fetch('/api/mcp/permission/location', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({ granted: true })
            })

            const data = await response.json()
            if (data.success) {
              await loadConfig()
              setSuccess('位置权限已授权')
              setTimeout(() => setSuccess(''), 3000)
            }
          },
          (error) => {
            setError('位置权限被拒绝')
          }
        )
      } else {
        setError('浏览器不支持位置服务')
      }
    } catch (err) {
      setError('请求位置权限失败')
    }
  }

  const updateWeatherApiKey = async () => {
    try {
      setSaving(true)
      const response = await fetch('/api/mcp/servers/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          weather_api_key: weatherApiKey
        })
      })

      const data = await response.json()
      if (data.success) {
        setConfig(data.config)
        setSuccess('天气API密钥已保存')
        setTimeout(() => setSuccess(''), 3000)
      } else {
        setError(data.message || '保存API密钥失败')
      }
    } catch (err) {
      setError('网络错误，请重试')
    } finally {
      setSaving(false)
    }
  }

  const testServer = async (serverName) => {
    try {
      setTesting(prev => ({ ...prev, [serverName]: true }))
      const response = await fetch('/api/mcp/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ server: serverName })
      })

      const data = await response.json()
      if (data.success) {
        setSuccess(`${serverName}服务器测试成功`)
        setTimeout(() => setSuccess(''), 3000)
      } else {
        setError(data.message || `${serverName}服务器测试失败`)
      }
    } catch (err) {
      setError('测试失败，请重试')
    } finally {
      setTesting(prev => ({ ...prev, [serverName]: false }))
    }
  }

  const getServerIcon = (serverName) => {
    switch (serverName) {
      case 'time': return <Clock className="h-5 w-5" />
      case 'location': return <MapPin className="h-5 w-5" />
      case 'weather': return <Cloud className="h-5 w-5" />
      case 'system': return <Monitor className="h-5 w-5" />
      default: return <Settings className="h-5 w-5" />
    }
  }

  const getServerStatus = (server) => {
    if (!server.enabled) return { text: '已禁用', color: 'secondary' }
    if (server.requires_permission && !server.permission_granted) return { text: '需要权限', color: 'destructive' }
    if (server.requires_api_key && !server.api_key_configured) return { text: '需要配置', color: 'destructive' }
    return { text: '已启用', color: 'default' }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="mobile-card-spacing"
    >
      <div className="flex items-center justify-between mb-4 sm:mb-6">
        <h2 className="mobile-title font-bold">MCP 设置</h2>
        <Button variant="outline" onClick={onClose} className="touch-button">
          <span className="mobile-text">关闭</span>
        </Button>
      </div>

      <div className="text-xs sm:text-sm text-gray-600 mb-4 sm:mb-6">
        Model Context Protocol (MCP) 为AI提供更多维度的上下文信息，包括时间、位置、天气等。
      </div>

      {error && (
        <Alert variant="destructive" className="mb-4">
          <AlertDescription className="mobile-text">{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="mb-4">
          <AlertDescription className="mobile-text">{success}</AlertDescription>
        </Alert>
      )}

      <div className="mobile-grid gap-3 sm:gap-4">
        {config?.servers?.map((server) => {
          const status = getServerStatus(server)
          
          return (
            <Card key={server.name} className="relative card-mobile">
              <CardHeader className="pb-2 sm:pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 sm:space-x-3">
                    {getServerIcon(server.name)}
                    <div>
                      <CardTitle className="text-base sm:text-lg">{server.name.toUpperCase()} 服务器</CardTitle>
                      <p className="text-xs sm:text-sm text-gray-600">{server.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-1 sm:space-x-2">
                    <Badge variant={status.color} className="text-xs">{status.text}</Badge>
                    <Switch
                      checked={server.enabled}
                      onCheckedChange={(checked) => updateServerEnabled(server.name, checked)}
                    />
                  </div>
                </div>
              </CardHeader>

              <CardContent className="space-y-3 sm:space-y-4">
                {/* 工具列表 */}
                <div>
                  <Label className="text-xs sm:text-sm font-medium">可用工具</Label>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {server.tools.map((tool) => (
                      <Badge key={tool} variant="outline" className="text-xs">
                        {tool}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* 资源列表 */}
                <div>
                  <Label className="text-xs sm:text-sm font-medium">可用资源</Label>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {server.resources.map((resource) => (
                      <Badge key={resource} variant="outline" className="text-xs">
                        {resource}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* 特殊配置 */}
                {server.name === 'location' && server.requires_permission && (
                  <div className="space-y-2">
                    <Label className="text-xs sm:text-sm font-medium">位置权限</Label>
                    {!server.permission_granted ? (
                      <Button
                        size="sm"
                        onClick={requestLocationPermission}
                        className="w-full touch-button"
                      >
                        <MapPin className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2" />
                        <span className="mobile-text">请求位置权限</span>
                      </Button>
                    ) : (
                      <div className="text-xs sm:text-sm text-green-600">✓ 位置权限已授权</div>
                    )}
                  </div>
                )}

                {server.name === 'weather' && server.requires_api_key && (
                  <div className="space-y-2">
                    <Label className="text-xs sm:text-sm font-medium">天气API密钥</Label>
                    <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
                      <Input
                        type="password"
                        placeholder="输入天气API密钥"
                        value={weatherApiKey}
                        onChange={(e) => setWeatherApiKey(e.target.value)}
                        className="flex-1 mobile-input"
                      />
                      <Button
                        size="sm"
                        onClick={updateWeatherApiKey}
                        disabled={saving || !weatherApiKey}
                        className="touch-button button-mobile"
                      >
                        {saving ? (
                          <Loader2 className="h-3 w-3 sm:h-4 sm:w-4 animate-spin" />
                        ) : (
                          <span className="mobile-text">保存</span>
                        )}
                      </Button>
                    </div>
                    {server.api_key_configured && (
                      <div className="text-xs sm:text-sm text-green-600">✓ API密钥已配置</div>
                    )}
                  </div>
                )}

                {/* 测试按钮 */}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => testServer(server.name)}
                  disabled={!server.enabled || testing[server.name]}
                  className="w-full touch-button"
                >
                  {testing[server.name] ? (
                    <>
                      <Loader2 className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2 animate-spin" />
                      <span className="mobile-text">测试中...</span>
                    </>
                  ) : (
                    <>
                      <TestTube className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2" />
                      <span className="mobile-text">测试服务器</span>
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </motion.div>
  )
}

export default MCPSettings

