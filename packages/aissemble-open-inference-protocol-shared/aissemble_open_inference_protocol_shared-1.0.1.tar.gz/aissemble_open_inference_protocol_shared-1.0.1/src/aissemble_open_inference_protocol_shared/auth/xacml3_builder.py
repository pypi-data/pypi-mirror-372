###
# #%L
# aiSSEMBLE::Open Inference Protocol::Shared
# %%
# Copyright (C) 2024 Booz Allen Hamilton Inc.
# %%
# This software package is licensed under the Booz Allen Public License. All Rights Reserved.
# #L%
###
from typing import List
import json


class Attribute:
    def __init__(
        self,
        include_in_result: bool,
        attribute_id: str,
        data_type: str,
        value: str,
    ) -> None:
        self.include_in_result = include_in_result
        self.attribute_id = attribute_id
        self.data_type = data_type
        self.value = value

    def to_dict(self):
        return {
            "AttributeId": self.attribute_id,
            "IncludeInResult": self.include_in_result,
            "DataType": self.data_type,
            "Value": self.value,
        }


class Category:
    def __init__(self, category_id: str, attribute: List[Attribute]) -> None:
        self.category_id = category_id
        self.attribute = attribute

    def to_dict(self):
        return {
            "CategoryId": self.category_id,
            "Attribute": [attr.to_dict() for attr in self.attribute],
        }


class Request:
    def __init__(
        self,
        return_policy_id_list: bool,
        combined_decision: bool,
        category: List[Category],
    ) -> None:
        self.return_policy_id_list = return_policy_id_list
        self.combined_decision = combined_decision
        self.category = category

    def to_dict(self):
        return {
            "ReturnPolicyIdList": self.return_policy_id_list,
            "CombinedDecision": self.combined_decision,
            "Category": [cat.to_dict() for cat in self.category],
        }


class XacmlRequestBuilder:
    CATEGORY_ACCESS_SUBJECT = (
        "urn:oasis:names:tc:xacml:1.0:subject-category:access-subject"
    )
    CATEGORY_RESOURCE = "urn:oasis:names:tc:xacml:3.0:attribute-category:resource"
    CATEGORY_ACTION = "urn:oasis:names:tc:xacml:3.0:attribute-category:action"
    SUBJECT_ID = "urn:oasis:names:tc:xacml:1.0:subject:subject-id"
    RESOURCE_ID = "urn:oasis:names:tc:xacml:1.0:resource:resource-id"
    ACTION_ID = "urn:oasis:names:tc:xacml:1.0:action:action-id"
    SUBJECT_ROLE = "urn:oasis:names:tc:xacml:2.0:subject:role"
    XML_STRING = "http://www.w3.org/2001/XMLSchema#string"

    def __init__(self) -> None:
        pass

    def build_request(self, user, role, resource, action):
        categories = []
        # ==========================
        # access-subject category
        # ==========================
        subject_atributes = []
        subject_atributes.append(
            Attribute(False, self.SUBJECT_ID, self.XML_STRING, user)
        )
        subject_atributes.append(
            Attribute(False, self.SUBJECT_ROLE, self.XML_STRING, role or "unknown")
        )
        access_subject_category = Category(
            self.CATEGORY_ACCESS_SUBJECT, subject_atributes
        )
        categories.append(access_subject_category)

        # ===================
        # resource category
        # ===================
        resource_id_attribute = Attribute(
            False, self.RESOURCE_ID, self.XML_STRING, resource
        )
        resource_category = Category(self.CATEGORY_RESOURCE, [resource_id_attribute])
        categories.append(resource_category)

        # ===================
        # action category
        # ===================
        action_id_attribute = Attribute(False, self.ACTION_ID, self.XML_STRING, action)
        action_category = Category(self.CATEGORY_ACTION, [action_id_attribute])
        categories.append(action_category)

        # ===================
        # Request
        # ===================
        request = Request(False, False, categories)

        # request_dict = request.__dict__
        request_dict = {"Request": request.to_dict()}

        json_string_request = json.dumps(request_dict, indent=2)

        return json_string_request
