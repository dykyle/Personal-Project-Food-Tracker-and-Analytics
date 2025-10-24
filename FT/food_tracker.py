import streamlit as st
import datetime
import pandas as pd
import io
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Page configuration
st.set_page_config(
    page_title="Food Tracker",
    page_icon="🍕",
    layout="wide"
)

# Database setup
def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('food_tracker.db', check_same_thread=False)
    c = conn.cursor()
    
    # Create table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS food_entries
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         date TEXT NOT NULL,
         category TEXT NOT NULL,
         food TEXT NOT NULL,
         beverage TEXT NOT NULL,
         protein INTEGER DEFAULT 0,
         notes TEXT,
         created_at TEXT)
    ''')
    
    conn.commit()
    return conn

# Initialize database
conn = init_db()

# Database functions
def get_all_entries():
    """Get all food entries from database"""
    c = conn.cursor()
    c.execute('SELECT * FROM food_entries ORDER BY date DESC, created_at DESC')
    entries = c.fetchall()
    
    # Convert to list of dictionaries
    result = []
    for entry in entries:
        result.append({
            'id': entry[0],
            'date': entry[1],
            'category': entry[2],
            'food': entry[3],
            'beverage': entry[4],
            'protein': entry[5],
            'notes': entry[6],
            'created_at': entry[7]
        })
    return result

def add_entry(entry):
    """Add a new entry to database"""
    c = conn.cursor()
    c.execute('''
        INSERT INTO food_entries (date, category, food, beverage, protein, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (entry['date'], entry['category'], entry['food'], entry['beverage'], 
          entry['protein'], entry.get('notes', ''), entry['created_at']))
    conn.commit()

def update_entry(entry_id, entry):
    """Update an existing entry"""
    c = conn.cursor()
    c.execute('''
        UPDATE food_entries 
        SET date=?, category=?, food=?, beverage=?, protein=?, notes=?
        WHERE id=?
    ''', (entry['date'], entry['category'], entry['food'], entry['beverage'],
          entry['protein'], entry.get('notes', ''), entry_id))
    conn.commit()

def delete_entry(entry_id):
    """Delete an entry from database"""
    c = conn.cursor()
    c.execute('DELETE FROM food_entries WHERE id=?', (entry_id,))
    conn.commit()

def clear_all_entries():
    """Clear all entries from database"""
    c = conn.cursor()
    c.execute('DELETE FROM food_entries')
    conn.commit()

# Initialize session state for current page only
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

def create_pdf_report():
    """Create a PDF download of all food entries"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "Food Tracker Report")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 130, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Table headers
    y_position = height - 170
    headers = ["Date", "Category", "Food", "Beverage", "Protein (g)"]
    col_positions = [50, 120, 220, 350, 450]
    
    c.setFont("Helvetica-Bold", 10)
    for i, header in enumerate(headers):
        c.drawString(col_positions[i], y_position, header)
    
    y_position -= 20
    
    # Data rows
    entries = get_all_entries()
    c.setFont("Helvetica", 9)
    for entry in entries:
        if y_position < 100:  # New page if needed
            c.showPage()
            y_position = height - 100
            # Redraw headers on new page
            c.setFont("Helvetica-Bold", 10)
            for i, header in enumerate(headers):
                c.drawString(col_positions[i], y_position, header)
            y_position -= 20
            c.setFont("Helvetica", 9)
        
        c.drawString(col_positions[0], y_position, entry['date'])
        c.drawString(col_positions[1], y_position, entry['category'])
        c.drawString(col_positions[2], y_position, entry['food'][:30])
        c.drawString(col_positions[3], y_position, entry['beverage'][:20])
        c.drawString(col_positions[4], y_position, str(entry.get('protein', 0)))
        y_position -= 15
    
    c.save()
    buffer.seek(0)
    return buffer

def transform_to_daily_table():
    """Transform data into your desired table format"""
    entries = get_all_entries()
    if not entries:
        return pd.DataFrame()
    
    daily_data = []
    dates = sorted(set(entry['date'] for entry in entries), reverse=True)
    
    for date in dates:
        day_entries = [entry for entry in entries if entry['date'] == date]
        
        day_row = {
            'Date': date,
            'Breakfast': '',
            'Lunch': '',
            'Snacks': '',
            'Dinner': '',
            'Beverage': '',
            'Protein Intake': 0
        }
        
        for entry in day_entries:
            category = entry['category']
            if category in ['Breakfast', 'Lunch', 'Snacks', 'Dinner']:
                if day_row[category]:
                    day_row[category] += f", {entry['food']}"
                else:
                    day_row[category] = entry['food']
            
            if entry['beverage']:
                if day_row['Beverage']:
                    day_row['Beverage'] += f", {entry['beverage']}"
                else:
                    day_row['Beverage'] = entry['beverage']
            
            day_row['Protein Intake'] += entry.get('protein', 0)
        
        daily_data.append(day_row)
    
    return pd.DataFrame(daily_data)

def create_protein_charts():
    """Create protein intake visualization"""
    entries = get_all_entries()
    if not entries:
        return None, None, None
    
    df = pd.DataFrame(entries)
    df['date'] = pd.to_datetime(df['date'])
    
    daily_protein = df.groupby('date')['protein'].sum().reset_index()
    weekly_protein = df.groupby(pd.Grouper(key='date', freq='W'))['protein'].sum().reset_index()
    weekly_protein['week'] = weekly_protein['date'].dt.strftime('Week of %b %d')
    category_protein = df.groupby('category')['protein'].sum().reset_index()
    
    return daily_protein, weekly_protein, category_protein

# App title
st.title("🍕 Food Tracker")
st.markdown("Track your daily meals, beverages, and protein intake!")

# Sidebar for navigation
st.sidebar.title("Navigation")

# Define pages
pages = {
    "📊 Dashboard": "Dashboard",
    "➕ Add Entry": "Add Entry", 
    "👀 View & Edit Entries": "View & Edit Entries",
    "📈 Protein Analytics": "Protein Analytics"
}

# Create navigation buttons
for page_name, page_id in pages.items():
    if st.sidebar.button(page_name, use_container_width=True, key=page_id):
        st.session_state.current_page = page_id

# Get current page
current_page = st.session_state.current_page

# Dashboard Page
if current_page == "Dashboard":
    st.header("📊 Dashboard")
    
    entries = get_all_entries()
    if not entries:
        st.info("No entries yet! Add some food entries first.")
    else:
        # Key metrics in beautiful cards
        st.subheader("📈 Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        total_entries = len(entries)
        unique_dates = len(set(entry['date'] for entry in entries))
        total_protein = sum(entry.get('protein', 0) for entry in entries)
        avg_daily_protein = total_protein / unique_dates if unique_dates > 0 else 0
        
        with col1:
            st.markdown(
                f"""
                <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; border-left: 4px solid #ff4b4b;">
                    <h3 style="margin: 0; color: #ff4b4b;">{total_entries}</h3>
                    <p style="margin: 0; color: #666;">Total Entries</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                f"""
                <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; border-left: 4px solid #00d4aa;">
                    <h3 style="margin: 0; color: #00d4aa;">{unique_dates}</h3>
                    <p style="margin: 0; color: #666;">Days Tracked</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown(
                f"""
                <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; border-left: 4px solid #ffa726;">
                    <h3 style="margin: 0; color: #ffa726;">{total_protein:.0f}g</h3>
                    <p style="margin: 0; color: #666;">Total Protein</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col4:
            st.markdown(
                f"""
                <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; border-left: 4px solid #42a5f5;">
                    <h3 style="margin: 0; color: #42a5f5;">{avg_daily_protein:.1f}g</h3>
                    <p style="margin: 0; color: #666;">Avg Daily Protein</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Recent entries in a proper table
        st.subheader("📋 Recent Entries")
        recent_entries = entries[:10]  # First 10 entries (already sorted by date DESC)
        
        # Create a DataFrame for the recent entries table
        recent_df = pd.DataFrame(recent_entries)
        recent_df['date'] = pd.to_datetime(recent_df['date']).dt.date
        
        # Reorder columns and format for better display
        display_df = recent_df[['date', 'category', 'food', 'beverage', 'protein']].copy()
        display_df = display_df.rename(columns={
            'date': 'Date',
            'category': 'Meal',
            'food': 'Food',
            'beverage': 'Beverage', 
            'protein': 'Protein (g)'
        })
        
        # Display the table with better styling
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Date": st.column_config.DateColumn("Date", width="small"),
                "Meal": st.column_config.TextColumn("Meal", width="small"),
                "Food": st.column_config.TextColumn("Food", width="medium"),
                "Beverage": st.column_config.TextColumn("Beverage", width="medium"),
                "Protein (g)": st.column_config.NumberColumn("Protein (g)", width="small")
            }
        )
        
        # Quick insights
        st.subheader("💡 Quick Insights")
        col1, col2 = st.columns(2)
        
        with col1:
            # Most common food category
            if recent_entries:
                categories = [entry['category'] for entry in recent_entries]
                most_common = max(set(categories), key=categories.count)
                st.info(f"**Most logged meal:** {most_common}")
            
            # Highest protein meal
            if recent_entries:
                highest_protein = max(recent_entries, key=lambda x: x.get('protein', 0))
                st.info(f"**Highest protein meal:** {highest_protein['food']} ({highest_protein.get('protein', 0)}g)")
        
        with col2:
            # Recent activity
            today = datetime.date.today()
            today_entries = [entry for entry in entries 
                           if datetime.datetime.strptime(entry['date'], '%Y-%m-%d').date() == today]
            st.info(f"**Today's entries:** {len(today_entries)}")
            
            # Weekly summary
            week_ago = today - datetime.timedelta(days=7)
            recent_week_entries = [entry for entry in entries 
                                 if datetime.datetime.strptime(entry['date'], '%Y-%m-%d').date() >= week_ago]
            st.info(f"**Last 7 days:** {len(recent_week_entries)} entries")

# Add Entry Page
elif current_page == "Add Entry":
    st.header("Add New Food Entry")
    
    with st.container():
        with st.form("food_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                date = st.date_input("Date", datetime.date.today())
                category = st.selectbox("Meal Category", ["Breakfast", "Lunch", "Snacks", "Dinner"])
                protein = st.number_input("Protein Intake (grams)", min_value=0, value=0, step=5)
            
            with col2:
                food = st.text_input("What did you eat?", placeholder="e.g., Grilled chicken with rice")
                beverage = st.text_input("What did you drink?", placeholder="e.g., Water, Protein shake")
                notes = st.text_area("Additional Notes (optional)", placeholder="Any extra details about your meal...")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button("🍽️ Add Food Entry", use_container_width=True)
            
            if submitted:
                if food:
                    new_entry = {
                        "date": date.isoformat(),
                        "category": category,
                        "food": food,
                        "beverage": beverage,
                        "protein": protein,
                        "notes": notes,
                        "created_at": datetime.datetime.now().isoformat()
                    }
                    
                    add_entry(new_entry)
                    st.success("✅ Entry added successfully!")
                    st.balloons()
                else:
                    st.error("Please fill in at least the food field!")

# View & Edit Entries Page
elif current_page == "View & Edit Entries":
    st.header("View & Manage Entries")
    
    entries = get_all_entries()
    if not entries:
        st.info("No entries yet! Add some food entries first.")
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            df = transform_to_daily_table()
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"food_tracker_{datetime.date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            pdf_buffer = create_pdf_report()
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_buffer,
                file_name=f"food_tracker_report_{datetime.date.today()}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        with col3:
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.rerun()
        
        st.markdown("---")
        st.subheader("Daily Summary Table")
        daily_df = transform_to_daily_table()
        
        if not daily_df.empty:
            st.dataframe(
                daily_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Date": st.column_config.DateColumn("Date", width="large"),
                    "Breakfast": st.column_config.TextColumn("Breakfast", width="large"),
                    "Lunch": st.column_config.TextColumn("Lunch", width="large"),
                    "Snacks": st.column_config.TextColumn("Snacks", width="large"),
                    "Dinner": st.column_config.TextColumn("Dinner", width="large"),
                    "Beverage": st.column_config.TextColumn("Beverage", width="medium"),
                    "Protein Intake": st.column_config.NumberColumn("Protein (g)", format="%d g")
                }
            )
        
        st.markdown("---")
        st.subheader("Manage Individual Entries")
        
        for entry in entries:
            with st.expander(f"{entry['date']} - {entry['category']}: {entry['food']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    with st.form(f"edit_form_{entry['id']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_date = st.date_input("Date", datetime.datetime.strptime(entry['date'], '%Y-%m-%d').date(), key=f"date_{entry['id']}")
                            edit_category = st.selectbox("Category", ["Breakfast", "Lunch", "Snacks", "Dinner"], index=["Breakfast", "Lunch", "Snacks", "Dinner"].index(entry['category']), key=f"cat_{entry['id']}")
                            edit_protein = st.number_input("Protein (g)", value=entry.get('protein', 0), key=f"prot_{entry['id']}")
                        
                        with col2:
                            edit_food = st.text_input("Food", value=entry['food'], key=f"food_{entry['id']}")
                            edit_beverage = st.text_input("Beverage", value=entry['beverage'], key=f"bev_{entry['id']}")
                            edit_notes = st.text_area("Notes", value=entry.get('notes', ''), key=f"notes_{entry['id']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Update Entry", use_container_width=True):
                                updated_entry = {
                                    "date": edit_date.isoformat(),
                                    "category": edit_category,
                                    "food": edit_food,
                                    "beverage": edit_beverage,
                                    "protein": edit_protein,
                                    "notes": edit_notes,
                                    "created_at": entry.get('created_at', datetime.datetime.now().isoformat())
                                }
                                update_entry(entry['id'], updated_entry)
                                st.success("Entry updated successfully!")
                                st.rerun()
                        
                        with col2:
                            if st.form_submit_button("🗑️ Delete Entry", use_container_width=True):
                                delete_entry(entry['id'])
                                st.success(f"Deleted entry: {entry['food']}")
                                st.rerun()
        
        st.markdown("---")
        st.subheader("🚨 Danger Zone")
        
        with st.expander("Clear All Entries"):
            st.warning("This will permanently delete ALL your food entries. This action cannot be undone!")
            st.write(f"**Total entries that will be deleted:** {len(entries)}")
            
            if st.button("🗑️ Yes, Clear All Entries", type="primary", use_container_width=True):
                clear_all_entries()
                st.success("All entries cleared successfully!")
                st.rerun()

# Protein Analytics Page
elif current_page == "Protein Analytics":
    st.header("📈 Protein Intake Analytics")
    
    entries = get_all_entries()
    if not entries:
        st.info("No entries yet! Add some food entries first.")
    else:
        daily_protein, weekly_protein, category_protein = create_protein_charts()
        
        col1, col2, col3 = st.columns(3)
        total_protein = sum(entry.get('protein', 0) for entry in entries)
        unique_dates = len(set(entry['date'] for entry in entries))
        avg_daily = total_protein / unique_dates if unique_dates > 0 else 0
        
        with col1:
            st.metric("Total Protein", f"{total_protein:.0f} g")
        with col2:
            st.metric("Average Daily", f"{avg_daily:.1f} g")
        with col3:
            st.metric("Days Tracked", unique_dates)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Daily Protein Intake")
            if len(daily_protein) > 1:
                fig_daily = px.line(daily_protein, x='date', y='protein', 
                                  labels={'protein': 'Protein (g)', 'date': 'Date'},
                                  title="Daily Protein Trend")
                fig_daily.update_traces(line=dict(color='#FF4B4B', width=3))
                st.plotly_chart(fig_daily, use_container_width=True)
            else:
                st.info("Need more data points for daily trend")
        
        with col2:
            st.subheader("Protein by Meal Category")
            if not category_protein.empty:
                fig_category = px.pie(category_protein, values='protein', names='category',
                                    title="Protein Distribution by Meal",
                                    color_discrete_sequence=px.colors.sequential.Redor_r)
                st.plotly_chart(fig_category, use_container_width=True)
        
        st.subheader("Weekly Protein Intake")
        if len(weekly_protein) > 1:
            fig_weekly = px.bar(weekly_protein, x='week', y='protein',
                              labels={'protein': 'Protein (g)', 'week': 'Week'},
                              title="Weekly Protein Summary")
            fig_weekly.update_traces(marker_color='#FF6B6B')
            st.plotly_chart(fig_weekly, use_container_width=True)
        
        st.subheader("🏋️ Protein Goals")
        goal_col1, goal_col2 = st.columns(2)
        
        with goal_col1:
            protein_goal = st.number_input("Set your daily protein goal (grams)", 
                                         min_value=0, value=130, step=5)
        
        with goal_col2:
            if daily_protein is not None and not daily_protein.empty:
                latest_protein = daily_protein['protein'].iloc[-1]
                goal_percentage = (latest_protein / protein_goal) * 100
                st.metric("Latest Day vs Goal", f"{goal_percentage:.1f}%", 
                         delta=f"{latest_protein - protein_goal:.0f} g")

# Enhanced Statistics in sidebar
st.sidebar.markdown("---")
st.sidebar.header("Statistics")
entries = get_all_entries()
if entries:
    total_entries = len(entries)
    unique_dates = len(set(entry['date'] for entry in entries))
    total_protein = sum(entry.get('protein', 0) for entry in entries)
    avg_daily_protein = total_protein / unique_dates if unique_dates > 0 else 0
    
    st.sidebar.metric("Total Entries", total_entries)
    st.sidebar.metric("Days Tracked", unique_dates)
    st.sidebar.metric("Total Protein", f"{total_protein:.0f} g")
    st.sidebar.metric("Avg Daily Protein", f"{avg_daily_protein:.1f} g")
else:
    st.sidebar.info("Add entries to see stats!")

# Close database connection when done
conn.close()