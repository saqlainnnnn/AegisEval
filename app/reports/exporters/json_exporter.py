from __future__ import annotations

import json

from pydantic import BaseModel


class JsonReportExporter:
    """
    Exports report models as formatted JSON.
    """

    def export(
        self,
        report: BaseModel,
    ) -> str:
        return json.dumps(
            report.model_dump(
                mode="json",
            ),
            indent=2,
            sort_keys=True,
        )