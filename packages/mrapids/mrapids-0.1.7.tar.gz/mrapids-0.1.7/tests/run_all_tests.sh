#!/bin/bash

# Master Test Runner - Execute All Test Suites
# Runs all Agent CLI test cases and generates a comprehensive report

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
export CLI_PATH="${CLI_PATH:-$PROJECT_ROOT/target/release/mrapids}"
export TEST_SPEC="${TEST_SPEC:-$PROJECT_ROOT/specs/httpbin.yaml}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Test tracking
TOTAL_SUITES=0
PASSED_SUITES=0
FAILED_SUITES=0
START_TIME=$(date +%s)

# Results file
RESULTS_FILE="$PROJECT_ROOT/test_results_$(date +%Y%m%d_%H%M%S).log"

# Header
echo -e "${CYAN}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║    🤖 Agent CLI - Comprehensive Test Suite 🤖     ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════╝${NC}"
echo ""
echo "Date: $(date)"
echo "CLI Path: $CLI_PATH"
echo "Test Spec: $TEST_SPEC"
echo "Results File: $RESULTS_FILE"
echo ""

# Log function
log() {
    echo "$1" | tee -a "$RESULTS_FILE"
}

# Run test suite
run_suite() {
    local suite_name="$1"
    local script_name="$2"
    local script_path="$SCRIPT_DIR/$script_name"
    
    ((TOTAL_SUITES++))
    
    log ""
    log "$(echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}")"
    log "$(echo -e "${BLUE}Running: $suite_name${NC}")"
    log "$(echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}")"
    
    if [ -f "$script_path" ]; then
        chmod +x "$script_path"
        if $script_path 2>&1 | tee -a "$RESULTS_FILE"; then
            log "$(echo -e "${GREEN}✅ $suite_name: PASSED${NC}")"
            ((PASSED_SUITES++))
        else
            log "$(echo -e "${RED}❌ $suite_name: FAILED${NC}")"
            ((FAILED_SUITES++))
        fi
    else
        log "$(echo -e "${RED}❌ $suite_name: SCRIPT NOT FOUND${NC}")"
        ((FAILED_SUITES++))
    fi
}

# Build project first
log "$(echo -e "${BLUE}🔨 Building Agent CLI...${NC}")"
if cd "$PROJECT_ROOT" && cargo build --release 2>&1 | tee -a "$RESULTS_FILE" | grep -q "Finished"; then
    log "$(echo -e "${GREEN}✅ Build successful${NC}")"
else
    log "$(echo -e "${RED}❌ Build failed${NC}")"
    exit 1
fi

# Make test directories
mkdir -p "$SCRIPT_DIR"

# Create test scripts if they don't exist
if [ ! -f "$SCRIPT_DIR/test_core_cli.sh" ]; then
    log "$(echo -e "${YELLOW}Creating test scripts...${NC}")"
    # Scripts would have been created by previous commands
fi

# Run all test suites
run_suite "Core CLI Tests" "test_core_cli.sh"
run_suite "Validation Tests" "test_validation.sh"
run_suite "Generation Tests" "test_generation.sh"
run_suite "Collections Tests" "test_collections.sh"

# Calculate duration
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

# Generate summary report
log ""
log "$(echo -e "${CYAN}╔═══════════════════════════════════════════════════╗${NC}")"
log "$(echo -e "${CYAN}║              📊 TEST SUMMARY REPORT               ║${NC}")"
log "$(echo -e "${CYAN}╚═══════════════════════════════════════════════════╝${NC}")"
log ""
log "Total Test Suites: $TOTAL_SUITES"
log "$(echo -e "${GREEN}Passed Suites: $PASSED_SUITES${NC}")"
log "$(echo -e "${RED}Failed Suites: $FAILED_SUITES${NC}")"
log ""
log "Test Duration: ${MINUTES}m ${SECONDS}s"
log "Completion Time: $(date)"
log ""

# Calculate pass rate
if [ $TOTAL_SUITES -gt 0 ]; then
    PASS_RATE=$((PASSED_SUITES * 100 / TOTAL_SUITES))
    log "Pass Rate: ${PASS_RATE}%"
    
    if [ $PASS_RATE -eq 100 ]; then
        log ""
        log "$(echo -e "${GREEN}🎉 ALL TESTS PASSED! 🎉${NC}")"
        log "$(echo -e "${GREEN}Agent CLI is production ready!${NC}")"
        EXIT_CODE=0
    elif [ $PASS_RATE -ge 80 ]; then
        log ""
        log "$(echo -e "${YELLOW}⚠️  MOSTLY PASSED (${PASS_RATE}%)${NC}")"
        log "$(echo -e "${YELLOW}Some issues need attention${NC}")"
        EXIT_CODE=1
    else
        log ""
        log "$(echo -e "${RED}❌ TESTS FAILED (${PASS_RATE}% pass rate)${NC}")"
        log "$(echo -e "${RED}Major issues detected${NC}")"
        EXIT_CODE=2
    fi
else
    log "$(echo -e "${RED}❌ No tests were run${NC}")"
    EXIT_CODE=3
fi

log ""
log "Full results saved to: $RESULTS_FILE"
log ""

# Generate HTML report (optional)
if command -v pandoc &> /dev/null; then
    HTML_FILE="${RESULTS_FILE%.log}.html"
    echo "<html><head><title>Agent CLI Test Results</title></head><body><pre>" > "$HTML_FILE"
    cat "$RESULTS_FILE" >> "$HTML_FILE"
    echo "</pre></body></html>" >> "$HTML_FILE"
    log "HTML report generated: $HTML_FILE"
fi

exit $EXIT_CODE