from uuid import uuid4
import hashlib

from time import sleep
from random import randint
import datetime

from sqlalchemy.sql import func
from sqlalchemy_utils import UUIDType
from sqlalchemy import (
    Column,
    cast,
    Date,
    ForeignKey,
    Integer,
    Float,
    NUMERIC,
    Boolean,
    UnicodeText,
    DateTime,
    Index,
    CHAR,
    distinct,
    func,
    desc,
    asc,
    or_,
)

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    relationship,
    scoped_session,
    sessionmaker,
)

DBSession = scoped_session(sessionmaker(expire_on_commit=False))
Base = declarative_base()


class TimeStampMixin(object):
    creation_datetime = Column(DateTime, server_default=func.now())
    modified_datetime = Column(DateTime, server_default=func.now())


class CreationMixin():

    id = Column(UUIDType(binary=False), primary_key=True, unique=True)

    @classmethod
    def add(cls, **kwargs):
        thing = cls(**kwargs)
        if thing.id is None:
            thing.id = str(uuid4())
        DBSession.add(thing)
        DBSession.commit()
        return thing

    @classmethod
    def get_all(cls):
        things = DBSession.query(
            cls,
        ).all()
        return things

    @classmethod
    def get_paged(cls, start=0, count=25):
        things = DBSession.query(
            cls,
        ).slice(start, start+count).all()
        return things

    @classmethod
    def get_by_id(cls, id):
        thing = DBSession.query(
            cls,
        ).filter(
            cls.id == id,
        ).first()
        return thing

    @classmethod
    def delete_by_id(cls, id):
        thing = cls.get_by_id(id)
        if thing is not None:
            DBSession.delete(thing)
            DBSession.commit()
        return thing

    @classmethod
    def update_by_id(cls, id, **kwargs):
        keys = set(cls.__dict__)
        thing = DBSession.query(cls).filter(cls.id==id).first()
        if thing is not None:
            for k in kwargs:
                if k in keys:
                    setattr(thing, k, kwargs[k])
            thing.modified_datetime = datetime.datetime.now()
            DBSession.add(thing)
            DBSession.commit()
        return thing

    @classmethod
    def reqkeys(cls):
        keys = []
        for key in cls.__table__.columns:
            if '__required__' in type(key).__dict__:
                keys.append(str(key).split('.')[1])
        return keys

    def to_dict(self):
        return {
            'id': str(self.id),
            'creation_datetime': str(self.creation_datetime),
        }


class Users(Base, TimeStampMixin, CreationMixin):

    __tablename__ = 'users'

    first = Column(UnicodeText, nullable=False)
    last = Column(UnicodeText, nullable=False)
    email = Column(UnicodeText, nullable=False)
    pass_salt = Column(UnicodeText, nullable=False)
    pass_hash = Column(UnicodeText, nullable=False)
    user_type = Column(Integer, nullable=False)
    token = Column(UnicodeText, nullable=True)
    token_expire_datetime = Column(DateTime, nullable=True)
    disabled = Column(Boolean, nullable=False)

    def generate_api_key(self):
        self.api_key = str(salt_bytes = hashlib.sha256(str(uuid4()).encode('utf-8')).hexdigest())
        Users.update_by_id(self.id, **self.__dict__)
        return self

    @classmethod
    def create_new_user(cls, first, last, email, password, user_type):

        '''
        user_type:
            admin
            service_sales_manager
            national_service_manager
            regional_service_manager
        '''

        user = None
        salt_bytes = hashlib.sha256(str(uuid4()).encode('utf-8')).hexdigest()
        pass_bytes = hashlib.sha256(password.encode('utf-8')).hexdigest()
        pass_val = pass_bytes + salt_bytes
        pass_hash = hashlib.sha256(pass_val.encode('utf-8')).hexdigest()
        user = Users.add(
            #is_admin= is_admin,
            first=first,
            last=last,
            email=email,
            pass_salt=salt_bytes,
            pass_hash=pass_hash,
            user_type=user_type,
            token=None,
            token_expire_datetime=None,
            disabled=False,
        )
        return user

    @classmethod
    def get_by_token(cls, token):
        user = DBSession.query(
            Users,
        ).filter(
            Users.token == token,
        ).first()
        return user


    @classmethod
    def get_by_email(cls, email):
        user = DBSession.query(
            Users,
        ).filter(
            Users.email == email,
        ).first()
        return user


    @classmethod
    def get_by_user_type(cls, user_type):
        user = DBSession.query(
            Users,
        ).filter(
            Users.user_type == user_type,
        ).first()
        return user


    @classmethod
    def authenticate(cls, email, password):
        _user = Users.get_by_email(email)
        user = None
        if _user is not None:
            if isinstance(_user.pass_salt, bytes):
                salt_bytes = _user.pass_salt.decode('utf-8')
            elif isinstance(_user.pass_salt, str):
                salt_bytes = _user.pass_salt
            else:
                salt_bytes = _user.pass_salt
            pass_bytes = hashlib.sha256(password.encode('utf-8')).hexdigest()
            pass_val = pass_bytes + salt_bytes
            pass_hash = hashlib.sha256(pass_val.encode('utf-8')).hexdigest()
            if (_user.pass_hash == pass_hash):
                token = str(uuid4())
                # does not expire for 10 years
                token_expire_datetime = datetime.datetime.now() + datetime.timedelta(hours=24*365*10)
                user = Users.update_by_id(
                    _user.id,
                    token=token,
                    token_expire_datetime=token_expire_datetime,
                )
        return user


    @classmethod
    def validate_token(cls, token):
        user = Users.get_by_token(token)
        valid = False
        if user != None:
            if user.token_expire_datetime > datetime.datetime.now():
                valid = True
        return valid, user


    @classmethod
    def invalidate_token(cls, token):
        user = Users.get_by_token(token)
        if user != None:
            user = Users.update_by_id(
                user.id,
                token=None,
                token_expire_datetime=None,
            )
        return user


    def to_dict(self):
        resp = super(Users, self).to_dict()
        resp.updte(
            first = self.first,
            last = self.last,
            email = self.email,
            user_type = self.user_type,
            token = self.token,
            token_expire_datetime = str(self.token_expire_datetime),
        )
        return resp


class Topics(Base, TimeStampMixin, CreationMixin):

    __tablename__ = 'topics'
    topic = Column(UnicodeText, nullable=False)

    def to_dict(self):
        resp = super(Topics, self).to_dict()
        resp.update(
            topic=self.topic,
        )


class Groups(Base, TimeStampMixin, CreationMixin):

    __tablename__ = 'groups'
    creator_id = Column(ForeignKey('users.id'), nullable=False)
    topic = Column(UnicodeText, nullable=False)
    description = Column(UnicodeText, nullable=False)

    def to_dict(self):
        resp = super(Groups, self).to_dict()
        resp.update(
            creator_id=self.creator_id,
            topic=self.topic,
            description=self.description,
        )
        return resp


class Beacons(Base, TimeStampMixin, CreationMixin):

    __tablename__ = 'beacons'
    creator_id = Column(ForeignKey('users.id'), nullable=False)
    group_id = Column(ForeignKey('groups.id'), nullable=True)
    description = Column(UnicodeText, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    radius = Column(Integer, nullable=False)
    expires = Column(Integer, nullable=False) # number of fifteen minute intervals

    group = None
    topics = None

    @classmethod
    def _decode_beacon(cls, _beacon):
        # pulls out the Beacons, Groups, and BeaconTopics objects from the tuple
        beacon = _beacons[0]
        beacon.group = _beacons[1]
        beacon.topics = _beacons[2]
        return beacon

    @classmethod
    def get_by_id(cls, _id):
        _beacon = DBSession.query(
            Beacons,
            Groups,
            BeaconTopics,
        ).filter(
            Groups.id == Beacons.group_id,
        ).filter(
            BeaconTopics.beacon_id == Beacons.id,
        ).first()

        return Beacons._decode_beacon(_beacon)

    @classmethod
    def get_paged(cls, start=0, count=50):
        _beacons = DBSession.query(
            Beacons,
            Groups,
            BeaconTopics,
        ).filter(
            Groups.id == Beacons.group_id,
        ).filter(
            BeaconTopics.beacon_id == Beacons.id,
        ).slice(start, start+count)

        beacons = []
        for _beacon in _beacons:
            beacons.append(Beacons._decode_beacon(_beacon))

        return beacons

    @classmethod
    def search_by_location(cls, lat, lng, radius, start=0, count=50):

        #
        # before you read the below code: it doesn't matter.  really.
        #
        # 0.02 is ~ 1 mile, so 0.005 is ~0.25 miles.
        # we support radius values of ..
        #     1  = 0.25 miles
        #     2  = 0.5  miles
        #     4  = 1    miles
        #     8  = 2    miles
        #     20 = 5    miles
        _radius = radius * 0.005

        top_left_lat = lat + 90 - _radius
        top_left_lng = lng + 180 - _radius
        bottom_right_lat = lat + 90 + _radius
        bottom_right_lng = lng + 180 + _radiu        

        _beacons = DBSession.query(
            Beacons,
            Groups,
            BeaconTopics,
        ).filter(
            Groups.id == Beacons.group_id,
        ).filter(
            BeaconTopics.beacon_id == Beacons.id,
        ).filter(
            ((top_left_lat + 90 > Beacons.lat + 90) &
                (top_left_lng + 180 < Beacons.lng + 180) &
                (bottom_right_lat + 90 < Beacons.lat + 90) &
                (bottom_right_lng + 180 > Beacons.lng + 180))
        ).slice(start, start+count)

        beacons = []
        for _beacon in _beacons:
            beacons.append(Beacons._decode_beacon(_beacon))

        return beacons

    def to_dict(self):
        resp = super(Beacons, self).to_dict()
        resp.update(
            creator_id=self.creator_id,
            creator=self.creator,
            group_id=self.group_id,
            group=self.group,
            description=self.description,
            lat=self.lat,
            lng=self.lng,
            radius=self.radius,
            expire_datetime=str(self.expire_datetime),
        )
        return resp


class BeaconTopics(Base, TimeStampMixin, CreationMixin):

    __tablename__ = 'beacon_topics'
    beacon_id = Column(ForeignKey('beacon.id'))
    topic = Column(UnicodeText, nullable=False)

    def to_dict(self):
        resp = super(BeaconTopics, self).to_dict()
        resp.update(
            beacon_id=self.beacon_id,
            topic=self.topic,
        )
        return resp