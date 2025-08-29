
class LexoRank:
    """
    Dynamic LexoRank implementation that allows for variable rank lengths and spacing.
    - Uses base-62 (0-9, A-Z, a-z)
    - Starts with 5-length ranks, increases length as needed
    - Default bulk rank generation start at 20% of the available rank space
    - Default spacing is 1,000 ranks between each rank
    - Can be configured to use different alphabet, min/max lengths, and spacing
    - Default max length is 100
    - Default min length is 5
    - Default default spacing is 1,000 ranks between each rank
    - Default rebalancing diff is 1
    - Default start from is 20%
    - Default end at is 60%

    Args:
        alphabet: str (Is is a default alphabet to generate ranks)
        min_length: int (Is is a minimum length of a rank)
        max_length: int (Is is a maximum length of a rank)
        default_spacing: int (Is is a default spacing between ranks)
        rebalancing_diff: int (Is is a min diff between two ranks to rebalance)
        start_from: int (Is is a start point (In percentage) from where we start generate ranks from the available space)
        end_at: int (Is is a end point (In percentage) to where we end generate ranks from the available space)
    """

    def __init__(self, 
                 alphabet:str='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                 min_length:int=5,
                 max_length:int=100,
                 default_spacing:int=1_000,
                 rebalancing_diff:int=1,
                 start_from:int=20,
                 end_at:int=60,
                 ):
        self.alphabet = alphabet
        self.base = len(alphabet)
        self.min_length = min_length
        self.max_length = max_length
        self.default_spacing = default_spacing
        self.start_from = start_from
        self.start_val = (self.base ** self.min_length * self.start_from) // 100
        self.end_at = end_at
        self.rebalancing_diff = rebalancing_diff
        self.char_to_val = {c: i for i, c in enumerate(alphabet)}
        self.val_to_char = {i: c for i, c in enumerate(alphabet)}

    def _pad(self, s:str, length:int):
        return s + self.alphabet[0] * (length - len(s))

    def _rank_to_int(self, rank:str):
        val = 0
        for c in rank:
            if c not in self.char_to_val:
                raise ValueError(f"Invalid character '{c}' in rank")
            val = val * self.base + self.char_to_val[c]
        return val

    def _int_to_rank(self, val: int, length: int = None):
        s = []
        # Always convert at least once (for val=0)
        while val > 0 or not s:
            val, r = divmod(val, self.base)
            s.append(self.val_to_char[r])
        rank = ''.join(reversed(s))
        if length is not None:
            rank = rank.rjust(length, self.alphabet[0])
        return rank
    
    def _dynamic_gap(self, rank_length: int) -> int:
        base_gap = self.default_spacing
        # For each character above min_length, double the gap
        return base_gap * (2 ** (rank_length - self.min_length))

    
    def between(self, prev: str = None, next: str = None, spacing: str = None):
        """
        Returns (new_rank, needs_rebalance)
        - new_rank: the generated rank between prev and next
        - needs_rebalance: True if the new rank's length exceeds max_length or if no space is left
        """
        gap = spacing if spacing else self.default_spacing
        
        # Case 1: No bounds - return middle rank
        if not prev and not next:
            rank = self._int_to_rank(self.start_val)
            return rank, len(rank) > self.max_length
        
        # Case 2: Only prev exists (append after)
        if not next:
            return self._generate_after(prev, gap)
        
        # Case 3: Only next exists (prepend before)
        if not prev:
            return self._generate_before(next, gap)
        
        # Case 4: Both exist - generate between
        return self._generate_between(prev, next)

    def _generate_after(self, prev: str, gap: int):
        """Generate rank after prev with given gap"""
        # Try to increment within same length first
        prev_val = self._rank_to_int(prev)

        if prev_val+1 >= self.base ** self.max_length:
            return None , True

        max_val_same_length = self.base ** len(prev)
        
        if prev_val + gap < max_val_same_length:
            new_rank = self._int_to_rank(prev_val + gap, len(prev))
            return new_rank, len(new_rank) > self.max_length
        
        # Need to extend length
        new_length = len(prev) + 1
        # Start from beginning of next length tier
        new_val = (self.base ** new_length * self.start_from) // 100
        new_rank = self._int_to_rank(new_val, new_length)
        return new_rank, new_length > self.max_length

    def _generate_before(self, next: str, gap: int):
        """Generate rank before next with given gap"""
        next_val = self._rank_to_int(next)

        if next_val <= 0:
            return None , True
        
        if next_val >= gap:
            new_rank = self._int_to_rank(next_val - gap, len(next))
            return new_rank, len(new_rank) > self.max_length
        
        # Need to extend length - create predecessor tier
        new_length = len(next) + 1
        # Use a value that's clearly before next when normalized
        base_val = (self.base ** new_length * self.start_from) // 100
        # Ensure it's less than next when compared
        target_val = min(base_val, next_val * self.base - gap)
        new_rank = self._int_to_rank(target_val, new_length)
        return new_rank, new_length > self.max_length

    def _generate_between(self, prev: str, next: str):
        """Generate rank between prev and next"""
        # Normalize to same length for comparison
        target_length = max(len(prev), len(next))
        prev_norm = self._normalize_to_length(prev, target_length)
        next_norm = self._normalize_to_length(next, target_length)
        
        prev_val = self._rank_to_int(prev_norm)
        next_val = self._rank_to_int(next_norm)
        
        # Check if there's space at current length
        if next_val - prev_val > 1:
            mid_val = (prev_val + next_val) // 2
            new_rank = self._int_to_rank(mid_val, target_length)
            return new_rank, target_length > self.max_length
        
        # No space at current length, need to extend
        return self._extend_and_split(prev, next, target_length)

    def _extend_and_split(self, prev: str, next: str, current_length: int):
        """Extend length and find split point"""
        # Try incrementally longer lengths
        for new_length in range(current_length + 1, min(current_length + 4, self.max_length + 2)):
            prev_extended = self._normalize_to_length(prev, new_length)
            next_extended = self._normalize_to_length(next, new_length)
            
            prev_val = self._rank_to_int(prev_extended)
            next_val = self._rank_to_int(next_extended)
            
            if next_val - prev_val > self.rebalancing_diff:
                mid_val = (prev_val + next_val) // 2
                new_rank = self._int_to_rank(mid_val, new_length)
                return new_rank, new_length > self.max_length
        
        # If we can't find space, signal rebalancing needed
        return None, True

    def _normalize_to_length(self, rank: str, target_length: int):
        """Normalize rank to target length by padding or truncating intelligently"""
        if len(rank) == target_length:
            return rank
        elif len(rank) < target_length:
            # Pad with start character (usually '0' or equivalent)
            return rank + self.alphabet[0] * (target_length - len(rank))
        else:
            # Truncate but preserve ordering
            return rank[:target_length]

    # Additional utility methods for better performance
    def get_next_rank(self, current: str, gap: int = None):
        """Get next rank after current"""
        gap = gap or self.default_spacing
        return self._generate_after(current, gap)

    def get_prev_rank(self, current: str, gap: int = None):
        """Get previous rank before current"""
        gap = gap or self.default_spacing
        return self._generate_before(current, gap)
    
    def create_initial_rank(self):
        return self.between()
    
    def create_previous_rank(self, rank:str):
        if not rank:
            raise ValueError("Rank is required")
        return self.between(next=rank)
    
    def create_next_rank(self, rank:str):
        if not rank:
            raise ValueError("Rank is required")
        return self.between(prev=rank)

    def generate_bulk(self, count:int = 0, rank_length:int = 0, gap:int = 0, start_rank:str=None):
        """
        Generate `count` ranks of `rank_length` characters.
        Starts from 20% of the available space and adds a fixed gap.
        """
        if not rank_length :
            rank_length = self.min_length

        if not gap:
            gap = self.default_spacing

        max_val = self.base ** rank_length

        if start_rank:
            start_val = self._rank_to_int(start_rank)
        else:
            start_val = (max_val * self.start_from) // 100

        usable_space = max_val - start_val

        if gap is None:
            gap = usable_space // (count + 1)

        if gap == 0:
            raise ValueError("Gap is too small for the given count and rank length")

        ranks = []
        for i in range(count):
            val = start_val + (i + 1) * gap
            rank = self._int_to_rank(val, rank_length)
            ranks.append(rank)

        return ranks
    

    def generate_evenly_bulk(self, count: int = 0, rank_length: int = 0, start_from: int = None, end_at: int = None):
        """
        Generate `count` ranks of `rank_length` characters, evenly distributed between
        self.start_from% and self.end_at% of the available space.
        """
        if not rank_length:
            rank_length = self.min_length

        start_from = start_from or self.start_from
        end_at = end_at or self.end_at

        max_val = self.base ** rank_length
        start_val = (max_val * start_from) // 100
        end_val = (max_val * end_at) // 100

        usable_space = end_val - start_val

        if count <= 0 or usable_space <= count:
            raise ValueError("Not enough space or invalid count")

        gap = usable_space // (count + 1)
        ranks = []
        for i in range(count):
            val = start_val + (i + 1) * gap
            rank = self._int_to_rank(val, rank_length)
            ranks.append(rank)

        return ranks

        