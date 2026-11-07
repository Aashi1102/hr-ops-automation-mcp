import os
from mcp.server.mcpserver import MCPServer, Context
from typing import List, Dict,Optional
from HRMS import *  # Import all classes from HRMS
from utils import seed_services  # Import the seeding function
from email_manager import EmailSender  # Import the EmailSender class
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

email_sender = EmailSender(
    smtp_server="smtp.gmail.com",
    port=587,
    username=os.getenv("Email"),
    password=os.getenv("Password"),
    use_tls=True
)

mcp = MCPServer("HR_Assist_Project")

emp_manager = EmployeeManager()
leave_manager = LeaveManager()
ticket_manager = TicketManager()
meeting_manager = MeetingManager()

seed_services(emp_manager, leave_manager, meeting_manager, ticket_manager)  # Seed the services with dummy data


#tools
#prompts
#KNOWLEDGE


@mcp.tool()

def add_employee(name: str, manager_id: str,email: str) -> str:
    """
    Add a new employee to the HRMS system.
    Employee ID is generated automatically.
    """

    emp = EmployeeCreate(
        emp_id=emp_manager.get_next_emp_id(),
        name=name,
        manager_id=manager_id,
        email=email
    )
    emp_manager.add_employee(emp)
    return f"Employee {name} with ID {emp.emp_id} added successfully."

@mcp.tool()

def get_employee_details(name: str) -> Dict[str, str]:
    """
    Get details of an employee by their name.
    """
    matches = emp_manager.search_employee_by_name(name)
    if len(matches) == 0:
        raise ValueError(f"Employee with name {name} not found.")
    
    emp_id_list = matches[0]
    return emp_manager.get_employee_details(emp_id_list)


@mcp.tool()
def send_email(
    subject: str,
    body: str,
    to_emails: List[str] | str
) -> str:
    """
    Send an email using the configured HR email account.

    Args:
        subject: Subject of the email.
        body: Content of the email.
        to_emails: Recipient email address or list of addresses.
    """

    try:
        email_sender.send_email(
            subject=subject,
            body=body,
            to_emails=to_emails,
            from_email=email_sender.username
        )

        return f"Email successfully sent to {to_emails}"

    except Exception as e:
        import logging

        logging.exception("Email sending failed")

        raise RuntimeError(
            f"Unable to send email: {type(e).__name__}: {e}"
        )

@mcp.tool()
def create_ticket(emp_id: str, item: str, reason:str) -> str:
    """
    Create a ticket for buying required items for an employee.
    :param emp_id: Employee ID
    :param item: Item requested (Laptop, ID Card, etc.)
    :param reason: Reason for the request
    :return: Confirmation message
    """
    ticket_req = TicketCreate(emp_id=emp_id, item=item, reason=reason)
    return ticket_manager.create_ticket(ticket_req)

@mcp.tool()
def update_ticket_status(ticket_id: str, status: str) -> str:
    """
    Update the status of a ticket.
    :param ticket_id: Ticket ID
    :param status: New status of the ticket
    :return: Confirmation message
    """
    ticket_status_update = TicketStatusUpdate(status=status)
    return ticket_manager.update_ticket_status(ticket_status_update, ticket_id)

@mcp.tool()
def list_tickets(employee_id: str, status: str) -> str:
    """
    List tickets for an employee with optional status filter.
    :param employee_id: Employee ID
    :param status: Ticket status (optional)
    :return: List of tickets
    """
    return ticket_manager.list_tickets(employee_id=employee_id, status=status)


@mcp.tool()
def schedule_meeting(employee_id: str, meeting_datetime: datetime, topic: str) -> str:
    """
    Schedule a meeting for an employee.
    :param employee_id: Employee ID
    :param meeting_datetime: Date and time of the meeting in python datetime format
    :param topic: Topic of the meeting
    :return: Confirmation message
    """
    meeting_req = MeetingCreate(
        emp_id=employee_id,
        meeting_dt=meeting_datetime,
        topic=topic
    )
    return meeting_manager.schedule_meeting(meeting_req)


@mcp.tool()
def get_meetings(employee_id: str) -> str:
    """
    Get the list of meetings scheduled for an employee.
    :param employee_id: Employee ID
    :return: List of meetings
    """
    return meeting_manager.get_meetings(employee_id)


@mcp.tool()
def cancel_meeting(employee_id: str, meeting_datetime: datetime, topic: str) -> str:
    """
    Cancel a scheduled meeting for an employee.
    :param employee_id: Employee ID
    :param meeting_datetime: Date and time of the meeting in python datetime format
    :param topic: Topic of the meeting (optional)
    :return: Confirmation message
    """
    meeting_req = MeetingCancelRequest(
        emp_id=employee_id,
        meeting_dt=meeting_datetime,
        topic=topic
    )
    return meeting_manager.cancel_meeting(meeting_req)


@mcp.tool()
def get_employee_leave_balance(emp_id: str) -> str:
    """
    Get the leave balance of an employee.
    :param emp_id: Employee ID
    :return: Leave balance message
    """
    return leave_manager.get_leave_balance(emp_id)

@mcp.tool()
def apply_leave(emp_id: str, leave_dates: list) -> str:
    """
    Apply for leave for an employee.
    :param emp_id: Employee ID
    :param leave_dates: List of leave dates
    :return: Leave application status message
    """
    req = LeaveApplyRequest(emp_id=emp_id, leave_dates=leave_dates)
    return leave_manager.apply_leave(req)


@mcp.tool()
def get_leave_history(emp_id: str) -> str:
    """
    Get the leave history of an employee.
    :param emp_id: Employee ID
    :return: Leave history message
    """
    return leave_manager.get_leave_history(emp_id)


@mcp.prompt("onboard_new_employee")
def onboard_new_employee(employee_name: str, manager_name: str):
    return f"""Onboard a new employee with the following details:
    - Name: {employee_name}
    - Manager Name: {manager_name}
    Steps to follow:
    - Add the employee to the HRMS system.
    - Send a welcome email to the employee with their login credentials. (Format: employee_name@atliq.com)
    - Notify the manager about the new employee's onboarding.
    - Raise tickets for a new laptop, id card, and other necessary equipment.
    - Schedule an introductory meeting between the employee and the manager.
    """



if __name__ == "__main__":
    mcp.run(transport="stdio")
