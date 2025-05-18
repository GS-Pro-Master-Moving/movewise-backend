from api.job.repositories.RepositoryJob import RepositoryJob

class ServicesJob:
    
    def __init__(self):
        self.repository = RepositoryJob()

    def set_inactive(self, id):
        job = self.get_job(id)
        if not job:
            return None
        return self.repository.set_inactive(id)

    def get_all_jobs(self):
        return self.repository.get_all_jobs()

    def get_job(self, id):
        return self.repository.get_job_by_id(id)

    def create_job(self, validated_data, company_id):
        return self.repository.create_job(validated_data, company_id)

    def update_job(self, id, validated_data):
        job = self.get_job(id)
        return self.repository.update_job(job, validated_data) if job else None

    def delete_job(self, id):
        job = self.get_job(id)
        if not job:
            return None
        return self.repository.delete_job(job)
