# CLI Refactoring Migration Plan

## Phase 1: Minimal Breaking Changes (Recommended First Step)

### 1. Add Command Aliases
Keep existing commands but add new names as aliases:
- `explore` → also accept `search`
- `init-config` → also accept `config`
- `setup-tests` → also accept `tests init`

### 2. Add Global Flags
Add global flags to existing structure without breaking current usage:
- Add `--spec`, `--env`, `--profile` as global options
- Add `--output`, `--quiet`, `--verbose` globally
- Keep existing command-specific flags for backward compatibility

### 3. Add Exit Codes
Update main.rs to return proper exit codes without changing command structure

### 4. Consolidate Similar Commands
- Merge `flatten` into `resolve` with `--bundle` flag
- Move `analyze` functionality to `gen snippets`
- Move `sdk` to `gen sdk`

## Phase 2: Full Migration (Breaking Changes)

### Prerequisites
1. Update all documentation
2. Create migration guide for users
3. Add deprecation warnings in Phase 1

### Implementation Steps

#### Step 1: Update CLI Structure
```rust
// Replace Commands enum with new structure
pub enum Commands {
    // Projects
    Init(InitCommand),
    Config(ConfigCommand),    // renamed from InitConfig
    Cleanup(CleanupCommand),
    
    // Specs
    Validate(ValidateCommand),
    Resolve(ResolveCommand),  // merged with Flatten
    Diff(DiffCommand),
    
    // Discoverability
    List(ListCommand),
    Show(ShowCommand),
    Search(SearchCommand),    // renamed from Explore
    
    // Execution
    Run(RunCommand),
    Test(TestCommand),
    Tests(TestsCommand),      // new subcommand structure
    
    // Generation
    Gen(GenCommand),          // new subcommand structure
    
    // Auth
    Auth(AuthCommand),
    
    // Help
    Help(HelpCommand),
}
```

#### Step 2: Update Command Handlers
1. Update core module functions to accept global options
2. Modify each handler to use new parameter structure
3. Add output formatting based on global --output flag

#### Step 3: Testing Strategy
1. Create parallel test suite for new commands
2. Ensure backward compatibility tests pass
3. Add integration tests for global flags
4. Test all exit codes

## Incremental Approach Benefits

1. **No Immediate Breaking Changes**: Users can continue using existing commands
2. **Gradual Migration**: Users can adopt new commands at their pace
3. **Testing Safety**: Can test new structure alongside old
4. **Rollback Capability**: Easy to revert if issues found

## Implementation Order

### Week 1: Non-Breaking Additions
- [ ] Add exit codes to main.rs
- [ ] Add global flags support (backward compatible)
- [ ] Add command aliases

### Week 2: Command Consolidation
- [ ] Implement `gen` subcommands (keep old commands)
- [ ] Implement `tests init` (keep `setup-tests`)
- [ ] Add `--bundle` to resolve command

### Week 3: Testing & Documentation
- [ ] Update all tests
- [ ] Update documentation
- [ ] Create migration guide

### Week 4: Deprecation & Release
- [ ] Add deprecation warnings
- [ ] Release with both old and new commands
- [ ] Monitor user feedback

### Month 2: Full Migration
- [ ] Remove deprecated commands
- [ ] Final cleanup
- [ ] Major version release

## Risk Mitigation

1. **Feature Flags**: Use compile-time flags to enable/disable new CLI
2. **A/B Testing**: Some users on new CLI, some on old
3. **Metrics**: Track which commands are used most
4. **Feedback Loop**: Quick iteration based on user feedback

## Decision Point

**Recommendation**: Start with Phase 1 (incremental approach) to minimize risk and user disruption. This allows:
- Immediate benefits (exit codes, global flags)
- No breaking changes
- Time to gather user feedback
- Smooth transition path