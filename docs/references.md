# References (models, algorithms, data, software)

| Used for | Reference |
|---|---|
| BS model, PDE, delta | F. Black, M. Scholes (1973). The pricing of options and corporate liabilities. *Journal of Political Economy* 81(3), 637–654. |
| BS model, no-arbitrage | R. C. Merton (1973). Theory of rational option pricing. *Bell Journal of Economics and Management Science* 4(1), 141–183. |
| Discrete hedging error | P. P. Boyle, D. Emanuel (1980). Discretely adjusted option hedges. *Journal of Financial Economics* 8(3), 259–282. doi:10.1016/0304-405X(80)90003-3 |
| Kamal–Derman approximation | M. Kamal, E. Derman (1999). When you cannot hedge continuously: the corrections of Black–Scholes. *Risk*, January 1999 (originally a Goldman Sachs research note). Volume/pages not verified. |
| Leland volatility | H. E. Leland (1985). Option pricing and replication with transactions costs. *Journal of Finance* 40(5), 1283–1301. |
| Leland's limiting error | Y. M. Kabanov, M. M. Safarian (1997). On Leland's strategy of option pricing with transactions costs. *Finance and Stochastics* 1, 239–250. |
| Cost–risk trade-off | K. B. Toft (1996). On the mean-variance tradeoff in option replication with transactions costs. *Journal of Financial and Quantitative Analysis* 31(2), 233–263. |
| Wrong-volatility formula | N. El Karoui, M. Jeanblanc-Picqué, S. E. Shreve (1998). Robustness of the Black and Scholes formula. *Mathematical Finance* 8(2), 93–126. doi:10.1111/1467-9965.00047 |
| Itô, Girsanov, Feynman–Kac | S. E. Shreve (2004). *Stochastic Calculus for Finance II: Continuous-Time Models*. Springer. |
| Exact GBM simulation, MC errors | P. Glasserman (2004). *Monte Carlo Methods in Financial Engineering*. Springer. |
| Software | NumPy (Harris et al., *Nature* 585, 357–362, 2020); SciPy (Virtanen et al., *Nature Methods* 17, 261–272, 2020); pandas; Matplotlib (Hunter, *Computing in Science & Engineering* 9(3), 90–95, 2007). |
| Data | vega-datasets `stocks.csv` via Python package `vega_datasets` 0.9.0; plotly/datasets `finance-charts-apple.csv` (GitHub). Details and SHA-256 in `data/SOURCES.md`. |
| Implementation cross-check (optional reading) | QuantLib `Examples/DiscreteHedging/DiscreteHedging.cpp`, which reproduces Derman & Kamal's replication-error study. |
