"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/10 15:25
@file: __init__.py.py
@project: django_aeotrade_connector
@describe: None
"""
import datetime

from django.db import models

from aeotrade_connector.utils import JsonFieldMixin


# Create your models here.
class Model(models.Model):
    class Meta:
        abstract = True
        app_label = ""


class TimestampsMixin(models.Model):
    created_at: datetime.datetime = models.DateTimeField(auto_now_add=True)
    updated_at: datetime.datetime = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    is_deleted: bool = models.BooleanField(default=False, help_text="数据是否假删除")

    class Meta:
        abstract = True


class SoftForeignKey(models.ForeignKey):
    def __init__(
            self,
            to,
            on_delete=None,
            related_name=None,
            related_query_name=None,
            limit_choices_to=None,
            parent_link=False,
            to_field=None,
            db_constraint=False,
            **kwargs
    ):
        on_delete = models.DO_NOTHING
        db_index = True  # noqa
        kwargs["default"] = 0
        super().__init__(
            to,
            on_delete,
            related_name,
            related_query_name,
            limit_choices_to,
            parent_link,
            to_field,
            db_constraint,
            **kwargs
        )

    def get_db_prep_save(self, value, connection):
        try:
            return super().get_db_prep_save(value, connection)
        except ValueError:
            # If the value equal to zero, django will raise "ValueError" which like this below
            # The database backend does not accept 0 as a value for AutoField.
            return value


class JSONCharField(JsonFieldMixin, models.CharField):
    pass


class JSONTextField(JsonFieldMixin, models.TextField):
    pass
