import streamlit as st
import requests
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# Set page configuration
st.set_page_config(
    page_title="AgentVerse",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Define the base URL for the API
BASE_URL = "https://agentverse-uz89.onrender.com"

# Define session state variables
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'landing'
if 'current_project_id' not in st.session_state:
    st.session_state.current_project_id = None
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 'chat'
if 'show_add_project' not in st.session_state:
    st.session_state.show_add_project = False
if 'active_project_id' not in st.session_state:
    st.session_state.active_project_id = None
if 'clear_chat_input' not in st.session_state:
    st.session_state.clear_chat_input = False

# CSS for styling
st.markdown("""
<style>
    .chat-container {
        border-radius: 10px;
        margin-bottom: 20px;
        padding: 10px;
    }
    .user-message {
        background-color: #2f2f2f;  /* Dark grey */
        color: white;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        text-align: right;
        max-width: 80%;
        margin-left: auto;
    }
    .assistant-message {
        background-color: #3a3a3a;  /* Medium grey */
        color: white;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        text-align: left;
        max-width: 80%;
    }
    .timestamp {
        font-size: 0.8em;
        color: #aaa;
        margin-top: 5px;
    }
    .project-card {
        cursor: pointer;
        padding: 20px;
        border-radius: 10px;
        background-color: #2c2c2c;  /* Slightly lighter grey */
        color: white;
        margin: 10px 0;
        transition: all 0.3s;
    }
    .project-card:hover {
        background-color: #444444;
        transform: translateY(-2px);
    }
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
    }
    .chat-input {
        border-radius: 20px;
        border: 1px solid #ddd;
        padding: 10px 15px;
    }
    .tab-container {
        margin-top: 20px;
    }
    .stAlert {
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)


# Function to fetch all projects
def get_projects():
    try:
        response = requests.get(f"{BASE_URL}/projects/")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching projects: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return []

# Function to create a new project
def create_project(name):
    try:
        response = requests.post(
            f"{BASE_URL}/projects/",
            json={"name": name}
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error creating project: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return None

# Function to initialize chat with files
def init_chat(project_id, employee_file, project_file, financial_file):
    try:
        files = {
            'employee_file': employee_file,
            'project_file': project_file,
            'financial_file': financial_file
        }
        response = requests.post(
            f"{BASE_URL}/chat/init/{project_id}",
            files=files
        )
        if response.status_code == 200:
            return True
        else:
            st.error(f"Error initializing chat: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return False

# Function to continue chat
def continue_chat(project_id, text):
    try:
        response = requests.post(
            f"{BASE_URL}/chat/continue/{project_id}",
            json={"text": text}
        )
        
        # Check if response is plain text (not JSON)
        if response.headers.get('content-type') == 'text/plain':
            return response.text
        
        # For JSON responses
        if response.status_code == 200:
            try:
                return response.json()
            except:
                return response.text
        else:
            st.error(f"Error sending message: {response.status_code}")
            st.error(f"Response text: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        st.error("This might be due to CORS issues if you're running the frontend locally.")
        st.info("Check that your backend has CORS configured correctly for localhost.")
        return None

# Function to get chat history
def get_chat_history(project_id):
    try:
        response = requests.get(f"{BASE_URL}/chats/{project_id}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching chat history: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return []

# Function to format timestamp
def format_timestamp(timestamp_str):
    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return timestamp.strftime("%B %d, %Y %I:%M %p")
    except Exception:
        return timestamp_str

# Function to navigate to a page
def navigate_to(page, project_id=None):
    st.session_state.current_page = page
    if project_id is not None:
        st.session_state.current_project_id = project_id
        # Only set as active project when creating a new project
        if page == "chat" and st.session_state.show_add_project:
            st.session_state.active_project_id = project_id
    st.rerun()

# Function to toggle the add project popup
def toggle_add_project():
    st.session_state.show_add_project = not st.session_state.show_add_project
    st.rerun()

# Function to change the current tab
def change_tab(tab):
    st.session_state.current_tab = tab
    st.rerun()

# Create project risk visualizations
def render_project_health_gauge(health_percentage):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=health_percentage,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Project Health"},
        number={'font': {'size': 40}, 'suffix': '%'},  # Improved number formatting
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': 'red'},
                {'range': [30, 70], 'color': 'yellow'},
                {'range': [70, 100], 'color': 'green'}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': health_percentage}}))
    
    # Center the gauge correctly
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        autosize=True
    )
    return fig

def create_risk_breakdown_chart(risks):
    risk_types = {}
    for risk in risks:
        factor = risk.get("factor", "Unknown")
        if factor in risk_types:
            risk_types[factor] += 1
        else:
            risk_types[factor] = 1
    
    fig = px.pie(
        names=list(risk_types.keys()),
        values=list(risk_types.values()),
        title="Risk Breakdown by Type",
        color_discrete_sequence=px.colors.sequential.Reds_r
    )
    fig.update_layout(height=400)
    return fig

def create_risk_heatmap(risks):
    probabilities = []
    impacts = []
    descriptions = []
    types = []
    colors = []
    
    severity_impact = {
        "Critical": 0.9, 
        "High": 0.7, 
        "Medium": 0.5, 
        "Low": 0.3
    }
    
    severity_color = {
        "Critical": "red", 
        "High": "orange", 
        "Medium": "yellow", 
        "Low": "green"
    }
    
    for risk in risks:
        severity = risk.get("severity", "Low")
        factor = risk.get("factor", "Unknown")
        description = risk.get("description", "No description")
        
        probability = risk.get("probability", 0.5)
        impact = severity_impact.get(severity, 0.3)
        
        probabilities.append(probability)
        impacts.append(impact)
        descriptions.append(description)
        types.append(factor)
        colors.append(severity_color.get(severity, "green"))
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=probabilities,
        y=impacts,
        mode='markers',
        marker=dict(
            size=12,
            color=colors,
            line=dict(width=1, color='DarkSlateGrey')
        ),
        text=[f"{t}: {d}" for t, d in zip(types, descriptions)],
        hoverinfo='text'
    ))
    
    fig.update_layout(
        title="Risk Evaluation Chart (Probability vs. Impact)",
        xaxis_title="Probability",
        yaxis_title="Impact",
        xaxis=dict(range=[0, 1]),
        yaxis=dict(range=[0, 1]),
        height=400
    )
    
    return fig

def create_risk_trend_chart(risk_history):
    dates = []
    critical = []
    high = []
    medium = []
    low = []
    
    for entry in risk_history:
        dates.append(entry.get("date"))
        counts = entry.get("counts", {})
        critical.append(counts.get("Critical", 0))
        high.append(counts.get("High", 0))
        medium.append(counts.get("Medium", 0))
        low.append(counts.get("Low", 0))
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates, y=critical,
        mode='lines+markers',
        name='Critical',
        line=dict(color='red', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=high,
        mode='lines+markers',
        name='High',
        line=dict(color='orange', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=medium,
        mode='lines+markers',
        name='Medium',
        line=dict(color='yellow', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=low,
        mode='lines+markers',
        name='Low',
        line=dict(color='green', width=2)
    ))
    
    fig.update_layout(
        title="Risk Trend Over Time",
        xaxis_title="Date",
        yaxis_title="Number of Risks",
        height=400
    )
    
    return fig

def create_timeline_chart(milestones):
    names = []
    start_dates = []
    end_dates = []
    colors = []
    
    for milestone in milestones:
        names.append(milestone.get("name", "Unnamed"))
        planned_date = milestone.get("planned_date")
        actual_date = milestone.get("actual_date")
        status = milestone.get("status", "unknown")
        
        start_dates.append(planned_date)
        end_dates.append(actual_date if actual_date else planned_date)
        
        if status == "completed":
            colors.append("green")
        elif status == "in_progress":
            colors.append("blue")
        else:
            colors.append("gray")
    
    fig = px.timeline(
        x_start=start_dates,
        x_end=end_dates,
        y=names,
        color=colors,
        labels={"x_start": "Planned Date", "x_end": "Actual/Expected Date", "color": "Status"}
    )
    
    fig.update_layout(
        title="Project Milestones",
        xaxis_title="Date",
        height=400
    )
    
    return fig

# Sample data for visualizations
def get_sample_data():
    # Sample risk data
    identified_risks = [
        {"severity": "Critical", "factor": "Schedule", "description": "Project timeline slipping due to resource constraints", "probability": 0.8},
        {"severity": "High", "factor": "Budget", "description": "Increased vendor costs exceeding planned budget", "probability": 0.6},
        {"severity": "Medium", "factor": "Resources", "description": "Key team member availability reduced", "probability": 0.4},
        {"severity": "High", "factor": "Technical", "description": "Integration issues with legacy systems", "probability": 0.7},
        {"severity": "Medium", "factor": "Market", "description": "Competitor launched similar product", "probability": 0.5},
        {"severity": "Critical", "factor": "Schedule", "description": "Delayed approvals from stakeholders", "probability": 0.9},
        {"severity": "Low", "factor": "Resources", "description": "Minor skill gaps in development team", "probability": 0.3}
    ]
    
    # Sample risk history data
    risk_history = [
        {"date": "2025-01-15", "counts": {"Critical": 3, "High": 5, "Medium": 8, "Low": 4}},
        {"date": "2025-02-01", "counts": {"Critical": 2, "High": 6, "Medium": 7, "Low": 5}},
        {"date": "2025-02-15", "counts": {"Critical": 3, "High": 4, "Medium": 6, "Low": 6}},
        {"date": "2025-03-01", "counts": {"Critical": 4, "High": 3, "Medium": 5, "Low": 7}},
        {"date": "2025-03-15", "counts": {"Critical": 2, "High": 4, "Medium": 4, "Low": 8}},
        {"date": "2025-04-01", "counts": {"Critical": 1, "High": 3, "Medium": 5, "Low": 7}}
    ]
    
    # Sample milestone data
    milestones = [
        {"name": "Project Kickoff", "planned_date": "2025-01-01", "actual_date": "2025-01-01", "status": "completed"},
        {"name": "Requirements Gathering", "planned_date": "2025-01-15", "actual_date": "2025-01-20", "status": "completed"},
        {"name": "Design Phase", "planned_date": "2025-02-01", "actual_date": "2025-02-10", "status": "completed"},
        {"name": "Development Phase", "planned_date": "2025-02-15", "actual_date": None, "status": "in_progress"},
        {"name": "Testing Phase", "planned_date": "2025-03-15", "actual_date": None, "status": "not_started"},
        {"name": "Deployment", "planned_date": "2025-04-15", "actual_date": None, "status": "not_started"}
    ]
    
    return {
        "health_percentage": 65,
        "identified_risks": identified_risks,
        "risk_history": risk_history,
        "milestones": milestones
    }

# Layout for the landing page
def render_landing_page():
    st.image("AGENTVERSE.png", use_container_width=True)
    
    # Header with Add Project button
    st.markdown("""
    <div class="header-container">
        <h1>AgentVerse- Project Risk Management System</h1>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("➕ Add Project"):
            toggle_add_project()
    
    # Add Project popup
    if st.session_state.show_add_project:
        with st.form(key="add_project_form"):
            st.subheader("Add New Project")
            project_name = st.text_input("Project Name")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                employee_file = st.file_uploader("Employee Data (CSV)", type="csv")
            with col2:
                project_file = st.file_uploader("Project Data (CSV)", type="csv")
            with col3:
                financial_file = st.file_uploader("Financial Data (CSV)", type="csv")
            
            submitted = st.form_submit_button("Get Started")
            
            if submitted:
                if not project_name:
                    st.error("Please enter a project name")
                elif not employee_file or not project_file or not financial_file:
                    st.error("Please upload all required files")
                else:
                    # Create project
                    project = create_project(project_name)
                    if project:
                        project_id = project.get("project_id")
                        
                        # Initialize chat with files
                        success = init_chat(
                            project_id, 
                            employee_file,
                            project_file,
                            financial_file
                        )
                        
                        if success:
                            st.success("Project created successfully!")
                            # Set this as the active project since it's new
                            st.session_state.active_project_id = project_id
                            navigate_to("chat", project_id)
                        else:
                            st.error("Failed to initialize chat")
    
    # Projects table
    st.subheader("Your Projects")
    
    projects = get_projects()
    
    if not projects:
        st.info("No projects found. Create a new project to get started.")
    else:
        for project in projects:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"""
                <div class="project-card" onclick="window.location.href='#'">
                    <h3>{project.get('name')}</h3>
                    <p>Project ID: {project.get('project_id')}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("View", key=f"view_{project.get('project_id')}"):
                    # When viewing an existing project, don't set it as active
                    navigate_to("chat", project.get('project_id'))

# Layout for the chat page
# Add this modified render_chat_page() function:

def render_chat_page():
    project_id = st.session_state.current_project_id

    # Get all projects to display the current project name
    projects = get_projects()
    current_project = next((p for p in projects if p.get('project_id') == project_id), None)
    project_name = current_project.get('name', f"Project {project_id}") if current_project else f"Project {project_id}"

    # Header with navigation
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back to Projects"):
            navigate_to("landing")
    with col2:
        st.header(f"{project_name}")

    # Tabs
    tab1, tab2 = st.tabs(["Chat", "Visualization"])

    with tab1:
        # Check if this is an active project (created in current session)
        is_active_project = st.session_state.active_project_id == project_id
        
        if is_active_project:
            render_active_chat(project_id)
        else:
            render_chat_history(project_id)
    
    with tab2:
        render_visualizations()

# Function to render chat history (read-only, no input box)
def render_chat_history(project_id):
    st.subheader("Project Risk Analysis History")
    st.info("Viewing chat history only. Create a new project to start a conversation.")
    
    chat_history = get_chat_history(project_id)

    if not chat_history:
        st.info("No chat history found for this project.")
    else:
        for entry in chat_history:
            # User message
            message = entry.get("message")
            if message:
                st.markdown(f"""
                <div class="user-message">
                    <p>{message}</p>
                    <div class="timestamp">{format_timestamp(entry.get("timestamp"))}</div>
                </div>
                """, unsafe_allow_html=True)

            # Assistant response
            response = entry.get("response")
            if response:
                st.markdown(f"""
                <div class="assistant-message">
                    <p>{response}</p>
                    <div class="timestamp">{format_timestamp(entry.get("timestamp"))}</div>
                </div>
                """, unsafe_allow_html=True)

# Function to render active chat with input box
def render_active_chat(project_id):
    st.subheader("Project Risk Analysis")
    
    # Chat history
    chat_history = get_chat_history(project_id)

    if not chat_history:
        st.info("No messages yet. Start a conversation below.")
    else:
        for entry in chat_history:
            # User message
            message = entry.get("message")
            if message:
                st.markdown(f"""
                <div class="user-message">
                    <p>{message}</p>
                    <div class="timestamp">{format_timestamp(entry.get("timestamp"))}</div>
                </div>
                """, unsafe_allow_html=True)

            # Assistant response
            response = entry.get("response")
            if response:
                st.markdown(f"""
                <div class="assistant-message">
                    <p>{response}</p>
                    <div class="timestamp">{format_timestamp(entry.get("timestamp"))}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Input for new messages
    st.markdown("---")
    
    # Initialize the clear chat input flag if not already set
    if 'clear_chat_input' not in st.session_state:
        st.session_state.clear_chat_input = False
        
    # Create a default value for the text area
    default_value = "" if st.session_state.clear_chat_input else st.session_state.get("chat_input", "")
    
    # Reset the clear flag after it's been used
    if st.session_state.clear_chat_input:
        st.session_state.clear_chat_input = False
    
    with st.form(key="chat_form"):
        user_message = st.text_area("Ask a question about project risks:", 
                                   value=default_value,
                                   height=100, 
                                   key="chat_input")
        submitted = st.form_submit_button("Send")

        if submitted and user_message:
            response = continue_chat(project_id, user_message)
            if response:
                # Set the flag to clear the input on next render
                st.session_state.clear_chat_input = True
                st.rerun()

# Function to render visualizations tab
def render_visualizations():
    st.subheader("Risk Visualizations")
    
    # Load sample data for visualizations
    sample_data = get_sample_data()
    
    # Project health visualization
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### Project Health Score")
        health_gauge = render_project_health_gauge(sample_data["health_percentage"])
        st.plotly_chart(health_gauge, use_container_width=True)
    
    with col2:
        st.markdown("### Project Status")
        st.markdown("""
        - **Schedule Status:** Moderately Delayed
        - **Resource Status:** At Risk
        - **Budget Status:** Healthy
        - **Completion:** 42.5%
        
        **Executive Summary:**
        The project is currently at risk with several critical schedule delays and resource constraints. 
        Key stakeholders should focus on addressing the critical risks related to schedule and resources.
        """)
    
    # Risk visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Risk Breakdown")
        risk_breakdown = create_risk_breakdown_chart(sample_data["identified_risks"])
        st.plotly_chart(risk_breakdown, use_container_width=True)
    
    with col2:
        st.markdown("### Risk Evaluation Chart")
        risk_heatmap = create_risk_heatmap(sample_data["identified_risks"])
        st.plotly_chart(risk_heatmap, use_container_width=True)
    
    # Risk trend chart
    st.markdown("### Risk Trend Over Time")
    risk_trend = create_risk_trend_chart(sample_data["risk_history"])
    st.plotly_chart(risk_trend, use_container_width=True)
    
    # Project timeline
    st.markdown("### Project Timeline")
    timeline_chart = create_timeline_chart(sample_data["milestones"])
    st.plotly_chart(timeline_chart, use_container_width=True)
    
    # Risk table
    st.markdown("### Identified Risks")
    risks_df = pd.DataFrame(sample_data["identified_risks"])
    st.dataframe(risks_df, use_container_width=True)
    
    # Mitigation recommendations
    st.markdown("### Risk Mitigation Recommendations")
    
    critical_risks = [r for r in sample_data["identified_risks"] if r["severity"] == "Critical"]
    for risk in critical_risks:
        st.error(f"**{risk['factor']}**: {risk['description']}")
        st.markdown("""
        **Recommended Actions:**
        - Review resource allocation and consider adding temporary contractors
        - Implement fast-tracking by overlapping activities
        - Schedule urgent stakeholder meeting to address approval delays
        """)
        st.markdown("---")

# Main app logic
def main():
    # Add ping route support to keep app alive
    if "ping" in st.query_params:
        st.write("✅ Ping received. App is alive.")
        return

    if st.session_state.current_page == "landing":
        render_landing_page()
    elif st.session_state.current_page == "chat":
        render_chat_page()

if __name__ == "__main__":
    main()