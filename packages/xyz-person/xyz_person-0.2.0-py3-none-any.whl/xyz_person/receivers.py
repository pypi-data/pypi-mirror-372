# -*- coding:utf-8 -*-
from django.dispatch import receiver
from xyz_auth.signals import to_save_user_profile
from . import helper
import logging

log = logging.getLogger("django")

# @receiver(post_save, sender=Worker)
# def init_person(sender, **kwargs):
#     try:
#         worker = kwargs['instance']
#         helper.init_person(worker)
#     except Exception as e:
#         import traceback
#         log.error("init_person error: %s" % traceback.format_exc())


@receiver(to_save_user_profile)
def init_person(sender, **kwargs):
    try:
        helper.init_person(kwargs['user'], kwargs['profile'])
    except Exception as e:
        import traceback
        log.error("init_person error: %s" % traceback.format_exc())