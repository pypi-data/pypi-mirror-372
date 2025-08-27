"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/12 10:31
@file: serializers.py
@project: django_aeotrade_connector
@describe: None
"""

from rest_framework import serializers


class BaseSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ConnectorCodeSerializer(BaseSerializer):
    connector_code = serializers.CharField(required=True, allow_null=False, allow_blank=False, max_length=50)


class TaskId(BaseSerializer):
    task_id = serializers.CharField(required=True, allow_null=False, allow_blank=False, max_length=50)


class TaskCreateUpdateReq(BaseSerializer):
    org_id = serializers.CharField(required=True, allow_null=False, allow_blank=False, max_length=32)
    contract_id = serializers.CharField(required=True, allow_null=False, allow_blank=False, max_length=32)
    activity_code = serializers.CharField(required=True, allow_null=False, allow_blank=False, max_length=32)
    event_action_id = serializers.CharField(required=True, allow_null=False, allow_blank=False, max_length=50)
    event_action_params = serializers.JSONField(required=False, default={}, allow_null=True)


class TaskCreateReq(ConnectorCodeSerializer, TaskId, TaskCreateUpdateReq):

    def validate(self, attrs):
        if not attrs.get("event_action_params"):
            attrs["event_action_params"] = {}
        return attrs


class TaskUpdateReq(ConnectorCodeSerializer, TaskCreateUpdateReq):

    def validate(self, attrs):
        if not attrs.get("event_action_params"):
            attrs["event_action_params"] = {}
        return attrs
