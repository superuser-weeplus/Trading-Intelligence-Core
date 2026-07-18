import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface PriceBar {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  spread: number;
}

export interface Trade {
  id?: number;
  symbol: string;
  direction: 'BUY' | 'SELL';
  size: number;
  entry_time: string;
  exit_time?: string;
  entry_price: number;
  exit_price?: number;
  pnl?: number;
  commission?: number;
  notes?: string;
  tags?: string;
  emotional_state?: string;
  status: 'OPEN' | 'CLOSED';
}

export interface AlertRule {
  id?: number;
  symbol: string;
  metric: string;
  operator: string;
  threshold: number;
  status: 'ACTIVE' | 'TRIGGERED' | 'DISABLED';
  created_at?: string;
  triggered_at?: string;
}

export interface AlertLog {
  id: number;
  alert_id: number;
  triggered_at: string;
  triggered_value: number;
  message: string;
}

export const marketService = {
  sync: async (symbol: string, timeframe: string, count: number = 500) => {
    const res = await api.post(`/market/sync?symbol=${symbol}&timeframe=${timeframe}&count=${count}`);
    return res.data;
  },
  getPrices: async (symbol: string, timeframe: string, limit: number = 500): Promise<PriceBar[]> => {
    const res = await api.get(`/market/prices?symbol=${symbol}&timeframe=${timeframe}&limit=${limit}`);
    return res.data;
  },
  getIndicators: async (symbol: string, timeframe: string) => {
    const res = await api.get(`/indicators?symbol=${symbol}&timeframe=${timeframe}`);
    return res.data;
  },
};

export const aiService = {
  train: async (symbol: string, timeframe: string) => {
    const res = await api.post(`/ai/train?symbol=${symbol}&timeframe=${timeframe}`);
    return res.data;
  },
  predict: async (symbol: string, timeframe: string) => {
    const res = await api.get(`/ai/predict?symbol=${symbol}&timeframe=${timeframe}`);
    return res.data;
  },
  chat: async (message: string, currentState: any = {}) => {
    const res = await api.post(`/ai/chat`, { message, current_state: currentState });
    return res.data;
  },
};

export const backtestService = {
  getStrategies: async () => {
    const res = await api.get(`/strategies`);
    return res.data;
  },
  runBacktest: async (config: {
    symbol: string;
    timeframe: string;
    strategy: string;
    initial_capital: number;
    commission: number;
    stop_loss_pct: number;
    take_profit_pct: number;
  }) => {
    const res = await api.post(`/backtest`, config);
    return res.data;
  },
};

export const journalService = {
  getTrades: async (): Promise<Trade[]> => {
    const res = await api.get(`/journal`);
    return res.data;
  },
  logTrade: async (trade: Partial<Trade>): Promise<Trade> => {
    const res = await api.post(`/journal`, trade);
    return res.data;
  },
  closeTrade: async (tradeId: number, exitData: { exit_price: number; exit_time: string; commission?: number; notes?: string; emotional_state?: string }): Promise<Trade> => {
    const res = await api.post(`/journal/close/${tradeId}`, exitData);
    return res.data;
  },
  getStats: async () => {
    const res = await api.get(`/journal/stats`);
    return res.data;
  },
};

export const alertService = {
  getAlerts: async (): Promise<AlertRule[]> => {
    const res = await api.get(`/alerts`);
    return res.data;
  },
  createAlert: async (alert: Partial<AlertRule>): Promise<AlertRule> => {
    const res = await api.post(`/alerts`, alert);
    return res.data;
  },
  getLogs: async (): Promise<AlertLog[]> => {
    const res = await api.get(`/alerts/logs`);
    return res.data;
  },
  checkAlerts: async () => {
    const res = await api.post(`/alerts/check`);
    return res.data;
  },
};
