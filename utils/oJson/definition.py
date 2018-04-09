

class ojUndefinded(Exception):
    pass


class ojMaster(object):

    counter = 0

    def __init__(self):
        ojMaster.counter = ojMaster.counter + 1
        self.counter = ojMaster.counter

    @classmethod
    def toTuple(cls, input):

        if isinstance(input, ojObject):
            _return = ()
            for _key in input.__dict__.keys():
                _obj = input.__dict__[_key]

                if isinstance(_obj, ojPair):
                    _return += ((_obj.counter, _obj, cls.toTuple(_obj.item)), )

            return (input.counter, input, tuple(sorted(_return)))

        elif isinstance(input, ojArray):

            _return = ()
            for _item in input.values:
                _return += (cls.toTuple(_item),)

            return (input.counter, input, _return)

        elif isinstance(input, ojPair):
            return (input.counter, input, cls.toTuple(input.item))

        elif isinstance(input, ojValue):
            return (input.counter, input, input.get())

    @classmethod
    def toJson(cls, input):

        _pos, _obj, _content = input

        if isinstance(_obj, ojObject):

            _str = "{"
            for _content2 in _content:
                _str = _str + cls.toJson(_content2) + ","

            return _str[:-1] + "}"

        elif isinstance(_obj, ojArray):

            _str = "["
            for _obj3 in _content:
                _str = _str + cls.toJson(_obj3) + ","
            return _str[:-1] + "]"

        elif isinstance(_obj, ojPair):
            _str = _obj.name + ":" + cls.toJson(_content)
            return _str

        elif isinstance(_obj, ojValue):
            _str = "{0}".format(_content)
            return _str


class ojObject(ojMaster):

    def __init__(self):
        ojMaster.__init__(self)


class ojPair(ojMaster):

    def __init__(self):
        ojMaster.__init__(self)

        self.name = None
        self.item = None

    def init(self, **u):

        for _key in u.keys():
            if _key in self.__dict__.keys():
                self.__dict__[_key] = u[_key]

        return self

    def init_item(self, item):

        if isinstance(item, ojValue):
            self.item = item
            return self

        elif isinstance(item, ojArray):
            self.item = item
            return self

        elif isinstance(item, ojObject):
            self.item = item
            return self

        raise ojUndefinded("{0}".format(item))


class ojValue(ojMaster):

    def __init__(self):
        ojMaster.__init__(self)
        self.value = None

    def init_value(self, value):
        self.set(value)
        return self

    def set(self, value):
        self.value = value

    def get(self):
        return self.value


class ojArray(ojMaster):

    def __init__(self):
        ojMaster.__init__(self)
        self.values = ()

    def init_values(self, *values):

        for _value in values:

            if isinstance(_value, ojValue):
                self.values += (_value, )

            elif isinstance(_value, ojArray):
                self.values += (_value, )

            elif isinstance(_value, ojObject):
                self.values += (_value, )

            else:
                raise ojUndefinded

        return self


class ojInt(ojValue):

    def __init__(self):
        ojValue.__init__(self)


class ojFloat(ojValue):

    def __init__(self):
        ojValue.__init__(self)


class ojString(ojValue):

    def __init__(self):
        ojValue.__init__(self)


class ojBool(ojValue):

    def __init__(self):
        ojValue.__init__(self)


class ojInt(ojValue):

    def __init__(self):
        ojValue.__init__(self)


if __name__ == "__main__":
    class test1(ojObject):

        def __init__(self):
            ojObject.__init__(self)

            self.int1 = ojPair().init(name="ini1").init_item(ojInt().init_value(1))
            self.int2 = ojPair().init(name="ini2").init_item(ojInt().init_value(1))
            self.int3 = ojPair().init(name="ini3").init_item(ojInt().init_value(1))
            self.int4 = ojPair().init(name="ini4").init_item(ojInt().init_value(1))

    class test2(ojObject):

        def __init__(self):
            ojObject.__init__(self)
            self.obj = ojPair().init(name="obj").init_item(test1())
            self.int2 = ojPair().init(name="ini2").init_item(ojInt().init_value(1))
            self.array = ojPair().init(name="array").init_item(ojArray().init_values(ojArray().init_values(ojInt().init_value(11), ojString().init_value("ich bin ein string")), test1(), test1()))

    x = test2()

    y = ojMaster.toJson(ojMaster.toTuple(x))

    print(y)
