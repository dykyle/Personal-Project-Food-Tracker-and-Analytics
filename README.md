# 🍕 Food Tracker

A sleek and powerful Streamlit web application for tracking daily meals, beverages, and protein intake. Built with Python and featuring beautiful data visualizations.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)

## 🚀 Features

### 📊 Dashboard
- **Overview Cards**: Beautiful metrics display for total entries, days tracked, and protein intake
- **Recent Entries Table**: Clean tabular view of your latest food entries
- **Quick Insights**: Smart statistics about your eating habits

### 🍽️ Food Management
- **Add Entries**: Simple form to log meals with category, food, beverage, and protein
- **Edit & Delete**: Full CRUD operations for managing existing entries
- **Daily Summary**: Organized view of meals by date and category

### 📈 Analytics
- **Protein Trends**: Interactive line charts showing daily protein intake
- **Category Distribution**: Pie charts breaking down protein by meal type
- **Weekly Overview**: Bar charts for weekly protein summaries
- **Goal Tracking**: Set and monitor daily protein targets

### 💾 Data Management
- **CSV Export**: Download your data for external analysis
- **PDF Reports**: Generate printable reports of your food logs
- **Local Storage**: JSON-based database that persists between sessions

## 🎯 Usage
- **Adding Food Entries**
  1. Navigate to "Add Entry" in the sidebar
  2. Fill in the date, meal category, food items, beverages, and protein content
  3. Click "Add Food Entry" to save

- **Viewing & Managing Data**
  1. Use "View & Edit Entries" to see all your data in a organized table
  2. Expand any entry to edit or delete it
  3. Use the download buttons to export your data
 
- **Analyzing Progress**
  1. Visit "Protein Analytics" to see interactive charts
  2. Set protein goals and track your progress
  3. Monitor trends in your eating habits

## 🔧 Configuration
- **Data Storage**
  - All data is stored locally in food_log.json
  - The data folder is ignored by Git for privacy
  - Your personal food data remains on your machine
 
- **Customization**
You can easily modify:
   - Protein goals in the Analytics page
   - Meal categories in the Add Entry form
   - Color schemes in the Plotly charts

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone [https://github.com/dykyle/food-tracker.git](https://github.com/dykyle/Personal-Project-Food-Tracker-and-Analytics.git)
   cd food-tracker

2. **Create a virtual environment (recommended)
   ```bash
   python -m venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate

3. **Instal Dependencies**
   ```bash
   pip install -r requirements.txt
   # You can also do py -m install -r requirements.txt

4. **Run the Application**
   ```bash
   streamlit run FT/food_tracker.py

   # You can also do py -m streamlit run FT/food_tracker.py

5. **Open your browser**
   - The app will automatically open at http://localhost:8501
   - If not, manually navigate to the URL shown in the terminal
