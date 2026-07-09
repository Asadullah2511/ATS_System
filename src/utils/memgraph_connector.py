from gqlalchemy import Memgraph
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime


class MemgraphConnector:
    def __init__(self, host: str = "localhost", port: int = 7687, username: str = "", password: str = ""):
        self.logger = logging.getLogger(__name__)
        try:
            self.db = Memgraph(host=host, port=port, username=username, password=password)
            self.logger.info("Connected to Memgraph successfully")
        except Exception as e:
            self.logger.error(f"Failed to connect to Memgraph: {e}")
            raise

    def create_indexes(self):
        queries = [
            "CREATE INDEX ON :Candidate(email);",
            "CREATE INDEX ON :Job(job_id);",
            "CREATE INDEX ON :Evaluation(evaluation_id);",
            "CREATE INDEX ON :Requirement(requirement_id);",
        ]
        for query in queries:
            try:
                self.db.execute(query)
            except Exception as e:
                self.logger.warning(f"Index creation warning: {e}")

    def store_candidate(self, candidate_data: Dict[str, Any]) -> str:
        query = """
        MERGE (c:Candidate {email: $email})
        SET c.name = $name,
            c.phone = $phone,
            c.location = $location,
            c.linkedin = $linkedin,
            c.github = $github,
            c.created_at = $created_at
        RETURN c.email as email
        """
        params = {
            "email": candidate_data.get("email", "unknown"),
            "name": candidate_data.get("name", "Unknown"),
            "phone": candidate_data.get("phone"),
            "location": candidate_data.get("location"),
            "linkedin": candidate_data.get("linkedin"),
            "github": candidate_data.get("github"),
            "created_at": datetime.now().isoformat()
        }
        result = self.db.execute_and_fetch(query, params)
        return list(result)[0]["email"]

    def store_job(self, job_data: Dict[str, Any]) -> str:
        query = """
        MERGE (j:Job {job_id: $job_id})
        SET j.title = $title,
            j.company = $company,
            j.location = $location,
            j.job_type = $job_type,
            j.description = $description,
            j.created_at = $created_at
        RETURN j.job_id as job_id
        """
        params = {
            "job_id": job_data.get("job_id", "unknown"),
            "title": job_data.get("title", "Unknown"),
            "company": job_data.get("company", "Unknown"),
            "location": job_data.get("location"),
            "job_type": job_data.get("job_type"),
            "description": job_data.get("description", ""),
            "created_at": datetime.now().isoformat()
        }
        result = self.db.execute_and_fetch(query, params)
        return list(result)[0]["job_id"]

    def store_requirement(self, job_id: str, requirement: Dict[str, Any]) -> str:
        query = """
        MATCH (j:Job {job_id: $job_id})
        CREATE (r:Requirement {
            requirement_id: randomUUID(),
            text: $text,
            category: $category,
            requirement_type: $requirement_type,
            reasoning: $reasoning,
            flexibility_score: $flexibility_score,
            created_at: $created_at
        })
        CREATE (j)-[:HAS_REQUIREMENT]->(r)
        RETURN r.requirement_id as requirement_id
        """
        params = {
            "job_id": job_id,
            "text": requirement.get("text", ""),
            "category": requirement.get("category", ""),
            "requirement_type": requirement.get("requirement_type", "must_have"),
            "reasoning": requirement.get("reasoning", ""),
            "flexibility_score": requirement.get("flexibility_score", 0),
            "created_at": datetime.now().isoformat()
        }
        result = self.db.execute_and_fetch(query, params)
        return list(result)[0]["requirement_id"]

    def store_evaluation(self, evaluation_data: Dict[str, Any]) -> str:
        query = """
        MATCH (c:Candidate {email: $candidate_email})
        MATCH (j:Job {job_id: $job_id})
        CREATE (e:Evaluation {
            evaluation_id: randomUUID(),
            overall_score: $overall_score,
            skills_score: $skills_score,
            experience_score: $experience_score,
            education_score: $education_score,
            match_level: $match_level,
            recommendation: $recommendation,
            confidence_level: $confidence_level,
            has_bias: $has_bias,
            fairness_score: $fairness_score,
            requires_human_review: $requires_human_review,
            created_at: $created_at
        })
        CREATE (c)-[:EVALUATED_FOR]->(e)
        CREATE (e)-[:FOR_JOB]->(j)
        RETURN e.evaluation_id as evaluation_id
        """
        params = {
            "candidate_email": evaluation_data.get("candidate_email"),
            "job_id": evaluation_data.get("job_id"),
            "overall_score": evaluation_data.get("overall_score", 0),
            "skills_score": evaluation_data.get("skills_score", 0),
            "experience_score": evaluation_data.get("experience_score", 0),
            "education_score": evaluation_data.get("education_score", 0),
            "match_level": evaluation_data.get("match_level", "poor"),
            "recommendation": evaluation_data.get("recommendation", "no"),
            "confidence_level": evaluation_data.get("confidence_level", "low"),
            "has_bias": evaluation_data.get("has_bias", False),
            "fairness_score": evaluation_data.get("fairness_score", 100),
            "requires_human_review": evaluation_data.get("requires_human_review", False),
            "created_at": datetime.now().isoformat()
        }
        result = self.db.execute_and_fetch(query, params)
        return list(result)[0]["evaluation_id"]

    def store_evidence(self, evaluation_id: str, requirement_id: str, evidence: Dict[str, Any]):
        query = """
        MATCH (e:Evaluation {evaluation_id: $evaluation_id})
        MATCH (r:Requirement {requirement_id: $requirement_id})
        CREATE (ev:Evidence {
            evidence_id: randomUUID(),
            resume_text: $resume_text,
            match_type: $match_type,
            confidence: $confidence,
            reasoning: $reasoning,
            is_keyword_match: $is_keyword_match,
            is_semantic_match: $is_semantic_match,
            created_at: $created_at
        })
        CREATE (e)-[:HAS_EVIDENCE]->(ev)
        CREATE (ev)-[:ADDRESSES]->(r)
        """
        params = {
            "evaluation_id": evaluation_id,
            "requirement_id": requirement_id,
            "resume_text": evidence.get("resume_text", ""),
            "match_type": evidence.get("match_type", ""),
            "confidence": evidence.get("confidence", 0),
            "reasoning": evidence.get("reasoning", ""),
            "is_keyword_match": evidence.get("is_keyword_match", False),
            "is_semantic_match": evidence.get("is_semantic_match", True),
            "created_at": datetime.now().isoformat()
        }
        self.db.execute(query, params)

    def store_bias_flag(self, evaluation_id: str, bias_flag: Dict[str, Any]):
        query = """
        MATCH (e:Evaluation {evaluation_id: $evaluation_id})
        CREATE (b:BiasFlag {
            flag_id: randomUUID(),
            bias_type: $bias_type,
            detected_in: $detected_in,
            problematic_text: $problematic_text,
            reasoning: $reasoning,
            severity: $severity,
            confidence: $confidence,
            created_at: $created_at
        })
        CREATE (e)-[:HAS_BIAS_FLAG]->(b)
        """
        params = {
            "evaluation_id": evaluation_id,
            "bias_type": bias_flag.get("bias_type", "other"),
            "detected_in": bias_flag.get("detected_in", ""),
            "problematic_text": bias_flag.get("problematic_text", ""),
            "reasoning": bias_flag.get("reasoning", ""),
            "severity": bias_flag.get("severity", "low"),
            "confidence": bias_flag.get("confidence", 0),
            "created_at": datetime.now().isoformat()
        }
        self.db.execute(query, params)

    def store_feedback(self, feedback: Dict[str, Any]):
        query = """
        MATCH (e:Evaluation {evaluation_id: $evaluation_id})
        CREATE (f:Feedback {
            feedback_id: randomUUID(),
            human_decision: $human_decision,
            human_reasoning: $human_reasoning,
            disagreement: $disagreement,
            disagreement_type: $disagreement_type,
            created_at: $created_at
        })
        CREATE (e)-[:HAS_FEEDBACK]->(f)
        """
        params = {
            "evaluation_id": feedback.get("evaluation_id"),
            "human_decision": feedback.get("human_decision"),
            "human_reasoning": feedback.get("human_reasoning"),
            "disagreement": feedback.get("disagreement", False),
            "disagreement_type": feedback.get("disagreement_type"),
            "created_at": datetime.now().isoformat()
        }
        self.db.execute(query, params)

    def get_drift_analysis(self, days: int = 30) -> List[Dict]:
        query = """
        MATCH (e:Evaluation)-[:HAS_FEEDBACK]->(f:Feedback)
        WHERE f.disagreement = true
        AND datetime(f.created_at) > datetime() - duration({days: $days})
        RETURN
            e.recommendation as model_recommendation,
            f.human_decision as human_decision,
            f.disagreement_type as disagreement_type,
            count(*) as count
        ORDER BY count DESC
        """
        result = self.db.execute_and_fetch(query, {"days": days})
        return [dict(record) for record in result]

    def get_bias_statistics(self, days: int = 30) -> Dict[str, Any]:
        query = """
        MATCH (e:Evaluation)-[:HAS_BIAS_FLAG]->(b:BiasFlag)
        WHERE datetime(b.created_at) > datetime() - duration({days: $days})
        RETURN
            b.bias_type as bias_type,
            b.severity as severity,
            count(*) as count
        ORDER BY count DESC
        """
        result = self.db.execute_and_fetch(query, {"days": days})
        return [dict(record) for record in result]

    def close(self):
        self.logger.info("Closing Memgraph connection")
