'use client';

import React from 'react';
import ReactECharts from 'echarts-for-react';

interface EquityChartProps {
  data: { timestamp: string; equity: number }[];
}

export const EquityChart: React.FC<EquityChartProps> = ({ data }) => {
  const dates = data.map((d) => d.timestamp);
  const values = data.map((d) => d.equity);

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#0c0c0f',
      borderColor: '#1e1e24',
      textStyle: { color: '#fafafa' },
      axisPointer: { type: 'cross' }
    },
    grid: {
      left: '3%',
      right: '3%',
      bottom: '3%',
      top: '10%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: '#27272a' } },
      axisLabel: { color: '#a1a1aa' },
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#27272a' } },
      axisLabel: { color: '#a1a1aa' },
      splitLine: { lineStyle: { color: '#1e1e24' } },
    },
    series: [
      {
        name: 'Equity',
        type: 'line',
        data: values,
        smooth: true,
        showSymbol: false,
        lineStyle: { color: '#3b82f6', width: 3 },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
              { offset: 1, color: 'rgba(59, 130, 246, 0.0)' }
            ]
          }
        }
      }
    ]
  };

  return <ReactECharts option={option} style={{ height: '350px', width: '100%' }} />;
};

interface FeatureImportanceChartProps {
  importances: Record<string, number>;
}

export const FeatureImportanceChart: React.FC<FeatureImportanceChartProps> = ({ importances }) => {
  // Sort and take top 10 features
  const sorted = Object.entries(importances)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8);

  const names = sorted.map((s) => s[0]).reverse();
  const values = sorted.map((s) => s[1] * 100).reverse(); // as percentage

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: '#0c0c0f',
      borderColor: '#1e1e24',
      textStyle: { color: '#fafafa' },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '5%',
      containLabel: true,
    },
    xAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#27272a' } },
      axisLabel: { color: '#a1a1aa' },
      splitLine: { lineStyle: { color: '#1e1e24' } },
    },
    yAxis: {
      type: 'category',
      data: names,
      axisLine: { lineStyle: { color: '#27272a' } },
      axisLabel: { color: '#a1a1aa' },
    },
    series: [
      {
        name: 'Importance (%)',
        type: 'bar',
        data: values,
        itemStyle: {
          color: '#3b82f6',
          borderRadius: [0, 4, 4, 0]
        }
      }
    ]
  };

  return <ReactECharts option={option} style={{ height: '300px', width: '100%' }} />;
};

interface WinLossProps {
  wins: number;
  losses: number;
}

export const WinLossChart: React.FC<WinLossProps> = ({ wins, losses }) => {
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#0c0c0f',
      borderColor: '#1e1e24',
      textStyle: { color: '#fafafa' },
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: { color: '#a1a1aa' }
    },
    series: [
      {
        name: 'Trades',
        type: 'pie',
        radius: '70%',
        data: [
          { value: wins, name: 'Wins', itemStyle: { color: '#10b981' } },
          { value: losses, name: 'Losses', itemStyle: { color: '#ef4444' } }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
          show: true,
          color: '#fafafa'
        }
      }
    ]
  };

  return <ReactECharts option={option} style={{ height: '220px', width: '100%' }} />;
};
