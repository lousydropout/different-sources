#!/usr/bin/env python3
import os
from aws_cdk import core as cdk
from cdk.main_stack import DifferentSources


is_review = os.environ.get("IS_REVIEW", "").lower() == "true"
name = "different-sources-review" if is_review else "different-sources"

app = cdk.App()

DifferentSources(
    app,
    name,
    prefix=name,
)

app.synth()
