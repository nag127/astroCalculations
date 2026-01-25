"""
CrewAI-based answer generation endpoint for astrology questions.
This replaces the direct OpenAI calls with a multi-agent CrewAI system.
"""

import json
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from crewai import Agent, Task, Crew, Process
from crewai.tools import tool

logger = logging.getLogger(__name__)


class AnswerRequest(BaseModel):
    """Request model for answer generation."""
    question: str = Field(..., description="User's astrology question")
    chart_data: Dict[str, Any] = Field(..., description="Full astrology chart JSON data")
    needed_sections: list[str] = Field(default_factory=list, description="Chart sections needed for answer")
    current_date: str = Field(..., description="Current date in YYYY-MM-DD format")
    dasha_info: Optional[Dict[str, Any]] = Field(None, description="Dasha information if needed")
    planner_response: Optional[str] = Field(None, description="Planner's analysis if available")


# Store chart data globally so tools can access it
_chart_data_global: Dict[str, Any] = {}
_dasha_info_global: Dict[str, Any] = {}


@tool
def analyze_chart_section(section_name: str) -> str:
    """
    Analyze a specific section of the astrology chart.
    
    Args:
        section_name: Name of the chart section (e.g., 'planets', 'houses', 'dasha', 'lagna', 'moon', 'transits')
    
    Returns:
        Analysis of the requested section in JSON format
    """
    global _chart_data_global
    
    if not _chart_data_global:
        return "Chart data not available. Please ensure chart data is loaded."
    
    section = _chart_data_global.get(section_name, {})
    if not section:
        available_sections = list(_chart_data_global.keys())
        return f"Section '{section_name}' not found. Available sections: {', '.join(available_sections)}"
    
    # Format the section data for analysis
    if isinstance(section, dict):
        return json.dumps(section, indent=2)
    return str(section)


@tool
def get_all_chart_sections() -> str:
    """
    Get a list of all available chart sections.
    
    Returns:
        List of available chart section names
    """
    global _chart_data_global
    
    if not _chart_data_global:
        return "Chart data not available."
    
    sections = list(_chart_data_global.keys())
    return f"Available chart sections: {', '.join(sections)}"


@tool
def get_dasha_timing() -> str:
    """
    Extract relevant dasha timing information from the chart.
    Use this tool to get current dasha periods and timing information.
    
    Returns:
        Relevant dasha timing information in JSON format
    """
    global _dasha_info_global, _chart_data_global
    
    # First try dasha_info_global (if passed separately)
    if _dasha_info_global:
        current = _dasha_info_global.get('current_dasha_info', {})
        if current:
            return json.dumps(current, indent=2)
        return json.dumps(_dasha_info_global, indent=2)
    
    # Fallback to chart data dasha section
    if _chart_data_global and 'dasha' in _chart_data_global:
        dasha_section = _chart_data_global['dasha']
        return json.dumps(dasha_section, indent=2)
    
    return "No dasha information available in the chart data."


def create_astrology_crew(
    question: str,
    chart_data: Dict[str, Any],
    needed_sections: list[str],
    current_date: str,
    dasha_info: Optional[Dict[str, Any]] = None,
    planner_response: Optional[str] = None
) -> str:
    """
    Create and execute a CrewAI crew to answer astrology questions.
    
    Args:
        question: User's question
        chart_data: Full astrology chart data
        needed_sections: List of chart sections needed
        current_date: Current date
        dasha_info: Optional dasha information
        planner_response: Optional planner analysis
    
    Returns:
        Final answer string
    """
    global _chart_data_global, _dasha_info_global
    
    # Store chart data globally so tools can access it
    _chart_data_global = chart_data
    _dasha_info_global = dasha_info or {}
    
    # Format chart data summary for agent context
    chart_summary = f"""
    Chart Data Available:
    - Available sections: {', '.join(list(chart_data.keys()))}
    - Needed sections: {', '.join(needed_sections) if needed_sections else 'All sections'}
    - Current date: {current_date}
    """
    
    if dasha_info:
        chart_summary += f"\n- Dasha information: Available (use get_dasha_timing tool)"
    
    # Chart Analyst Agent - Analyzes the chart data
    chart_analyst = Agent(
        role='Vedic Astrology Chart Analyst',
        goal='Thoroughly analyze the astrology chart data and extract relevant information for answering the question',
        backstory="""You are an expert in Vedic astrology with deep knowledge of:
        - Planetary positions and their significations
        - House placements and meanings
        - Nakshatras and their characteristics
        - Dasha (planetary periods) systems
        - Yogas and planetary combinations
        - Divisional charts (D1, D9, D10, etc.)
        
        IMPORTANT: The full chart data is available to you through the analyze_chart_section tool.
        You MUST use this tool to examine the chart data. Do NOT ask the user for chart information.
        The chart data has already been calculated and provided to you.
        
        Your task is to carefully examine the chart data using the tools and identify the key astrological factors
        relevant to the user's question.""",
        tools=[analyze_chart_section, get_all_chart_sections],
        verbose=True,
        allow_delegation=False
    )
    
    # Answer Specialist Agent - Crafts the final answer
    answer_specialist = Agent(
        role='Vedic Astrology Answer Specialist',
        goal='Provide accurate, detailed, and helpful answers to astrology questions based on chart analysis',
        backstory="""You are a renowned Vedic astrologer known for:
        - Providing clear, accurate predictions
        - Explaining astrological concepts in understandable terms
        - Combining multiple chart factors for comprehensive answers
        - Being specific about timing when dasha information is available
        - Offering practical remedies when appropriate
        
        You communicate in a warm, professional manner while maintaining astrological accuracy.
        You always base your answers on the actual chart data provided, not general knowledge.""",
        tools=[get_dasha_timing],
        verbose=True,
        allow_delegation=False
    )
    
    # Task 1: Analyze the chart
    analyze_task = Task(
        description=f"""
        Analyze the astrology chart to answer this question: "{question}"
        
        {chart_summary}
        
        {f"Planner's analysis: {planner_response}" if planner_response else ""}
        
        CRITICAL INSTRUCTIONS:
        1. Use the analyze_chart_section tool to examine each relevant chart section
        2. Start by calling get_all_chart_sections to see what's available
        3. For each needed section, use analyze_chart_section('section_name') to get the data
        4. If timing is involved, use get_dasha_timing() to get dasha information
        5. DO NOT ask the user for chart data - it's already provided and accessible via tools
        
        Examine the chart data carefully and identify:
        1. Key planetary positions and their houses (use analyze_chart_section('planets'))
        2. House placements (use analyze_chart_section('houses'))
        3. Dasha information if timing is involved (use get_dasha_timing())
        4. Relevant yogas or combinations (use analyze_chart_section('yogas'))
        5. Transits if available (use analyze_chart_section('transits'))
        6. Any other factors relevant to the question
        
        Provide a detailed analysis of the chart factors relevant to answering the question.
        Base your analysis on the actual chart data you retrieve using the tools.
        """,
        agent=chart_analyst,
        expected_output="A detailed analysis of relevant chart factors based on actual chart data"
    )
    
    # Task 2: Generate the answer
    answer_task = Task(
        description=f"""
        Based on the chart analysis from the previous task, provide a comprehensive answer to: "{question}"
        
        Current Date: {current_date}
        
        Requirements:
        1. Use the chart analysis provided by the Chart Analyst - it contains the actual chart data
        2. Be specific and accurate based on the actual chart data from the analysis
        3. If timing is involved, use the dasha information from the analysis or use get_dasha_timing() tool
        4. Reference specific planetary positions, houses, and dasha periods from the chart
        5. Explain astrological concepts clearly
        6. Provide practical insights and guidance
        7. If remedies are appropriate, suggest them
        
        IMPORTANT: 
        - The chart data has already been analyzed in the previous task
        - You have access to the full chart through tools if you need additional details
        - DO NOT ask the user for chart information - it's already available
        - Base your answer on the actual chart calculations, not general knowledge
        
        The answer should be:
        - Clear and easy to understand
        - Based on actual chart calculations (reference specific planets, houses, dashas)
        - Specific rather than generic (mention actual planetary positions and periods)
        - Helpful and actionable when possible
        - Include timing information if the question asks "when"
        """,
        agent=answer_specialist,
        expected_output="A comprehensive, accurate answer to the user's astrology question based on their actual chart data",
        context=[analyze_task]
    )
    
    # Create and run the crew
    crew = Crew(
        agents=[chart_analyst, answer_specialist],
        tasks=[analyze_task, answer_task],
        process=Process.sequential,
        verbose=True
    )
    
    # Prepare context for the crew
    inputs = {
        'question': question,
        'chart_data': chart_data,
        'needed_sections': needed_sections,
        'current_date': current_date,
        'dasha_info': dasha_info or {},
        'planner_response': planner_response or ""
    }
    
    try:
        result = crew.kickoff(inputs=inputs)
        return str(result)
    except Exception as e:
        logger.error(f"Error in CrewAI execution: {e}", exc_info=True)
        raise


def generate_answer_with_crewai(
    question: str,
    chart_data: Dict[str, Any],
    needed_sections: list[str],
    current_date: str,
    dasha_info: Optional[Dict[str, Any]] = None,
    planner_response: Optional[str] = None
) -> str:
    """
    Main function to generate answers using CrewAI.
    
    This is called from the FastAPI endpoint.
    """
    return create_astrology_crew(
        question=question,
        chart_data=chart_data,
        needed_sections=needed_sections,
        current_date=current_date,
        dasha_info=dasha_info,
        planner_response=planner_response
    )

