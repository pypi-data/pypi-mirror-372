import json
from typing import Any, Dict, List, Optional

import yaml

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.translate import _


class SchemaParser(models.Model):
    _name = "schema_parser"
    _description = "Schema Parser"
    _inherit = "mixin.master_data"

    category_id = fields.Many2one(
        comodel_name="schema_parser_category",
        string="Category",
        ondelete="restrict",
        index=True,
    )
    schema = fields.Text(
        string="Schema",
        help="Validation schema (JSON Schema). Supports JSON or YAML text.",
    )
    parser = fields.Text(
        string="Specification",
        help="Specification to be validated and parsed. Supports JSON or YAML text.",
    )
    documentation = fields.Text(
        string="Documentation",
    )
    schema_example = fields.Text(
        string="Example",
    )
    result_example = fields.Text(
        string="Result Example",
        compute="_compute_result_example",
    )

    @api.depends(
        "schema",
        "parser",
        "schema_example",
    )
    def _compute_result_example(self):
        for record in self:
            if record.schema and record.parser and record.schema_example:
                result = record.parse_specification(record.schema)
                record.result_example = json.dumps(result, ensure_ascii=False, indent=2)
            else:
                record.result_example = False

    def parse_specification(self, schema):
        self.ensure_one()
        localdict = {
            "yaml_safe_load": yaml.safe_load,
            "yaml_safe_dump": yaml.safe_dump,
            "json_dumps": json.dumps,
            "json_loads": json.loads,
            "Any": Any,
            "Dict": Dict,
            "List": List,
            "Optional": Optional,
            "schema": schema,
        }
        try:
            safe_eval(self.parser, localdict, mode="exec", nocopy=True)
            result = localdict.get("result")
            if result is None:
                raise UserError(_("Parser did not set `result`."))
            if not isinstance(result, dict):
                raise UserError(
                    _("`result` must be a dict, got: %s") % type(result).__name__
                )
            return result
        except Exception as error:
            raise UserError(_("Error executing parser.\n%s") % error)
