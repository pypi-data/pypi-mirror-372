from typing import Tuple, Optional, List
import numpy as np

class FastPseudoRandomRotation:
    """
    Fast pseudorandom rotation using blocked Walsh-Hadamard Transform (FWHT).
    Supports arbitrary dimensions by padding and using block-wise transformations.
    """
    
    def __init__(self, dimension: int, rounds: int = 3, seed: Optional[int] = None):
        self.dimension = dimension
        self.rounds = rounds
        self.rng = np.random.RandomState(seed)
        
        # Pre-compute rotation parameters for efficiency
        self._setup_rotation_params()
    
    def _setup_rotation_params(self):
        """Pre-compute random signs and permutations for each round."""
        self.sign_matrices = []
        self.permutations = []
        
        # Pad to nearest multiple of 32 for efficient block processing
        self.padded_dim = ((self.dimension + 31) // 32) * 32
        
        for _ in range(self.rounds):
            # Random signs for each dimension
            signs = self.rng.choice([-1, 1], size=self.padded_dim)
            self.sign_matrices.append(signs)
            
            # Random permutation for swapping elements between blocks
            perm = self.rng.permutation(self.padded_dim)
            self.permutations.append(perm)
    
    def _fwht_block(self, x: np.ndarray, block_size: int) -> np.ndarray:
        """Fast Walsh-Hadamard Transform for a block of size 2^k."""
        n = len(x)
        if n != block_size or (block_size & (block_size - 1)) != 0:
            raise ValueError("Block size must be a power of 2")
        
        result = x.copy()
        step = 1
        
        while step < block_size:
            for i in range(0, block_size, step * 2):
                for j in range(step):
                    u = result[i + j]
                    v = result[i + j + step]
                    result[i + j] = u + v
                    result[i + j + step] = u - v
            step *= 2
        
        # Normalize
        return result / np.sqrt(block_size)
    
    def _apply_blocked_fwht(self, x: np.ndarray) -> np.ndarray:
        """Apply FWHT in blocks along the vector."""
        result = x.copy()
        pos = 0
        
        while pos < len(result):
            remaining = len(result) - pos
            
            if remaining >= 256:
                block_size = 256
            elif remaining >= 64:
                block_size = 64
            elif remaining >= 32:
                block_size = 32
            else:
                block_size = 32
                padding_needed = block_size - remaining
                result = np.concatenate([result, np.zeros(padding_needed)])
            
            block = result[pos:pos + block_size]
            result[pos:pos + block_size] = self._fwht_block(block, block_size)
            pos += block_size
        
        return result[:self.padded_dim]
    
    def rotate(self, x: np.ndarray) -> np.ndarray:
        """Apply fast pseudorandom rotation to vector x."""
        if len(x) != self.dimension:
            raise ValueError(f"Vector dimension {len(x)} doesn't match expected {self.dimension}")
        
        padded_x = np.zeros(self.padded_dim)
        padded_x[:self.dimension] = x
        
        result = padded_x.copy()
        
        for round_idx in range(self.rounds):
            result *= self.sign_matrices[round_idx]
            result = self._apply_blocked_fwht(result)
            result = result[self.permutations[round_idx]]
        
        return result[:self.dimension]

class RotationalQuantization:
    """
    8-bit Rotational Quantization.
    Combines fast pseudorandom rotation with scalar quantization.
    """
    
    def __init__(self, dimension: int, rotation_rounds: int = 3, seed: Optional[int] = None):
        self.dimension = dimension
        self.rotation = FastPseudoRandomRotation(dimension, rotation_rounds, seed)
    
    def encode(self, x: np.ndarray) -> Tuple[np.ndarray, float, float, float]:
        """Encode vector x using 8-bit rotational quantization."""
        if len(x) != self.dimension:
            raise ValueError(f"Vector dimension {len(x)} doesn't match expected {self.dimension}")
        
        norm_squared = np.dot(x, x)
        rotated_x = self.rotation.rotate(x)
        
        min_val, max_val = np.min(rotated_x), np.max(rotated_x)
        l_x = min_val
        delta_x = (max_val - min_val) / 255.0 if max_val != min_val else 1.0
        
        quantized = np.floor((rotated_x - l_x) / delta_x + 0.5).astype(np.uint8)
        quantized = np.clip(quantized, 0, 255)
        
        return quantized, l_x, delta_x, norm_squared
    
    def estimate_inner_product(self, 
                               q_code: np.ndarray, q_l: float, q_delta: float,
                               x_code: np.ndarray, x_l: float, x_delta: float) -> float:
        """Estimate inner product between two 8-bit quantized vectors."""
        d = len(q_code)
        sum_q = np.sum(q_code.astype(np.float32))
        sum_x = np.sum(x_code.astype(np.float32))
        dot_product = np.dot(q_code.astype(np.float32), x_code.astype(np.float32))
        
        inner_product = (d * q_l * x_l + 
                         q_l * x_delta * sum_x + 
                         x_l * q_delta * sum_q + 
                         q_delta * x_delta * dot_product)
        return inner_product
    
    def cosine_similarity(self,
                          q_code: np.ndarray, q_l: float, q_delta: float, q_norm_sq: float,
                          x_code: np.ndarray, x_l: float, x_delta: float, x_norm_sq: float) -> float:
        """Estimate cosine similarity between 8-bit quantized vectors."""
        if q_norm_sq == 0 or x_norm_sq == 0:
            return 0.0
        inner_prod = self.estimate_inner_product(q_code, q_l, q_delta, x_code, x_l, x_delta)
        return inner_prod / (np.sqrt(q_norm_sq) * np.sqrt(x_norm_sq))

class BinaryRotationalQuantization:
    """
    1-bit Rotational Quantization (RaBitQ) based on the Go implementation.
    Combines fast pseudorandom rotation with 1-bit (sign) and multi-bit (query) quantization.
    """
    
    MIN_CODE_BITS = 256
    QUERY_BITS = 5

    def __init__(self, dimension: int, rotation_rounds: int = 3, seed: Optional[int] = None):
        self.input_dimension = dimension
        self.padded_dimension = max(dimension, self.MIN_CODE_BITS)
        self.rotation = FastPseudoRandomRotation(self.padded_dimension, rotation_rounds, seed)
        self.rng = np.random.RandomState(seed)
        self.rounding = self.rng.rand(self.padded_dimension).astype(np.float32)

    def _pad_vector(self, x: np.ndarray) -> np.ndarray:
        if len(x) >= self.padded_dimension:
            return x[:self.padded_dimension]
        padded_x = np.zeros(self.padded_dimension, dtype=np.float32)
        padded_x[:len(x)] = x
        return padded_x

    def encode(self, x: np.ndarray) -> Tuple[np.ndarray, float, float]:
        """Encode a database vector x using 1-bit rotational quantization."""
        if x.ndim != 1: raise ValueError("Input vector must be 1D.")
        norm_squared = np.dot(x, x)
        padded_x = self._pad_vector(x)
        rotated_x = self.rotation.rotate(padded_x)
        
        l1_norm = np.sum(np.abs(rotated_x))
        if l1_norm == 0:
            step = 0.0
        else:
            rotated_norm_sq = np.dot(rotated_x, rotated_x)
            step = rotated_norm_sq / l1_norm
        
        bits = (rotated_x > 0)
        packed_bits = np.packbits(bits)
        return packed_bits, float(step), float(norm_squared)

    def encode_query(self, q: np.ndarray) -> Tuple[List[np.ndarray], float, float]:
        """Encode a query vector q using multi-bit quantization."""
        if q.ndim != 1: raise ValueError("Query vector must be 1D.")
        norm_squared = np.dot(q, q)
        padded_q = self._pad_vector(q)
        rotated_q = self.rotation.rotate(padded_q)
        
        max_abs = np.max(np.abs(rotated_q))
        if max_abs == 0:
            num_bytes = int(np.ceil(self.padded_dimension / 8))
            return ([np.zeros(num_bytes, dtype=np.uint8)] * self.QUERY_BITS, 0.0, float(norm_squared))
        
        num_levels = 2**self.QUERY_BITS - 1
        step = max_abs / num_levels
        
        quantized_indices = np.floor(((rotated_q + max_abs) / (2 * step)) + self.rounding).astype(np.uint32)
        
        query_codes = []
        for i in range(self.QUERY_BITS):
            bit_plane = ((quantized_indices >> i) & 1).astype(bool)
            query_codes.append(np.packbits(bit_plane))
        return query_codes, float(step), float(norm_squared)
    
    @staticmethod
    def _hamming_dist_packed(a: np.ndarray, b: np.ndarray) -> int:
        """Calculates Hamming distance between two packed uint8 arrays."""
        xor_result = np.bitwise_xor(a, b)
        popcount_table = np.array([bin(i).count('1') for i in range(256)], dtype=np.uint8)
        return np.sum(popcount_table[xor_result])

    def estimate_inner_product(self,
                               query_codes: List[np.ndarray], q_step: float,
                               db_packed_bits: np.ndarray, db_step: float) -> float:
        """Estimate inner product between 1-bit and multi-bit quantized vectors."""
        if q_step == 0 or db_step == 0: return 0.0
        num_levels = (1 << self.QUERY_BITS) - 1
        dot = float(num_levels * self.padded_dimension)
        
        for i in range(self.QUERY_BITS):
            hamming_dist = self._hamming_dist_packed(query_codes[i], db_packed_bits)
            dot -= (1 << (i + 1)) * hamming_dist
        
        return q_step * db_step * dot

    def cosine_similarity(self, 
                          query_codes: List[np.ndarray], q_step: float, q_norm_sq: float,
                          db_packed_bits: np.ndarray, db_step: float, db_norm_sq: float) -> float:
        """Estimate cosine similarity from 1-bit quantized codes."""
        if q_norm_sq == 0 or db_norm_sq == 0: return 0.0
        inner_prod = self.estimate_inner_product(query_codes, q_step, db_packed_bits, db_step)
        denominator = np.sqrt(q_norm_sq) * np.sqrt(db_norm_sq)
        if denominator == 0: return 0.0
        return inner_prod / denominator
