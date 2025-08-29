//! Analyzers for processing collected data from AST visitors
//!
//! This module contains pure analysis logic separated from code generation.
//! Analyzers work with data collected by visitors to derive insights about
//! module dependencies, symbol relationships, and import requirements.

pub mod dependency_analyzer;
pub mod forward_reference_analyzer;
pub mod import_analyzer;
pub mod module_classifier;
pub mod statement_categorizer;
pub mod symbol_analyzer;
pub mod types;

pub use forward_reference_analyzer::ForwardReferenceAnalyzer;
pub use import_analyzer::ImportAnalyzer;
pub use module_classifier::ModuleClassifier;
pub use statement_categorizer::StatementCategorizer;
pub use symbol_analyzer::SymbolAnalyzer;
