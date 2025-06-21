# Enhanced AI Portfolio Tracker with Netflix-style UI
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import time
import logging
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Enhanced Page Config ---
st.set_page_config(
    page_title="AI Portfolio Tracker", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📈"
)

# --- Enhanced Netflix-style CSS ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Netflix+Sans:wght@300;400;500;700&display=swap');
        
        .main { background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%); }
        .stApp { background: #141414; color: white; font-family: 'Netflix Sans', 'Helvetica Neue', sans-serif; }
        
        /* Header Styles */
        .netflix-header {
            background: linear-gradient(90deg, #E50914 0%, #B20710 100%);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(229, 9, 20, 0.3);
        }
        
        .netflix-logo {
            font-size: 32px;
            font-weight: 700;
            color: white;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        /* Enhanced Tile Styles */
        .movie-tile {
            background: linear-gradient(145deg, #1c1c1c 0%, #2a2a2a 100%);
            padding: 20px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            position: relative;
            overflow: hidden;
            cursor: pointer;
            border: 2px solid transparent;
        }
        
        .movie-tile:hover {
            transform: scale(1.05) translateY(-10px);
            box-shadow: 0 20px 40px rgba(229, 9, 20, 0.4);
            border-color: #E50914;
        }
        
        .movie-tile::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            transition: left 0.5s;
        }
        
        .movie-tile:hover::before {
            left: 100%;
        }
        
        /* Loading Animation */
        .loading-spinner {
            border: 4px solid #333;
            border-top: 4px solid #E50914;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Error Message Styles */
        .error-card {
            background: linear-gradient(135deg, #722F37 0%, #5D1F1F 100%);
            border: 1px solid #E50914;
            border-radius: 12px;
            padding: 15px;
            margin: 10px 0;
            animation: fadeIn 0.3s ease-in;
        }
        
        .success-card {
            background: linear-gradient(135deg, #2D5016 0%, #1F3A0F 100%);
            border: 1px solid #46D369;
            border-radius: 12px;
            padding: 15px;
            margin: 10px 0;
            animation: fadeIn 0.3s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* News Card Styles */
        .news-carousel {
            display: flex;
            overflow-x: auto;
            gap: 20px;
            padding: 20px 0;
            scrollbar-width: thin;
            scrollbar-color: #E50914 #333;
        }
        
        .news-item {
            min-width: 300px;
            background: linear-gradient(145deg, #1c1c1c 0%, #2a2a2a 100%);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            transition: transform 0.3s ease;
        }
        
        .news-item:hover {
            transform: translateY(-5px);
        }
        
        /* Button Styles */
        .stButton>button {
            background: linear-gradient(135deg, #E50914 0%, #B20710 100%);
            color: white;
            border: none;
            font-weight: 600;
            border-radius: 25px;
            padding: 12px 24px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(229, 9, 20, 0.3);
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(229, 9, 20, 0.5);
        }
        
        /* Enhanced Input Styles */
        .stTextInput>div>input, .stNumberInput>div>input {
            background: rgba(255,255,255,0.1);
            border: 2px solid #333;
            border-radius: 12px;
            color: white;
            padding: 16px 20px;
            font-size: 18px;
            min-height: 50px;
            transition: all 0.3s ease;
        }
        
        .stTextInput>div>input:focus, .stNumberInput>div>input:focus {
            border-color: #E50914;
            box-shadow: 0 0 15px rgba(229, 9, 20, 0.4);
            transform: scale(1.02);
        }
        
        /* Input Labels */
        .stTextInput>label, .stNumberInput>label {
            font-size: 16px;
            font-weight: 600;
            color: #E50914;
            margin-bottom: 8px;
        }
        
        /* Add Stock Section */
        .add-stock-container {
            background: linear-gradient(135deg, #2a2a2a 0%, #1c1c1c 100%);
            padding: 30px;
            border-radius: 20px;
            margin: 30px 0;
            border: 2px solid #333;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .add-stock-container:hover {
            border-color: #E50914;
            box-shadow: 0 15px 40px rgba(229, 9, 20, 0.2);
        }
        
        /* Sidebar Styles */
        .css-1d391kg {
            background: linear-gradient(180deg, #1a1a1a 0%, #0f0f0f 100%);
        }
        
        /* Metrics Cards */
        .metric-card {
            background: linear-gradient(135deg, #2a2a2a 0%, #1c1c1c 100%);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            border: 1px solid #333;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            border-color: #E50914;
            transform: translateY(-3px);
        }
    </style>
""", unsafe_allow_html=True)

# --- Error Handling Classes ---
class PortfolioError(Exception):
    """Base exception for portfolio operations"""
    pass

class StockNotFoundError(PortfolioError):
    """Raised when stock ticker is not found"""
    pass

class DataFetchError(PortfolioError):
    """Raised when data fetching fails"""
    pass

class ValidationError(PortfolioError):
    """Raised when input validation fails"""
    pass

# --- Enhanced Session State ---
def initialize_session_state():
    """Initialize session state with default values"""
    defaults = {
        "portfolio": {},  # Format: {ticker: {"quantity": int, "purchase_price": float, "purchase_date": str}}
        "selected_stock": None,
        "loading": False,
        "error_messages": [],
        "success_messages": [],
        "last_update": None,
        "watchlist": [],
        "total_portfolio_value": 0.0,
        "daily_change": 0.0,
        "user_preferences": {
            "currency": "₹",
            "theme": "dark",
            "notifications": True
        }
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# --- Enhanced Helper Functions with Error Handling ---
def safe_request(url: str, headers: dict = None, timeout: int = 10) -> Optional[requests.Response]:
    """Make a safe HTTP request with error handling"""
    try:
        headers = headers or {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logger.error(f"Request failed for {url}: {str(e)}")
        return None

def search_ticker(company_name: str) -> Optional[str]:
    """Search for ticker symbol with enhanced error handling"""
    if not company_name or len(company_name.strip()) < 2:
        raise ValidationError("Company name must be at least 2 characters long")
    
    try:
        # Try multiple search methods
        search_methods = [
            f"https://query2.finance.yahoo.com/v1/finance/search?q={company_name}",
            f"https://query1.finance.yahoo.com/v7/finance/search?q={company_name}"
        ]
        
        for url in search_methods:
            response = safe_request(url)
            if response:
                result = response.json()
                quotes = result.get("quotes", [])
                
                for quote in quotes:
                    if quote.get("quoteType") == "EQUITY" and quote.get("symbol"):
                        return quote.get("symbol")
        
        raise StockNotFoundError(f"No ticker found for '{company_name}'")
        
    except Exception as e:
        logger.error(f"Ticker search failed: {str(e)}")
        raise DataFetchError(f"Failed to search for ticker: {str(e)}")

def get_stock_data(ticker: str) -> Dict:
    """Fetch stock data with comprehensive error handling"""
    try:
        stock = yf.Ticker(ticker)
        
        # Get basic info
        info = stock.info
        if not info:
            raise DataFetchError(f"No data available for {ticker}")
        
        # Get recent price data
        hist = stock.history(period="5d")
        if hist.empty:
            raise DataFetchError(f"No price history available for {ticker}")
        
        current_price = hist["Close"].iloc[-1]
        prev_price = hist["Close"].iloc[-2] if len(hist) > 1 else current_price
        change = current_price - prev_price
        change_pct = (change / prev_price) * 100 if prev_price != 0 else 0
        
        return {
            "name": info.get("shortName", ticker),
            "price": current_price,
            "change": change,
            "change_pct": change_pct,
            "volume": info.get("volume", 0),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE", "N/A"),
            "dividend_yield": info.get("dividendYield", 0),
            "52_week_high": info.get("fiftyTwoWeekHigh", 0),
            "52_week_low": info.get("fiftyTwoWeekLow", 0),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown")
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch data for {ticker}: {str(e)}")
        raise DataFetchError(f"Unable to fetch data for {ticker}: {str(e)}")

def get_enhanced_logo_url(company_name: str) -> str:
    """Get company logo with fallback options"""
    fallback_urls = [
        f"https://logo.clearbit.com/{company_name.lower().replace(' ', '')}.com",
        f"https://img.logo.dev/{company_name.lower().replace(' ', '')}.com?token=pk_X-1ZO13GSgeOeUrIuSKdKQ",
        "https://via.placeholder.com/100x100/E50914/FFFFFF?text=📈"
    ]
    
    for url in fallback_urls:
        try:
            response = safe_request(url)
            if response and response.status_code == 200:
                return url
        except:
            continue
    
    return fallback_urls[-1]  # Return placeholder

def fetch_enhanced_news(company_name: str) -> List[Dict]:
    """Fetch news with multiple sources and error handling"""
    news_sources = [
        f"https://newsapi.org/v2/everything?q={company_name}+stock&sortBy=publishedAt&apiKey=YOUR_API_KEY",
        f"https://news.google.com/rss/search?q={company_name}+stock&hl=en-US&gl=US&ceid=US:en"
    ]
    
    all_news = []
    
    for source in news_sources:
        try:
            if "newsapi.org" in source:
                # Skip NewsAPI for now (requires API key)
                continue
                
            response = safe_request(source)
            if response:
                # Parse RSS feed
                from xml.etree import ElementTree as ET
                root = ET.fromstring(response.content)
                items = root.findall(".//item")[:10]
                
                for item in items:
                    title_elem = item.find("title")
                    link_elem = item.find("link")
                    desc_elem = item.find("description")
                    date_elem = item.find("pubDate")
                    
                    if title_elem is not None and link_elem is not None:
                        title = title_elem.text
                        link = link_elem.text
                        desc = desc_elem.text if desc_elem is not None else ""
                        date = date_elem.text if date_elem is not None else ""
                        
                        # Clean description
                        summary = desc.split("<")[0][:200] + "..." if desc else "No summary available."
                        
                        all_news.append({
                            "title": title,
                            "link": link,
                            "summary": summary,
                            "date": date,
                            "source": "Google News"
                        })
                        
        except Exception as e:
            logger.error(f"Failed to fetch news from {source}: {str(e)}")
            continue
    
    return all_news[:6]  # Return top 6 articles

def show_error_message(message: str, error_type: str = "error"):
    """Display enhanced error messages"""
    if error_type == "error":
        st.markdown(f"""
        <div class="error-card">
            <strong>❌ Error:</strong> {message}
        </div>
        """, unsafe_allow_html=True)
    elif error_type == "warning":
        st.markdown(f"""
        <div class="error-card" style="background: linear-gradient(135deg, #8B4513 0%, #654321 100%); border-color: #FFA500;">
            <strong>⚠️ Warning:</strong> {message}
        </div>
        """, unsafe_allow_html=True)

def show_success_message(message: str):
    """Display enhanced success messages"""
    st.markdown(f"""
    <div class="success-card">
        <strong>✅ Success:</strong> {message}
    </div>
    """, unsafe_allow_html=True)

def show_loading_spinner():
    """Display loading animation"""
    st.markdown('<div class="loading-spinner"></div>', unsafe_allow_html=True)

# --- Initialize Session State ---
initialize_session_state()

# --- Netflix-style Header ---
st.markdown("""
<div class="netflix-header">
    <div class="netflix-logo">🎬 PORTFOLIO TRACKER</div>
    <p style="margin-top: 10px; font-size: 16px; opacity: 0.9;">Your investments, Netflix-style experience</p>
</div>
""", unsafe_allow_html=True)

# --- Enhanced Sidebar ---
with st.sidebar:
    st.markdown("### 👤 Investor Profile")
    
    # Profile Section
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("🎭", unsafe_allow_html=True)
    with col2:
        investor_name = st.text_input("Name", value="Investor", label_visibility="collapsed")
    
    bio = st.text_area("About you", value="Passionate investor building a better future.", height=100)
    
    st.markdown("---")
    
    # Preferences
    st.markdown("### ⚙️ Preferences")
    currency = st.selectbox("Currency", ["₹", "$", "€", "£"], index=0)
    st.session_state.user_preferences["currency"] = currency
    
    notifications = st.checkbox("Enable Notifications", value=True)
    st.session_state.user_preferences["notifications"] = notifications
    
    st.markdown("---")
    
    # Portfolio Summary
    if st.session_state.portfolio:
        st.markdown("### 📊 Portfolio Summary")
        total_value = sum([
            holding["total_cost"] if isinstance(holding, dict) else holding * 100 
            for holding in st.session_state.portfolio.values()
        ])
        
        st.metric("Total Value", f"{currency}{total_value:,.2f}")
        st.metric("Holdings", f"{len(st.session_state.portfolio)} stocks")

# --- Main Content ---
st.markdown(f"## 👋 Welcome back, **{investor_name}**")
st.caption(f"🎯 {bio}")

# --- Enhanced Portfolio Management ---
st.markdown("""
<div class="add-stock-container">
    <h3 style="color: #E50914; text-align: center; margin-bottom: 25px; font-size: 24px;">
        ➕ Add New Stock to Your Portfolio
    </h3>
</div>
""", unsafe_allow_html=True)

# Create larger input section
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("### 🔍 Stock Details")
    
    # Larger input fields
    company_input = st.text_input(
        "🏢 Company Name or Ticker", 
        placeholder="e.g., Apple, AAPL, Tesla, TSLA, Infosys, INFY",
        help="Enter company name (Apple) or ticker symbol (AAPL)",
        key="company_search"
    )
    
    # Three columns for stock details
    input_col1, input_col2, input_col3 = st.columns(3)
    
    with input_col1:
        shares_input = st.number_input(
            "📊 Number of Shares", 
            min_value=1, 
            step=1, 
            value=1,
            help="How many shares did you buy?"
        )
    
    with input_col2:
        purchase_price = st.number_input(
            "💰 Purchase Price per Share", 
            min_value=0.01,
            step=0.01,
            value=100.00,
            help="What price did you pay per share?",
            format="%.2f"
        )
    
    with input_col3:
        purchase_date = st.date_input(
            "📅 Purchase Date",
            value=datetime.now().date(),
            help="When did you buy this stock?"
        )

with col2:
    st.markdown("### 🎬")
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Large add button
    add_button = st.button(
        "🎬 ADD TO PORTFOLIO", 
        use_container_width=True,
        help="Click to add this stock to your portfolio"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick add preset buttons
    st.markdown("**Quick Add Popular Stocks:**")
    if st.button("🍎 Apple", use_container_width=True, key="quick_aapl"):
        st.session_state.company_search = "AAPL"
        st.rerun()
    
    if st.button("⚡ Tesla", use_container_width=True, key="quick_tsla"):
        st.session_state.company_search = "TSLA"
        st.rerun()
    
    if st.button("💻 Microsoft", use_container_width=True, key="quick_msft"):
        st.session_state.company_search = "MSFT"
        st.rerun()

if add_button and company_input:
    try:
        with st.spinner("🔍 Searching for stock..."):
            ticker = search_ticker(company_input)
            
        with st.spinner("📈 Fetching stock data..."):
            stock_data = get_stock_data(ticker)
            
        # Add to portfolio with purchase details
        if ticker not in st.session_state.portfolio:
            st.session_state.portfolio[ticker] = {
                "quantity": 0,
                "total_cost": 0.0,
                "purchases": []
            }
        
        # Add new purchase
        st.session_state.portfolio[ticker]["quantity"] += shares_input
        st.session_state.portfolio[ticker]["total_cost"] += (shares_input * purchase_price)
        st.session_state.portfolio[ticker]["purchases"].append({
            "quantity": shares_input,
            "price": purchase_price,
            "date": purchase_date.strftime("%Y-%m-%d"),
            "total": shares_input * purchase_price
        })
        
        total_invested = shares_input * purchase_price
        current_value = shares_input * stock_data["price"]
        profit_loss = current_value - total_invested
        profit_loss_pct = (profit_loss / total_invested) * 100 if total_invested > 0 else 0
        
        show_success_message(
            f"Added {shares_input} shares of {stock_data['name']} ({ticker}) at {currency}{purchase_price:.2f} per share. "
            f"Investment: {currency}{total_invested:.2f}, Current Value: {currency}{current_value:.2f}, "
            f"P&L: {currency}{profit_loss:+.2f} ({profit_loss_pct:+.2f}%)"
        )
        
        # Clear inputs and refresh
        time.sleep(2)
        st.rerun()
        
    except ValidationError as e:
        show_error_message(str(e))
    except StockNotFoundError as e:
        show_error_message(f"Stock not found: {str(e)}")
    except DataFetchError as e:
        show_error_message(f"Data fetch failed: {str(e)}")
    except Exception as e:
        show_error_message(f"Unexpected error: {str(e)}")

# --- Portfolio Management ---
if st.session_state.portfolio:
    with st.expander("🗑️ Manage Holdings", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            to_remove = st.selectbox("Select stock to remove", list(st.session_state.portfolio.keys()))
            
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Remove Stock", type="secondary"):
                removed_stock = st.session_state.portfolio.pop(to_remove, None)
                if removed_stock:
                    show_success_message(f"Removed {to_remove} from portfolio")
                    st.rerun()

# --- Enhanced Portfolio Display ---
if st.session_state.portfolio:
    st.markdown("## 🎞️ Your Portfolio Collection")
    
    # Portfolio metrics
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        portfolio_data = {}
        total_value = 0
        total_invested = 0
        total_change = 0
        
        for ticker, holding in st.session_state.portfolio.items():
            try:
                data = get_stock_data(ticker)
                quantity = holding["quantity"]
                avg_purchase_price = holding["total_cost"] / quantity if quantity > 0 else 0
                current_value = data["price"] * quantity
                invested_amount = holding["total_cost"]
                
                portfolio_data[ticker] = {
                    **data, 
                    "quantity": quantity,
                    "avg_purchase_price": avg_purchase_price,
                    "invested_amount": invested_amount,
                    "current_value": current_value,
                    "profit_loss": current_value - invested_amount,
                    "profit_loss_pct": ((current_value - invested_amount) / invested_amount) * 100 if invested_amount > 0 else 0,
                    "purchases": holding["purchases"]
                }
                
                total_value += current_value
                total_invested += invested_amount
                total_change += current_value - invested_amount
            except Exception as e:
                logger.error(f"Error fetching data for {ticker}: {e}")
                continue
        
        total_change_pct = (total_change / total_invested) * 100 if total_invested > 0 else 0
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>💰 Total Value</h3>
                <h2>{}{:,.2f}</h2>
            </div>
            """.format(currency, total_value), unsafe_allow_html=True)
        
        with col2:
            change_color = "#46D369" if total_change >= 0 else "#E50914"
            st.markdown(f"""
            <div class="metric-card">
                <h3>📈 Total P&L</h3>
                <h2 style="color: {change_color};">{currency}{total_change:+.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>💰 Invested</h3>
                <h2>{currency}{total_invested:,.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            change_color = "#46D369" if total_change_pct >= 0 else "#E50914"
            st.markdown(f"""
            <div class="metric-card">
                <h3>📋 Return %</h3>
                <h2 style="color: {change_color};">{total_change_pct:+.2f}%</h2>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Portfolio tiles
        cols = st.columns(3)
        for i, (ticker, data) in enumerate(portfolio_data.items()):
            with cols[i % 3]:
                try:
                    logo_url = get_enhanced_logo_url(data["name"])
                    current_value = data["current_value"]
                    invested_amount = data["invested_amount"]
                    profit_loss = data["profit_loss"]
                    profit_loss_pct = data["profit_loss_pct"]
                    change_color = "#46D369" if profit_loss >= 0 else "#E50914"
                    
                    if st.button(f"📺 {data['name']}", key=f"select_{ticker}", use_container_width=True):
                        st.session_state.selected_stock = (data["name"], ticker)
                        st.rerun()
                    
                    st.markdown(f"""
                    <div class="movie-tile">
                        <img src="{logo_url}" width="60" style="border-radius: 15px; margin-bottom: 15px;" onerror="this.src='https://via.placeholder.com/60x60/E50914/FFFFFF?text=📈'"/>
                        <h4 style="margin: 10px 0;">{data['name']}</h4>
                        <p><strong>Current Price:</strong> {currency}{data['price']:.2f}</p>
                        <p><strong>Avg. Buy Price:</strong> {currency}{data['avg_purchase_price']:.2f}</p>
                        <p><strong>Shares:</strong> {data['quantity']}</p>
                        <p><strong>Invested:</strong> {currency}{invested_amount:,.2f}</p>
                        <p><strong>Current Value:</strong> {currency}{current_value:,.2f}</p>
                        <p style="color: {change_color};"><strong>P&L:</strong> {currency}{profit_loss:+.2f} ({profit_loss_pct:+.2f}%)</p>
                        <p><strong>Sector:</strong> {data['sector']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    show_error_message(f"Error displaying {ticker}: {str(e)}", "warning")
                    
    except Exception as e:
        show_error_message(f"Error calculating portfolio metrics: {str(e)}")

else:
    # Empty state
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px; background: linear-gradient(135deg, #1c1c1c 0%, #2a2a2a 100%); border-radius: 20px; margin: 40px 0;">
        <h2 style="color: #E50914; margin-bottom: 20px;">🎬 Your Portfolio Awaits</h2>
        <p style="font-size: 18px; color: #ccc; margin-bottom: 30px;">Start building your investment portfolio by adding your first stock above.</p>
        <p style="font-size: 16px; color: #999;">🎯 Search for companies like Apple, Tesla, or Infosys to get started!</p>
    </div>
    """, unsafe_allow_html=True)

# --- Enhanced News Section ---
if st.session_state.get("selected_stock"):
    name, ticker = st.session_state.selected_stock
    st.markdown(f"## 📺 {name} - Latest Updates")
    
    try:
        with st.spinner("📰 Loading latest news..."):
            news_list = fetch_enhanced_news(name)
        
        if news_list:
            st.markdown('<div class="news-carousel">', unsafe_allow_html=True)
            
            cols = st.columns(min(len(news_list), 3))
            for i, article in enumerate(news_list[:3]):
                with cols[i]:
                    st.markdown(f"""
                    <div class="news-item">
                        <h4 style="color: #E50914; margin-bottom: 10px;">{article['title'][:80]}...</h4>
                        <p style="color: #ccc; font-size: 14px; margin-bottom: 15px;">{article['summary']}</p>
                        <small style="color: #999;">{article.get('date', 'Recent')}</small><br>
                        <a href="{article['link']}" target="_blank" style="color: #E50914; text-decoration: none; font-weight: 500;">
                            🔗 Read Full Article
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Show more news in expandable section
            if len(news_list) > 3:
                with st.expander(f"📰 More News ({len(news_list) - 3} articles)"):
                    for article in news_list[3:]:
                        st.markdown(f"""
                        <div style="padding: 15px; border-bottom: 1px solid #333;">
                            <h5 style="color: #E50914;">{article['title']}</h5>
                            <p style="color: #ccc; font-size: 14px;">{article['summary']}</p>
                            <a href="{article['link']}" target="_blank" style="color: #E50914;">Read more →</a>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("📰 No recent news found for this stock.")
            
    except Exception as e:
        show_error_message(f"Failed to load news: {str(e)}", "warning")

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: #666;">
    <p>🎬 AI Portfolio Tracker | Built with ❤️ using Streamlit</p>
    <p style="font-size: 12px;">⚠️ This is for educational purposes only. Not financial advice.</p>
</div>
""", unsafe_allow_html=True)