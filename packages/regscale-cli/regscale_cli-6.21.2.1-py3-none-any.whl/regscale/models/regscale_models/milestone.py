#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Class for milestone model in RegScale platform"""

from typing import Optional

from pydantic import Field, field_validator

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class Milestone(RegScaleModel):
    """Milestone Model"""

    _module_slug = "milestones"
    _module_string = "milestones"
    _unique_fields = ["title", "parentID", "parentModule"]

    title: str
    id: int = 0
    isPublic: Optional[bool] = True
    milestoneDate: Optional[str] = Field(default_factory=get_current_datetime)
    responsiblePersonId: Optional[str] = None
    predecessorStepId: Optional[int] = None
    completed: Optional[bool] = False
    dateCompleted: Optional[str] = None
    notes: Optional[str] = ""
    parentID: Optional[int] = None
    parentModule: str = ""

    @field_validator("dateCompleted")
    @classmethod
    def set_date_completed(cls, v: Optional[str], info) -> Optional[str]:
        """Set dateCompleted based on completed field."""
        completed = info.data.get("completed", False)
        if completed and v is None:
            return get_current_datetime()
        if not completed:
            return None
        return v
