from api.job.models.Job import Job

class RepositoryJob:

    def set_inactive(self, id):
        job = self.get_job_by_id(id)
        if not job:
            return None
        job.state = False
        job.save(update_fields=['state'])
        return job

    def get_all_jobs(self):
        return Job.objects.filter(state=True).all()

    def get_job_by_id(self, id):
        return Job.objects.filter(pk=id).first()

    def create_job(self, data, company_id):
        return Job.objects.create(
            name=data.get('name'),
            id_company_id=company_id
        )

    def update_job(self, job_instance, data):
        for attr, value in data.items():
            setattr(job_instance, attr, value)
        job_instance.save(update_fields=list(data.keys()))
        return job_instance

    def delete_job(self, job_instance):
        job_instance.delete()
        return True
