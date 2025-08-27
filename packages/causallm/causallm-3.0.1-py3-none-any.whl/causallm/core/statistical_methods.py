"""
Statistical Methods for Causal Inference
Core statistical algorithms for causal discovery and validation
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Optional, Set
from itertools import combinations
from scipy.stats import chi2_contingency, pearsonr
from sklearn.feature_selection import mutual_info_regression
import networkx as nx
from ..utils.logging import get_logger

logger = get_logger(__name__)

class ConditionalIndependenceTest:
    """Conditional independence testing for causal discovery"""
    
    def __init__(self, method: str = "partial_correlation", alpha: float = 0.05):
        self.method = method
        self.alpha = alpha
        
    def test(self, X: np.ndarray, Y: np.ndarray, Z: Optional[np.ndarray] = None) -> Tuple[bool, float]:
        """
        Test conditional independence: X ⊥ Y | Z
        
        Returns:
            (is_independent, p_value)
        """
        if self.method == "partial_correlation":
            return self._partial_correlation_test(X, Y, Z)
        elif self.method == "mutual_information":
            return self._mutual_info_test(X, Y, Z)
        elif self.method == "chi_square":
            return self._chi_square_test(X, Y, Z)
        else:
            raise ValueError(f"Unknown method: {self.method}")
    
    def _partial_correlation_test(self, X: np.ndarray, Y: np.ndarray, Z: Optional[np.ndarray] = None) -> Tuple[bool, float]:
        """Partial correlation test"""
        if Z is None or Z.shape[1] == 0:
            # Simple correlation
            corr, p_value = pearsonr(X.flatten(), Y.flatten())
            return p_value > self.alpha, p_value
        
        # Partial correlation using linear regression residuals
        from sklearn.linear_model import LinearRegression
        
        # Regress X on Z and Y on Z
        reg_x = LinearRegression().fit(Z, X)
        reg_y = LinearRegression().fit(Z, Y)
        
        # Get residuals
        res_x = X - reg_x.predict(Z)
        res_y = Y - reg_y.predict(Z)
        
        # Correlation of residuals
        corr, p_value = pearsonr(res_x.flatten(), res_y.flatten())
        return p_value > self.alpha, p_value
    
    def _mutual_info_test(self, X: np.ndarray, Y: np.ndarray, Z: Optional[np.ndarray] = None) -> Tuple[bool, float]:
        """Mutual information test (simplified)"""
        if Z is None or Z.shape[1] == 0:
            mi = mutual_info_regression(X.reshape(-1, 1), Y.flatten())[0]
        else:
            # Conditional mutual information (approximated)
            mi = mutual_info_regression(np.hstack([X, Z]), Y.flatten())[0]
            mi_z = mutual_info_regression(Z, Y.flatten())[0]
            mi = max(0, mi - mi_z)
        
        # Convert MI to pseudo p-value (heuristic)
        p_value = np.exp(-mi)
        return p_value > self.alpha, p_value
    
    def _chi_square_test(self, X: np.ndarray, Y: np.ndarray, Z: Optional[np.ndarray] = None) -> Tuple[bool, float]:
        """Chi-square test for categorical variables"""
        # Discretize continuous variables if needed
        X_cat = self._discretize(X)
        Y_cat = self._discretize(Y)
        
        if Z is None or Z.shape[1] == 0:
            contingency = pd.crosstab(X_cat.flatten(), Y_cat.flatten())
            chi2_stat, p_value, _, _ = chi2_contingency(contingency)
            return p_value > self.alpha, p_value
        else:
            # Conditional independence via stratification
            Z_cat = self._discretize(Z)
            p_values = []
            
            for z_val in np.unique(Z_cat):
                mask = Z_cat.flatten() == z_val
                if np.sum(mask) < 10:  # Skip small strata
                    continue
                    
                X_stratum = X_cat[mask]
                Y_stratum = Y_cat[mask]
                
                if len(np.unique(X_stratum)) > 1 and len(np.unique(Y_stratum)) > 1:
                    contingency = pd.crosstab(X_stratum.flatten(), Y_stratum.flatten())
                    chi2_stat, p_val, _, _ = chi2_contingency(contingency)
                    p_values.append(p_val)
            
            if not p_values:
                return True, 1.0
                
            # Combined p-value (Fisher's method)
            combined_stat = -2 * np.sum(np.log(p_values))
            from scipy.stats import chi2
            p_value = 1 - chi2.cdf(combined_stat, 2 * len(p_values))
            return p_value > self.alpha, p_value
    
    def _discretize(self, X: np.ndarray, bins: int = 3) -> np.ndarray:
        """Discretize continuous variables"""
        if X.dtype in [np.int32, np.int64, np.bool_]:
            return X
        
        # Use quantile-based binning
        quantiles = np.linspace(0, 1, bins + 1)
        thresholds = np.quantile(X, quantiles)
        return np.digitize(X, thresholds[1:-1])

class PCAlgorithm:
    """PC Algorithm for Causal Discovery"""
    
    def __init__(self, ci_test: ConditionalIndependenceTest = None, max_conditioning_size: int = 3):
        self.ci_test = ci_test or ConditionalIndependenceTest()
        self.max_conditioning_size = max_conditioning_size
        
    def discover_skeleton(self, data: pd.DataFrame) -> nx.Graph:
        """
        Discover the skeleton of the causal graph using PC algorithm
        
        Returns:
            Undirected graph representing causal skeleton
        """
        logger.info(f"Starting PC algorithm skeleton discovery with {len(data.columns)} variables")
        
        variables = list(data.columns)
        n_vars = len(variables)
        
        # Initialize complete graph
        G = nx.complete_graph(variables)
        
        # Store separation sets
        sep_sets = {}
        
        # PC algorithm phases
        for conditioning_size in range(self.max_conditioning_size + 1):
            edges_to_remove = []
            
            for u, v in list(G.edges()):
                neighbors_u = set(G.neighbors(u)) - {v}
                neighbors_v = set(G.neighbors(v)) - {u}
                
                # Find conditioning sets of appropriate size
                all_neighbors = neighbors_u | neighbors_v
                
                if len(all_neighbors) >= conditioning_size:
                    for cond_set in combinations(all_neighbors, conditioning_size):
                        # Test conditional independence
                        X = data[u].values.reshape(-1, 1)
                        Y = data[v].values.reshape(-1, 1)
                        Z = data[list(cond_set)].values if cond_set else None
                        
                        is_independent, p_value = self.ci_test.test(X, Y, Z)
                        
                        if is_independent:
                            logger.debug(f"Found independence: {u} ⊥ {v} | {cond_set} (p={p_value:.4f})")
                            edges_to_remove.append((u, v))
                            sep_sets[(u, v)] = set(cond_set)
                            break
            
            # Remove edges
            for u, v in edges_to_remove:
                if G.has_edge(u, v):
                    G.remove_edge(u, v)
        
        logger.info(f"PC skeleton discovery complete. Found {G.number_of_edges()} edges")
        return G
    
    def orient_edges(self, skeleton: nx.Graph, data: pd.DataFrame) -> nx.DiGraph:
        """Orient edges in the skeleton to create CPDAG"""
        dag = skeleton.to_directed()
        
        # Rule R0: Orient v-structures (colliders)
        self._orient_v_structures(dag)
        
        # Rules R1-R3: Orient remaining edges to avoid cycles and new v-structures
        changed = True
        while changed:
            changed = False
            changed |= self._apply_rule_r1(dag)
            changed |= self._apply_rule_r2(dag)
            changed |= self._apply_rule_r3(dag)
        
        return dag
    
    def _orient_v_structures(self, dag: nx.DiGraph):
        """Orient v-structures (X -> Z <- Y where X and Y are not adjacent)"""
        nodes = list(dag.nodes())
        
        for i, x in enumerate(nodes):
            for j, y in enumerate(nodes[i+1:], i+1):
                if dag.has_edge(x, y) or dag.has_edge(y, x):
                    continue  # Skip if adjacent
                
                # Find common neighbors
                common_neighbors = set(dag.neighbors(x)) & set(dag.neighbors(y))
                
                for z in common_neighbors:
                    # Check if this forms a v-structure
                    if (dag.has_edge(x, z) and dag.has_edge(z, x) and 
                        dag.has_edge(y, z) and dag.has_edge(z, y)):
                        
                        # Orient as X -> Z <- Y
                        dag.remove_edge(z, x)
                        dag.remove_edge(z, y)
                        logger.debug(f"Oriented v-structure: {x} -> {z} <- {y}")
    
    def _apply_rule_r1(self, dag: nx.DiGraph) -> bool:
        """Rule R1: If X -> Y - Z and X, Z not adjacent, then Y -> Z"""
        changed = False
        for y in dag.nodes():
            predecessors = set(dag.predecessors(y)) - set(dag.successors(y))
            bidirectional = set(dag.predecessors(y)) & set(dag.successors(y))
            
            for x in predecessors:
                for z in bidirectional:
                    if not (dag.has_edge(x, z) or dag.has_edge(z, x)):
                        dag.remove_edge(z, y)
                        changed = True
        return changed
    
    def _apply_rule_r2(self, dag: nx.DiGraph) -> bool:
        """Rule R2: If X -> Y -> Z and X - Z, then X -> Z"""
        changed = False
        for y in dag.nodes():
            predecessors = set(dag.predecessors(y)) - set(dag.successors(y))
            successors = set(dag.successors(y)) - set(dag.predecessors(y))
            
            for x in predecessors:
                for z in successors:
                    if dag.has_edge(z, x):  # X - Z (bidirectional)
                        dag.remove_edge(z, x)
                        changed = True
        return changed
    
    def _apply_rule_r3(self, dag: nx.DiGraph) -> bool:
        """Rule R3: If X - Y, X - Z, Y -> Z, then X -> Y"""
        changed = False
        for x in dag.nodes():
            bidirectional = set(dag.predecessors(x)) & set(dag.successors(x))
            
            for y in bidirectional.copy():
                for z in bidirectional.copy():
                    if y != z and dag.has_edge(y, z) and not dag.has_edge(z, y):
                        dag.remove_edge(x, y)
                        changed = True
        return changed

def bootstrap_stability_test(data: pd.DataFrame, algorithm: PCAlgorithm, 
                           n_bootstrap: int = 100, stability_threshold: float = 0.8) -> Tuple[nx.DiGraph, Dict]:
    """
    Test stability of causal discovery using bootstrap
    
    Returns:
        (stable_graph, stability_scores)
    """
    logger.info(f"Starting bootstrap stability test with {n_bootstrap} samples")
    
    edge_counts: Dict[Tuple[str, str], int] = {}
    n_samples = len(data)
    
    for i in range(n_bootstrap):
        # Bootstrap sample
        bootstrap_data = data.sample(n=n_samples, replace=True)
        
        # Run PC algorithm
        skeleton = algorithm.discover_skeleton(bootstrap_data)
        dag = algorithm.orient_edges(skeleton, bootstrap_data)
        
        # Count edges
        for edge in dag.edges():
            edge_counts[edge] = edge_counts.get(edge, 0) + 1
    
    # Create stable graph with edges that appear frequently
    stable_edges = {edge: count/n_bootstrap for edge, count in edge_counts.items() 
                   if count/n_bootstrap >= stability_threshold}
    
    stable_graph = nx.DiGraph()
    stable_graph.add_nodes_from(data.columns)
    stable_graph.add_edges_from(stable_edges.keys())
    
    logger.info(f"Bootstrap complete. {len(stable_edges)} stable edges found")
    
    return stable_graph, stable_edges

# Additional statistical utilities
def calculate_effect_size_cohen_d(treatment_group: np.ndarray, control_group: np.ndarray) -> float:
    """Calculate Cohen's d effect size"""
    pooled_std = np.sqrt(((len(treatment_group) - 1) * np.var(treatment_group, ddof=1) +
                         (len(control_group) - 1) * np.var(control_group, ddof=1)) /
                        (len(treatment_group) + len(control_group) - 2))
    
    return (np.mean(treatment_group) - np.mean(control_group)) / pooled_std

def granger_causality_test(X: np.ndarray, Y: np.ndarray, max_lags: int = 5) -> Dict:
    """
    Granger causality test for time series data
    
    Returns:
        Dictionary with test results
    """
    from scipy import stats
    from sklearn.linear_model import LinearRegression
    
    results = {}
    
    for lag in range(1, max_lags + 1):
        # Create lagged features
        X_lagged = np.column_stack([X[i:-(lag-i)] for i in range(lag)])
        Y_lagged = np.column_stack([Y[i:-(lag-i)] for i in range(lag)])
        Y_target = Y[lag:]
        
        if len(Y_target) < lag + 10:  # Need sufficient data
            continue
        
        # Restricted model: Y ~ Y_lagged
        model_restricted = LinearRegression().fit(Y_lagged, Y_target)
        rss_restricted = np.sum((Y_target - model_restricted.predict(Y_lagged)) ** 2)
        
        # Unrestricted model: Y ~ Y_lagged + X_lagged
        X_combined = np.column_stack([Y_lagged, X_lagged])
        model_unrestricted = LinearRegression().fit(X_combined, Y_target)
        rss_unrestricted = np.sum((Y_target - model_unrestricted.predict(X_combined)) ** 2)
        
        # F-test
        f_stat = ((rss_restricted - rss_unrestricted) / lag) / (rss_unrestricted / (len(Y_target) - 2 * lag))
        p_value = 1 - stats.f.cdf(f_stat, lag, len(Y_target) - 2 * lag)
        
        results[lag] = {
            'f_statistic': f_stat,
            'p_value': p_value,
            'causality_detected': p_value < 0.05
        }
    
    return results

if __name__ == "__main__":
    # Example usage
    np.random.seed(42)
    
    # Generate synthetic data
    n = 1000
    X1 = np.random.normal(0, 1, n)
    X2 = 0.5 * X1 + np.random.normal(0, 0.5, n)
    X3 = 0.3 * X1 + 0.4 * X2 + np.random.normal(0, 0.3, n)
    X4 = np.random.normal(0, 1, n)  # Independent
    
    data = pd.DataFrame({
        'X1': X1, 'X2': X2, 'X3': X3, 'X4': X4
    })
    
    # Run PC algorithm
    ci_test = ConditionalIndependenceTest(method="partial_correlation", alpha=0.01)
    pc = PCAlgorithm(ci_test=ci_test, max_conditioning_size=2)
    
    skeleton = pc.discover_skeleton(data)
    dag = pc.orient_edges(skeleton, data)
    
    print("Discovered edges:")
    for edge in dag.edges():
        print(f"  {edge[0]} -> {edge[1]}")
    
    # Bootstrap stability test
    stable_dag, stability = bootstrap_stability_test(data, pc, n_bootstrap=50)
    
    print("\nStable edges (>80% bootstrap support):")
    for edge, support in stability.items():
        print(f"  {edge[0]} -> {edge[1]} (support: {support:.2f})")