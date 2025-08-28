"""
Aurora Trinity-3 Trigate Implementation
======================================

Fundamental logic module based on geometric coherence and ternary logic.
Implements inference, learning, and deduction modes with O(1) LUT operations.

Based on the principle: A + B + R = 180° (geometric triangle closure)
Translated to ternary logic: {0, 1, NULL}

Author: Aurora Program
License: Apache-2.0 + CC-BY-4.0
"""

from typing import List, Union, Optional, Tuple, Dict
import itertools


# Ternary values
NULL = None
TERNARY_VALUES = [0, 1, NULL]


class Trigate:
    """
    Fundamental Aurora logic module implementing ternary operations.
    
    Supports three operational modes:
    1. Inference: A + B + M -> R (given inputs and control, compute result)
    2. Learning: A + B + R -> M (given inputs and result, learn control)
    3. Deduction: M + R + A -> B (given control, result, and one input, deduce other)
    
    All operations are O(1) using precomputed lookup tables (LUTs).
    """
    
    # Class-level LUTs (computed once at module load)
    _LUT_INFER: Dict[Tuple, int] = {}
    _LUT_LEARN: Dict[Tuple, int] = {}
    _LUT_DEDUCE_A: Dict[Tuple, int] = {}
    _LUT_DEDUCE_B: Dict[Tuple, int] = {}
    _initialized = False
    
    def __init__(self):
        """Initialize Trigate and ensure LUTs are computed."""
        if not Trigate._initialized:
            Trigate._initialize_luts()
    
    @classmethod
    def _initialize_luts(cls):
        """
        Initialize all lookup tables for O(1) operations.
        
        Based on extended XOR logic with NULL propagation:
        - 0 XOR 0 = 0, 0 XOR 1 = 1, 1 XOR 0 = 1, 1 XOR 1 = 0
        - Any operation with NULL propagates NULL
        - Control bit M determines XOR (1) or XNOR (0)
        """
        print("Initializing Trigate LUTs...")
        
        # Generate all possible combinations for ternary logic
        for a, b, m, r in itertools.product(TERNARY_VALUES, repeat=4):
            
            # INFERENCE LUT: (a, b, m) -> r
            computed_r = cls._compute_inference(a, b, m)
            cls._LUT_INFER[(a, b, m)] = computed_r
            
            # LEARNING LUT: (a, b, r) -> m
            # Find control M that produces R given A, B
            learned_m = cls._compute_learning(a, b, r)
            cls._LUT_LEARN[(a, b, r)] = learned_m
            
            # DEDUCTION LUTS: (m, r, a) -> b and (m, r, b) -> a
            deduced_b = cls._compute_deduction_b(m, r, a)
            deduced_a = cls._compute_deduction_a(m, r, b)
            
            cls._LUT_DEDUCE_B[(m, r, a)] = deduced_b
            cls._LUT_DEDUCE_A[(m, r, b)] = deduced_a
        
        cls._initialized = True
        print(f"Trigate LUTs initialized: {len(cls._LUT_INFER)} entries each")
    
    @staticmethod
    def _compute_inference(a: Union[int, None], b: Union[int, None], m: Union[int, None]) -> Union[int, None]:
        """
        Compute R given A, B, M using ternary logic.
        
        Logic:
        - If any input is NULL, result is NULL
        - If M is 1: R = A XOR B
        - If M is 0: R = A XNOR B (NOT(A XOR B))
        """
        if a is NULL or b is NULL or m is NULL:
            return NULL
        
        if m == 1:  # XOR mode
            return a ^ b
        else:  # XNOR mode (m == 0)
            return 1 - (a ^ b)
    
    @staticmethod
    def _compute_learning(a: Union[int, None], b: Union[int, None], r: Union[int, None]) -> Union[int, None]:
        """
        Learn control M given A, B, R.
        
        Logic:
        - If any input is NULL, cannot learn -> NULL
        - If A XOR B == R, then M = 1 (XOR)
        - If A XOR B != R, then M = 0 (XNOR)
        """
        if a is NULL or b is NULL or r is NULL:
            return NULL
        
        xor_result = a ^ b
        if xor_result == r:
            return 1  # XOR mode produces correct result
        else:
            return 0  # XNOR mode produces correct result
    
    @staticmethod
    def _compute_deduction_a(m: Union[int, None], r: Union[int, None], b: Union[int, None]) -> Union[int, None]:
        """
        Deduce A given M, R, B.
        
        Logic:
        - If any input is NULL, cannot deduce -> NULL
        - If M is 1: A = R XOR B (since R = A XOR B)
        - If M is 0: A = NOT(R) XOR B (since R = NOT(A XOR B))
        """
        if m is NULL or r is NULL or b is NULL:
            return NULL
        
        if m == 1:  # XOR mode: A XOR B = R -> A = R XOR B
            return r ^ b
        else:  # XNOR mode: NOT(A XOR B) = R -> A XOR B = NOT(R) -> A = NOT(R) XOR B
            return (1 - r) ^ b
    
    @staticmethod
    def _compute_deduction_b(m: Union[int, None], r: Union[int, None], a: Union[int, None]) -> Union[int, None]:
        """
        Deduce B given M, R, A.
        
        Logic: Same as deduce_a but solving for B instead of A.
        """
        if m is NULL or r is NULL or a is NULL:
            return NULL
        
        if m == 1:  # XOR mode: A XOR B = R -> B = R XOR A
            return r ^ a
        else:  # XNOR mode: NOT(A XOR B) = R -> A XOR B = NOT(R) -> B = NOT(R) XOR A
            return (1 - r) ^ a
    
    def infer(self, A: List[Union[int, None]], B: List[Union[int, None]], M: List[Union[int, None]]) -> List[Union[int, None]]:
        """
        Inference mode: Compute R given A, B, M.
        
        Args:
            A: First input vector (3 bits)
            B: Second input vector (3 bits)
            M: Control vector (3 bits)
            
        Returns:
            R: Result vector (3 bits)
            
        Example:
            >>> trigate = Trigate()
            >>> A = [0, 1, 0]
            >>> B = [1, 0, 1]
            >>> M = [1, 1, 0]  # XOR, XOR, XNOR
            >>> R = trigate.infer(A, B, M)
            >>> print(R)  # [1, 1, 1]
        """
        if not (len(A) == len(B) == len(M) == 3):
            raise ValueError("All vectors must have exactly 3 elements")
        
        return [self._LUT_INFER[(a, b, m)] for a, b, m in zip(A, B, M)]
    
    def learn(self, A: List[Union[int, None]], B: List[Union[int, None]], R: List[Union[int, None]]) -> List[Union[int, None]]:
        """
        Learning mode: Learn control M given A, B, R.
        
        Args:
            A: First input vector (3 bits)
            B: Second input vector (3 bits)
            R: Target result vector (3 bits)
            
        Returns:
            M: Learned control vector (3 bits)
            
        Example:
            >>> trigate = Trigate()
            >>> A = [0, 1, 0]
            >>> B = [1, 0, 1]
            >>> R = [1, 1, 1]
            >>> M = trigate.learn(A, B, R)
            >>> print(M)  # [1, 1, 0]
        """
        if not (len(A) == len(B) == len(R) == 3):
            raise ValueError("All vectors must have exactly 3 elements")
        
        return [self._LUT_LEARN[(a, b, r)] for a, b, r in zip(A, B, R)]
    
    def deduce_a(self, M: List[Union[int, None]], R: List[Union[int, None]], B: List[Union[int, None]]) -> List[Union[int, None]]:
        """
        Deduction mode: Deduce A given M, R, B.
        
        Args:
            M: Control vector (3 bits)
            R: Result vector (3 bits)
            B: Known input vector (3 bits)
            
        Returns:
            A: Deduced input vector (3 bits)
        """
        if not (len(M) == len(R) == len(B) == 3):
            raise ValueError("All vectors must have exactly 3 elements")
        
        return [self._LUT_DEDUCE_A[(m, r, b)] for m, r, b in zip(M, R, B)]
    
    def deduce_b(self, M: List[Union[int, None]], R: List[Union[int, None]], A: List[Union[int, None]]) -> List[Union[int, None]]:
        """
        Deduction mode: Deduce B given M, R, A.
        
        Args:
            M: Control vector (3 bits)
            R: Result vector (3 bits)
            A: Known input vector (3 bits)
            
        Returns:
            B: Deduced input vector (3 bits)
        """
        if not (len(M) == len(R) == len(A) == 3):
            raise ValueError("All vectors must have exactly 3 elements")
        
        return [self._LUT_DEDUCE_B[(m, r, a)] for m, r, a in zip(M, R, A)]
    
    def validate_triangle_closure(self, A: List[Union[int, None]], B: List[Union[int, None]], 
                                  M: List[Union[int, None]], R: List[Union[int, None]]) -> bool:
        """
        Validate that A, B, M, R form a valid logical triangle.
        
        This ensures geometric coherence: the triangle "closes" properly.
        
        Args:
            A, B, M, R: The four vectors forming the logical triangle
            
        Returns:
            True if triangle is valid, False otherwise
        """
        # Compute expected R from A, B, M
        expected_R = self.infer(A, B, M)
        
        # Check if computed R matches provided R
        for expected, actual in zip(expected_R, R):
            if expected != actual:
                return False
        
        return True
    
    def get_truth_table(self, operation: str = "infer") -> str:
        """
        Generate human-readable truth table for debugging.
        
        Args:
            operation: "infer", "learn", "deduce_a", or "deduce_b"
            
        Returns:
            Formatted truth table string
        """
        if operation == "infer":
            lut = self._LUT_INFER
            header = "A | B | M | R"
        elif operation == "learn":
            lut = self._LUT_LEARN
            header = "A | B | R | M"
        elif operation == "deduce_a":
            lut = self._LUT_DEDUCE_A
            header = "M | R | B | A"
        elif operation == "deduce_b":
            lut = self._LUT_DEDUCE_B
            header = "M | R | A | B"
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        def format_val(v):
            return "N" if v is NULL else str(v)
        
        lines = [header, "-" * len(header)]
        
        for key, value in sorted(lut.items()):
            key_str = " | ".join(format_val(k) for k in key)
            val_str = format_val(value)
            lines.append(f"{key_str} | {val_str}")
        
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        return f"Trigate(initialized={self._initialized}, lut_size={len(self._LUT_INFER)})"


# Example usage and testing
if __name__ == "__main__":
    # Create Trigate instance
    trigate = Trigate()
    
    print("=== Aurora Trigate Implementation ===\n")
    
    # Test inference
    print("1. Inference Test:")
    A = [0, 1, 0]
    B = [1, 0, 1]
    M = [1, 1, 0]  # XOR, XOR, XNOR
    R = trigate.infer(A, B, M)
    print(f"   A={A}, B={B}, M={M} -> R={R}")
    
    # Test learning
    print("\n2. Learning Test:")
    A = [0, 1, 0]
    B = [1, 0, 1]
    R = [1, 1, 1]
    M_learned = trigate.learn(A, B, R)
    print(f"   A={A}, B={B}, R={R} -> M={M_learned}")
    
    # Test deduction
    print("\n3. Deduction Test:")
    M = [1, 1, 0]
    R = [1, 1, 1]
    A = [0, 1, 0]
    B_deduced = trigate.deduce_b(M, R, A)
    print(f"   M={M}, R={R}, A={A} -> B={B_deduced}")
    
    # Test with NULL values
    print("\n4. NULL Propagation Test:")
    A_null = [0, 1, None]
    B_null = [1, 0, 1]
    M_null = [1, 1, 1]
    R_null = trigate.infer(A_null, B_null, M_null)
    print(f"   A={A_null}, B={B_null}, M={M_null} -> R={R_null}")
    
    # Validate triangle closure
    print("\n5. Triangle Closure Validation:")
    is_valid = trigate.validate_triangle_closure([0, 1, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1])
    print(f"   Triangle is valid: {is_valid}")
    
    print(f"\n6. Trigate Status: {trigate}")
