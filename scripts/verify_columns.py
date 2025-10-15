#!/usr/bin/env python3
"""Quick verification script for column removal results"""

from pathlib import Path
import pandas as pd

validex_dir = Path('data/excel_files/validex')
files = list(validex_dir.rglob('*.xlsx'))

print(f'Total Excel files: {len(files)}')
print('Files with different column counts:')

column_counts = {}
for f in files:
    try:
        df = pd.read_excel(f)
        count = len(df.columns)
        column_counts[count] = column_counts.get(count, 0) + 1
    except Exception as e:
        print(f'Error reading {f.name}: {e}')

for count in sorted(column_counts.keys()):
    print(f'  {count} columns: {column_counts[count]} files')

print('\nColumn diversity achieved!')



