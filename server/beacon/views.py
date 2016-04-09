from pyramid.response import Response
from pyramid.view import view_defaults
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Users,
    Topics,
    Groups,
    Beacons,
    BeaconTopics,
)

import json

import datetime

def get_payload(request):
    try:
        payload = request.json_body
        #for key in payload:
        #    if '_datetime' in key:
        #        payload[key] = datetime.datetime.strptime(payload[key], '%m/%d/%Y')
    except:
        payload = None
    return payload


def build_paging(request):
    start = 0
    count = 50
    if 'start' in request.GET and 'count' in request.GET:
        try:
            start = int(float(request.GET['start']))
            count = int(float(request.GET['count']))
            if count > 1000:
                count = 1000
        except:
            start = 0
            count = 50
    return start, count


def authenticate(request):
    token = None
    user = None
    try:
        token = request.session['token']
    except:
        try:
            token = request.GET['token']
        except:
            pass
    if token:
        user = Users.get_by_token(token)
    return user 

class BaseRequest(object):

    def __init__(self, request):
        self.request = request
        self.start, self.count = build_paging(request)
        self.user = authenticate(request)
        self.payload = get_payload(request)

    def auth(self, needs_admin=False):
        if self.user:
            if needs_admin:
                if self.user.user_type == 'admin':
                    return True
            else:
                return True
        self.request.response.status = 403
        return False

    def validate(self):
        print('\n\nPAYLOAD\n\n')
        print(self.payload)
        print(self.req)
        if self.payload and all(r in self.payload for r in self.req):
            return True
        self.request.response.status = 400
        return False

    def _get(self):
        resp = {}
        id = self.request.matchdict['id']
        thing = self.cls.get_by_id(id)
        if thing:
            resp = thing.to_dict()
        return resp

    def _get_collection(self):
        resp = []
        things = self.cls.get_paged(self.start, self.count)
        if things:
            if 'type' in self.request.GET and self.request.GET['type'] == 'tsv':
                resp = Response('\n'.join([t.to_tsv() for t in things]))
            elif 'type' in self.request.GET and self.request.GET['type'] == 'for_macro':
                resp = Response('\t'.join([json.dumps(t.to_dict()) for t in things]))
            else:
                resp = Response(json.dumps([t.to_dict() for t in things]), content_type='application/json')
        else:
            self.request.response.status = 404
        return resp    

    def _post(self):
        resp = {}
        if self.validate():
            thing = self.cls.add(**self.payload)
            if thing:
                resp = thing.to_dict()
            else:
                self.request.response.status = 500
        return resp

    def _put(self):
        resp = {}
        if self.validate():
            id = self.request.matchdict['id'].replace('-','')
            thing = self.cls.update_by_id(id, **self.payload)
            if thing:
                resp = thing.to_dict()
            else:
                self.request.response.status = 404
        return resp

    def _delete(self):
        resp = {}
        id = self.request.matchdict['id']
        thing = self.cls.delete_by_id(id)
        if thing:
            resp = thing.to_dict()
        else:
            self.request.response.status = 404
        return resp

@view_defaults(route_name='/')
class Index(object):

    def __init__(self, request):
        self.request = request

    @view_config(request_method='GET', renderer='templates/index.mak')
    def get(self):
        return {}


@view_defaults(route_name='/api/users/login', renderer='json')
class UserLoginAPI(BaseRequest):

    req = (
        'email',
        'password',
    )

    def __init__(self, request):
        super(UserLoginAPI, self).__init__(request)

    #[ GET ] - check if logged in
    @view_config(request_method='GET')
    def get(self):
        resp = {'loggedin': False}
        if self.user:
            resp = {'loggedin': True, 'user': self.user.to_dict()}
        return resp

    #[ POST ] - perform login
    @view_config(request_method='POST')
    def post(self):
        resp = {}
        if self.validate():
            email = self.payload['email']
            password = self.payload['password']
            self.user = Users.authenticate(email, password)
            if self.auth():
                self.request.session['token'] = self.user.token
                _user = self.user.to_dict()
                _user.update(token=self.user.token)
                resp = _user
        return resp


@view_defaults(route_name='/api/users/logout', renderer='json')
class UserLogoutAPI(BaseRequest):


    def __init__(self, request):
        super(UserLogoutAPI, self).__init__(request)

    #[ POST ] - logs the user out
    @view_config(request_method='POST')
    def post(self):
        resp = {}
        if 'token' in self.request.session:
            token = self.request.session['token']
            if token:
                user = Users.invalidate_token(token)
                if not user:
                    self.request.response.status = 403
        return resp  


@view_defaults(route_name='/api/users', renderer='json')
class UsersAPI(BaseRequest):

    req = (
        'first',
        'last',
        'email',
        'password',
        'user_type',
    )

    def __init__(self, request):
        super(UsersAPI, self).__init__(request)

    #[ GET ]
    @view_config(request_method='GET')
    def get(self):
        resp = {'users': []}
        if self.auth(needs_admin=True):
            _users = Users.get_paged(self.start, self.count)
            resp = [u.to_dict() for u in _users]
        return resp

    #[ POST ]
    @view_config(request_method='POST')
    def post(self):
        resp = {}
        if self.auth(needs_admin=True):
            if self.validate():
                user = Users.create_new_user(
                    first=self.payload['first'],
                    last=self.payload['last'],
                    email=self.payload['email'],
                    password=self.payload['password'],
                    user_type=self.payload['user_type']
                )
                if user:
                    resp = user.to_dict()
                    self.request.response.status = 201
                else:
                    self.request.response.status = 500
        return resp


@view_defaults(route_name='/api/users/{id}', renderer='json')
class UserAPI(BaseRequest):

    req = (
        'first',
        'last',
        'email',
        'user_type',
    )

    cls = Users

    def __init__(self, request):
        super(UserAPI, self).__init__(request)

    #[ PUT ]
    @view_config(request_method='PUT')
    def put(self):
        resp = {}
        if self.auth():
            resp = self._put()
        return resp

    #[ DELETE ]
    @view_config(request_method='DELETE')
    def delete(self):
        resp = {}
        if self.auth():
            resp = self._delete()
        return resp


@view_defaults(route_name='/api/topics')
class TopicsAPI(BaseRequest):

    cls = Topics

    def __init__(self, request):
        super(TopicsAPI, self).__init__(request)

    #[ GET ]
    @view_config(request_method='GET')
    def get(self):
        resp = {}
        if self.auth():
            resp = self._get_collection()
        return resp

'''
@view_defaults(route_name='/api/topics/{id}', renderer='json')
class TopicAPI(BaseRequest):

    req = (
        'topic',
    )

    cls = Topics

    def __init__(self, request):
        super(TopicAPI, self).__init__(request)

    #[ GET ]
    @view_config(request_method='GET')
    def get(self):
        resp = {}
        if self.auth():
            resp = self._get()
        return resp

    #[ PUT ]
    @view_config(request_method='PUT')
    def put(self):
        resp = {}
        if self.auth():
            resp = self._put()
        return resp

    #[ DELETE ]
    @view_config(request_method='DELETE')
    def delete(self):
        resp = {}
        if self.auth():
            resp = self._delete()
        return resp
'''


@view_defaults(route_name='/api/groups')
class GroupsAPI(BaseRequest):

    req = (
        #'creator_id',
        'topic',
        'description',
    )

    cls = Groups

    def __init__(self, request):
        super(GroupsAPI, self).__init__(request)

    #[ GET ]
    @view_config(request_method='GET')
    def get(self):
        resp = {}
        if self.auth():
            resp = self._get_collection()
        return resp

    #[ POST ]
    @view_config(request_method='POST', renderer='json')
    def post(self):
        resp = {}
        if self.auth():
            resp = self._post()
        return resp


@view_defaults(route_name='/api/groups/{id}', renderer='json')
class GroupAPI(BaseRequest):

    req = (
        #'creator_id',
        'topic',
        'description',
    )

    cls = Groups

    def __init__(self, request):
        super(GroupAPI, self).__init__(request)

    #[ GET ]
    @view_config(request_method='GET')
    def get(self):
        resp = {}
        if self.auth():
            resp = self._get()
        return resp

    #[ PUT ]
    @view_config(request_method='PUT')
    def put(self):
        resp = {}
        if self.auth():
            resp = self._put()
        return resp

    #[ DELETE ]
    @view_config(request_method='DELETE')
    def delete(self):
        resp = {}
        if self.auth():
            resp = self._delete()
        return resp


@view_defaults(route_name='/api/beacons')
class BeaconsAPI(BaseRequest):

    req = (
        #'creator_id',
        #'group_id',
        'description',
        'lat',
        'lng',
        'radius',
        #'expire_datetime',
    )

    cls = Beacons

    def __init__(self, request):
        super(BeaconsAPI, self).__init__(request)

    #[ GET ]
    @view_config(request_method='GET')
    def get(self):
        resp = {}
        if self.auth():
            resp = self._get_collection()
        return resp

    #[ POST ]
    @view_config(request_method='POST', renderer='json')
    def post(self):
        resp = {}
        if self.auth():
            resp = self._post()
        return resp


@view_defaults(route_name='/api/beacons/{id}', renderer='json')
class BeaconAPI(BaseRequest):

    req = (
        #'creator_id',
        #'group_id',
        'description',
        'lat',
        'lng',
        'radius',
        'expires',
    )

    cls = Beacons

    def __init__(self, request):
        super(BeaconAPI, self).__init__(request)

    #[ GET ]
    @view_config(request_method='GET')
    def get(self):
        resp = {}
        if self.auth():
            resp = self._get()
        return resp

    #[ PUT ]
    @view_config(request_method='PUT')
    def put(self):
        resp = {}
        if self.auth():
            resp = self._put()
        return resp

    #[ DELETE ]
    @view_config(request_method='DELETE')
    def delete(self):
        resp = {}
        if self.auth():
            resp = self._delete()
        return resp