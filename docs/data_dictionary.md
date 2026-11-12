# Data Dictionary

**Dataset Name:** Zorvio Customer Churn Dataset (Synthetic)  
**Timeframe:** 2024-01-01 to 2025-12-31  
**Notice:** All data is synthetically generated for educational purposes.

## 1. `customers.csv`
Core demographic and acquisition data for each customer. One row per customer.

| Column | Type | Description |
|---|---|---|
| `customer_id` | String | Unique identifier (UUID). |
| `signup_date` | Date | The date the customer first signed up. |
| `acquisition_channel` | String | How the customer found Zorvio (e.g., Organic Search, App Store). |
| `city` | String | Customer's city in India. |
| `city_tier` | String | Tier classification of the city (Tier 1, 2, 3). |
| `company_size_band` | String | E.g., 'Solo', '2-10', '11-50'. |

## 2. `subscriptions.csv`
Subscription lifecycle history. Note: Trial periods are excluded; this tracks paying customers.

| Column | Type | Description |
|---|---|---|
| `subscription_id` | String | Unique ID for the subscription. |
| `customer_id` | String | Foreign key to `customers`. |
| `plan` | String | 'Starter', 'Growth', or 'Scale'. |
| `billing_cycle` | String | 'Monthly' or 'Annual'. |
| `mrr` | Float | Monthly Recurring Revenue in INR. |
| `start_date` | Date | Date this specific subscription plan started. |
| `end_date` | Date | Date this subscription ended (NULL if active as of 2025-12-31). |
| `status` | String | 'Active', 'Canceled', or 'Past_Due' (failed payment). |
| `cancel_reason` | String | Self-reported reason for leaving (NULL if active or involuntary). |

## 3. `payments.csv`
Transaction history.

| Column | Type | Description |
|---|---|---|
| `payment_id` | String | Unique transaction ID. |
| `customer_id` | String | Foreign key to `customers`. |
| `payment_date` | Date | Date the charge was attempted. |
| `amount` | Float | Amount in INR. |
| `status` | String | 'Success' or 'Failed'. |

## 4. `usage_daily.csv`
Aggregated daily product usage logs. Only days with >0 activity are recorded.

| Column | Type | Description |
|---|---|---|
| `customer_id` | String | Foreign key to `customers`. |
| `date` | Date | The date of activity. |
| `sessions` | Integer | Number of distinct login sessions that day. |
| `session_minutes` | Integer | Total time spent in the app in minutes. |
| `feature_core_actions` | Integer | Counts of core action events. |
| `feature_collaboration` | Integer | Counts of collaboration feature events. |
| `failed_actions` | Integer | Count of errors or failed actions experienced. |

## 5. `support_tickets.csv`
Customer service interactions.

| Column | Type | Description |
|---|---|---|
| `ticket_id` | String | Unique ticket ID. |
| `customer_id` | String | Foreign key to `customers`. |
| `open_date` | Date | Date the ticket was created. |
| `close_date` | Date | Date the ticket was resolved (NULL if unresolved). |
| `category` | String | E.g., 'Billing', 'Technical', 'How-to'. |
| `status` | String | 'Open', 'Closed'. |

## 6. `marketing_spend.csv`
Aggregated monthly marketing expenditure by channel, allowing CAC estimation.

| Column | Type | Description |
|---|---|---|
| `month` | Date | First day of the month (YYYY-MM-01). |
| `channel` | String | Matches `acquisition_channel`. |
| `spend_inr` | Float | Total ad/marketing spend in INR for that month. |
