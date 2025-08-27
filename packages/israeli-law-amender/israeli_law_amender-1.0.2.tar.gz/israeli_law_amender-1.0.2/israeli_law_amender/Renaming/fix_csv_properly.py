import pandas as pd
import warnings
warnings.filterwarnings('ignore')

def fix_csv_properly():
    print('Reading CSV with proper quote handling...')
    
    # Read the CSV with proper handling of quoted fields
    # This should preserve law names as single fields despite internal commas
    df = pd.read_csv('Data/amd_database_flow.csv', 
                     delimiter=',',
                     quotechar='"',
                     doublequote=True,
                     skipinitialspace=True,
                     encoding='utf-8')
    
    print(f'Successfully read CSV with {len(df)} rows and {len(df.columns)} columns')
    print('Column names:', df.columns.tolist())
    
    # Check for the problematic law name to verify it's intact
    if 'Name' in df.columns:
        problem_rows = df[df['Name'].str.contains('עידוד מעורבות סטודנטים', na=False)]
        if not problem_rows.empty:
            print('Found problematic law name (should be intact):')
            print(repr(problem_rows['Name'].iloc[0]))
    
    # Save with pipe delimiter
    output_file = 'Data/amd_database_flow_fixed.csv'
    df.to_csv(output_file, sep='|', index=False, encoding='utf-8', quoting=1)
    
    print(f'Successfully saved CSV with pipe delimiters to: {output_file}')
    
    # Verify the conversion worked
    print('Verifying the conversion...')
    df_verify = pd.read_csv(output_file, sep='|', encoding='utf-8')
    print(f'Verification: Read {len(df_verify)} rows and {len(df_verify.columns)} columns')
    
    if 'Name' in df_verify.columns:
        problem_rows_verify = df_verify[df_verify['Name'].str.contains('עידוד מעורבות סטודנטים', na=False)]
        if not problem_rows_verify.empty:
            print('Verified law name is intact:')
            print(repr(problem_rows_verify['Name'].iloc[0]))
    
    return True

if __name__ == "__main__":
    fix_csv_properly() 