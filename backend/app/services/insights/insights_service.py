"""
Insights service for generating and managing user insights.
"""
import logging
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from app.db.supabase import supabase_client
from app.services.llm.factory import llm_factory
from app.services.knowledge.knowledge_service import knowledge_service

logger = logging.getLogger(__name__)

class InsightsService:
    """
    Service for generating and managing user insights.
    """
    _instance = None

    def __new__(cls):
        """Singleton pattern to ensure only one instance of the service exists."""
        if cls._instance is None:
            cls._instance = super(InsightsService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the insights service."""
        logger.info("Insights service initialized")
    
    async def generate_conversation_insights(self, user_id: str, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Generate insights from a conversation.
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
            
        Returns:
            List of generated insights
        """
        # Get conversation messages
        messages = await supabase_client.get_messages(conversation_id)
        
        if not messages:
            return []
        
        # Prepare prompt for insight extraction
        prompt = """Extract key insights about the user from the following conversation.
        Look for:
        - Beliefs: What the user believes about themselves, others, or the world
        - Values: What the user finds important or prioritizes
        - Traits: Personality characteristics or tendencies
        - Patterns: Recurring behaviors or thought processes
        - Goals: What the user is working towards
        - Challenges: What the user is struggling with
        - Preferences: What the user likes or dislikes

        Format each insight as a JSON object with 'type' (belief, value, trait, etc.), 'content' (the insight itself), 
        and 'evidence' (specific text from the conversation that supports this insight).
        Return a list of JSON objects:
        
        Conversation:
        """
        
        for msg in messages:
            prompt += f"\n{msg['role'].capitalize()}: {msg['content']}"
        
        prompt += "\n\nInsights (as JSON list):"
        
        # Get LLM service
        llm_service = llm_factory.get_service()
        
        # Generate insights
        insights_text = await llm_service.generate_text(
            prompt,
            system_message="You are an AI assistant tasked with extracting meaningful insights about users. Be thoughtful, nuanced, and evidence-based in your analysis.",
            temperature=0.3
        )
        
        # Parse insights from JSON
        try:
            # Find JSON in the response
            start_idx = insights_text.find("[")
            end_idx = insights_text.rfind("]") + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = insights_text[start_idx:end_idx]
                insights = json.loads(json_str)
            else:
                logger.error("Failed to extract JSON from insights response")
                return []
            
            # Store insights in database
            stored_insights = []
            for insight in insights:
                insight_data = {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "type": insight.get("type", "unknown"),
                    "content": insight.get("content", ""),
                    "evidence": insight.get("evidence", ""),
                    "created_at": datetime.now().isoformat(),
                    "confidence": 0.8,  # Default confidence
                    "metadata": {}
                }
                
                result = await supabase_client.create_insight(insight_data)
                if result:
                    stored_insights.append(result)
            
            # Process insights in knowledge graph
            await knowledge_service.process_conversation(user_id, conversation_id, messages)
            
            return stored_insights
        except Exception as e:
            logger.error(f"Error parsing insights: {str(e)}")
            return []
    
    async def get_user_insights(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all insights for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of insights
        """
        return await supabase_client.get_insights(user_id)
    
    async def generate_user_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Generate a summary of a user based on their insights.
        
        Args:
            user_id: User ID
            
        Returns:
            User summary
        """
        # Get user insights
        insights = await supabase_client.get_insights(user_id)
        
        if not insights:
            return {
                "summary": "No insights available yet.",
                "categories": {}
            }
        
        # Get knowledge graph data
        graph_data = await knowledge_service.get_user_knowledge_graph(user_id)
        
        # Format insights for the prompt
        insights_text = json.dumps(insights, indent=2)
        
        # Prepare prompt for summary generation
        prompt = f"""Generate a comprehensive summary of the user based on the following insights and knowledge graph data.
        Organize the summary into the following sections:
        1. Overall Summary: A concise paragraph describing the user
        2. Key Traits: Personality characteristics or tendencies
        3. Values & Beliefs: What matters to the user and their worldview
        4. Goals & Aspirations: What the user is working towards
        5. Challenges: What the user is struggling with
        6. Patterns: Recurring behaviors or thought processes

        For each section, cite specific insights as evidence.
        
        User Insights:
        {insights_text}
        
        Format the output as a JSON object with 'summary' (the overall paragraph) and 'categories' (an object with the sections above).
        """
        
        # Get LLM service
        llm_service = llm_factory.get_service()
        
        # Generate summary
        summary_text = await llm_service.generate_text(
            prompt,
            system_message="You are an AI assistant tasked with creating insightful user summaries. Be thoughtful, respectful, and evidence-based in your analysis.",
            temperature=0.3
        )
        
        # Parse summary from JSON
        try:
            # Find JSON in the response
            start_idx = summary_text.find("{")
            end_idx = summary_text.rfind("}") + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = summary_text[start_idx:end_idx]
                summary = json.loads(json_str)
                return summary
            else:
                logger.error("Failed to extract JSON from summary response")
                return {
                    "summary": "Error generating summary.",
                    "categories": {}
                }
        except Exception as e:
            logger.error(f"Error parsing summary: {str(e)}")
            return {
                "summary": "Error generating summary.",
                "categories": {}
            }
    
    async def generate_insight_graph(self, user_id: str) -> Dict[str, Any]:
        """
        Generate a graph visualization of insights.
        
        Args:
            user_id: User ID
            
        Returns:
            Graph data with nodes and links
        """
        # Get user insights
        insights = await supabase_client.get_insights(user_id)
        
        if not insights:
            return {
                "nodes": [],
                "links": []
            }
        
        # Get graph data from the knowledge service
        graph_data = await knowledge_service.get_user_knowledge_graph(user_id)
        
        # Process graph data into visualization format
        nodes = []
        links = []
        node_ids = set()
        
        # Add user node
        user_node = {
            "id": user_id,
            "label": "User",
            "type": "user",
            "size": 20
        }
        nodes.append(user_node)
        node_ids.add(user_id)
        
        # Process all nodes connected to the user
        for insight in insights:
            # Create insight node
            node_id = insight["id"]
            if node_id not in node_ids:
                node_type = insight.get("type", "unknown").lower()
                
                node = {
                    "id": node_id,
                    "label": insight.get("content", "")[:30] + "..." if len(insight.get("content", "")) > 30 else insight.get("content", ""),
                    "type": node_type,
                    "size": 10,
                    "content": insight.get("content", ""),
                    "evidence": insight.get("evidence", "")
                }
                
                nodes.append(node)
                node_ids.add(node_id)
                
                # Create link to user
                link = {
                    "source": user_id,
                    "target": node_id,
                    "label": f"has_{node_type}",
                    "type": node_type
                }
                
                links.append(link)
        
        # Add connections between related nodes
        # This requires some analysis of the content
        llm_service = llm_factory.get_service()
        
        # Analyze connections between insights
        if len(insights) > 1:
            # Prepare prompt for connection analysis
            insights_text = json.dumps(insights, indent=2)
            
            prompt = f"""Analyze the following user insights and identify connections between them.
            For each pair of connected insights, explain the relationship between them.
            Return the connections as a JSON list where each object has 'source' (insight ID), 'target' (insight ID), and 'relationship' (description of how they're related).
            Only include meaningful connections where there is a clear relationship.
            
            User Insights:
            {insights_text}
            
            Connections (as JSON list):"""
            
            # Generate connections
            connections_text = await llm_service.generate_text(
                prompt,
                system_message="You are an AI assistant tasked with finding meaningful connections between insights. Focus on substantial relationships.",
                temperature=0.3
            )
            
            # Parse connections from JSON
            try:
                # Find JSON in the response
                start_idx = connections_text.find("[")
                end_idx = connections_text.rfind("]") + 1
                
                if start_idx != -1 and end_idx != -1:
                    json_str = connections_text[start_idx:end_idx]
                    connections = json.loads(json_str)
                    
                    # Add connections to links
                    for connection in connections:
                        source = connection.get("source")
                        target = connection.get("target")
                        relationship = connection.get("relationship", "related_to")
                        
                        if source and target and source != target:
                            link = {
                                "source": source,
                                "target": target,
                                "label": relationship[:20] + "..." if len(relationship) > 20 else relationship,
                                "type": "connection"
                            }
                            
                            links.append(link)
            except Exception as e:
                logger.error(f"Error parsing connections: {str(e)}")
        
        return {
            "nodes": nodes,
            "links": links
        }

# Create a singleton instance
insights_service = InsightsService()