# Canvas Discussion Board Grading App

![UC Logo](uc_logo.png) ![Lindner Logo](lindner_logo.png)

## Overview

The Canvas Discussion Board Grading App is a Streamlit-based application designed to automate and streamline the grading process for Canvas LMS discussion boards. This tool leverages OpenAI's language models to evaluate student posts and replies based on customizable grading criteria, saving educators valuable time while providing consistent feedback.

**Author:** Aedhan Scott  
**Capstone Reader:** Jeffery Shaffer

## Features

- **Canvas LMS Integration**: Connect directly to Canvas courses and discussion boards using the Canvas API
- **AI-Powered Grading**: Utilize OpenAI's language models to evaluate discussion posts and replies
- **Customizable Grading**: Set point values for posts and replies, and customize grading instructions
- **Batch Processing**: Grade entire discussion boards at once
- **Export Functionality**: Download grading results as CSV files for easy import back into Canvas
- **Debug Mode**: Test the application with direct URL input for troubleshooting

## Prerequisites

- Python 3.8+
- Canvas API Key (with appropriate permissions)
- OpenAI API Key

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/canvas-discussion-grading-app.git
   cd canvas-discussion-grading-app
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your API keys:
   - Create a `.env` file in the project root with the following content:
     ```
     CANVAS_API_KEY=your_canvas_api_key
     OPENAI_API_KEY=your_openai_api_key
     ```
   - Alternatively, you can input these keys directly in the application

## Usage

1. Start the application:
   ```
   streamlit run app.py
   ```

2. Enter your Canvas and OpenAI API keys in the application interface
3. Click "Initialize APIs" to connect to the services
4. Follow the workflow to select a course and discussion topic
5. Configure grading parameters (points for posts/replies and grading instructions)
6. Click "Grade Posts" to begin the automated grading process
7. Review and download the grading results

### Debug Mode

Enable Debug Mode to directly input a Canvas discussion URL for testing purposes. This is useful for troubleshooting or when you want to grade a specific discussion without navigating through the course selection interface.

## Project Structure

- `app.py`: Main Streamlit application
- `src/`: Source code directory
  - `canvas_api.py`: Canvas LMS API integration
  - `data_processor.py`: Discussion data processing utilities
  - `grading_service.py`: OpenAI integration for grading
  - `config.py`: Application configuration settings
- `Canvas_Discussion_Exports/`: Directory for exported grading results

## Configuration

The application's default settings are defined in `src/config.py`:

- **Canvas API**: Base URL and default parameters
- **OpenAI**: Default model (gpt-4o) and temperature settings
- **Grading**: Default point values for posts and replies
- **Output**: Directory for exported grading results

## How It Works

1. **API Connection**: The app connects to both Canvas LMS and OpenAI APIs
2. **Data Retrieval**: Fetches courses, discussion topics, and discussion data from Canvas
3. **Data Processing**: Processes raw discussion data into structured formats
4. **AI Grading**: Sends each post/reply to OpenAI for evaluation based on custom criteria
5. **Results Processing**: Compiles grading results and provides download options

## Limitations

- Requires valid API keys with appropriate permissions
- Grading quality depends on the OpenAI model used and the clarity of grading instructions
- API rate limits may affect processing time for large discussion boards

## Future Enhancements

- Support for additional LMS platforms
- Batch processing of multiple discussion boards
- Enhanced analytics and reporting features
- Integration with Canvas gradebook for direct grade submission

## License

[Specify your license information here]

## Acknowledgments

- University of Cincinnati
- Lindner College of Business
- OpenAI for providing the language models
- Canvas LMS for their API documentation 