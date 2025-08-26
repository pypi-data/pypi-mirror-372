import { useState, useEffect } from 'react';
import { Line } from '@ant-design/plots';
import { Empty, Spin } from 'antd';
import dayjs from 'dayjs';

const QueueTrendChart = ({ data = [], loading = false }) => {
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    if (data && data.length > 0) {
      // 处理数据，转换为Date对象并按时间排序
      const processedData = data.map(item => ({
        ...item,
        date: new Date(item.time), // 使用date字段，与示例保持一致
        value: item.value || 0,
        queue: item.queue
      }));

      // 按时间排序确保连线正确
      processedData.sort((a, b) => a.date.getTime() - b.date.getTime());

      setChartData(processedData);
    }
  }, [data]);

  // 图表配置 - 参考Ant Design Charts示例
  const config = {
    data: chartData,
    xField: (d) => d.date,  // 返回Date对象，让图表库自动处理
    yField: 'value',
    seriesField: 'queue', // 如果有多个队列，按队列分组
    
    // 连接空值配置
    connectNulls: {
      connect: true,
      connectStroke: '#ccc',
    },
    
    // X轴会自动优化显示，不需要手动设置formatter
    xAxis: {
      type: 'time',
      nice: true,
    },
    
    // Y轴配置
    yAxis: {
      label: {
        formatter: (v) => {
          // 格式化数字显示
          if (v >= 1000000) {
            return `${(v / 1000000).toFixed(1)}M`;
          } else if (v >= 1000) {
            return `${(v / 1000).toFixed(1)}K`;
          }
          return String(v);
        }
      }
    },
    
    // 悬浮提示配置
    tooltip: {
      showTitle: true,
      title: (title) => {
        // 格式化时间显示
        return dayjs(title).format('YYYY-MM-DD HH:mm:ss');
      },
      formatter: (datum) => {
        return {
          name: datum.queue || '任务数',
          value: datum.value.toLocaleString(), // 添加千分位分隔符
        };
      },
    },
    
    // 平滑曲线
    smooth: true,
    
    // 动画配置
    animation: {
      appear: {
        animation: 'path-in',
        duration: 1000,
      },
    },
    
    // 响应式配置
    autoFit: true,
    height: 300,
    
    // 主题颜色
    color: ['#5B8FF9', '#61DDAA', '#65789B', '#F6BD16', '#7262FD'],
  };

  // 空数据处理
  if (!loading && (!chartData || chartData.length === 0)) {
    return (
      <div style={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Empty description="暂无数据" />
      </div>
    );
  }

  // 加载状态
  if (loading) {
    return (
      <div style={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  return <Line {...config} />;
};

export default QueueTrendChart;