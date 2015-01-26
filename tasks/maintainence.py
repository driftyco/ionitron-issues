import threading
import util
from datetime import datetime
from worker import q
import github_api


def queue_daily_tasks():
    print 'Queueing daily tasks update'

    if should_run_daily_maintainence():
        q.enqueue(run_maintainence_tasks)


def run_maintainence_tasks():
    """
    Maintainence tasks to run on older issues.
    """

    if not should_run_daily_maintainence():
        return 0

    print "Running daily tasks..."

    open_issues = []
    try:
        open_issues = github_api.fetch_open_issues()
        if not open_issues:
            return open_issues

        set_last_update()

        for issue in open_issues:
            issue_maintainence(issue)

    except Exception as ex:
        print 'run_maintainence_tasks error: %s' % ex

    return len(open_issues)


def issue_maintainence_number(number):
    try:
        issue = github_api.fetch_issue(number)

        if issue.get('error'):
            return issue

        return issue_maintainence(issue)

    except Exception as ex:
        print 'run_maintainence_tasks error: %s' % ex
        return { 'error': '%s' % ex }


def issue_maintainence(issue):
    from tasks import old_issues, github_issue_submit, needs_reply, issue_scores
    data = {}
    number = 0

    try:
        if not issue:
            data['error'] = 'invalid issue'
            return data

        number = issue.get('number')
        if not number:
            data['error'] = 'invalid issue number'
            return data

        data['number'] = number

        if issue.get('pull_request') is not None:
            data['invalid'] = 'pull request'
            return data

        if issue.get('closed_at') is not None:
            data['invalid'] = 'closed_at %s' % issue.get('closed_at')
            return data

        old_issue_data = old_issues.manage_old_issue(issue)
        if old_issue_data:
            data['closed_old_issue'] = True
            return data

        if github_issue_submit.remove_flag_if_submitted_through_github(issue):
            data['removed_submitted_through_github_flag'] = True

        needs_reply_data = needs_reply.manage_needs_reply_issue(issue)
        if needs_reply_data:
            data['needs_reply_data'] = needs_reply_data
            if needs_reply_data.get('close_needs_reply_issue'):
                return data

        data['issue_score'] = issue_scores.update_issue_score(number, data={
            'issue': issue
        })

    except Exception as ex:
        print 'issue_maintainence error, issue %s: %s' % (number, ex)
        data['error'] = 'issue %s, %s' % (number, ex)

    return data


def should_run_daily_maintainence(min_refresh_seconds=1800, last_update_str=None, now=datetime.now()):
    if not last_update_str:
        last_update_str = util.get_cached_value('maintainence_last_update')

    if not last_update_str:
        print 'should_run_daily_maintainence, no last_update_str'
        return True

    last_update = datetime.strptime(last_update_str, '%Y-%m-%d %H:%M:%S')

    diff = (now - last_update).seconds

    should_run = diff > min_refresh_seconds

    print 'should_run_daily_maintainence, last_update: %s, now: %s, difference: %s, should_run: %s' % (last_update, now, diff, should_run)

    return should_run


def set_last_update():
    util.set_cached_value('maintainence_last_update', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), expires=60*60*24*7)

