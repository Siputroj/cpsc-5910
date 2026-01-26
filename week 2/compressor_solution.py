"""
Jason Siputro 
CPSC 5910 03 26WQ
Assignment 1: The Re-Pair Compressor
Jan 25, 2026
"""
from collections import defaultdict
import heapq


def compress_text(text: str, k: int, return_count: bool = False):
   '''
   compress the text by merging the most frequent pair k times

   :param text: text to compres
   :type text: str
   :param k: number of times merging happen
   :type k: int
   :return: compressed string
   :rtype: str
   '''

   # simulate a linked list using arrays
   next = []
   char = []
   prev = []

   if not text:
      return ("", 0) if return_count else ""

   for i in range(len(text)):
      char.append(text[i])

      # represent -1 for index that does not exist
      next.append(i + 1) if i + 1 < len(text) else next.append(-1)
      prev.append(i - 1) if i - 1 >= 0 else prev.append(-1)

   pairs_dict = defaultdict(set)    # store pairs in dictionary key: pair, value: all the positions of that pair
   pair_version = {}                # store pair versions to check for stale heap entry
   pair_min = {}                    # keep track of the first appearance of the pair
   heap = []                        # heap to find which pair to merge

   # initializing pairs_dict
   for i in range(len(char)):
      if next[i] == -1:
         continue
      charPair = (char[i], char[next[i]])
      pairs_dict[charPair].add(i)

   # initialize the heap
   for pair, positions in pairs_dict.items():
      first_pos = min(positions)
      pair_min[pair] = first_pos
      pair_version[pair] = 0

      # store the frequency --> -ve frequency since heap is min heap
      # store first position --> tie breaker for equal frequency
      # store version --> for stale entry invalidation
      # store the pair
      if len(positions) >= 2:
         heapq.heappush(heap, (-len(positions), first_pos, pair_version[pair], pair))

   replacement_code = 65 # starts with 'A', 26 characters to 'Z'

   # function to add pair to dict and if total positions is more than 1, add to heap
   def add_pair(pos, pair, update_heap=True):
      positions = pairs_dict[pair]

      if pos in positions:
         return
      
      positions.add(pos)

      # update the pair version, if not initialize to 0
      if pair in pair_version:
         pair_version[pair] += 1
      else:
         pair_version[pair] = 0

      # check if pair exis
      if pair not in pair_min or pos < pair_min[pair]:
         pair_min[pair] = pos
      
      if not update_heap:
         return

      if len(positions) < 2:
         return
      heapq.heappush(heap, (-len(positions), pair_min[pair], pair_version[pair], pair))

   # function to remove a position from the pair dict and push to heap if needed.
   # some pair may not be in the heap anymore after removal, so we need to check if it still has more than 1 instance
   def remove_pair(pos, pair, update_heap=True):
      positions = pairs_dict.get(pair)
      if not positions or pos not in positions:
         return
      
      positions.remove(pos)

      if pair in pair_version:
         pair_version[pair] += 1
      else:
         pair_version[pair] = 0

      # if no more instance, remove all entry of that pair from all dict
      if not positions:
         pair_min.pop(pair, None)
         pair_version.pop(pair, None)
         pairs_dict.pop(pair, None)
         return
      
      if not update_heap:
         return
      
      # find the new minimum for that pair
      if pair_min.get(pair) == pos:
         new_min = None
         for p in positions:
            if new_min is None or p < new_min:
               new_min = p
         pair_min[pair] = new_min

      # add to heap again if pair appear more than once
      if len(positions) < 2:
         return
      heapq.heappush(heap, (-len(positions), pair_min[pair], pair_version[pair], pair))

   for _ in range(k):
      # pop until we find a valid, up-to-date entry
      target_pair = None
      positions = None
      while heap:
         freq_neg, _, candidate_version, candidate_pair = heapq.heappop(heap)
         candidate_positions = pairs_dict.get(candidate_pair)

         # check if candidate pair exist
         if not candidate_positions:
            continue

         # check if entry is stale -- if it matches the dict state
         if candidate_version != pair_version[candidate_pair]:
            continue
         
         # select the target pair and their positions
         target_pair = candidate_pair
         positions = candidate_positions
         break

      # check if frequency is now less than 2 -- everything else under it will be less or equal
      if not target_pair or len(positions) < 2:
         break

      # get new symbol to replace
      new_symbol = chr(replacement_code)
      replacement_code += 1

      # sort the positions to ensure we process them in order
      positions_snapshot = sorted(list(positions))
      target_left, target_right = target_pair

      for i in positions_snapshot:
         
         # check if j is valid
         j = next[i]
         if j == -1:
            remove_pair(i, target_pair, update_heap=False)
            continue

         # check if the pair matches the target pair
         char_i = char[i]
         char_j = char[j]
         if char_i != target_left or char_j != target_right:
            remove_pair(i, target_pair, update_heap=False)
            continue
         
         # get the adjacent symbols' indexes
         prev_i = prev[i]
         next_j = next[j]

         # remove the previous pair that includes char_i
         if prev_i != -1:
            remove_pair(prev_i, (char[prev_i], char_i))

         # remove the current pair. no need to update heap here
         remove_pair(i, (char_i, char_j), update_heap=False)

         # remove the next pair that includes char_j
         if next_j != -1:
            remove_pair(j, (char_j, char[next_j]))

         # merge i and j
         char[i] = new_symbol
         next[i] = next_j
         if next_j != -1:
            prev[next_j] = i
         prev[j] = -1
         next[j] = -1

         # add new pairs around merged symbol
         if prev_i != -1:
            add_pair(prev_i, (char[prev_i], char[i]))
         if next_j != -1:
            add_pair(i, (char[i], char[next_j]))
         

   # rebuild compressed string
   out = []
   idx = 0
   while idx != -1:
      out.append(char[idx])
      idx = next[idx]
   result = "".join(out)
   return result


# function to run the tests
def _run_tests():
   import random
   import time


   rng = random.Random(42)

   def random_text(n):
      return "".join(rng.choice("abcd") for _ in range(n))

   short_cases = [
      (1, "", 5),
      (2, "a", 3),
      (3, "ab", 10),
      (4, "ababcababc", 2),
      (5, "abcdef", 3),
      (6, "abababab", 26),
      (7, "aaaaa", 2),
      (8, "abcabcabc", 4),
   ]

   long_cases = [
      (9, 10_000, 26),
      (10, 20_000, 26),
      (11, 30_000, 26),
      (12, 50_000, 26),
      (13, 70_000, 26),
      (14, 90_000, 26),
      (15, 100_000, 26),
      (16, 200_000, 26),
      (17, 300_000, 26),
      (18, 400_000, 26),
      (19, 500_000, 26),
      (20, 1_000_000, 26),
   ]

   suite_start = time.perf_counter()

   for case_num, text, k in short_cases:
      start = time.perf_counter()
      result = compress_text(text, k)
      elapsed = time.perf_counter() - start

      print(f"================= case {case_num} =================")
      print(f"input: \'{text}\'")
      print(f"merges: {k}")
      print(f"output: \'{result}\'")
      
      print(f"time: {elapsed:.6f}s")

   for case_num, size, k in long_cases:
      text = random_text(size)
      start = time.perf_counter()
      compress_text(text, k)
      elapsed = time.perf_counter() - start

      print(f"================= case {case_num} =================")
      print(f"input_len: {size}")
      print(f"time: {elapsed:.6f}s")

   total_elapsed = time.perf_counter() - suite_start
   print(f"total_time={total_elapsed:.6f}s")

if __name__ == "__main__":
   _run_tests()
