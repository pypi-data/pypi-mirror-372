# -*- coding:utf-8 -*- 
__author__ = 'denishuang'
from . import models
from xyz_util.modelutils import translate_model_values


def init_person(user, profile):
    fns = "email,mobile,id_card,gender,ethnic,city".split(",")
    ps = translate_model_values(models.Person, profile, fns)
    ps['name'] = user.get_full_name()
    # print "init_person", ps
    return models.Person.objects.update_or_create(user=user, defaults=ps)
