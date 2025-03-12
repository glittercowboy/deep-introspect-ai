"""
Neo4j client for knowledge graph operations.
"""
import logging
from typing import Dict, List, Optional, Any, Union
from neo4j import GraphDatabase, Driver, AsyncDriver, AsyncSession
from neo4j.exceptions import Neo4jError
from app.core.config import settings

logger = logging.getLogger(__name__)

class Neo4jClient:
    """
    Client for interacting with Neo4j knowledge graph.
    """
    _instance = None

    def __new__(cls):
        """Singleton pattern to ensure only one instance of the client exists."""
        if cls._instance is None:
            cls._instance = super(Neo4jClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the Neo4j client."""
        self.driver: Driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
        )
        logger.info("Neo4j client initialized")
        
        # Ensure the database is properly initialized with constraints
        self._create_constraints()
    
    def _create_constraints(self):
        """Create necessary constraints in the database."""
        with self.driver.session() as session:
            # Create unique constraints for nodes
            constraints = [
                "CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE",
                "CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE",
                "CREATE CONSTRAINT concept_id IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE",
                "CREATE CONSTRAINT event_id IF NOT EXISTS FOR (e:Event) REQUIRE e.id IS UNIQUE",
                "CREATE CONSTRAINT belief_id IF NOT EXISTS FOR (b:Belief) REQUIRE b.id IS UNIQUE",
                "CREATE CONSTRAINT value_id IF NOT EXISTS FOR (v:Value) REQUIRE v.id IS UNIQUE",
                "CREATE CONSTRAINT trait_id IF NOT EXISTS FOR (t:Trait) REQUIRE t.id IS UNIQUE",
                "CREATE CONSTRAINT goal_id IF NOT EXISTS FOR (g:Goal) REQUIRE g.id IS UNIQUE",
                "CREATE CONSTRAINT habit_id IF NOT EXISTS FOR (h:Habit) REQUIRE h.id IS UNIQUE",
                "CREATE CONSTRAINT pattern_id IF NOT EXISTS FOR (p:Pattern) REQUIRE p.id IS UNIQUE",
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Neo4jError as e:
                    logger.error(f"Error creating constraint: {str(e)}")
    
    def close(self):
        """Close the Neo4j driver."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j client closed")
    
    async def create_user_node(self, user_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Create a user node in the knowledge graph.
        
        Args:
            user_id: The user ID
            metadata: User metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MERGE (u:User {id: $user_id})
                    SET u += $metadata
                    RETURN u
                    """,
                    user_id=user_id,
                    metadata=metadata
                )
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating user node: {str(e)}")
            return False
    
    async def create_entity_node(
        self, 
        entity_id: str, 
        entity_type: str, 
        name: str, 
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Create an entity node in the knowledge graph.
        
        Args:
            entity_id: Unique entity ID
            entity_type: Type of entity (Person, Location, Organization, etc.)
            name: Entity name
            metadata: Entity metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    f"""
                    MERGE (e:Entity:{entity_type} {{id: $entity_id}})
                    SET e.name = $name
                    SET e += $metadata
                    RETURN e
                    """,
                    entity_id=entity_id,
                    name=name,
                    metadata=metadata
                )
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating entity node: {str(e)}")
            return False
    
    async def create_concept_node(
        self, 
        concept_id: str, 
        name: str, 
        description: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Create a concept node in the knowledge graph.
        
        Args:
            concept_id: Unique concept ID
            name: Concept name
            description: Concept description
            metadata: Concept metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MERGE (c:Concept {id: $concept_id})
                    SET c.name = $name
                    SET c.description = $description
                    SET c += $metadata
                    RETURN c
                    """,
                    concept_id=concept_id,
                    name=name,
                    description=description,
                    metadata=metadata
                )
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating concept node: {str(e)}")
            return False
    
    async def create_relationship(
        self,
        from_id: str,
        from_type: str,
        to_id: str,
        to_type: str,
        relationship_type: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Create a relationship between two nodes in the knowledge graph.
        
        Args:
            from_id: ID of the source node
            from_type: Type of the source node
            to_id: ID of the target node
            to_type: Type of the target node
            relationship_type: Type of relationship
            metadata: Relationship metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    f"""
                    MATCH (a:{from_type} {{id: $from_id}})
                    MATCH (b:{to_type} {{id: $to_id}})
                    MERGE (a)-[r:{relationship_type}]->(b)
                    SET r += $metadata
                    RETURN r
                    """,
                    from_id=from_id,
                    to_id=to_id,
                    metadata=metadata
                )
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating relationship: {str(e)}")
            return False
    
    async def get_user_graph(self, user_id: str, depth: int = 2) -> Dict[str, Any]:
        """
        Get a subgraph centered on a user.
        
        Args:
            user_id: The user ID
            depth: Depth of relationships to traverse
            
        Returns:
            Dictionary with nodes and relationships
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH path = (u:User {id: $user_id})-[*1..$depth]-(related)
                    WITH collect(path) AS paths
                    CALL apoc.convert.toTree(paths) YIELD value
                    RETURN value
                    """,
                    user_id=user_id,
                    depth=depth
                )
                record = result.single()
                if record:
                    return record["value"]
                return {"nodes": [], "relationships": []}
        except Exception as e:
            logger.error(f"Error getting user graph: {str(e)}")
            return {"nodes": [], "relationships": []}
    
    async def get_entity_connections(self, entity_id: str, entity_type: str) -> List[Dict[str, Any]]:
        """
        Get all connections for an entity.
        
        Args:
            entity_id: The entity ID
            entity_type: Type of the entity
            
        Returns:
            List of connected entities with relationship information
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    f"""
                    MATCH (e:{entity_type} {{id: $entity_id}})-[r]-(connected)
                    RETURN type(r) as relationship_type, connected, r
                    """,
                    entity_id=entity_id
                )
                
                connections = []
                for record in result:
                    connected_node = record["connected"]
                    relationship = record["r"]
                    
                    connections.append({
                        "node": dict(connected_node),
                        "relationship_type": record["relationship_type"],
                        "relationship_properties": dict(relationship)
                    })
                
                return connections
        except Exception as e:
            logger.error(f"Error getting entity connections: {str(e)}")
            return []
    
    async def search_knowledge_graph(self, query: str) -> List[Dict[str, Any]]:
        """
        Search the knowledge graph using a text query.
        
        Args:
            query: Search query
            
        Returns:
            List of matching nodes
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    CALL db.index.fulltext.queryNodes("node_index", $query) YIELD node, score
                    RETURN node, score
                    ORDER BY score DESC
                    LIMIT 10
                    """,
                    query=query
                )
                
                nodes = []
                for record in result:
                    node = record["node"]
                    score = record["score"]
                    
                    nodes.append({
                        "node": dict(node),
                        "score": score
                    })
                
                return nodes
        except Exception as e:
            logger.error(f"Error searching knowledge graph: {str(e)}")
            return []
    
    async def find_patterns(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Find patterns in user data.
        
        Args:
            user_id: The user ID
            
        Returns:
            List of detected patterns
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (u:User {id: $user_id})-[:HAS_PATTERN]->(p:Pattern)
                    RETURN p
                    ORDER BY p.confidence DESC
                    """,
                    user_id=user_id
                )
                
                patterns = []
                for record in result:
                    pattern = record["p"]
                    patterns.append(dict(pattern))
                
                return patterns
        except Exception as e:
            logger.error(f"Error finding patterns: {str(e)}")
            return []

# Create a singleton instance
neo4j_client = Neo4jClient()