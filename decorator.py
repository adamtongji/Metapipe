#!/usr/bin/env python
#coding:utf-8
import os,sys,time
from functools import wraps


def const():
    """
    this function defines inner constants, which will not change
    in whole scripts
        Usage:
                import const (class _const saved as const.py)
                const.ConstNames = ConstValues
        Notice:
                ConstNames should be all upperCase!
                this func(class) can save as another file for import

    """
    class _const:
        class ConstError(TypeError):
            pass

        class ConstCaseError(ConstError):
            pass

        def __setattr__(self, name, value):
            if self.__dict__.has_key(name):
                raise self.ConstError, "Can't change const.%s" % name
            if not name.isupper():
                raise self.ConstCaseError,\
                    'const name "%s" is not all uppercase!' % name
            self.__dict__[name] = value

    sys.modules[__name__] = _const()


def trans_time(TITLE,seconds):
    print "\033[1;32;38m"
    print "#" * 50
    print TITLE + ' ends at ' + \
          time.strftime("%Y-%m-%d %X", time.localtime()) + '...'

    hour = int(seconds / 3600)
    mins = int((seconds - 3600 * hour) / 60)
    sec = seconds - 3600 * hour - 60 * mins
    if int(hour) > 0:
        print "Totally \t{0}hours {1}minutes {2:.4}seconds lapsed"\
        .format(hour, mins, sec)
    elif int(mins) >0:
        print "Totally \t{0}minutes {1:.4}seconds lapsed" \
            .format( mins, sec)
    else:
        print "Totally \t{0:.4}seconds lapsed" \
            .format(sec)
    print "#" * 50
    print "\033[0m"


def time_dec(func):
    @wraps(func)
    def _time_dec(*args, **kwargs):
        const.TITLE = 'Metamed analysis pipeline'
        const.AUTHOR = os.popen("whoami").read().rstrip()
        const.TEMPLATEDATE = 'June 22, 2017'
        const.CODEFUNCTION = 'This program is for Metamed.'
        # begin_time = time.clock()
        begin_time = time.time()
        print "\033[1;32;38m"
        print "#" * 50
        print 'User ' + const.AUTHOR + ':'
        print const.TITLE + ' runs at ' + \
              time.strftime("%Y-%m-%d %X", time.localtime()) + '...'
        print 'Pipeline update: ' + const.TEMPLATEDATE
        print const.CODEFUNCTION
        print "#" * 50
        print "\033[0m"
        res = func(*args, **kwargs)
        end_time = time.time()
        lapsed_time = end_time - begin_time

        trans_time(const.TITLE, lapsed_time)

        return res

    return _time_dec


def time_func(func):
    @wraps(func)
    def _time_func(*args, **kwargs):
        start= time.time()
        res = func(*args, **kwargs)
        end = time.time()
        lapse = end - start
        print "{} takes {} seconds.".format(func.__name__, lapse)
        return res
    return _time_func

