from api.job.models.Job import Job

class RepositoryJob:
    
    @staticmethod
    def get_all_jobs():
        """Get all jobs"""
        return Job.objects.all()
