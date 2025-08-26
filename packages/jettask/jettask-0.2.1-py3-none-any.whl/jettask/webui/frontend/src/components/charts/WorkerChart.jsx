import React from 'react';
import { Card, Empty } from 'antd';
import { Pie } from '@ant-design/plots';

const WorkerChart = ({ data, loading }) => {
  const chartData = data || [
    { type: '在线', value: 0 },
    { type: '离线', value: 0 },
  ];

  const config = {
    appendPadding: 10,
    data: chartData,
    angleField: 'value',
    colorField: 'type',
    radius: 0.8,
    label: {
      type: 'inner',
      offset: '-30%',
      content: ({ percent }) => `${(percent * 100).toFixed(0)}%`,
      style: {
        fontSize: 14,
        textAlign: 'center',
      },
    },
    interactions: [{ type: 'element-active' }],
  };

  return (
    <Card title="Worker 状态分布" loading={loading}>
      {chartData.some(item => item.value > 0) ? (
        <Pie {...config} />
      ) : (
        <Empty description="暂无数据" />
      )}
    </Card>
  );
};

export default WorkerChart;