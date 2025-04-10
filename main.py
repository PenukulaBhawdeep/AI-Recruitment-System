# main.py
import os
import sqlite3
import pandas as pd
import re
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('recruitment.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS jobs
                 (id INTEGER PRIMARY KEY, title TEXT, description TEXT, requirements TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS candidates
                 (id INTEGER PRIMARY KEY, name TEXT, email TEXT, resume TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS matches
                 (job_id INTEGER, candidate_id INTEGER, score REAL,
                 PRIMARY KEY (job_id, candidate_id))''')
    conn.commit()
    conn.close()

# Agent 1: JD Analyzer
class JDAnalyzerAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = PromptTemplate(
            input_variables=["job_description"],
            template="Extract key requirements from this job description:\n{job_description}\n\nRequirements:"
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def analyze(self, title, job_description):
        requirements = self.chain.run(job_description=job_description)
        conn = sqlite3.connect('recruitment.db')
        c = conn.cursor()
        c.execute("INSERT INTO jobs (title, description, requirements) VALUES (?, ?, ?)",
                  (title, job_description, requirements))
        job_id = c.lastrowid
        conn.commit()
        conn.close()
        return job_id, requirements

# Agent 2: CV Evaluator
class CVEvaluatorAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = PromptTemplate(
            input_variables=["resume"],
            template="Extract key skills and experience from this resume:\n{resume}\n\nSkills and Experience:"
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def evaluate(self, name, email, resume):
        skills = self.chain.run(resume=resume)
        conn = sqlite3.connect('recruitment.db')
        c = conn.cursor()
        c.execute("INSERT INTO candidates (name, email, resume) VALUES (?, ?, ?)",
                  (name, email, resume))
        candidate_id = c.lastrowid
        conn.commit()
        conn.close()
        return candidate_id, skills

# Agent 3: Matching Agent
import re  # Add this to the top if not already there

class MatchingAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = PromptTemplate(
            input_variables=["requirements", "skills"],
            template="On a scale of 0-100, how well does this candidate match the job requirements?\n\nJob Requirements: {requirements}\n\nCandidate Skills: {skills}\n\nMatch Score:"
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def match(self, job_id, candidate_id, requirements, skills):
        response = self.chain.run(requirements=requirements, skills=skills).strip()
        match = re.search(r'\d+(?:\.\d+)?', response)
        if match:
            score = float(match.group())
        else:
            score = 0.0  # fallback if no number is found
        conn = sqlite3.connect('recruitment.db')
        c = conn.cursor()
        c.execute("INSERT INTO matches (job_id, candidate_id, score) VALUES (?, ?, ?)",
                  (job_id, candidate_id, score))
        conn.commit()
        conn.close()
        return score

# Agent 4: Scheduler Agent
class SchedulerAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = PromptTemplate(
            input_variables=["name", "job_title", "score"],
            template="Write a formal interview invitation email to {name}, who scored {score}% for the position of {job_title}."
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def schedule(self, name, email, job_title, score):
        if score >= 80:
            email_content = self.chain.run(name=name, job_title=job_title, score=score)
            return email_content
        return None

# Orchestrator
def process_recruitment(job_title, job_description, candidates):    
    llm = OpenAI(temperature=0.7)

    jd_agent = JDAnalyzerAgent(llm)
    cv_agent = CVEvaluatorAgent(llm)
    match_agent = MatchingAgent(llm)
    scheduler_agent = SchedulerAgent(llm)

    job_id, requirements = jd_agent.analyze(job_title, job_description)

    results = []
    for candidate in candidates:
        name, email, resume = candidate
        candidate_id, skills = cv_agent.evaluate(name, email, resume)
        score = match_agent.match(job_id, candidate_id, requirements, skills)
        email_content = scheduler_agent.schedule(name, email, job_title, score)

        results.append({
            "name": name,
            "email": email,
            "score": score,
            "interview_scheduled": email_content is not None,
            "email_content": email_content
        })

    return results

