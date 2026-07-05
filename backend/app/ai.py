import json
import re
import httpx
from typing import List, Dict, Any, Optional
from app.config import settings

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama3-8b-8192"

def clean_json_response(text: str) -> str:
    # Extracts JSON content from potential markdown markers e.g. ```json ... ```
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if match:
        return match.group(1).strip()
    return text.strip()

async def call_groq_api(messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not configured")
        
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": temperature,
        "response_format": {"type": "json_object"} if "json" in str(messages[-1].get("content", "")).lower() else None
    }
    
    async with httpx.AsyncClient(timeout=45.0) as client:
        response = await client.post(GROQ_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

# --- AI Methods ---

async def generate_roadmap_ai(career_goal: str, skill_level: str, daily_hours: float, study_duration: Optional[str] = None) -> Dict[str, Any]:
    system_prompt = (
        "You are an expert Career Counselor and Curriculum Designer.\n\n"
        "Generate a personalized roadmap ONLY for the selected career.\n\n"
        "Rules:\n"
        "First identify the career domain.\n"
        "Identify the required skills, subjects, exams, certifications, or prerequisites for that career.\n"
        "Generate roadmap phases in the correct order.\n"
        "Include milestones and weekly goals.\n"
        "Include assessments or mock tests if applicable.\n"
        "Return only topics relevant to the selected career.\n"
        "Do NOT include software or programming topics unless the selected career requires them.\n\n"
        "The user has provided a Study Duration (e.g., '30 days', '2 months', '1 year'). You MUST generate a roadmap matching this duration by adjusting the number of learning phases, weekly goals, milestones, study workload, and revision schedule. For example, a shorter duration should have fewer, more intensive phases with compressed timelines and a focused revision schedule, while a longer duration should have more comprehensive phases, detailed milestones, and a thorough revision phase.\n\n"
        "Examples:\n"
        "If Career Goal = Railway Ticket Collector\n"
        "Include:\n"
        "RRB Recruitment Process\n"
        "Mathematics\n"
        "Reasoning\n"
        "General Awareness\n"
        "English\n"
        "Mock Tests\n"
        "Previous Year Papers\n"
        "Do NOT include:\n"
        "Python\n"
        "Java\n"
        "React\n"
        "Machine Learning\n\n"
        "If Career Goal = Doctor\n"
        "Include:\n"
        "Biology\n"
        "Chemistry\n"
        "Physics\n"
        "NEET Preparation\n"
        "Mock Tests\n\n"
        "If Career Goal = Software Engineer\n"
        "Include:\n"
        "Programming Fundamentals\n"
        "Data Structures\n"
        "Algorithms\n"
        "Databases\n"
        "Projects\n"
        "Interview Preparation\n\n"
        "Output format:\n"
        "Return structured JSON matching the required schema. MUST contain:\n"
        "{\n"
        "  \"title\": \"Roadmap Title\",\n"
        "  \"target_goal\": \"Career Goal name\",\n"
        "  \"milestones\": [\n"
        "    {\n"
        "      \"phase_number\": 1,\n"
        "      \"title\": \"Phase/Milestone Title\",\n"
        "      \"description\": \"Include weekly goals and estimated completion\",\n"
        "      \"estimated_weeks\": 2,\n"
        "      \"topics\": [\n"
        "        {\n"
        "          \"title\": \"Topic Title\",\n"
        "          \"description\": \"Details of what to study\"\n"
        "        }\n"
        "      ]\n"
        "    }\n"
        "  ]\n"
        "}\n"
        "Do not output markdown wrappers surrounding the JSON unless it is standard ```json ... ``` wrapper. Ensure the JSON is completely valid."
    )
    user_prompt = f"Input:\nCareer Goal: {career_goal}\nSkill Level: {skill_level}\nDaily Study Hours: {daily_hours}\nStudy Duration: {study_duration or 'Flexible'}"
    
    if not settings.GROQ_API_KEY:
        return get_mock_roadmap(career_goal, skill_level, daily_hours, study_duration)

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        res_text = await call_groq_api(messages)
        return json.loads(clean_json_response(res_text))
    except Exception as e:
        print(f"Error calling Groq API: {e}. Falling back to mockup generator.")
        return get_mock_roadmap(career_goal, skill_level, daily_hours, study_duration)

async def get_adaptive_coach_insight_ai(quiz_score: int, topic: str, career_goal: str) -> str:
    system_prompt = (
        "You are the EDUMITHRA Adaptive Learning Coach. Provide a brief, supportive, and analytical explanation "
        "of why a student's study plan has been modified based on their quiz score. "
        "If score is <70, explain that we are inserting prerequisite foundational topics and adjusting deadlines. "
        "If score is >90, explain that we are unlocking advanced tracks and acceleration. "
        "Keep it to 2-3 inspiring sentences."
    )
    user_prompt = f"The student failed a quiz on '{topic}' with a score of {quiz_score}% while preparing for '{career_goal}'."
    if quiz_score >= 90:
        user_prompt = f"The student excelled on '{topic}' with a score of {quiz_score}% while preparing for '{career_goal}'."
    elif quiz_score >= 70:
        user_prompt = f"The student passed a quiz on '{topic}' with a score of {quiz_score}% while preparing for '{career_goal}'."

    if not settings.GROQ_API_KEY:
        return get_mock_coach_insight(quiz_score, topic, career_goal)

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        return await call_groq_api(messages, temperature=0.7)
    except Exception as e:
        print(f"Error in coach insight: {e}")
        return get_mock_coach_insight(quiz_score, topic, career_goal)


# --- MOCKUP RE-CREATION UTILITIES (Deterministic Mock Fallback) ---

def get_mock_roadmap(goal: str, level: str, hours: float, study_duration: Optional[str] = None) -> Dict[str, Any]:
    # Custom mocks based on typical inputs
    title = f"Mastery Path for {goal}"
    
    g_lower = goal.lower()
    
    if "railway" in g_lower or "ticket collector" in g_lower or "rrb" in g_lower:
        milestones = [
            {
                "phase_number": 1,
                "title": "Phase 1: Understand RRB Recruitment Process & Syllabus",
                "description": "Familiarize yourself with the selection process, exam pattern, basic computer test (CBT) requirements, and eligibility guidelines.",
                "estimated_weeks": int(4 / (hours/2)) or 1,
                "topics": [
                    {"title": "RRB NTPC Selection Process", "description": "Review eligibility, age criteria, stages of examination, and document verification rules.", "resource_keyword": "rrb ntpc recruitment process details"},
                    {"title": "Exam Pattern & CBT Overview", "description": "Understand marking schemes, sections (Awareness, Math, Reasoning), and time allocations.", "resource_keyword": "rrb ntpc exam pattern cbt syllabus"}
                ]
            },
            {
                "phase_number": 2,
                "title": "Phase 2: Core Subjects - General Awareness & Arithmetic",
                "description": "Master the critical high-scoring sections of the RRB syllabus.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "Mathematics & Basic Arithmetic", "description": "Study number systems, percentages, profit & loss, ratios, simple/compound interest, and algebra.", "resource_keyword": "rrb math arithmetic lectures"},
                    {"title": "General Awareness & Static GK", "description": "Focus on Indian history, geography, constitution, general science, and current events.", "resource_keyword": "general awareness static gk for rrb"},
                    {"title": "General Intelligence & Reasoning", "description": "Practice analogies, coding-decoding, relationships, syllogisms, and puzzles.", "resource_keyword": "rrb reasoning and general intelligence"}
                ]
            },
            {
                "phase_number": 3,
                "title": "Phase 3: Previous Year Papers & Mock Tests",
                "description": "Take full-length simulated mock tests and analyze past year examination papers to build speed and accuracy.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "Previous Year Question Papers", "description": "Solve and review official past exam papers to understand question styles.", "resource_keyword": "rrb ntpc previous year question paper solved"},
                    {"title": "Full-Length Mock Exams", "description": "Take timed mock tests online to practice time-management under stress.", "resource_keyword": "rrb ntpc online mock test practice"}
                ]
            },
            {
                "phase_number": 4,
                "title": "Phase 4: Revision & Document Verification Prep",
                "description": "Consolidate study notes and prepare for the final stages of the recruitment drive.",
                "estimated_weeks": int(4 / (hours/2)) or 1,
                "topics": [
                    {"title": "Syllabus Revision", "description": "Quickly revise formulas, shortcuts, current affairs, and GK notes.", "resource_keyword": "rrb quick revision current affairs math formulas"},
                    {"title": "Medical & Document Verification Guidance", "description": "Understand physical and medical standards, eye test criteria, and required certificates.", "resource_keyword": "rrb medical exam document verification guidelines"}
                ]
            }
        ]
    elif "ias" in g_lower or "ips" in g_lower or "upsc" in g_lower or "civil officer" in g_lower:
        milestones = [
            {
                "phase_number": 1,
                "title": "Phase 1: Civil Services Prelims Preparation",
                "description": "Build foundations in General Studies and the CSAT aptitude test.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "General Studies I: Indian History & Polity", "description": "Study Indian constitution, governance, history, and physical geography.", "resource_keyword": "upsc history polity basic lectures"},
                    {"title": "CSAT (Paper II) Aptitude", "description": "Practice comprehension, logical reasoning, and basic numeracy.", "resource_keyword": "upsc csat paper 2 math reasoning"},
                    {"title": "Current Affairs & Newspaper Analysis", "description": "Form a daily habit of reading editorials and taking current affairs notes.", "resource_keyword": "daily newspaper analysis for upsc"}
                ]
            },
            {
                "phase_number": 2,
                "title": "Phase 2: Civil Services Mains Writing Prep",
                "description": "Prepare for core writing papers, essays, and your optional subject.",
                "estimated_weeks": int(8 / (hours/2)) or 3,
                "topics": [
                    {"title": "Optional Subject Core Foundations", "description": "Study the detailed theory and concepts of your chosen optional subject.", "resource_keyword": "how to prepare upsc optional subject"},
                    {"title": "Answer Writing Practicum", "description": "Learn to write structured, comprehensive answers within word limits.", "resource_keyword": "upsc mains answer writing practice tips"}
                ]
            },
            {
                "phase_number": 3,
                "title": "Phase 3: UPSC Interview / Personality Test preparation",
                "description": "Build confidence, refine communication, and study your Detailed Application Form (DAF).",
                "estimated_weeks": int(4 / (hours/2)) or 1,
                "topics": [
                    {"title": "DAF Analysis & Mock Interviews", "description": "Practice answering questions based on your background, state, and hobbies.", "resource_keyword": "upsc mock interview sessions personality test"}
                ]
            }
        ]
    elif "doctor" in g_lower or "neet" in g_lower or "medical" in g_lower:
        milestones = [
            {
                "phase_number": 1,
                "title": "Phase 1: NEET Physics, Chemistry, & Biology Core",
                "description": "Establish absolute mastery of the NCERT Class 11 and 12 science syllabus.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "Biology: Human Physiology & Genetics", "description": "Learn core biological systems, cell structure, plant anatomy, and genetics.", "resource_keyword": "neet biology genetics physiology ncert"},
                    {"title": "Chemistry: Organic & Physical Principles", "description": "Study chemical bonding, stoichiometry, organic reaction mechanisms, and thermodynamics.", "resource_keyword": "neet chemistry lectures organic physical"},
                    {"title": "Physics: Mechanics & Electrodynamics", "description": "Master laws of motion, kinematics, optics, and current electricity.", "resource_keyword": "neet physics conceptual lectures mechanics"}
                ]
            },
            {
                "phase_number": 2,
                "title": "Phase 2: NEET Mock Papers & Revision Sessions",
                "description": "Solve test questions and revise core definitions.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "NCERT Line-by-Line Revision", "description": "Go through high-yield diagrams and text highlights in NCERT.", "resource_keyword": "neet biology ncert line by line revision"},
                    {"title": "Solving Previous Year Question Papers", "description": "Solve past 10 years of NEET questions under examination timers.", "resource_keyword": "neet solved previous papers physics chemistry biology"}
                ]
            },
            {
                "phase_number": 3,
                "title": "Phase 3: NEET Mock Tests & Admission Guidance",
                "description": "Simulate mock exams and research medical colleges counseling processes.",
                "estimated_weeks": int(4 / (hours/2)) or 1,
                "topics": [
                    {"title": "NEET Full Syllabus Mock Tests", "description": "Submit practice mock tests, review wrong answers, and optimize score strategies.", "resource_keyword": "neet full mock test papers series"},
                    {"title": "Medical College Counseling Guidance", "description": "Learn about AIQ, state counseling, cutoffs, and document collection.", "resource_keyword": "neet pg ug counseling admission guide"}
                ]
            }
        ]
    elif "nurse" in g_lower or "nursing" in g_lower:
        milestones = [
            {
                "phase_number": 1,
                "title": "Phase 1: Anatomy, Physiology, & Pharmacology Foundations",
                "description": "Understand the basic sciences required to deliver clinical care.",
                "estimated_weeks": int(4 / (hours/2)) or 1,
                "topics": [
                    {"title": "Anatomy & Physiology for Nurses", "description": "Learn organ systems, skeletal frameworks, and anatomical terms.", "resource_keyword": "nursing anatomy and physiology lessons"},
                    {"title": "Basic Pharmacology & Medication Calculation", "description": "Study drug classifications, dosage calculations, and administration guidelines.", "resource_keyword": "pharmacology for nurses dosage calculation"}
                ]
            },
            {
                "phase_number": 2,
                "title": "Phase 2: Clinical Nursing Principles & Safety",
                "description": "Master patient care operations, hygiene, diagnostics, and emergency procedures.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "Nursing Foundations & Patient Assessment", "description": "Perform physical assessments, monitor vital signs, and handle document records.", "resource_keyword": "nursing head to toe assessment procedures"},
                    {"title": "Infection Control & Patient Safety", "description": "Understand sterilization, sterile fields, medical waste, and mobility safety.", "resource_keyword": "infection control clinical nursing guidelines"}
                ]
            },
            {
                "phase_number": 3,
                "title": "Phase 3: Nursing Licensing & NCLEX Review",
                "description": "Prepare for licensing board exams and hospital orientation checklists.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "NCLEX-RN Exam Practice Questions", "description": "Solve test items focused on prioritization, safety, and health promotion.", "resource_keyword": "nclex rn review practice questions"},
                    {"title": "Clinical Rotation & Shift Management", "description": "Understand shift handoffs, nurse-patient communication, and nursing ethics.", "resource_keyword": "clinical nursing shifts handoff tutorial"}
                ]
            }
        ]
    elif "ca " in g_lower or "chartered accountant" in g_lower or "accounting" in g_lower or "cpa" in g_lower:
        milestones = [
            {
                "phase_number": 1,
                "title": "Phase 1: Financial Accounting Principles & Accounting Standards",
                "description": "Master corporate accounting, bookkeeping, ledger reconciliation, and basic standards.",
                "estimated_weeks": int(4 / (hours/2)) or 1,
                "topics": [
                    {"title": "Accounting Principles & Bookkeeping", "description": "Master double-entry bookkeeping, journals, ledgers, and trial balances.", "resource_keyword": "double entry accounting bookkeeping foundations"},
                    {"title": "Preparation of Financial Statements", "description": "Build Profit & Loss accounts, Balance Sheets, and Cash Flow summaries.", "resource_keyword": "how to prepare balance sheet income statement"}
                ]
            },
            {
                "phase_number": 2,
                "title": "Phase 2: Taxation & Auditing Regulations",
                "description": "Study corporate tax systems, auditing guidelines, and fiscal controls.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "Direct and Indirect Taxation", "description": "Learn income tax computation, corporate deductions, GST, and filing rules.", "resource_keyword": "direct indirect taxation gst concepts"},
                    {"title": "Auditing Standards & Internal Controls", "description": "Review audit evidence, verification techniques, fraud detection, and reporting.", "resource_keyword": "auditing standards internal controls course"}
                ]
            },
            {
                "phase_number": 3,
                "title": "Phase 3: CA / CPA Exam Preparation & Practice",
                "description": "Solve case studies, practice mock papers, and prepare for articleship/internship boards.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "CA/CPA Past Exam Paper Review", "description": "Solve past exam questions under strict time constraints.", "resource_keyword": "ca final intermediate solved past papers"},
                    {"title": "Professional Ethics & Code of Conduct", "description": "Master auditor responsibilities, independence rules, and client confidentiality.", "resource_keyword": "accounting professional ethics audit independence"}
                ]
            }
        ]
    elif "law" in g_lower or "lawyer" in g_lower or "clat" in g_lower:
        milestones = [
            {
                "phase_number": 1,
                "title": "Phase 1: Constitutional Law & Legal Foundations",
                "description": "Learn fundamental rights, legal system layout, and historical statutes.",
                "estimated_weeks": int(4 / (hours/2)) or 1,
                "topics": [
                    {"title": "Indian Constitution & Governance", "description": "Study fundamental rights, directive principles, judiciary system structure.", "resource_keyword": "indian constitution law basic lectures"},
                    {"title": "Intro to Jurisprudence & Legal Reasoning", "description": "Analyze sources of law, judicial precedents, and basic legal aptitude.", "resource_keyword": "legal reasoning logic clat preparation"}
                ]
            },
            {
                "phase_number": 2,
                "title": "Phase 2: Civil, Criminal, & Contract Laws",
                "description": "Master legal definitions, contracts, penal codes, and dispute resolutions.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "Law of Contracts & Torts", "description": "Understand valid contracts, breach of contract, liabilities, and tort rules.", "resource_keyword": "law of contracts and torts basics"},
                    {"title": "Criminal Law & Criminal Procedure", "description": "Study IPC, offences, investigations, trials, and penal processes.", "resource_keyword": "criminal law ipc basic lectures"}
                ]
            },
            {
                "phase_number": 3,
                "title": "Phase 3: Moot Court Practice & Licensing Board exams",
                "description": "Prepare for legal practice, bar exams, and internship processes.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "All India Bar Exam (AIBE) Review", "description": "Practice mock papers and review notes for licensing boards.", "resource_keyword": "aibe bar exam practice questions prep"},
                    {"title": "Legal Drafting & Case Analysis", "description": "Write plaints, petitions, affidavits, and contract templates.", "resource_keyword": "legal drafting petition writing tutorial"}
                ]
            }
        ]
    elif "electrician" in g_lower or "plumber" in g_lower or "trades" in g_lower:
        milestones = [
            {
                "phase_number": 1,
                "title": "Phase 1: Trade Safety & Electrical/Plumbing Theory",
                "description": "Learn safety parameters, basic circuit principles, pressure flows, and hand tools.",
                "estimated_weeks": int(4 / (hours/2)) or 1,
                "topics": [
                    {"title": "Workplace Safety & Hazard Management", "description": "Learn OSHA rules, personal protective equipment (PPE), and shock/leak prevention.", "resource_keyword": "trade safety osha instructions plumbing electrical"},
                    {"title": "Basic Electrical/Plumbing Principles", "description": "Master Ohm's Law, voltage, currents, or pipe pressure, grading, and venting.", "resource_keyword": "basic electrical circuits plumbing design physics"}
                ]
            },
            {
                "phase_number": 2,
                "title": "Phase 2: Technical Diagrams, Codes, & Layouts",
                "description": "Understand blueprints, wiring schematics, code requirements, and planning rules.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "Reading Blueprints & Schematics", "description": "Interpret symbols, plan layouts, and calculate material requirements.", "resource_keyword": "how to read blue prints schematics plumbing electrical"},
                    {"title": "National Code Compliance (NEC/IPC)", "description": "Study safety clearances, pipe material requirements, and regulatory standards.", "resource_keyword": "national electrical code plumbing code guidelines"}
                ]
            },
            {
                "phase_number": 3,
                "title": "Phase 3: Practical Tools & License Exam preparation",
                "description": "Study practical equipment use and prepare for journeyman certification.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "Journeyman Licensing Exam Review", "description": "Solve test questions regarding code limits, safety parameters, and calculations.", "resource_keyword": "journeyman electrician plumber licensing exam questions"},
                    {"title": "Diagnostic Tools & Troubleshooting", "description": "Learn how to use multimeters, leak detectors, and clear system failures.", "resource_keyword": "trade troubleshooting diagnostics testing electrical plumbing"}
                ]
            }
        ]
    elif "graphic" in g_lower or "design" in g_lower or "creative" in g_lower:
        milestones = [
            {
                "phase_number": 1,
                "title": "Phase 1: Design Principles, Typography & Color Theory",
                "description": "Learn layout grids, font pairings, visual balance, and color combinations.",
                "estimated_weeks": int(4 / (hours/2)) or 1,
                "topics": [
                    {"title": "Elements & Principles of Design", "description": "Understand contrast, hierarchy, alignment, balance, and negative space.", "resource_keyword": "principles of graphic design tutorial"},
                    {"title": "Color Theory & Typography", "description": "Master color wheels, psychology, typeface families, and readability rules.", "resource_keyword": "typography and color theory crash course"}
                ]
            },
            {
                "phase_number": 2,
                "title": "Phase 2: Creative Software Mastery (Figma, Photoshop, Illustrator)",
                "description": "Build high-fidelity vector assets, wireframes, and layouts.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "Adobe Illustrator & Photoshop basics", "description": "Learn vector pen tools, masking, photo editing, and layer controls.", "resource_keyword": "photoshop illustrator basic design course"},
                    {"title": "UI Design & Prototyping in Figma", "description": "Construct buttons, UI components, auto-layouts, and interactive mockups.", "resource_keyword": "figma ui design components auto layout"}
                ]
            },
            {
                "phase_number": 3,
                "title": "Phase 3: Portfolio Building & Freelancing",
                "description": "Establish a personal brand, compile project studies, and acquire clients.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "Case Studies & Behance Portfolio", "description": "Structure design projects explaining the problem, process, and final layout.", "resource_keyword": "design portfolio case study tips behance"},
                    {"title": "Client Onboarding & Pricing Basics", "description": "Draft client proposals, set hourly/project rates, and manage files.", "resource_keyword": "how to freelance as a graphic designer"}
                ]
            }
        ]
    elif "marketing" in g_lower or "digital marketer" in g_lower:
        milestones = [
            {
                "phase_number": 1,
                "title": "Phase 1: Marketing Funnels & Copywriting Basics",
                "description": "Learn customer journeys, landing pages, headlines, and call-to-actions.",
                "estimated_weeks": int(4 / (hours/2)) or 1,
                "topics": [
                    {"title": "Marketing Funnels & Customer Lifecycle", "description": "Understand TOFU, MOFU, BOFU, conversion rates, and retention loops.", "resource_keyword": "marketing funnels customer conversion funnel"},
                    {"title": "Copywriting Fundamentals", "description": "Write persuasive headlines, hooks, and descriptions that drive actions.", "resource_keyword": "copywriting tutorial secrets basics"}
                ]
            },
            {
                "phase_number": 2,
                "title": "Phase 2: SEO, Paid Ads, & Social Media Campaign",
                "description": "Establish brand reach, configure ad platforms, and monitor keywords.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "Search Engine Optimization (SEO) basics", "description": "Optimize metadata, write keyword-focused content, and monitor backlink structures.", "resource_keyword": "seo tutorial rank website google"},
                    {"title": "Google Ads & Meta Ads Campaigns", "description": "Configure ad budgets, targeting, copy, and set up pixel tracking scripts.", "resource_keyword": "how to run google meta facebook ads"}
                ]
            },
            {
                "phase_number": 3,
                "title": "Phase 3: Web Analytics & Marketing Strategy",
                "description": "Measure conversion KPIs, configure Google Analytics, and optimize campaigns.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "Google Analytics 4 & Dashboards", "description": "Interpret traffic sources, bounce rates, and goals in GA4.", "resource_keyword": "google analytics 4 setup dashboards"},
                    {"title": "Digital Marketing Strategy & Pitching", "description": "Compile comprehensive marketing audits and pitch marketing campaigns.", "resource_keyword": "digital marketing business strategy proposal"}
                ]
            }
        ]
    elif "entrepreneur" in g_lower or "business" in g_lower or "startup" in g_lower:
        milestones = [
            {
                "phase_number": 1,
                "title": "Phase 1: Idea Validation & Market Research",
                "description": "Verify customer problems, check market sizing, and design user interviews.",
                "estimated_weeks": int(4 / (hours/2)) or 1,
                "topics": [
                    {"title": "Problem-Solution Fit & Validation", "description": "Run customer validation interviews without leading questions.", "resource_keyword": "mom test customer interviews validation"},
                    {"title": "Market Sizing & TAM/SAM/SOM", "description": "Calculate target market volume, competitors, and potential audience sizing.", "resource_keyword": "market sizing tam sam som calculation"}
                ]
            },
            {
                "phase_number": 2,
                "title": "Phase 2: Business Models & Minimum Viable Product (MVP)",
                "description": "Outline revenue streams, costs, channels, and build basic product versions.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "Business Model Canvas", "description": "Construct key partners, activities, resources, and cost structures.", "resource_keyword": "business model canvas template walkthrough"},
                    {"title": "Defining & Launching an MVP", "description": "Focus on the smallest set of features that can satisfy core problems.", "resource_keyword": "how to build launch mvp product"}
                ]
            },
            {
                "phase_number": 3,
                "title": "Phase 3: Sales, Unit Economics, & Pitching",
                "description": "Optimize margins, calculate Customer Acquisition Cost (CAC), and write pitch decks.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "CAC, LTV & Unit Economics", "description": "Compute customer lifetime value, acquisition cost, and gross margins.", "resource_keyword": "unit economics cac ltv startup calculations"},
                    {"title": "Pitch Deck Design & Fundraising Basics", "description": "Structure a 10-slide deck covering problem, solution, market size, team, and financials.", "resource_keyword": "startup pitch deck template fundraising"}
                ]
            }
        ]
    elif "photographer" in g_lower or "photography" in g_lower:
        milestones = [
            {
                "phase_number": 1,
                "title": "Phase 1: Camera Controls & The Exposure Triangle",
                "description": "Master camera settings, manual exposure, and basic lenses.",
                "estimated_weeks": int(4 / (hours/2)) or 1,
                "topics": [
                    {"title": "Aperture, Shutter Speed, & ISO", "description": "Manage brightness, depth of field, motion blur, and digital noise.", "resource_keyword": "exposure triangle aperture shutter speed iso"},
                    {"title": "Lenses & Composition rules", "description": "Learn focal lengths, rule of thirds, leading lines, and framing concepts.", "resource_keyword": "photography composition rules lens guide"}
                ]
            },
            {
                "phase_number": 2,
                "title": "Phase 2: Lighting Techniques & Photo Editing",
                "description": "Understand natural and studio light, and edit RAW images in Lightroom.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "Natural & Studio Lighting Basics", "description": "Learn golden hour setups, flash triggers, softboxes, and reflectors.", "resource_keyword": "photography lighting techniques studio tutorial"},
                    {"title": "Lightroom Classic Post-Processing", "description": "Master color grading, highlights/shadows, masking, and export settings.", "resource_keyword": "lightroom classic photo editing tutorials"}
                ]
            },
            {
                "phase_number": 3,
                "title": "Phase 3: Photography Portfolio & Client Acquisition",
                "description": "Build galleries, price shoots (portraits, events, commercial), and manage files.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "Portfolio Website & Booking System", "description": "Compile your best works, design layout layouts, and setup scheduling tools.", "resource_keyword": "photography portfolio layout squarespace pixieset"},
                    {"title": "Client Management & Pricing Packages", "description": "Structure print packaging, digital delivery rules, and contract terms.", "resource_keyword": "pricing photography packages client contract"}
                ]
            }
        ]
    elif "teacher" in g_lower or "education" in g_lower or "pedagogy" in g_lower:
        milestones = [
            {
                "phase_number": 1,
                "title": "Phase 1: Child Psychology & Learning Theories",
                "description": "Learn cognitive development, behaviorism, and student motivations.",
                "estimated_weeks": int(4 / (hours/2)) or 1,
                "topics": [
                    {"title": "Piaget, Vygotsky, & Cognitive Development", "description": "Study development stages, scaffolding, and social learning processes.", "resource_keyword": "cognitive learning theories piaget vygotsky"},
                    {"title": "Behaviorist, Cognitivist, & Constructivist Models", "description": "Understand educational theories and how students process knowledge.", "resource_keyword": "educational psychology constructivism behaviorism"}
                ]
            },
            {
                "phase_number": 2,
                "title": "Phase 2: Pedagogy, Lesson Planning & Classroom Management",
                "description": "Design lesson objectives, select activities, and handle class behaviors.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "Bloom's Taxonomy & Lesson Planning", "description": "Write clear learning goals, design starter, core, and review activities.", "resource_keyword": "blooms taxonomy lesson plan writing template"},
                    {"title": "Classroom Management & Engagement", "description": "Configure tables, establish routines, manage behaviors, and maintain focus.", "resource_keyword": "classroom management strategies for teachers"}
                ]
            },
            {
                "phase_number": 3,
                "title": "Phase 3: Assessments & Teacher Certification Prep",
                "description": "Analyze rubrics, design quizzes, and prepare for state/national teacher tests.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "Formative & Summative Assessments", "description": "Write exam items, configure rubrics, and provide feedback.", "resource_keyword": "formative vs summative assessment rubrics"},
                    {"title": "Teacher Eligibility Test (TET/NET) Prep", "description": "Review past questions, subject-specific pedagogy, and exam rules.", "resource_keyword": "teacher eligibility test study guide questions"}
                ]
            }
        ]
    elif "data scientist" in g_lower or "data science" in g_lower:
        milestones = [
            {
                "phase_number": 1,
                "title": "Phase 1: Python Basics, Pandas & SQL Data Queries",
                "description": "Learn scripting, read files, run database queries, and clean tables.",
                "estimated_weeks": int(4 / (hours/2)) or 1,
                "topics": [
                    {"title": "Python for Data Analysis", "description": "Understand syntax, variables, lists, dicts, and functions.", "resource_keyword": "python for data science crash course"},
                    {"title": "SQL Databases & Data Extraction", "description": "Query tables, write joins, groups, and aggregations.", "resource_keyword": "sql database queries data science"},
                    {"title": "Pandas & NumPy Foundations", "description": "Clean missing values, filter rows, merge tables, and compute stats.", "resource_keyword": "pandas numpy tutorial data cleaning"}
                ]
            },
            {
                "phase_number": 2,
                "title": "Phase 2: Probability, Statistics, & Data Visualization",
                "description": "Study hypothesis testing, distributions, and plot charts.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "Descriptive & Inferential Statistics", "description": "Master mean/median, standard deviation, normal distribution, and A/B testing.", "resource_keyword": "probability and statistics for data science"},
                    {"title": "Data Visualization with Matplotlib & Seaborn", "description": "Draw scatterplots, histograms, bar charts, and heatmaps.", "resource_keyword": "data visualization matplotlib seaborn python"}
                ]
            },
            {
                "phase_number": 3,
                "title": "Phase 3: Machine Learning Models & Portfolios",
                "description": "Implement linear regression, decision trees, clustering, and compile code on GitHub.",
                "estimated_weeks": int(8 / (hours/2)) or 3,
                "topics": [
                    {"title": "Supervised Learning Algorithms", "description": "Learn regression, classification, random forests, and metrics (accuracy, recall).", "resource_keyword": "supervised machine learning scikit learn"},
                    {"title": "Unsupervised Learning & Clustering", "description": "Master K-means clustering and PCA dimensionality reduction.", "resource_keyword": "unsupervised learning clustering k means"},
                    {"title": "Data Science Portfolio & Git", "description": "Push your datasets, notebooks, and models to GitHub repositories.", "resource_keyword": "how to build a data science portfolio"}
                ]
            }
        ]
    elif "ai" in g_lower or "machine learning" in g_lower or "artificial intelligence" in g_lower:
        milestones = [
            {
                "phase_number": 1,
                "title": "Phase 1: Math Foundations & Machine Learning Basics",
                "description": "Master linear algebra, calculus, and basic scikit-learn models.",
                "estimated_weeks": int(4 / (hours/2)) or 1,
                "topics": [
                    {"title": "Linear Algebra & Calculus for ML", "description": "Understand matrices, dot products, gradients, and partial derivatives.", "resource_keyword": "mathematics for machine learning linear algebra"},
                    {"title": "Classical Machine Learning with Scikit-Learn", "description": "Implement linear/logistic regression, SVM, and random forests.", "resource_keyword": "scikit learn machine learning tutorial"}
                ]
            },
            {
                "phase_number": 2,
                "title": "Phase 2: Deep Learning, Neural Networks & PyTorch",
                "description": "Construct neural layers, activation functions, and optimize model loss.",
                "estimated_weeks": int(8 / (hours/2)) or 3,
                "topics": [
                    {"title": "Deep Learning & Artificial Neural Networks", "description": "Learn forward/backpropagation, loss functions, and optimizers (SGD, Adam).", "resource_keyword": "deep learning neural networks explained"},
                    {"title": "PyTorch Framework & Model Building", "description": "Write tensor graphs, custom datasets, model classes, and training loops.", "resource_keyword": "pytorch deep learning crash course"}
                ]
            },
            {
                "phase_number": 3,
                "title": "Phase 3: Large Language Models (LLMs) & Deployments",
                "description": "Learn transformer blocks, prompt templates, and host endpoints.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "Transformers & LLM API Integration", "description": "Understand self-attention, tokenizers, and call APIs (OpenAI/Groq).", "resource_keyword": "transformer neural network architecture llm"},
                    {"title": "Deploying Models to Production (M LOps)", "description": "Dockerize model servers, deploy to Hugging Face, or host via FastAPI.", "resource_keyword": "deploy machine learning model fastapi docker"}
                ]
            }
        ]
    elif "software" in g_lower or "computer" in g_lower or "developer" in g_lower:
        milestones = [
            {
                "phase_number": 1,
                "title": "Phase 1: Programming Fundamentals & Logic",
                "description": "Acquire syntax, data structures, and foundational algorithms.",
                "estimated_weeks": int(4 / (hours/2)) or 1,
                "topics": [
                    {"title": "Core Syntax & Variables", "description": "Learn syntax rules, data types, scoping, loops, and conditions.", "resource_keyword": "programming fundamentals for beginners"},
                    {"title": "Basic Data Structures", "description": "Master arrays, lists, key-value maps, and standard operations.", "resource_keyword": "data structures arrays lists maps"},
                    {"title": "Functions & Computational Logic", "description": "Write reusable logic, scoping parameters, and basic recursion.", "resource_keyword": "writing functions algorithms programming"}
                ]
            },
            {
                "phase_number": 2,
                "title": "Phase 2: Databases, APIs, & Backend Web Services",
                "description": "Master relational databases, SQL queries, and designing API servers.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "Relational Databases & SQL Queries", "description": "Query tables, perform JOINs, write group-by filters in SQL.", "resource_keyword": "SQL database crash course"},
                    {"title": "Building Web REST APIs", "description": "Build high-performance endpoints, handle payloads, and return JSON responses.", "resource_keyword": "building rest api backend web service"}
                ]
            },
            {
                "phase_number": 3,
                "title": "Phase 3: System Design & Deployment",
                "description": "Deploy secure, production-grade applications with authentication.",
                "estimated_weeks": int(8 / (hours/2)) or 3,
                "topics": [
                    {"title": "JWT Auth & API Security", "description": "Secure API endpoints with JSON Web Tokens and user authentication flows.", "resource_keyword": "jwt authentication security backend"},
                    {"title": "Dockerizing & Cloud Deployment", "description": "Containerize web services with Docker and host on AWS/Render/Vercel.", "resource_keyword": "docker deploy web application cloud"}
                ]
            }
        ]
    elif "civil" in g_lower:
        milestones = [
            {
                "phase_number": 1,
                "title": "Phase 1: Engineering Mechanics & Materials",
                "description": "Learn static forces, stress/strain properties, and properties of concrete/steel.",
                "estimated_weeks": int(4 / (hours/2)) or 1,
                "topics": [
                    {"title": "Engineering Mechanics & Statics", "description": "Learn vector forces, equilibrium, moment calculations, and truss analysis.", "resource_keyword": "engineering mechanics statics lectures"},
                    {"title": "Strength of Materials", "description": "Understand stress, strain, shear force, and bending moments.", "resource_keyword": "strength of materials civil engineering"}
                ]
            },
            {
                "phase_number": 2,
                "title": "Phase 2: Structural Analysis & CAD Design",
                "description": "Draw blueprint diagrams, calculate structures, and evaluate loads.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "AutoCAD Drafting & 3D Modeling", "description": "Learn vector plans, sections, elevations, and structural modeling.", "resource_keyword": "autocad civil engineering drafting tutorial"},
                    {"title": "Structural Analysis & Concrete Design", "description": "Calculate load distributions, reinforce columns, slabs, and foundations.", "resource_keyword": "reinforced concrete design structures civil"}
                ]
            },
            {
                "phase_number": 3,
                "title": "Phase 3: Soil Mechanics & Site Operations",
                "description": "Perform soil testing, survey sites, and draft environmental reports.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "Soil Mechanics & Foundation Engineering", "description": "Evaluate bearing capacity, settlement, and retain walls.", "resource_keyword": "soil mechanics foundation engineering lectures"},
                    {"title": "Construction Management & Estimating", "description": "Draft schedules, cost estimations, and safety site supervision reports.", "resource_keyword": "construction cost estimation civil management"}
                ]
            }
        ]
    elif "mechanical" in g_lower:
        milestones = [
            {
                "phase_number": 1,
                "title": "Phase 1: Engineering Statics, Dynamics & Thermodynamics",
                "description": "Learn heat cycles, vector motions, force systems, and energy conversions.",
                "estimated_weeks": int(4 / (hours/2)) or 1,
                "topics": [
                    {"title": "Engineering Statics & Vector Forces", "description": "Learn force resolutions, friction, trusses, and moments.", "resource_keyword": "mechanical engineering statics lessons"},
                    {"title": "Thermodynamics & Heat Cycles", "description": "Study energy conservation, entropy, Carnot/Rankine cycles, and boilers.", "resource_keyword": "thermodynamics laws heat cycles mechanical"}
                ]
            },
            {
                "phase_number": 2,
                "title": "Phase 2: Fluid Mechanics & CAD/CAM Modeling",
                "description": "Learn pressure flows, boundary layers, and design parts in SolidWorks/AutoCAD.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "SolidWorks Part Modeling & Assemblies", "description": "Draft 3D components, configure constraints, and run stress simulations.", "resource_keyword": "solidworks mechanical drafting tutorial assembly"},
                    {"title": "Fluid Mechanics & Heat Transfer", "description": "Master Bernoulli's equation, pipe friction, laminar/turbulent flows, and heat exchangers.", "resource_keyword": "fluid mechanics heat transfer mechanical engineering"}
                ]
            },
            {
                "phase_number": 3,
                "title": "Phase 3: Kinematics of Machines & Manufacturing Practice",
                "description": "Understand gear ratios, vibrations, CNC machines, and factory operations.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": "Theory of Machines & Vibration", "description": "Study cams, gears, flywheels, gyroscopes, and dampers.", "resource_keyword": "theory of machines mechanical gears vibrations"},
                    {"title": "Manufacturing Processes & CNC", "description": "Learn milling, lathe operations, casting, welding, and CNC coding.", "resource_keyword": "manufacturing processes lathe cnc machining"}
                ]
            }
        ]
    else:
        # Dynamic fallback based on the actual career goal input
        milestones = [
            {
                "phase_number": 1,
                "title": f"Phase 1: Foundations of {goal}",
                "description": f"Acquire basic concepts, industry terminology, and fundamental tools for entering the field as a {goal}.",
                "estimated_weeks": int(4 / (hours/2)) or 1,
                "topics": [
                    {"title": f"Introduction to {goal}", "description": f"Learn the overview, key roles, responsibilities, and basic skills required for a {goal}.", "resource_keyword": f"{goal} career basic overview tutorial"},
                    {"title": f"Core Terminology & Industry Standards", "description": f"Master standard vocabularies, workflows, and protocols used daily by a {goal}.", "resource_keyword": f"{goal} industry concepts explained"},
                    {"title": f"Fundamental Tools & Applications", "description": f"Understand software, equipment, or tools that a {goal} uses on entry-level projects.", "resource_keyword": f"tools used by {goal} tutorial"}
                ]
            },
            {
                "phase_number": 2,
                "title": f"Phase 2: Core Methodologies & Practice for {goal}",
                "description": f"Establish practical capabilities and workflow management required for a {goal}.",
                "estimated_weeks": int(6 / (hours/2)) or 2,
                "topics": [
                    {"title": f"Essential Processes & Workflows", "description": f"Standard operational procedures and frameworks for a {goal}.", "resource_keyword": f"{goal} work processes guidelines"},
                    {"title": f"Practical Application & Exercises", "description": f"Hands-on exercises and simulated projects mimicking daily responsibilities of a {goal}.", "resource_keyword": f"{goal} hands on projects practical course"},
                    {"title": f"Intermediate Software & Tools", "description": f"Master productivity platforms and specialized programs for a {goal}.", "resource_keyword": f"software tools for {goal} walkthrough"}
                ]
            },
            {
                "phase_number": 3,
                "title": f"Phase 3: Advanced Specialization & Job Readiness as a {goal}",
                "description": f"Prepare for professional entry, construct portfolios, and review compliance requirements.",
                "estimated_weeks": int(8 / (hours/2)) or 3,
                "topics": [
                    {"title": f"Advanced Case Studies & Best Practices", "description": f"Explore senior-level projects, complex challenges, and quality controls.", "resource_keyword": f"advanced {goal} practices case studies"},
                    {"title": f"Professional Certifications & Standards", "description": f"Identify key industry credentials and regulatory guidelines for a {goal}.", "resource_keyword": f"{goal} certifications and standards exam"},
                    {"title": f"Portfolio & Interview Preparation", "description": f"Package your projects, build a professional profile, and simulate interviews for a {goal} job.", "resource_keyword": f"how to pass a {goal} interview tutorial"}
                ]
            }
        ]

    # Dynamic skill-level adaptation filtering
    level_lower = level.lower()
    if level_lower == "intermediate":
        # Keep intermediate & advanced concepts (skip Phase 1)
        filtered = []
        for idx, m in enumerate(milestones[1:]):
            m_copy = m.copy()
            m_copy["phase_number"] = idx + 1
            m_copy["title"] = f"Phase {idx + 1}: " + m_copy["title"].split(": ", 1)[-1]
            filtered.append(m_copy)
        if filtered:
            milestones = filtered
    elif level_lower == "advanced":
        # Keep only the final milestone (mock tests, interview/counseling prep, revision)
        filtered = []
        for idx, m in enumerate(milestones[-1:]):
            m_copy = m.copy()
            m_copy["phase_number"] = idx + 1
            m_copy["title"] = f"Phase {idx + 1}: " + m_copy["title"].split(": ", 1)[-1]
            filtered.append(m_copy)
        if filtered:
            milestones = filtered

    # Dynamic study-duration adaptation
    import re
    def parse_study_duration_to_weeks(duration_str: str) -> float:
        if not duration_str:
            return 12.0  # default / flexible (approx 3 months)
        s = duration_str.lower().strip()
        match = re.search(r'(\d+(?:\.\d+)?)\s*(day|week|month|year)', s)
        if not match:
            num_match = re.search(r'\d+(?:\.\d+)?', s)
            if num_match:
                val = float(num_match.group(0))
                if val > 15:
                    return val / 7.0
                return val
            return 12.0
        val = float(match.group(1))
        unit = match.group(2)
        if 'day' in unit:
            return val / 7.0
        elif 'week' in unit:
            return val
        elif 'month' in unit:
            return val * 4.33
        elif 'year' in unit:
            return val * 52.0
        return 12.0

    weeks = 12.0
    if study_duration:
        try:
            weeks = parse_study_duration_to_weeks(study_duration)
        except Exception:
            pass

    # Number of learning phases adjustment based on study duration
    # If weeks <= 4, keep only 2 phases (Foundations and Revision/Tests)
    if weeks <= 4.0 and len(milestones) > 2:
        milestones = [milestones[0], milestones[-1]]
    # If weeks <= 8, keep at most 3 phases
    elif weeks <= 8.0 and len(milestones) > 3:
        milestones = [milestones[0], milestones[1], milestones[-1]]

    # Re-index phase numbers, add workload notes, and ensure revision info is explicitly detailed
    for idx, m in enumerate(milestones):
        m["phase_number"] = idx + 1
        m["title"] = f"Phase {idx + 1}: " + m["title"].split(": ", 1)[-1]
        
        workload = "Intensive study workload" if hours >= 4 else "Moderate study workload"
        pace = "accelerated pacing" if weeks <= 6.0 else "steady pacing"
        revision = "with compressed revision schedule" if weeks <= 6.0 else "with thorough revision and practice schedule"
        m["description"] = f"{m['description']} ({workload}: {hours} hrs/day, {pace}, {revision})."

    # Distribute the estimated weeks proportionally
    current_sum = sum(m.get("estimated_weeks", 2) for m in milestones)
    if current_sum > 0:
        target_weeks = max(int(round(weeks)), len(milestones))
        for m in milestones:
            fraction = m.get("estimated_weeks", 2) / current_sum
            m_weeks = max(int(round(fraction * target_weeks)), 1)
            m["estimated_weeks"] = m_weeks

    return {
        "title": title,
        "target_goal": goal,
        "milestones": milestones
    }

def get_mock_coach_insight(score: int, topic: str, career_goal: str) -> str:
    if score < 70:
        return (
            f"Adaptive Alert: Quiz score of {score}% on '{topic}' signals conceptual gaps. "
            "To prevent compounding learning gaps, EDUMITHRA has inserted foundational prerequisite modules into your roadmap, "
            "extended subsequent deadlines, and curated highly specific base tutorials. Take this revision opportunity to master the core concepts."
        )
    elif score >= 90:
        return (
            f"Acceleration Unlocked! Exceptional score of {score}% on '{topic}' demonstrates complete mastery. "
            f"We have accelerated your roadmap toward '{career_goal}', skipping introductory components and unlocking advanced tracks early. Keep up the high velocity!"
        )
    else:
        return (
            f"Solid progress! A score of {score}% confirms you have met the proficiency threshold for '{topic}'. "
            "We are moving directly to the next milestone in your schedule. Review your weak points periodically to maintain complete mastery."
        )

async def generate_topic_resources_ai(
    career_goal: str,
    skill_level: str,
    topic_title: str,
    topic_desc: str,
    progress_percent: float,
    quiz_score: Optional[int] = None
) -> Dict[str, Any]:
    system_prompt = (
        "You are an expert AI Career Copilot and learning assistant. "
        "Your task is to generate highly personalized learning resources for a specific career and topic.\n\n"
        "You must return a valid JSON object matching this schema:\n"
        "{\n"
        "  \"notes\": {\n"
        "    \"key_concepts\": [\"concept 1\", \"concept 2\"],\n"
        "    \"important_points\": [\"point 1\", \"point 2\"],\n"
        "    \"revision_summary\": \"summary text...\",\n"
        "    \"common_mistakes\": [\"mistake 1\", \"mistake 2\"]\n"
        "  },\n"
        "  \"questions\": [\n"
        "    {\n"
        "      \"type\": \"MCQ\" | \"Short Answer\" | \"Coding Problem\" | \"Scenario-Based\",\n"
        "      \"question\": \"question text...\",\n"
        "      \"options\": [\"opt A\", \"opt B\", \"opt C\", \"opt D\"] (only for MCQ, otherwise empty or null),\n"
        "      \"correct_answer\": \"answer text...\",\n"
        "      \"explanation\": \"explanation text...\"\n"
        "    }\n"
        "  ],\n"
        "  ],\n"
        "  \"official_resources\": [\n"
        "    {\n"
        "      \"name\": \"resource name...\",\n"
        "      \"description\": \"resource description...\",\n"
        "      \"link\": \"resource URL...\"\n"
        "    }\n"
        "  ]\n"
        "}\n"
    )
    
    is_software = any(kw in career_goal.lower() for kw in ["software", "developer", "engineer", "scientist", "ai", "coder", "programmer", "coding", "web", "app"])
    allowed_types = "MCQs, Short Answer Questions, Coding Problems, Scenario-Based Questions" if is_software else "MCQs, Short Answer Questions, Scenario-Based Questions"
    
    score_info = f"The user scored {quiz_score}% on a recent quiz for this topic." if quiz_score is not None else "The user has not taken a quiz for this topic yet."
    
    user_prompt = (
        f"Career Goal: {career_goal}\n"
        f"Current Skill Level: {skill_level}\n"
        f"Topic: {topic_title}\n"
        f"Topic Description: {topic_desc}\n"
        f"Roadmap Progress: {progress_percent:.1f}% complete\n"
        f"Quiz Performance: {score_info}\n\n"
        f"Please generate the study notes, practice questions (include at least 2 questions of types: {allowed_types}), "
        f"and 2 relevant official resource portals (use realistic links related to the career)."
    )
    
    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        res_str = await call_groq_api(messages)
        res_clean = clean_json_response(res_str)
        return json.loads(res_clean)
    except Exception as e:
        print(f"Error calling Groq for resources: {e}. Using fallback generator.")
        return generate_fallback_resources(career_goal, skill_level, topic_title, topic_desc, is_software)

def generate_fallback_resources(career_goal: str, skill_level: str, topic_title: str, topic_desc: str, is_software: bool) -> Dict[str, Any]:
    key_concepts = [
        f"Understanding the core principles of {topic_title}.",
        f"Adapting resource allocation for {career_goal} tasks.",
        f"Key standard practices at the {skill_level} level."
    ]
    important_points = [
        f"Verify entry criteria, guidelines, or specifications relative to {topic_title}.",
        "Focus on safety, reliability, and standards of the profession.",
        "Always document steps and review reference documents."
    ]
    revision_summary = (
        f"This module guides you through the core requirements of {topic_title} tailored for a career as a {career_goal}. "
        f"For {skill_level} learners, emphasis is placed on syntax, standards, and practical implementation frameworks."
    )
    common_mistakes = [
        "Skipping prerequisite steps or general guidelines.",
        "Underestimating exam duration or standard verification procedures.",
        "Not cross-checking official portals or documentation."
    ]
    
    questions = [
        {
            "type": "MCQ",
            "question": f"Which of the following is a primary consideration when analyzing {topic_title} for a {career_goal}?",
            "options": [
                "Ignoring default parameters",
                "Adhering to standard operating procedures and validation rules",
                "Deferring to non-authorized guidelines",
                "None of the above"
            ],
            "correct_answer": "Adhering to standard operating procedures and validation rules",
            "explanation": f"Professional standards for a {career_goal} require strict adherence to validated workflows and safety/exam protocols."
        }
    ]
    if is_software:
        questions.append({
            "type": "Coding Problem",
            "question": f"Write a function or algorithm to validate input tokens matching the standard configuration for {topic_title}.",
            "options": None,
            "correct_answer": "def validate_config(tokens):\n    return all(t.isalnum() for t in tokens)",
            "explanation": "Standard helper to sanitize and filter alphanumeric codes or identifiers."
        })
    else:
        questions.append({
            "type": "Scenario-Based",
            "question": f"A supervisor requests you to perform an assessment on {topic_title}. You notice a discrepancy. How do you resolve this?",
            "options": None,
            "correct_answer": "Log the variance, consult the official guidelines handbook, and report the correction immediately.",
            "explanation": f"Maintaining accuracy and integrity is key for a {career_goal} at the {skill_level} stage."
        })
        
    if "railway" in career_goal.lower() or "ticket" in career_goal.lower() or "rrb" in career_goal.lower():
        official = [
            {"name": "Indian Railways RRB Portal", "description": "Official recruitment board portal for notification, schedules, and patterns.", "link": "https://www.rrcb.gov.in"},
            {"name": "Ministry of Railways", "description": "Official website of Indian Railways containing guidelines and documents.", "link": "https://indianrailways.gov.in"}
        ]
    elif any(kw in career_goal.lower() for kw in ["ias", "ips", "ssc", "government", "cgl"]):
        official = [
            {"name": "Union Public Service Commission (UPSC)", "description": "Official portal for civil services exam registration, syllabus, and notifications.", "link": "https://www.upsc.gov.in"},
            {"name": "Staff Selection Commission (SSC)", "description": "Official site for CGL recruitment notifications and guidelines.", "link": "https://ssc.gov.in"}
        ]
    elif any(kw in career_goal.lower() for kw in ["doctor", "nurse", "neet", "medical"]):
        official = [
            {"name": "National Testing Agency (NTA)", "description": "Official portal conducting medical eligibility entrance tests.", "link": "https://neet.nta.nic.in"},
            {"name": "World Health Organization (WHO)", "description": "International guidelines and health standard reference portal.", "link": "https://www.who.int"}
        ]
    else:
        official = [
            {"name": "Official Professional Association website", "description": "The primary administrative body guiding standards and practice frameworks.", "link": "https://www.wikipedia.org"},
            {"name": "National Board of Education and Careers", "description": "Standard portal for syllabus rules and certification details.", "link": "https://www.gov.uk"}
        ]
        
    return {
        "notes": {
            "key_concepts": key_concepts,
            "important_points": important_points,
            "revision_summary": revision_summary,
            "common_mistakes": common_mistakes
        },
        "questions": questions,
        "official_resources": official
    }
