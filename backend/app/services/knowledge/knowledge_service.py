"""
Knowledge graph service for extracting and storing user insights.
"""
import logging
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from app.db.neo4j import neo4j_client
from app.services.llm.factory import llm_factory

logger = logging.getLogger(__name__)

class KnowledgeService:
    """
    Service for managing the knowledge graph.
    """
    _instance = None

    def __new__(cls):
        """Singleton pattern to ensure only one instance of the service exists."""
        if cls._instance is None:
            cls._instance = super(KnowledgeService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the knowledge service."""
        logger.info("Knowledge service initialized")
    
    async def process_conversation(self, user_id: str, conversation_id: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a conversation to extract knowledge and insights.
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
            messages: List of conversation messages
            
        Returns:
            Dictionary with extraction results
        """
        # Ensure user node exists
        await neo4j_client.create_user_node(user_id, {"last_activity": datetime.now().isoformat()})
        
        # Extract entities from conversation
        entities = await self._extract_entities(messages)
        
        # Extract concepts from conversation
        concepts = await self._extract_concepts(messages)
        
        # Extract beliefs and values
        beliefs_values = await self._extract_beliefs_values(messages)
        
        # Extract patterns
        patterns = await self._extract_patterns(user_id, messages)
        
        # Create nodes and relationships
        created_nodes = await self._create_knowledge_nodes(user_id, entities, concepts, beliefs_values, patterns)
        
        return {
            "entities": entities,
            "concepts": concepts,
            "beliefs_values": beliefs_values,
            "patterns": patterns,
            "created_nodes": created_nodes
        }
    
    async def _extract_entities(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract entities from conversation messages.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            List of extracted entities
        """
        # Combine messages into a single text
        conversation_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages])
        
        # Prepare prompt for entity extraction
        prompt = """Extract named entities from the following conversation. 
        Include people, places, organizations, products, and other specific entities mentioned.
        For each entity, provide the entity type, name, and any additional information mentioned.
        Format the output as a JSON list where each object has 'type', 'name', and 'info' fields.
        
        Conversation:
        """
        prompt += conversation_text
        prompt += "\n\nEntities (as JSON):"
        
        # Get LLM service
        llm_service = llm_factory.get_service()
        
        # Generate entities
        entities_text = await llm_service.generate_text(
            prompt,
            system_message="You are an AI assistant tasked with extracting named entities from text. Be precise and only extract clearly defined entities.",
            temperature=0.2
        )
        
        # Parse entities from JSON
        try:
            # Find JSON in the response
            start_idx = entities_text.find("[")
            end_idx = entities_text.rfind("]") + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = entities_text[start_idx:end_idx]
                entities = json.loads(json_str)
            else:
                logger.error("Failed to extract JSON from entities response")
                return []
            
            # Add unique IDs to entities
            for entity in entities:
                entity["id"] = str(uuid.uuid4())
            
            return entities
        except Exception as e:
            logger.error(f"Error parsing entities: {str(e)}")
            return []
    
    async def _extract_concepts(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract concepts from conversation messages.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            List of extracted concepts
        """
        # Combine messages into a single text
        conversation_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages])
        
        # Prepare prompt for concept extraction
        prompt = """Extract abstract concepts discussed in the following conversation.
        Focus on ideas, themes, and topics rather than specific entities.
        For each concept, provide the name and a brief description based on the conversation.
        Format the output as a JSON list where each object has 'name' and 'description' fields.
        
        Conversation:
        """
        prompt += conversation_text
        prompt += "\n\nConcepts (as JSON):"
        
        # Get LLM service
        llm_service = llm_factory.get_service()
        
        # Generate concepts
        concepts_text = await llm_service.generate_text(
            prompt,
            system_message="You are an AI assistant tasked with extracting abstract concepts from text. Focus on meaningful ideas and themes.",
            temperature=0.3
        )
        
        # Parse concepts from JSON
        try:
            # Find JSON in the response
            start_idx = concepts_text.find("[")
            end_idx = concepts_text.rfind("]") + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = concepts_text[start_idx:end_idx]
                concepts = json.loads(json_str)
            else:
                logger.error("Failed to extract JSON from concepts response")
                return []
            
            # Add unique IDs to concepts
            for concept in concepts:
                concept["id"] = str(uuid.uuid4())
            
            return concepts
        except Exception as e:
            logger.error(f"Error parsing concepts: {str(e)}")
            return []
    
    async def _extract_beliefs_values(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract beliefs and values from conversation messages.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            List of extracted beliefs and values
        """
        # Combine messages into a single text
        conversation_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages])
        
        # Prepare prompt for belief/value extraction
        prompt = """Extract beliefs and values expressed by the user in the following conversation.
        Beliefs are statements about what the user thinks is true about the world.
        Values are principles or qualities that the user considers important or worthwhile.
        For each belief or value, provide the type ('belief' or 'value'), the content, and evidence from the conversation.
        Format the output as a JSON list where each object has 'type', 'content', and 'evidence' fields.
        
        Conversation:
        """
        prompt += conversation_text
        prompt += "\n\nBeliefs and Values (as JSON):"
        
        # Get LLM service
        llm_service = llm_factory.get_service()
        
        # Generate beliefs/values
        beliefs_text = await llm_service.generate_text(
            prompt,
            system_message="You are an AI assistant tasked with extracting beliefs and values from text. Be evidence-based and avoid over-interpretation.",
            temperature=0.3
        )
        
        # Parse beliefs/values from JSON
        try:
            # Find JSON in the response
            start_idx = beliefs_text.find("[")
            end_idx = beliefs_text.rfind("]") + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = beliefs_text[start_idx:end_idx]
                beliefs_values = json.loads(json_str)
            else:
                logger.error("Failed to extract JSON from beliefs/values response")
                return []
            
            # Add unique IDs
            for item in beliefs_values:
                item["id"] = str(uuid.uuid4())
            
            return beliefs_values
        except Exception as e:
            logger.error(f"Error parsing beliefs/values: {str(e)}")
            return []
    
    async def _extract_patterns(self, user_id: str, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract patterns from conversation messages and user history.
        
        Args:
            user_id: User ID
            messages: List of conversation messages
            
        Returns:
            List of extracted patterns
        """
        # Combine messages into a single text
        conversation_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages])
        
        # Get existing patterns for the user
        existing_patterns = await neo4j_client.find_patterns(user_id)
        existing_patterns_text = json.dumps(existing_patterns) if existing_patterns else "[]"
        
        # Prepare prompt for pattern extraction
        prompt = f"""Identify behavioral or thinking patterns based on the conversation and existing known patterns.
        Consider how the user approaches problems, recurring themes, or habits that emerge from their statements.
        
        Existing patterns for this user:
        {existing_patterns_text}
        
        Conversation:
        {conversation_text}
        
        For each pattern, provide a name, description, evidence from the conversation, and confidence level (0.0-1.0).
        Format the output as a JSON list where each object has 'name', 'description', 'evidence', and 'confidence' fields.
        Include both new patterns and updates to existing patterns if supported by this conversation.
        
        Patterns (as JSON):"""
        
        # Get LLM service
        llm_service = llm_factory.get_service()
        
        # Generate patterns
        patterns_text = await llm_service.generate_text(
            prompt,
            system_message="You are an AI assistant tasked with identifying behavioral and thinking patterns. Be evidence-based and assign appropriate confidence levels.",
            temperature=0.3
        )
        
        # Parse patterns from JSON
        try:
            # Find JSON in the response
            start_idx = patterns_text.find("[")
            end_idx = patterns_text.rfind("]") + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = patterns_text[start_idx:end_idx]
                patterns = json.loads(json_str)
            else:
                logger.error("Failed to extract JSON from patterns response")
                return []
            
            # Add unique IDs
            for pattern in patterns:
                pattern["id"] = str(uuid.uuid4())
            
            return patterns
        except Exception as e:
            logger.error(f"Error parsing patterns: {str(e)}")
            return []
    
    async def _create_knowledge_nodes(
        self, 
        user_id: str, 
        entities: List[Dict[str, Any]], 
        concepts: List[Dict[str, Any]],
        beliefs_values: List[Dict[str, Any]],
        patterns: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Create knowledge graph nodes and relationships.
        
        Args:
            user_id: User ID
            entities: List of entities
            concepts: List of concepts
            beliefs_values: List of beliefs and values
            patterns: List of patterns
            
        Returns:
            Dictionary with counts of created nodes and relationships
        """
        entity_count = 0
        concept_count = 0
        belief_value_count = 0
        pattern_count = 0
        relationship_count = 0
        
        # Create entity nodes
        for entity in entities:
            success = await neo4j_client.create_entity_node(
                entity_id=entity["id"],
                entity_type=entity.get("type", "Unknown"),
                name=entity.get("name", ""),
                metadata={"info": entity.get("info", "")}
            )
            
            if success:
                entity_count += 1
                
                # Create relationship to user
                rel_success = await neo4j_client.create_relationship(
                    from_id=user_id,
                    from_type="User",
                    to_id=entity["id"],
                    to_type="Entity",
                    relationship_type="KNOWS_ABOUT",
                    metadata={"created_at": datetime.now().isoformat()}
                )
                
                if rel_success:
                    relationship_count += 1
        
        # Create concept nodes
        for concept in concepts:
            success = await neo4j_client.create_concept_node(
                concept_id=concept["id"],
                name=concept.get("name", ""),
                description=concept.get("description", ""),
                metadata={}
            )
            
            if success:
                concept_count += 1
                
                # Create relationship to user
                rel_success = await neo4j_client.create_relationship(
                    from_id=user_id,
                    from_type="User",
                    to_id=concept["id"],
                    to_type="Concept",
                    relationship_type="HAS_KNOWLEDGE_OF",
                    metadata={"created_at": datetime.now().isoformat()}
                )
                
                if rel_success:
                    relationship_count += 1
        
        # Create belief/value nodes
        for item in beliefs_values:
            node_type = item.get("type", "Belief").capitalize()
            
            if node_type not in ["Belief", "Value"]:
                node_type = "Belief"  # Default fallback
            
            # Create node with appropriate type
            with neo4j_client.driver.session() as session:
                result = session.run(
                    f"""
                    MERGE (n:{node_type} {{id: $id}})
                    SET n.content = $content
                    SET n.evidence = $evidence
                    SET n.created_at = $created_at
                    RETURN n
                    """,
                    id=item["id"],
                    content=item.get("content", ""),
                    evidence=item.get("evidence", ""),
                    created_at=datetime.now().isoformat()
                )
                
                if result.single():
                    belief_value_count += 1
                    
                    # Create relationship to user
                    rel_type = "HAS_BELIEF" if node_type == "Belief" else "HAS_VALUE"
                    rel_success = await neo4j_client.create_relationship(
                        from_id=user_id,
                        from_type="User",
                        to_id=item["id"],
                        to_type=node_type,
                        relationship_type=rel_type,
                        metadata={"created_at": datetime.now().isoformat()}
                    )
                    
                    if rel_success:
                        relationship_count += 1
        
        # Create pattern nodes
        for pattern in patterns:
            # Create pattern node
            with neo4j_client.driver.session() as session:
                result = session.run(
                    """
                    MERGE (p:Pattern {id: $id})
                    SET p.name = $name
                    SET p.description = $description
                    SET p.evidence = $evidence
                    SET p.confidence = $confidence
                    SET p.created_at = $created_at
                    RETURN p
                    """,
                    id=pattern["id"],
                    name=pattern.get("name", ""),
                    description=pattern.get("description", ""),
                    evidence=pattern.get("evidence", ""),
                    confidence=pattern.get("confidence", 0.5),
                    created_at=datetime.now().isoformat()
                )
                
                if result.single():
                    pattern_count += 1
                    
                    # Create relationship to user
                    rel_success = await neo4j_client.create_relationship(
                        from_id=user_id,
                        from_type="User",
                        to_id=pattern["id"],
                        to_type="Pattern",
                        relationship_type="HAS_PATTERN",
                        metadata={"created_at": datetime.now().isoformat()}
                    )
                    
                    if rel_success:
                        relationship_count += 1
        
        return {
            "entities": entity_count,
            "concepts": concept_count,
            "beliefs_values": belief_value_count,
            "patterns": pattern_count,
            "relationships": relationship_count
        }
    
    async def get_user_knowledge_graph(self, user_id: str, depth: int = 2) -> Dict[str, Any]:
        """
        Get a user's knowledge graph.
        
        Args:
            user_id: User ID
            depth: Relationship depth
            
        Returns:
            Graph data with nodes and relationships
        """
        return await neo4j_client.get_user_graph(user_id, depth)
    
    async def search_knowledge(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """
        Search the knowledge graph.
        
        Args:
            user_id: User ID
            query: Search query
            
        Returns:
            List of matching nodes
        """
        # Get nodes connected to the user that match the query
        with neo4j_client.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {id: $user_id})-[r]-(n)
                WHERE n.name =~ $query OR n.content =~ $query OR n.description =~ $query
                RETURN n, type(r) as relationship
                """,
                user_id=user_id,
                query=f"(?i).*{query}.*"
            )
            
            nodes = []
            for record in result:
                node = record["n"]
                relationship = record["relationship"]
                
                nodes.append({
                    "node": dict(node),
                    "relationship": relationship
                })
            
            return nodes

# Create a singleton instance
knowledge_service = KnowledgeService()