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


@tool
def analyze_chart_section(section_name: str, chart_data: Dict[str, Any]) -> str:
    """
    Analyze a specific section of the astrology chart.
    
    Args:
        section_name: Name of the chart section (e.g., 'planets', 'houses', 'dasha')
        chart_data: Full chart JSON data
    
    Returns:
        Analysis of the requested section
    """
    section = chart_data.get(section_name, {})
    if not section:
        return f"Section '{section_name}' not found in chart data."
    
    # Format the section data for analysis
    if isinstance(section, dict):
        return json.dumps(section, indent=2)
    return str(section)


@tool
def get_dasha_timing(dasha_info: Dict[str, Any], question: str) -> str:
    """
    Extract relevant dasha timing information based on the question.
    
    Args:
        dasha_info: Dasha information dictionary
        question: User's question to determine what timing info is needed
    
    Returns:
        Relevant dasha timing information
    """
    if not dasha_info:
        return "No dasha information available."
    
    # Extract current dasha if available
    current = dasha_info.get('current_dasha_info', {})
    if current:
        return json.dumps(current, indent=2)
    
    return json.dumps(dasha_info, indent=2)


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
        
        Your task is to carefully examine the chart data and identify the key astrological factors
        relevant to the user's question.""",
        tools=[analyze_chart_section],
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
        
        Current Date: {current_date}
        
        Chart sections to focus on: {', '.join(needed_sections) if needed_sections else 'All relevant sections'}
        
        {f"Planner's analysis: {planner_response}" if planner_response else ""}
        
        Examine the chart data carefully and identify:
        1. Key planetary positions and their houses
        2. Relevant yogas or combinations
        3. Dasha information if timing is involved
        4. Any other factors relevant to the question
        
        Provide a detailed analysis of the chart factors relevant to answering the question.
        """,
        agent=chart_analyst,
        expected_output="A detailed analysis of relevant chart factors"
    )
    
    # Task 2: Generate the answer
    answer_task = Task(
        description=f"""
        Based on the chart analysis, provide a comprehensive answer to: "{question}"
        
        Requirements:
        1. Be specific and accurate based on the actual chart data
        2. If timing is involved, use the dasha information provided
        3. Explain astrological concepts clearly
        4. Provide practical insights and guidance
        5. If remedies are appropriate, suggest them
        
        The answer should be:
        - Clear and easy to understand
        - Based on actual chart calculations
        - Specific rather than generic
        - Helpful and actionable when possible
        """,
        agent=answer_specialist,
        expected_output="A comprehensive, accurate answer to the user's astrology question",
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

