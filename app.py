import streamlit as st
import pandas as pd
from housing_optimizer import HousingOptimizer
from excel_processor import ExcelDataProcessor, create_example_excel

def main():
    st.set_page_config(page_title="Conference Housing Optimizer", layout="wide")
    
    st.title("Conference Housing Optimizer")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("Controls")
        if st.button("Download Example Template"):
            create_example_excel("example_template.xlsx")
            with open("example_template.xlsx", "rb") as file:
                st.download_button(
                    label="📥 Download Template",
                    data=file,
                    file_name="housing_template.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    # Main area
    tab1, tab2, tab3 = st.tabs(["📤 Upload Data", "📊 Review Data", "🏠 Assignments"])
    
    # Upload Tab
    with tab1:
        st.header("Upload Your Data")
        uploaded_file = st.file_uploader(
            "Upload Excel file with Participants, Buildings, and Rooms sheets",
            type=['xlsx', 'xls']
        )
        
        if uploaded_file:
            try:
                # Store the uploaded file in session state
                st.session_state['optimizer'] = HousingOptimizer()
                st.session_state['optimizer'].load_from_excel(uploaded_file)
                st.success("Data loaded successfully!")
                
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
                st.info("Please make sure your file has the correct sheets and columns:")
                st.markdown("""
                - Participants (participant_id, name, church_id, is_leader, gender)
                - Buildings (building_id, name, floors)
                - Rooms (room_id, building_id, floor, capacity)
                """)
    
    # Review Tab
    with tab2:
        if 'optimizer' in st.session_state:
            optimizer = st.session_state['optimizer']
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Participants", len(optimizer.people))
            with col2:
                st.metric("Total Buildings", len(optimizer.buildings))
            with col3:
                st.metric("Total Rooms", len(optimizer.rooms))
            
            # Detailed data views
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
            
            if st.button("Generate Assignments"):
                with st.spinner("Optimizing room assignments..."):
                    success = optimizer.optimize()
                
                if success:
                    st.success("✅ Optimization completed successfully!")
                    
                    # Get and display assignments
                    assignments = optimizer.get_assignments()
                    st.dataframe(assignments, use_container_width=True)
                    
                    # Add download button
                    csv = assignments.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Assignments",
                        data=csv,
                        file_name="room_assignments.csv",
                        mime="text/csv"
                    )
                    
                    # Display summary statistics
                    st.subheader("Assignment Summary")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("Assignments by Building")
                        st.dataframe(
                            assignments['building'].value_counts().reset_index(),
                            use_container_width=True
                        )
                    
                    with col2:
                        st.write("Assignments by Floor")
                        floor_counts = assignments.groupby(['building', 'floor']).size()
                        st.dataframe(
                            floor_counts.reset_index(name='count'),
                            use_container_width=True
                        )
                else:
                    st.error("Could not find valid assignment configuration")
                    st.info("""
                    This could be due to:
                    - Insufficient rooms for all participants
                    - Conflicting constraints (gender/leader separation)
                    - Invalid data in the input file
                    """)
        else:
            st.info("Please upload data in the Upload tab first")

if __name__ == "__main__":
    main()