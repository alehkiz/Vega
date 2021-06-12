from app.models.app import Visit
from sqlalchemy import extract, cast, Date
from sqlalchemy.sql import visitors
from sqlalchemy.sql.functions import user
from app.models.wiki import Question, QuestionView
from app.models.security import User
import datetime
from collections import namedtuple
from os import name

fields_date = ['today',
               #    'day',
               #    'week',
               'month',
               'year',
               'yesterday',
               #    'lask_week',
               'last_month',
               'last_year']

fields_name_counter = ['count'] + fields_date

date_structure = namedtuple('date_structure', fields_date)

question_views = namedtuple('question_views', fields_name_counter)  # ,
# defaults=[None] * len(fields_name_counter))

questions = namedtuple('questions', fields_name_counter)  # ,
#    defaults=[None] * len(fields_name_counter))
users = namedtuple('users',
                   fields_name_counter)  # ,
#    defaults=[None] * len(fields_name_counter))

visitors = namedtuple('visitors', fields_name_counter)

dash_struct = namedtuple('dash_struct', [
    'date',
    'users',
    'questions',
    'question_views'
    'visitors'
])




class Dashboard():

    def __init__(self) -> None:
        today = datetime.datetime.today().date()
        self.date = date_structure(
            today=today,
            # day=today.day,
            month=today.month,
            year=today.year,
            last_month=(today.replace(
                day=1) - datetime.timedelta(days=1)).replace(day=1),
            last_year=today.year - 1,
            yesterday=today -
            datetime.timedelta(1)
        )

    def start(self):
        self.users = users(
            count=User.query.count(),
            today=User.query_by_date(
                self.date.today).count(),
            month=User.query_by_month_year(
                self.date.year, self.date.month).count(),
            year=User.query_by_year(self.date.year).count(),
            yesterday=User.query_by_date(
                self.date.yesterday).count(),
            last_month=User.query_by_month_year(
                self.date.last_month.year, self.date.last_month.month).count(),
            last_year=User.query_by_year(
                self.date.last_year).count()
        )
        self.questions = questions(
            count=Question.query.count(),
            today=Question.query_by_date(
                self.date.today).count(),
            month=Question.query_by_month_year(
                self.date.year, self.date.month).count(),
            year=Question.query_by_year(
                self.date.year).count(),
            yesterday=Question.query_by_date(
                self.date.yesterday).count(),
            last_month=Question.query_by_month_year(
                self.date.last_month.year, self.date.last_month.month).count(),
            last_year=Question.query_by_year(
                self.date.last_year).count()
        )
        self.question_views = question_views(
            count=QuestionView.query.count(),
            today=QuestionView.query_by_date(
                self.date.today).count(),
            month=QuestionView.query_by_month_year(
                self.date.year, self.date.month).count(),
            year=QuestionView.query_by_year(
                self.date.year).count(),
            yesterday=QuestionView.query_by_date(
                self.date.yesterday).count(),
            last_month=QuestionView.query_by_month_year(
                self.date.last_month.year, self.date.last_month.month).count(),
            last_year=QuestionView.query_by_year(
                self.date.last_year).count()
        )
        self.visitors = visitors(
            count = Visit.query.count(),
            today=Visit.query_by_date(
                self.date.today).count(),
            month=Visit.query_by_month_year(
                self.date.year, self.date.month).count(),
            year=Visit.query_by_year(
                self.date.year).count(),
            yesterday=Visit.query_by_date(
                self.date.yesterday).count(),
            last_month=Visit.query_by_month_year(
                self.date.last_month.year, self.date.last_month.month).count(),
            last_year=Visit.query_by_year(
                self.date.last_year).count()
        )
        # self.visitors_compare_last_month = self.visitors.month * 100 if \
        #                                     self.visitors.last_month == 0 else \
        #                                     ((self.visitors.month / self.visitors.last_month)*100 if \
        #                                     self.visitors.month > self.visitors.last_month else \
        #                                         -(self.visitors.last_month / self.visitors.month)*100
        #                                     )

        self.visitors_compare_last_month = int((1-(self.visitors.last_month / (self.visitors.month if self.visitors.month > 0 else 1)))*100 if \
                                            self.visitors.last_month != 0 else self.visitors.month * 100)
        self.questions_compare_last_month = int((1-(self.questions.last_month / (self.visitors.month if self.visitors.month > 0 else 1)))*100 if \
                                            self.questions.last_month != 0 else self.questions.month * 100)
        self.question_views_compare_last_month = int((1-(self.question_views.last_month / (self.visitors.month if self.visitors.month > 0 else 1)))*100 if \
                                            self.question_views.last_month != 0 else self.question_views.month * 100)
        # (self.visitors.month / self.visitors.last_month)*100 if \
        #                                     self.visitors.last_month != 0 else \
        #                                         self.visitors.month * 100


        # self.data.question_views.count = QuestionView.query.count()
        # self.data.question_views.today = QuestionView.query_by_date(
        #     self.data.date.today).count()
        # self.data.question_views.month = QuestionView.query_by_month_year(
        #     self.data.date.year, self.data.date.month).count()
        # self.data.question_views.year = QuestionView.query_by_year(
        #     self.data.date.year).count()
        # self.data.question_views.yesterday = QuestionView.query_by_date(
        #     self.data.date.yesterday).count()
        # self.data.question_views.last_month = QuestionView.query_by_month_year(
        #     self.data.date.last_month.year, self.data.date.last_month.month).count()
        # self.data.question_views.last_year = QuestionView.query_by_year(
        #     self.data.date.last_year).count()

        # self.data.date.today = datetime.datetime.today().date()
        # self.data.date.day = self.data.date.today.day
        # self.data.date.month = self.data.date.today.month
        # self.data.date.year = self.data.date.today.year
        # self.data.date.last_month = (self.data.date.today.replace(
        #     day=1) - datetime.timedelta(days=1)).replace(day=1)
        # self.data.date.last_year = self.data.date.year - 1
        # self.data.date.yesterday = self.data.date.today - datetime.timedelta(1)
        # self.data.users.count = User.query.count()
        # self.data.users.today = User.query_by_date(
        #     self.data.date.today).count()
        # self.data.users.month = User.query_by_month_year(
        #     self.data.date.year, self.data.date.month).count()
        # self.data.users.year = User.query_by_year(self.data.date.year).count()
        # self.data.users.yesterday = User.query_by_date(
        #     self.data.date.yesterday).count()
        # self.data.users.last_month = User.query_by_month_year(
        #     self.data.date.last_month.year, self.data.date.last_month.month).count()
        # self.data.users.last_year = User.query_by_year(
        #     self.data.date.last_year).count()
        # self.data.questions.count = Question.query.count()
        # self.data.questions.today = Question.query_by_date(
        #     self.data.date.today).count()
        # self.data.questions.month = Question.query_by_month_year(
        #     self.data.date.year, self.data.date.month).count()
        # self.data.questions.year = Question.query_by_year(
        #     self.data.date.year).count()
        # self.data.questions.yesterday = Question.query_by_date(
        #     self.data.date.yesterday).count()
        # self.data.questions.last_month = Question.query_by_month_year(
        #     self.data.date.last_month.year, self.data.date.last_month.month).count()
        # self.data.questions.last_year = Question.query_by_year(
        #     self.data.date.last_year).count()
        # self.data.question_views.count = QuestionView.query.count()
        # self.data.question_views.today = QuestionView.query_by_date(
        #     self.data.date.today).count()
        # self.data.question_views.month = QuestionView.query_by_month_year(
        #     self.data.date.year, self.data.date.month).count()
        # self.data.question_views.year = QuestionView.query_by_year(
        #     self.data.date.year).count()
        # self.data.question_views.yesterday = QuestionView.query_by_date(
        #     self.data.date.yesterday).count()
        # self.data.question_views.last_month = QuestionView.query_by_month_year(
        #     self.data.date.last_month.year, self.data.date.last_month.month).count()
        # self.data.question_views.last_year = QuestionView.query_by_year(
        #     self.data.date.last_year).count()
