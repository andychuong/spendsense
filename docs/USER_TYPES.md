# User Types in SpendSense

This document explains the two main ways we categorize users in the SpendSense platform:

1. **User Roles** (RBAC - Authentication/Authorization)
2. **Behavioral Personas** (Data Analysis - Based on Financial Behavior)

---

## 1. User Roles (RBAC - Role-Based Access Control)

User roles control **what users can do** in the system - their permissions and access levels.

### Role Hierarchy

```
ADMIN (Level 3) > OPERATOR (Level 2) > USER (Level 1)
```

### Role 1: USER (Regular End User)

**Role Value**: `"user"`
**Default Role**: All new registrations start as `USER`

**Permissions**:
- ✅ Access own profile and data
- ✅ Upload transaction data
- ✅ View own recommendations
- ✅ Manage own consent settings
- ✅ View own behavioral signals
- ✅ View own persona assignment
- ✅ Access own dashboard
- ❌ Cannot access operator endpoints
- ❌ Cannot access admin endpoints
- ❌ Cannot view other users' data

**Use Cases**:
- Upload financial data
- View personalized recommendations
- Manage consent preferences
- View financial profile

**Database Storage**:
```sql
users.role = 'user'
```

---

### Role 2: OPERATOR (Platform Operator)

**Role Value**: `"operator"`
**Purpose**: Bank employees or financial advisors who review recommendations

**Permissions**:
- ✅ All USER permissions (for their own account)
- ✅ View all user data (must respect consent)
- ✅ Review recommendation queue
- ✅ Approve/reject recommendations
- ✅ View decision traces
- ✅ View analytics dashboard
- ✅ View any user's profile (with consent)
- ❌ Cannot access admin endpoints
- ❌ Cannot manage user roles
- ❌ Cannot access system configuration

**Special Rules**:
- Must respect user consent - cannot access data if user revoked consent
- Can view all recommendations (pending, approved, rejected)
- Can modify recommendations before approval
- Can view analytics and metrics

**Endpoints**:
- `GET /api/v1/operator/review` - Review queue
- `PUT /api/v1/operator/review/{id}` - Approve/reject recommendations
- `GET /api/v1/operator/analytics` - View analytics
- `GET /api/v1/operator/users/{user_id}` - View user details

**Database Storage**:
```sql
users.role = 'operator'
```

**Example Users**:
- Bank financial advisors
- Platform quality assurance team
- Compliance reviewers

---

### Role 3: ADMIN (System Administrator)

**Role Value**: `"admin"`
**Purpose**: System administrators with full access

**Permissions**:
- ✅ All OPERATOR permissions
- ✅ All USER permissions
- ✅ Manage user roles
- ✅ Access admin endpoints
- ✅ View system configuration
- ✅ Access audit logs
- ✅ Manage users (update roles, delete users)
- ✅ View all data (must respect consent)

**Special Rules**:
- Must respect user consent - cannot access data if user revoked consent
- Can change any user's role
- Can delete users
- Full system access

**Endpoints**:
- `GET /api/v1/operator/admin/users` - List all users
- `PUT /api/v1/operator/admin/users/{user_id}/role` - Update user role

**Database Storage**:
```sql
users.role = 'admin'
```

**Example Users**:
- System administrators
- Platform owners
- Technical leads

---

## 2. Behavioral Personas (Financial Behavior Analysis)

Behavioral personas are assigned to users based on their **financial behavior patterns**. These determine what recommendations they receive.

### Persona Assignment Priority

Personas are checked in priority order (1 → 2 → 3 → 4 → 5). If multiple personas match, the highest priority (lowest number) is assigned.

### Persona 1: High Utilization

**Persona ID**: `1`
**Priority**: Highest (checked first)

**Detection Criteria** (ANY of the following):
- Credit card utilization ≥50% OR
- Interest charges > 0 OR
- Minimum-payment-only behavior OR
- Overdue accounts (`is_overdue = true`)

**Example Signals**:
- Visa ending in 4523 at 68% utilization ($3,400 of $5,000 limit)
- Paying $87/month in interest charges
- Making minimum payments only
- Account overdue

**Recommendations**:
- Debt paydown strategies (Snowball vs. Avalanche)
- Credit utilization education
- Balance transfer credit card offers
- Interest charge reduction strategies

**Education Items**: 3 items
**Partner Offers**: 1 offer (balance transfer card)

---

### Persona 2: Variable Income Budgeter

**Persona ID**: `2`
**Priority**: Second (checked after Persona 1)

**Detection Criteria** (BOTH required):
- Median pay gap > 45 days AND
- Cash-flow buffer < 1 month

**Example Signals**:
- Median pay gap: 52 days
- Cash-flow buffer: 0.6 months
- Irregular income pattern
- Variable payment amounts

**Recommendations**:
- Variable income budget templates
- Cash flow buffer building strategies
- Emergency fund vs. cash flow buffer education
- Budgeting apps for variable income

**Education Items**: 3 items
**Partner Offers**: 1 offer (budgeting app)

---

### Persona 3: Subscription-Heavy

**Persona ID**: `3`
**Priority**: Third (checked after Persona 2)

**Detection Criteria** (ALL required):
- Recurring merchants ≥3 AND
- (Monthly recurring spend ≥$50 OR subscription share ≥10%)

**Example Signals**:
- 5 recurring subscriptions
- $125/month in recurring spend
- 15.2% of total spending on subscriptions
- Top subscriptions: Netflix, Spotify, Gym, etc.

**Recommendations**:
- Subscription audit checklists
- Subscription cost awareness education
- Subscription management tools
- Tips for reducing subscription costs

**Education Items**: 3 items
**Partner Offers**: 1 offer (subscription management tool)

---

### Persona 4: Savings Builder

**Persona ID**: `4`
**Priority**: Fourth (checked after Persona 3)

**Detection Criteria** (BOTH required):
- (Savings growth rate ≥2% OR net savings inflow ≥$200/month) AND
- All card utilizations < 30%

**Example Signals**:
- Savings growth rate: 3.5%
- Net monthly savings inflow: $250
- All credit cards below 30% utilization
- Building emergency fund

**Recommendations**:
- Emergency fund calculator
- High-yield savings account education
- Automated savings strategies
- Savings optimization tips

**Education Items**: 3 items
**Partner Offers**: 2 offers (high-yield savings, round-up app)

---

### Persona 5: Custom Persona

**Persona ID**: `5`
**Priority**: Lowest (default fallback)

**Assignment**:
- Assigned when user doesn't match any specific persona criteria
- Default fallback for new users without clear patterns
- General financial education recommendations

**Recommendations**:
- General credit score education
- Basic budgeting (50/30/20 rule)
- General financial wellness content

**Education Items**: 2 items (general)
**Partner Offers**: 1 offer (credit monitoring)

---

## User Type Matrix

| User Type | Role | Persona | Example |
|-----------|------|---------|---------|
| End User | USER | 1-5 | Regular customer with high credit utilization |
| End User | USER | 1-5 | Regular customer with subscription-heavy spending |
| Operator | OPERATOR | N/A | Bank employee reviewing recommendations |
| Admin | ADMIN | N/A | System administrator managing platform |

**Note**: Only `USER` role users get behavioral personas assigned. Operators and Admins don't have personas (they're for platform management).

---

## How Roles and Personas Interact

### For Regular Users (USER role):

1. **User registers** → Role = `USER`
2. **User uploads data** → System analyzes behavior
3. **System assigns persona** → Persona 1-5 based on signals
4. **System generates recommendations** → Based on assigned persona
5. **User views recommendations** → Personalized to their persona

### For Operators (OPERATOR role):

1. **Operator logs in** → Role = `OPERATOR`
2. **Operator reviews recommendations** → Can see all users' recommendations
3. **Operator approves/rejects** → Controls what users see
4. **No persona assigned** → Operators don't have personas

### For Admins (ADMIN role):

1. **Admin logs in** → Role = `ADMIN`
2. **Admin manages users** → Can change roles, view all data
3. **Admin views analytics** → System-wide metrics
4. **No persona assigned** → Admins don't have personas

---

## Database Storage

### User Roles (users table)

```sql
users.role = 'user' | 'operator' | 'admin'
```

### Behavioral Personas (user_profiles table)

```sql
user_profiles.persona_id = 1 | 2 | 3 | 4 | 5
user_profiles.persona_name = 'High Utilization' | 'Variable Income Budgeter' | 'Subscription-Heavy' | 'Savings Builder' | 'Custom Persona'
```

---

## Summary

**User Roles** (3 types):
- **USER**: Regular end users (get personas assigned)
- **OPERATOR**: Platform operators (review recommendations)
- **ADMIN**: System administrators (full access)

**Behavioral Personas** (5 types):
- **Persona 1**: High Utilization (highest priority)
- **Persona 2**: Variable Income Budgeter
- **Persona 3**: Subscription-Heavy
- **Persona 4**: Savings Builder
- **Persona 5**: Custom Persona (default fallback)

**Key Points**:
- All users have a role (USER, OPERATOR, or ADMIN)
- Only USER role users get behavioral personas assigned
- Personas determine what recommendations users receive
- Roles determine what actions users can perform
- Persona assignment is automatic based on financial behavior
- Role assignment is manual (via registration or admin action)



