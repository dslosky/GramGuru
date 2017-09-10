import time

from orm import *
from crawler import Insta
from util import shuffle, rando_hour, log

WEEK = 60 * 60 * 24 * 7
#MONTH = 60 * 60 * 24 * 31
MONTH = 60 * 5

def like(job):
    session = Session()
    job = session.merge(job)

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
    Session.remove()
    return job

def follow(job):
    session = Session()
    job = session.merge(job)

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
    Session.remove()
    return job

def unfollow(job):
    session = Session()
    job = session.merge(job)
    
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

    Session.remove()
    return job

def charge(job):
    session = Session()
    job = session.merge(job)
    
    p = Payment()
    try:
        user = job.i_user.user
        p.user = user
        p.timestamp = time.time()
        session.add(p)

        next_charge = 0
        if user.subscription == '1month':
            user.charge(4000)
            p.amount = 4000
            p.paid_through = time.time() + MONTH

        if user.subscription == '3month':
            user.charge(9000)
            p.amount = 9000
            p.paid_through = time.time() + (3 * MONTH)

        elif user.subscription == 'continuous':
            user.charge(2500)
            p.amount = 2500
            p.paid_through = time.time() + MONTH
            next_charge = time.time() + MONTH

        log('Charged {} ${}'.format(user.username, p.amount))
    except Exception as e:
        job.error = '{}: {}'.format(type(e), e)

    job.end_time = time.time()
    job.running = False
    job.finished = True

    session.commit()

    if next_charge > 0:
        new_job = Job(type='charge', run=next_charge)
        new_job.i_user = job.i_user
        session.add(new_job)
        session.commit()

    Session.remove()
    return job