import streamlit as st
from src.canvas_api import CanvasAPI
from src.data_processor import DiscussionDataProcessor
from src.grading_service import GradingService
from src.config import *
import os
import requests

def main():
    # Layout setup
    col1, col2, col3 = st.columns([1, 4, 1])
    
    # Add UC logo on left
    with col1:
        st.image("uc_logo.png", width=100)
    
    # Add title and author in middle
    with col2:
        st.title("Canvas Discussion Board Grading App")
        st.markdown("**Author:** Aedhan Scott  \n**Capstone Reader:** Jeffery Shaffer")
    
    # Add Lindner logo on right
    with col3:
        st.image("lindner_logo.png", width=100)
    
    # Debug Mode Toggle - Moved to top level
    debug_mode = st.checkbox("Debug Mode")
    
    # Initialize session state
    if 'api_initialized' not in st.session_state:
        st.session_state.api_initialized = False
    
    # API Key Configuration Section
    st.subheader("API Configuration")
    
    # Try to get API keys from secrets or environment variables
    try:
        default_canvas_key = st.secrets.api_keys.canvas if hasattr(st.secrets, "api_keys") and hasattr(st.secrets.api_keys, "canvas") else os.environ.get("CANVAS_API_KEY", "")
        default_openai_key = st.secrets.api_keys.openai if hasattr(st.secrets, "api_keys") and hasattr(st.secrets.api_keys, "openai") else os.environ.get("OPENAI_API_KEY", "")
    except Exception:
        default_canvas_key = os.environ.get("CANVAS_API_KEY", "")
        default_openai_key = os.environ.get("OPENAI_API_KEY", "")
    
    # Create input fields for API keys
    col1, col2 = st.columns(2)
    with col1:
        canvas_api_key = st.text_input("Canvas API Key", value=default_canvas_key, type="password")
    with col2:
        openai_api_key = st.text_input("OpenAI API Key", value=default_openai_key, type="password")
    
    # Initialize APIs with user-provided keys
    if st.button("Initialize APIs"):
        initialize_apis(canvas_api_key, openai_api_key)
    
    if st.session_state.api_initialized:
        run_grading_workflow(debug_mode)
    else:
        st.info("Please enter your API keys and click 'Initialize APIs' to continue.")

def initialize_apis(canvas_api_key, openai_api_key):
    """Initialize API services from user-provided keys"""
    try:
        if canvas_api_key and openai_api_key:
            st.session_state.canvas_api = CanvasAPI(CANVAS_BASE_URL, canvas_api_key)
            st.session_state.grading_service = GradingService(
                openai_api_key, DEFAULT_MODEL, DEFAULT_TEMPERATURE)
            st.session_state.api_initialized = True
            st.success("APIs initialized successfully!")
        else:
            if not canvas_api_key:
                st.warning("Canvas API key is required.")
            if not openai_api_key:
                st.warning("OpenAI API key is required.")
    except Exception as e:
        st.error(f"Error initializing APIs: {e}")

def run_grading_workflow(debug_mode: bool):
    if debug_mode:
        st.subheader("Debug Mode - Direct URL Input")
        col1, col2 = st.columns(2)
        with col1:
            direct_url = st.text_input(
                "Enter Canvas Discussion URL",
                help="Example: https://uc.instructure.com/api/v1/courses/1717948/discussion_topics/9120860/view"
            )
        with col2:
            st.session_state.post_limit = st.number_input(
                "Number of Posts to Grade (0 for all)", 
                min_value=0, 
                value=5
            )
        
        if direct_url:
            try:
                params = {"access_token": st.session_state.canvas_api.api_key}
                response = requests.get(direct_url, params=params)
                data = response.json()
                if data:
                    df_participants, df_posts = DiscussionDataProcessor.process_discussion_data(data)
                    if st.session_state.post_limit > 0:
                        df_posts = df_posts.head(st.session_state.post_limit)
                    show_grading_options(df_participants, df_posts, "debug")
            except Exception as e:
                st.error(f"Error processing URL: {e}")
        return

    # Regular workflow
    # Initialize session states for tracking button clicks if not already present
    if 'fetch_courses_clicked' not in st.session_state:
        st.session_state.fetch_courses_clicked = False
    
    if st.button("Fetch Courses"):
        st.session_state.fetch_courses_clicked = True
        try:
            courses = st.session_state.canvas_api.get_courses()
            if courses:
                st.session_state.courses = courses
                st.success(f"Found {len(courses)} courses")
            else:
                st.warning("No courses found. Please check your Canvas API key and permissions.")
        except Exception as e:
            st.error(f"Error fetching courses: {e}")
    
    if 'courses' in st.session_state and st.session_state.courses:
        course_options = {course[1]: course[0] for course in st.session_state.courses}
        selected_course = st.selectbox("Select Course", options=list(course_options.keys()))
        course_id = course_options[selected_course]
        
        if 'fetch_topics_clicked' not in st.session_state:
            st.session_state.fetch_topics_clicked = False
        
        if st.button("Fetch Discussion Topics"):
            st.session_state.fetch_topics_clicked = True
            try:
                topics = st.session_state.canvas_api.get_discussion_topics(course_id)
                if topics:
                    st.session_state.topics = topics
                    st.success(f"Found {len(topics)} discussion topics")
                else:
                    st.warning("No discussion topics found for this course.")
            except Exception as e:
                st.error(f"Error fetching discussion topics: {e}")
        
        if 'topics' in st.session_state and st.session_state.topics:
            topic_options = {topic[1]: topic[0] for topic in st.session_state.topics}
            selected_topic = st.selectbox("Select Discussion Topic", options=list(topic_options.keys()))
            topic_id = topic_options[selected_topic]
            
            try:
                data = st.session_state.canvas_api.get_discussion_data(course_id, topic_id)
                if data:
                    df_participants, df_posts = DiscussionDataProcessor.process_discussion_data(data)
                    show_grading_options(df_participants, df_posts, f"{course_id}_{topic_id}")
                else:
                    st.warning("No data found for this discussion topic.")
            except Exception as e:
                st.error(f"Error fetching discussion data: {e}")

def show_grading_options(df_participants, df_posts, identifier):
    if 'current_data' not in st.session_state:
        st.session_state.current_data = {
            'df_participants': df_participants,
            'df_posts': df_posts,
            'identifier': identifier
        }
    
    # Store values in session state if not already present
    if 'post_points' not in st.session_state:
        st.session_state.post_points = DEFAULT_POST_POINTS
    if 'reply_points' not in st.session_state:
        st.session_state.reply_points = DEFAULT_REPLY_POINTS
    if 'system_prompt' not in st.session_state:
        st.session_state.system_prompt = "You are a teaching assistant grading discussion board posts. Grade based on quality, relevance, and critical thinking."

    st.subheader("Grading Configuration")
    col1, col2 = st.columns(2)
    with col1:
        post_points = st.number_input(
            "Points for Posts", 
            value=st.session_state.post_points,
            key="post_points_input"
        )
    with col2:
        reply_points = st.number_input(
            "Points for Replies", 
            value=st.session_state.reply_points,
            key="reply_points_input"
        )
    
    system_prompt = st.text_area(
        "Grading Instructions",
        value=st.session_state.system_prompt,
        height=100,
        key="system_prompt_input"
    )
    
    if st.button("Grade Posts", key="grade_button"):
        process_grading(
            st.session_state.current_data['df_participants'],
            st.session_state.current_data['df_posts'],
            post_points,
            reply_points,
            system_prompt,
            st.session_state.current_data['identifier']
        )

def process_grading(df_participants, df_posts, post_points, reply_points, system_prompt, identifier):
    # Create a status container to show detailed progress
    status_container = st.container()
    with status_container:
        st.write("Starting grading process...")
        st.write(f"Number of posts to grade: {len(df_posts)}")
        progress_bar = st.progress(0)
        status_text = st.empty()
        error_text = st.empty()
    
    # Check if dataframe is empty
    if df_posts.empty:
        status_container.error("No posts found to grade!")
        return
    
    # Create a copy of the dataframe to avoid modifying the original during iteration
    graded_posts = df_posts.copy()
    
    # Set up columns for grades and feedback if they don't exist
    if 'grade_numeric' not in graded_posts.columns:
        graded_posts['grade_numeric'] = None
    if 'grade_feedback' not in graded_posts.columns:
        graded_posts['grade_feedback'] = None
    
    # Track if any grading was successful
    grading_success = False
    
    # Apply post limit if in debug mode
    if 'post_limit' in st.session_state and st.session_state.post_limit > 0:
        graded_posts = graded_posts.head(st.session_state.post_limit)
    
    try:
        # Display DataFrame columns for debugging
        error_text.text(f"DataFrame columns: {list(graded_posts.columns)}")
        
        for idx, row in graded_posts.iterrows():
            progress = (idx + 1) / len(graded_posts)
            progress_bar.progress(progress)
            status_text.text(f"Grading post {idx + 1}/{len(graded_posts)}")
            
            try:
                # Debug info
                error_text.text(f"Processing post type: {row['type']}, length: {len(row['message'])}")
                
                # Call the grading service
                grade, feedback = st.session_state.grading_service.grade_discussion(
                    row['message'],
                    row['type'],
                    post_points,
                    reply_points,
                    system_prompt
                )
                
                # Update the dataframe with results
                graded_posts.at[idx, 'grade_numeric'] = grade
                graded_posts.at[idx, 'grade_feedback'] = feedback
                grading_success = True
                
                # Show current grading result
                error_text.text(f"Graded post {idx + 1}: Score = {grade}")
                
            except Exception as e:
                error_text.error(f"Error grading post {idx + 1}: {str(e)}")
                # Continue with next post instead of breaking
                continue
        
        # Update the original dataframe with graded results
        for idx in graded_posts.index:
            if idx in df_posts.index:
                df_posts.at[idx, 'grade_numeric'] = graded_posts.at[idx, 'grade_numeric']
                df_posts.at[idx, 'grade_feedback'] = graded_posts.at[idx, 'grade_feedback']
        
        if grading_success:
            # Save the results
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            output_file = f"{OUTPUT_DIR}/graded_discussion_{identifier}.csv"
            df_posts.to_csv(output_file, index=False)
            
            status_container.success("Grading completed!")
            st.download_button(
                "Download Graded Results",
                df_posts.to_csv(index=False),
                file_name=f"graded_discussion_{identifier}.csv",
                mime="text/csv"
            )
            
            # Display results in the app - with dynamic column selection
            st.subheader("Grading Results")
            
            # Determine which columns to display based on what's available
            display_columns = []
            
            # Try to find user identification column
            if 'user_name' in df_posts.columns:
                display_columns.append('user_name')
            elif 'username' in df_posts.columns:
                display_columns.append('username')
            elif 'user_id' in df_posts.columns:
                display_columns.append('user_id')
            
            # Add other important columns
            for col in ['type', 'message', 'grade_numeric', 'grade_feedback']:
                if col in df_posts.columns:
                    display_columns.append(col)
            
            # If no columns were found, display all columns
            if not display_columns:
                st.dataframe(df_posts.head(10))
            else:
                st.dataframe(df_posts[display_columns].head(10))
        else:
            status_container.warning("No posts were successfully graded. Check the errors above.")
            
    except Exception as e:
        status_container.error(f"Critical error in grading process: {str(e)}")
        # Print full stack trace for debugging
        import traceback
        error_text.code(traceback.format_exc())

if __name__ == "__main__":
    main()