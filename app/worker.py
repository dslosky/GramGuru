import time
import json

from orm import *
from crawler import Insta
from util import shuffle, Configs, rando_hour, log
from threading import Thread

CONFIGS = Configs()
WEEK = 60 * 60 * 24 * 7

class Worker(object):
    def __init__(self):
        self.threads = []

    def get_job(self):
        now = time.time()

        # grab a job ready to run from users that don't have any
        # jobs currently running.
        session.commit()
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
                            .first)

        return job

    def run(self):
        session = Session()
        try:
            job = self.get_job()

            # Let the database know which jobs we're taking
            job.running = True
            job.start_time = time.time()
            session.commit()

            if job.type == 'like':
                self.run_like(job)
            elif job.type == 'follow':
                self.run_follow(job)
            elif job.type == 'unfollow':
                self.run_unfollow(job)

        except Exception as e:
            log(msg='Worker error', err=e)

        Session.remove()
        return

    def run_like(self, job):
        count = 0
        try:
            insta = Insta()
            insta.login(username=job._user)
            time.sleep(1)

            # get users tags and shuffles them
            tag_names = [str(tag) for tag in job.i_user.tags]
            tags = shuffle(tag_names)
            for tag in tags:
                insta.search(tag)
                count += insta.like_tag(tag)
                time.sleep(5)

        except Exception as e:
            job.error = '{}: {}'.format(type(e), e)

        job.count = count
        job.end_time = time.time()
        job.running = False
        job.finished = True
        
        # new run for jobs
        new_job = Job(type='like', run=time.time() + rando_hour())
        new_job.i_user = job.i_user
        session.add(new_job)
        session.commit()

        insta.driver.quit()
        return

    def run_follow(self, job):
        users = []
        count = 0
        try:
            insta = Insta()
            insta.login(username=job._user)
            time.sleep(1)

            # get users tags and shuffles them
            tag_names = [str(tag) for tag in job.i_user.tags]
            tags = shuffle(tag_names)
            for tag in tags:
                insta.search(tag)
                users, finished = insta.follow(tag)
                count += len(users)
                if finished is True:
                    break
                time.sleep(5)

        except Exception as e:
            job.error = '{}: {}'.format(type(e), e)

        job.count = count
        job.end_time = time.time()
        job.running = False
        job.finished = True

        # new run for jobs
        new_job = Job(type='follow', run=time.time() + (1.5 * rando_hour()))
        new_job.i_user = job.i_user
        session.add(new_job)
        session.commit()

        insta.driver.quit()
        return

    def run_unfollow(self, job):
        deleted = []
        try:
            insta = Insta()
            insta.login(username=job._user)
            time.sleep(1)

            # get users to unfollow
            following = job.i_user.following[:5]
            filtered_following = [f for f in following if 
                                    f.timestamp < time.time() - WEEK]
            deleted = insta.unfollow(following=filtered_following)
        except Exception as e:
            job.error = '{}: {}'.format(type(e), e)
        

        session.commit()

        job.count = len(deleted)
        job.end_time = time.time()
        job.running = False
        job.finished = True

        # new run for job
        new_job = Job(type='unfollow', run=time.time() + rando_hour())
        new_job.i_user = job.i_user
        session.add(new_job)
        session.commit()

        insta.driver.quit()
        return
