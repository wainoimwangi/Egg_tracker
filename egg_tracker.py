# egg_tracker.py
import streamlit as st
import pandas as pd
from datetime import date
from sqlalchemy import text, create_engine
import os

# Constants
MIN_EGGS = 0
MAX_EGGS = 1  # Assuming chickens lay 0 or 1 egg per day

def get_engine():
    try:
        # Try Streamlit secrets first
        secrets = st.secrets["postgres"]
        conn_string = (
            f"postgresql://{secrets['username']}:{secrets['password']}@"
            f"{secrets['host']}:{secrets['port']}/{secrets['database']}"
        )
    except:
        # Fallback to environment variables
        conn_string = os.getenv("DATABASE_URL", 
            "postgresql://postgres:Khanselm%4023@localhost:5432/egg_tracker")
    
    return create_engine(conn_string)

def apply_custom_styles():
    """Load and apply custom CSS styles"""
    try:
        with open("styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Custom stylesheet not found. Using default styles.")

def record_eggs_form(engine):
    """Form for recording daily egg counts"""
    with st.form("🐔 Record Eggs Laid", clear_on_submit=True):
        
        record_date = st.date_input("Date", date.today())
        imani_eggs = st.number_input("Imani's Eggs", MIN_EGGS, MAX_EGGS, step=1)
        hansel_eggs = st.number_input("Hansel's Eggs", MIN_EGGS, MAX_EGGS, step=1)

        if st.form_submit_button("Save Entry"):
            try:
                with engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO eggs (record_date, imani, hansel)
                        VALUES (:record_date, :imani, :hansel)
                        ON CONFLICT(record_date) DO UPDATE SET
                            imani = EXCLUDED.imani, 
                            hansel = EXCLUDED.hansel
                    """), {
                        'record_date': record_date, 
                        'imani': imani_eggs, 
                        'hansel': hansel_eggs
                    })
                    conn.commit()
                    st.success("🥚 Eggs recorded successfully!")
            except Exception as e:
                st.error(f"Database error: {str(e)}")

def display_egg_metrics(df):
    """Display egg statistics metrics"""
    total_eggs = df[['imani', 'hansel']].sum().sum()
    imani_total = df['imani'].sum()
    hansel_total = df['hansel'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Eggs Recorded", total_eggs)
    col2.metric("Imani's Total Eggs", imani_total)
    col3.metric("Hansel's Total Eggs", hansel_total)
    
    # Add any additional metrics you want here
    avg_eggs = round(total_eggs / len(df), 2) if len(df) > 0 else 0
    col4.metric("Daily Average", avg_eggs)

def display_egg_data(engine):
    """Display and filter egg data with visualizations"""
    try:
        df = pd.read_sql("SELECT * FROM eggs ORDER BY record_date DESC", engine)
        
        if not df.empty:
            # Convert record_date to datetime.date if it's not already
            if pd.api.types.is_datetime64_any_dtype(df['record_date']):
                df['record_date'] = df['record_date'].dt.date
            display_egg_metrics(df)
            # Create two columns
            col1, col2 = st.columns(2)
            
            with col1:
                # Display metrics
                
                
                # Record eggs form
                st.markdown("---")
                record_eggs_form(engine)
            
            with col2:
                # Date range filter
                st.subheader("📆 View Egg Logs by Date")
                min_date = df['record_date'].min()
                max_date = df['record_date'].max()
                
                start_date, end_date = st.date_input(
                    "Select date range",
                    [min_date, max_date],
                    min_value=min_date,
                    max_value=max_date
                )
                
                # Filter data
                filtered_df = df[
                    (df['record_date'] >= start_date) & 
                    (df['record_date'] <= end_date)
                ]
                
                # Expandable table view
                with st.expander("📋 View Detailed Egg Log", expanded=True):
                    st.dataframe(
                        filtered_df,
                        hide_index=True,
                        use_container_width=True,
                        column_config={
                            "record_date": "Date",
                            "imani": "Imani's Eggs",
                            "hansel": "Hansel's Eggs"
                        }
                    )
                

            # st.subheader("📊 Egg Trends")
            # chart_data = filtered_df.copy()
            # chart_data['record_date'] = pd.to_datetime(chart_data['record_date'])
            # chart_data = chart_data.set_index('record_date')[['imani', 'hansel']]
            # st.bar_chart(chart_data)
                
        else:
            # Single column layout when no data exists
            record_eggs_form(engine)
            st.info("No data available yet. Start by recording some entries!")
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

def main():
    """Main application function"""
    st.set_page_config(page_title="Egg Tracker",
                        page_icon='🥚',
                        layout='wide',
                        initial_sidebar_state='collapsed')
    
    apply_custom_styles()
    st.title("🥚 Egg Tracker")
    
    try:
        engine = get_engine()
        display_egg_data(engine)
    except Exception as e:
        st.error(f"Application error: {str(e)}")

if __name__ == "__main__":
    main()