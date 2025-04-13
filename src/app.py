from config import Config
from job_analyzer import JobAnalyzer
from job_searcher import JobSearcher
from ui import StreamlitUI


def main():
    config = Config()
    job_analyzer = JobAnalyzer(config)
    job_searcher = JobSearcher(config)
    ui = StreamlitUI(job_analyzer, job_searcher)
    ui.run()


if __name__ == "__main__":
    main()
