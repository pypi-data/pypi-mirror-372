//! Statement categorizer for analyzing and grouping Python statements
//!
//! This module categorizes statements based on their type and dependencies,
//! identifying which statements need to be declared before others. It handles
//! various Python constructs including class inheritance, decorators, metaclasses,
//! and module namespaces.

use crate::types::FxIndexSet;
use ruff_python_ast::{Expr, Stmt};

/// Extended categories for cross-module statement reordering
#[derive(Debug, Default, Clone)]
pub struct CrossModuleStatementCategories {
    /// Import statements
    pub imports: Vec<Stmt>,
    /// Built-in type restorations (e.g., bytes = bytes)
    pub builtin_restorations: Vec<Stmt>,
    /// Namespace built-in assignments (e.g., compat.bytes = bytes)
    pub namespace_builtin_assignments: Vec<Stmt>,
    /// Assignments that define base classes
    pub base_class_assignments: Vec<Stmt>,
    /// Regular assignments
    pub regular_assignments: Vec<Stmt>,
    /// Class definitions
    pub classes: Vec<Stmt>,
    /// Function definitions
    pub functions: Vec<Stmt>,
    /// Other statements
    pub other_statements: Vec<Stmt>,
}

/// Categorizer for analyzing and grouping statements by type and dependencies
#[derive(Copy, Clone, Debug)]
pub struct StatementCategorizer {
    /// Python version for built-in detection
    python_version: u8,
}

/// Check if an expression looks like it could be a class-like value
/// (base class, metaclass, or other class-producing expression)
fn is_class_like_expr(expr: &Expr) -> bool {
    match expr {
        // e.g., json.JSONDecodeError
        Expr::Attribute(_) => true,
        // e.g., BaseClass, Exception (uppercase names typically indicate classes)
        Expr::Name(name) => name.id.chars().next().is_some_and(char::is_uppercase),
        // e.g., NamedTuple("Point", ...), type("MyClass", ...), TypedDict(...)
        Expr::Call(call) => {
            match call.func.as_ref() {
                // Constructor calls like module.NamedTuple(...)
                Expr::Attribute(_) => true,
                // Constructor calls like NamedTuple(...), type(...), etc.
                Expr::Name(name) => name.id.chars().next().is_some_and(char::is_uppercase),
                _ => false,
            }
        }
        // e.g., Protocol[T], Generic[T], TypeVar[...]
        Expr::Subscript(sub) => {
            match sub.value.as_ref() {
                // Subscripted attributes like typing.Protocol[...]
                Expr::Attribute(_) => true,
                // Subscripted names like Protocol[...], Generic[...]
                Expr::Name(name) => name.id.chars().next().is_some_and(char::is_uppercase),
                _ => false,
            }
        }
        _ => false,
    }
}

impl StatementCategorizer {
    /// Create a new categorizer
    pub fn new(python_version: u8) -> Self {
        Self { python_version }
    }

    /// Analyze statements for cross-module reordering
    ///
    /// This handles additional categories needed when combining statements from multiple modules,
    /// such as built-in type restorations and namespace assignments.
    pub fn analyze_cross_module_statements<I>(
        &self,
        statements_iter: I,
    ) -> CrossModuleStatementCategories
    where
        I: IntoIterator<Item = Stmt>,
    {
        // Materialize once for the two-pass analysis
        let statements: Vec<Stmt> = statements_iter.into_iter().collect();

        // First pass: identify all symbols used as dependencies
        let dependency_symbols =
            crate::visitors::ClassDefDependencyCollector::collect_from_statements(&statements);

        // Second pass: categorize statements using visitor
        let mut visitor = CrossModuleCategorizationVisitor {
            categories: CrossModuleStatementCategories::default(),
            dependency_symbols,
            python_version: self.python_version,
        };

        for stmt in statements {
            visitor.categorize_statement(stmt);
        }

        visitor.categories
    }
}

/// Internal visitor for cross-module categorization
struct CrossModuleCategorizationVisitor {
    categories: CrossModuleStatementCategories,
    dependency_symbols: FxIndexSet<String>,
    python_version: u8,
}

impl CrossModuleCategorizationVisitor {
    fn categorize_statement(&mut self, stmt: Stmt) {
        match stmt {
            Stmt::Import(_) | Stmt::ImportFrom(_) => {
                self.categories.imports.push(stmt);
            }
            Stmt::Assign(ref assign) => {
                // Multi-target assignments are treated as regular assignments
                if assign.targets.len() != 1 {
                    self.categories.regular_assignments.push(stmt);
                    return;
                }

                // Now we can assume a single target for all checks
                // Check if this is an attribute assignment
                if self.is_attribute_assignment(assign) {
                    // Check for namespace built-in assignment (e.g., compat.bytes = bytes)
                    if self.is_namespace_builtin_assignment(assign) {
                        self.categories.namespace_builtin_assignments.push(stmt);
                        return;
                    }

                    // Check for module namespace assignment
                    if self.is_module_namespace_assignment(assign) {
                        self.categories.regular_assignments.push(stmt);
                        return;
                    }

                    // Other attribute assignments come after class definitions
                    self.categories.other_statements.push(stmt);
                    return;
                }

                // Check for built-in type restoration (e.g., bytes = bytes)
                if self.is_builtin_restoration(assign) {
                    self.categories.builtin_restorations.push(stmt);
                    return;
                }

                // Check if this defines a base class symbol
                if self.defines_base_class_for_cross_module(assign) {
                    self.categories.base_class_assignments.push(stmt);
                } else {
                    self.categories.regular_assignments.push(stmt);
                }
            }
            Stmt::ClassDef(_) => {
                self.categories.classes.push(stmt);
            }
            Stmt::FunctionDef(_) => {
                self.categories.functions.push(stmt);
            }
            _ => {
                self.categories.other_statements.push(stmt);
            }
        }
    }

    fn is_attribute_assignment(&self, assign: &ruff_python_ast::StmtAssign) -> bool {
        // Assumes single target (checked in categorize_statement)
        matches!(&assign.targets[0], Expr::Attribute(_))
    }

    fn is_namespace_builtin_assignment(&self, assign: &ruff_python_ast::StmtAssign) -> bool {
        if let (Expr::Attribute(_), Expr::Name(value_name)) =
            (&assign.targets[0], assign.value.as_ref())
        {
            ruff_python_stdlib::builtins::is_python_builtin(
                value_name.id.as_str(),
                self.python_version,
                false,
            )
        } else {
            false
        }
    }

    fn is_module_namespace_assignment(&self, assign: &ruff_python_ast::StmtAssign) -> bool {
        if let Expr::Attribute(attr) = &assign.targets[0] {
            if let Expr::Name(name) = attr.value.as_ref() {
                let parent_name = name.id.as_str();
                let child_name = attr.attr.as_str();

                if let Expr::Name(value_name) = assign.value.as_ref() {
                    value_name.id.as_str() == child_name
                        || value_name.id.as_str() == format!("{parent_name}_{child_name}")
                        || value_name
                            .id
                            .as_str()
                            .starts_with(&format!("{child_name}_"))
                } else {
                    false
                }
            } else {
                false
            }
        } else {
            false
        }
    }

    fn is_builtin_restoration(&self, assign: &ruff_python_ast::StmtAssign) -> bool {
        if let ([Expr::Name(target)], Expr::Name(value)) =
            (assign.targets.as_slice(), assign.value.as_ref())
        {
            target.id == value.id
                && ruff_python_stdlib::builtins::is_python_builtin(
                    target.id.as_str(),
                    self.python_version,
                    false,
                )
        } else {
            false
        }
    }

    fn defines_base_class_for_cross_module(&self, assign: &ruff_python_ast::StmtAssign) -> bool {
        // Assumes single target (checked in categorize_statement)
        if let Expr::Name(target) = &assign.targets[0] {
            if self.dependency_symbols.contains(target.id.as_str()) {
                // Check if the value looks like it could be a class
                is_class_like_expr(assign.value.as_ref())
            } else {
                false
            }
        } else {
            false
        }
    }
}
