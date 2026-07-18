import logging
from app.config import settings

logger = logging.getLogger("app.ai_engine.llm_helper")

# Check if google-genai can be imported
LLM_AVAILABLE = False
try:
    from google import genai
    from google.genai import types
    LLM_AVAILABLE = True
except ImportError:
    logger.warning("google-genai library not installed. LLM helper running in Mock/Simulated mode.")

class LLMHelper:
    def __init__(self):
        self.client = None
        if LLM_AVAILABLE and settings.GEMINI_API_KEY:
            try:
                # Initialize the Google GenAI SDK client
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
                logger.info("Successfully initialized Gemini GenAI Client.")
            except Exception as e:
                logger.error(f"Error initializing Gemini GenAI Client: {e}")

    def generate_market_rationale(self, symbol: str, timeframe: str, indicators: dict, ml_prediction: dict) -> str:
        """
        Queries Gemini to generate a narrative reasoning explaining the ML predictions and Technical Indicators.
        """
        # Formulate prompt
        prompt = f"""
You are an expert quantitative trading analyst and AI assistant.
Analyze the following market data for the asset '{symbol}' on timeframe '{timeframe}':

1. Technical Indicators:
- Last Close Price: {indicators.get('close')}
- RSI (14): {indicators.get('rsi_14'):.2f} (Oversold < 30, Overbought > 70)
- MACD Histogram: {indicators.get('macd_hist'):.6f}
- Bollinger Band position (BB Percent): {indicators.get('bb_percent'):.2f} (0 = lower band, 1 = upper band)
- ATR (Volatility): {indicators.get('atr_14'):.6f}

2. Machine Learning Signal:
- ML Direction Prediction: {ml_prediction.get('direction')}
- Confidence score: {ml_prediction.get('confidence') * 100:.1f}%
- Probability of going UP: {ml_prediction.get('probability') * 100:.1f}%

Task:
Write a brief, concise technical market analysis (max 3 sentences) explaining the alignment or conflict between the machine learning direction prediction and technical indicators. Recommend a clear trading stance (Buy/Sell/Hold) with risk management suggestions based on ATR. Keep the language professional.
"""
        
        if self.client:
            try:
                # Generate content using Gemini 2.5 Flash
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                return response.text.strip()
            except Exception as e:
                logger.error(f"Gemini API call failed: {e}. Falling back to mock rationale.")
                
        # Mock/Simulated rationale fallback
        return self._generate_mock_rationale(symbol, timeframe, indicators, ml_prediction)

    def chat_with_strategy_advisor(self, user_message: str, current_state: dict) -> str:
        """
        Provides a chat interface for the user to query strategy ideas, analyze logs, or optimize parameters.
        """
        prompt = f"""
You are the Trading Strategy Advisor for the Trading Intelligence Platform.
Your goal is to help traders refine their technical setups, analyze their trade logs, and review ML predictions.

System Status Context:
- Active Assets: EURUSD, USDJPY, GBPUSD, BTCUSD
- Database: PostgreSQL (active)
- Data Source: MetaTrader 5
- Models: RandomForestClassifier (active)

User Query: "{user_message}"

Provide a professional, clear response recommending specific trading rules, risk adjustments, or explaining concepts. If they ask about indicators, explain how to combine them. Keep the tone helpful, analytical, and concise.
"""
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                return response.text.strip()
            except Exception as e:
                logger.error(f"Gemini API chat call failed: {e}")
                
        return f"Hello! (Advisor Offline Mode) I received your query: '{user_message}'. Currently, the Gemini API is offline or not configured. To enable full AI intelligence, please provide a valid GEMINI_API_KEY in the configuration."

    def _generate_mock_rationale(self, symbol: str, timeframe: str, indicators: dict, ml_prediction: dict) -> str:
        direction = ml_prediction.get("direction", "HOLD")
        rsi = indicators.get("rsi_14", 50.0)
        
        if direction == "UP":
            if rsi < 40:
                return f"The Machine Learning model predicts an UPWARD movement, coinciding with an oversold RSI of {rsi:.1f}, indicating a strong bullish reversal opportunity. We recommend a BUY stance, placing a stop-loss proportional to the ATR of {indicators.get('atr_14', 0.001):.4f} below the latest swing low."
            else:
                return f"ML suggests bullish momentum (UP) with a confidence of {ml_prediction.get('confidence', 0.0)*100:.1f}%. However, indicators show neutral readings. Suggest scaling in lightly with tight risk controls."
        elif direction == "DOWN":
            if rsi > 60:
                return f"ML predicts a DOWNWARD correction while RSI sits in overbought territory at {rsi:.1f}. This represents a potential bearish breakdown. Recommend a SELL stance with a stop loss placed above recent resistance."
            else:
                return f"Bearish signals are indicated by the ML model. Wait for a confirmation breakdown below support before executing short positions."
        else:
            return "No clear direction. The ML model predicts consolidation (HOLD) due to converging moving averages and contracting Bollinger Bands. Stance remains NEUTRAL until volatility expands."
