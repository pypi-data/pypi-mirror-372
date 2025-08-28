# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
from six import string_types
from xyz_util.mongoutils import Store

from xyz_util.datautils import access
from xyz_util.dateutils import format_the_date


class PointsSession(Store):
    name = 'points_session'

    def log(self, id, user_id, category, delta=1):
        vs = {}
        vs['category.%s.user.%s' % (category, user_id)] = delta
        self.inc({'id': int(id)}, vs)


class PointsSessionDaily(Store):
    name = 'points_session_daily'

    def log(self, id, user_id, the_date=None, delta=1):
        vs = {}
        d = format_the_date(the_date).isoformat()
        vs['user.%s' % user_id] = delta
        self.inc({'id': int(id), 'date': d}, vs)
