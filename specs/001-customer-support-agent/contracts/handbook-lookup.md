# Handbook Lookup Tool Contract

**Date**: 2026-04-15  
**Reference**: [data-model.md](../data-model.md), [request-response.md](request-response.md)

---

## Overview

The handbook lookup tool is the mechanism by which the support agent accesses company policies. This contract defines how the tool is invoked, what it searches, and what results it returns.

---

## Tool Definition (MAF)

### Tool Name
`lookup_handbook_policy`

### Tool Description
Searches the support handbook for company policies matching a query. Used to ground agent responses in official policy, preventing hallucinated or invented rules.

### Tool Input Schema

```
{
  "query": "string (required, <200 chars)",
    description: "Search query or keywords, e.g., 'refund policy', 'billing', 'plan upgrade'",
  
  "context": {
    "intent": "string (optional)",
      description: "Customer intent for query ranking, e.g., 'refund', 'billing', 'feature_question'",
    "customer_entities": {
      "order_id": "string (optional)",
      "purchase_date": "string (optional, ISO format)",
      "charge_amount": "number (optional)",
      "plan_name": "string (optional)"
    }
  } (optional)
}
```

### Tool Output Schema

```
{
  "status": "success | not_found | error",
  "policies": [
    {
      "policy_id": "string",
      "section": "string",
      "title": "string",
      "content": "string (markdown)",
      "tags": ["string"],
      "relevance_score": "float (0.0-1.0)"
    }
  ],
  "search_explanation": "string"
    description: "Why these results were returned or why no results found"
}
```

---

## Handbook Structure

The handbook is stored in `data/support_handbook.md` (both Python and C# skeletons). It is structured as markdown sections, each section a policy or FAQ.

### Handbook Sections (Authoritative)

**Note**: The actual sections in skelton's `support_handbook.md` override these examples. **Tool must parse the actual file, not these templates.**

#### Section 1: Refund Policy
- Title: "30-Day Money-Back Guarantee"
- Keywords: refund, money-back, 30-day, return, full refund, non-refundable
- Content: Explains 30-day window, refund methods, non-refundable purchases (if any), process

#### Section 2: Cancellation Policy
- Title: "Subscription Cancellation"
- Keywords: cancel, cancellation, terminate, unsubscribe, final invoice
- Content: Explains immediate cancellation, final invoice, refund of remaining balance (if prorated), data retention/deletion

#### Section 3: Billing Patterns
- Title: "Charges & Billing Explained"
- Keywords: charge, billing, subscription renewal, monthly, feature fee, tax, duplicate, pending
- Content: Explains subscription renewal date, pro-rated charges, feature add-on fees, tax treatment, common false positives (e.g., "pending charges from payment processor consolidate after 48 hours")

#### Section 4: Plan Features
- Title: "Plans & Features"
- Keywords: plan, upgrade, downgrade, feature, limit, basic, pro, premium, enterprise
- Content: Describes available plans, feature comparison, upgrade/downgrade process, limits per plan

#### Section 5: Account Management
- Title: "Account & Login"
- Keywords: account, email, password, reset, change email, login, authentication, 2FA
- Content: Explains email change process, password reset, two-factor authentication

#### Section 6: General FAQs
- Title: "Frequently Asked Questions"
- Keywords: faq, how to, can I, do you, is it possible
- Content: Miscellaneous FAQs (e.g., "Can I have multiple accounts?", "Is my data encrypted/private?")

#### Section 7: Escalation Indicators (for internal use)
- Title: "Cases Requiring Human Review"
- Keywords: escalation, manual review, custom, exception, edge case, dispute
- Content: Describes when to escalate (custom contracts, billing disputes, repeated complaints, emotional escalation)

---

## Tool Implementation (Pseudo-Code)

### Python

```python
async def lookup_handbook_policy(query: str, context: Optional[Dict[str, Any]] = None) -> Dict:
    """
    Search handbook for matching policies.
    """
    # Load handbook from file
    handbook_path = "data/support_handbook.md"
    with open(handbook_path, "r") as f:
        handbook_content = f.read()
    
    # Parse sections (split by ## markdown headers)
    sections = parse_handbook_sections(handbook_content)
    
    # Score each section by relevance to query
    scored_sections = []
    for section in sections:
        relevance = score_relevance(query, section, context)
        if relevance > 0.5:  # Threshold
            scored_sections.append({
                "section": section,
                "relevance_score": relevance
            })
    
    # Sort by relevance, return top 3
    scored_sections.sort(key=lambda x: x["relevance_score"], reverse=True)
    policies = [s["section"] for s in scored_sections[:3]]
    
    if policies:
        return {
            "status": "success",
            "policies": policies,
            "search_explanation": f"Found {len(policies)} policy section(s) matching '{query}'"
        }
    else:
        return {
            "status": "not_found",
            "policies": [],
            "search_explanation": f"No handbook section matched query '{query}'. This issue may require human review."
        }

def parse_handbook_sections(content: str) -> List[Dict]:
    """
    Parse markdown sections from handbook.
    Returns list of {policy_id, section, title, content, tags}
    """
    sections = []
    current_section = None
    
    for line in content.split("\n"):
        if line.startswith("## "):
            # New section header
            title = line[3:].strip()
            current_section = {
                "policy_id": hashlib.md5(title.encode()).hexdigest()[:8],
                "section": "Unknown",  # Will infer from title
                "title": title,
                "content": "",
                "tags": extract_tags(title)
            }
            sections.append(current_section)
        elif current_section:
            current_section["content"] += line + "\n"
    
    return sections

def score_relevance(query: str, section: Dict, context: Optional[Dict]) -> float:
    """
    Score how relevant a section is to the query.
    Simple keyword matching; can be enhanced with embeddings.
    
    Returns 0.0-1.0
    """
    query_words = set(query.lower().split())
    title_words = set(section["title"].lower().split())
    tag_words = set(section["tags"])
    content_words = set(section["content"].lower().split())
    
    # Calculate overlap
    title_overlap = len(query_words & title_words) / len(query_words)
    tag_overlap = len(query_words & tag_words) / len(query_words) if query_words else 0
    content_overlap = len(query_words & content_words) / len(query_words) if query_words else 0
    
    # Weight title > tags > content
    relevance = (title_overlap * 0.6) + (tag_overlap * 0.3) + (content_overlap * 0.1)
    
    # Boost if context matches (e.g., intent=refund and section is Refund Policy)
    if context and context.get("intent") and context["intent"].lower() in section["title"].lower():
        relevance = min(1.0, relevance + 0.2)
    
    return relevance
```

### C#

```csharp
public class HandbookLookupTool
{
    public async Task<HandbookSearchResult> LookupPolicyAsync(
        string query, 
        HandbookContext? context = null)
    {
        // Load handbook from file
        var handbookPath = Path.Combine("data", "support_handbook.md");
        var handbookContent = await File.ReadAllTextAsync(handbookPath);
        
        // Parse sections
        var sections = ParseHandbookSections(handbookContent);
        
        // Score each section
        var scoredSections = sections
            .Select(s => new { Section = s, Score = ScoreRelevance(query, s, context) })
            .Where(x => x.Score > 0.5)
            .OrderByDescending(x => x.Score)
            .Take(3)
            .Select(x => x.Section)
            .ToList();
        
        if (scoredSections.Any())
        {
            return new HandbookSearchResult
            {
                Status = "success",
                Policies = scoredSections,
                SearchExplanation = $"Found {scoredSections.Count} policy section(s) matching '{query}'"
            };
        }
        else
        {
            return new HandbookSearchResult
            {
                Status = "not_found",
                Policies = new List<HandbookPolicy>(),
                SearchExplanation = $"No handbook section matched query '{query}'. This issue may require human review."
            };
        }
    }
    
    private List<HandbookPolicy> ParseHandbookSections(string content)
    {
        var sections = new List<HandbookPolicy>();
        HandbookPolicy? currentSection = null;
        
        foreach (var line in content.Split('\n'))
        {
            if (line.StartsWith("## "))
            {
                var title = line[3..].Trim();
                currentSection = new HandbookPolicy
                {
                    PolicyId = title.GetHashCode().ToString(),
                    Section = "Unknown",
                    Title = title,
                    Content = "",
                    Tags = ExtractTags(title)
                };
                sections.Add(currentSection);
            }
            else if (currentSection != null)
            {
                currentSection.Content += line + "\n";
            }
        }
        
        return sections;
    }
    
    private float ScoreRelevance(string query, HandbookPolicy section, HandbookContext? context)
    {
        var queryWords = new HashSet<string>(query.ToLower().Split());
        var titleWords = new HashSet<string>(section.Title.ToLower().Split());
        var tagWords = new HashSet<string>(section.Tags);
        
        // Calculate overlap
        var titleOverlap = queryWords.Count > 0 ? (float)queryWords.Intersect(titleWords).Count() / queryWords.Count : 0;
        var tagOverlap = queryWords.Count > 0 ? (float)queryWords.Intersect(tagWords).Count() / queryWords.Count : 0;
        
        // Weight title > tags
        var relevance = (titleOverlap * 0.6f) + (tagOverlap * 0.4f);
        
        // Boost if context intent matches
        if (context?.Intent != null && section.Title.ToLower().Contains(context.Intent.ToLower()))
        {
            relevance = Math.Min(1.0f, relevance + 0.2f);
        }
        
        return relevance;
    }
}

public record HandbookSearchResult
{
    public string Status { get; init; } // "success" | "not_found" | "error"
    public List<HandbookPolicy> Policies { get; init; }
    public string SearchExplanation { get; init; }
}

public record HandbookContext
{
    public string? Intent { get; init; }
    public Dictionary<string, object>? CustomerEntities { get; init; }
}
```

---

## Tool Behavior Examples

### Example 1: Refund Query (High Confidence Match)

**Tool Call**:
```json
{
  "query": "refund eligibility",
  "context": {
    "intent": "refund",
    "customer_entities": {
      "order_id": "789",
      "purchase_date": "2026-04-05"
    }
  }
}
```

**Tool Response**:
```json
{
  "status": "success",
  "policies": [
    {
      "policy_id": "policy-001",
      "section": "Refund Policy",
      "title": "30-Day Money-Back Guarantee",
      "content": "We offer a 30-day money-back guarantee. If you're not satisfied within 30 days of purchase, we'll refund your full payment. ...conditions... Non-refundable items: Bulk licenses, used/downloaded content.",
      "tags": ["refund", "money-back", "30-day", "guarantee"],
      "relevance_score": 0.98
    }
  ],
  "search_explanation": "Matched 'refund' in query with Refund Policy section. Customer intent='refund' confirms high relevance."
}
```

### Example 2: Vague Billing Query (Multiple Candidates)

**Tool Call**:
```json
{
  "query": "charge",
  "context": {
    "intent": "billing_explanation"
  }
}
```

**Tool Response**:
```json
{
  "status": "success",
  "policies": [
    {
      "policy_id": "policy-003",
      "section": "Billing Patterns",
      "title": "Charges & Billing Explained",
      "content": "**Subscription Renewal**: Your subscription renews automatically on your renewal date (visible in Account settings). ...Monthly charges are for your active subscription... **Duplicate Charges**: Payment processors sometimes hold pending charges for 48 hours before consolidating. This is normal and not a duplicate charge. ...",
      "tags": ["billing", "charge", "subscription", "renewal", "monthly"],
      "relevance_score": 0.89
    },
    {
      "policy_id": "policy-002",
      "section": "Plan Features",
      "title": "Plans & Features",
      "content": "...",
      "tags": ["plan", "feature"],
      "relevance_score": 0.52
    }
  ],
  "search_explanation": "Matched 'charge' with two sections. Billing Patterns (0.89) is more relevant than Plan Features (0.52)."
}
```

Agent should cite Billing Patterns and explain the subscription renewal (if applicable).

### Example 3: Not Found (Handbook Gap)

**Tool Call**:
```json
{
  "query": "enterprise custom contract negotiation",
  "context": {
    "intent": null
  }
}
```

**Tool Response**:
```json
{
  "status": "not_found",
  "policies": [],
  "search_explanation": "No handbook section matched query 'enterprise custom contract negotiation'. This issue may require human review."
}
```

Agent should respond with ESCALATION (handbook_gap reason).

---

## Agent Instructions (In MAF Agent Prompt)

```
You are a customer support agent. Your responses MUST be grounded in company policy.

CRITICAL RULE: When responding to refund, cancellation, billing, or policy questions:
1. ALWAYS call lookup_handbook_policy FIRST
2. Cite the returned policy sections in your response
3. If lookup returns no_results, IMMEDIATELY escalate to human support (do not invent policies)
4. If policy clearly denies the request, explain the policy reason (cite handbook)
5. If policy is ambiguous or edge case, escalate with recommendation

NEVER:
- Invent refund terms, cancellation rules, or billing explanations
- Promise anything outside the handbook
- Make exceptions without stating you're escalating for human approval

Example:
  Customer: "Can I get a refund?"
  You: Call lookup_handbook_policy(query="refund", intent="refund")
  Response: "Policies found: 30-Day Money-Back Guarantee"
  You: "Yes, if you're within 30 days of purchase, you qualify for our money-back guarantee. [cite policy]. When did you purchase?"
  
  Customer: "I purchased 60 days ago"
  You: Your purchase is outside the 30-day window. However, I'm escalating to our team as they may be able to help in special cases.
```

---

## Testing Considerations

### Unit Test Fixtures

- **Valid Query**: `lookup_handbook_policy("refund")` → Returns Refund Policy section
- **Ambiguous Query**: `lookup_handbook_policy("problem")` → Returns top-3 matching sections ranked by relevance
- **No Match**: `lookup_handbook_policy("quantum entanglement")` → Returns not_found

### Integration Test Fixtures

- **Refund Flow**: Agent calls tool, citation appears in response ✓
- **Handbook Gap**: Agent detects no_found status, escalates ✓
- **Wrong Intent**: Agent calls tool with wrong context, still ranks correctly ✓

---

**Handbook Lookup Tool Contract**: Complete  
**Status**: Ready for implementation
