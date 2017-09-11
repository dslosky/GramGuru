import time

from orm import *
from crawler import Insta
from util import shuffle, rando_hour, log

WEEK = 60 * 60 * 24 * 7
MONTH = 60 * 60 * 24 * 31

def like(job, session=None):
    count = 0
    try:
        insta = Insta()
        insta.login(username=job.i_user.username,
                    password=job.i_user.get_password())
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
    return job

def follow(job, session=None):
    new_follows = []
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
            new_follows += users
            if finished is True:
                break
            time.sleep(5)

    except Exception as e:
        job.error = '{}: {}'.format(type(e), e)

    if len(new_follows) > 0:
        for user in new_follows:
            f = Following()
            f.timestamp = time.time()
            f.i_user = job.i_user
            f.other_user = user
            session.add(f)

    session.commit()
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
    return job

@dbconnect
def unfollow(job, session=None):
    deleted = []
    try:
        insta = Insta()
        insta.login(username=job._user)
        time.sleep(1)

        # get users to unfollow
        following = job.i_user.following[:5]
        filtered_following = [f.other_user for f in following if 
                                f.timestamp < time.time() - WEEK]
        deleted = insta.unfollow(following=filtered_following)
    except Exception as e:
        job.error = '{}: {}'.format(type(e), e)
    
    # remove deleted follows from the database
    deleted_follows = (session.query(Following)
                            .filter(Following._user == job._user)
                            .filter(Following.other_user.in_(deleted))
                            .all())
    for follow in deleted_follows:
        session.delete(follow)

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
    return job

@dbconnect
def charge(job, session=None):
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

    return job