import React, { useState, useEffect, useRef } from 'react';
import { Card, Select, DatePicker, Space, Spin, message, Button } from 'antd';
import { Line } from '@ant-design/plots';
import { G2 } from "@ant-design/plots";



import { ReloadOutlined } from '@ant-design/icons';
import { useLoading } from '../contexts/LoadingContext';

import dayjs from 'dayjs';
import axios from 'axios';

const { RangePicker } = DatePicker;
const { ChartEvent } = G2;

// 时间范围选项
const TIME_RANGES = [
  { label: '最近15分钟', value: '15m' },
  { label: '最近30分钟', value: '30m' },
  { label: '最近1小时', value: '1h' },
  { label: '最近3小时', value: '3h' },
  { label: '最近6小时', value: '6h' },
  { label: '最近12小时', value: '12h' },
  { label: '最近24小时', value: '24h' },
  { label: '最近7天', value: '7d' },
  { label: '最近30天', value: '30d' },
];

function QueueMonitor() {
  const { setLoading: setGlobalLoading } = useLoading();
  const [loading, setLoading] = useState(false);
  const [queues, setQueues] = useState([]);
  const [selectedQueues, setSelectedQueues] = useState([]);
  const [timeRange, setTimeRange] = useState('15m');
  const [customTimeRange, setCustomTimeRange] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [granularity, setGranularity] = useState('');
  const [sliderValues, setSliderValues] = useState([0, 1]);

  // 用于防抖的 ref
  const fetchTimeoutRef = useRef(null);
  const isBrushingRef = useRef(false);

  // 获取队列列表
  const fetchQueues = async () => {
    try {
      const response = await axios.get('/api/queues');
      if (response.data.success) {
        const queueList = response.data.data;
        setQueues(queueList);
        // 默认选择前3个队列
        if (selectedQueues.length === 0 && queueList.length > 0) {
          setSelectedQueues(queueList.slice(0, 10));
        }
      }
    } catch (error) {
      message.error('获取队列列表失败');
      console.error('Failed to fetch queues:', error);
    }
  };

  // 获取队列趋势数据
  const fetchQueueTimeline = async () => {
    if (selectedQueues.length === 0) {
      return;
    }

    setLoading(true);
    setGlobalLoading(true, '加载数据中...');
    try {
      const params = {
        queues: selectedQueues,
        time_range: timeRange,
      };

      // 如果有自定义时间范围
      if (customTimeRange) {
        params.start_time = customTimeRange[0].toISOString();
        params.end_time = customTimeRange[1].toISOString();
      }
      console.log('请求参数:', params);

      const response = await axios.post('/api/queue-timeline', params);
      const { data, granularity: dataGranularity } = response.data;

      setChartData(data);
      setGranularity(dataGranularity);
      // 如果是刷选触发，获取新数据后重置 slider 为全范围
      // 这样新数据会完整显示
      setSliderValues([0, 1]);
    } catch (error) {
      message.error('获取队列趋势数据失败');
      console.error('Failed to fetch queue timeline:', error);
    } finally {
      setLoading(false);
      setGlobalLoading(false);
      isBrushingRef.current = false;
    }
  };

  // 初始化
  useEffect(() => {
    fetchQueues();
  }, []);

  // 当选择的队列或时间范围改变时，重新获取数据
  useEffect(() => {
    if (selectedQueues.length > 0) {
      console.log('触发数据更新 - timeRange:', timeRange, 'customTimeRange:', customTimeRange);

      // 清除之前的定时器
      if (fetchTimeoutRef.current) {
        clearTimeout(fetchTimeoutRef.current);
      }

      // 如果是刷选触发的自定义时间范围，延迟一点获取数据
      const delay = isBrushingRef.current ? 300 : 0;
      
      fetchTimeoutRef.current = setTimeout(() => {
        fetchQueueTimeline();
      }, delay);
    }

    // 清理函数
    return () => {
      if (fetchTimeoutRef.current) {
        clearTimeout(fetchTimeoutRef.current);
      }
    };
  }, [selectedQueues, timeRange, customTimeRange]);

  // 处理预设时间范围变化
  const handleTimeRangeChange = (value) => {
    console.log('选择的时间范围:', value);
    setTimeRange(value);
    setCustomTimeRange(null);
  };

  // 处理自定义时间范围变化
  const handleCustomTimeRangeChange = (dates) => {
    if (dates && dates.length === 2) {
      console.log('选择的自定义时间范围:', dates);
      setCustomTimeRange(dates);
      setTimeRange('custom');
    } else {
      setCustomTimeRange(null);
      setTimeRange('15m');
    }
  };

  // 手动刷新
  const handleRefresh = () => {
    fetchQueueTimeline();
  };


  // 图表配置
  const chartConfig = {
    data: chartData,
    xField: (d) => new Date(d.time),
    yField: 'value',
    colorField: 'queue',  // 使用 colorField 替代 seriesField
    smooth: true,
    // 禁用动画以避免错误
    animate: false,
    meta: {
      value: {
        alias: '任务数',
      },
      time: {
        type: 'time',
        alias: '时间',
      },
    },
    scale: {
      time: {
        type: 'time',
      },
      y: { nice: true },
      // 定义不同队列的颜色
      color: {
        range: ['#5B8FF9', '#5AD8A6', '#5D7092', '#F6BD16', '#E8684A', '#6DC8EC', '#9270CA', '#FF9D4D', '#269A99', '#FF99C3']
      }
    },
    point: {
      size: 3,
      shape: 'circle',
    },
    style: {
      lineWidth: 2,
    },
    xAxis: {
      type: 'time',
      label: {
        autoRotate: true,
        formatter: (text) => {
          // text 可能是时间戳或ISO字符串，统一处理
          const date = dayjs(text);
          
          // 根据后端返回的粒度决定显示格式
          switch(granularity) {
            case 'second':
              // 秒级：显示时分秒
              return date.format('HH:mm:ss');
            
            case 'minute':
              // 分钟级：显示时分
              return date.format('HH:mm');
            
            case 'hour':
              // 小时级：显示日期和小时
              return date.format('MM-DD HH:00');
            
            case 'day':
              // 跨天：显示年月日
              return date.format('YYYY-MM-DD');
            
            default:
              // 默认显示日期和小时
              return date.format('MM-DD HH:mm');
          }
        },
      },
    },
    yAxis: {
      label: {
        formatter: (v) => `${v}`,
      },
      title: {
        text: '处理任务数',
        style: {
          fontSize: 14,
        },
      },
    },

    // autoFit: true,
    interaction: {
      brushXFilter: true // 启用横向筛选
    },

    slider: {
      x: {
        values: sliderValues,
      },
    },
    connectNulls: {
      connect: true,
      connectStroke: '#aaa',
    },
    // 监听brush事件，实现框选后自动请求数据
    onReady: (plot) => {
      console.log('图表已准备就绪', plot);

      // 获取所有可用的事件
      const chart = plot.chart;

      chart.on("brush:filter", (e) => {
        console.log('Brush filter 事件:', e);

        // 获取刷选的数据范围
        if (e.data && e.data.selection) {
          const selection = e.data.selection;
          console.log('Selection 数据:', selection);

          // selection[0] 是选中的时间数组
          if (selection && selection[0] && selection[0].length > 0) {
            const selectedTimes = selection[0];

            // 获取选中时间的起止
            const startTime = dayjs(selectedTimes[0]);
            const endTime = dayjs(selectedTimes[selectedTimes.length - 1]);

            console.log('刷选范围:', startTime.format(), endTime.format());

            // 设置刷选标志
            isBrushingRef.current = true;

            // 更新UI状态，这会触发 useEffect 重新获取数据
            setTimeRange('custom');
            setCustomTimeRange([startTime, endTime]);
            
            // 不需要手动更新 slider，fetchQueueTimeline 会处理
          }
        }
      });
    },
  };

  return (
    <Card>
      {/* 控制面板 */}
      <Space size="large" style={{ marginBottom: '24px' }} wrap>
        <div>
          <span style={{ marginRight: '8px' }}>选择队列：</span>
          <Select
            mode="multiple"
            style={{ width: 400 }}
            placeholder="请选择队列"
            value={selectedQueues}
            onChange={setSelectedQueues}
            options={queues.map(q => ({ label: q, value: q }))}
            maxTagCount="responsive"
          />
        </div>

        <div>
          <span style={{ marginRight: '8px' }}>时间范围：</span>
          <Select
            style={{ width: 150 }}
            value={customTimeRange ? 'custom' : timeRange}
            onChange={handleTimeRangeChange}
            options={[...TIME_RANGES, { label: '自定义', value: 'custom', disabled: true }]}
          />
        </div>

        <div>
          <RangePicker
            showTime
            format="YYYY-MM-DD HH:mm:ss"
            value={customTimeRange}
            onChange={handleCustomTimeRangeChange}
            placeholder={['开始时间', '结束时间']}
          />
        </div>

        <Button
          icon={<ReloadOutlined spin={loading} />}
          onClick={handleRefresh}
          disabled={loading}
          type="primary"
        >
          {loading ? '加载中...' : '刷新'}
        </Button>
      </Space>

      {/* 数据粒度提示 */}
      {granularity && (
        <div style={{ marginBottom: '16px', color: '#666' }}>
          数据粒度：{
            granularity === 'second' ? '秒级' :
            granularity === 'minute' ? '分钟级' :
            granularity === 'hour' ? '小时级' :
            granularity === 'day' ? '天级' :
            granularity
          }
        </div>
      )}

      {/* 图表 */}
      <div style={{ height: '500px', position: 'relative' }}>
        {chartData.length > 0 ? (
          <>
            <Line {...chartConfig} />
            {/* {loading && (
              <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'rgba(255, 255, 255, 0.8)',
                zIndex: 1000,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Spin size="large" tip="正在获取选定时间范围的详细数据..." />
              </div>
            )} */}
          </>
        ) : (
          <div style={{
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#999'
          }}>
            {loading ? (
              <Spin size="large" tip="正在加载数据..." />
            ) : (
              selectedQueues.length === 0 ? '请选择队列' : '暂无数据'
            )}
          </div>
        )}
      </div>

      {/* 使用提示 */}
      <div style={{ marginTop: '16px', padding: '12px', background: '#e6f7ff', borderRadius: '4px', border: '1px solid #91d5ff' }}>
        <div style={{ color: '#1890ff', fontSize: '14px', fontWeight: 500 }}>
          💡 操作提示：
        </div>
        <ul style={{ margin: '8px 0 0 20px', color: '#666', fontSize: '13px', paddingLeft: '20px' }}>
          <li>使用鼠标在图表上<strong>按住左键并横向拖动</strong>来刷选时间范围</li>
          <li>刷选完成后，系统会自动获取该时段的详细数据</li>
          <li>数据粒度会根据选中的时间范围自动调整</li>
          <li>点击图表空白处可以取消刷选</li>
        </ul>
      </div>
    </Card>
  );
}

export default QueueMonitor;