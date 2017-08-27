import time
import json

from orm import *
from crawler import Insta
from util import shuffle, Configs, rando_hour, log
from threading import Thread

CONFIGS = Configs()

class Worker(object):
    def __init__(self):
        self.threads = []

    def get_jobs(self):
        now = time.time()

        # grab all jobs ready to run from users that don't have any
        # jobs currently running.
        jobs = (session.query(Job)
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
                            .all())

        # filter jobs for the same username
        filter_jobs = [job for idx, job in enumerate(jobs) 
                                if job.i_user not in 
                                        [j.i_user for j in  jobs[idx + 1:]]]

        # return 3 jobs max
        return filter_jobs[:3]

    def run(self):
        try:
            jobs = self.get_jobs()

            # Let the database know which jobs we're taking
            for job in jobs:
                job.running = True
                job.start_time = time.time()
            session.commit()

            # run each job in a seperate thread
            for job in jobs:
                if job.type == 'like':
                    thread = Thread(target=self.run_like, args=[job])
                elif job.type == 'follow':
                    thread = Thread(target=self.run_follow, args=[job])
                elif job.type == 'unfollow':
                    thread = Thread(target=self.run_unfollow, args=[job])

                self.threads.append(thread)
                thread.start()
        except Exception as e:
            log(msg='Worker error', err=e)

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
                if finished is True:
                    break
                time.sleep(5)

        except Exception as e:
            job.error = '{}: {}'.format(type(e), e)

        job.count = len(users)
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
            following = job.i_user.following[:15]
            deleted = insta.unfollow(following=following)
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
