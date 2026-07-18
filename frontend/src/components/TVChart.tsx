'use client';

import React, { useEffect, useRef } from 'react';
import { 
  createChart, 
  ColorType, 
  CandlestickSeries, 
  LineSeries, 
  HistogramSeries,
  CandlestickData, 
  LineData 
} from 'lightweight-charts';

interface TVChartProps {
  data: {
    timestamp: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }[];
  sma20Data?: { time: string; value: number }[];
  ema9Data?: { time: string; value: number }[];
}

export const TVChart: React.FC<TVChartProps> = ({ data, sma20Data = [], ema9Data = [] }) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);

  useEffect(() => {
    if (!chartContainerRef.current || data.length === 0) return;

    // Handle responsiveness
    const handleResize = () => {
      if (chartRef.current && chartContainerRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    // Format bars for Lightweight Charts (requires { time: 'YYYY-MM-DD' or Unix timestamp, open, high, low, close })
    const formattedCandles: CandlestickData[] = data.map((d) => {
      const dateObj = new Date(d.timestamp);
      const timeVal = Math.floor(dateObj.getTime() / 1000); // Unix timestamp in seconds
      return {
        time: timeVal as any,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
      };
    });

    // Create chart instance
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#0c0c0f' },
        textColor: '#a1a1aa',
      },
      grid: {
        vertLines: { color: '#1e1e24' },
        horzLines: { color: '#1e1e24' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 450,
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
    });

    chartRef.current = chart;

    // Add candlestick series
    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#10b981',
      downColor: '#ef4444',
      borderVisible: false,
      wickUpColor: '#10b981',
      wickDownColor: '#ef4444',
    });
    candlestickSeries.setData(formattedCandles);

    // Add moving averages if data is present
    if (sma20Data.length > 0) {
      const smaSeries = chart.addSeries(LineSeries, {
        color: '#3b82f6',
        lineWidth: 2,
        title: 'SMA 20',
      });
      const formattedSma: LineData[] = sma20Data.map((d) => ({
        time: Math.floor(new Date(d.time).getTime() / 1000) as any,
        value: d.value,
      }));
      smaSeries.setData(formattedSma);
    }

    if (ema9Data.length > 0) {
      const emaSeries = chart.addSeries(LineSeries, {
        color: '#f59e0b',
        lineWidth: 2,
        title: 'EMA 9',
      });
      const formattedEma: LineData[] = ema9Data.map((d) => ({
        time: Math.floor(new Date(d.time).getTime() / 1000) as any,
        value: d.value,
      }));
      emaSeries.setData(formattedEma);
    }

    // Add volume series in pane
    const volumeSeries = chart.addSeries(HistogramSeries, {
      color: '#26a69a',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '', // Overlay over price pane
    });
    
    // Scale volume down so it sits at the bottom 20%
    const formattedVolume = data.map((d) => {
      const dateObj = new Date(d.timestamp);
      const timeVal = Math.floor(dateObj.getTime() / 1000);
      const isUp = d.close >= d.open;
      return {
        time: timeVal as any,
        value: d.volume,
        color: isUp ? 'rgba(16, 185, 129, 0.25)' : 'rgba(239, 68, 68, 0.25)',
      };
    });
    volumeSeries.setData(formattedVolume);

    chart.timeScale().fitContent();

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [data, sma20Data, ema9Data]);

  return (
    <div className="relative w-full rounded-xl overflow-hidden border border-[#1e1e24] bg-[#0c0c0f] p-4">
      <div ref={chartContainerRef} className="w-full h-[450px]" />
    </div>
  );
};
