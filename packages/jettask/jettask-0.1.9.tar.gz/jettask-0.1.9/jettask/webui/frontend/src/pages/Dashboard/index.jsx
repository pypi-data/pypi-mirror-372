import React, { useState, useEffect, useRef, useCallback } from 'react'
import { Row, Col, Card, Statistic, Space, Button, DatePicker, message, Spin } from 'antd'
import { 
  RocketOutlined, 
  TeamOutlined, 
  AppstoreOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
  ClockCircleOutlined
} from '@ant-design/icons'
import dayjs from 'dayjs'
import StatsCard from '../../components/common/StatsCard'
import QueueChart from '../../components/charts/QueueChart'
import WorkerChart from '../../components/charts/WorkerChart'
import { fetchGlobalStats, fetchQueues, connectWebSocket } from '../../services/api'
import './index.css'

const { RangePicker } = DatePicker

const Dashboard = () => {
  // 状态管理
  const [loading, setLoading] = useState(true)
  const [globalStats, setGlobalStats] = useState({
    total_workers: 0,
    online_workers: 0,
    total_queues: 0,
    active_queues: 0,
    total_tasks: 0,
    pending_tasks: 0,
    running_tasks: 0,
    completed_tasks: 0,
    failed_tasks: 0
  })
  const [queues, setQueues] = useState([])
  const [workers, setWorkers] = useState([])
  const [connectionStatus, setConnectionStatus] = useState('disconnected')
  
  // 图表时间范围
  const [chartTimeRange, setChartTimeRange] = useState('1h')
  const [customTimeRange, setCustomTimeRange] = useState(null)
  
  // WebSocket 引用
  const wsRef = useRef(null)

  // 时间范围选项
  const timeRangeOptions = [
    { label: '15分钟', value: '15m' },
    { label: '30分钟', value: '30m' },
    { label: '1小时', value: '1h' },
    { label: '3小时', value: '3h' },
    { label: '6小时', value: '6h' },
    { label: '12小时', value: '12h' },
    { label: '24小时', value: '24h' },
    { label: '3天', value: '3d' },
    { label: '7天', value: '7d' },
  ]

  // 获取数据
  const fetchData = useCallback(async () => {
    try {
      setLoading(true)
      
      // 获取全局统计
      const stats = await fetchGlobalStats()
      setGlobalStats(stats)
      
      // 获取队列列表
      const queuesData = await fetchQueues()
      setQueues(queuesData.queues || [])
      
    } catch (error) {
      console.error('Failed to fetch data:', error)
      message.error('获取数据失败')
    } finally {
      setLoading(false)
    }
  }, [])

  // WebSocket 连接
  const setupWebSocket = useCallback(() => {
    const ws = connectWebSocket({
      onOpen: () => {
        setConnectionStatus('connected')
        message.success('实时连接已建立')
      },
      onMessage: (data) => {
        // 处理实时数据更新
        if (data.globalStats) {
          setGlobalStats(data.globalStats)
        }
        if (data.workers) {
          const allWorkers = []
          Object.entries(data.workers).forEach(([queueName, queueWorkers]) => {
            queueWorkers.forEach(worker => {
              allWorkers.push({ ...worker, queue: queueName })
            })
          })
          setWorkers(allWorkers)
        }
      },
      onClose: () => {
        setConnectionStatus('disconnected')
        message.warning('实时连接已断开')
      },
      onError: () => {
        setConnectionStatus('error')
      }
    })
    
    wsRef.current = ws
    return ws
  }, [])

  // 组件挂载时初始化
  useEffect(() => {
    fetchData()
    const ws = setupWebSocket()
    
    // 设置定时刷新
    const refreshInterval = setInterval(fetchData, 30000) // 30秒刷新一次
    
    return () => {
      clearInterval(refreshInterval)
      if (ws) {
        ws.close()
      }
    }
  }, [fetchData, setupWebSocket])

  // 处理时间范围变化
  const handleTimeRangeChange = (value) => {
    setChartTimeRange(value)
    setCustomTimeRange(null)
  }

  const handleCustomTimeRangeChange = (dates) => {
    if (dates) {
      setCustomTimeRange(dates)
      setChartTimeRange('custom')
    }
  }

  // 渲染统计卡片
  const renderStatsCards = () => {
    const statsData = [
      {
        title: 'Workers',
        value: globalStats.online_workers,
        total: globalStats.total_workers,
        icon: <TeamOutlined />,
        color: '#52c41a',
        suffix: `/ ${globalStats.total_workers}`,
        trend: globalStats.online_workers > 0 ? 'up' : 'down'
      },
      {
        title: '活跃队列',
        value: globalStats.active_queues,
        total: globalStats.total_queues,
        icon: <AppstoreOutlined />,
        color: '#1890ff',
        suffix: `/ ${globalStats.total_queues}`,
      },
      {
        title: '运行中任务',
        value: globalStats.running_tasks,
        icon: <SyncOutlined spin />,
        color: '#faad14',
      },
      {
        title: '待处理任务',
        value: globalStats.pending_tasks,
        icon: <ClockCircleOutlined />,
        color: '#13c2c2',
      },
      {
        title: '已完成',
        value: globalStats.completed_tasks,
        icon: <CheckCircleOutlined />,
        color: '#52c41a',
        precision: 0,
      },
      {
        title: '失败任务',
        value: globalStats.failed_tasks,
        icon: <CloseCircleOutlined />,
        color: '#ff4d4f',
        precision: 0,
      },
    ]

    return statsData.map((stat, index) => (
      <Col xs={24} sm={12} md={8} lg={4} key={index}>
        <StatsCard {...stat} />
      </Col>
    ))
  }

  return (
    <div className="dashboard-container">
      <Spin spinning={loading} size="large">
        {/* 统计概览 */}
        <Row gutter={[16, 16]} className="stats-row">
          {renderStatsCards()}
        </Row>

        {/* 图表区域 */}
        <Row gutter={[16, 16]} className="charts-row">
          <Col xs={24} lg={16}>
            <Card 
              className="chart-card"
              title="队列处理趋势"
              extra={
                <Space>
                  <div className="time-range-selector">
                    {timeRangeOptions.map(option => (
                      <Button
                        key={option.value}
                        type={chartTimeRange === option.value ? 'primary' : 'text'}
                        size="small"
                        onClick={() => handleTimeRangeChange(option.value)}
                      >
                        {option.label}
                      </Button>
                    ))}
                  </div>
                  <RangePicker
                    showTime
                    size="small"
                    value={customTimeRange}
                    onChange={handleCustomTimeRangeChange}
                    placeholder={['开始时间', '结束时间']}
                  />
                </Space>
              }
            >
              <QueueChart 
                queues={queues}
                timeRange={chartTimeRange}
                customTimeRange={customTimeRange}
                mode="trend"  // 使用趋势图模式
                loading={loading}
              />
            </Card>
          </Col>
          
          <Col xs={24} lg={8}>
            <Card 
              className="chart-card"
              title="Worker 分布"
            >
              <WorkerChart workers={workers} />
            </Card>
          </Col>
        </Row>

        {/* 队列状态表格 */}
        <Row gutter={[16, 16]} className="table-row">
          <Col span={24}>
            <Card 
              className="table-card"
              title="队列状态"
              extra={
                <Button 
                  type="link" 
                  onClick={() => window.location.href = '/queues'}
                >
                  查看全部
                </Button>
              }
            >
              {/* 这里可以添加队列表格组件 */}
            </Card>
          </Col>
        </Row>
      </Spin>
    </div>
  )
}

export default Dashboard