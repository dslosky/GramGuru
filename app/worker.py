import time
import json

from orm import *
import jobs
from crawler import Insta
from util import shuffle, log


class Worker(object):
    def __init__(self):
        self.threads = []

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
            job = self.get_job(session=session)
            if job is not None:
                # Let the database know which job we're taking
                job.running = True
                job.start_time = time.time()
                session.commit()

                if job.type == 'like':
                    jobs.like(job, session)
                elif job.type == 'follow':
                    jobs.follow(job, session)
                elif job.type == 'unfollow':
                    jobs.unfollow(job, session)
                elif job.type == 'charge':
                    jobs.charge(job, session)

        except Exception as e:
            # rollback here so we can store the error with the job
            session.rollback()
            job.error = '{}: {}'.format(type(e), e)
            session.commit()
            
            f_name = os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)
            line_num = sys.exc_info()[2].tb_lineno
            log(msg='Worker error: {} line {}'.format(f_name,
                                                      line_num), err=e)

            # raise to let dbconnect handle the rollback
            raise
        return
