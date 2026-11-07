# Test script for EmployeeManager and related services
from HRMS import *
from utils import seed_services

emp_manager = EmployeeManager()
leave_manager = LeaveManager()
ticket_manager = TicketManager()
meeting_manager = MeetingManager()

seed_services(
    emp_manager,
    leave_manager,
    meeting_manager,
    ticket_manager
)

for name in ["Tony Sharma", "Sarah", "Suhani"]:
    print(f"\nSearching: {name}")

    matches = emp_manager.search_employee_by_name(name)

    print("Matches:", matches)

    if matches:
        print(
            "Details:",
            emp_manager.get_employee_details(matches[0])
        )