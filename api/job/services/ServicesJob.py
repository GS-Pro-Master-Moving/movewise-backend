from api.job.repositories.RepositoryJob import RepositoryJob

class ServicesJob:
    
    def __init__(self):
        self.repository = RepositoryJob()
    def get_all_jobs(self):
        """Getting all jobs"""
        return self.repository.get_all_jobs()
