import streamlit as st
import pandas as pd
from housing_optimizer import HousingOptimizer
from excel_processor import ExcelDataProcessor, create_example_excel

def initialize_parameters():
    if 'parameters' not in st.session_state:
        st.session_state.parameters = {
            'gender_separation': True,
            'leader_separation': True,
            'church_grouping': True,
            'room_capacity': True
        }

def customize_streamlit():
    # [Previous customize_streamlit code remains the same]
    pass

def main():
    customize_streamlit()
    initialize_parameters()
    
    st.markdown("""
        <h1 style='text-align: center; margin-bottom: 2rem; color: #1e3d59;'>
            🏠 Conference Housing Optimizer
        </h1>
    """, unsafe_allow_html=True)
    
    # Sidebar remains the same
    with st.sidebar:
        # [Previous sidebar code remains the same]
        pass

    # Main tabs - add Parameters tab
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload Data", "⚙️ Parameters", "📊 Review Data", "🏠 Assignments"])
    
    # Upload Tab
    with tab1:
        # [Previous upload tab code remains the same]
        pass

    # New Parameters Tab
    with tab2:
        st.markdown("""
            <div style='text-align: center; padding: 1rem; background-color: #f8f9fa; 
                border-radius: 0.5rem; margin-bottom: 2rem;'>
                <h2 style='margin: 0;'>Optimization Parameters</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # Parameter toggles
        st.markdown("### Assignment Criteria")
        
        # Gender Separation
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("""
                **Gender Separation**  
                Males and females will not be assigned to the same room
            """)
        with col2:
            st.session_state.parameters['gender_separation'] = st.toggle(
                "Enable Gender Separation",
                value=st.session_state.parameters['gender_separation'],
                key='gender_toggle'
            )
        
        st.divider()
        
        # Leader Separation
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("""
                **Leader/Student Separation**  
                Leaders will not be assigned to rooms with students
            """)
        with col2:
            st.session_state.parameters['leader_separation'] = st.toggle(
                "Enable Leader Separation",
                value=st.session_state.parameters['leader_separation'],
                key='leader_toggle'
            )
        
        st.divider()
        
        # Church Grouping
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("""
                **Church Grouping**  
                Attempt to keep members of the same church in proximity
            """)
        with col2:
            st.session_state.parameters['church_grouping'] = st.toggle(
                "Enable Church Grouping",
                value=st.session_state.parameters['church_grouping'],
                key='church_toggle'
            )
        
        st.divider()
        
        # Room Capacity
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("""
                **Room Capacity Limits**  
                Enforce maximum capacity limits for each room
            """)
        with col2:
            st.session_state.parameters['room_capacity'] = st.toggle(
                "Enable Capacity Limits",
                value=st.session_state.parameters['room_capacity'],
                key='capacity_toggle'
            )
        
        # Display current parameter status
        st.markdown("### Current Configuration")
        status_df = pd.DataFrame([
            {"Parameter": k, "Status": "Enabled" if v else "Disabled"} 
            for k, v in st.session_state.parameters.items()
        ])
        st.dataframe(status_df, use_container_width=True)

    # Review Tab
    with tab3:
        # [Previous review tab code remains the same]
        pass

    # Assignments Tab
    with tab4:
        if 'optimizer' in st.session_state:
            optimizer = st.session_state['optimizer']
            
            st.markdown("""
                <div style='text-align: center; padding: 1rem; background-color: #f8f9fa; 
                    border-radius: 0.5rem; margin-bottom: 2rem;'>
                    <h2 style='margin: 0;'>Room Assignments</h2>
                </div>
            """, unsafe_allow_html=True)
            
            # Add parameters summary before generation
            with st.expander("View Current Parameters"):
                st.dataframe(status_df, use_container_width=True)
            
            if st.button("🎯 Generate Assignments"):
                with st.spinner("Optimizing room assignments..."):
                    # Pass parameters to optimizer
                    success = optimizer.optimize(parameters=st.session_state.parameters)
                
                # [Rest of assignments tab code remains the same]
                pass
        else:
            st.info("Please upload data in the Upload tab first")

if __name__ == "__main__":
    main()