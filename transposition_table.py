from constants import *
import sys


class TableEntry:
    EXACT = 0
    LOWER_BOUND = 1
    UPPER_BOUND = 2

    def __init__(self, zobrist_key, depth, value, flag):
        self.zobrist_key = zobrist_key
        self.depth = depth
        self.value = value
        self.flag = flag

    def __str__(self):
        flag_to_str = {0: "EXACT", 1: "LOWER_BOUND", 2: "UPPER_BOUND"}
        return f"Entry(key={self.zobrist_key}, depth={self.depth}, value={self.value}, flag={flag_to_str[self.flag]})"


class TranspositionTable:
    TABLE_SIZE_MB = 100

    def __init__(self):
        # Calculate the size of a single Entry instance in bytes
        zobrist_key_size = 64
        depth_size = 4
        value_size = 4
        flag_size = 4
        entry_size = zobrist_key_size + depth_size + value_size + flag_size
        # entry_size = sys.getsizeof(TableEntry(0, 0, 0, TableEntry.EXACT))

        target_size = TranspositionTable.TABLE_SIZE_MB * 1024 * 1024
        self.num_entries = target_size // entry_size

        self.table = [TableEntry(-1, -1, -1, TableEntry.EXACT)] * self.num_entries

    def clear(self):
        self.table = [TableEntry(-1, -1, -1, TableEntry.EXACT)] * self.num_entries

    def lookup(self, zobrist_key):
        index = zobrist_key % self.num_entries
        entry = self.table[index]

        if entry.zobrist_key == zobrist_key:
            return entry
        else:
            return None

    def store(self, zobrist_key, depth, value, flag):
        index = zobrist_key % self.num_entries
        self.table[index] = TableEntry(zobrist_key, depth, value, flag)


if __name__ == "__main__":
    tt = TranspositionTable()
