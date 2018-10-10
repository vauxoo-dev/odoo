#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tokenize

import astroid
from pylint import checkers, interfaces

DFTL_CURSOR_EXPR = [
    'self.env.cr', 'self._cr',  # new api
    'self.cr',  # controllers and test
    'cr',  # old api
]


class PEP3110TokenChecker(checkers.BaseTokenChecker):
    __implements__ = interfaces.ITokenChecker
    name = 'python3'
    enabled = False

    msgs = {
        'E3110': ('Python 3 uses `as` instead of comma token to catch exceptions',
                  'no-comma-exception',
                  'See http://www.python.org/dev/peps/pep-3110/',
                  {'maxversion': (3, 0)}),
    }

    def process_tokens(self, tokens):
        comma_found = in_except = False
        pcount = 0
        for tok_type, token, start, _, _ in tokens:
            if tok_type == tokenize.NAME and token == 'except':
                in_except = True
                comma_found = False
                pcount = 0

            elif tok_type == tokenize.OP and in_except:
                if token == '(':
                    pcount += 1
                elif token == ')':
                    pcount -= 1
                elif token == ',' and pcount == 0:
                    comma_found = True
                if token == ':':
                    if in_except and comma_found:
                        self.add_message('no-comma-exception', line=start[0])
                    comma_found = in_except = False
                    pcount = 0


class OdooBaseChecker(checkers.BaseChecker):
    __implements__ = interfaces.IAstroidChecker
    name = 'odoo'

    msgs = {
        'E8501': (
            'Possible SQL injection risk.',
            'sql-injection',
            'See http://www.bobby-tables.com try using '
            'execute(query, tuple(params))',
        ),
        'E8502': (
            'Possible domain injection risk.',
            'domain-injection',
            'Check odoo guidelines.',
        ),
    }

    def _get_cursor_name(self, node):
        expr_list = []
        node_expr = node.expr
        while isinstance(node_expr, astroid.Attribute):
            expr_list.insert(0, node_expr.attrname)
            node_expr = node_expr.expr
        if isinstance(node_expr, astroid.Name):
            expr_list.insert(0, node_expr.name)
        cursor_name = '.'.join(expr_list)
        return cursor_name

    def _get_func_name(self, node):
        func_name = (
            isinstance(node, astroid.Name) and node.name or
            isinstance(node, astroid.Attribute) and node.attrname or '')
        return func_name

    def _check_concatenation(self, node):
        is_bin_op = False
        if isinstance(node, astroid.BinOp) and node.op in ('%', '+'):
            if (isinstance(node.right, astroid.Attribute) and
                    not node.right.attrname.startswith('_')):
                is_bin_op = True
            if isinstance(node.right, astroid.Tuple):
                for elt in node.right.elts:
                    if (isinstance(elt, astroid.Call) and
                            not self._get_func_name(elt.func).startswith('_')):
                        is_bin_op = True

        is_format = False
        if (isinstance(node, astroid.Call) and
                self._get_func_name(node.func) == 'format'):
            for keyword in node.keywords or []:
                if (isinstance(keyword.value, astroid.Attribute) and
                        not keyword.value.attrname.startswith('_')):
                    is_format = True
                    break
            for argument in node.args or []:
                if (isinstance(argument, astroid.Name) and
                        not argument.name.startswith('_')):
                    is_format = True
                    break

        return is_bin_op or is_format

    def _check_sql_injection_risky(self, node):
        # Inspired from OCA/pylint-odoo project
        # Thanks @moylop260 (Moisés López) & @nilshamerlinck (Nils Hamerlinck)
        current_file_bname = os.path.basename(self.linter.current_file)
        if not (isinstance(node, astroid.Call) and node.args and
                isinstance(node.func, astroid.Attribute) and
                node.func.attrname in ('execute', 'executemany') and
                self._get_cursor_name(node.func) in DFTL_CURSOR_EXPR and
                len(node.args) <= 1 and
                not current_file_bname.startswith('test_') and
                current_file_bname != 'sql.py'):
            return False
        first_arg = node.args[0]
        is_concatenation = self._check_concatenation(first_arg)
        if (not is_concatenation and
                isinstance(first_arg, (astroid.Name, astroid.Subscript))):

            # 1) look for parent method / controller
            current = node
            while (current and
                   not isinstance(current.parent, astroid.FunctionDef)):
                current = current.parent
            parent = current.parent

            # 2) check how was the variable built
            for node_ofc in parent.nodes_of_class(astroid.Assign):
                if node_ofc.targets[0].as_string() != first_arg.as_string():
                    continue
                is_concatenation = self._check_concatenation(node_ofc.value)
                if is_concatenation:
                    break
        return is_concatenation

    def _get_domain_arg(self, node):
        # original_method using domains
        # def search(self, args, offset=0, limit=None, order=None, count=False):
        # def search_count(self, args):
        # def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):

        # def name_search(self, name='', args=None, operator='ilike', limit=100):
        # def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):

        # def _read_group_fill_results(self, domain, groupby, remaining_groupbys,
        # def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        # def _read_group_raw(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        # def _where_calc(self, domain, active_test=True):
        # def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        # def _read_group_format_result(self, data, annotated_groupbys, groupby, domain):

        func_name = node.func.attrname
        keywords = {kw.arg: kw.value for kw in node.keywords or []}
        domain_arg = keywords.get('domain') or keywords.get('args')
        if domain_arg:
            return domain_arg
        if func_name in ['search', 'search_count', '_search']:
            pos = 0
            domain_arg = len(node.args) >= pos + 1 and node.args[pos]
        elif func_name in ['name_search', '_name_search',
                           '_read_group_fill_results', 'read_group',
                           '_read_group_raw', '_where_calc', 'search_read']:
            pos = 1
            domain_arg = len(node.args) >= pos + 1 and node.args[pos]
        elif func_name == '_read_group_format_result':
            pos = 3
            domain_arg = len(node.args) >= pos + 1 and node.args[pos]
        return domain_arg

    def _check_domain_injection_risky(self, node):
        current_file_bname = os.path.basename(self.linter.current_file)
        if not (isinstance(node, astroid.Call) and
                isinstance(node.func, astroid.Attribute) and
                node.func.attrname in ('search', 'search_count') and
                not current_file_bname.startswith('test_')):
            return
        infered = checkers.utils.safe_infer(node.func)
        if (infered is None or infered is astroid.Uninferable or
            not isinstance(infered, astroid.BoundMethod)):
            return
        infered_name = "%s.%s" % (infered.bound.root().name, infered.bound.name)
        if infered_name != 'odoo.models.BaseModel':
            return
        domain_node = self._get_domain_arg(node)

    @checkers.utils.check_messages('sql-injection', 'domain-injection')
    def visit_call(self, node):
        if self._check_sql_injection_risky(node):
            self.add_message('sql-injection', node=node)
        if self._check_domain_injection_risky(node):
            self.add_message('domain-injection', node=node)


def register(linter):
    linter.register_checker(PEP3110TokenChecker(linter))
    linter.register_checker(OdooBaseChecker(linter))
