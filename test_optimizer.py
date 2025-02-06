import pandas as pd
from housing_optimizer import HousingOptimizer
from excel_processor import ExcelDataProcessor, create_example_excel
from datetime import datetime

def test_housing_optimizer():
    # 1. Create a test data file
    test_file = "test_conference_data.xlsx"
    print("1. Creating test Excel file...")
    create_test_data(test_file)
    
    # 2. Initialize the optimizer
    print("\n2. Initializing Housing Optimizer...")
    optimizer = HousingOptimizer()
    
    # 3. Load data from Excel
    print("\n3. Loading data from Excel...")
    optimizer.load_from_excel(test_file)
    
    # 4. Print summary of loaded data
    print("\nLoaded Data Summary:")
    print(f"Number of participants: {len(optimizer.people)}")
    print(f"Number of buildings: {len(optimizer.buildings)}")
    print(f"Number of rooms: {len(optimizer.rooms)}")
    
    # 5. Run optimization
    print("\n4. Running optimization...")
    success = optimizer.optimize()
    
    if success:
        print("\nOptimization successful!")
        # 6. Get and display assignments
        assignments = optimizer.get_assignments()
        print("\nSample of Room Assignments:")
        print(assignments.head())
        
        # 7. Save assignments to Excel
        output_file = f"assignments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        assignments.to_excel(output_file, index=False)
        print(f"\nFull assignments saved to: {output_file}")
        
        # 8. Print summary statistics
        print("\nAssignment Summary:")
        print(f"Total assignments made: {len(assignments)}")
        print("\nAssignments by building:")
        print(assignments['building'].value_counts())
        
        # 9. Test handling a dropout
        print("\n5. Testing dropout handling...")
        first_person_id = list(optimizer.people.keys())[0]
        print(f"Removing participant {first_person_id}")
        optimizer.remove_person(first_person_id)
        
        # 10. Rerun optimization and show new assignments
        success = optimizer.optimize()
        if success:
            new_assignments = optimizer.get_assignments()
            print("\nNew assignments after dropout:")
            print(new_assignments.head())
    else:
        print("\nOptimization failed - could not find valid assignment")

def create_test_data(filename: str):
    """Create a more comprehensive test dataset"""
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Create participants data
        num_participants = 40  # Reduced number
        participants_data = {
            'participant_id': [f'P{str(i).zfill(3)}' for i in range(num_participants)],
            'name': [f'Person {i}' for i in range(num_participants)],
            'church_id': [f'C{i % 5 + 1}' for i in range(num_participants)],  # 5 churches
            'is_leader': [i % 8 == 0 for i in range(num_participants)],  # Fewer leaders
            'gender': ['M' if i < num_participants//2 else 'F' for i in range(num_participants)]  # Equal gender split
        }
        pd.DataFrame(participants_data).to_excel(writer, sheet_name='Participants', index=False)
        
        # Create buildings data
        buildings_data = {
            'building_id': ['B1', 'B2'],
            'name': ['North Hall', 'South Hall'],
            'floors': [3, 3]
        }
        pd.DataFrame(buildings_data).to_excel(writer, sheet_name='Buildings', index=False)
        
        # Create rooms data
        rooms_data = []
        for building in ['B1', 'B2']:
            for floor in range(1, 4):  # 3 floors
                for room in range(1, 11):  # 10 rooms per floor
                    rooms_data.append({
                        'room_id': f'{building}-{floor}-{str(room).zfill(2)}',
                        'building_id': building,
                        'floor': floor,
                        'capacity': 2
                    })
        pd.DataFrame(rooms_data).to_excel(writer, sheet_name='Rooms', index=False)

if __name__ == "__main__":
    test_housing_optimizer()