# In-memory storage — swap this with SQLite/SQLAlchemy later
# All routes import from here, so switching to a real DB
# only requires changing this file

applications_db = {}    # {app_id: CompanyApplication}
documents_db = {}       # {doc_id: IngestedDocument}
insights_db = {}        # {insight_id: PrimaryInsight}
research_db = {}        # {app_id: ResearchResult}
cam_reports_db = {}     # {app_id: CAMReport}
