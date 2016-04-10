from uuid import uuid4
import hashlib
import re
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

        ####################################################
        # remove any keys in the payload that don't belong
        bad_keys = []
        for key in kwargs:
            if not key in cls.__dict__:
                bad_keys.append(key)
        for key in bad_keys:
            del kwargs[key]
        ####################################################

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
    gender = Column(UnicodeText, nullable=False)
    bio = Column(UnicodeText, nullable=False)
    birthday_datetime = Column(DateTime, nullable=False)
    zipcode = Column(UnicodeText, nullable=False)
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
    def create_new_user(cls, first, last, email, gender, bio, birthday_datetime, zipcode, password, user_type):

        #
        # gender:
        #  1 : male
        #  2 : female
        #  3 : rather not say
        #  4 : i don't know
        #  5 : yes.

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
            gender=gender,
            bio=bio,
            birthday_datetime=birthday_datetime,
            zipcode=zipcode,
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
        print('\nUser:\n')
        print(_user)
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
            print(_user.pass_hash == pass_hash)
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


    def to_dict(self, me=False, full=False):
        resp = super(Users, self).to_dict()
        resp.update(
            first=self.first,
            last=self.last,
            gender=self.gender,
            bio=self.bio,
            birthday_datetime=str(self.birthday_datetime).split(' ')[0],
        )
        if me:
            resp.update(
                token=self.token,
                token_expire_datetime=str(self.token_expire_datetime),
            )
        if full:
            resp.update(
                email=self.email,
                user_type=self.user_type,
                zipcode=self.zipcode,
                disabled=self.disabled,
            )
        return resp


class Groups(Base, TimeStampMixin, CreationMixin):

    __tablename__ = 'groups'
    creator_id = Column(ForeignKey('users.id'), nullable=False)
    title = Column(UnicodeText, nullable=False)
    topic = Column(UnicodeText, nullable=False)
    description = Column(UnicodeText, nullable=False)

    @classmethod
    def search_by_location(cls, lat, lng, radius, start=0, count=50):
        
        # 0.005 is ~ 0.25 miles
        _radius = float(radius) * 0.005

        top_left_lat = float(lat) + 90 - _radius
        top_left_lng = float(lng) + 180 - _radius
        bottom_right_lat = float(lat) + 90 + _radius
        bottom_right_lng = float(lng) + 180 + _radius

        DBSession.query(
            Groups,
        ).filter(
            ((top_left_lat < Beacons.lat + 90) &
                (top_left_lng < Beacons.lng + 180) &
                (bottom_right_lat > Beacons.lat + 90) &
                (bottom_right_lng > Beacons.lng + 180))
        ).slice(start, start+count).all()

        return groups

    def to_dict(self):
        resp = super(Groups, self).to_dict()
        resp.update(
            creator_id=str(self.creator_id),
            topic=self.topic,
            description=self.description,
        )
        return resp


class Beacons(Base, TimeStampMixin, CreationMixin):

    __tablename__ = 'beacons'
    creator_id = Column(ForeignKey('users.id'), nullable=False)
    group_id = Column(ForeignKey('groups.id'), nullable=True)
    title = Column(UnicodeText, nullable=False)
    topics = Column(UnicodeText, nullable=False)
    description = Column(UnicodeText, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    radius = Column(Integer, nullable=False)
    expire_datetime = Column(Integer, nullable=False)

    _creator = None
    _group = None
    #_topics = None

    @classmethod
    def _decode_beacon(cls, _beacon):
        beacon = _beacon[0]
        beacon._creator = _beacon[1]
        return beacon

    @classmethod
    def get_by_id(cls, _id):
        _beacon = DBSession.query(
            Beacons,
            Users,
            #Groups,
            #BeaconTopics,
            DBSession.query(
                BeaconTopics,
            ).filter(
                BeaconTopics.beacon_id == Beacons.id,
            ).label('topics')
        ).filter(
            Users.id == Beacons.creator_id,    
        #).filter(
        #    Groups.id == Beacons.group_id,
        #).filter(
        #    BeaconTopics.beacon_id == Beacons.id,
        ).first()

        return Beacons._decode_beacon(_beacon)

    @classmethod
    def get_paged(cls, start=0, count=50):
        _beacons = DBSession.query(
            Beacons,
            Users,
            #Groups,
        ).filter(
            Users.id == Beacons.creator_id,
        #).filter(
        #    Groups.id == Beacons.group_id,
        ).slice(start, start+count)

        beacons = []
        for _beacon in _beacons:
            beacons.append(Beacons._decode_beacon(_beacon))

        return beacons

    @classmethod
    def get_by_location(cls, lat, lng, radius, start=0, count=50):

        # 0.005 is ~ 0.25 miles
        _radius = float(radius) * 0.005

        top_left_lat = float(lat) + 90 - _radius
        top_left_lng = float(lng) + 180 - _radius
        bottom_right_lat = float(lat) + 90 + _radius
        bottom_right_lng = float(lng) + 180 + _radius

        _beacons = DBSession.query(
            Beacons,
            Users,
            #Groups,
        ).filter(
            Users.id == Beacons.creator_id,
        #).filter(
        #    Groups.id == Beacons.group_id,
        ).filter(
            BeaconTopics.beacon_id == Beacons.id,
        ).join(
            BeaconTopics, BeaconTopics.beacon_id == Beacons.id,
        ).filter(
            ((top_left_lat < Beacons.lat + 90) &
                (top_left_lng < Beacons.lng + 180) &
                (bottom_right_lat > Beacons.lat + 90) &
                (bottom_right_lng > Beacons.lng + 180))
        ).slice(start, start+count).all()

        print('\n\n')
        print(_beacons)

        beacons = []
        for _beacon in _beacons:
            beacons.append(Beacons._decode_beacon(_beacon))
        
        return beacons    


    @classmethod
    def search_by_location(cls, lat, lng, radius, start=0, count=50):

        # 0.005 is ~ 0.25 miles
        _radius = float(radius) * 0.005

        top_left_lat = lat + 90 - _radius
        top_left_lng = lng + 180 - _radius
        bottom_right_lat = lat + 90 + _radius
        bottom_right_lng = lng + 180 + _radiu        

        _beacons = DBSession.query(
            Beacons,
            Users,
            #Groups,
        ).filter(
            Users.id == Beacons.creator_id,
        #).filter(
        #    Groups.id == Beacons.group_id,
        ).join(
            BeaconTopics, BeaconTopics.beacon_id == Beacons.id,
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

    @classmethod
    def search_by_topic(cls, topic, lat, lng, radius, start=0, count=50):

        # 0.005 is ~ 0.25 miles
        _radius = float(radius) * 0.005

        top_left_lat = float(lat) + 90 - _radius
        top_left_lng = float(lng) + 180 - _radius
        bottom_right_lat = float(lat) + 90 + _radius
        bottom_right_lng = float(lng) + 180 + _radius

        _beacons = DBSession.query(
            Beacons,
            Users,
            #Groups,
        ).filter(
            Users.id == Beacons.creator_id,
        #).filter(
        #    Groups.id == Beacons.group_id,
        ).join(
            BeaconTopics, BeaconTopics.beacon_id == Beacons.id,
        ).filter(
            BeaconTopics.beacon_id == Beacons.id,
        ).filter(
            BeaconTopics.topic == topic,
        ).filter(
            ((top_left_lat < Beacons.lat + 90) &
                (top_left_lng < Beacons.lng + 180) &
                (bottom_right_lat > Beacons.lat + 90) &
                (bottom_right_lng > Beacons.lng + 180))
        ).slice(start, start+count).all()

        beacons = []
        for _beacon in _beacons:
            beacons.append(Beacons._decode_beacon(_beacon))
        
        return beacons    

    def to_dict(self):
        resp = super(Beacons, self).to_dict()

        resp.update(
            creator_id=str(self.creator_id),
            creator=self._creator.to_dict() if self._creator else None,
            group_id=str(self.group_id),
            #group=self._group.to_dict() if self._group else None,
            #topics=[t.to_dict() for t in self._topics] if self._topics else None,
            title=self.title,
            topics=re.sub(' +', ' ', self.topics).split(' '),
            description=self.description,
            lat=self.lat,
            lng=self.lng,
            radius=self.radius,
            expire_datetime=str(self.expire_datetime),
        )
        return resp


class BeaconTopics(Base, TimeStampMixin, CreationMixin):

    __tablename__ = 'beacon_topics'
    beacon_id = Column(ForeignKey('beacons.id'))
    topic = Column(UnicodeText, nullable=False)

    def to_dict(self):
        resp = super(BeaconTopics, self).to_dict()
        resp.update(
            beacon_id=str(self.beacon_id),
            topic=str(self.topic),
        )
        return resp