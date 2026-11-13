// Builds slides/deck.pptx  --  node build_deck.js   (numbers from results/full/tables)
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const { applyTheme } = require("/root/.claude/skills/synced/0c5659ab-3dbb-4418-9aa5-224ad696391e_f8443fa9-5c0a-4cbf-845f-920ebfc44424/pptx/scripts/apply_theme.js");

const THEME = {
  name: "Hedging", headFontFace: "Cambria", bodyFontFace: "Calibri",
  colors: { dk1: "141B2D", lt1: "FFFFFF", dk2: "1B2A41", lt2: "EEF2F7",
    accent1: "2A78D6", accent2: "EB6834", accent3: "1BAF7A", accent4: "EDA100",
    accent5: "6250D6", accent6: "52514E", hlink: "2A78D6", folHlink: "6250D6" },
};
const HEX = { navy: "1B2A41", orange: "EB6834", blue: "2A78D6", tint: "EEF2F7", grey: "52514E", white: "FFFFFF", green: "1BAF7A" };

async function icon(Comp, color) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color: "#" + color, size: 256 }));
  const buf = await sharp(Buffer.from(svg)).resize(256, 256).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.title = "Delta Hedging of European Options";
  pres.author = "MAC F244 project group";
  const C = pres.SchemeColor;

  pres.defineSlideMaster({
    title: "Title Dark", background: { color: HEX.navy },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.0, w: 11.7, h: 1.9,
        fontSize: 40, bold: true, color: C.background1, valign: "bottom", align: "left" }, text: "" } },
      { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 4.1, w: 11.7, h: 2.2,
        fontSize: 18, color: "CADCFC", valign: "top" }, text: "" } },
    ],
  });
  pres.defineSlideMaster({
    title: "Content", background: { color: HEX.white },
    slideNumber: { x: 12.4, y: 7.0, w: 0.6, h: 0.3, fontSize: 10, color: HEX.grey },
    objects: [
      { text: { text: "MAC F244 · Delta hedging project", options: { x: 0.6, y: 7.0, w: 6, h: 0.3, fontSize: 10, color: HEX.grey } } },
      { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 12.1, h: 0.85,
        fontSize: 32, bold: true, color: C.text2, valign: "middle" }, text: "" } },
    ],
  });

  const sec = (t) => pres.addSection({ title: t });
  const T = (s, txt) => s.addText(txt, { placeholder: "title" });
  const body = (s, items, o) => s.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })),
    Object.assign({ isTextBox: true, fontSize: 16, color: HEX.navy, paraSpaceAfter: 8, valign: "top" }, o));
  const card = (s, x, y, w, h, name) => s.addShape(pres.shapes.ROUNDED_RECTANGLE,
    { x, y, w, h, fill: { color: HEX.tint }, line: { color: HEX.tint }, rectRadius: 0.12, objectName: name });
  const badge = (s, letter, x = 0.6, y = 0.47) => {
    s.addShape(pres.shapes.OVAL, { x, y, w: 0.6, h: 0.6, fill: { color: HEX.orange }, line: { color: HEX.orange }, objectName: "badge" });
    s.addText(letter, { isTextBox: true, x, y, w: 0.6, h: 0.6, fontSize: 20, bold: true, color: HEX.white, align: "center", valign: "middle", margin: 0 });
  };
  const titleWithBadge = (s, letter, txt) => { badge(s, letter); s.addText(txt, { placeholder: "title", x: 1.4, w: 11.3 }); };
  const fig = (s, file, y = 1.35, w = 12.1) => s.addImage({ path: file, x: (13.33 - w) / 2, y, w, h: w * (2.8 / 7.2), altText: file });
  const takeaway = (s, txt, y = 6.25) => s.addText(txt, { isTextBox: true, x: 0.6, y, w: 12.1, h: 0.6, fontSize: 16, color: HEX.navy, bold: true, valign: "middle" });

  // 1 ── Title
  sec("Opening");
  let s = pres.addSlide({ masterName: "Title Dark", sectionTitle: "Opening" });
  s.addText("Delta Hedging of European Options", { placeholder: "title" });
  s.addText([
    { text: "How rebalancing frequency, volatility misspecification and transaction costs affect hedging errors", options: { breakLine: true } },
    { text: " ", options: { breakLine: true, fontSize: 10 } },
    { text: "MAC F244 · Semester I, AY 2026–27 · Project topic 12", options: { breakLine: true, fontSize: 15 } },
    { text: "[Name 1, ID] · [Name 2, ID] · [Name 3, ID] · [Name 4, ID] · [Name 5, ID]", options: { fontSize: 15 } },
  ], { placeholder: "body" });
  s.addNotes("SPEAKER: Member 1. TIME: 0:30 (cumulative 0:30).\nGood morning. We studied what happens when a bank that sells an option tries to hedge it the way Black–Scholes says, but in a realistic world: trading only at discrete times, using a possibly wrong volatility, and paying transaction costs. All our code, data and results are reproducible from one folder.");

  // 2 ── Problem
  s = pres.addSlide({ masterName: "Content", sectionTitle: "Opening" });
  T(s, "The seller's problem in plain English");
  body(s, ["We sell a call: receive premium V₀ today, owe max(S_T − K, 0) at maturity",
    "Delta hedge: hold Δ = ∂C/∂S shares and keep adjusting as the price moves",
    "Black–Scholes: continuous, costless trading with the true σ ⇒ the payoff is replicated exactly",
    "Reality breaks all three assumptions. We measure the leftover hedging error P&L_T"], { x: 0.6, y: 1.4, w: 5.9, h: 4.8 });
  const probs = [[fa.FaClock, "A · Discrete trading", "Rebalance only N times"], [fa.FaBullseye, "B · Wrong volatility", "Price and hedge with σ_h ≠ σ"],
    [fa.FaCoins, "C · Transaction costs", "Pay c per unit traded"], [fa.FaLayerGroup, "D/E · Different assets", "Volatility regimes, moneyness, maturity, real data"]];
  for (let i = 0; i < probs.length; i++) {
    const y = 1.4 + i * 1.22;
    card(s, 6.9, y, 5.8, 1.05, "problem-card");
    s.addImage({ data: await icon(probs[i][0], HEX.orange), x: 7.1, y: y + 0.25, w: 0.55, h: 0.55, altText: probs[i][1] });
    s.addText([{ text: probs[i][1], options: { bold: true, breakLine: true, fontSize: 17 } }, { text: probs[i][2], options: { fontSize: 14, color: HEX.grey } }],
      { isTextBox: true, x: 7.85, y, w: 4.7, h: 1.05, color: HEX.navy, valign: "middle", margin: 0 });
  }
  s.addNotes("SPEAKER: Member 1. TIME: 1:15 (cumulative 1:45).\nSelling a call means we owe the payoff if the stock rises. To avoid betting, we hold delta shares; delta changes with the price, so we keep trading. Black–Scholes says this replicates the payoff exactly, but only under three idealisations. We relax each one: A discrete trading, B wrong volatility, C costs, and then we check how the answers change across assets (D) and on one real price series (E). Sign convention throughout: P&L at maturity, positive means the seller gains.");

  // 3 ── Model
  sec("Mathematics");
  s = pres.addSlide({ masterName: "Content", sectionTitle: "Mathematics" });
  T(s, "Model: GBM under two measures");
  card(s, 0.6, 1.4, 5.9, 2.4, "P-card"); card(s, 6.8, 1.4, 5.9, 2.4, "Q-card");
  s.addText([{ text: "Physical measure ℙ (real world)", options: { bold: true, breakLine: true, fontSize: 18 } },
    { text: "dS = μS dt + σS dW", options: { fontFace: "Cambria", fontSize: 20, breakLine: true } },
    { text: "Generates the paths on which hedging P&L is realised (experiments A–D, μ = 10%)", options: { fontSize: 14, color: HEX.grey } }],
    { isTextBox: true, x: 0.8, y: 1.5, w: 5.5, h: 2.2, color: HEX.navy, valign: "top", paraSpaceAfter: 6 });
  s.addText([{ text: "Risk-neutral measure ℚ (pricing)", options: { bold: true, breakLine: true, fontSize: 18 } },
    { text: "dS = rS dt + σS dWᵠ", options: { fontFace: "Cambria", fontSize: 20, breakLine: true } },
    { text: "Prices are ℚ-expectations: C₀ = e^(−rT) 𝔼ᵠ[(S_T − K)⁺]. Checked: MC under ℚ gives z = −0.35; the same estimator under ℙ is rejected (z = 401)", options: { fontSize: 14, color: HEX.grey } }],
    { isTextBox: true, x: 7.0, y: 1.5, w: 5.5, h: 2.2, color: HEX.navy, valign: "top", paraSpaceAfter: 6 });
  s.addText([{ text: "Exact simulation (no discretisation error): ", options: { bold: true } },
    { text: "S(t+Δt) = S(t)·exp[(m − σ²/2)Δt + σ√Δt·Z],  Z ~ N(0,1),  m = μ or r", options: { fontFace: "Cambria" } }],
    { isTextBox: true, x: 0.6, y: 4.1, w: 12.1, h: 0.6, fontSize: 16, color: HEX.navy });
  body(s, ["BS assumptions: constant r and σ, no dividends, no costs, continuous trading, unlimited borrowing and short-selling",
    "Base case: S₀ = K = 100, T = 0.25 yr, r = 5%, σ = 20%. Money in currency units, time in years"], { x: 0.6, y: 4.85, w: 12.1, h: 1.6, fontSize: 15 });
  s.addNotes("SPEAKER: Member 1. TIME: 1:15 (cumulative 3:00).\nTwo measures, two jobs. Under P the stock drifts at mu; that is where we live and where hedging profits and losses happen, so we simulate hedging paths under P. Under Q the drift is r; prices are discounted Q-expectations. Our validation shows this distinction matters numerically: the Monte Carlo price under Q matches Black–Scholes, the same estimator under P is wildly off. The log-price update is exact for any step size, so simulation adds no time-discretisation error. List the BS assumptions; units: currency with S0 = 100, years.");

  // 4 ── Itô → PDE → delta
  s = pres.addSlide({ masterName: "Content", sectionTitle: "Mathematics" });
  T(s, "From Itô's lemma to the hedge ratio");
  const steps = [["1  Itô", "dV = (V_t + μSV_S + ½σ²S²V_SS)dt + σSV_S dW"],
    ["2  Replicate", "Π = V − V_S·S has no dW term ⇒ riskless ⇒ dΠ = rΠ dt"],
    ["3  PDE", "V_t + rSV_S + ½σ²S²V_SS − rV = 0,  V(T,S) = (S−K)⁺   (μ cancels)"],
    ["4  Solution", "C = S·N(d₁) − K·e^(−rτ)·N(d₂),   Δ = N(d₁),   Γ = φ(d₁)/(Sσ√τ)"]];
  steps.forEach(([h, eq], i) => {
    const y = 1.4 + i * 1.0;
    card(s, 0.6, y, 12.1, 0.85, "step-card");
    s.addText(h, { isTextBox: true, x: 0.8, y, w: 1.9, h: 0.85, fontSize: 17, bold: true, color: HEX.orange, valign: "middle", margin: 0 });
    s.addText(eq, { isTextBox: true, x: 2.7, y, w: 9.9, h: 0.85, fontSize: 19, fontFace: "Cambria", color: HEX.navy, valign: "middle", margin: 0 });
  });
  body(s, ["d₁,₂ = [ln(S/K) + (r ± σ²/2)τ] / (σ√τ),  τ = T − t",
    "At maturity τ = 0: C = (S−K)⁺ and Δ = 1{S > K}, coded explicitly; we never rebalance at T",
    "Near expiry at the money Γ ~ 1/√τ blows up, which is where discrete hedging hurts most"], { x: 0.6, y: 5.45, w: 12.1, h: 1.5, fontSize: 15, paraSpaceAfter: 4 });
  s.addNotes("SPEAKER: Member 2. TIME: 1:15 (cumulative 4:15).\nWalk down the four boxes. Itô gives dV. Holding the option and shorting V_S shares kills the dW term, so the portfolio is riskless and must earn r. That gives the PDE, and mu disappears, which is why the price does not depend on expected returns. The solution is the BS formula; delta is N(d1). Maturity: the formula divides by root tau, so the code sets the payoff and indicator delta at tau = 0 explicitly. Gamma explodes near expiry at the money; remember that for later.");

  // 5 ── Bookkeeping
  s = pres.addSlide({ masterName: "Content", sectionTitle: "Mathematics" });
  T(s, "The seller's books: discrete self-financing hedge");
  const tl = [["t₀", "B₀ = V₀ − φ₀S₀ − c|φ₀|S₀", "premium in, buy φ₀ = Δ₀ shares"],
    ["t_k", "B_k = B_{k−1}e^(rΔt) − (φ_k − φ_{k−1})S_k − c|φ_k − φ_{k−1}|S_k", "interest, then rebalance"],
    ["T", "P&L_T = B_{N−1}e^(rΔt) + φ_{N−1}S_T(1 − c) − (S_T − K)⁺", "sell shares, pay cash payoff"]];
  s.addShape(pres.shapes.LINE, { x: 1.15, y: 1.75, w: 0, h: 2.9, line: { color: HEX.blue, width: 2 }, objectName: "timeline" });
  tl.forEach(([t, eq, note], i) => {
    const y = 1.45 + i * 1.3;
    s.addShape(pres.shapes.OVAL, { x: 0.8, y, w: 0.7, h: 0.7, fill: { color: HEX.blue }, line: { color: HEX.blue }, objectName: "time-dot" });
    s.addText(t, { isTextBox: true, x: 0.8, y, w: 0.7, h: 0.7, fontSize: 15, bold: true, color: HEX.white, align: "center", valign: "middle", margin: 0 });
    s.addText([{ text: eq, options: { fontFace: "Cambria", fontSize: 18, breakLine: true } }, { text: note, options: { fontSize: 14, color: HEX.grey } }],
      { isTextBox: true, x: 1.8, y: y - 0.1, w: 10.9, h: 0.95, color: HEX.navy, valign: "middle", margin: 0 });
  });
  card(s, 0.6, 5.3, 12.1, 1.45, "convention-card");
  s.addText([{ text: "Conventions. ", options: { bold: true } },
    { text: "P&L_T > 0 ⇒ seller gains (currency at T). Cost c per side on every trade incl. the initial purchase and final sale. Δ ignores c, so P&L(c) = P&L(0) − c·TV exactly: one simulation serves all cost levels. Check: an independent gains-form formula agrees to 10⁻¹³." }],
    { isTextBox: true, x: 0.8, y: 5.35, w: 11.7, h: 1.35, fontSize: 15, color: HEX.navy, valign: "middle", margin: 0 });
  s.addNotes("SPEAKER: Member 2. TIME: 1:30 (cumulative 5:45).\nThis slide is the heart of the code. At t0 we receive the premium and buy delta shares, paying cost c. At each later date cash earns interest, then we trade the change in delta. At T we sell the shares and pay the cash-settled payoff; what is left is P&L. Self-financing means no other cash enters or leaves. Because delta does not depend on c, P&L is exactly linear in c. In the viva notes we work through a 4-step path by hand: premium 4.615, final P&L 1.349.");

  // 6 ── Why discrete ≠ exact
  s = pres.addSlide({ masterName: "Content", sectionTitle: "Mathematics" });
  T(s, "Why discrete hedging cannot be exact");
  card(s, 0.6, 1.4, 12.1, 1.15, "eq-card");
  s.addText("One-step error:  ε_k ≈ ½Γ_kS_k²σ²Δt · (1 − Z_k²),     𝔼[1 − Z²] = 0,   Var[1 − Z²] = 2",
    { isTextBox: true, x: 0.8, y: 1.4, w: 11.7, h: 1.15, fontSize: 20, fontFace: "Cambria", color: HEX.navy, valign: "middle", margin: 0 });
  const three = [["No bias", "Each step's error has mean ≈ 0"], ["Noise ∝ 1/√N", "N independent errors, each of size ~T/N, so Var ~ 1/N"],
    ["Continuous limit", "Σ(ΔS/S)² → σ²T (quadratic variation) ⇒ error → 0"]];
  three.forEach(([h, t], i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 2.8, 3.9, 1.6, "idea-card");
    s.addText([{ text: h, options: { bold: true, fontSize: 18, color: HEX.orange, breakLine: true } }, { text: t, options: { fontSize: 15 } }],
      { isTextBox: true, x: x + 0.2, y: 2.85, w: 3.5, h: 1.5, color: HEX.navy, valign: "middle", margin: 0 });
  });
  body(s, ["Kamal–Derman (ATM): sd(P&L) ≈ √(π/4) · vega · σ / √N  →  0.439 at N = 63 (simulated 0.434)",
    "Wrong volatility σ_h: P&L ≈ ½∫ e^(r(T−t)) Γ_h S² (σ_h² − σ²) dt: a bias that does not shrink with N",
    "Leland: hedge and price at σ_L² = σ²[1 + √(2/π)·k/(σ√Δt)], k = 2c round trip"], { x: 0.6, y: 4.65, w: 12.1, h: 2.2, fontSize: 16 });
  s.addNotes("SPEAKER: Member 2. TIME: 1:15 (cumulative 7:00).\nTaylor-expand the option over one step and use the PDE: what remains is half gamma S squared sigma squared dt times (1 minus Z squared). It has mean zero, so no bias, but variance, so noise. N independent steps of size T/N give variance proportional to 1/N, so sd proportional to 1/root N. In continuous time the realised variance equals sigma squared T exactly, which is why the BS argument works. Three formulas we will test: Kamal–Derman for the noise, the gamma-weighted variance gap for a wrong volatility, and Leland's cost-adjusted volatility.");

  // 7 ── Implementation & validation
  sec("Implementation");
  s = pres.addSlide({ masterName: "Content", sectionTitle: "Implementation" });
  T(s, "Code mirrors the maths, and it is checked");
  const rows = [["Equation", "Python function"], ["Exact GBM step", "gbm.simulate_gbm"], ["C, Δ, Γ, vega; τ = 0", "black_scholes.py"],
    ["Books B₀, B_k, P&L_T", "hedge.hedge_short_call"], ["Gains form (check)", "hedge.pnl_gains_form"], ["Wrong-σ formula", "hedge.predicted_pnl_misspecified"], ["Stats + Monte Carlo SEs", "stats.summarize"]];
  s.addTable(rows.map((r, i) => r.map((c) => ({ text: c, options: { bold: i === 0, color: i === 0 ? HEX.white : HEX.navy, fill: { color: i === 0 ? HEX.navy : (i % 2 ? HEX.tint : HEX.white) }, fontFace: i > 0 && c.includes(".") ? "Courier New" : undefined } }))),
    { x: 0.6, y: 1.4, w: 6.5, colW: [2.4, 4.1], fontSize: 13, rowH: 0.42, border: { type: "none" }, margin: 0.06 });
  s.addText([{ text: "22 / 22", options: { fontSize: 54, bold: true, color: HEX.green, breakLine: true } }, { text: "validation checks pass", options: { fontSize: 16, color: HEX.grey } }],
    { isTextBox: true, x: 7.3, y: 1.3, w: 5.4, h: 1.5, align: "left", valign: "middle" });
  body(s, ["Put–call parity error 2×10⁻¹⁴; delta vs finite difference 2×10⁻¹⁰", "Hand ledger = simulator = gains form",
    "Boundaries: τ→0, deep ITM/OTM, σ→0, 0 ≤ Δ ≤ 1", "Refinement slope of error −0.49 (theory −½); two seeds agree"], { x: 7.3, y: 2.9, w: 5.4, h: 3.0, fontSize: 15, paraSpaceAfter: 6 });
  s.addText("Common random numbers: every N uses the same 40,000 paths (fine grid, 1260 steps), so comparisons are paired. Quick mode ≈ 10 s; full mode ≈ 70 s.",
    { isTextBox: true, x: 0.6, y: 5.95, w: 12.1, h: 0.8, fontSize: 15, color: HEX.navy, italic: true });
  s.addNotes("SPEAKER: Member 3. TIME: 1:00 (cumulative 8:00).\nEach equation maps to one function; the hedge function follows the bookkeeping line by line. Before trusting any result we ran 22 checks, all pass, also as pytest. Key design choice: we simulate each path once on a fine grid and sub-sample it for every rebalancing frequency, so differences between frequencies are not caused by different random paths. Seeds are fixed via NumPy SeedSequence.");

  // 8 ── A
  sec("Results");
  s = pres.addSlide({ masterName: "Content", sectionTitle: "Results" });
  titleWithBadge(s, "A", "More frequent trading: error falls like 1/√N");
  fig(s, "fig1_frequency.png", 1.3, 11.6);
  takeaway(s, "sd 1.86 (N = 3) → 0.43 (daily) → 0.10 (N = 1260); slope −0.488 ± 0.001; mean ≈ 0. Daily error = 9% of the 4.62 premium", 5.95);
  s.addNotes("SPEAKER: Member 3. TIME: 1:30 (cumulative 9:30).\nLeft: same paths, three frequencies. All centred at zero, narrower with more trading. Right: log-log, slope minus 0.488 across 8 independent batches; the asymptotic theory says minus one half; coarse grids are outside the asymptotic regime, and from N = 63 upward the slope is minus 0.497. The Kamal–Derman line is within 1.4% for N ≥ 63. To halve the error you must trade four times as often. Tails are fat: expected shortfall is 2.3 sd versus 2.06 for a normal. What it cannot show: anything beyond the BS world. Also, not every statistic is monotone: the absolute mean is not.");

  // 9 ── B
  s = pres.addSlide({ masterName: "Content", sectionTitle: "Results" });
  titleWithBadge(s, "B", "Wrong volatility: a bias that trading cannot remove");
  fig(s, "fig2_misspecification.png", 1.3, 11.6);
  takeaway(s, "Mean P&L −1.94 / −0.98 / 0 / +0.99 / +1.98 for σ_h = 10–30%, matching the gamma formula, at N = 63 and at N = 1260", 5.95);
  s.addNotes("SPEAKER: Member 4. TIME: 1:30 (cumulative 11:00).\nTrue sigma is 20%. If we price and hedge at 25%, we collect a bigger premium and on average keep about 0.99; at 15% we lose about 0.98. The line is the gamma-weighted variance-gap formula; it matches to two decimals. Crucially, the mean is the same at daily and at 20-times-daily trading: frequency cannot fix a wrong volatility. Right panel: path by path the realised P&L sits on the 45-degree line, correlation 0.965 to 0.992. If the premium is charged at the true sigma but delta uses the wrong one, the mean is about zero: the bias is a pricing error; the wrong delta adds risk, not expected loss.");

  // 10 ── C
  s = pres.addSlide({ masterName: "Content", sectionTitle: "Results" });
  titleWithBadge(s, "C", "Costs: there is a best rebalancing frequency");
  fig(s, "fig3_costs.png", 1.3, 11.6);
  takeaway(s, "RMSE-optimal N: 1260 / 252 / 126 / 63 / 21 for 0 / 5 / 10 / 20 / 50 bp. Leland's σ_L leaves only the 0.12 setup + unwind cost (10 bp)", 5.95);
  s.addNotes("SPEAKER: Member 4. TIME: 1:30 (cumulative 12:30).\nCosts grow roughly with root N because each step trades about gamma times |dS|. Combined with hedging noise falling like 1/root N, RMSE becomes U-shaped; circles mark the minimum. At 10 bp the best is twice a day, N = 126; at 50 bp, every 3 trading days. At the optimum, bias from costs (0.47) dominates noise (0.34). Right: with Leland's volatility the extra premium pays for rebalancing; the remaining mean of minus 0.12 is exactly the cost of the initial purchase and final sale, 0.121, which Leland's model does not include. Our conclusion depends on choosing RMSE; a different risk criterion would move the optimum.");

  // 11 ── D
  s = pres.addSlide({ masterName: "Content", sectionTitle: "Results" });
  titleWithBadge(s, "D", "Asset regimes, moneyness and maturity");
  fig(s, "fig4_regimes.png", 1.3, 11.6);
  takeaway(s, "ATM daily-hedge sd 0.32 (σ = 15%) vs 0.98 (σ = 45%): ∝ σ. OTM K/S₀ = 1.2: sd = 254% of a 0.03 premium (low vol). Absolute error flat in T", 5.95);
  s.addNotes("SPEAKER: Member 5. TIME: 1:00 (cumulative 13:30).\nTwo stylised regimes, both hedged daily, simulated under P. Error scales with sigma, ratio 3.03, as Kamal–Derman predicts because ATM vega barely depends on sigma. Left, relative to premium: out-of-the-money options in calm markets are almost impossible to hedge in relative terms, because the premium is tiny while gamma can spike. Right: at fixed daily rebalancing the absolute error is flat in maturity, because vega grows like root T and N grows like T. Costs of 10 bp, however, grow with maturity: from 0.25 for one month to 0.62 for one year at 15% vol.");

  // 12 ── E
  s = pres.addSlide({ masterName: "Content", sectionTitle: "Results" });
  titleWithBadge(s, "E", "Real prices (secondary source, illustration only)");
  fig(s, "fig5_realdata.png", 1.3, 11.6);
  takeaway(s, "σ̂: IBM 29%, MSFT 34%, GOOG 39%, AAPL 55%, AMZN 59% (2000–10, monthly); AAPL 24% (2015–17, daily). Backtest corr(P&L, σ_h² − σ²_real) = 0.87", 5.95);
  s.addNotes("SPEAKER: Member 5. TIME: 1:00 (cumulative 14:30).\nThe data are secondary-source price files with documented hashes, not option quotes; premiums are model prices. Calibrated volatilities range from 24% to 59%; drift has standard errors of 9 to 19% per year, so it is essentially unknowable, which is fine because the hedge does not use it. Backtest: sell a 63-day ATM AAPL call priced and hedged with trailing volatility, hedge daily along the real path. The P&L sign follows the variance gap, correlation 0.87, as the misspecification formula predicts. Caveat: 380 windows overlap heavily; only 7 are independent, so the average P&L is not interpretable.");

  // 13 ── Conclusions
  sec("Close");
  s = pres.addSlide({ masterName: "Title Dark", sectionTitle: "Close" });
  s.addText("What we learned", { isTextBox: true, x: 0.8, y: 0.6, w: 11.7, h: 1.0, fontSize: 36, bold: true, color: HEX.white, fontFace: "Cambria" });
  const concl = [["Frequency", "Unbiased noise; sd ≈ √(π/4)·vega·σ/√N. 4× trading halves the error"],
    ["Volatility", "Bias = gamma-weighted (σ_h² − σ²). More trading cannot remove it"],
    ["Costs", "U-shaped RMSE ⇒ an optimal frequency; Leland covers rebalancing costs only"],
    ["Assets", "Relative error largest for OTM, short-dated, low-vol options; absolute ∝ σ"]];
  concl.forEach(([h, t], i) => {
    const y = 1.85 + i * 1.2;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.8, y, w: 11.7, h: 1.0, fill: { color: "24375A" }, line: { color: "24375A" }, rectRadius: 0.12, objectName: "concl-card" });
    s.addText(h, { isTextBox: true, x: 1.05, y, w: 2.4, h: 1.0, fontSize: 20, bold: true, color: HEX.orange, valign: "middle", margin: 0 });
    s.addText(t, { isTextBox: true, x: 3.5, y, w: 8.8, h: 1.0, fontSize: 18, color: HEX.white, valign: "middle", margin: 0 });
  });
  s.addNotes("SPEAKER: Member 5. TIME: 1:00 (cumulative 15:30).\nFour take-aways, one per experiment family. Each one was predicted by a formula we derived and confirmed by simulation with standard errors.");

  // 14 ── Limitations
  s = pres.addSlide({ masterName: "Content", sectionTitle: "Close" });
  T(s, "Limitations and next steps");
  card(s, 0.6, 1.4, 5.9, 4.9, "limits"); card(s, 6.8, 1.4, 5.9, 4.9, "next");
  s.addText("Limitations", { isTextBox: true, x: 0.85, y: 1.5, w: 5.4, h: 0.5, fontSize: 20, bold: true, color: HEX.orange });
  body(s, ["Constant σ and r; no jumps, dividends, bid–ask dynamics or market impact", "RMSE is one criterion among many",
    "Monte Carlo SEs measure sampling error, not model error", "Real data: secondary source, model premiums, short overlapping sample"], { x: 0.85, y: 2.1, w: 5.4, h: 4.1, fontSize: 16 });
  s.addText("Next steps", { isTextBox: true, x: 7.05, y: 1.5, w: 5.4, h: 0.5, fontSize: 20, bold: true, color: HEX.orange });
  body(s, ["Stochastic volatility (Heston) and jumps", "Band (move-based) rebalancing instead of fixed times",
    "Real option quotes and implied volatility", "Gamma hedging with a second option"], { x: 7.05, y: 2.1, w: 5.4, h: 4.1, fontSize: 16 });
  s.addNotes("SPEAKER: All (Member 1 leads). TIME: 0:45 (cumulative 16:15).\nBe upfront: everything except E lives in the Black–Scholes world. Our optimum depends on RMSE. Real-data results are illustrations. Natural extensions: stochastic volatility, band rebalancing, real option quotes, gamma hedging.");

  // 15 ── References
  s = pres.addSlide({ masterName: "Content", sectionTitle: "Close" });
  T(s, "References, data and AI-assistance disclosure");
  body(s, ["Black & Scholes (1973) JPE 81(3); Merton (1973) Bell J. Econ. 4(1)", "Boyle & Emanuel (1980) JFE 8(3); Leland (1985) J. Finance 40(5); Kabanov & Safarian (1997) Fin. Stoch. 1",
    "El Karoui, Jeanblanc-Picqué & Shreve (1998) Math. Finance 8(2); Kamal & Derman (1999) Risk", "Shreve (2004) Stochastic Calculus for Finance II; Glasserman (2004) Monte Carlo Methods in Financial Engineering",
    "Data: vega-datasets stocks.csv; plotly/datasets finance-charts-apple.csv (provenance and hashes in data/SOURCES.md)",
    "AI assistance: code, text and figures were drafted with an AI assistant (Claude) and verified by running the code; see docs/ai_disclosure.md"],
    { x: 0.6, y: 1.4, w: 12.1, h: 4.6, fontSize: 15, paraSpaceAfter: 6 });
  s.addText("Thank you. Questions?", { isTextBox: true, x: 0.6, y: 6.05, w: 12.1, h: 0.7, fontSize: 24, bold: true, color: HEX.orange });
  s.addNotes("SPEAKER: Member 1. TIME: 0:15 (cumulative 16:30). Then about 3:30 for questions (total 20:00).\nAll models and data are referenced; full list in the report. Invite questions; every member can answer any part.");

  await pres.writeFile({ fileName: "../deck.pptx" });
  await applyTheme("../deck.pptx", THEME);
  console.log("written");
})();
