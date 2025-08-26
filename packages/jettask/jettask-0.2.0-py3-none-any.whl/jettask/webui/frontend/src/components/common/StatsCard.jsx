import React from 'react';
import { Card, Statistic } from 'antd';

const StatsCard = ({ title, value, icon, prefix, suffix, valueStyle }) => {
  return (
    <Card>
      <Statistic
        title={title}
        value={value}
        prefix={icon}
        suffix={suffix}
        valueStyle={valueStyle}
      />
    </Card>
  );
};

export default StatsCard;