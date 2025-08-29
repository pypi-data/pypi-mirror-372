from relationalai.early_access.metamodel.compiler import Pass
from relationalai.early_access.metamodel import ir, builtins as rel_builtins, factory as f, visitor
from relationalai.early_access.metamodel.typer import Checker, InferTypes, typer
from relationalai.early_access.metamodel import helpers
from relationalai.early_access.metamodel.rewrite import Splinter, ExtractNestedLogicals
from relationalai.early_access.metamodel.util import FrozenOrderedSet

from relationalai.early_access.metamodel.rewrite import Flatten
# TODO: Move this into metamodel.rewrite
from relationalai.early_access.rel.rewrite import QuantifyVars, CDC

from relationalai.early_access.lqp.utils import output_names

from typing import cast, List, Sequence, Tuple, Union, Optional
from collections import defaultdict

def lqp_passes() -> list[Pass]:
    return [
        Checker(),
        ExtractNestedLogicals(), # before InferTypes to avoid extracting casts
        InferTypes(),
        CDC(),
        # Broken
        # ExtractCommon(),
        Flatten(),
        Splinter(), # Splits multi-headed rules into multiple rules
        QuantifyVars(), # Adds missing existentials
        EliminateData(),  # Turns Data nodes into ordinary relations.
        DeduplicateVars(),  # Deduplicates vars in Updates and Outputs.
        ConstantsToVars(),  # Turns constants in Updates and Outputs into vars.
        UnifyDefinitions(),
    ]

# LQP does not support multiple definitions for the same relation. This pass unifies all
# definitions for each relation into a single definition using a union.
class UnifyDefinitions(Pass):
    def __init__(self):
        super().__init__()
        self.renamed_relation_args: dict[ir.Relation, list[ir.Var]] = {}

    def rewrite(self, model: ir.Model, options:dict={}) -> ir.Model:
        root = cast(ir.Logical, model.root)
        new_tasks = self.get_combined_multidefs(root)
        return ir.Model(
            model.engines,
            model.relations,
            model.types,
            f.logical(
                tuple(new_tasks),
                root.hoisted,
                model.root.engine,
            ),
            model.annotations,
        )

    def _get_derives(self, logical: ir.Logical) -> list[ir.Update]:
        derives = []
        for task in logical.body:
            if isinstance(task, ir.Update) and task.effect == ir.Effect.derive:
                derives.append(task)
        return derives

    def _get_non_derives(self, logical: ir.Logical) -> list[ir.Update]:
        non_derives = []
        for task in logical.body:
            if not(isinstance(task, ir.Update) and task.effect == ir.Effect.derive):
                non_derives.append(task)
        return non_derives

    def get_combined_multidefs(self, root: ir.Logical) -> list[ir.Logical]:
        # Step 1: Group tasks by the relation they define.
        relation_to_tasks: dict[Optional[ir.Relation], list[ir.Logical]] = defaultdict(list)

        for task in root.body:
            task = cast(ir.Logical, task)
            task_derives = self._get_derives(task)

            # Some relations do not need to be grouped, e.g., if they don't contain a
            # derive. Use `None` as a placeholder key for these cases.
            if len(task_derives) != 1:
                relation_to_tasks[None].append(task)
                continue

            derive_name = task_derives[0].relation
            relation_to_tasks[derive_name].append(task)

        # Step 2: For each relation, combine all of the body definitions into a union.
        result_tasks = []
        for relation, tasks in relation_to_tasks.items():
            # If there's only one task for the relation, or if grouping is not needed, then
            # just keep the original tasks.
            if len(tasks) == 1 or relation is None:
                result_tasks.extend(tasks)
                continue

            result_tasks.append(self._combine_tasks_into_union(tasks))
        return result_tasks

    def _get_variable_mapping(self, logical: ir.Logical) -> dict[ir.Value, ir.Var]:
        derives = self._get_derives(logical)
        assert len(derives) == 1, "should only have one derive in a logical at this stage"
        derive = derives[0]

        var_mapping = {}

        if derive.relation not in self.renamed_relation_args:
            renamed_vars = []
            for (i, arg) in enumerate(derive.args):
                typ = typer.to_type(arg)
                assert arg not in var_mapping, "args of update should be unique"
                if isinstance(arg, ir.Var):
                    var_mapping[arg] = ir.Var(typ, arg.name)
                else:
                    var_mapping[arg] = ir.Var(typ, f"arg_{i}")

                renamed_vars.append(var_mapping[arg])

            self.renamed_relation_args[derive.relation] = renamed_vars
        else:
            for (arg, var) in zip(derive.args, self.renamed_relation_args[derive.relation]):
                var_mapping[arg] = var

        return var_mapping

    def _rename_variables(self, logical: ir.Logical) -> ir.Logical:
        class RenameVisitor(visitor.Rewriter):
            def __init__(self, var_mapping: dict[ir.Value, ir.Var]):
                super().__init__()
                self.var_mapping = var_mapping

            def handle_var(self, node: ir.Var, parent: ir.Node) -> ir.Var:
                if node in self.var_mapping:
                    return self.var_mapping[node]
                return node

            # TODO: ideally, extend the rewriter class to allow rewriting PyValue to Var so
            # we don't need to separately handle all cases containing them.
            def handle_update(self, node: ir.Update, parent: ir.Node) -> ir.Update:
                new_args = tuple(self.var_mapping.get(arg, arg) for arg in node.args)
                return ir.Update(
                    node.engine,
                    node.relation,
                    new_args,
                    node.effect,
                    node.annotations,
                )

            def handle_lookup(self, node: ir.Lookup, parent: ir.Node) -> ir.Lookup:
                new_args = tuple(self.var_mapping.get(arg, arg) for arg in node.args)
                return ir.Lookup(
                    node.engine,
                    node.relation,
                    new_args,
                    node.annotations,
                )

            def handle_output(self, node: ir.Output, parent: ir.Node) -> ir.Output:
                new_aliases = FrozenOrderedSet(
                    [(name, self.var_mapping.get(value, value)) for name, value in node.aliases]
                )
                if node.keys:
                    new_keys = FrozenOrderedSet(
                        [self.var_mapping.get(key, key) for key in node.keys]
                    )
                else:
                    new_keys = node.keys

                return ir.Output(
                    node.engine,
                    new_aliases,
                    new_keys,
                    node.annotations,
                )

            def handle_construct(self, node: ir.Construct, parent: ir.Node) -> ir.Construct:
                new_values = tuple(self.var_mapping.get(arg, arg) for arg in node.values)
                new_id_var = self.var_mapping.get(node.id_var, node.id_var)
                return ir.Construct(
                    node.engine,
                    new_values,
                    new_id_var,
                    node.annotations,
                )

            def handle_aggregate(self, node: ir.Aggregate, parent: ir.Node) -> ir.Aggregate:
                new_projection = tuple(self.var_mapping.get(arg, arg) for arg in node.projection)
                new_group = tuple(self.var_mapping.get(arg, arg) for arg in node.group)
                new_args = tuple(self.var_mapping.get(arg, arg) for arg in node.args)
                return ir.Aggregate(
                    node.engine,
                    node.aggregation,
                    new_projection,
                    new_group,
                    new_args,
                    node.annotations,
                )

            def handle_rank(self, node: ir.Rank, parent: ir.Node) -> ir.Rank:
                new_projection = tuple(self.var_mapping.get(arg, arg) for arg in node.projection)
                new_group = tuple(self.var_mapping.get(arg, arg) for arg in node.group)
                new_args = tuple(self.var_mapping.get(arg, arg) for arg in node.args)
                new_result = self.var_mapping.get(node.result, node.result)

                return ir.Rank(
                    node.engine,
                    new_projection,
                    new_group,
                    new_args,
                    node.arg_is_ascending,
                    new_result,
                    node.limit,
                    node.annotations,
                )

        var_mapping = self._get_variable_mapping(logical)
        renamer = RenameVisitor(var_mapping)
        result = renamer.walk(logical)

        # Also need to append the equality for each renamed constant. E.g., if the mapping
        # contains (50.0::FLOAT -> arg_2::FLOAT), we need to add
        # `eq(arg_2::FLOAT, 50.0::FLOAT)` to the result.
        value_eqs = []
        for (old_var, new_var) in var_mapping.items():
            if not isinstance(old_var, ir.Var):
                value_eqs.append(f.lookup(rel_builtins.eq, [new_var, old_var]))

        result = ir.Logical(
            result.engine,
            result.hoisted,
            tuple(value_eqs) + tuple(result.body),
            result.annotations,
        )

        return result

    # This function is the main workhorse for this rewrite pass. It takes a list of tasks
    # that define the same relation, and combines them into a single task that defines
    # the relation using a union of all of the bodies.
    def _combine_tasks_into_union(self, tasks: list[ir.Logical]) -> ir.Logical:
        # Step 1: Rename the variables in all tasks so that they will match the final derive
        # after reconstructing into a union
        renamed_tasks = [self._rename_variables(task) for task in tasks]

        # Step 2: Get the final derive
        derives = self._get_derives(renamed_tasks[0])
        assert len(derives) == 1, "should only have one derive in a logical at this stage"
        # Also make sure that all the derives are the same. This should be the case because
        # we renamed all the variables to be the same in step 1.
        for task in renamed_tasks[1:]:
            assert self._get_derives(task) == derives, "all derives should be the same"

        derive = derives[0]

        # Step 3: Remove the final `derive` from each task
        renamed_task_bodies = [
            f.logical(
                tuple(self._get_non_derives(t)),  # Only keep non-derive tasks
                t.hoisted,
                t.engine,
            )
            for t in renamed_tasks
        ]

        # Step 4: Construct a union of all the task bodies
        union = f.union(
            tuple(renamed_task_bodies),
            [],
            renamed_tasks[0].engine,
        )

        # Step 5: Add the final derive back
        return f.logical(
            (union, derive),
            [],
            renamed_tasks[0].engine,
        )

# Creates intermediary relations for all Data nodes and replaces said Data nodes
# with a Lookup into these created relations.
class EliminateData(Pass):
    def rewrite(self, model: ir.Model, options:dict={}) -> ir.Model:
        r = self.DataRewriter()
        return r.walk(model)

    # Does the actual work.
    class DataRewriter(visitor.Rewriter):
        new_relations: list[ir.Relation]
        new_updates: list[ir.Logical]
        # Counter for naming new relations.
        # It must be that new_count == len new_updates == len new_relations.
        new_count: int

        def __init__(self):
            self.new_relations = []
            self.new_updates = []
            self.new_count = 0
            super().__init__()

        # Create a new intermediary relation representing the Data (and pop it in
        # new_updates/new_relations) and replace this Data with a Lookup of said
        # intermediary.
        def handle_data(self, node: ir.Data, parent: ir.Node) -> ir.Lookup:
            self.new_count += 1
            intermediary_name = f"formerly_Data_{self.new_count}"

            intermediary_relation = f.relation(
                intermediary_name,
                [f.field(v.name, v.type) for v in node.vars]
            )
            self.new_relations.append(intermediary_relation)

            intermediary_update = f.logical([
                # For each row (union), equate values and their variable (logical).
                f.union(
                    [
                        f.logical(
                            [
                                f.lookup(rel_builtins.eq, [val, var])
                                for (val, var) in zip(row, node.vars)
                            ],
                            hoisted = node.vars,
                        )
                        for row in node
                    ],
                    hoisted = node.vars,
                ),
                # And pop it back into the relation.
                f.update(intermediary_relation, node.vars, ir.Effect.derive),
            ])
            self.new_updates.append(intermediary_update)

            replacement_lookup = f.lookup(intermediary_relation, node.vars)

            return replacement_lookup

        # Walks the model for the handle_data work then updates the model with
        # the new state.
        def handle_model(self, model: ir.Model, parent: None):
            walked_model = super().handle_model(model, parent)
            assert len(self.new_relations) == len(self.new_updates) and self.new_count == len(self.new_relations)

            # This is okay because its LQP.
            assert isinstance(walked_model.root, ir.Logical)
            root_logical = cast(ir.Logical, walked_model.root)

            # We may need to add the new intermediaries from handle_data to the model.
            if self.new_count  == 0:
                return model
            else:
                return ir.Model(
                    walked_model.engines,
                    walked_model.relations | self.new_relations,
                    walked_model.types,
                    ir.Logical(
                        root_logical.engine,
                        root_logical.hoisted,
                        root_logical.body + tuple(self.new_updates),
                        root_logical.annotations,
                    ),
                    walked_model.annotations,
                )

# Deduplicate Vars in Updates and Outputs.
class DeduplicateVars(Pass):
    def rewrite(self, model: ir.Model, options:dict={}) -> ir.Model:
        r = self.VarDeduplicator()
        return r.walk(model)

    # Return 1) a new list of Values with no duplicates (at the object level) and
    # 2) equalities between any original Value and a deduplicated Value.
    @staticmethod
    def dedup_values(vals: Sequence[ir.Value]) -> Tuple[List[ir.Value], List[ir.Lookup]]:
        # If a var is seen more than once, it is a duplicate and we will create
        # a new Var and equate it with the seen one.
        seen_vars = set()

        new_vals = []
        eqs = []

        for i, val in enumerate(vals):
            # Duplicates can only occur within Vars.
            # TODO: we don't know for sure if these are the only relevant cases.
            if isinstance(val, ir.Default) or isinstance(val, ir.Var):
                var = val if isinstance(val, ir.Var) else val.var
                if var in seen_vars:
                    new_var = ir.Var(var.type, var.name + "_dup_" + str(i))
                    new_val = new_var if isinstance(val, ir.Var) else ir.Default(new_var, val.value)
                    new_vals.append(new_val)
                    eqs.append(f.lookup(rel_builtins.eq, [new_var, var]))
                else:
                    seen_vars.add(var)
                    new_vals.append(val)
            else:
                # No possibility of problematic duplication.
                new_vals.append(val)

        return new_vals, eqs

    # Returns a reconstructed output with no duplicate variable objects
    # (dedup_values) and now necessary equalities between any two previously
    # duplicate variables.
    @staticmethod
    def dedup_output(output: ir.Output) -> List[Union[ir.Output, ir.Lookup]]:
        vals = helpers.output_values(output.aliases)
        deduped_vals, req_lookups = DeduplicateVars.dedup_values(vals)
        # Need the names so we can recombine.
        alias_names = output_names(output.aliases)
        new_output = ir.Output(
            output.engine,
            FrozenOrderedSet(list(zip(alias_names, deduped_vals))),
            output.keys,
            output.annotations,
        )
        return req_lookups + [new_output]

    # Returns a replacement update with no duplicate variable objects
    # (dedup_values) and now necessary equalities between any two previously
    # duplicate variables.
    @staticmethod
    def dedup_update(update: ir.Update) -> List[Union[ir.Update, ir.Lookup]]:
        deduped_vals, req_lookups = DeduplicateVars.dedup_values(update.args)
        new_update = ir.Update(
            update.engine,
            update.relation,
            tuple(deduped_vals),
            update.effect,
            update.annotations,
        )
        return req_lookups + [new_update]

    # Does the actual work.
    class VarDeduplicator(visitor.Rewriter):
        def __init__(self):
            super().__init__()

        # We implement handle_logical instead of handle_update/handle_output
        # because in addition to modifying said update/output we require new
        # lookups (equality between original and deduplicated variables).
        def handle_logical(self, node: ir.Logical, parent: ir.Node):
            # In order to recurse over subtasks.
            node = super().handle_logical(node, parent)

            new_body = []
            for subtask in node.body:
                if isinstance(subtask, ir.Output):
                    new_body.extend(DeduplicateVars.dedup_output(subtask))
                elif isinstance(subtask, ir.Update):
                    new_body.extend(DeduplicateVars.dedup_update(subtask))
                else:
                    new_body.append(subtask)

            return ir.Logical(
                node.engine,
                node.hoisted,
                tuple(new_body),
                node.annotations
            )

# Rewrite constants to vars in Updates. This results in a more normalized format where
# updates contain only variables. This allows for easier rewrites in later passes.
class ConstantsToVars(Pass):
    def rewrite(self, model: ir.Model, options:dict={}) -> ir.Model:
        r = self.ConstantToVarRewriter()
        return r.walk(model)

    # Return 1) a new list of Values with no duplicates (at the object level) and
    # 2) equalities between any original Value and a deduplicated Value.
    @staticmethod
    def replace_constants_with_vars(vals: Sequence[ir.Value]) -> Tuple[List[ir.Value], List[ir.Lookup]]:
        new_vals = []
        eqs = []

        for i, val in enumerate(vals):
            if isinstance(val, ir.PyValue) or isinstance(val, ir.Literal):
                # Replace constant with a new Var.
                typ = typer.to_type(val)
                assert isinstance(typ, ir.ScalarType), "can only replace scalar constants with vars"
                new_var = ir.Var(typ, f"{typ.name.lower()}_{i}")
                new_vals.append(new_var)
                eqs.append(f.lookup(rel_builtins.eq, [new_var, val]))
            else:
                new_vals.append(val)

        return new_vals, eqs

    @staticmethod
    def dedup_update(update: ir.Update) -> List[Union[ir.Update, ir.Lookup]]:
        deduped_vals, req_lookups = ConstantsToVars.replace_constants_with_vars(update.args)
        new_update = ir.Update(
            update.engine,
            update.relation,
            tuple(deduped_vals),
            update.effect,
            update.annotations,
        )
        return req_lookups + [new_update]

    # Does the actual work.
    class ConstantToVarRewriter(visitor.Rewriter):
        def __init__(self):
            super().__init__()

        # We implement handle_logical instead of handle_update because in
        # addition to modifying said update we require new lookups (equality
        # between original and deduplicated variables).
        def handle_logical(self, node: ir.Logical, parent: ir.Node):
            # In order to recurse over subtasks.
            node = super().handle_logical(node, parent)

            new_body = []
            for subtask in node.body:
                if isinstance(subtask, ir.Update):
                    new_body.extend(ConstantsToVars.dedup_update(subtask))
                else:
                    new_body.append(subtask)

            return ir.Logical(
                node.engine,
                node.hoisted,
                tuple(new_body),
                node.annotations
            )
