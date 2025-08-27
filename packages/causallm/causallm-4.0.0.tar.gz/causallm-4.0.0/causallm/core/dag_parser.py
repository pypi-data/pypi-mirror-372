from typing import Dict, List, Optional
import networkx as nx
import matplotlib.pyplot as plt
from ..utils.logging import get_logger, get_structured_logger

class DAGParser:
    def __init__(self, edges: List[tuple]) -> None:
        self.logger = get_logger("causalllm.dag_parser")
        self.struct_logger = get_structured_logger("dag_parser")
        
        self.logger.info("Initializing DAGParser")
        self.logger.debug(f"Creating DAG with {len(edges)} edges: {edges}")
        
        try:
            self.graph = nx.DiGraph()
            self.graph.add_edges_from(edges)
            
            # Validate DAG
            if not nx.is_directed_acyclic_graph(self.graph):
                self.logger.error("Graph contains cycles - not a valid DAG")
                raise ValueError("Graph contains cycles - not a valid DAG")
            
            self.struct_logger.log_interaction(
                "dag_initialization",
                {
                    "edges_count": len(edges),
                    "nodes_count": self.graph.number_of_nodes(),
                    "edges": edges,
                    "is_valid_dag": True
                }
            )
            
            self.logger.info(f"DAG initialized successfully with {self.graph.number_of_nodes()} nodes and {len(edges)} edges")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize DAG: {e}")
            self.struct_logger.log_error(e, {"edges": edges})
            raise

    def get_ancestors(self, node: str) -> List[str]:
        self.logger.debug(f"Getting ancestors for node: {node}")
        
        try:
            ancestors = list(nx.ancestors(self.graph, node))
            
            self.logger.debug(f"Found {len(ancestors)} ancestors for {node}: {ancestors}")
            self.struct_logger.log_interaction(
                "get_ancestors",
                {
                    "node": node,
                    "ancestors": ancestors,
                    "ancestors_count": len(ancestors)
                }
            )
            
            return ancestors
            
        except Exception as e:
            self.logger.error(f"Error getting ancestors for node {node}: {e}")
            self.struct_logger.log_error(e, {"node": node})
            raise

    def get_descendants(self, node: str) -> List[str]:
        self.logger.debug(f"Getting descendants for node: {node}")
        
        try:
            descendants = list(nx.descendants(self.graph, node))
            
            self.logger.debug(f"Found {len(descendants)} descendants for {node}: {descendants}")
            self.struct_logger.log_interaction(
                "get_descendants",
                {
                    "node": node,
                    "descendants": descendants,
                    "descendants_count": len(descendants)
                }
            )
            
            return descendants
            
        except Exception as e:
            self.logger.error(f"Error getting descendants for node {node}: {e}")
            self.struct_logger.log_error(e, {"node": node})
            raise

    def to_prompt(self, task: str) -> str:
        self.logger.info(f"Converting DAG to prompt for task: {task}")
        
        try:
            edges = list(self.graph.edges())
            prompt = f"Task: {task}\nGraph structure: {edges}"
            
            self.logger.debug(f"Generated prompt with length: {len(prompt)}")
            self.struct_logger.log_interaction(
                "to_prompt",
                {
                    "task": task,
                    "edges_count": len(edges),
                    "prompt_length": len(prompt),
                    "graph_edges": edges
                }
            )
            
            return prompt
            
        except Exception as e:
            self.logger.error(f"Error converting DAG to prompt: {e}")
            self.struct_logger.log_error(e, {"task": task})
            raise

    def visualize(self, path: str = "dag.png") -> None:
        self.logger.info(f"Visualizing DAG to path: {path}")
        
        try:
            pos = nx.spring_layout(self.graph)
            nx.draw(
                self.graph,
                pos,
                with_labels=True,
                node_color="skyblue",
                node_size=2000,
                font_size=10,
                font_weight="bold",
                arrows=True,
            )
            plt.savefig(path)
            plt.close()
            
            self.struct_logger.log_interaction(
                "visualize",
                {
                    "output_path": path,
                    "nodes_count": self.graph.number_of_nodes(),
                    "edges_count": self.graph.number_of_edges()
                }
            )
            
            self.logger.info(f"DAG visualization saved to: {path}")
            
        except Exception as e:
            self.logger.error(f"Error visualizing DAG: {e}")
            self.struct_logger.log_error(e, {"output_path": path})
            raise
