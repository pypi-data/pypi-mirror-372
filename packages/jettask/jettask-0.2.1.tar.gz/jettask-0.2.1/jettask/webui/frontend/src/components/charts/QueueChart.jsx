import React, { useState, useEffect } from 'react';
import { Card, Empty, Tabs } from 'antd';
import { Column } from '@ant-design/plots';
import QueueTrendChart from './QueueTrendChart';
import { fetchQueueTrend } from '../../services/queueTrend';

const { TabPane } = Tabs;

const QueueChart = ({ 
  data, 
  loading, 
  queues = [], 
  timeRange = '1h', 
  customTimeRange = null,
  mode = 'distribution' // 'distribution' | 'trend'
}) => {
  const [trendData, setTrendData] = useState([]);
  const [activeTab, setActiveTab] = useState('trend');

  // 获取趋势数据
  useEffect(() => {
    if (queues && queues.length > 0 && (mode === 'trend' || activeTab === 'trend')) {
      // 获取队列名称列表
      const queueNames = queues.map(q => q.name || q);
      
      // 从API获取趋势数据
      const loadTrendData = async () => {
        try {
          const data = await fetchQueueTrend(timeRange, queueNames, customTimeRange);
          setTrendData(data);
        } catch (error) {
          console.error('Failed to load trend data:', error);
          // 如果失败，使用空数据
          setTrendData([]);
        }
      };
      
      loadTrendData();
    }
  }, [queues, timeRange, customTimeRange, mode, activeTab]);

  // 柱状图配置
  const columnConfig = {
    data: data || [],
    xField: 'name',
    yField: 'value',
    label: {
      position: 'middle',
      style: {
        fill: '#FFFFFF',
        opacity: 0.6,
      },
    },
    xAxis: {
      label: {
        autoHide: true,
        autoRotate: false,
      },
    },
    meta: {
      name: { alias: '队列' },
      value: { alias: '任务数' },
    },
  };

  // 如果指定为趋势模式，直接返回趋势图
  if (mode === 'trend') {
    return (
      <QueueTrendChart 
        data={trendData}
        loading={loading}
        timeRange={timeRange}
      />
    );
  }

  // 如果没有指定模式，显示标签页切换
  if (!mode || mode === 'both') {
    return (
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab="处理趋势" key="trend">
          <QueueTrendChart 
            data={trendData}
            loading={loading}
            timeRange={timeRange}
          />
        </TabPane>
        <TabPane tab="队列分布" key="distribution">
          {data && data.length > 0 ? (
            <Column {...columnConfig} />
          ) : (
            <Empty description="暂无数据" />
          )}
        </TabPane>
      </Tabs>
    );
  }

  // 默认显示分布图
  return (
    <Card title="队列任务分布" loading={loading}>
      {data && data.length > 0 ? (
        <Column {...columnConfig} />
      ) : (
        <Empty description="暂无数据" />
      )}
    </Card>
  );
};

export default QueueChart;