import axios from 'axios';

// 在 React 应用中，环境变量需要以 REACT_APP_ 开头
// 使用 window.location 作为后备方案
const getApiBaseUrl = () => {
  // 尝试从环境变量获取（Create React App 会在构建时注入）
  if (typeof window !== 'undefined' && window.REACT_APP_API_URL) {
    return window.REACT_APP_API_URL;
  }
  
  // 如果是生产环境，使用相同的域名和端口
  if (typeof window !== 'undefined' && window.location.hostname !== 'localhost') {
    return `${window.location.protocol}//${window.location.hostname}:8001`;
  }
  
  // 默认使用 localhost
  return 'http://localhost:8001';
};

const API_BASE_URL = getApiBaseUrl();

/**
 * 获取队列趋势数据
 * @param {string} timeRange - 时间范围 (15m, 30m, 1h, 3h, 6h, 12h, 24h, 3d, 7d)
 * @param {Array} queues - 队列名称列表
 * @param {Object} customTimeRange - 自定义时间范围 {start: Date, end: Date}
 * @returns {Promise<Array>} 趋势数据
 */
export const fetchQueueTrend = async (timeRange = '1h', queues = [], customTimeRange = null) => {
  try {
    const params = {
      range: timeRange,
      queues: queues.join(',')
    };

    // 如果有自定义时间范围
    if (customTimeRange) {
      params.start = customTimeRange[0].valueOf();
      params.end = customTimeRange[1].valueOf();
    }

    const response = await axios.get(`${API_BASE_URL}/api/queue-trend`, { params });
    
    // 处理响应数据 - 后端现在直接返回时间线数据
    const data = response.data.data || response.data || [];
    
    // 转换数据格式，保持时间字段为ISO字符串，让组件转换为Date对象
    return data.map(item => ({
      time: item.time || item.timestamp, // 保持原始时间字符串
      value: item.value || item.count || 0,
      queue: item.queue || item.queue_name
    }));
  } catch (error) {
    console.error('Failed to fetch queue trend:', error);
    
    // 如果API失败，返回模拟数据
    return generateMockTrendData(timeRange, queues);
  }
};

/**
 * 生成模拟趋势数据（用于开发和测试）
 */
const generateMockTrendData = (timeRange, queues) => {
  const now = Date.now();
  const points = getDataPoints(timeRange);
  const interval = getIntervalByRange(timeRange);
  
  const data = [];
  
  // 为每个队列生成数据
  queues.slice(0, 3).forEach(queue => {
    // 生成基础值和趋势
    const baseValue = Math.floor(Math.random() * 50) + 20;
    const trend = Math.random() > 0.5 ? 1 : -1;
    
    for (let i = 0; i < points; i++) {
      // 添加一些随机波动
      const variation = Math.sin(i / 5) * 10 + Math.random() * 10 - 5;
      const value = Math.max(0, baseValue + trend * i * 0.5 + variation);
      
      data.push({
        time: now - (points - i - 1) * interval,
        value: Math.floor(value),
        queue: queue.name || queue,
        originalTime: new Date(now - (points - i - 1) * interval).toISOString()
      });
    }
  });
  
  return data;
};

/**
 * 根据时间范围获取数据点数量
 */
const getDataPoints = (range) => {
  const points = {
    '15m': 15,   // 每分钟一个点
    '30m': 30,   // 每分钟一个点
    '1h': 30,    // 每2分钟一个点
    '3h': 36,    // 每5分钟一个点
    '6h': 36,    // 每10分钟一个点
    '12h': 36,   // 每20分钟一个点
    '24h': 48,   // 每30分钟一个点
    '3d': 36,    // 每2小时一个点
    '7d': 42,    // 每4小时一个点
  };
  return points[range] || 30;
};

/**
 * 根据时间范围获取数据间隔（毫秒）
 */
const getIntervalByRange = (range) => {
  const intervals = {
    '15m': 60 * 1000,           // 1分钟
    '30m': 60 * 1000,           // 1分钟
    '1h': 2 * 60 * 1000,        // 2分钟
    '3h': 5 * 60 * 1000,        // 5分钟
    '6h': 10 * 60 * 1000,       // 10分钟
    '12h': 20 * 60 * 1000,      // 20分钟
    '24h': 30 * 60 * 1000,      // 30分钟
    '3d': 2 * 60 * 60 * 1000,   // 2小时
    '7d': 4 * 60 * 60 * 1000,   // 4小时
  };
  return intervals[range] || 60 * 1000;
};

/**
 * 获取队列统计信息
 */
export const fetchQueueStats = async (queueName, timeRange = '1h') => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/queue/${queueName}/stats`, {
      params: { range: timeRange }
    });
    
    return response.data;
  } catch (error) {
    console.error('Failed to fetch queue stats:', error);
    return {
      total: 0,
      pending: 0,
      running: 0,
      completed: 0,
      failed: 0,
      avgProcessTime: 0,
      throughput: 0
    };
  }
};