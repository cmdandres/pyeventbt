"""
PyEventBT
Documentation: https://pyeventbt.com
GitHub: https://github.com/marticastany/pyeventbt

Author: Marti Castany
Copyright (c) 2025 Marti Castany
Licensed under the Apache License, Version 2.0
"""

#import numpy as np
import pandas as pd
#import os
import matplotlib.pyplot as plt
#from functools import lru_cache
#from typing import Callable
#from sklearn.linear_model import LinearRegression
#from pydantic import BaseModel
#from scipy.stats import norm
#from enum import Enum
#from pyeventbt.utils.utils import print_percentage_bar

# Silence Matplotlib Futurewarnings
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="matplotlib")

        
class BacktestResults:

    #backtest_results_save_name = 'backtest_results.csv'

    def __init__(self, backtest_pnl: pd.DataFrame, trades: pd.DataFrame) -> None:
        self._backtest_pnl = backtest_pnl
        self._pnl = backtest_pnl.astype(float)
        self._returns = backtest_pnl.EQUITY.pct_change()
        self._trades = trades

    @property
    def pnl(self):
        return self._pnl
    
    @property
    def returns(self):
        return self._returns
    
    @property
    def trades(self):
        return self._trades
    
    @property
    def backtest_pnl(self):
        return self._backtest_pnl        
    
    
    def plot(self, title: str = "Backtest", subtitle: str = "", save_path: str = "", show: bool = False):
        # Calcular metricas clave
        equity      = self._pnl["EQUITY"]
        balance     = self._pnl["BALANCE"]
        initial_cap = float(balance.iloc[0])
        final_bal   = float(balance.iloc[-1])
        net_pnl     = final_bal - initial_cap
        net_pct     = (net_pnl / initial_cap) * 100 if initial_cap else 0.0
        peak        = equity.cummax()
        drawdown    = (equity - peak) / peak * 100
        max_dd      = float(drawdown.min())
        start_date  = str(self._pnl.index[0])[:10]
        end_date    = str(self._pnl.index[-1])[:10]

        n_trades = len(self._trades) if self._trades is not None else 0
        if self._trades is not None and len(self._trades) > 0 and "profit" in self._trades.columns:
            wins    = (self._trades["profit"] > 0).sum()
            wr      = wins / n_trades * 100
            gross_w = self._trades.loc[self._trades["profit"] > 0, "profit"].sum()
            gross_l = abs(self._trades.loc[self._trades["profit"] < 0, "profit"].sum())
            pf      = gross_w / gross_l if gross_l > 0 else float("inf")
        else:
            wr = pf = 0.0

        full_title = (
            f"{title}  |  {start_date} -> {end_date}\n"
            f"Trades: {n_trades}  WR: {wr:.1f}%  PF: {pf:.2f}  "
            f"Net PnL: ${net_pnl:+,.0f} ({net_pct:+.1f}%)  Max DD: {max_dd:.2f}%"
        )
        if subtitle:
            full_title = subtitle + "\n" + full_title

        fig, ax = plt.subplots(figsize=(14, 6))
        self.pnl[["EQUITY", "BALANCE"]].plot(ax=ax)
        ax.set_title(full_title, fontsize=10, pad=12)
        ax.legend(["Equity", "Balance"])
        ax.set_xlabel("Date")
        ax.set_ylabel(f"Balance (USD) — Capital inicial: ${initial_cap:,.0f}")
        ax.margins(x=0.01, y=0.05)
        ax.grid(True, alpha=0.3) 
        fig.tight_layout()
        if save_path:
            import os
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
        if show:
            plt.show()
        plt.close(fig)