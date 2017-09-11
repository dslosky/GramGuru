import time
import json

from orm import *
import jobs
from crawler import Insta
from util import shuffle, log


class Worker(object):
    def __init__(self):
        self.threads = []

    @dbconnect
    def get_job(self, session=None):
        now = time.time()

        # grab a job ready to run from users that don't have any
        # jobs currently running.
        job = (session.query(Job)
                            .filter(Job.run < now)
                            .filter(not_(Job.running))
                            .filter(not_(Job.finished))
                            .filter(not_(Job.i_user.has(IUser.jobs.any(Job.running == True))))
                            .filter(Job.i_user.has(
                                        IUser.user.has(
                                            User.payments.any(Payment.paid_through > now)
                                        )
                                    ))
                            .order_by(Job.run)
                            .first())

        # grab the next charge as well
        charge = (session.query(Job)
                            .filter(Job.run < now)
                            .filter(not_(Job.running))
                            .filter(not_(Job.finished))
                            .filter(Job.type == 'charge')
                            .order_by(Job.run)
                            .first())

        if job is None:
            return charge
        if charge is None:
            return job
        if charge.run < job.run:
            return charge

        return job

    @dbconnect
    def run(self, session=None):
        try:
            job = self.get_job()
            if job is not None:
                job = session.merge(job)
                # Let the database know which job we're taking
                job.running = True
                job.start_time = time.time()
                session.commit()

                if job.type == 'like':
                    jobs.like(job)
                elif job.type == 'follow':
                    jobs.follow(job)
                elif job.type == 'unfollow':
                    jobs.unfollow(job)
                elif job.type == 'charge':
                    jobs.charge(job)

        except Exception as e:
            log(msg='Worker error', err=e)
        return
