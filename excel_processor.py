from dataclasses import dataclass
import pandas as pd
from typing import Dict, List, Tuple
import logging
from pathlib import Path

@dataclass
class ExcelConfig:
    """Configuration for Excel sheet names and required columns"""
    PARTICIPANTS_SHEET = "Participants"
    BUILDINGS_SHEET = "Buildings"
    ROOMS_SHEET = "Rooms"
    
    # Required columns for each sheet
    PARTICIPANT_COLUMNS = {
        "participant_id": str,
        "name": str,
        "church_id": str,
        "is_leader": bool,
        "gender": str
    }
    
    BUILDING_COLUMNS = {
        "building_id": str,
        "name": str,
        "floors": int,
    }
    
    ROOM_COLUMNS = {
        "room_id": str,
        "building_id": str,
        "floor": int,
        "capacity": int
    }

class ExcelDataProcessor:
    def __init__(self, config: ExcelConfig = None):
        self.config = config or ExcelConfig()
        self.logger = logging.getLogger(__name__)

    def validate_sheet_columns(self, df: pd.DataFrame, required_columns: Dict[str, type], sheet_name: str) -> bool:
        """Validate that all required columns are present and of correct type"""
        missing_columns = set(required_columns.keys()) - set(df.columns)
        if missing_columns:
            self.logger.error(f"Missing required columns in {sheet_name}: {missing_columns}")
            return False
        
        # Validate data types
        for col, expected_type in required_columns.items():
            if expected_type == bool:
                # Convert common boolean representations
                df[col] = df[col].map({'Yes': True, 'No': False, True: True, False: False, 
                                     1: True, 0: False, 'TRUE': True, 'FALSE': False})
            try:
                df[col] = df[col].astype(expected_type)
            except Exception as e:
                self.logger.error(f"Error converting column {col} to {expected_type} in {sheet_name}: {str(e)}")
                return False
        return True

    def load_excel_data(self, file_path: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load and validate data from Excel file"""
        try:
            # Read all sheets
            xlsx = pd.ExcelFile(file_path)
            
            # Verify all required sheets exist
            required_sheets = [self.config.PARTICIPANTS_SHEET, 
                             self.config.BUILDINGS_SHEET, 
                             self.config.ROOMS_SHEET]
            
            missing_sheets = set(required_sheets) - set(xlsx.sheet_names)
            if missing_sheets:
                raise ValueError(f"Missing required sheets: {missing_sheets}")

            # Load each sheet
            participants_df = pd.read_excel(xlsx, self.config.PARTICIPANTS_SHEET)
            buildings_df = pd.read_excel(xlsx, self.config.BUILDINGS_SHEET)
            rooms_df = pd.read_excel(xlsx, self.config.ROOMS_SHEET)

            # Validate each sheet
            if not all([
                self.validate_sheet_columns(participants_df, self.config.PARTICIPANT_COLUMNS, "Participants"),
                self.validate_sheet_columns(buildings_df, self.config.BUILDING_COLUMNS, "Buildings"),
                self.validate_sheet_columns(rooms_df, self.config.ROOM_COLUMNS, "Rooms")
            ]):
                raise ValueError("Data validation failed")

            return participants_df, buildings_df, rooms_df

        except Exception as e:
            self.logger.error(f"Error loading Excel file: {str(e)}")
            raise

    def process_data_for_optimizer(self, file_path: str) -> Dict:
        """Process Excel data and return in format needed for HousingOptimizer"""
        participants_df, buildings_df, rooms_df = self.load_excel_data(file_path)
        
        # Convert DataFrames to dictionary format needed by optimizer
        processed_data = {
            'people': {},
            'buildings': {},
            'rooms': {}
        }
        
        # Process participants
        for _, row in participants_df.iterrows():
            processed_data['people'][row['participant_id']] = {
                'id': row['participant_id'],
                'name': row['name'],
                'church_id': row['church_id'],
                'is_leader': row['is_leader'],
                'gender': row['gender']
            }
        
        # Process buildings
        for _, row in buildings_df.iterrows():
            processed_data['buildings'][row['building_id']] = {
                'id': row['building_id'],
                'name': row['name'],
                'floors': row['floors']
            }
        
        # Process rooms
        for _, row in rooms_df.iterrows():
            processed_data['rooms'][row['room_id']] = {
                'id': row['room_id'],
                'building_id': row['building_id'],
                'floor': row['floor'],
                'capacity': row['capacity']
            }
        
        return processed_data

def create_example_excel(output_path: str):
    """Create an example Excel file with the required structure"""
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Create example participants data
        participants_data = {
            'participant_id': ['P001', 'P002', 'P003'],
            'name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
            'church_id': ['C1', 'C1', 'C2'],
            'is_leader': [False, True, False],
            'gender': ['M', 'F', 'M']
        }
        pd.DataFrame(participants_data).to_excel(writer, sheet_name='Participants', index=False)

        # Create example buildings data
        buildings_data = {
            'building_id': ['B1', 'B2'],
            'name': ['North Hall', 'South Hall'],
            'floors': [3, 4]
        }
        pd.DataFrame(buildings_data).to_excel(writer, sheet_name='Buildings', index=False)

        # Create example rooms data
        rooms_data = {
            'room_id': ['B1-1-101', 'B1-1-102', 'B1-2-201'],
            'building_id': ['B1', 'B1', 'B1'],
            'floor': [1, 1, 2],
            'capacity': [2, 2, 2]
        }
        pd.DataFrame(rooms_data).to_excel(writer, sheet_name='Rooms', index=False) 