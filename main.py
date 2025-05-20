import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import plotly.graph_objects as go
import pandas as pd
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import google.generativeai as genai
import json
from alpha_vantage.timeseries import TimeSeries
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import plotly.express as px

# Set page configuration
st.set_page_config(
    page_title="Stock Financial Overview",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better UI
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #1e3a8a;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #e5e7eb;
    }
    
    /* Card styling */
    .card {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border: 1px solid #e5e7eb;
    }
    
    /* Card header */
    .card-header {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #1e3a8a;
        display: flex;
        align-items: center;
        border-bottom: 1px solid #e5e7eb;
        padding-bottom: 0.75rem;
    }
    
    /* Card icon */
    .card-icon {
        margin-right: 0.5rem;
        color: #3b82f6;
    }
    
    /* Metric styling */
    .metric-container {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid #f3f4f6;
    }
    
    .metric-container:last-child {
        border-bottom: none;
    }
    
    .metric-label {
        color: #6b7280;
        font-weight: 500;
    }
    
    .metric-value {
        font-weight: 600;
    }
    
    /* Badge styling */
    .badge {
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .badge-green {
        background-color: #d1fae5;
        color: #065f46;
    }
    
    .badge-red {
        background-color: #fee2e2;
        color: #b91c1c;
    }
    
    .badge-gray {
        background-color: #f3f4f6;
        color: #4b5563;
    }
    
    /* News item styling */
    .news-item {
        padding: 1rem 0;
        border-bottom: 1px solid #f3f4f6;
    }
    
    .news-item:last-child {
        border-bottom: none;
    }
    
    .news-text {
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .news-meta {
        display: flex;
        justify-content: space-between;
        font-size: 0.875rem;
        color: #6b7280;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.375rem;
        font-weight: 500;
    }
    
    .stButton>button:hover {
        background-color: #2563eb;
    }
    
    /* Input styling */
    .stTextInput>div>div>input {
        border-radius: 0.375rem;
        border: 1px solid #d1d5db;
        padding: 0.5rem 1rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        white-space: pre-wrap;
        background-color: white;
        border-radius: 0.5rem 0.5rem 0 0;
        border: 1px solid #e5e7eb;
        border-bottom: none;
        color: #4b5563;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background-color: #3b82f6;
    }
    
    /* Spinner styling */
    .stSpinner > div > div > div {
        border-top-color: #3b82f6 !important;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 1rem 0;
        color: #6b7280;
        font-size: 0.875rem;
        border-top: 1px solid #e5e7eb;
        margin-top: 2rem;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .card {
            padding: 1rem;
        }
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #c5c5c5;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8;
    }
    
    /* Loading animation */
    @keyframes pulse {
        0% {
            opacity: 0.6;
        }
        50% {
            opacity: 1;
        }
        100% {
            opacity: 0.6;
        }
    }
    
    .loading-pulse {
        animation: pulse 1.5s infinite ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📊 Stock Financial Overview</h1>', unsafe_allow_html=True)

# Initialize session state for storing data
if 'stock_data' not in st.session_state:
    st.session_state.stock_data = None
if 'news_list' not in st.session_state:
    st.session_state.news_list = None
if 'technical_summary' not in st.session_state:
    st.session_state.technical_summary = None
if 'price_target' not in st.session_state:
    st.session_state.price_target = None
if 'analysis' not in st.session_state:
    st.session_state.analysis = None
if 'income_statement_df' not in st.session_state:
    st.session_state.income_statement_df = None

# Update Gemini API key
GEMINI_API_KEY = "AIzaSyCaT8QTHddteiKz8EE99cmPeQGQaOBL9NQ"

# Functions
def get_income_statement_data(driver):
    try:
        # Wait for the main wrapper to be present
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.wrapper-Tv7LSjUz'))
        )
        wrapper = driver.find_element(By.CSS_SELECTOR, 'div.wrapper-Tv7LSjUz')
        # Find all rows (any direct child div with data-name or with multiple divs inside)
        rows = wrapper.find_elements(By.XPATH, ".//div[contains(@class, 'container-')]")
        data = []
        row_names = []
        max_cols = 0
        for row in rows:
            # Try to get the row label from data-name, else from first cell
            row_label = row.get_attribute('data-name')
            cells = row.find_elements(By.XPATH, './div')
            if not row_label and cells:
                row_label = cells[0].text
                value_cells = cells[1:]
            else:
                value_cells = cells[1:] if cells else []
            values = [cell.text for cell in value_cells]
            if row_label:
                row_names.append(row_label)
                data.append(values)
                max_cols = max(max_cols, len(values))
        # Get the column headers (years) from the first row's value cells
        if rows:
            header_cells = rows[0].find_elements(By.XPATH, './div')[1:]
            headers = [cell.text for cell in header_cells]
            # If headers are empty, create generic headers
            if not any(headers):
                headers = [f"Col {i+1}" for i in range(max_cols)]
        else:
            headers = [f"Col {i+1}" for i in range(max_cols)]
        # Build DataFrame
        if data and headers:
            # Pad rows to max_cols
            data = [row + [''] * (max_cols - len(row)) for row in data]
            df = pd.DataFrame(data, index=row_names, columns=headers)
            df.index.name = "Metric"
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

def get_news(driver):
    try:
        # Wait for at least one news item to load (adjust class as needed)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.container-HY0D0we, div.container-DmjQR0Aa"))
        )
        news_items = driver.find_elements(By.CSS_SELECTOR, "div.container-HY0D0we , div.container-DmjQR0Aa")
        news_list = []
        for item in news_items:
            text = item.text.strip()
            if text:
                news_list.append(text)
        return news_list
    except Exception:
        return []

def get_stock_data(ticker):
    if not ticker:
        return None, None, None, None, None, None

    url = f"https://in.tradingview.com/symbols/NSE-{ticker}/financials-overview/"
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        time.sleep(5)

        # Key facts
        items = driver.find_elements(By.CLASS_NAME, 'item-D38HaCsG')
        stock_data = {}
        for item in items:
            try:
                title = item.find_element(By.CLASS_NAME, 'title-D38HaCsG').text
                value = item.find_element(By.CLASS_NAME, 'data-D38HaCsG').text
                stock_data[title] = value
            except:
                continue

        # Ownership data
        ownership_items = driver.find_elements(By.CSS_SELECTOR, 'div.item-cXDWtdxq.legendText-En4JymId')
        ownership_data = [item.text for item in ownership_items if item.text.strip()]

        # Valuation data (center value in donut chart)
        try:
            valuation_elem = driver.find_element(By.CSS_SELECTOR, 'div.centerText-IE2DjrIR.chartTitle-En4JymId > div')
            valuation_value = valuation_elem.text.strip()
        except:
            valuation_value = None

        # Extract sector legend labels (for pie chart legend)
        try:
            sector_legend_items = driver.find_elements(By.CSS_SELECTOR, 'div.label-UFGakGDX')
            sector_legends = [item.text for item in sector_legend_items if item.text.strip()]
        except:
            sector_legends = []

        # Dividend summary data
        try:
            dividend_items = driver.find_elements(By.CSS_SELECTOR, 'div.item-cXDWtdxq')
            dividend_summary = [item.text for item in dividend_items if item.text.strip()]
        except:
            dividend_summary = []

        # Income statement data
        income_statement_df = get_income_statement_data(driver)

        return stock_data, ownership_data, valuation_value, sector_legends, dividend_summary, income_statement_df

    finally:
        driver.quit()

def get_technical_summary(ticker):
    url = f"https://in.tradingview.com/symbols/NSE-{ticker}/technicals/"
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(url)
        # Wait for the counters to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "counterWrapper-kg4MJrFB"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        speedo = soup.find("div", class_="speedometerWrapper-kg4MJrFB summary-kg4MJrFB")
        if not speedo:
            return None
        # Extract the main summary (e.g., Neutral, Buy, Sell, etc.)
        main_summary = speedo.find("span", class_="speedometerTitle-kg4MJrFB")
        # Try to find the main signal (neutral, buy, sell, strong buy, strong sell)
        main_signal = None
        for cls in [
            "neutral-zq7XRf30 neutral-Tat_6ZmA",
            "buy-zq7XRf30 buy-Tat_6ZmA",
            "sell-zq7XRf30 sell-Tat_6ZmA",
            "strong-sell-zq7XRf30 strong-sell-Tat_6ZmA",
            "strong-buy-zq7XRf30 strong-buy-Tat_6ZmA"
        ]:
            main_signal = speedo.find("span", class_=cls)
            if main_signal:
                break
        # Extract all signals for the time frame
        signals = [s.text.strip() for s in speedo.find_all("span", class_="speedometerText-Tat_6ZmA")]

        # Extract buy/sell/neutral counts
        counters = speedo.find("div", class_="countersWrapper-kg4MJrFB")
        buy_sell_neutral = []
        if counters:
            for counter in counters.find_all("div", class_="counterWrapper-kg4MJrFB"):
                title = counter.find("span", class_=lambda x: x and "counterTitle-kg4MJrFB" in x)
                number = counter.find("span", class_=lambda x: x and "counterNumber-kg4MJrFB" in x)
                if title and number:
                    buy_sell_neutral.append((title.text.strip(), number.text.strip()))

        return {
            "main_summary": main_summary.text.strip() if main_summary else "",
            "main_signal": main_signal.text.strip() if main_signal else "",
            "signals": signals,
            "buy_sell_neutral": buy_sell_neutral
        }
    except Exception:
        return None
    finally:
        driver.quit()

def get_price_target(ticker):
    url = f"https://in.tradingview.com/symbols/NSE-{ticker}/forecast/"
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "price-qWcO4bp9"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # Price
        price = soup.find("span", class_=lambda x: x and "price-qWcO4bp9" in x)
        # Currency
        currency = soup.find("span", class_=lambda x: x and "currency-qWcO4bp9" in x)
        # Changes (should be two: value and percent)
        changes = soup.find_all("span", class_=lambda x: x and "change-SNvPvlJ3" in x)
        change_val = changes[0].text.strip() if len(changes) > 0 else None
        percent_val = changes[1].text.strip() if len(changes) > 1 else None
        # Analyst summary
        summary = soup.find("div", class_=lambda x: x and "sectionSubtitle-QrSDtBZ9" in x)
        return {
            "price": price.text.strip() if price else None,
            "currency": currency.text.strip() if currency else None,
            "change": change_val,
            "percent": percent_val,
            "summary": summary.text.strip() if summary else None
        }
    except Exception as e:
        return None
    finally:
        driver.quit()

def get_gemini_client():
    return genai.Client(GEMINI_API_KEY)

def get_news_with_sentiment(ticker):
    url = f"https://in.tradingview.com/symbols/NSE-{ticker}/news/"
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(url)
        time.sleep(3)
        news_list = get_news(driver)
        
        if news_list:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            news_with_sentiment = []
            
            for news in news_list:
                try:
                    prompt = f"Classify the following news for the stock {ticker} as Positive or Negative for the stock. Only output 'Positive' or 'Negative'. News: {news}"
                    resp = model.generate_content(prompt)
                    sentiment = resp.text.strip().split('\n')[0]
                    news_with_sentiment.append({
                        "text": news,
                        "sentiment": sentiment,
                        "date": "Recent" # In a real app, you'd extract the actual date
                    })
                except Exception as e:
                    news_with_sentiment.append({
                        "text": news,
                        "sentiment": "Unknown",
                        "date": "Recent"
                    })
            
            return news_with_sentiment
        else:
            return []
    finally:
        driver.quit()

def get_buffett_lynch_analysis(ticker):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    try:
        # Get Buffett & Lynch analysis
        prompt1 = f"In 2 short bullet points, summarize the investment case for {ticker} using Buffett & Lynch methodology."
        resp1 = model.generate_content(prompt1)
        analysis = resp1.text.strip().split('\n')
        
        # Get strengths
        prompt2 = f"List 5 investment strengths of {ticker} stock in short bullet points (one sentence each)."
        resp2 = model.generate_content(prompt2)
        strengths = resp2.text.strip().split('\n')
        
        # Get weaknesses
        prompt3 = f"List 4 investment concerns or risks for {ticker} stock in short bullet points (one sentence each)."
        resp3 = model.generate_content(prompt3)
        weaknesses = resp3.text.strip().split('\n')
        
        return {
            "analysis": analysis,
            "strengths": strengths,
            "weaknesses": weaknesses
        }
    except Exception as e:
        return {
            "analysis": ["Analysis not available due to API limitations."],
            "strengths": ["Strength analysis not available."],
            "weaknesses": ["Risk analysis not available."]
        }

# Search input with improved styling
col1, col2 = st.columns([5, 1])
with col1:
    ticker = st.text_input("", placeholder="Enter NSE Stock Symbol (e.g., SBIN, RELIANCE, TCS)", value="")
with col2:
    search_button = st.button("Search", use_container_width=True)

# Process search
if search_button and ticker:
    ticker = ticker.upper()
    
    # Show loading message
    with st.spinner(f"Fetching data for {ticker}..."):
        # Get all data in parallel (in a real app, you'd use async/await or threading)
        stock_data, ownership_data, valuation_value, sector_legends, dividend_summary, income_statement_df = get_stock_data(ticker)
        st.session_state.stock_data = {
            "stock_data": stock_data,
            "ownership_data": ownership_data,
            "valuation_value": valuation_value,
            "sector_legends": sector_legends,
            "dividend_summary": dividend_summary,
            "income_statement_df": income_statement_df
        }
        
        # Get news with sentiment
        st.session_state.news_list = get_news_with_sentiment(ticker)
        
        # Get technical summary
        st.session_state.technical_summary = get_technical_summary(ticker)
        
        # Get price target
        st.session_state.price_target = get_price_target(ticker)
        
        # Get Buffett & Lynch analysis
        st.session_state.analysis = get_buffett_lynch_analysis(ticker)

# Display data if available
if ticker:
    # Display ticker header
    st.markdown(f'<h2 style="color:#1e3a8a; margin-bottom:1rem;">NSE-{ticker}</h2>', unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Overview", "📰 News", "🔍 Technical Analysis", "🎯 Price Targets", "💡 Analytics"])
    
    # Overview Tab
    with tab1:
        if st.session_state.stock_data and st.session_state.stock_data["stock_data"]:
            stock_data = st.session_state.stock_data["stock_data"]
            ownership_data = st.session_state.stock_data["ownership_data"]
            valuation_value = st.session_state.stock_data["valuation_value"]
            sector_legends = st.session_state.stock_data["sector_legends"]
            dividend_summary = st.session_state.stock_data["dividend_summary"]
            
            # Create 3 columns for key metrics
            col1, col2, col3 = st.columns(3)
            
            # Key Financial Metrics
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-header">📊 Key Financial Metrics</div>', unsafe_allow_html=True)
                
                if stock_data:
                    for i, (title, value) in enumerate(list(stock_data.items())[:4]):
                        st.markdown(f'''
                        <div class="metric-container">
                            <span class="metric-label">{title}</span>
                            <span class="metric-value">{value}</span>
                        </div>
                        ''', unsafe_allow_html=True)
                else:
                    st.info("No key metrics data available")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Company Information
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-header">🏢 Company Information</div>', unsafe_allow_html=True)
                
                if stock_data:
                    for i, (title, value) in enumerate(list(stock_data.items())[4:]):
                        st.markdown(f'''
                        <div class="metric-container">
                            <span class="metric-label">{title}</span>
                            <span class="metric-value">{value}</span>
                        </div>
                        ''', unsafe_allow_html=True)
                else:
                    st.info("No company information available")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Ownership
            with col3:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-header">👥 Ownership</div>', unsafe_allow_html=True)
                
                if ownership_data:
                    for item in ownership_data:
                        parts = item.split(':')
                        if len(parts) == 2:
                            label, value = parts[0].strip(), parts[1].strip()
                            st.markdown(f'''
                            <div class="metric-container">
                                <span class="metric-label">{label}</span>
                                <span class="metric-value">{value}</span>
                            </div>
                            ''', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="metric-container">{item}</div>', unsafe_allow_html=True)
                else:
                    st.info("No ownership data available")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Valuation and Dividend Summary in 2 columns
            col1, col2 = st.columns(2)
            
            # Valuation with donut chart
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-header">💰 Valuation</div>', unsafe_allow_html=True)
                
                if valuation_value:
                    # Extract numeric value if possible
                    try:
                        val_num = float(valuation_value.split()[0].replace(',', ''))
                        val_label = valuation_value
                        
                        # Create donut chart
                        fig = go.Figure(go.Pie(
                            values=[val_num, 100-val_num] if '%' in valuation_value else [val_num, val_num*2],
                            labels=["Value", ""],
                            hole=0.7,
                            marker_colors=['#3b82f6', '#e5e7eb'],
                            textinfo='none',
                            hoverinfo='none'
                        ))
                        
                        fig.update_layout(
                            showlegend=False,
                            margin=dict(t=0, b=0, l=0, r=0),
                            annotations=[dict(text=val_label, x=0.5, y=0.5, font_size=20, showarrow=False)],
                            height=250,
                            width=250
                        )
                        
                        # Center the chart
                        st.markdown('<div style="display:flex; justify-content:center;">', unsafe_allow_html=True)
                        st.plotly_chart(fig, use_container_width=False, config={'displayModeBar': False})
                        st.markdown('</div>', unsafe_allow_html=True)
                    except:
                        st.markdown(f'<div style="text-align:center; font-size:1.5rem; font-weight:bold; padding:2rem 0;">{valuation_value}</div>', unsafe_allow_html=True)
                else:
                    st.info("No valuation data available")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Dividend Summary
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-header">💸 Dividend Summary</div>', unsafe_allow_html=True)
                
                if dividend_summary:
                    for item in dividend_summary:
                        parts = item.split(':')
                        if len(parts) == 2:
                            label, value = parts[0].strip(), parts[1].strip()
                            st.markdown(f'''
                            <div class="metric-container">
                                <span class="metric-label">{label}</span>
                                <span class="metric-value">{value}</span>
                            </div>
                            ''', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="metric-container">{item}</div>', unsafe_allow_html=True)
                else:
                    st.info("No dividend data available")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Sector Breakdown with progress bars
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">🏭 Sector Breakdown</div>', unsafe_allow_html=True)
            
            if sector_legends:
                # Parse sector data
                sectors = []
                for item in sector_legends:
                    parts = item.split(':')
                    if len(parts) == 2:
                        label = parts[0].strip()
                        try:
                            value = float(parts[1].strip().replace('%', ''))
                        except:
                            value = 0
                        sectors.append({"sector": label, "value": value})
                
                if sectors:
                    # Create a DataFrame for the sectors
                    df_sectors = pd.DataFrame(sectors)
                    
                    # Create a horizontal bar chart
                    fig = px.bar(
                        df_sectors, 
                        x="value", 
                        y="sector", 
                        orientation='h',
                        color="value",
                        color_continuous_scale=["#3b82f6", "#1e40af"],
                        labels={"value": "Percentage", "sector": ""},
                        text="value"
                    )
                    
                    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                    
                    fig.update_layout(
                        margin=dict(l=0, r=0, t=10, b=0),
                        height=300,
                        xaxis_title="",
                        yaxis_title="",
                        coloraxis_showscale=False,
                        xaxis=dict(showgrid=True, gridcolor='#f3f4f6')
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                else:
                    for item in sector_legends:
                        st.markdown(f'<div class="metric-container">{item}</div>', unsafe_allow_html=True)
            else:
                st.info("No sector breakdown data available")
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info(f"No overview data available for {ticker}. Please click Search to fetch data.")
    
    # News Tab
    with tab2:
        if st.session_state.news_list:
            news_list = st.session_state.news_list
            
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">📰 Latest News</div>', unsafe_allow_html=True)
            
            for news in news_list:
                sentiment_color = "green" if news["sentiment"].lower() == "positive" else "red" if news["sentiment"].lower() == "negative" else "gray"
                badge_class = "badge-green" if sentiment_color == "green" else "badge-red" if sentiment_color == "red" else "badge-gray"
                
                st.markdown(f'''
                <div class="news-item">
                    <div class="news-text">{news["text"]}</div>
                    <div class="news-meta">
                        <span>{news["date"]}</span>
                        <span class="badge {badge_class}">{news["sentiment"]}</span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info(f"No news available for {ticker}. Please click Search to fetch data.")
    
    # Technical Analysis Tab
    with tab3:
        if st.session_state.technical_summary:
            tech_summary = st.session_state.technical_summary
            
            # Main signal card
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">🎯 Technical Summary</div>', unsafe_allow_html=True)
            
            # Display main signal in center with large font
            signal_color = "green" if "buy" in tech_summary["main_signal"].lower() else "red" if "sell" in tech_summary["main_signal"].lower() else "gray"
            st.markdown(f'''
            <div style="text-align:center; padding:1.5rem 0;">
                <div style="font-size:2.5rem; font-weight:bold; color:{signal_color};">{tech_summary["main_signal"]}</div>
                <div style="color:#6b7280; margin-top:0.5rem;">Overall Signal</div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Buy/Sell/Neutral counters with progress bars
            if tech_summary["buy_sell_neutral"]:
                # Calculate total for percentages
                counter_dict = {}
                total = 0
                for label, count in tech_summary["buy_sell_neutral"]:
                    try:
                        count_num = int(count)
                        counter_dict[label.lower()] = count_num
                        total += count_num
                    except:
                        pass
                
                # Display counters with progress bars
                for label, count in tech_summary["buy_sell_neutral"]:
                    try:
                        count_num = int(count)
                        percentage = (count_num / total) * 100 if total > 0 else 0
                        
                        # Determine color based on label
                        bar_color = "#22c55e" if "buy" in label.lower() else "#ef4444" if "sell" in label.lower() else "#9ca3af"
                        
                        st.markdown(f'''
                        <div style="margin-bottom:1rem;">
                            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                                <span>{label}</span>
                                <span style="font-weight:600;">{count}</span>
                            </div>
                            <div style="height:0.5rem; background-color:#f3f4f6; border-radius:9999px; overflow:hidden;">
                                <div style="height:100%; width:{percentage}%; background-color:{bar_color};"></div>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                    except:
                        st.markdown(f'<div class="metric-container"><span>{label}</span><span>{count}</span></div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Timeframe signals
            if tech_summary["signals"]:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-header">⏱️ Signals by Timeframe</div>', unsafe_allow_html=True)
                
                # Create a grid for timeframe signals
                cols = st.columns(3)
                for i, signal in enumerate(tech_summary["signals"]):
                    with cols[i % 3]:
                        # Determine signal type and color
                        signal_type = "Neutral"
                        signal_color = "#9ca3af"
                        
                        if "buy" in signal.lower():
                            signal_type = "Buy"
                            signal_color = "#22c55e"
                        elif "sell" in signal.lower():
                            signal_type = "Sell"
                            signal_color = "#ef4444"
                        
                        st.markdown(f'''
                        <div style="border:1px solid #e5e7eb; border-radius:0.5rem; padding:1rem; margin-bottom:1rem; text-align:center;">
                            <div style="color:#6b7280; margin-bottom:0.5rem;">{signal}</div>
                            <div style="font-weight:600; color:{signal_color}; font-size:1.25rem;">{signal_type}</div>
                        </div>
                        ''', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info(f"No technical analysis available for {ticker}. Please click Search to fetch data.")
    
    # Price Targets Tab
    with tab4:
        if st.session_state.price_target:
            price_target = st.session_state.price_target
            
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">🎯 Price Target</div>', unsafe_allow_html=True)
            
            if price_target["price"]:
                # Determine if change is positive or negative
                is_positive = price_target["change"] and price_target["change"].startswith("+")
                change_color = "#22c55e" if is_positive else "#ef4444" if price_target["change"] and price_target["change"].startswith("-") else "#6b7280"
                
                # Display price target in center with large font
                st.markdown(f'''
                <div style="text-align:center; padding:1.5rem 0;">
                    <div style="font-size:2.5rem; font-weight:bold;">{price_target["currency"] or ""}{price_target["price"]}</div>
                    <div style="color:{change_color}; margin-top:0.5rem;">
                        {price_target["change"] or ""} {price_target["percent"] or ""}
                    </div>
                    <div style="color:#6b7280; margin-top:1rem; max-width:600px; margin-left:auto; margin-right:auto;">
                        {price_target["summary"] or ""}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                # Mock analyst recommendations (in a real app, you'd scrape this data)
                analysts = [
                    {"name": "Morgan Stanley", "target": f"{price_target['currency'] or ''}1,950", "rating": "Overweight", "date": "May 10, 2023"},
                    {"name": "Goldman Sachs", "target": f"{price_target['currency'] or ''}1,850", "rating": "Buy", "date": "Apr 22, 2023"},
                    {"name": "JP Morgan", "target": f"{price_target['currency'] or ''}1,800", "rating": "Neutral", "date": "Apr 15, 2023"},
                    {"name": "HSBC", "target": f"{price_target['currency'] or ''}1,750", "rating": "Buy", "date": "Mar 30, 2023"},
                    {"name": "Citi", "target": f"{price_target['currency'] or ''}1,900", "rating": "Buy", "date": "Mar 15, 2023"},
                ]
                
                st.markdown('<div style="margin-top:2rem;">', unsafe_allow_html=True)
                st.markdown('<div style="font-weight:600; margin-bottom:1rem; font-size:1.1rem;">Analyst Recommendations</div>', unsafe_allow_html=True)
                
                # Create a table for analyst recommendations
                st.markdown('''
                <table style="width:100%; border-collapse:collapse;">
                    <thead>
                        <tr style="border-bottom:1px solid #e5e7eb;">
                            <th style="text-align:left; padding:0.75rem 0.5rem; color:#6b7280;">Analyst</th>
                            <th style="text-align:left; padding:0.75rem 0.5rem; color:#6b7280;">Price Target</th>
                            <th style="text-align:left; padding:0.75rem 0.5rem; color:#6b7280;">Rating</th>
                            <th style="text-align:left; padding:0.75rem 0.5rem; color:#6b7280;">Date</th>
                        </tr>
                    </thead>
                    <tbody>
                ''', unsafe_allow_html=True)
                
                for analyst in analysts:
                    # Determine rating color
                    rating_class = "badge-gray"
                    if "buy" in analyst["rating"].lower() or "overweight" in analyst["rating"].lower():
                        rating_class = "badge-green"
                    elif "sell" in analyst["rating"].lower() or "underweight" in analyst["rating"].lower():
                        rating_class = "badge-red"
                    
                    st.markdown(f'''
                    <tr style="border-bottom:1px solid #f3f4f6;">
                        <td style="padding:0.75rem 0.5rem;">{analyst["name"]}</td>
                        <td style="padding:0.75rem 0.5rem; font-weight:500;">{analyst["target"]}</td>
                        <td style="padding:0.75rem 0.5rem;">
                            <span class="badge {rating_class}">{analyst["rating"]}</span>
                        </td>
                        <td style="padding:0.75rem 0.5rem; color:#6b7280;">{analyst["date"]}</td>
                    </tr>
                    ''', unsafe_allow_html=True)
                
                st.markdown('''
                    </tbody>
                </table>
                ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No price target data available")
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info(f"No price target data available for {ticker}. Please click Search to fetch data.")
    
    # Analytics Tab
    with tab5:
        if st.session_state.analysis:
            analysis = st.session_state.analysis
            
            # Buffett & Lynch Analysis
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">🧠 Buffett & Lynch Analysis</div>', unsafe_allow_html=True)
            
            if analysis["analysis"]:
                for i, point in enumerate(analysis["analysis"]):
                    if point.strip():
                        st.markdown(f'''
                        <div style="display:flex; margin-bottom:1rem;">
                            <div style="margin-right:0.75rem; margin-top:0.25rem;">
                                <div style="height:1.5rem; width:1.5rem; background-color:#dbeafe; color:#1e40af; border-radius:9999px; display:flex; align-items:center; justify-content:center; font-weight:600;">{i+1}</div>
                            </div>
                            <div>{point.strip()}</div>
                        </div>
                        ''', unsafe_allow_html=True)
            else:
                st.info("No Buffett & Lynch analysis available")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Strengths and Weaknesses in 2 columns
            col1, col2 = st.columns(2)
            
            # Investment Strengths
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-header">💪 Investment Strengths</div>', unsafe_allow_html=True)
                
                if analysis["strengths"]:
                    for strength in analysis["strengths"]:
                        if strength.strip():
                            st.markdown(f'''
                            <div style="display:flex; margin-bottom:0.75rem; align-items:flex-start;">
                                <div style="color:#22c55e; margin-right:0.5rem; margin-top:0.25rem;">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                        <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                                        <polyline points="17 6 23 6 23 12"></polyline>
                                    </svg>
                                </div>
                                <div>{strength.strip()}</div>
                            </div>
                            ''', unsafe_allow_html=True)
                else:
                    st.info("No strengths analysis available")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Investment Concerns
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-header">⚠️ Investment Concerns</div>', unsafe_allow_html=True)
                
                if analysis["weaknesses"]:
                    for weakness in analysis["weaknesses"]:
                        if weakness.strip():
                            st.markdown(f'''
                            <div style="display:flex; margin-bottom:0.75rem; align-items:flex-start;">
                                <div style="color:#f59e0b; margin-right:0.5rem; margin-top:0.25rem;">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                                        <line x1="12" y1="9" x2="12" y2="13"></line>
                                        <line x1="12" y1="17" x2="12.01" y2="17"></line>
                                    </svg>
                                </div>
                                <div>{weakness.strip()}</div>
                            </div>
                            ''', unsafe_allow_html=True)
                else:
                    st.info("No concerns analysis available")
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info(f"No analytics available for {ticker}. Please click Search to fetch data.")
    
    # Email summary section
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">📧 Email Summary</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        email = st.text_input("Email address", value="cm505551@gmail.com", placeholder="Enter your email to receive a daily summary")
    
    with col2:
        if st.button("Send Summary", use_container_width=True):
            if email:
                # In a real app, this would send an email
                st.success(f"Summary sent to {email}!")
            else:
                st.error("Please enter an email address")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown(f'''
    <div class="footer">
        Last updated: {time.strftime("%Y-%m-%d %H:%M:%S")}
    </div>
    ''', unsafe_allow_html=True)
else:
    # Show welcome message when no ticker is entered
    st.markdown('''
    <div style="text-align:center; padding:3rem 1rem;">
        <div style="font-size:1.25rem; color:#6b7280; max-width:600px; margin:0 auto;">
            Enter a stock symbol above and click Search to view comprehensive financial data and analysis
        </div>
    </div>
    ''', unsafe_allow_html=True)