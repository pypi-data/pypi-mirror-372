// Test cleanup utilities
use crate::utils::security::validate_delete_path;
use anyhow::Result;
use std::fs;
use std::path::Path;

/// Clean up test-generated directories and files
pub fn cleanup_test_artifacts(base_path: &Path, preserve_specs: bool) -> Result<()> {
    // Validate the base path before any cleanup
    validate_delete_path(base_path)?;

    // Patterns for test-generated directories
    let test_patterns = ["test-", "tmp-", "temp-", ".test-", "test_output"];

    // Patterns for generated files/dirs to clean
    let generated_patterns = ["generated-", "output-", "build-test-"];

    // Clean directories matching test patterns
    if base_path.exists() && base_path.is_dir() {
        for entry in fs::read_dir(base_path)? {
            let entry = entry?;
            let path = entry.path();
            let file_name = entry.file_name();
            let name = file_name.to_string_lossy();

            // Check if this is a test directory
            let is_test_dir = test_patterns
                .iter()
                .any(|pattern| name.starts_with(pattern));
            let is_generated = generated_patterns
                .iter()
                .any(|pattern| name.starts_with(pattern));

            if is_test_dir || is_generated {
                if path.is_dir() {
                    // Skip if it contains important specs and preserve_specs is true
                    if preserve_specs && contains_spec_files(&path) {
                        println!("  ⚠️  Preserving {} (contains spec files)", name);
                        continue;
                    }

                    // Extra validation before deletion
                    validate_delete_path(&path)?;
                    println!("  🗑️  Removing test directory: {}", name);
                    fs::remove_dir_all(&path)?;
                } else if path.is_file() {
                    // Clean test files
                    if is_test_file(&name) {
                        // Validate file deletion
                        validate_delete_path(&path)?;
                        println!("  🗑️  Removing test file: {}", name);
                        fs::remove_file(&path)?;
                    }
                }
            }
        }
    }

    Ok(())
}

/// Check if a directory contains spec files
fn contains_spec_files(dir: &Path) -> bool {
    if let Ok(entries) = fs::read_dir(dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_file() {
                if let Some(ext) = path.extension() {
                    if ext == "yaml" || ext == "json" || ext == "yml" {
                        if let Some(name) = path.file_name() {
                            let name_str = name.to_string_lossy();
                            if name_str.contains("spec")
                                || name_str.contains("api")
                                || name_str.contains("swagger")
                                || name_str.contains("openapi")
                            {
                                return true;
                            }
                        }
                    }
                }
            } else if path.is_dir() && path.file_name().map_or(false, |n| n == "specs") {
                return true;
            }
        }
    }
    false
}

/// Check if a file is a test file
fn is_test_file(name: &str) -> bool {
    name.ends_with("-test.sh")
        || name.ends_with(".test.js")
        || name.ends_with(".test.ts")
        || name.starts_with("test-") && name.ends_with(".json")
        || name.starts_with("test-") && name.ends_with(".mk")
        || name == "test.mk"
}

/// Clean up after analyze command
pub fn cleanup_analyze_artifacts(output_dir: &Path, keep_latest: bool) -> Result<()> {
    // Validate the output directory
    validate_delete_path(output_dir)?;

    if !keep_latest {
        // Clean old backup directories
        let backup_patterns = [".backup", ".old", ".prev"];

        if output_dir.exists() {
            for entry in fs::read_dir(output_dir)? {
                let entry = entry?;
                let path = entry.path();
                let name = entry.file_name().to_string_lossy().to_string();

                if backup_patterns.iter().any(|p| name.contains(p)) {
                    if path.is_dir() {
                        println!("  🗑️  Removing backup: {}", name);
                        fs::remove_dir_all(&path)?;
                    }
                }
            }
        }
    }

    Ok(())
}

/// Clean up empty directories
pub fn cleanup_empty_dirs(base_path: &Path) -> Result<()> {
    if base_path.is_dir() {
        let mut is_empty = true;

        for entry in fs::read_dir(base_path)? {
            let entry = entry?;
            let path = entry.path();

            if path.is_dir() {
                // Recursively clean subdirectories
                cleanup_empty_dirs(&path)?;

                // Check if directory is now empty
                if fs::read_dir(&path)?.next().is_none() {
                    println!("  🗑️  Removing empty directory: {}", path.display());
                    fs::remove_dir(&path)?;
                } else {
                    is_empty = false;
                }
            } else {
                is_empty = false;
            }
        }

        // Don't remove the base path itself
        let _ = is_empty;
    }

    Ok(())
}
