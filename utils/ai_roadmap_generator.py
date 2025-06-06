import os
import json
import logging
import re
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from groq import Groq

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = None
AI_GENERATION_SUPPORTED = True
try:
    if GROQ_API_KEY:
        client = Groq(api_key=GROQ_API_KEY)
    else:
        logger.warning("Groq API key not found. AI generation will be disabled.")
        AI_GENERATION_SUPPORTED = False
except Exception as e:
    logger.error(f"Error initializing Groq client: {str(e)}")
    AI_GENERATION_SUPPORTED = False

def clean_content(content: str) -> str:
    content = content.replace("```json", "").replace("```", "")
    
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    
    return content.strip()

def generate_roadmap(query: str) -> Optional[Dict[str, Any]]:

    if not AI_GENERATION_SUPPORTED or not client:
        logger.warning("AI generation is not supported, returning None")
        return None
        
    try:
        logger.info(f"Generating roadmap for query: {query}")
        
        system_message = """
        You are an expert in creating educational roadmaps for various fields.
        Generate a comprehensive learning roadmap in JSON format based on the user's query.
        
        The roadmap should follow this structure:
        {
            "name": "Title of the roadmap",
            "description": "Description of what this roadmap covers",
            "steps": [
                {
                    "id": "1-1",
                    "title": "Step title",
                    "description": "Detailed description of this step",
                    "icon": "Icon name",
                    "iconColor": "text-blue-600",
                    "iconBg": "bg-blue-100",
                    "timeToComplete": "Estimated time (e.g., 2-4 weeks)",
                    "difficulty": 1,
                    "resources": [
                        {
                            "title": "Resource title",
                            "url": "URL to the resource",
                            "source": "Source name",
                            "description": "Brief description of the resource"
                        }
                    ],
                    "tips": "Helpful tips for completing this step"
                }
            ]
        }
        
        Include 6 steps per section, with each step having 2-3 resources.
        For icons, select from Lucid React icon list
        Make sure all JSON is properly formatted and valid.
        Only return the JSON object, with no additional text, comments, or markdown formatting.
        Do not include any thinking process or explanations in the response.
        """
        
        # Generate roadmap using Groq Chat API
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": query}
            ],
            model="deepseek-r1-distill-llama-70b",
            temperature=0.7,
            max_tokens=3000
        )
        
        # Extract and clean the generated content
        content = chat_completion.choices[0].message.content
        content = clean_content(content)
        
        print(content)

        # Parse the JSON response
        roadmap_data = json.loads(content)
        
        logger.info(f"Successfully generated roadmap with {len(roadmap_data.get('steps', []))} steps")
        return roadmap_data
    
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error generating roadmap: {str(e)}", exc_info=True)
        return None 