from dataclasses import dataclass
from typing import List, Dict, Set
from pulp import *
import pandas as pd
from excel_processor import ExcelDataProcessor

@dataclass
class Person:
    id: str
    name: str
    church_id: str
    is_leader: bool
    gender: str

@dataclass
class Room:
    id: str
    building_id: str
    floor: int
    capacity: int
    current_occupants: List[str] = None

@dataclass
class Building:
    id: str
    name: str
    floors: int
    rooms_per_floor: Dict[int, int]

class HousingOptimizer:
    def __init__(self):
        self.people: Dict[str, Person] = {}
        self.rooms: Dict[str, Room] = {}
        self.buildings: Dict[str, Building] = {}
        self.assignments: Dict[str, str] = {}  # person_id -> room_id

    def add_person(self, person: Person):
        """Add or update a person in the system"""
        self.people[person.id] = person

    def remove_person(self, person_id: str):
        """Remove a person (e.g., dropout) and trigger reoptimization"""
        if person_id in self.people:
            del self.people[person_id]
            if person_id in self.assignments:
                del self.assignments[person_id]
                self.optimize()

    def add_building(self, building: Building):
        """Add a building to the system"""
        self.buildings[building.id] = building

    def optimize(self, parameters=None) -> bool:
        """Run the main optimization algorithm with optional parameter controls"""
        if parameters is None:
            parameters = {
                'gender_separation': True,
                'leader_separation': True,
                'church_grouping': True,
                'room_capacity': True
            }
            
        # Create the optimization problem
        prob = LpProblem("Conference_Housing_Assignment", LpMinimize)

        # Decision variables: 1 if person i is assigned to room j, 0 otherwise
        x = LpVariable.dicts("assign",
                           ((p, r) for p in self.people.keys() 
                            for r in self.rooms.keys()),
                           cat='Binary')

        # Objective: Minimize room usage (can be modified later for other objectives)
        prob += lpSum(x[p, r] for p in self.people.keys() 
                     for r in self.rooms.keys())

        # Constraints
        # 1. Each person must be assigned to exactly one room
        for p_id in self.people.keys():
            prob += lpSum(x[p_id, r] for r in self.rooms.keys()) == 1

        # 2. Room capacity constraints (if enabled)
        if parameters['room_capacity']:
            for r_id, room in self.rooms.items():
                prob += lpSum(x[p_id, r_id] for p_id in self.people.keys()) <= room.capacity

        # 3. Gender separation constraints (if enabled)
        if parameters['gender_separation']:
            for r_id in self.rooms.keys():
                males = [p_id for p_id, p in self.people.items() if p.gender == 'M']
                females = [p_id for p_id, p in self.people.items() if p.gender == 'F']
                
                # If there's anyone of one gender in a room, there can't be anyone of the other gender
                for m in males:
                    for f in females:
                        prob += x[m, r_id] + x[f, r_id] <= 1

        # 4. Leader/Student separation (if enabled)
        if parameters['leader_separation']:
            for r_id in self.rooms.keys():
                leaders = [p_id for p_id, p in self.people.items() if p.is_leader]
                students = [p_id for p_id, p in self.people.items() if not p.is_leader]
                
                # If there's a leader in a room, there can't be any students
                for l in leaders:
                    for s in students:
                        prob += x[l, r_id] + x[s, r_id] <= 1

        # 5. Church grouping preference (if enabled)
        if parameters['church_grouping']:
            # Add soft constraints to encourage same-church grouping
            for church_id in set(p.church_id for p in self.people.values()):
                church_members = [p_id for p_id, p in self.people.items() 
                                if p.church_id == church_id]
                # Try to keep church members in same or adjacent rooms
                for building in self.buildings.values():
                    for floor in range(1, building.floors + 1):
                        floor_rooms = [r_id for r_id, r in self.rooms.items() 
                                     if r.building_id == building.id and r.floor == floor]
                        if floor_rooms:
                            # Encourage at least some church members on each floor
                            prob += lpSum(x[m, r] for m in church_members 
                                       for r in floor_rooms) >= 1

        # Solve the problem
        status = prob.solve()

        if LpStatus[prob.status] == 'Optimal':
            # Update assignments
            self.assignments = {}
            for p_id in self.people.keys():
                for r_id in self.rooms.keys():
                    if value(x[p_id, r_id]) > 0.5:  # Using 0.5 as threshold for binary variables
                        self.assignments[p_id] = r_id
            return True
        return False

    def get_assignments(self) -> pd.DataFrame:
        """Return current assignments in a readable format"""
        assignments_list = []
        for person_id, room_id in self.assignments.items():
            person = self.people[person_id]
            room = self.rooms[room_id]
            building = self.buildings[room.building_id]
            
            assignments_list.append({
                'person_id': person_id,
                'name': person.name,
                'church_id': person.church_id,
                'is_leader': person.is_leader,
                'building': building.name,
                'floor': room.floor,
                'room_id': room_id
            })
        
        return pd.DataFrame(assignments_list)

    def load_from_excel(self, file_path: str):
        """Load data from Excel file"""
        processor = ExcelDataProcessor()
        data = processor.process_data_for_optimizer(file_path)
        
        # Load buildings
        for building_id, building_data in data['buildings'].items():
            building = Building(
                id=building_data['id'],
                name=building_data['name'],
                floors=building_data['floors'],
                rooms_per_floor={}  # Will be populated from rooms data
            )
            self.add_building(building)
        
        # Load rooms
        for room_id, room_data in data['rooms'].items():
            room = Room(
                id=room_data['id'],
                building_id=room_data['building_id'],
                floor=room_data['floor'],
                capacity=room_data['capacity']
            )
            self.rooms[room_id] = room
            
        # Load people
        for person_id, person_data in data['people'].items():
            person = Person(
                id=person_data['id'],
                name=person_data['name'],
                church_id=person_data['church_id'],
                is_leader=person_data['is_leader'],
                gender=person_data['gender']
            )
            self.add_person(person)