# Advanced ATS System - Features Documentation

## Overview

This is a production-grade ATS system with advanced features that go beyond simple keyword matching:

1. **Requirement Classifier** - Detects inflated requirements
2. **Evidence Matcher** - Finds implicit skill demonstrations
3. **Gap Analyzer** - Explains gaps instead of auto-rejecting
4. **Bias Auditor** - Flags discrimination proxies
5. **Human-in-the-Loop** - Routes borderline cases to recruiters
6. **Feedback Loop** - Learns from human decisions

## Architecture

```
┌─────────────────┐
│  Resume Parser  │
└────────┬────────┘
         │
         v
┌─────────────────┐
│   Job Parser    │
└────────┬────────┘
         │
         v
┌──────────────────────┐
│ Requirement          │ ← Detects "disguised nice-to-have"
│ Classifier           │   (e.g., "5+ years required" but 3 is fine)
└─────────┬────────────┘
          │
          v
┌──────────────────────┐
│ Evidence Matcher     │ ← Semantic matching, not keywords
│                      │   ("mentored junior devs" = leadership)
└─────────┬────────────┘
          │
          v
┌──────────────────────┐
│ Gap Analyzer         │ ← Critical gaps → request explanation
│                      │   (career break, pivot, etc.)
└─────────┬────────────┘
          │
          ├─[needs explanation]─> Generate Request
          │
          v
┌──────────────────────┐
│ Bias Auditor         │ ← Flags age/gender/name proxies
│                      │   (graduation year → age inference)
└─────────┬────────────┘
          │
          v
┌──────────────────────┐
│ Match Scorer         │
└─────────┬────────────┘
          │
          v
┌──────────────────────┐
│ Recommendation       │
└─────────┬────────────┘
          │
          v
┌──────────────────────┐
│ Human Review?        │ ← Borderline cases → human
│                      │   (score 45-65, bias detected, etc.)
└─────────┬────────────┘
          │
          ├─[yes]─> Human Review (pause)
          │
          v
┌──────────────────────┐
│ Final Evaluation     │ → Stored in Memgraph
└──────────────────────┘
```

## Feature Details

### 1. Requirement Classifier

**Problem**: Job descriptions often have inflated requirements ("5+ years required") when they'd actually hire someone with less experience.

**Solution**: LLM analyzes requirements and detects:
- **Must-have**: Truly critical (candidate fails without it)
- **Nice-to-have**: Explicitly optional
- **Disguised nice-to-have**: Stated as required but contextually flexible

**Example**:
```
JD says: "5+ years Python experience REQUIRED"
Role context: Mid-level position, mentorship available, strong team
Classification: DISGUISED_NICE_TO_HAVE
Reasoning: "Role description and company culture suggest 3+ years 
           with strong fundamentals would be acceptable"
Flexibility Score: 75/100
```

### 2. Evidence Matcher

**Problem**: Keyword matching misses implicit skill demonstrations.

**Solution**: Semantic search finds evidence even when exact terms aren't used.

**Examples**:

| Requirement | Resume Text | Match Type | Reasoning |
|------------|-------------|------------|-----------|
| Leadership | "Mentored 2 junior developers" | Implicit | Demonstrates leadership without using the word |
| Scalability | "Optimized system to handle 10x traffic" | Demonstrated | Shows scalability work without saying "scalability" |
| Stakeholder Management | "Presented quarterly updates to C-suite" | Transferable | Communication with executives |

**Anti-Pattern Detection**:
The system also detects if candidates are over-claiming (using same vague experience for too many requirements).

### 3. Gap Analyzer

**Problem**: Traditional ATS auto-rejects for missing requirements without considering context.

**Solution**: Categorizes gaps and generates explanation requests for critical ones.

**Gap Types**:
1. **CRITICAL**: Must-have requirement with no evidence
2. **SIGNIFICANT**: Must-have with weak evidence
3. **MODERATE**: Nice-to-have missing
4. **BRIDGEABLE**: Learnable quickly given background
5. **EXPLAINABLE**: May have valid reason (career break, pivot)

**Example**:
```
Gap: "No Kubernetes experience"
Type: CRITICAL
Severity: HIGH
Is Bridgeable: YES
Time to Bridge: "2-3 weeks given strong Docker experience"
Recommendation: REQUEST_EXPLANATION

Generated Question:
"We noticed you have strong Docker experience but haven't worked 
with Kubernetes. Have you had exposure to container orchestration, 
or would you be interested in learning Kubernetes on the job?"
```

Instead of auto-rejecting, the system generates a respectful email asking the candidate to explain.

### 4. Bias Auditor

**Problem**: AI models can inadvertently use proxies for protected attributes.

**Solution**: Meta-analysis that audits the model's OWN reasoning for bias.

**Bias Types Detected**:

#### Age Proxies
- Graduation year → age inference
- "Long career" → age discrimination
- "Recent grad" → age discrimination
- "Overqualified" → often age-related

#### Gender Proxies
- Career gaps → maternity leave assumption
- Part-time work → caregiving assumption
- "Aggressive" vs "assertive" → gendered language
- Industry stereotypes (nursing, engineering)

#### Name Bias
- Ethnic-sounding names
- Assumptions about cultural fit
- Language skill assumptions

#### Education Prestige
- Ivy League bias → socioeconomic proxy
- "Target school" preference
- Non-traditional education discounting

#### Location Bias
- Urban vs rural assumptions
- International experience bias

#### Career Path Bias
- Non-linear paths penalized
- Job hopping (may be industry norm)
- Startup vs enterprise bias

**Example Output**:
```json
{
  "has_bias": true,
  "bias_flags": [
    {
      "bias_type": "age",
      "detected_in": "experience_scoring",
      "problematic_text": "candidate graduated in 2020, suggesting limited experience",
      "reasoning": "Inferred age from graduation year, which is discriminatory",
      "severity": "high",
      "alternative_framing": "Evaluate actual years of experience, not graduation year",
      "confidence": 85
    }
  ],
  "overall_fairness_score": 65,
  "requires_human_review": true
}
```

### 5. Human-in-the-Loop

**Problem**: Borderline cases need human judgment, but reviewers are overwhelmed.

**Solution**: Smart routing that only escalates when truly needed.

**Trigger Conditions**:
1. **Borderline Score**: 45-65 range
2. **Bias Detected**: High-severity bias flags
3. **Critical Gaps**: Need candidate explanation first
4. **Low Confidence**: Model uncertain
5. **Credibility Issues**: Evidence seems weak

**Review Package Includes**:
- Executive summary (3-5 key points)
- Specific questions for reviewer
- Bias warnings
- Relevant excerpts
- Estimated review time
- Priority level

**Example**:
```
REQUIRES HUMAN REVIEW

Priority: HIGH
Estimated Time: 15 minutes
Review Deadline: within 24 hours

Triggers:
- Borderline score (58/100)
- High severity bias flag detected (age inference)
- Critical gap needs explanation (no Kubernetes experience)

Executive Summary:
Strong candidate with 3.5 years experience applying for "5+ years 
required" senior role. Has relevant skills but below stated requirement. 
Requirement may be inflated based on role description. Bias flag for 
age inference from graduation year. Gap in Kubernetes is bridgeable 
given strong Docker background.

Key Questions:
1. Is 3.5 years acceptable given strong fundamentals?
2. Should we request Kubernetes explanation before deciding?
3. Are we comfortable with the bias risk identified?

Recommendation: Interview, with focus on Kubernetes willingness to learn
```

### 6. Feedback Loop

**Problem**: Models drift from company hiring preferences over time.

**Solution**: Captures human decisions and analyzes disagreements.

**What's Tracked**:
- Model recommendation vs human decision
- Human reasoning
- Disagreement type
- Timestamp and metadata

**Disagreement Types**:
1. **better_context**: Human had context model lacked
2. **bias_correction**: Human caught model bias
3. **risk_tolerance**: Different risk assessment
4. **gut_feeling**: Culture fit, intangibles
5. **domain_expertise**: Industry knowledge
6. **error_correction**: Model made factual error

**Analytics**:
```
Drift Analysis (Last 30 Days):

Disagreements: 23
- Model said "no", Human said "yes": 15 (65%)
- Model said "yes", Human said "no": 8 (35%)

Top Disagreement Reasons:
1. better_context (9 cases)
   → Model needs more context about role flexibility
2. gut_feeling (7 cases)
   → Model can't assess culture fit well
3. bias_correction (4 cases)
   → Model still has some bias issues

Recommendation: Retrain with emphasis on role flexibility
```

## Memgraph Database Schema

### Nodes

```cypher
// Candidate node
(:Candidate {
  email: string,
  name: string,
  phone: string,
  location: string,
  linkedin: string,
  github: string,
  created_at: datetime
})

// Job node
(:Job {
  job_id: string,
  title: string,
  company: string,
  location: string,
  job_type: string,
  description: string,
  created_at: datetime
})

// Requirement node
(:Requirement {
  requirement_id: uuid,
  text: string,
  category: string,
  requirement_type: enum,
  reasoning: string,
  flexibility_score: float,
  created_at: datetime
})

// Evaluation node
(:Evaluation {
  evaluation_id: uuid,
  overall_score: float,
  skills_score: float,
  experience_score: float,
  education_score: float,
  match_level: enum,
  recommendation: enum,
  confidence_level: enum,
  has_bias: boolean,
  fairness_score: float,
  requires_human_review: boolean,
  created_at: datetime
})

// Evidence node
(:Evidence {
  evidence_id: uuid,
  resume_text: string,
  match_type: string,
  confidence: float,
  reasoning: string,
  is_keyword_match: boolean,
  is_semantic_match: boolean,
  created_at: datetime
})

// BiasFlag node
(:BiasFlag {
  flag_id: uuid,
  bias_type: enum,
  detected_in: string,
  problematic_text: string,
  reasoning: string,
  severity: enum,
  confidence: float,
  created_at: datetime
})

// Feedback node
(:Feedback {
  feedback_id: uuid,
  human_decision: enum,
  human_reasoning: string,
  disagreement: boolean,
  disagreement_type: enum,
  created_at: datetime
})
```

### Relationships

```cypher
(Candidate)-[:EVALUATED_FOR]->(Evaluation)
(Evaluation)-[:FOR_JOB]->(Job)
(Job)-[:HAS_REQUIREMENT]->(Requirement)
(Evaluation)-[:HAS_EVIDENCE]->(Evidence)
(Evidence)-[:ADDRESSES]->(Requirement)
(Evaluation)-[:HAS_BIAS_FLAG]->(BiasFlag)
(Evaluation)-[:HAS_FEEDBACK]->(Feedback)
```

### Query Examples

**Find evaluations with bias issues:**
```cypher
MATCH (e:Evaluation)-[:HAS_BIAS_FLAG]->(b:BiasFlag)
WHERE b.severity = 'high'
RETURN e, b
ORDER BY e.created_at DESC
LIMIT 10
```

**Drift analysis:**
```cypher
MATCH (e:Evaluation)-[:HAS_FEEDBACK]->(f:Feedback)
WHERE f.disagreement = true
  AND datetime(f.created_at) > datetime() - duration({days: 30})
RETURN
  e.recommendation as model_rec,
  f.human_decision as human_dec,
  f.disagreement_type as type,
  count(*) as count
ORDER BY count DESC
```

**Bias statistics:**
```cypher
MATCH (e:Evaluation)-[:HAS_BIAS_FLAG]->(b:BiasFlag)
WHERE datetime(b.created_at) > datetime() - duration({days: 30})
RETURN
  b.bias_type,
  b.severity,
  count(*) as count
ORDER BY count DESC
```

## Usage

### Basic Usage

```python
from src.graphs.advanced_ats_graph import create_advanced_ats_graph

graph = create_advanced_ats_graph(
    memgraph_host="localhost",
    memgraph_password="AsadMemgraph12345"
)

state = {
    "messages": [],
    "resume_file_path": "resume.pdf",
    "job_description": "Your job description...",
    "job_id": "JOB-001"
}

result = graph.invoke(state)
evaluation = result["final_evaluation"]

print(f"Needs human review: {evaluation['needs_human_review']}")
print(f"Bias detected: {evaluation['bias_audit']['has_bias']}")
print(f"Fairness score: {evaluation['fairness_score']}")
```

### With Human Review

```python
from src.agents.human_review_handler import HumanReviewHandler

handler = HumanReviewHandler()

if evaluation["needs_human_review"]:
    review_package = evaluation["review_package"]
    
    print(review_package["executive_summary"])
    print("\nQuestions:")
    for q in review_package["key_questions"]:
        print(f"  - {q}")
    
    human_decision = input("\nYour decision (yes/no/maybe): ")
    reasoning = input("Your reasoning: ")
    
    feedback = handler.capture_human_decision(
        evaluation_id=evaluation["evaluation_id"],
        reviewer_name="Jane Recruiter",
        decision=human_decision,
        reasoning=reasoning
    )
    
    db.store_feedback(feedback)
```

### Analyze Drift

```python
from src.utils.memgraph_connector import MemgraphConnector

db = MemgraphConnector(password="AsadMemgraph12345")

drift = db.get_drift_analysis(days=30)
for record in drift:
    print(f"{record['model_recommendation']} → {record['human_decision']}: {record['count']} cases")

bias_stats = db.get_bias_statistics(days=30)
for record in bias_stats:
    print(f"{record['bias_type']} ({record['severity']}): {record['count']} flags")
```

## Key Differentiators

### vs Traditional ATS
- **Traditional**: Keyword matching
- **This System**: Semantic understanding + evidence

### vs Basic AI ATS
- **Basic**: Scores and rejects
- **This System**: Explains, requests clarification, routes to humans

### vs Other AI Tools
- **Others**: Black box decisions
- **This System**: Audits its OWN reasoning for bias

## Ethical Considerations

### What This System Does
✅ Flags potential bias in its own reasoning
✅ Provides alternative framings
✅ Routes high-risk cases to humans
✅ Tracks disagreements to improve fairness
✅ Respects candidate context (career breaks, pivots)

### What This System Does NOT Do
❌ Replace human judgment entirely
❌ Guarantee perfect fairness
❌ Make final hiring decisions
❌ Process candidates without human oversight

### Recommendations
1. **Always review bias flags** before making decisions
2. **Audit regularly** using drift analysis
3. **Train reviewers** on interpreting AI recommendations
4. **Be transparent** with candidates about AI usage
5. **Provide appeal process** for rejected candidates

## Performance

- **Single evaluation**: 60-120 seconds (with advanced features)
- **Memgraph queries**: Sub-second response times
- **Drift analysis**: Updates daily via batch job
- **Human review rate**: Typically 15-25% of candidates

## Future Enhancements

- [ ] Multi-language bias detection
- [ ] Industry-specific bias patterns
- [ ] Real-time drift alerts
- [ ] Automated retraining triggers
- [ ] Candidate appeal interface
- [ ] Interview question bias detection
- [ ] Offer negotiation bias analysis

## License

MIT License - Use responsibly and ethically.

---

**Remember**: This is an ASSISTIVE tool, not a replacement for human judgment. Always review AI recommendations critically, especially when bias flags are present.
