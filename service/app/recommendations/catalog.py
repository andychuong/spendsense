"""Recommendation catalog with education items and partner offers."""

from typing import Dict, List, Any

# Education items catalog
# Each item has: id, title, content, persona_ids (list of personas it applies to)
EDUCATION_CATALOG: List[Dict[str, Any]] = [
    # Persona 1: High Utilization
    {
        "id": "edu_001",
        "title": "Debt Paydown Strategies: The Snowball vs. Avalanche Method",
        "content": (
            "Learn two proven strategies for paying down credit card debt:\n\n"
            "**Snowball Method**: Pay minimums on all cards, then focus extra payments on the smallest balance first. "
            "This builds momentum as you eliminate debts one by one.\n\n"
            "**Avalanche Method**: Pay minimums on all cards, then focus extra payments on the highest interest rate first. "
            "This saves the most money in interest charges.\n\n"
            "Both methods work! Choose the one that motivates you most. The key is consistency and avoiding new charges."
        ),
        "persona_ids": [1],
        "tags": ["debt", "credit cards", "interest"],
    },
    {
        "id": "edu_002",
        "title": "Understanding Credit Utilization: How It Affects Your Score",
        "content": (
            "Credit utilization is the percentage of your available credit that you're using. "
            "For example, if you have a $5,000 limit and a $2,500 balance, your utilization is 50%.\n\n"
            "**Why it matters**: Credit utilization makes up 30% of your credit score. "
            "Keeping utilization below 30% is ideal, and below 10% is even better.\n\n"
            "**How to improve**: Pay down balances, request credit limit increases (if you won't use them), "
            "or open a new card (if you're responsible with credit). Lower utilization = higher credit score."
        ),
        "persona_ids": [1],
        "tags": ["credit score", "utilization", "credit cards"],
    },
    {
        "id": "edu_003",
        "title": "The True Cost of Minimum Payments",
        "content": (
            "Making only minimum payments can keep you in debt for years and cost thousands in interest.\n\n"
            "**Example**: If you have a $5,000 balance at 18% APR and only pay the minimum ($125/month), "
            "it will take over 5 years to pay off and cost $2,500+ in interest.\n\n"
            "**Better approach**: Even paying $50 extra per month can cut years off your payoff timeline. "
            "Use a debt payoff calculator to see how small increases in payments dramatically reduce total interest."
        ),
        "persona_ids": [1],
        "tags": ["minimum payments", "interest", "debt"],
    },

    # Persona 2: Variable Income Budgeter
    {
        "id": "edu_004",
        "title": "Variable Income Budget Template",
        "content": (
            "Budgeting with irregular income requires a different approach:\n\n"
            "**Step 1: Calculate Your Baseline**\n"
            "Average your income over the last 6-12 months to find your baseline monthly income.\n\n"
            "**Step 2: Prioritize Expenses**\n"
            "- **Essential**: Rent, utilities, groceries, minimum debt payments\n"
            "- **Important**: Insurance, savings, some entertainment\n"
            "- **Optional**: Dining out, subscriptions, shopping\n\n"
            "**Step 3: Build a Buffer**\n"
            "During high-income months, save extra to cover low-income months. "
            "Aim for 1-2 months of expenses in your checking account as a buffer.\n\n"
            "**Step 4: Use Zero-Based Budgeting**\n"
            "Every dollar has a job. When income arrives, allocate it immediately to your priorities."
        ),
        "persona_ids": [2],
        "tags": ["budgeting", "variable income", "planning"],
    },
    {
        "id": "edu_005",
        "title": "Building Your Cash Flow Buffer",
        "content": (
            "A cash flow buffer protects you from income variability.\n\n"
            "**What is it?**: Money set aside to cover expenses during low-income months.\n\n"
            "**How much?**: Aim for 1-2 months of essential expenses. "
            "If your monthly essentials are $2,000, target $2,000-$4,000 in your buffer.\n\n"
            "**Where to keep it**: A high-yield savings account that's separate from your emergency fund. "
            "This is your 'income smoothing' account.\n\n"
            "**How to build it**: During high-income months, transfer extra to your buffer. "
            "During low-income months, withdraw from it to cover essentials. "
            "This creates stability even with variable income."
        ),
        "persona_ids": [2],
        "tags": ["cash flow", "savings", "variable income"],
    },
    {
        "id": "edu_006",
        "title": "Emergency Fund vs. Cash Flow Buffer",
        "content": (
            "These are two different financial tools:\n\n"
            "**Emergency Fund**: For unexpected expenses (car repair, medical bill, job loss). "
            "Typically 3-6 months of expenses. Keep this separate and don't touch it except for true emergencies.\n\n"
            "**Cash Flow Buffer**: For income variability. "
            "If your income is irregular, you need 1-2 months of expenses to smooth out low-income months. "
            "You'll actively use this month-to-month.\n\n"
            "**Both are important**: The emergency fund protects against unexpected expenses. "
            "The cash flow buffer protects against expected income swings. "
            "Variable income earners need both."
        ),
        "persona_ids": [2],
        "tags": ["emergency fund", "cash flow", "savings"],
    },

    # Persona 3: Subscription-Heavy
    {
        "id": "edu_007",
        "title": "Subscription Audit Checklist",
        "content": (
            "Review your subscriptions regularly to avoid 'subscription creep':\n\n"
            "**Step 1: List Everything**\n"
            "Streaming services, software, apps, memberships, box subscriptions, etc.\n\n"
            "**Step 2: Rate Each One**\n"
            "- **Essential**: You use it weekly and couldn't live without it\n"
            "- **Useful**: You use it monthly and get value\n"
            "- **Questionable**: You use it rarely or forgot you have it\n\n"
            "**Step 3: Calculate Monthly Cost**\n"
            "Add up all your subscriptions. Multiply by 12 for annual cost. "
            "Many people are surprised by the total!\n\n"
            "**Step 4: Cut the Questionable Ones**\n"
            "Cancel anything you rated 'questionable'. You can always resubscribe later if you miss it.\n\n"
            "**Step 5: Set a Review Reminder**\n"
            "Review subscriptions quarterly. They add up quickly!"
        ),
        "persona_ids": [3],
        "tags": ["subscriptions", "saving money", "budgeting"],
    },
    {
        "id": "edu_008",
        "title": "The Hidden Cost of 'Just $9.99' Subscriptions",
        "content": (
            "Small subscriptions add up faster than you think.\n\n"
            "**The Math**: 10 subscriptions at $9.99/month = $100/month = $1,200/year.\n\n"
            "**The Problem**: It's easy to sign up for 'just $9.99' but hard to cancel. "
            "Many people don't realize how much they're spending until they audit.\n\n"
            "**Action Steps**:\n"
            "1. Track every subscription (check bank statements)\n"
            "2. Cancel any you haven't used in 30 days\n"
            "3. Share accounts with family/friends when possible\n"
            "4. Use annual billing when it saves money (but only if you'll use it all year)\n"
            "5. Set a monthly subscription budget (e.g., $50/month max)\n\n"
            "Small cuts add up to big savings."
        ),
        "persona_ids": [3],
        "tags": ["subscriptions", "saving money", "budgeting"],
    },
    {
        "id": "edu_009",
        "title": "Subscription Management Tools",
        "content": (
            "Several tools can help you track and manage subscriptions:\n\n"
            "**Bobby**: Tracks subscriptions, sends renewal reminders, shows total monthly cost.\n\n"
            "**Truebill**: Tracks subscriptions, helps negotiate bills, identifies recurring charges.\n\n"
            "**Mint/YNAB**: Budgeting apps that categorize subscriptions automatically.\n\n"
            "**Manual Tracking**: Create a simple spreadsheet with subscription name, monthly cost, "
            "renewal date, and last used date.\n\n"
            "**Pro Tip**: Use your bank's automatic categorization to find subscriptions you forgot about. "
            "Look for recurring charges on your statements.\n\n"
            "The best tool is the one you'll actually use. Start simple, then upgrade if needed."
        ),
        "persona_ids": [3],
        "tags": ["subscriptions", "tools", "management"],
    },

    # Persona 4: Savings Builder
    {
        "id": "edu_010",
        "title": "Emergency Fund Calculator: How Much Do You Need?",
        "content": (
            "An emergency fund protects you from unexpected expenses.\n\n"
            "**How Much?**: 3-6 months of essential expenses.\n\n"
            "**Essential Expenses Include**:\n"
            "- Rent/mortgage\n"
            "- Utilities\n"
            "- Groceries\n"
            "- Insurance\n"
            "- Minimum debt payments\n"
            "- Transportation\n\n"
            "**Example**: If your monthly essentials are $3,000, your emergency fund target is $9,000-$18,000.\n\n"
            "**Where to Keep It**: High-yield savings account (separate from checking). "
            "It should be easily accessible but not too tempting to spend.\n\n"
            "**Build It Gradually**: Start with $1,000, then build to 1 month, then 3 months, then 6 months. "
            "Every bit helps!"
        ),
        "persona_ids": [4],
        "tags": ["emergency fund", "savings", "planning"],
    },
    {
        "id": "edu_011",
        "title": "High-Yield Savings Accounts: Where to Put Your Emergency Fund",
        "content": (
            "Not all savings accounts are created equal.\n\n"
            "**Traditional Savings**: Typically 0.01-0.05% APY. Your money barely grows.\n\n"
            "**High-Yield Savings**: Typically 4-5% APY (as of 2024). Your money grows significantly faster.\n\n"
            "**The Difference**: On a $10,000 emergency fund:\n"
            "- Traditional: $10-50/year in interest\n"
            "- High-yield: $400-500/year in interest\n\n"
            "**Where to Find Them**: Online banks like Ally, Marcus, Discover, Capital One offer high-yield savings. "
            "They're FDIC-insured and easy to open.\n\n"
            "**Pro Tip**: Keep your emergency fund separate from your checking account. "
            "Out of sight, out of mind, but still accessible in emergencies."
        ),
        "persona_ids": [4],
        "tags": ["savings", "high-yield", "emergency fund"],
    },
    {
        "id": "edu_012",
        "title": "Automating Your Savings: Set It and Forget It",
        "content": (
            "Automation is the secret to consistent savings.\n\n"
            "**How It Works**: Set up automatic transfers from checking to savings on payday. "
            "You'll save before you have a chance to spend.\n\n"
            "**Start Small**: Even $25/week = $1,300/year. Start with an amount you won't miss.\n\n"
            "**Increase Gradually**: Every 3-6 months, increase your automatic transfer by $25-50. "
            "You'll barely notice, but your savings will grow.\n\n"
            "**Make It Conditional**: Use your bank's 'round up' feature to save spare change, "
            "or set up transfers for specific triggers (e.g., when your balance exceeds a threshold).\n\n"
            "**The Goal**: Make saving automatic so you don't have to think about it. "
            "The best savings plan is the one you'll stick to."
        ),
        "persona_ids": [4],
        "tags": ["savings", "automation", "habits"],
    },

    # Persona 5: Custom (general recommendations)
    {
        "id": "edu_013",
        "title": "Understanding Your Credit Score",
        "content": (
            "Your credit score affects loans, insurance rates, and even job applications.\n\n"
            "**What Affects It**:\n"
            "- Payment history (35%): Pay on time, every time\n"
            "- Credit utilization (30%): Keep balances low\n"
            "- Credit history length (15%): Older accounts help\n"
            "- Credit mix (10%): Different types of credit\n"
            "- New credit inquiries (10%): Limit hard pulls\n\n"
            "**How to Improve**: Pay bills on time, keep utilization below 30%, "
            "don't close old accounts, use credit responsibly.\n\n"
            "**Check Regularly**: Many banks offer free credit score monitoring. "
            "Check your credit report annually at annualcreditreport.com (free)."
        ),
        "persona_ids": [5],
        "tags": ["credit score", "credit", "general"],
    },
    {
        "id": "edu_014",
        "title": "Basic Budgeting: The 50/30/20 Rule",
        "content": (
            "A simple budgeting framework that works for many people:\n\n"
            "**50% Needs**: Essential expenses like rent, utilities, groceries, insurance, minimum debt payments.\n\n"
            "**30% Wants**: Non-essential expenses like dining out, entertainment, subscriptions, shopping.\n\n"
            "**20% Savings**: Emergency fund, retirement, debt payoff beyond minimums.\n\n"
            "**Example**: If you earn $4,000/month:\n"
            "- Needs: $2,000\n"
            "- Wants: $1,200\n"
            "- Savings: $800\n\n"
            "**Adjust as Needed**: This is a starting point. Adjust percentages based on your situation. "
            "The key is spending intentionally, not impulsively."
        ),
        "persona_ids": [5],
        "tags": ["budgeting", "general", "planning"],
    },
]

# Partner offers catalog
# Each offer has: id, title, content, persona_ids, eligibility_requirements
PARTNER_OFFER_CATALOG: List[Dict[str, Any]] = [
    # Persona 1: High Utilization
    {
        "id": "offer_001",
        "title": "Balance Transfer Credit Card - 0% APR for 18 Months",
        "content": (
            "Transfer high-interest credit card debt to a card with 0% APR for 18 months. "
            "This can save hundreds or thousands in interest charges while you pay down debt.\n\n"
            "**Benefits**:\n"
            "- 0% APR on balance transfers for 18 months\n"
            "- No annual fee\n"
            "- Helps consolidate debt\n\n"
            "**Important**: Pay off the balance before the promotional period ends. "
            "Don't use the card for new purchases during the promotional period.\n\n"
            "**Eligibility**: Requires good credit score (typically 670+)."
        ),
        "persona_ids": [1],
        "eligibility_requirements": {
            "min_credit_score": 670,
            "min_income": None,
            "existing_products": ["credit_card"],  # User should have existing credit cards
            "blocked_if": [],  # No blocking conditions
        },
        "tags": ["balance transfer", "credit card", "debt"],
    },

    # Persona 2: Variable Income Budgeter
    {
        "id": "offer_002",
        "title": "Budgeting App Premium - Free Trial",
        "content": (
            "Get 3 months free of premium budgeting app features designed for variable income earners.\n\n"
            "**Features**:\n"
            "- Variable income budgeting tools\n"
            "- Cash flow forecasting\n"
            "- Income smoothing recommendations\n"
            "- Expense categorization\n\n"
            "**Perfect For**: Freelancers, contractors, commission-based workers, or anyone with irregular income.\n\n"
            "**No Credit Check Required**: Sign up with email and link your bank account (bank-level security)."
        ),
        "persona_ids": [2],
        "eligibility_requirements": {
            "min_credit_score": None,
            "min_income": None,
            "existing_products": [],
            "blocked_if": [],
        },
        "tags": ["budgeting", "app", "variable income"],
    },

    # Persona 3: Subscription-Heavy
    {
        "id": "offer_003",
        "title": "Subscription Management Tool - Free Premium Plan",
        "content": (
            "Track and manage all your subscriptions in one place with a free premium subscription.\n\n"
            "**Features**:\n"
            "- Automatic subscription detection\n"
            "- Renewal reminders\n"
            "- Total monthly cost tracking\n"
            "- Easy cancellation links\n"
            "- Price drop alerts\n\n"
            "**Perfect For**: Anyone with multiple subscriptions who wants to save money and avoid surprise charges.\n\n"
            "**Sign Up**: Link your bank accounts securely (bank-level encryption). No credit check required."
        ),
        "persona_ids": [3],
        "eligibility_requirements": {
            "min_credit_score": None,
            "min_income": None,
            "existing_products": [],
            "blocked_if": [],
        },
        "tags": ["subscriptions", "management", "tools"],
    },

    # Persona 4: Savings Builder
    {
        "id": "offer_004",
        "title": "High-Yield Savings Account - 4.5% APY",
        "content": (
            "Open a high-yield savings account with 4.5% APY (as of 2024). "
            "FDIC-insured up to $250,000.\n\n"
            "**Benefits**:\n"
            "- 4.5% APY (vs. 0.01% at traditional banks)\n"
            "- No minimum balance\n"
            "- No monthly fees\n"
            "- Easy online access\n"
            "- FDIC-insured\n\n"
            "**Example**: On a $10,000 balance, you'll earn $450/year in interest "
            "(vs. $1 at a traditional bank).\n\n"
            "**Perfect For**: Emergency funds, short-term savings goals, cash flow buffers.\n\n"
            "**Eligibility**: No credit check required. Just link your bank account."
        ),
        "persona_ids": [4],
        "eligibility_requirements": {
            "min_credit_score": None,
            "min_income": None,
            "existing_products": [],  # Check if user already has high-yield savings
            "blocked_if": ["high_yield_savings"],  # Don't offer if they already have one
        },
        "tags": ["savings", "high-yield", "emergency fund"],
    },
    {
        "id": "offer_005",
        "title": "Automated Savings App - Round-Up Feature",
        "content": (
            "Automatically save spare change from everyday purchases.\n\n"
            "**How It Works**:\n"
            "- Link your debit card\n"
            "- Every purchase rounds up to the nearest dollar\n"
            "- Spare change goes to savings automatically\n"
            "- Example: Buy coffee for $4.75, $0.25 goes to savings\n\n"
            "**Benefits**:\n"
            "- Save without thinking about it\n"
            "- Small amounts add up over time\n"
            "- Can save $200-500/year automatically\n"
            "- No minimums or fees\n\n"
            "**Perfect For**: Anyone who wants to save but struggles with discipline.\n\n"
            "**Sign Up**: Link your bank account securely. No credit check required."
        ),
        "persona_ids": [4],
        "eligibility_requirements": {
            "min_credit_score": None,
            "min_income": None,
            "existing_products": [],
            "blocked_if": [],
        },
        "tags": ["savings", "automation", "round-up"],
    },

    # Persona 5: Custom (general offers)
    {
        "id": "offer_006",
        "title": "Credit Monitoring Service - Free Credit Score",
        "content": (
            "Monitor your credit score and credit report for free.\n\n"
            "**Features**:\n"
            "- Free credit score updates\n"
            "- Credit report monitoring\n"
            "- Identity theft protection\n"
            "- Credit score improvement tips\n\n"
            "**Perfect For**: Anyone who wants to understand and improve their credit.\n\n"
            "**Sign Up**: Create account with email. No credit check required."
        ),
        "persona_ids": [5],
        "eligibility_requirements": {
            "min_credit_score": None,
            "min_income": None,
            "existing_products": [],
            "blocked_if": [],
        },
        "tags": ["credit score", "monitoring", "general"],
    },
]

# Regulatory disclaimer text
REGULATORY_DISCLAIMER = (
    "**Disclaimer**: This is educational content, not financial advice. "
    "Consult a licensed financial advisor for personalized guidance."
)



