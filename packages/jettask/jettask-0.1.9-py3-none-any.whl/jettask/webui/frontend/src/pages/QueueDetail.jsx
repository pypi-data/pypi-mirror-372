import React from 'react';
import { useParams } from 'react-router-dom';
import { Card, Descriptions } from 'antd';

function QueueDetail() {
  const { queueName } = useParams();
  
  return (
    <Card title={`队列详情: ${queueName}`}>
      <Descriptions column={1}>
        <Descriptions.Item label="队列名称">{queueName}</Descriptions.Item>
        <Descriptions.Item label="状态">活跃</Descriptions.Item>
      </Descriptions>
    </Card>
  );
}

export default QueueDetail;