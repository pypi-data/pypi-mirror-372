import axios from 'axios';

// 智能获取 API 基础 URL
const getApiBaseUrl = () => {
  // 在开发环境中使用 localhost
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    
    // 如果是生产环境，使用相同的域名
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
      return `${protocol}//${hostname}:8000/api`;
    }
  }
  
  // 默认开发环境
  return 'http://localhost:8000/api';
};

// 智能获取 WebSocket URL
const getWsBaseUrl = () => {
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    
    // 如果是生产环境，使用相同的域名
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
      return `${wsProtocol}//${hostname}:8000/ws`;
    }
  }
  
  // 默认开发环境
  return 'ws://localhost:8000/ws';
};

const API_BASE_URL = getApiBaseUrl();
const WS_BASE_URL = getWsBaseUrl();

// 创建 axios 实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// 获取全局统计信息
export const fetchGlobalStats = async () => {
  try {
    const response = await api.get('/stats');
    return response.data.data;
  } catch (error) {
    console.error('Failed to fetch global stats:', error);
    throw error;
  }
};

// 获取队列列表
export const fetchQueues = async () => {
  try {
    const response = await api.get('/queues');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch queues:', error);
    throw error;
  }
};

// 获取队列时间线数据
export const fetchQueueTimeline = async (params) => {
  try {
    const response = await api.post('/queue-timeline', params);
    // 处理数据，确保不包含填充的空值
    const data = response.data.data || response.data || [];
    return {
      ...response.data,
      data: data.filter(item => item.value > 0) // 只返回有实际值的数据点
    };
  } catch (error) {
    console.error('Failed to fetch queue timeline:', error);
    throw error;
  }
};

// WebSocket 连接
export const connectWebSocket = (onMessage, onError) => {
  const ws = new WebSocket(`${WS_BASE_URL}/monitor`);
  
  ws.onopen = () => {
    console.log('WebSocket connected');
  };
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    if (onError) onError(error);
  };
  
  ws.onclose = () => {
    console.log('WebSocket disconnected');
  };
  
  return ws;
};

export default api;