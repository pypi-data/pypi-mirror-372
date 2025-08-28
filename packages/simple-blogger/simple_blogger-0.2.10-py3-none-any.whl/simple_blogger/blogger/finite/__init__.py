from simple_blogger.blogger.basic import SimpleBlogger, CommonBlogger, ProjectBlogger
from datetime import date, timedelta, datetime
import math

class FiniteBlogger(ProjectBlogger):
    def _set_dates(self, project_tasks, first_post_date=None, days_between_posts=1):
        first_post_date = first_post_date or date.today()
        days_between_posts = timedelta(days=days_between_posts)
        for tasks in project_tasks:
            curr_date = first_post_date
            for task in tasks:
                task["date"] = curr_date.strftime("%Y-%m-%d")
                curr_date += days_between_posts

    def create_simple_tasks(self, first_post_date=None, days_between_posts=1, multiple_projects=False, shuffle=True):
        project_tasks=self._load_project_tasks(multiple_projects)
        if shuffle: self._shuffle(project_tasks)
        self.__set_dates(project_tasks, first_post_date, days_between_posts)
        self._save_tasks(project_tasks)

    def __set_dates(self, project_tasks, first_post_date=None, days_between_posts=1):
        first_post_date = first_post_date or date.today()
        days_between_posts = timedelta(days=days_between_posts)
        for tasks in project_tasks:
            curr_date = first_post_date
            for task in tasks:
                task["date"] = curr_date.strftime("%Y-%m-%d")
                curr_date += days_between_posts

    def create_tasks_between(self, first_post_date, last_post_date, exclude_weekends=True, multiple_projects=False, shuffle=True):
        project_tasks=self._load_project_tasks(multiple_projects)
        if shuffle: self._shuffle(project_tasks)
        self.__set_dates_between(project_tasks, first_post_date, last_post_date, exclude_weekends)
        self._save_tasks(project_tasks=project_tasks)

    def __set_dates_between(self, project_tasks, first_post_date, last_post_date, exclude_weekends):
        first_post_date = datetime.fromordinal(first_post_date.toordinal())
        last_post_date = datetime.fromordinal(last_post_date.toordinal())
        for i, tasks in enumerate(project_tasks):
            curr_date = first_post_date + timedelta(days=math.trunc(i/2))
            d = (last_post_date - curr_date).days / len(tasks)
            days_between_posts = timedelta(days = d)
            for task in tasks:
                if exclude_weekends:
                    if curr_date.weekday() == 6: curr_date += timedelta(days=1)
                    if curr_date.weekday() == 5: curr_date += timedelta(days=-1)
                task["date"] = curr_date.strftime("%Y-%m-%d")
                curr_date += days_between_posts

class FiniteSimpleBlogger(SimpleBlogger, FiniteBlogger):
    def __init__(self, posters, index=None):
        SimpleBlogger.__init__(self, posters, index)

class FiniteCommonBlogger(CommonBlogger, FiniteBlogger):
    def __init__(self, posters, index=None):
        CommonBlogger.__init__(self, posters, index)