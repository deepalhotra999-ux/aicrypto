import time, requests, math, logging, json, os
from datetime import datetime

# ─────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────
TOKEN    = "8628489665:AAF2-cmo6fYVA2YfYCWyZqGSSXH9dJoQhsE"
CHAT     = 508265847
CHECK    = 3600
PAPER_BAL = 50.0
RISK_PCT  = 0.15
SL_PCT    = 0.025
TP1_PCT   = 0.025
TP2_PCT   = 0.045
TP3_PCT   = 0.075
STATE_FILE = "state.json"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()])
log = logging.getLogger(__name__)

# ─────────────────────────────────────────
#  STATE (persists across restarts)
# ─────────────────────────────────────────
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except:
            pass
    return {
        "balance": PAPER_BAL,
        "open_trades": {},
        "closed_trades": [],
        "total_pnl": 0.0,
        "wins": 0,
        "losses": 0,
        "fired": [],
        "scan_count": 0,
        "start_time": datetime.now().isoformat()
    }

def save_state(s):
    with open(STATE_FILE, "w") as f:
        json.dump(s, f, indent=2)

# ─────────────────────────────────────────
#  COINS
# ─────────────────────────────────────────
COINS = [
    # ── Top 50 (original) ──
    ("bitcoin","BTC/USDT"),("ethereum","ETH/USDT"),("solana","SOL/USDT"),
    ("binancecoin","BNB/USDT"),("ripple","XRP/USDT"),("dogecoin","DOGE/USDT"),
    ("cardano","ADA/USDT"),("avalanche-2","AVAX/USDT"),("chainlink","LINK/USDT"),
    ("polkadot","DOT/USDT"),("near","NEAR/USDT"),("uniswap","UNI/USDT"),
    ("litecoin","LTC/USDT"),("cosmos","ATOM/USDT"),("aptos","APT/USDT"),
    ("sui","SUI/USDT"),("arbitrum","ARB/USDT"),("optimism","OP/USDT"),
    ("injective-protocol","INJ/USDT"),("render-token","RENDER/USDT"),
    ("aave","AAVE/USDT"),("maker","MKR/USDT"),("pepe","PEPE/USDT"),
    ("shiba-inu","SHIB/USDT"),("tron","TRX/USDT"),("stellar","XLM/USDT"),
    ("filecoin","FIL/USDT"),("hedera","HBAR/USDT"),("fantom","FTM/USDT"),
    ("the-sandbox","SAND/USDT"),("decentraland","MANA/USDT"),("stacks","STX/USDT"),
    ("curve-dao-token","CRV/USDT"),("gala","GALA/USDT"),("vechain","VET/USDT"),
    ("internet-computer","ICP/USDT"),("the-graph","GRT/USDT"),
    ("algorand","ALGO/USDT"),("theta-token","THETA/USDT"),("tezos","XTZ/USDT"),
    ("monero","XMR/USDT"),("zcash","ZEC/USDT"),("1inch","1INCH/USDT"),
    ("ocean-protocol","OCEAN/USDT"),("band-protocol","BAND/USDT"),
    ("lido-dao","LDO/USDT"),("compound-governance-token","COMP/USDT"),
    ("synthetix-network-token","SNX/USDT"),("axie-infinity","AXS/USDT"),
    ("enjincoin","ENJ/USDT"),
    # ── 100 New Coins ──
    ("sei-network","SEI/USDT"),("celestia","TIA/USDT"),("pyth-network","PYTH/USDT"),
    ("jupiter","JUP/USDT"),("jito-governance-token","JTO/USDT"),("wormhole","W/USDT"),
    ("tensor","TNSR/USDT"),("parcl","PRCL/USDT"),("saga","SAGA/USDT"),
    ("zksync","ZK/USDT"),("layerzero","ZRO/USDT"),("eigen-layer","EIGEN/USDT"),
    ("scroll","SCR/USDT"),("taiko","TAIKO/USDT"),("blast","BLAST/USDT"),
    ("manta-network","MANTA/USDT"),("mantle","MNT/USDT"),("wld","WLD/USDT"),
    ("worldcoin-wld","WLD/USDT"),("dydx","DYDX/USDT"),
    ("gmx","GMX/USDT"),("gains-network","GNS/USDT"),("kwenta","KWENTA/USDT"),
    ("pendle","PENDLE/USDT"),("ethena","ENA/USDT"),("renzo","REZ/USDT"),
    ("puffer-finance","PUFFER/USDT"),("kelp-dao-restaked-eth","RSETH/USDT"),
    ("notcoin","NOT/USDT"),("dogs-2","DOGS/USDT"),("hamster-kombat","HMSTR/USDT"),
    ("catizen","CATI/USDT"),("major","MAJOR/USDT"),
    ("bonk","BONK/USDT"),("dogwifcoin","WIF/USDT"),("book-of-meme","BOME/USDT"),
    ("popcat","POPCAT/USDT"),("mog-coin","MOG/USDT"),("brett-based","BRETT/USDT"),
    ("floki","FLOKI/USDT"),("baby-doge-coin","BABYDOGE/USDT"),
    ("kaspa","KAS/USDT"),("conflux-token","CFX/USDT"),("nervos-network","CKB/USDT"),
    ("immutable-x","IMX/USDT"),("ronin","RON/USDT"),("illuvium","ILV/USDT"),
    ("gods-unchained","GODS/USDT"),("alien-worlds","TLM/USDT"),("stepn","GMT/USDT"),
    ("magic","MAGIC/USDT"),("treasure","MAGIC/USDT"),
    ("blur","BLUR/USDT"),("looks-rare","LOOKS/USDT"),("x2y2","X2Y2/USDT"),
    ("sudoswap","SUDO/USDT"),
    ("fetch-ai","FET/USDT"),("singularitynet","AGIX/USDT"),("ocean-protocol","OCEAN/USDT"),
    ("artificial-superintelligence-alliance","FET/USDT"),
    ("numeraire","NMR/USDT"),("cortex","CTXC/USDT"),("matrix-ai-network","MAN/USDT"),
    ("chaingpt","CGPT/USDT"),
    ("helium","HNT/USDT"),("iotex","IOTX/USDT"),("deeper-network","DPR/USDT"),
    ("akash-network","AKT/USDT"),("flux","FLUX/USDT"),("storj","STORJ/USDT"),
    ("arweave","AR/USDT"),("siacoin","SC/USDT"),
    ("terra-luna-2","LUNA/USDT"),("oasis-network","ROSE/USDT"),
    ("harmony","ONE/USDT"),("icon","ICX/USDT"),("ontology","ONT/USDT"),
    ("wax","WAXP/USDT"),("eos","EOS/USDT"),("neo","NEO/USDT"),
    ("waves","WAVES/USDT"),("iota","IOTA/USDT"),("nano","XNO/USDT"),
    ("ravencoin","RVN/USDT"),("digibyte","DGB/USDT"),("horizen","ZEN/USDT"),
    ("syscoin","SYS/USDT"),("stratis","STRAX/USDT"),
    ("ankr","ANKR/USDT"),("celer-network","CELR/USDT"),("power-ledger","POWR/USDT"),
    ("origintrail","TRAC/USDT"),("quant-network","QNT/USDT"),
    ("civic","CVC/USDT"),("request-network","REQ/USDT"),
    ("status","SNT/USDT"),("loopring","LRC/USDT"),("skale","SKL/USDT"),
    ("omisego","OMG/USDT"),("woo-network","WOO/USDT"),("dusk-network","DUSK/USDT"),
    ("moonbeam","GLMR/USDT"),("moonriver","MOVR/USDT"),("clover-finance","CLV/USDT"),
    ("celo","CELO/USDT"),("uma","UMA/USDT"),("badger-dao","BADGER/USDT"),
    ("harvest-finance","FARM/USDT"),("alpha-finance","ALPHA/USDT"),
    ("bancor","BNT/USDT"),("balancer","BAL/USDT"),("kyber-network","KNC/USDT"),
    ("tornado-cash","TORN/USDT"),("keep-network","KEEP/USDT"),
]

# ─────────────────────────────────────────
#  TELEGRAM
# ─────────────────────────────────────────
def tg(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": CHAT, "text": msg, "parse_mode": "HTML"}, timeout=10)
    except Exception as e:
        log.error(f"TG: {e}")

# ─────────────────────────────────────────
#  COINGECKO
# ─────────────────────────────────────────
def get_ohlc(coin_id, days=14):
    try:
        r = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc",
            params={"vs_currency": "usd", "days": days}, timeout=15)
        if r.status_code == 200:
            d = r.json()
            if len(d) >= 40: return d
    except Exception as e:
        log.warning(f"OHLC {coin_id}: {e}")
    return None

def get_price_data(coin_id):
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price",
            params={"ids": coin_id, "vs_currencies": "usd",
                    "include_24hr_change": "true"}, timeout=10)
        if r.status_code == 200:
            d = r.json().get(coin_id, {})
            return d.get("usd", 0), d.get("usd_24h_change", 0)
    except: pass
    return 0, 0

# ─────────────────────────────────────────
#  INDICATORS
# ─────────────────────────────────────────
def ema(prices, n):
    k = 2/(n+1); e = [prices[0]]
    for p in prices[1:]: e.append(p*k + e[-1]*(1-k))
    return e

def rsi(prices, n=14):
    g = [max(prices[i]-prices[i-1],0) for i in range(1,len(prices))]
    l = [max(prices[i-1]-prices[i],0) for i in range(1,len(prices))]
    if len(g)<n: return 50
    ag=sum(g[-n:])/n; al=sum(l[-n:])/n
    return 100 if al==0 else 100-(100/(1+ag/al))

def atr(highs, lows, closes, n=14):
    trs=[max(highs[i]-lows[i],abs(highs[i]-closes[i-1]),
             abs(lows[i]-closes[i-1])) for i in range(1,len(closes))]
    return sum(trs[-n:])/n if len(trs)>=n else 0

def swing_levels(highs, lows, lookback=12):
    sh = max(highs[-lookback:])
    sl = min(lows[-lookback:])
    psh = max(highs[-lookback*2:-lookback]) if len(highs)>=lookback*2 else max(highs[:lookback])
    psl = min(lows[-lookback*2:-lookback])  if len(lows)>=lookback*2  else min(lows[:lookback])
    return sh, sl, psh, psl

def rejection_candle(o, h, l, c):
    body = abs(c-o)
    if body==0: return False, False
    lw = min(o,c)-l
    uw = h-max(o,c)
    return lw>=2*body and c>o, uw>=2*body and c<o

# ─────────────────────────────────────────
#  LIQUIDITY GRAB DETECTION
# ─────────────────────────────────────────
def detect_grab(opens, highs, lows, closes):
    if len(closes)<30: return None,0,[],0,0,0,0
    o,h,l,c = opens[-1],highs[-1],lows[-1],closes[-1]
    vols = [(hi-lo)*cl for hi,lo,cl in zip(highs,lows,closes)]
    avg_vol = sum(vols[-11:-1])/10 if len(vols)>10 else 1
    vol_spike = vols[-1] > avg_vol*1.3
    sh,sl,psh,psl = swing_levels(highs[:-1], lows[:-1])
    bull_rej, bear_rej = rejection_candle(o,h,l,c)
    e21 = ema(closes,21); e50 = ema(closes,50)
    rsi_val = rsi(closes)
    atr_val = atr(highs,lows,closes)

    # LONG
    bs=0; bt=[]
    if l<sl and c>sl:    bs+=3; bt.append(f"Liq grab below swing low {fmt(sl)}")
    if bull_rej:         bs+=2; bt.append("Bullish pin bar / hammer")
    if vol_spike:        bs+=1; bt.append("Volume spike confirmed")
    if rsi_val<65:       bs+=1; bt.append(f"RSI healthy ({rsi_val:.0f})")
    if c>e21[-1]*0.995:  bs+=1; bt.append("EMA21 support")
    if abs(l-psl)/max(psl,1)<0.015: bs+=1; bt.append("Double bottom zone")

    # SHORT
    ss=0; st=[]
    if h>sh and c<sh:    ss+=3; st.append(f"Liq grab above swing high {fmt(sh)}")
    if bear_rej:         ss+=2; st.append("Bearish pin bar / shooting star")
    if vol_spike:        ss+=1; st.append("Volume spike confirmed")
    if rsi_val>35:       ss+=1; st.append(f"RSI healthy ({rsi_val:.0f})")
    if c<e21[-1]*1.005:  ss+=1; st.append("EMA21 resistance")
    if abs(h-psh)/max(psh,1)<0.015: ss+=1; st.append("Double top zone")

    if bs>=4 and bs>ss: return "LONG",bs,bt,rsi_val,atr_val,sl,sh
    if ss>=4 and ss>bs: return "SHORT",ss,st,rsi_val,atr_val,sl,sh
    return None,0,[],rsi_val,atr_val,sl,sh

# ─────────────────────────────────────────
#  FORMAT
# ─────────────────────────────────────────
def fmt(v):
    if v>=1000:   return f"{v:,.2f}"
    elif v>=1:    return f"{v:.4f}"
    elif v>=0.01: return f"{v:.6f}"
    else:         return f"{v:.8f}"

def pnl_emoji(v):
    return "📈" if v>=0 else "📉"

def conf(score):
    return min(round(55+(score/8)*42,1), 97.5)

# ─────────────────────────────────────────
#  OPEN PAPER TRADE
# ─────────────────────────────────────────
def open_trade(state, coin_id, pair, direction, price, score, tags, sl_level, sh_level):
    bal = state["balance"]
    size = round(bal * RISK_PCT, 4)
    if size < 0.5: return

    p = price
    if direction=="LONG":
        sl  = round(min(p*(1-SL_PCT), sl_level*0.995), 8)
        tp1 = round(p*(1+TP1_PCT), 8)
        tp2 = round(p*(1+TP2_PCT), 8)
        tp3 = round(p*(1+TP3_PCT), 8)
    else:
        sl  = round(max(p*(1+SL_PCT), sh_level*1.005), 8)
        tp1 = round(p*(1-TP1_PCT), 8)
        tp2 = round(p*(1-TP2_PCT), 8)
        tp3 = round(p*(1-TP3_PCT), 8)

    state["open_trades"][coin_id] = {
        "pair": pair, "direction": direction,
        "entry": p, "size": size,
        "sl": sl, "tp1": tp1, "tp2": tp2, "tp3": tp3,
        "tph": 0, "score": score,
        "opened": datetime.now().strftime("%b %d %H:%M"),
        "tags": tags[:2]
    }
    state["balance"] = round(bal - size, 4)
    return sl, tp1, tp2, tp3

# ─────────────────────────────────────────
#  SIGNAL MESSAGE
# ─────────────────────────────────────────
def signal_msg(pair, direction, price, change_24h, tags, score, rsi_val, sl, tp1, tp2, tp3, size, balance):
    arrow = "🟢" if direction=="LONG" else "🔴"
    el = round(price*0.999,8); eh = round(price*1.002,8)
    c = conf(score)
    setup = "Liquidity Sweep + Bullish Reversal" if direction=="LONG" else "Liquidity Sweep + Bearish Reversal"
    reason = tags[0] if tags else setup
    return (
        f"🚀 <b>AI SIGNAL IS READY</b>\n\n"
        f"📊 <b>Pair:</b> {pair}\n"
        f"{arrow} <b>Direction:</b> {direction}\n"
        f"🎯 <b>Entry Zone:</b> {fmt(el)} – {fmt(eh)}\n"
        f"🛡 <b>Stop Loss:</b> {fmt(sl)}\n\n"
        f"🎯 <b>Take Profits:</b>\n"
        f"1️⃣  {fmt(tp1)}\n"
        f"2️⃣  {fmt(tp2)}\n"
        f"3️⃣  {fmt(tp3)}\n\n"
        f"🧠 <b>Confidence:</b> {c}%\n"
        f"{reason}\n\n"
        f"📈 <b>24h Change:</b> {change_24h:+.2f}%\n"
        f"RSI: {rsi_val:.1f} | Confirmations: {score}/8\n"
        f"💼 <b>Trade Size:</b> ${size:.2f} | Balance: ${balance:.2f}\n"
        f"Setup: <b>{setup}</b>\n"
        f"⏰ {datetime.now().strftime('%b %d, %Y, %I:%M %p')}"
    )

# ─────────────────────────────────────────
#  CHECK EXITS
# ─────────────────────────────────────────
def check_exits(state):
    to_close = []
    for coin_id, t in state["open_trades"].items():
        price, _ = get_price_data(coin_id)
        if price==0: continue
        p=price; il=t["direction"]=="LONG"
        tps=[t["tp1"],t["tp2"],t["tp3"]]
        hit_sl=(p<=t["sl"]) if il else (p>=t["sl"])
        nth=t["tph"]
        for i,tp in enumerate(tps):
            if il and p>=tp and i>=t["tph"]: nth=i+1
            elif not il and p<=tp and i>=t["tph"]: nth=i+1

        if nth>t["tph"]:
            state["open_trades"][coin_id]["tph"]=nth
            pct=[TP1_PCT,TP2_PCT,TP3_PCT][nth-1]
            profit=round(t["size"]*pct*(1 if il else -1),4)
            roi=round(pct*100*(1 if il else -1),2)
            tg(
                f"✅ <b>TP{nth} HIT!</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📌 <b>{t['pair']}</b> {t['direction']}\n"
                f"📥 Entry: {fmt(t['entry'])}\n"
                f"📤 Exit: {fmt(p)}\n"
                f"📈 ROI: <b>+{roi}%</b>\n"
                f"💰 Profit: <b>+${profit}</b>\n"
                f"{'🏆 All TPs hit! Close the trade!' if nth==3 else '🛡 Move SL to breakeven now!'}\n"
                f"Congratulations on your profit! 🎉"
            )
            if nth==3:
                final_pnl=round(t["size"]*TP3_PCT*(1 if il else -1),4)
                state["balance"]=round(state["balance"]+t["size"]+final_pnl,4)
                state["total_pnl"]=round(state["total_pnl"]+final_pnl,4)
                state["wins"]+=1
                state["closed_trades"].append({
                    "pair":t["pair"],"direction":t["direction"],
                    "entry":t["entry"],"exit":p,
                    "pnl":final_pnl,"roi":round(TP3_PCT*100,2),
                    "result":"TP3","size":t["size"],
                    "opened":t["opened"],
                    "closed":datetime.now().strftime("%b %d %H:%M")
                })
                to_close.append(coin_id)
                time.sleep(1)

        if hit_sl and coin_id not in to_close:
            loss=round(t["size"]*SL_PCT,4)
            state["balance"]=round(state["balance"]+t["size"]-loss,4)
            state["total_pnl"]=round(state["total_pnl"]-loss,4)
            state["losses"]+=1
            roi=-round(SL_PCT*100,2)
            state["closed_trades"].append({
                "pair":t["pair"],"direction":t["direction"],
                "entry":t["entry"],"exit":p,
                "pnl":-loss,"roi":roi,
                "result":"SL","size":t["size"],
                "opened":t["opened"],
                "closed":datetime.now().strftime("%b %d %H:%M")
            })
            tg(
                f"❌ <b>STOP LOSS HIT</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📌 <b>{t['pair']}</b> {t['direction']}\n"
                f"📥 Entry: {fmt(t['entry'])}\n"
                f"📤 Exit: {fmt(p)}\n"
                f"📉 ROI: <b>{roi}%</b>\n"
                f"💸 Loss: <b>-${loss}</b>\n"
                f"💼 Balance: <b>${state['balance']:.2f}</b>"
            )
            to_close.append(coin_id)
            time.sleep(1)

    for c in to_close:
        del state["open_trades"][c]

# ─────────────────────────────────────────
#  PORTFOLIO REPORT
# ─────────────────────────────────────────
def portfolio_report(state):
    bal = state["balance"]
    total_pnl = state["total_pnl"]
    wins = state["wins"]
    losses = state["losses"]
    total = wins+losses
    wr = round(wins/total*100,1) if total>0 else 0
    growth = round((bal-PAPER_BAL)/PAPER_BAL*100,2)
    open_t = state["open_trades"]

    # Open trades unrealized PnL
    unreal = 0.0
    open_lines = ""
    for cid, t in open_t.items():
        price, _ = get_price_data(cid)
        if price>0:
            if t["direction"]=="LONG":
                upnl=round((price-t["entry"])/t["entry"]*t["size"],4)
            else:
                upnl=round((t["entry"]-price)/t["entry"]*t["size"],4)
            unreal+=upnl
            em="📈" if upnl>=0 else "📉"
            open_lines+=f"  {em} {t['pair']} {t['direction']} | Entry:{fmt(t['entry'])} | uPnL:${upnl:+.4f}\n"
        time.sleep(1.5)

    # Last 5 closed trades
    recent = state["closed_trades"][-5:]
    closed_lines=""
    for ct in reversed(recent):
        em="✅" if ct["result"]!="SL" else "❌"
        closed_lines+=f"  {em} {ct['pair']} {ct['direction']} | {ct['result']} | ${ct['pnl']:+.4f} ({ct['roi']:+.2f}%) | {ct['closed']}\n"

    msg=(
        f"📊 <b>PORTFOLIO REPORT</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"💼 <b>Balance:</b> ${bal:.4f}\n"
        f"🚀 <b>Started with:</b> ${PAPER_BAL:.2f}\n"
        f"{'📈' if growth>=0 else '📉'} <b>Growth:</b> {growth:+.2f}%\n"
        f"💰 <b>Realized PnL:</b> ${total_pnl:+.4f}\n"
        f"📊 <b>Unrealized PnL:</b> ${unreal:+.4f}\n"
        f"🏆 <b>Total PnL:</b> ${total_pnl+unreal:+.4f}\n\n"
        f"📈 <b>Trades:</b> {total} | ✅ Wins: {wins} | ❌ Losses: {losses}\n"
        f"🎯 <b>Win Rate:</b> {wr}%\n\n"
        f"🔄 <b>Open Trades ({len(open_t)}):</b>\n"
        f"{open_lines if open_lines else '  None\n'}\n"
        f"📋 <b>Last 5 Closed:</b>\n"
        f"{closed_lines if closed_lines else '  None yet\n'}\n"
        f"⏰ {datetime.now().strftime('%b %d, %Y %H:%M')}"
    )
    tg(msg)

# ─────────────────────────────────────────
#  MAIN LOOP
# ─────────────────────────────────────────
def main():
    state = load_state()
    state["scan_count"] = state.get("scan_count", 0)
    fired = set(state.get("fired", []))

    log.info("Bot starting — Liquidity Grab Strategy")
    tg(
        f"🤖 <b>AI CRYPTO BOT RESTARTED</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📌 Coins: <b>{len(COINS)}</b> | Timeframe: <b>1H</b>\n"
        f"💼 Balance: <b>${state['balance']:.4f}</b>\n"
        f"📊 Realized PnL: <b>${state['total_pnl']:+.4f}</b>\n"
        f"🏆 Trades: {state['wins']+state['losses']} | "
        f"Wins: {state['wins']} | Losses: {state['losses']}\n"
        f"🔄 Open Trades: {len(state['open_trades'])}\n"
        f"📡 Strategy: Liquidity Grab + Price Action\n"
        f"⚠️ <i>PAPER TRADING MODE</i>"
    )

    last_report = time.time()
    last_cmd_check = time.time()

    while True:
        try:
            # Check for Telegram commands every 30 seconds
            if time.time()-last_cmd_check > 30:
                handle_commands(state)
                last_cmd_check = time.time()
            state["scan_count"] += 1
            scan = state["scan_count"]
            log.info(f"Scan #{scan} — {datetime.now().strftime('%H:%M:%S')}")

            # Check exits first
            if state["open_trades"]:
                check_exits(state)
                save_state({**state, "fired": list(fired)})

            signals = 0
            for coin_id, pair in COINS:
                try:
                    data = get_ohlc(coin_id, days=14)
                    if not data or len(data)<40:
                        time.sleep(2); continue

                    opens  = [c[1] for c in data]
                    highs  = [c[2] for c in data]
                    lows   = [c[3] for c in data]
                    closes = [c[4] for c in data]

                    direction,score,tags,rsi_val,atr_val,sl_lvl,sh_lvl = detect_grab(opens,highs,lows,closes)

                    if direction:
                        hour_key = datetime.now().strftime('%Y%m%d%H')
                        fkey = f"{coin_id}_{direction}_{hour_key}"
                        if fkey not in fired and coin_id not in state["open_trades"]:
                            price, change_24h = get_price_data(coin_id)
                            if price==0: time.sleep(1); continue
                            result = open_trade(state,coin_id,pair,direction,price,score,tags,sl_lvl,sh_lvl)
                            if result:
                                sl,tp1,tp2,tp3 = result
                                size = state["open_trades"][coin_id]["size"]
                                msg = signal_msg(pair,direction,price,change_24h,
                                                 tags,score,rsi_val,sl,tp1,tp2,tp3,
                                                 size,state["balance"])
                                tg(msg)
                                fired.add(fkey)
                                signals+=1
                                log.info(f"Signal: {direction} {pair} score={score}")
                                save_state({**state,"fired":list(fired)})
                                time.sleep(4)

                    time.sleep(2.5)

                except Exception as e:
                    log.error(f"{pair}: {e}"); time.sleep(2)

            log.info(f"Scan #{scan} done — {signals} new signals — {len(state['open_trades'])} open trades")

            # Portfolio report every 4 hours
            if time.time()-last_report > 4*3600:
                portfolio_report(state)
                last_report = time.time()
                save_state({**state,"fired":list(fired)})

            # Clean old fired keys
            if len(fired)>600:
                old=list(fired)[:250]
                for k in old: fired.discard(k)

        except KeyboardInterrupt:
            tg("🛑 <b>Bot stopped.</b>")
            portfolio_report(state)
            save_state({**state,"fired":list(fired)})
            break
        except Exception as e:
            log.error(f"Loop: {e}"); tg(f"⚠️ Error: {e}")

        log.info(f"Next scan in {CHECK//60} min...")
        time.sleep(CHECK)

# ─────────────────────────────────────────
#  TELEGRAM COMMAND HANDLER
# ─────────────────────────────────────────
last_update_id = 0

def get_updates():
    global last_update_id
    try:
        r = requests.get(
            f"https://api.telegram.org/bot{TOKEN}/getUpdates",
            params={"offset": last_update_id+1, "timeout": 2},
            timeout=8
        )
        if r.status_code==200:
            updates = r.json().get("result", [])
            if updates:
                last_update_id = updates[-1]["update_id"]
            return updates
    except: pass
    return []

def handle_commands(state):
    updates = get_updates()
    for u in updates:
        msg = u.get("message",{})
        text = msg.get("text","").strip().lower()
        chat_id = msg.get("chat",{}).get("id")
        if chat_id != CHAT: continue

        if text in ["/balance", "balance", "/bal"]:
            cmd_balance(state)
        elif text in ["/trades", "/open", "trades", "open trades"]:
            cmd_open_trades(state)
        elif text in ["/portfolio", "/report", "portfolio", "/p"]:
            portfolio_report(state)
        elif text in ["/history", "/closed", "history"]:
            cmd_history(state)
        elif text in ["/stats", "stats"]:
            cmd_stats(state)
        elif text in ["/help", "help", "/start"]:
            cmd_help()

def cmd_help():
    tg(
        "🤖 <b>BOT COMMANDS</b>\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "/balance — Current balance & growth\n"
        "/trades — All open trades with live PnL\n"
        "/portfolio — Full portfolio report\n"
        "/history — Last 10 closed trades\n"
        "/stats — Win rate & performance stats\n"
        "/help — Show this menu\n\n"
        "<i>Commands work anytime — reply is instant!</i>"
    )

def cmd_balance(state):
    bal = state["balance"]
    pnl = state["total_pnl"]
    growth = round((bal-PAPER_BAL)/PAPER_BAL*100,2)
    open_count = len(state["open_trades"])
    em = "📈" if growth>=0 else "📉"
    tg(
        f"💼 <b>BALANCE</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"💵 Available: <b>${bal:.4f}</b>\n"
        f"🚀 Started: <b>${PAPER_BAL:.2f}</b>\n"
        f"{em} Growth: <b>{growth:+.2f}%</b>\n"
        f"💰 Realized PnL: <b>${pnl:+.4f}</b>\n"
        f"🔄 Open Trades: <b>{open_count}</b>\n"
        f"⏰ {datetime.now().strftime('%H:%M:%S')}"
    )

def cmd_open_trades(state):
    open_t = state["open_trades"]
    if not open_t:
        tg("🔄 <b>No open trades right now.</b>\n\nBot is scanning for setups...")
        return
    lines = f"🔄 <b>OPEN TRADES ({len(open_t)})</b>\n━━━━━━━━━━━━━━━━━━━\n"
    total_upnl = 0.0
    for cid, t in open_t.items():
        price, _ = get_price_data(cid)
        if price>0:
            if t["direction"]=="LONG":
                upnl = round((price-t["entry"])/t["entry"]*t["size"],4)
                roi  = round((price-t["entry"])/t["entry"]*100,2)
            else:
                upnl = round((t["entry"]-price)/t["entry"]*t["size"],4)
                roi  = round((t["entry"]-price)/t["entry"]*100,2)
            total_upnl += upnl
            em = "📈" if upnl>=0 else "📉"
            arrow = "🟢" if t["direction"]=="LONG" else "🔴"
            tph = t.get("tph",0)
            tp_status = f"TP{tph} hit ✅" if tph>0 else "Waiting..."
            lines += (
                f"\n{arrow} <b>{t['pair']}</b> {t['direction']}\n"
                f"   Entry: {fmt(t['entry'])} → Now: {fmt(price)}\n"
                f"   {em} uPnL: <b>${upnl:+.4f} ({roi:+.2f}%)</b>\n"
                f"   Size: ${t['size']:.2f} | {tp_status}\n"
                f"   SL: {fmt(t['sl'])} | TP3: {fmt(t['tp3'])}\n"
                f"   Opened: {t['opened']}\n"
            )
        time.sleep(1.2)
    lines += f"\n💰 Total Unrealized PnL: <b>${total_upnl:+.4f}</b>"
    tg(lines)

def cmd_history(state):
    closed = state["closed_trades"]
    if not closed:
        tg("📋 <b>No closed trades yet.</b>")
        return
    recent = closed[-10:]
    lines = f"📋 <b>LAST {len(recent)} CLOSED TRADES</b>\n━━━━━━━━━━━━━━━━━━━\n"
    total = sum(t["pnl"] for t in recent)
    for ct in reversed(recent):
        em = "✅" if ct["result"]!="SL" else "❌"
        arrow = "🟢" if ct["direction"]=="LONG" else "🔴"
        lines += (
            f"\n{em} {arrow} <b>{ct['pair']}</b> {ct['direction']}\n"
            f"   Entry: {fmt(ct['entry'])} → Exit: {fmt(ct['exit'])}\n"
            f"   PnL: <b>${ct['pnl']:+.4f} ({ct['roi']:+.2f}%)</b> | {ct['result']}\n"
            f"   {ct['opened']} → {ct['closed']}\n"
        )
    lines += f"\n💰 Combined PnL (last {len(recent)}): <b>${total:+.4f}</b>"
    tg(lines)

def cmd_stats(state):
    wins = state["wins"]
    losses = state["losses"]
    total = wins+losses
    wr = round(wins/total*100,1) if total>0 else 0
    bal = state["balance"]
    growth = round((bal-PAPER_BAL)/PAPER_BAL*100,2)
    avg_win  = round(PAPER_BAL*RISK_PCT*TP3_PCT,4)
    avg_loss = round(PAPER_BAL*RISK_PCT*SL_PCT,4)
    rr = round(TP3_PCT/SL_PCT,1)
    tg(
        f"📊 <b>PERFORMANCE STATS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🏆 Total Trades: <b>{total}</b>\n"
        f"✅ Wins: <b>{wins}</b> | ❌ Losses: <b>{losses}</b>\n"
        f"🎯 Win Rate: <b>{wr}%</b>\n"
        f"💰 Realized PnL: <b>${state['total_pnl']:+.4f}</b>\n"
        f"📈 Balance Growth: <b>{growth:+.2f}%</b>\n"
        f"⚖️ Risk/Reward: <b>1:{rr}</b>\n"
        f"🔄 Open Now: <b>{len(state['open_trades'])}</b>\n"
        f"🔍 Coins Watched: <b>{len(COINS)}</b>\n"
        f"📡 Scans Done: <b>{state.get('scan_count',0)}</b>\n"
        f"⏰ {datetime.now().strftime('%b %d, %Y %H:%M')}"
    )

if __name__=="__main__":
    main()
