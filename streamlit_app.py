import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote
import ssl
from datetime import datetime
import concurrent.futures

# --- 1. EXCLUSION LIST ---
# Sourced from your provided image.
EXCLUDED_SOURCES = [
    "simplywall.st", "Yahoo Finance", "reminetwork.com",
    "The Motley Fool Canada", "mission.ca", "TBNewsWatch.com",
    "Finimize", "Weekly Voice", "Stock Traders Daily", "AD HOC NEWS",
    "Moomoo", "eKathimerini.com", "Binance", "MarketBeat",
    "Seeking Alpha", "GuruFocus", "Investing.com Canada", "kare11.com",
    "WKYC", "Sahm", "Morningstar", "NBA", "Semiconductor Industry Association | SIA",
    "Dailyhunt", "MarketWatch", "Yahoo! Finance Canada", "Music Talkers",
    "People.com", "Yahoo News Canada", "ChartMill", "Travel And Tour World",
    "Croatia Week", "Shop Eat Surf Outdoor", "The J-Notes", "defenceWeb",
    "Firefighter Nation", "Manila Bulletin", "Evertiq", "The Times of India"
]

# --- 2. DATA STRUCTURE ---
COVERAGE = {
    "Cameco Saskatchewan": {"ticker": "CCO.TO", "full_name": "Cameco Corporation", "ref_names": ["Cameco Saskatchewan", "Cameco"]},
    "LNG Canada Phase 2": {"ticker": "PRIVATE", "full_name": "LNG Canada Phase 2 Project", "ref_names": ["LNG Canada Phase 2", "LNG Canada"]},
    "Denison Phoenix": {"ticker": "DML.TO", "full_name": "Denison Mines Corp. - Phoenix Deposit", "ref_names": ["Denison Phoenix", "Denison Mines", "Phoenix Deposit"]},
    "Cameco Uranium City": {"ticker": "CCO.TO", "full_name": "Cameco Corporation - Uranium City Operations", "ref_names": ["Cameco Uranium City", "Uranium City"]},
    "Ksi Lisims": {"ticker": "PRIVATE", "full_name": "Ksi Lisims LNG Project", "ref_names": ["Ksi Lisims", "Ksi Lisims LNG"]},
    "West Coast Pipeline": {"ticker": "PRIVATE", "full_name": "West Coast Oil Pipeline Project", "ref_names": ["West Coast Pipeline", "West Coast Oil Pipeline"]},
    "Pacific Link": {"ticker": "PPL.TO", "full_name": "Pacific Link Pipeline Project (Pembina / Trans Mountain / GoA)", "ref_names": ["Pacific Link", "Pacific Link Pipeline", "West Coast Oil Pipeline"]},
    "PRGT": {"ticker": "PRIVATE", "full_name": "Prince Rupert Gas Transmission Pipeline", "ref_names": ["PRGT", "Prince Rupert Gas Transmission"]},
    "Prince Rupert Gas Transmission": {"ticker": "PRIVATE", "full_name": "Prince Rupert Gas Transmission Pipeline", "ref_names": ["Prince Rupert Gas Transmission", "PRGT"]},
    "Newmont Red Chris Expansion": {"ticker": "NGT.TO", "full_name": "Newmont Corporation - Red Chris Mine Expansion", "ref_names": ["Newmont Red Chris Expansion", "Red Chris Mine", "Newmont Red Chris"]},
    "Artemis Gold": {"ticker": "ARTG.V", "full_name": "Artemis Gold Inc.", "ref_names": ["Artemis Gold", "Blackwater Mine"]},
    "NexGen": {"ticker": "NXE.TO", "full_name": "NexGen Energy Ltd.", "ref_names": ["NexGen", "NexGen Energy", "Rook I"]},
    "Ring of Fire": {"ticker": "INFRA", "full_name": "Ring of Fire Mining Region Infrastructure", "ref_names": ["Ring of Fire"]},
    "Northcliff Sisson Mine": {"ticker": "NCF.V", "full_name": "Northcliff Resources Ltd. - Sisson Tungsten-Molybdenum Project", "ref_names": ["Northcliff Sisson Mine", "Sisson Mine", "Northcliff Resources"]},
    "Canada Nickel Crawford Project": {"ticker": "CNC.V", "full_name": "Canada Nickel Company Inc. - Crawford Nickel Project", "ref_names": ["Canada Nickel Crawford Project", "Canada Nickel", "Crawford Nickel"]},
    "Taltson Hydro Expansion": {"ticker": "GOV", "full_name": "Taltson Hydro Expansion Project (NWT)", "ref_names": ["Taltson Hydro Expansion", "Taltson Hydro"]},
    "North Coast Transmission Line": {"ticker": "INFRA", "full_name": "North Coast Transmission Line Project", "ref_names": ["North Coast Transmission Line", "North Coast Transmission"]},
    "Iqaluit Nukkiksautiit Hydro Project": {"ticker": "INFRA", "full_name": "Iqaluit Nukkiksautiit Hydro Project", "ref_names": ["Iqaluit Nukkiksautiit Hydro Project", "Nukkiksautiit Hydro"]},
    "Mackenzie Valley Highway": {"ticker": "INFRA", "full_name": "Mackenzie Valley Highway Infrastructure Project", "ref_names": ["Mackenzie Valley Highway"]},
    "Grays Bay Road and Port": {"ticker": "INFRA", "full_name": "Grays Bay Road and Port Project", "ref_names": ["Grays Bay Road and Port", "Grays Bay"]},
    "Arctic Economic and Security Corridor": {"ticker": "INFRA", "full_name": "Arctic Economic and Security Corridor Project", "ref_names": ["Arctic Economic and Security Corridor", "Arctic Economic Corridor"]},
    "Conagra Brands": {"ticker": "CAG", "full_name": "Conagra Brands, Inc.", "ref_names": ["Conagra Brands", "Conagra"]},
    "Premium Brands": {"ticker": "PBH.TO", "full_name": "Premium Brands Holdings Corporation", "ref_names": ["Premium Brands Holdings", "Premium Brands"]},
    "Sysco": {"ticker": "SYY", "full_name": "Sysco Corporation", "ref_names": ["Sysco Corporation", "Sysco"]},
    "Gordon Food Service": {"ticker": "PRIVATE", "full_name": "Gordon Food Service Inc.", "ref_names": ["Gordon Food Service", "GFS"]},
    "Performance Food Group": {"ticker": "PFGC", "full_name": "Performance Food Group Company", "ref_names": ["Performance Food Group", "PFG"]},
    "Hormel Foods": {"ticker": "HRL", "full_name": "Hormel Foods Corporation", "ref_names": ["Hormel Foods", "Hormel"]},
    "Tyson Foods": {"ticker": "TSN", "full_name": "Tyson Foods, Inc.", "ref_names": ["Tyson Foods", "Tyson"]},
    "US Foods": {"ticker": "USFD", "full_name": "US Foods Holding Corp.", "ref_names": ["US Foods Holding", "US Foods"]},
    "QXO": {"ticker": "QXO", "full_name": "QXO, Inc.", "ref_names": ["QXO"]},
    "Richelieu Hardware": {"ticker": "RCH.TO", "full_name": "Richelieu Hardware Ltd.", "ref_names": ["Richelieu Hardware", "Richelieu"]},
    "Builders FirstSource": {"ticker": "BLDR", "full_name": "Builders FirstSource, Inc.", "ref_names": ["Builders FirstSource"]},
    "BlueLinx": {"ticker": "BXC", "full_name": "BlueLinx Holdings Inc.", "ref_names": ["BlueLinx Holdings", "BlueLinx"]},
    "Home Depot": {"ticker": "HD", "full_name": "The Home Depot, Inc.", "ref_names": ["Home Depot"]},
    "Lowe's": {"ticker": "LOW", "full_name": "Lowe's Companies, Inc.", "ref_names": ["Lowe's Companies", "Lowe's"]},
    "BGIS": {"ticker": "PRIVATE", "full_name": "BGIS (Brookfield Global Integrated Solutions)", "ref_names": ["BGIS"]},
    "Aramark": {"ticker": "ARMK", "full_name": "Aramark", "ref_names": ["Aramark Services", "Aramark"]},
    "Sodexo": {"ticker": "SW.PA", "full_name": "Sodexo S.A.", "ref_names": ["Sodexo Canada", "Sodexo"]},
    "Compass": {"ticker": "CPG.L", "full_name": "Compass Group PLC", "ref_names": ["Compass Group", "Compass"]},
    "Securitas": {"ticker": "SECU-B.ST", "full_name": "Securitas AB", "ref_names": ["Securitas Canada", "Securitas"]},
    "ISS": {"ticker": "ISS.CO", "full_name": "ISS A/S", "ref_names": ["ISS Facility Services", "ISS"]},
    "Coor Service Management": {"ticker": "COOR.ST", "full_name": "Coor Service Management Holding AB", "ref_names": ["Coor Service Management", "Coor Service", "Coor"]},
    "ECAMSECURE": {"ticker": "PRIVATE", "full_name": "ECAMSECURE (GardaWorld Company)", "ref_names": ["Ecamsecure", "ECAMSECURE"]},
    "GardaWorld": {"ticker": "PRIVATE", "full_name": "GardaWorld Security Corporation", "ref_names": ["Gardaworld", "GardaWorld Security"]},
    "LiveView Technologies": {"ticker": "PRIVATE", "full_name": "LiveView Technologies, Inc. (LVT)", "ref_names": ["Liveview technologies", "LiveView Technologies", "LVT"]}
}

# --- 3. THE SCANNER ---
def get_google_news(search_term, display_name, validation_list):
    query = quote(f'{search_term} when:100d')
    url = f"https://news.google.com/rss/search?q={query}&hl=en-CA&gl=CA&ceid=CA:en"
    
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context
        
    feed = feedparser.parse(url)
    results = []
    
    for entry in feed.entries[:30]:
        headline = entry.title
        headline_lower = headline.lower()
        
        # HEADLINE VALIDATION: Checking if the company is actually mentioned in the title
        if not any(val.lower() in headline_lower for val in validation_list):
            continue

        parsed_date = entry.get('published_parsed')
        sort_date = datetime(*parsed_date[:6]) if parsed_date else datetime(1900, 1, 1)
        
        source = "Google News"
        if hasattr(entry, 'source'):
            source = entry.source.get('title', 'Google News')
        elif " - " in headline:
            source = headline.split(" - ")[-1]
        
        # --- SOURCE EXCLUSION CHECK ---
        if any(excluded.lower() in source.lower() for excluded in EXCLUDED_SOURCES):
            continue
            
        results.append({
            "sort_key": sort_date,
            "Date": sort_date.strftime('%b %d, %Y'),
            "Company": display_name,
            "Source": source,
            "Headline": headline, 
            "Link": entry.link
        })
    return results

# --- 4. UI ---
st.set_page_config(page_title="REITs News Screener", page_icon="📈", layout="wide")

if 'news_data' not in st.session_state:
    st.session_state.news_data = []

with st.sidebar:
    LOGO_URL = "https://atbcm.atb.com/siteassets/global-components/atb-cormarkcapitalmarkets-logo-1125x1125-white.svg"
    st.image(LOGO_URL, link="https://cormark.com/")
    st.title("Screener Settings")
    
    dropdown_options = ["--- MASTER VIEWS ---", "Entire Coverage"]
    dropdown_options += ["--- INDIVIDUAL NAMES ---"] + sorted(list(COVERAGE.keys()))
    
    selected_view = st.selectbox("Select Watchlist", options=dropdown_options)
    
    st.divider()
    keyword_filter = st.text_input("🔍 Search Headlines", "").strip().lower()

st.title("McPharis's Coverage News Screener")

# --- 5. BUILD SEARCH TASKS ---
search_tasks = []

def build_tasks_for_company(company_key):
    company_data = COVERAGE[company_key]
    ticker = company_data["ticker"]
    full_name = company_data["full_name"]
    ref_names = company_data["ref_names"]
    
    validation_list = [ticker, full_name] + ref_names
    
    search_tasks.append((full_name, company_key, validation_list))
    for ref in ref_names:
        search_tasks.append((ref, company_key, validation_list))
    search_tasks.append((ticker, company_key, validation_list))

if selected_view == "Entire Coverage":
    for company in COVERAGE:
        build_tasks_for_company(company)
elif selected_view in COVERAGE:
    build_tasks_for_company(selected_view)

# --- 6. EXECUTION ---
if not selected_view.startswith("---"):
    if st.button(f"Search {selected_view}", use_container_width=True):
        all_hits = []
        with st.spinner(f'Searching {selected_view}...'):
            with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
                future_to_company = {executor.submit(get_google_news, task[0], task[1], task[2]): task[0] for task in search_tasks}
                for future in concurrent.futures.as_completed(future_to_company):
                    all_hits.extend(future.result())
        st.session_state.news_data = all_hits

# --- 7. DISPLAY & DUPLICATE FILTERING ---
if st.session_state.news_data:
    df = pd.DataFrame(st.session_state.news_data)
    df = df.sort_values(by="sort_key", ascending=False)
    
    # --- ROBUST DUPLICATE FILTER ---
    # Create a normalized headline column to catch duplicates with slight case/spacing variations
    df['normalized_headline'] = df['Headline'].str.lower().str.strip()
    # Drop duplicates globally based on the normalized headline
    df = df.drop_duplicates(subset=['normalized_headline'], keep='first')
    # Remove the temporary column
    df = df.drop(columns=['normalized_headline'])
    
    if keyword_filter:
        df = df[df['Headline'].str.lower().str.contains(keyword_filter)]

    st.success(f"Found {len(df)} headlines.")
    
    st.dataframe(
        df[["Date", "Company", "Source", "Headline", "Link"]], 
        column_config={"Link": st.column_config.LinkColumn("View", display_text="Open")},
        use_container_width=True, 
        hide_index=True
    )
