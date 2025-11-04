# Data Examples

This directory contains example data files that demonstrate the expected format for user financial data uploads.

## Files

- `example_user_data_1.json` - Example user financial data with accounts, transactions, and liabilities
- `example_user_data_2.json` - Another example with different account types and transaction patterns

## Data Format

The JSON files follow the Plaid API format and include:

- **user_id**: Unique identifier for the user
- **accounts**: Array of account objects (checking, savings, credit cards, etc.)
- **transactions**: Array of transaction objects
- **liabilities**: Array of liability objects (loans, mortgages, etc.)

## Usage

These examples can be used for:
- Testing the data upload endpoint
- Understanding the expected data structure
- Local development and testing
- Documentation purposes

## Notes

- These are example files only and do not contain real user data
- The actual synthetic data directories (`synthetic_data/`, `synthetic_data 2/`, etc.) are excluded from version control via `.gitignore`
- When uploading via the API, ensure the file matches this structure

