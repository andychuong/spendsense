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
    {
        "id": "edu_015",
        "title": "Setting Financial Goals: Short, Mid, and Long-Term",
        "content": (
            "Setting clear financial goals is the first step toward achieving them.\n\n"
            "**Short-Term Goals (1-12 months)**:\n"
            "- Build a starter emergency fund ($1,000)\n"
            "- Pay off a small credit card balance\n"
            "- Save for a weekend trip\n\n"
            "**Mid-Term Goals (1-5 years)**:\n"
            "- Save for a down payment on a car\n"
            "- Build a 3-6 month emergency fund\n"
            "- Pay off student loans\n\n"
            "**Long-Term Goals (5+ years)**:\n"
            "- Save for a down payment on a house\n"
            "- Invest for retirement\n"
            "- Save for a child's education\n\n"
            "**Pro Tip**: Use the SMART goals framework: Specific, Measurable, Achievable, Relevant, Time-bound. "
            "Write down your goals and track your progress!"
        ),
        "persona_ids": [5],
        "tags": ["financial goals", "planning", "general"],
    },
    
    # Category-Based Recommendations: Food & Dining
    {
        "id": "edu_016",
        "title": "Smart Grocery Shopping: Save $200+/Month",
        "content": (
            "Groceries are one of the easiest places to cut costs without sacrificing quality.\n\n"
            "**Plan Before You Shop**:\n"
            "- Make a weekly meal plan and shopping list\n"
            "- Never shop hungry (you'll buy 40% more!)\n"
            "- Check your pantry first to avoid duplicates\n\n"
            "**Smart Shopping Strategies**:\n"
            "- Buy store brands (often 30-50% cheaper, same quality)\n"
            "- Use cash-back apps like Ibotta or Fetch\n"
            "- Shop sales and buy in bulk for non-perishables\n"
            "- Choose frozen vegetables (just as nutritious, less waste)\n\n"
            "**Meal Prep**: Cooking at home saves $10-15 per meal vs. dining out. "
            "Prep 3-4 meals on Sunday to reduce weeknight takeout temptation.\n\n"
            "**Expert Tip**: Food should be 10-15% of your income. If you're spending more, start with one change at a time."
        ),
        "persona_ids": [5],
        "tags": ["food", "groceries", "budgeting", "savings"],
    },
    {
        "id": "edu_017",
        "title": "Dining Out Without Breaking the Bank",
        "content": (
            "You can enjoy restaurants and save money with smart strategies:\n\n"
            "**Set a Monthly Dining Budget**: Experts recommend keeping dining out to 5-7% of take-home pay. "
            "For a $4,000/month income, that's $200-280.\n\n"
            "**Money-Saving Tactics**:\n"
            "- Order water instead of drinks (saves $3-5 per person)\n"
            "- Split entrees or take half home\n"
            "- Look for restaurant week deals or lunch specials\n"
            "- Use credit card dining rewards (4% back adds up!)\n\n"
            "**The 50/50 Rule**: For every restaurant meal, eat one meal at home. "
            "This naturally reduces dining costs by half.\n\n"
            "**Coffee Shop Savings**: That daily $5 coffee is $1,825/year. "
            "Make coffee at home 3-4 days/week and save $1,000+/year."
        ),
        "persona_ids": [5],
        "tags": ["dining", "restaurants", "budgeting"],
    },
    {
        "id": "edu_018",
        "title": "Meal Prep 101: Your Secret Weapon Against Overspending",
        "content": (
            "Meal prep is the single best way to reduce food spending.\n\n"
            "**The Math**: Home-cooked meal = $3-5. Restaurant meal = $12-20. "
            "Prep 10 meals on Sunday and save $90-150/week!\n\n"
            "**Easy Meal Prep Strategy**:\n"
            "1. Choose 3-4 simple recipes (Pinterest or YouTube)\n"
            "2. Shop once for all ingredients\n"
            "3. Spend 2-3 hours Sunday cooking and portioning\n"
            "4. Store in containers (invest in good ones!)\n\n"
            "**Beginner-Friendly Meals**:\n"
            "- Chicken and rice bowls (add different vegetables)\n"
            "- Pasta with marinara (make large batch)\n"
            "- Chili or soup (freezes well)\n"
            "- Breakfast burritos (freeze individually)\n\n"
            "**Pro Tip**: Start small! Prep lunch only for first 2 weeks. Build the habit before adding dinner."
        ),
        "persona_ids": [5],
        "tags": ["meal prep", "cooking", "budgeting", "food"],
    },
    
    # Category-Based Recommendations: Transportation
    {
        "id": "edu_019",
        "title": "Transportation Costs: Are You Spending Too Much?",
        "content": (
            "Transportation should be 10-15% of your income maximum.\n\n"
            "**Total Transportation Costs Include**:\n"
            "- Car payment or lease\n"
            "- Gas and maintenance\n"
            "- Insurance\n"
            "- Parking fees\n"
            "- Registration and taxes\n\n"
            "**The 20/4/10 Rule for Car Buying**:\n"
            "- 20% down payment\n"
            "- 4-year loan maximum\n"
            "- Total monthly payment < 10% of gross income\n\n"
            "**Cost-Cutting Strategies**:\n"
            "- Bundle insurance policies for discounts (10-25% savings)\n"
            "- Pay insurance annually instead of monthly (save $50-100/year)\n"
            "- Regular maintenance prevents costly repairs\n"
            "- Use GasBuddy app to find cheapest gas\n\n"
            "**Consider**: If transportation is >15% of income, explore alternatives like public transit, carpooling, or downsizing your vehicle."
        ),
        "persona_ids": [5],
        "tags": ["transportation", "car", "budgeting", "expenses"],
    },
    {
        "id": "edu_020",
        "title": "Public Transit: The $5,000/Year Savings Option",
        "content": (
            "AAA estimates the average cost of car ownership at $12,000+/year. Public transit can slash that dramatically.\n\n"
            "**Annual Cost Comparison**:\n"
            "- Car ownership: $12,000+ (payment, insurance, gas, maintenance)\n"
            "- Monthly transit pass: $600-1,200/year\n"
            "- Savings: $10,000+/year!\n\n"
            "**Making Transit Work**:\n"
            "- Use transit apps for real-time schedules\n"
            "- Combine transit with bike sharing for first/last mile\n"
            "- Ask employer about commuter benefits (pre-tax transit spending)\n"
            "- Use rideshare only for late nights or heavy cargo\n\n"
            "**Not Fully Feasible?**: Hybrid approach works too:\n"
            "- Transit for commute, car share for weekends\n"
            "- Carpool 2-3 days/week (split gas costs)\n"
            "- Work from home when possible\n\n"
            "**Calculate Your Savings**: Use AAA's Driving Costs calculator to see your real car ownership cost, then compare to transit."
        ),
        "persona_ids": [5],
        "tags": ["transportation", "public transit", "savings"],
    },
    
    # Category-Based Recommendations: Shopping
    {
        "id": "edu_021",
        "title": "The 30-Day Rule: Stop Impulse Buying",
        "content": (
            "Impulse purchases are budget killers. The 30-day rule helps you buy intentionally.\n\n"
            "**How It Works**:\n"
            "1. See something you want? Don't buy it yet.\n"
            "2. Add it to a 'wish list' with the date\n"
            "3. Wait 30 days (24 hours for items under $50)\n"
            "4. After waiting, if you still want it AND it fits your budget, buy it\n\n"
            "**Why It Works**: Most impulse purchases lose appeal within days. "
            "Studies show 80% of wish-listed items are never purchased.\n\n"
            "**Bonus Strategies**:\n"
            "- Unsubscribe from marketing emails (reduces temptation)\n"
            "- Delete shopping apps from your phone\n"
            "- Use cash for discretionary spending (physical pain of spending)\n"
            "- Calculate cost in 'hours worked' (Is this worth 6 hours of work?)\n\n"
            "**Expert Tip**: Shopping should be 5-10% of income. Track it monthly to stay within budget."
        ),
        "persona_ids": [5],
        "tags": ["shopping", "impulse buying", "budgeting"],
    },
    {
        "id": "edu_022",
        "title": "Buy It Right: Quality vs. Cheap",
        "content": (
            "Sometimes spending more upfront saves money long-term.\n\n"
            "**The Cost Per Use Formula**: Price ÷ Number of Uses = Real Cost\n"
            "- $50 shoes worn 200 times = $0.25/use\n"
            "- $20 shoes worn 30 times = $0.67/use\n\n"
            "**When to Buy Quality**:\n"
            "- Items you use daily (shoes, work clothes, mattress)\n"
            "- Tools and appliances (better warranty, longer life)\n"
            "- Safety equipment (car seats, helmets)\n\n"
            "**When Cheap is Fine**:\n"
            "- Trendy items you'll wear once\n"
            "- Kids' clothes (they outgrow them fast)\n"
            "- Occasional-use items\n\n"
            "**Smart Shopping**:\n"
            "- Buy quality items secondhand (thrift stores, Poshmark, eBay)\n"
            "- Wait for sales on quality brands (sign up for alerts)\n"
            "- Check Buy It For Life subreddit for product recommendations\n\n"
            "**The Sweet Spot**: Invest in quality for things you use every day, save on everything else."
        ),
        "persona_ids": [5],
        "tags": ["shopping", "quality", "budgeting", "value"],
    },
    
    # Category-Based Recommendations: Entertainment
    {
        "id": "edu_023",
        "title": "Entertainment on a Budget: Still Have Fun, Save Money",
        "content": (
            "Entertainment should be 5-10% of your budget. You can have fun without overspending!\n\n"
            "**Free Entertainment Options**:\n"
            "- Public libraries (books, movies, events, museum passes)\n"
            "- Community events (concerts, festivals, farmers markets)\n"
            "- Parks and hiking trails (exercise + entertainment)\n"
            "- Free museum days (most cities have them monthly)\n"
            "- Game nights with friends at home\n\n"
            "**Subscription Audit**: The average person spends $270/month on subscriptions!\n"
            "- Netflix, Hulu, Disney+, HBO, Peacock, Apple TV ($80/month)\n"
            "- Spotify, Apple Music, Audible ($35/month)\n"
            "- Gaming subscriptions ($30/month)\n"
            "**Action**: Cancel what you haven't used in 30 days. Rotate subscriptions monthly.\n\n"
            "**Low-Cost Entertainment**:\n"
            "- Matinee movies instead of evening ($8 vs $15)\n"
            "- Happy hour instead of dinner ($10 vs $40)\n"
            "- Streaming sports at home with friends instead of bars\n\n"
            "**The Challenge**: Go one month trying only free entertainment. You'll find activities you love!"
        ),
        "persona_ids": [5],
        "tags": ["entertainment", "budgeting", "subscriptions", "savings"],
    },
    {
        "id": "edu_024",
        "title": "Subscription Creep: The Silent Budget Killer",
        "content": (
            "The average American spends $270/month on subscriptions but thinks they spend $86. Sound familiar?\n\n"
            "**Common Subscriptions to Audit**:\n"
            "- Streaming services (Netflix, Hulu, Disney+, HBO, Apple TV, Prime Video)\n"
            "- Music/Audio (Spotify, Apple Music, Audible, Podcasts)\n"
            "- Software (Adobe, Microsoft, Dropbox, VPNs)\n"
            "- Fitness (gym, fitness apps, online classes)\n"
            "- Food delivery (DashPass, Uber Eats+)\n"
            "- Gaming (Xbox Live, PlayStation Plus, Nintendo Online)\n\n"
            "**The 90-Day Audit**:\n"
            "1. List ALL subscriptions (check bank/credit card statements)\n"
            "2. Cancel anything you haven't used in 60 days\n"
            "3. Keep only 3-5 you actively use\n"
            "4. Share subscriptions with family (most allow multiple profiles)\n"
            "5. Rotate streaming services monthly (binge, cancel, switch)\n\n"
            "**Annual Subscriptions**: Often 20-30% cheaper than monthly, but ONLY if you'll use it all year.\n\n"
            "**Goal**: Get subscriptions under $100/month. Reallocate savings to debt payoff or emergency fund."
        ),
        "persona_ids": [3, 5],
        "tags": ["subscriptions", "budgeting", "entertainment", "savings"],
    },
    
    # Category-Based Recommendations: Bills & Utilities
    {
        "id": "edu_025",
        "title": "Lower Your Utility Bills: Easy Wins",
        "content": (
            "Small changes to utility usage can save $50-150/month.\n\n"
            "**Electricity Savings**:\n"
            "- LED bulbs (save $75/year per bulb vs incandescent)\n"
            "- Smart thermostat (saves 10-12% on heating/cooling, $130/year)\n"
            "- Unplug vampire devices (chargers, appliances on standby = 10% of bill)\n"
            "- Adjust thermostat 7-10°F for 8 hours/day (saves 10%/year)\n\n"
            "**Water Savings**:\n"
            "- Fix leaky faucets (saves 3,000 gallons/year)\n"
            "- Low-flow showerheads ($20, saves $70/year)\n"
            "- Run dishwasher/laundry only when full\n\n"
            "**Internet/Phone**:\n"
            "- Call and negotiate (mention competitor prices, ask for retention deals)\n"
            "- Remove cable, keep internet (save $50-100/month)\n"
            "- Use WiFi calling instead of unlimited plans\n\n"
            "**Annual Savings**: Implementing all strategies = $1,000+/year!\n\n"
            "**Pro Tip**: Set a calendar reminder annually to call providers and negotiate. "
            "Competition for customers means deals are always available."
        ),
        "persona_ids": [5],
        "tags": ["utilities", "bills", "savings", "budgeting"],
    },
    {
        "id": "edu_026",
        "title": "The Art of Negotiating Bills",
        "content": (
            "You can negotiate almost any bill. Companies would rather give you a discount than lose you as a customer.\n\n"
            "**What You Can Negotiate**:\n"
            "- Internet/cable ($20-50/month savings)\n"
            "- Cell phone plans ($10-30/month)\n"
            "- Car insurance ($200-500/year)\n"
            "- Credit card APR and fees\n"
            "- Gym memberships\n\n"
            "**The Script**:\n"
            "1. 'I've been a loyal customer for [X years]'\n"
            "2. 'I'm reviewing my expenses and your service is expensive'\n"
            "3. 'I saw [competitor] offers [service] for $[lower price]'\n"
            "4. 'Can you match or beat that price to keep my business?'\n"
            "5. If no: 'Can I speak to your retention department?'\n\n"
            "**Best Times to Negotiate**:\n"
            "- When promotional pricing expires\n"
            "- Before contract renewal\n"
            "- After seeing competitor ads\n\n"
            "**Services That Do It For You**: BillShark, Truebill, Rocket Money (take 30-50% of savings, but hands-off).\n\n"
            "**Goal**: Negotiate 3 bills this quarter and save $500+/year."
        ),
        "persona_ids": [5],
        "tags": ["negotiation", "bills", "savings", "utilities"],
    },
    
    # Category-Based Recommendations: Healthcare
    {
        "id": "edu_027",
        "title": "Healthcare Costs: Save on Medical Expenses",
        "content": (
            "Healthcare costs are rising, but smart strategies can reduce your burden.\n\n"
            "**Preventive Care is Free**: ACA requires insurance to cover preventive care at 100%:\n"
            "- Annual physical exam\n"
            "- Vaccinations\n"
            "- Cancer screenings\n"
            "- Blood pressure and cholesterol tests\n"
            "Use it! Prevention is cheaper than treatment.\n\n"
            "**Prescription Savings**:\n"
            "- Ask for generic (50-80% cheaper, same active ingredient)\n"
            "- Use GoodRx or RxSaver (find lowest pharmacy prices)\n"
            "- 90-day supply vs 30-day (often cheaper per dose)\n"
            "- Manufacturer coupons (check drug website)\n\n"
            "**HSA/FSA Accounts**: Use pre-tax dollars for medical expenses:\n"
            "- HSA: You own it forever, grows tax-free\n"
            "- FSA: Use it or lose it annually\n"
            "Both save 20-30% on medical costs via tax savings.\n\n"
            "**Negotiate Medical Bills**: Call billing department, ask for:\n"
            "- Itemized bill (catches errors)\n"
            "- Financial assistance (many hospitals offer it)\n"
            "- Payment plan (often interest-free)"
        ),
        "persona_ids": [5],
        "tags": ["healthcare", "medical", "savings", "insurance"],
    },
    
    # Category-Based Recommendations: Housing
    {
        "id": "edu_028",
        "title": "The 28% Rule: Are You House Poor?",
        "content": (
            "Financial experts recommend spending no more than 28% of gross income on housing.\n\n"
            "**Total Housing Costs Include**:\n"
            "- Rent or mortgage payment\n"
            "- Property taxes\n"
            "- Homeowners insurance\n"
            "- HOA fees\n"
            "- Maintenance and repairs (budget 1-2% of home value annually)\n"
            "- Utilities (sometimes)\n\n"
            "**Example**: $5,000/month gross income → $1,400/month maximum housing\n\n"
            "**Spending More Than 28%?** You might be 'house poor'. Options:\n"
            "- Refinance mortgage (if rates are lower)\n"
            "- Challenge property tax assessment (could save hundreds)\n"
            "- Shop insurance annually (save $200-500/year)\n"
            "- Get a roommate (cut rent/mortgage in half)\n"
            "- Rent out a room on Airbnb (side income)\n\n"
            "**Renters**: Negotiate rent at renewal:\n"
            "- Research comparable units\n"
            "- Highlight your reliability as tenant\n"
            "- Offer to sign longer lease for discount\n"
            "- Be willing to walk away\n\n"
            "**Long-Term**: If housing >30% of income, consider downsizing or relocating to more affordable area."
        ),
        "persona_ids": [5],
        "tags": ["housing", "rent", "mortgage", "budgeting"],
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
    {
        "id": "offer_001b",
        "title": "Debt Consolidation Loan - Fixed Rate",
        "content": (
            "Consolidate multiple high-interest debts into a single loan with a fixed monthly payment. "
            "This can simplify your payments and potentially lower your overall interest rate.\n\n"
            "**Benefits**:\n"
            "- Fixed interest rate and monthly payment\n"
            "- Can be used for credit cards, personal loans, and medical debt\n"
            "- Potential to lower your total monthly payment\n\n"
            "**Important**: Make sure the new loan's interest rate is lower than the average rate of your current debts. "
            "Avoid using credit cards after consolidating.\n\n"
            "**Eligibility**: Requires fair to good credit score (typically 640+)."
        ),
        "persona_ids": [1],
        "eligibility_requirements": {
            "min_credit_score": 640,
            "min_income": 2500,  # Example: $30k/year
            "existing_products": ["credit_card"],  # User should have existing credit cards
            "blocked_if": [],
        },
        "tags": ["debt consolidation", "loan", "debt"],
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
            "Monitor your credit score and credit report for free. Stay on top of your credit health with regular updates and alerts.\n\n"
            "**What You Get**:\n"
            "- Free credit score updates\n"
            "- Credit report monitoring\n"
            "- Identity theft protection\n"
            "- Credit score improvement tips\n\n"
            "**Who This Helps**: Anyone who wants to understand and improve their credit. No credit check required to sign up.\n\n"
            "**Getting Started**: Create a free account with your email. You'll get instant access to your credit score and personalized tips for improvement."
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

# Regulatory disclaimer text (removed - now handled by frontend only)



