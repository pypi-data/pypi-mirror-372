import logging
import sys
from collections import OrderedDict

from typing import Any, Final, List

from .utils import random_password
from .rgw import RGWAdmin
from .exceptions import NoSuchKey

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

log: Final = logging.getLogger(__name__)


class AttributeMixin(object):
    attrs: List[str] = []

    def __str__(self) -> str:
        try:
            from qav.listpack import ListPack
        except ImportError:
            return str(self.to_tuples())
        return str(ListPack(self.to_tuples()))

    def to_tuples(self) -> list:
        return [(x, getattr(self, x)) for x in self.attrs]

    def to_dict(self) -> dict:
        return dict(self.to_tuples())


class RGWCap(AttributeMixin):
    attrs = ['type', 'perm']

    def __init__(self, type: str, perm: str) -> None:
        self.type = type
        self.perm = perm

    def __repr__(self) -> str:
        return str('%s %s' % (self.__class__.__name__, self.type))


class RGWKey(AttributeMixin):
    attrs = ['user', 'access_key', 'secret_key']

    def __init__(self, user: str, access_key: str, secret_key: str) -> None:
        self.user = user
        self.access_key = access_key
        self.secret_key = secret_key

    def __repr__(self) -> str:
        return str('%s %s' % (self.__class__.__name__, self.user))

    @classmethod
    def generate(cls, user: str, access_size: int = 20, secret_size: int = 40) -> Self:
        access_key = random_password(size=access_size)
        secret_key = random_password(size=secret_size)
        return cls(user, access_key, secret_key)


class RGWSubuser(AttributeMixin):
    attrs = ['id', 'permissions']
    permission_list = ['read', 'write', 'read-write', 'full-control']

    def __init__(self, id: str, permissions: str) -> None:
        self.id = id
        self.permissions = permissions

    def __repr__(self) -> str:
        return str('%s %s' % (self.__class__.__name__, self.id))

    @property
    def permissions(self) -> str:
        return self._permissions

    @permissions.setter
    def permissions(self, value: str) -> None:
        if value in self.permission_list:
            self._permissions = value
        elif value == '<none>':
            self._permissions = None
        else:
            raise AttributeError


class RGWSwiftKey(AttributeMixin):
    attrs = ['user', 'secret_key']

    def __init__(self, user: str, secret_key: str) -> None:
        self.user = user
        self.secret_key = secret_key

    def __repr__(self) -> str:
        return str('%s %s' % (self.__class__.__name__, self.user))

    @classmethod
    def generate(cls, user: str, secret_size: int = 40) -> Self:
        secret_key = random_password(size=secret_size)
        return cls(user, secret_key)


class RGWQuota(AttributeMixin):
    attrs = ['enabled', 'max_objects', 'max_size_kb']
    defaults = OrderedDict([('enabled', False), ('max_objects', -1), ('max_size_kb', -1)])

    def __init__(self, **kwargs: Any) -> None:
        for attr in self.attrs:
            setattr(self, attr, kwargs[attr])

    def __repr__(self) -> str:
        return '%s %s/%s' % (self.enabled, self.max_objects, self.string_size())

    def string_size(self) -> int | str:
        weights = ['KB', 'MB', 'GB', 'TB', 'PB']
        size = int(self.max_size_kb)
        weight = 0
        if size < 0:
            return size
        while True:
            if size < 1024 or weight == len(weights):
                return str('%s%s' % (size, weights[weight]))
            else:
                size = size / 1024
                weight += 1

    @classmethod
    def default(cls) -> Self:
        return cls(**cls.defaults)

    @property
    def size(self) -> int:
        return int(self.max_size_kb) * 1000

    @size.setter
    def size(self, new_size: int) -> None:
        self.max_size_kb = int(new_size) / 1000


class RGWUser(AttributeMixin):
    attrs = ['user_id', 'display_name', 'email', 'caps', 'keys',
             'max_buckets', 'suspended', 'swift_keys', 'subusers',
             'placement_tags', 'bucket_quota', 'user_quota',
             'default_placement', 'op_mask', 'temp_url_keys']
    modify_attrs_mask = ['placement_tags', 'default_placement', 'op_mask', 'temp_url_keys']
    sub_attrs = OrderedDict([('caps', RGWCap),
                             ('keys', RGWKey),
                             ('swift_keys', RGWSwiftKey),
                             ('subusers', RGWSubuser),
                             ('bucket_quota', RGWQuota),
                             ('user_quota', RGWQuota)])

    """Representation of a RadosGW User"""

    def __init__(self, **kwargs: Any) -> None:
        self.sensitive_attrs = [('keys', 'secret_key')]
        for attr in self.attrs:
            setattr(self, attr, kwargs[attr])
        if kwargs.get('sensitive_attrs'):
            self.sensitive_attrs.append(kwargs.get('sensitive_attrs'))

    def __repr__(self) -> str:
        return str('%s %s' % (self.__class__.__name__, self.user_id))

    @classmethod
    async def create(cls, user_id: str, display_name: str, **kwargs: Any) -> Self | None:
        rgw = RGWAdmin.get_connection()
        log.debug('Creating user %s' % user_id)
        await rgw.create_user(uid=user_id, display_name=display_name, **kwargs)
        return await cls.fetch(user_id)

    async def diff(self) -> dict:
        rgw = RGWAdmin.get_connection()
        d = {}
        current = self.to_dict()
        try:
            existing = await rgw.get_metadata('user', self.user_id)['data']
        except NoSuchKey:
            logging.info('Unable to fetch the user %s.' % self.user_id)
            return current
        for k in current.keys():
            if k in existing.keys():
                if current[k] != existing[k]:
                    d[k] = (existing[k], current[k])
        return d

    async def exists(self) -> bool:
        """Return True if the user exists.  False otherwise."""
        rgw = RGWAdmin.get_connection()
        try:
            await rgw.get_metadata('user', self.user_id)
            return True
        except NoSuchKey:
            return False

    async def save(self) -> None:
        rgw = RGWAdmin.get_connection()

        if not await self.exists():
            log.debug('User does not exist. Creating %s' % self.user_id)
            await rgw.create_user(uid=self.user_id, display_name=self.display_name)

        d = self._modify_dict()
        log.debug('Modify existing user %s %s' % (self.user_id, d))
        await rgw.modify_user(**d)
        await rgw.set_user_quota(self.user_id, 'user', **self.user_quota.to_dict())
        await rgw.set_user_quota(self.user_id, 'bucket', **self.bucket_quota.to_dict())

    async def delete(self) -> Any:
        rgw = RGWAdmin.get_connection()
        try:
            await rgw.get_metadata('user', self.user_id)
        except NoSuchKey:
            logging.error('User %s does not exist yet aborting.' % self.user_id)
            return False
        logging.info('Deleting user %s from %s' % (self.user_id, rgw.get_base_url()))
        return await rgw.remove_user(uid=self.user_id)

    @classmethod
    async def list(cls) -> list:
        rgw = RGWAdmin.get_connection()
        return [await cls.fetch(x) for x in await rgw.get_users()]

    @classmethod
    async def fetch(cls, user: str) -> Self | None:
        log.debug('Fetching user %s' % user)
        rgw = RGWAdmin.get_connection()
        try:
            j = await rgw.get_metadata('user', user)
        except NoSuchKey:
            return None
        else:
            return cls._parse_user(j['data'])

    @classmethod
    def _parse_user(cls, rgw_user: Any) -> Self | None:
        # we expect to be passed a dict
        if type(rgw_user) is not dict:
            log.warning('rgw_user is not a dict instance')
            return None
        # check to make sure we have all the correct keys
        if not set([str(x) for x in cls.attrs]) <= \
                set(rgw_user.keys()):
            return None
        log.debug('Parsing RGWUser %s' % rgw_user)
        for subattr in cls.sub_attrs.keys():
            log.debug('Loading attribute %s with class %s' %
                      (subattr, cls.sub_attrs[subattr].__name__))
            if type(rgw_user[subattr]) is list:
                obj = [cls.sub_attrs[subattr](**x) for x in rgw_user[subattr]]
            elif type(rgw_user[subattr]) is dict:
                obj = cls.sub_attrs[subattr](**rgw_user[subattr])
            else:
                obj = rgw_user[subattr]
            rgw_user[subattr] = obj
        return cls(**rgw_user)

    def _scrubbed_dict(self) -> dict:
        '''Return a dict representation of the object with sensitve attrs
           filtered.
        '''
        scrubbed = self.to_dict()
        censor = '******'
        for k, v in self.sensitive_attrs:
            if type(scrubbed[k]) is list:
                for o in scrubbed[k]:
                    o[v] = censor
            else:
                scrubbed[k] = censor
        return scrubbed

    def _modify_dict(self) -> dict:
        '''Return flat dict representation of the object'''
        d = {}
        for attr in self.attrs:
            if attr not in self.modify_attrs_mask+list(self.sub_attrs.keys()):
                d[attr] = getattr(self, attr)
        d['uid'] = d.pop('user_id')
        d['generate_key'] = False
        return d

    def to_dict(self) -> dict:
        '''Return the dict representation of the object'''
        d = {}
        for attr in self.attrs:
            if attr in self.sub_attrs.keys():
                if type(getattr(self, attr)) is list:
                    d[attr] = []
                    for o in getattr(self, attr):
                        d[attr].append(o.to_dict())
                else:
                    d[attr] = getattr(self, attr).to_dict()
            else:
                d[attr] = getattr(self, attr)
        return d
