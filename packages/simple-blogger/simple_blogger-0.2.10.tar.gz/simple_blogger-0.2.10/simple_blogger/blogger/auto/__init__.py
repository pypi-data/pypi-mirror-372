from simple_blogger.blogger.basic import SimpleBlogger, CommonBlogger, ProjectBlogger
from datetime import date, timedelta

class AutoBlogger(ProjectBlogger):
    def __init__(self, first_post_date=None):
        self.first_post_date = first_post_date or date.today()

    def _check_task(self, task, tasks, days_before=0):
        check_date = date.today() + timedelta(days=days_before)
        days_diff = check_date - self.first_post_date
        return task["day"] == days_diff.days % len(tasks)
    
    def create_auto_tasks(self, day_offset=0, days_between_posts=1, multiple_projects=False, shuffle=True):
        project_tasks=self._load_project_tasks(multiple_projects)
        if shuffle: self._shuffle(project_tasks)
        self.__set_days(project_tasks, day_offset, days_between_posts)
        self._save_tasks(project_tasks=project_tasks)

    def __set_days(self, project_tasks, day_offset=0, days_between_posts=1):
        for tasks in project_tasks:
            day=day_offset
            for task in tasks:
                task["day"] = day
                day += days_between_posts

class AutoSimpleBlogger(SimpleBlogger, AutoBlogger):
    def __init__(self, posters, first_post_date=None, index=None):
        AutoBlogger.__init__(self, first_post_date)
        SimpleBlogger.__init__(self, posters, index)

class AutoCommonBlogger(CommonBlogger, AutoBlogger):
    def __init__(self, posters, first_post_date=None, index=None):
        AutoBlogger.__init__(self, first_post_date)
        CommonBlogger.__init__(self, posters, index)