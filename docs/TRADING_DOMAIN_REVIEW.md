# Trading Domain & Quant Review Specification

This document details the quantitative verification standards enforced by the **Trading Domain / Quant Research Agent**.

---

## Quantitative Review Standards

### 1. Mathematical Accuracy of Indicators
- **EMA Calculation**: Must use multiplier $k = \frac{2}{N + 1}$ and seed with Simple Moving Average (SMA).
- **RSI Calculation**: Must use Wilder's Smoothing Technique for gain/loss averages rather than simple moving averages.
- **VWAP Calculation**: Must reset daily/weekly at session open: $\text{VWAP} = \frac{\sum (\text{Typical Price} \times \text{Volume})}{\sum \text{Volume}}$.
- **ATR Calculation**: Must use True Range formula: $\max(H - L, |H - C_{\text{prev}}|, |L - C_{\text{prev}}|)$.

### 2. Prevention of Lookahead Bias
- Feature extraction and indicator calculations MUST ONLY use historical candles available up to time $t$.
- Future price data ($t+1$) MUST NEVER leak into feature vectors or backtest calculations.

### 3. Data Gap & Weekend Handling
- Non-trading market gap hours (Friday close to Sunday open) MUST NOT be treated as anomalous missing data gaps.
- Multi-hour resampling (e.g. H4 from H1) MUST correctly calculate:
  - `open`: first candle close
  - `high`: maximum high
  - `low`: minimum low
  - `close`: last candle close
  - `tick_volume`: sum of volumes

### 4. Trend Classification Standards
- `Bullish`: Current close price > SMA20 and EMA50 > EMA200.
- `Bearish`: Current close price < SMA20 and EMA50 < EMA200.
- `Neutral`: Price within SMA20 standard deviation band.
