import streamlit as st
import pandas as pd
from housing_optimizer import HousingOptimizer
from excel_processor import ExcelDataProcessor, create_example_excel

def customize_streamlit():
    st.set_page_config(
        page_title="Conference Housing Optimizer",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .main {
            padding: 1rem 2rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 1rem 2rem;
        }
        .stButton>button {
            width: 100%;
            background-color: #4CAF50;
            color: white;
        }
        .stMetric .label {
            font-size: 1.2rem;
        }
        div[data-testid="stMetricValue"] {
            font-size: 2rem;
        }
        .styled-metric {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .info-box {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #e8f4f8;
            margin: 1rem 0;
        }
        .success-box {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #d4edda;
            margin: 1rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

def main():
    customize_streamlit()
    
    # Header
    st.markdown("""
        <h1 style='text-align: center; margin-bottom: 2rem; color: #1e3d59;'>
            🏠 Conference Housing Optimizer
        </h1>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
            <div style='text-align: center; padding: 1rem; background-color: #f8f9fa; 
                border-radius: 0.5rem; margin-bottom: 1rem;'>
                <h3 style='margin: 0;'>Quick Actions</h3>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("📥 Download Example Template"):
            create_example_excel("example_template.xlsx")
            with open("example_template.xlsx", "rb") as file:
                st.download_button(
                    label="Save Template",
                    data=file,
                    file_name="housing_template.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        st.markdown("""
            <div class='info-box'>
                <h4>About This Tool</h4>
                <p>This tool helps organize conference housing assignments by:</p>
                <ul>
                    <li>Managing participant data</li>
                    <li>Handling building/room assignments</li>
                    <li>Optimizing room allocations</li>
                    <li>Generating assignment reports</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📤 Upload Data", "📊 Review Data", "🏠 Assignments"])
    
    # Upload Tab
    with tab1:
        st.markdown("""
            <div style='text-align: center; padding: 1.5rem; background-color: #f8f9fa; 
                border-radius: 0.5rem; margin-bottom: 2rem;'>
                <h2 style='margin: 0;'>Upload Your Data</h2>
            </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Upload Excel file with Participants, Buildings, and Rooms sheets",
            type=['xlsx', 'xls']
        )
        
        if uploaded_file:
            try:
                st.session_state['optimizer'] = HousingOptimizer()
                st.session_state['optimizer'].load_from_excel(uploaded_file)
                st.markdown("""
                    <div class='success-box'>
                        ✅ Data loaded successfully!
                    </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
                st.markdown("""
                    <div class='info-box'>
                        <h4>Required File Format:</h4>
                        <ul>
                            <li>Participants sheet (columns: participant_id, name, church_id, is_leader, gender)</li>
                            <li>Buildings sheet (columns: building_id, name, floors)</li>
                            <li>Rooms sheet (columns: room_id, building_id, floor, capacity)</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
    
    # Review Tab
    with tab2:
        if 'optimizer' in st.session_state:
            optimizer = st.session_state['optimizer']
            
            st.markdown("""
                <div style='text-align: center; padding: 1rem; background-color: #f8f9fa; 
                    border-radius: 0.5rem; margin-bottom: 2rem;'>
                    <h2 style='margin: 0;'>Data Overview</h2>
                </div>
            """, unsafe_allow_html=True)
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("👥 Total Participants", 
                         len(optimizer.people),
                         help="Number of people to be assigned rooms")
            with col2:
                st.metric("🏢 Buildings", 
                         len(optimizer.buildings),
                         help="Available buildings")
            with col3:
                st.metric("🚪 Rooms", 
                         len(optimizer.rooms),
                         help="Total available rooms")
            
            # Data tables
            st.markdown("<h3>Detailed Data</h3>", unsafe_allow_html=True)
            
            st.subheader("Participants")
            participants_df = pd.DataFrame([
                {
                    "ID": p.id,
                    "Name": p.name,
                    "Church": p.church_id,
                    "Leader": "Yes" if p.is_leader else "No",
                    "Gender": p.gender
                }
                for p in optimizer.people.values()
            ])
            st.dataframe(participants_df, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Buildings")
                buildings_df = pd.DataFrame([
                    {
                        "ID": b.id,
                        "Name": b.name,
                        "Floors": b.floors
                    }
                    for b in optimizer.buildings.values()
                ])
                st.dataframe(buildings_df, use_container_width=True)
            
            with col2:
                st.subheader("Rooms")
                rooms_df = pd.DataFrame([
                    {
                        "ID": r.id,
                        "Building": r.building_id,
                        "Floor": r.floor,
                        "Capacity": r.capacity
                    }
                    for r in optimizer.rooms.values()
                ])
                st.dataframe(rooms_df, use_container_width=True)
        else:
            st.info("Please upload data in the Upload tab first")
    
    # Assignments Tab
    with tab3:
        if 'optimizer' in st.session_state:
            optimizer = st.session_state['optimizer']
            
            st.markdown("""
                <div style='text-align: center; padding: 1rem; background-color: #f8f9fa; 
                    border-radius: 0.5rem; margin-bottom: 2rem;'>
                    <h2 style='margin: 0;'>Room Assignments</h2>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("🎯 Generate Assignments"):
                with st.spinner("Optimizing room assignments..."):
                    success = optimizer.optimize()
                
                if success:
                    st.markdown("""
                        <div class='success-box'>
                            ✅ Optimization completed successfully!
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Get and display assignments
                    assignments = optimizer.get_assignments()
                    st.dataframe(assignments, use_container_width=True)
                    
                    # Download button
                    csv = assignments.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Assignments",
                        data=csv,
                        file_name="room_assignments.csv",
                        mime="text/csv"
                    )
                    
                    # Summary statistics
                    st.markdown("<h3>Assignment Summary</h3>", unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("<h4>Assignments by Building</h4>", unsafe_allow_html=True)
                        st.dataframe(
                            assignments['building'].value_counts().reset_index(),
                            use_container_width=True
                        )
                    
                    with col2:
                        st.markdown("<h4>Assignments by Floor</h4>", unsafe_allow_html=True)
                        floor_counts = assignments.groupby(['building', 'floor']).size()
                        st.dataframe(
                            floor_counts.reset_index(name='count'),
                            use_container_width=True
                        )
                else:
                    st.error("Could not find valid assignment configuration")
                    st.markdown("""
                        <div class='info-box'>
                            <h4>Possible reasons:</h4>
                            <ul>
                                <li>Insufficient rooms for all participants</li>
                                <li>Conflicting constraints (gender/leader separation)</li>
                                <li>Invalid data in the input file</li>
                            </ul>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Please upload data in the Upload tab first")

if __name__ == "__main__":
    main()