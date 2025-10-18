import axios from "axios";
import type { Strategy, BacktestRun, Trade } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Strategies
export async function getStrategies(filters?: any): Promise<Strategy[]> {
  const response = await api.get("/strategies", { params: filters });
  return response.data;
}

export async function getStrategy(id: string): Promise<Strategy> {
  const response = await api.get(`/strategies/${id}`);
  return response.data;
}

export async function createStrategy(data: Partial<Strategy>): Promise<Strategy> {
  const response = await api.post("/strategies", data);
  return response.data;
}

export async function updateStrategy(id: string, data: Partial<Strategy>): Promise<Strategy> {
  const response = await api.put(`/strategies/${id}`, data);
  return response.data;
}

export async function deleteStrategy(id: string): Promise<void> {
  await api.delete(`/strategies/${id}`);
}

// Backtests
export async function getStrategyBacktests(strategyId: string): Promise<BacktestRun[]> {
  const response = await api.get(`/strategies/${strategyId}/backtests`);
  return response.data;
}

export async function createBacktest(strategyId: string, params: any): Promise<BacktestRun> {
  const response = await api.post(`/strategies/${strategyId}/backtests`, params);
  return response.data;
}

export async function getBacktest(backtestId: string): Promise<BacktestRun> {
  const response = await api.get(`/backtests/${backtestId}`);
  return response.data;
}

// Trades
export async function getStrategyTrades(strategyId: string): Promise<Trade[]> {
  const response = await api.get(`/strategies/${strategyId}/trades`);
  return response.data;
}

export default api;

