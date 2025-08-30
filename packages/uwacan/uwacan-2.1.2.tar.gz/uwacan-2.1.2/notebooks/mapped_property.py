# %%
class DefaultDict(dict):
    def __init__(self, default_value, **kwargs):
        super().__init__(**kwargs)
        self.default_value = default_value

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            return self.default_value

class DictMapper:
    def __init__(self, preprocessor):
        self.name = preprocessor.__name__
        self.preprocessor = preprocessor

    def __get__(self, owner, owner_class=None):
        data = getattr(owner, '_' + self.name)
        if isinstance(data, DefaultDict):
            return data.default_value
        return data
        # if not isinstance(owner.identifiers, list):
            # data, = data.values()
        return data

    def __set__(self, owner, data):
        try:
            # Multiple data
            data = {key: self.preprocessor(owner, val) for key, val in data.items()}
            # multiple_data = True
        except AttributeError as err:
            if str(err).endswith("object has no attribute 'items'"):
                data = self.preprocessor(owner, data)
                data = DefaultDict(data)
                # multiple_data = False
            else:
                raise

        # if isinstance(owner.identifiers, list):
        #     if multiple_data:
        #         data = {key: data[key] for key in owner.identifiers}
        #     else:
        #         data = {key: data for key in owner.identifiers}
        # else:
        #     if multiple_data:
        #         data = data[owner.identifiers]
        #     data = {owner.identifiers: data}
        setattr(owner, '_' + self.name, data)
        # setattr(owner, '_DictMapper__' + self.name, multiple_data)


class PlainDictInterface:
    def __init__(self, identifiers=None):
        self.identifiers = identifiers

    @property
    def identifiers(self):
        ids = self._identifiers
        if len(ids) == 0:
            return None
        if len(ids) == 1:
            return ids[0]
        return ids

    @identifiers.setter
    def identifiers(self, identifiers):
        if identifiers is None or isinstance(identifiers, str):
            identifiers = [identifiers]
        else:
            try:
                iter(identifiers)
            except TypeError as err:
                if str(err).endswith('object is not iterable'):
                    # identifiers = str(identifiers)
                    identifiers = [identifiers]
                else:
                    raise
                identifiers = list(identifiers)
        self._identifiers = identifiers

    @DictMapper
    def x(self, val):
        return val + ', preprocessed'

# %%
# This almost works! If we only send a single data in, we rig a tiny dict subclass which returns the same value for all keys.
# This is the "private" data, so we can use it to get properties for all the id keys in the internal code without hassle.
# If we send multiple data in, we store a normal dictionary that is used for both the public and private access.
# The only remaining issue is how we want to deal with keys that are strings but should be ints? Is this just a bad idea and we should leave all the keys as is?
# Alternate solution is to make a second dict subclass that we use when we have multiple data, which tests the key as a string as well?
i = PlainDictInterface(5)
i.x = {5: 'five', 3: 'three'}
print(i._x)
print(i.x)
print(i._x[5])

# %%
class Container:
    def __init__(self, data, multiple_data):
        print(f'__init__ in container, {data = }, {multiple_data = }')
        self.data = data
        self.multiple_data = multiple_data

    def __get__(self, owner, owner_class=None):
        print(f'__get__ in container')
        return self

    def __getitem__(self, key):
        print(f'__getitem__ in container')
        if self.multiple_data:
            return self.data[str(key)]
        return self.data

    def __setitem__(self, key, value):
        print(f'__setitem__ in container')
        if self.multiple_data:
            self.data[str(key)] = value


class Mapper:
    def __init__(self, preprocessor):
        self.name = preprocessor.__name__
        self.preprocessor = preprocessor

    def __get__(self, owner, owner_class=None):
        print(f'__get__ in Mapper: {self.name}')
        data = getattr(owner, '_' + self.name)
        return data.data

    def __set__(self, owner, data):
        print(f'__set__ in Mapper: {self.name}')
        try:
            # Multiple data
            data = {str(key): self.preprocessor(owner, val) for key, val in data.items()}
            multiple_data = True
        except AttributeError as err:
            if str(err).endswith("object has no attribute 'items'"):
                data = self.preprocessor(owner, data)
                multiple_data = False
            else:
                raise

        # if isinstance(owner.identifiers, list):
        #     if multiple_data:
        #         data = {key: data[key] for key in owner.identifiers}
        #     else:
        #         data = {key: data for key in owner.identifiers}
        # else:
        #     if multiple_data:
        #         data = data[owner.identifiers]
            # data = {owner.identifiers: data}


        container = Container(data, multiple_data)

        setattr(owner, '_' + self.name, container)


class Interface:
    def __init__(self, identifiers):
        self.identifiers = identifiers

    @property
    def identifiers(self):
        ids = self._identifiers
        if len(ids) == 0:
            return None
        if len(ids) == 1:
            return ids[0]
        return ids

    @identifiers.setter
    def identifiers(self, identifiers):
        if identifiers is None or isinstance(identifiers, str):
            identifiers = [identifiers]
        else:
            try:
                identifiers = [str(identifier) for identifier in identifiers]
            except TypeError as err:
                if str(err).endswith('object is not iterable'):
                    # identifiers = str(identifiers)
                    identifiers = [identifiers]
                else:
                    raise
                identifiers = [str(identifier) for identifier in identifiers]
        self._identifiers = identifiers

    @Mapper
    def x(self, x):
        return x


# %%
i = Interface([5, 3])
i.x = {5: 'five', 3: 'three'}
print('plain access:', i.x)
print('private access and key:', i._x[3])
i._x[4] = 'four'
i._x.data

# %%

class AltInterface:
    def __init__(self, identifiers, normal, mapped):
        self.identifiers = identifiers
        self.normal = normal
        self._mapped = mapped

    @property
    def identifiers(self):
        ids = self._identifiers
        if len(ids) == 0:
            return None
        if len(ids) == 1:
            return ids[0]
        return ids

    @identifiers.setter
    def identifiers(self, identifiers):
        if identifiers is None or isinstance(identifiers, str):
            identifiers = [identifiers]
        else:
            try:
                identifiers = [str(identifier) for identifier in identifiers]
            except TypeError as err:
                if str(err).endswith('object is not iterable'):
                    # identifiers = str(identifiers)
                    identifiers = [identifiers]
                else:
                    raise
                identifiers = [str(identifier) for identifier in identifiers]
        self._identifiers = identifiers

    def __getattr__(self, name):
        print('__getattr__ in AltInterface')
        name = '_' + name
        if name in self.__dict__:
            print('getting value')
            value = self.__dict__[name]
            if isinstance(value, dict):
                if len(value) == 0:
                    value, = value.values()
            return value
        else:
            print('raising')
            raise AttributeError()
# %%
i = AltInterface('id', 'normal', 'mapped')
print(i.identifiers)
print(f'getting normal value: {i.normal}')
print(f'getting mapped value: {i.mapped}')
print(f'getting private mapped value: {i._mapped}')
print('setting mapped value')
i._mapped = {5: 'five'}
print(i.mapped)
print(i._mapped)
print(i.missing)
# %%
