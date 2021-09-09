#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

from cdk.main_stack import DifferentSources


is_review = os.environ.get("IS_REVIEW", "").lower() == "true"

app = cdk.App()
DifferentSources(
    app,
    "different-sources-review" if is_review else "different-sources",
    prefix="different-sources-review" if is_review else "different-sources",
)

app.synth()
