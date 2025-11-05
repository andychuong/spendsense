# User Types Quick Reference

## User Roles (3 Types)

### USER (Regular End User)
- **Default role** for all new registrations
- Gets **behavioral persona** assigned (1-5)
- Can access own data, upload files, view recommendations
- Cannot access operator/admin endpoints

### OPERATOR (Platform Operator)
- Bank employees/advisors who review recommendations
- Can view all user data (with consent)
- Can approve/reject recommendations
- Can view analytics
- **No persona assigned** (not an end user)

### ADMIN (System Administrator)
- Full system access
- Can manage user roles
- Can view all data (with consent)
- Can access admin endpoints
- **No persona assigned** (not an end user)

---

## Behavioral Personas (5 Types)

### Persona 1: High Utilization
- **Criteria**: Utilization ≥50% OR interest charges OR minimum payments OR overdue
- **Priority**: Highest (checked first)

### Persona 2: Variable Income Budgeter
- **Criteria**: Median pay gap >45 days AND cash-flow buffer <1 month
- **Priority**: Second

### Persona 3: Subscription-Heavy
- **Criteria**: ≥3 subscriptions AND (≥$50/month OR ≥10% of spending)
- **Priority**: Third

### Persona 4: Savings Builder
- **Criteria**: Savings growth ≥2% OR inflow ≥$200/month AND all utilizations <30%
- **Priority**: Fourth

### Persona 5: Custom Persona
- **Criteria**: Default fallback (doesn't match 1-4)
- **Priority**: Lowest

---

## Quick Facts

- **3 Roles**: USER, OPERATOR, ADMIN
- **5 Personas**: High Utilization, Variable Income, Subscription-Heavy, Savings Builder, Custom
- **Only USER role gets personas** (operators/admins don't)
- **Persona assignment is automatic** based on financial behavior
- **Role assignment is manual** (registration or admin action)



