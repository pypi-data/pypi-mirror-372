"""
Core stock analysis functionality.

This module contains the main StockAnalyzer class that orchestrates
the analysis of stocks using technical and fundamental analysis.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional


from .models import AnalysisResult, Recommendation, StockData
from data.fetcher import DataFetcher
from technical_analysis import TechnicalAnalysis, calculate_fundamental_metrics

logger = logging.getLogger(__name__)


class StockAnalyzer:
    """
    Main class for performing stock analysis.

    This class coordinates data fetching, technical analysis, and fundamental
    analysis to provide comprehensive stock analysis.
    """

    def __init__(self, symbols: Optional[List[str]] = None, days: int = 365):
        """
        Initialize the StockAnalyzer.

        Args:
            symbols: List of stock symbols to analyze (default: top BSE stocks)
            days: Number of days of historical data to fetch (default: 365)
        """
        from config.settings import TOP_BSE_STOCKS  # Avoid circular import

        self.symbols = symbols or TOP_BSE_STOCKS
        self.days = days
        self.data_fetcher = DataFetcher()
        self.analysis_results: Dict[str, AnalysisResult] = {}

    def fetch_data(self) -> Dict[str, StockData]:
        """
        Fetch data for all symbols.

        Returns:
            Dictionary mapping symbols to StockData objects
        """
        logger.info(f"Fetching data for {len(self.symbols)} stocks...")
        raw_data = self.data_fetcher.fetch_multiple_stocks(self.symbols, self.days)

        stock_data = {}
        for symbol, df in raw_data.items():
            stock_data[symbol] = StockData(
                symbol=symbol,
                data=df,
                metadata={
                    "days": len(df),
                    "first_date": df.index.min().strftime("%Y-%m-%d"),
                    "last_date": df.index.max().strftime("%Y-%m-%d"),
                },
            )

        return stock_data

    def analyze_stock(self, symbol: str, stock_data: StockData) -> AnalysisResult:
        """
        Perform technical and fundamental analysis on a stock.

        Args:
            symbol: Stock symbol
            stock_data: StockData object containing the stock's data

        Returns:
            AnalysisResult containing all analysis data
        """
        logger.info(f"Analyzing {symbol}...")

        # Technical Analysis
        ta = TechnicalAnalysis(stock_data.data)
        indicators = ta.calculate_all_indicators()

        # Fundamental Analysis
        fundamentals = calculate_fundamental_metrics(symbol)

        return AnalysisResult(
            symbol=symbol,
            technical_indicators=indicators,
            fundamental_metrics=fundamentals,
            metadata={
                "analysis_date": datetime.utcnow().isoformat(),
                "data_points": len(stock_data.data),
            },
        )

    def analyze_all(self) -> Dict[str, AnalysisResult]:
        """
        Run analysis for all symbols.

        Returns:
            Dictionary mapping symbols to their AnalysisResults
        """
        stock_data = self.fetch_data()

        for symbol, data in stock_data.items():
            try:
                self.analysis_results[symbol] = self.analyze_stock(symbol, data)
                logger.info(f"Completed analysis for {symbol}")
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {str(e)}")
                continue

        return self.analysis_results

    def generate_recommendation(self, analysis: AnalysisResult) -> Recommendation:
        """
        Generate a recommendation based on analysis results.

        Args:
            analysis: AnalysisResult to base the recommendation on

        Returns:
            Recommendation object with action and reasoning
        """
        # This is a simplified version - expand with actual recommendation logic
        reasoning = []

        # Example recommendation logic
        rsi = analysis.technical_indicators.get("rsi")
        if rsi is not None:
            if rsi < 30:
                reasoning.append("RSI indicates oversold conditions")
            elif rsi > 70:
                reasoning.append("RSI indicates overbought conditions")

        pe = analysis.fundamental_metrics.get("pe_ratio")
        if pe is not None:
            if pe < 15:
                reasoning.append("Low P/E ratio suggests good value")
            elif pe > 25:
                reasoning.append("High P/E ratio suggests overvaluation")

        # Default to HOLD if no strong signals
        if not reasoning:
            reasoning.append("No strong buy/sell signals detected")
            return Recommendation(
                symbol=analysis.symbol,
                action="HOLD",
                confidence=0.5,
                reasoning=reasoning,
            )

        # Simple decision logic - expand based on your strategy
        if any("oversold" in r.lower() or "low" in r.lower() for r in reasoning):
            action = "BUY"
            confidence = 0.7
        elif any("overbought" in r.lower() or "high" in r.lower() for r in reasoning):
            action = "SELL"
            confidence = 0.6
        else:
            action = "HOLD"
            confidence = 0.5

        return Recommendation(
            symbol=analysis.symbol,
            action=action,
            confidence=confidence,
            reasoning=reasoning,
        )
