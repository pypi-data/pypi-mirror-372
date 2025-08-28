# GitLab Gemini Reviewer

An automated code review assistant powered by Google's Gemini AI. This tool analyzes GitLab Merge Requests, provides feedback as comments, creates Jira tickets, and generates QA test plans, streamlining your development workflow.

## ✨ Features

- **Automated Code Analysis**: Leverages the Gemini API to perform detailed code reviews.
- **Smart MR Discussions**: 
  - Tracks existing discussions to avoid duplicates
  - Automatically resolves discussions when issues are fixed
  - Filters discussions by severity before creating new ones
- **Inline MR Commenting**: Posts suggestions and issues as discussions directly on the relevant code lines in the merge request.
- **Overall Summary**: Adds a general summary comment to the MR with a quality score.
- **Automatic Approval & Merge**: Can automatically approve and optionally merge requests that meet a configurable quality threshold.
  - Control merging behavior with the `--auto-merge` flag or `AUTO_MERGE` environment variable
- **Seamless Jira Integration**:
  - Creates a specific sub-task for the code review under the main story.
  - Generates and posts a detailed QA test plan as a comment on the parent ticket.
- **Multi-language Support**: Can provide feedback in English or Brazilian Portuguese.
- **Simulation Mode**: Preview and analyze local uncommitted changes without making real modifications.
- **Highly Configurable**: All parameters are controlled via environment variables, making it perfect for CI/CD environments.

## 🚀 How It Works

1.  **Trigger**: The tool is designed to be run in a CI/CD pipeline when a merge request is created or updated.
2.  **Fetch Diffs**: It fetches the code changes (diffs) from the specified GitLab merge request.
3.  **Check Existing Discussions**: 
    - Fetches all existing discussions to avoid duplicates
    - Resolves discussions for issues that have been fixed
4.  **Analyze**: It sends the code, along with contextual information from the MR title and description, to the Gemini API for analysis.
5.  **Post Feedback**: It parses the AI's response and posts feedback to GitLab:
    - A general summary note.
    - Discussions attached to specific lines of code for each new issue found.
6.  **Integrate with Jira**:
    - Extracts the Jira ticket key from the MR title (e.g., `PROJ-123`).
    - Creates a "Code Review" sub-task.
    - Generates a complete QA test plan and posts it as a comment on the main Jira ticket.

## 📦 Installation

You can install the package directly from the source code.

```bash
# Clone the repository first
git clone https://github.com/alairjt/gitlab-gemini-reviewer.git
cd gitlab-gemini-reviewer

# Install using pip
pip install .
```

## ⚙️ Configuration

The tool is configured entirely through environment variables.

| Variable                 | Description                                                              | Default                  | Required |
| ------------------------ | ------------------------------------------------------------------------ | ------------------------ | :------: |
| `GITLAB_TOKEN`           | Your GitLab personal access token with `api` scope.                      | -                        |   Yes    |
| `GEMINI_API_KEY`         | Your Google AI Studio API key for Gemini.                                | -                        |   Yes    |
| `CI_PROJECT_ID`          | The ID of your GitLab project. Provided by GitLab CI.                    | -                        |   Yes    |
| `CI_MERGE_REQUEST_IID`   | The IID (internal ID) of the merge request. Provided by GitLab CI.       | -                        |   Yes    |
| `CI_SERVER_URL`          | The base URL of your GitLab instance (e.g., `https://gitlab.com`).        | -                        |   Yes    |
| `JIRA_URL`               | The base URL of your Jira instance.                                      | -                        |    No    |
| `JIRA_USER`              | The email or username for the Jira service account.                      | -                        |    No    |
| `JIRA_TOKEN`             | The API token for the Jira service account.                              | -                        |    No    |
| `REVIEW_LANGUAGE`        | The language for the AI's response (`en` or `pt-BR`).                    | `pt-BR`                  |    No    |
| `GEMINI_MODEL`           | The Gemini model to use for the review.                                  | `gemini-2.5-flash`       |    No    |
| `DEBUG`                  | Set to `1` or `true` for verbose error logging.                          | -                        |    No    |

**Note**: The Jira variables are only required if you want to enable Jira integration.

## ▶️ Usage

After installation, the tool can be run from the command line.

```bash
gemini-reviewer
```

If you encounter a `command not found` error, it means the installation directory is not in your shell's `PATH`. You can either add it or run the tool as a module:

```bash
python -m gitlab_gemini_reviewer.gemini_mr_review
```

### GitLab CI/CD Example

It's intended to be used as a step in your CI/CD pipeline.

```yaml
# .gitlab-ci.yml

gitlab_gemini_reviewer:
  stage: review
  image: python:3.11-slim
  before_script:
    - pip install --upgrade pip
    - pip install gitlab-gemini-reviewer>=0.3.0
  script:
    - gemini-reviewer
  needs: ['unit test'] # ✅ Ensures that the 'unit test' stage runs before.
  rules:
    # Main rule:
    # 1. Run only on Merge Request events.
    # 2. Do NOT run if the target branch is 'production' or 'pre-production'.
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event" && $CI_MERGE_REQUEST_TARGET_BRANCH_NAME != "production" && $CI_MERGE_REQUEST_TARGET_BRANCH_NAME != "pre-production"'
      when: on_success # Runs if the job in 'needs' succeeds (default).
  interruptible: true # ✅ Cancels the old job if a new commit is pushed to the MR, saving resources.


```

## 🔄 Discussion Management

The tool now includes intelligent discussion management features:

### Avoiding Duplicate Discussions
- Automatically checks for existing discussions on the same lines of code
- Prevents creating duplicate discussions for the same issue
- Uses file path and line number to identify duplicate issues

### Automatic Resolution
- Tracks when issues are fixed in subsequent commits
- Automatically resolves discussions when the corresponding issues are no longer present
- Only creates new discussions for issues that don't already have open discussions

### Severity Filtering
- Filters issues by severity before creating discussions
- Helps focus on the most important feedback first
- Configurable through the API response

## ⚙️ Auto-Merge Configuration

You can enable automatic merging of approved MRs using either the command line flag or environment variable:

```bash
# Using command line flag
gemini-reviewer --auto-merge

# Using environment variable
export AUTO_MERGE=true
gemini-reviewer
```

## 🎭 Simulation Mode

You can use the simulation mode to preview and analyze your local uncommitted changes without making any real modifications to GitLab or Jira. This is perfect for testing and reviewing your code before committing.

### Usage

```bash
# Run simulation mode
python -m gitlab_gemini_reviewer.gemini_mr_review --simulate

# Or if installed as package
gemini-reviewer --simulate
```

### What it does:

1. **Detects Local Changes**: Automatically finds all uncommitted changes in your git repository
2. **Analyzes Code**: Sends your changes to Gemini AI for review
3. **Shows Preview**: Displays what would happen if run in normal mode:
   - Code review results and scores
   - Issues that would be created
   - Actions that would be taken (comments, approvals, etc.)
4. **Safe Testing**: No real changes are made to GitLab or Jira

### Requirements for Simulation Mode:

Only `GEMINI_API_KEY` is required in simulation mode. GitLab and Jira credentials are not needed.

```bash
# Set only the Gemini API key
export GEMINI_API_KEY="your_gemini_api_key_here"

# Run simulation
python -m gitlab_gemini_reviewer.gemini_mr_review --simulate
```

### Example Output:

```
🎭 Running in SIMULATION MODE
This will analyze your local uncommitted changes without making any real changes.

🔍 Simulating review for 3 local changes...
🤖 Analyzing src/main.py...
🤖 Analyzing tests/test_main.py...
🤖 Analyzing README.md...

============================================================
🎭 SIMULATION RESULTS
============================================================
## ✅ Review Summary
**Score**: 🟢 85/100
**Status**: APPROVED
**Files Analyzed**: 3

### Changes Detected:
- `src/main.py` (modified)
- `tests/test_main.py` (added)
- `README.md` (modified)

### AI Analysis Summary
[AI analysis would appear here...]

### Issues Found (2)
1. 🔴 **Issue Title**
   - File: `src/main.py`
   - Line: 42
   - Severity: medium
   - Description: [issue description]
   - Suggestion: [suggested fix]

============================================================
📝 WHAT WOULD HAPPEN IN REAL MODE:
- A comment would be posted on the GitLab MR
- 2 discussion threads would be created
============================================================
```

## 📋 Development Plan Generation

You can generate a comprehensive development plan in Markdown format that can be used by LLMs and shared with your team. This feature works only in simulation mode and creates a detailed analysis document.

### Usage

```bash
# Generate development plan
python -m gitlab_gemini_reviewer.gemini_mr_review --simulate --generate-plan development-plan.md

# Or with a custom filename
python -m gitlab_gemini_reviewer.gemini_mr_review --simulate --generate-plan my-plan.md
```

### What the plan includes:

1. **Executive Summary**
   - Code review results and scores
   - Risk assessment and recommendations
   - Key metrics and status

2. **Files Modified**
   - Detailed list of all changed files
   - Change types (modified, added, deleted)
   - Code diffs for modified files

3. **Code Review Analysis**
   - AI analysis summary
   - Detailed issues with severity levels
   - Suggested fixes and improvements

4. **Development Recommendations**
   - Immediate actions checklist
   - Best practices checklist
   - Next steps for development

5. **Technical Context**
   - Development environment details
   - Code quality metrics
   - AI analysis methodology

### Example Generated Plan

The generated plan will look like this:

```markdown
# 📋 Development Plan - Code Review Analysis

**Generated on:** 2025-08-27 16:35:42
**Analysis Language:** pt-BR
**Files Analyzed:** 3

---

## 🎯 Executive Summary

### Code Review Results
- **Overall Score:** 85/100
- **Status:** ✅ APPROVED
- **Issues Found:** 2
- **Recommendation:** Ready for merge

### Key Metrics
- **Files Changed:** 3
- **Risk Level:** 🟢 Low

---

## 📁 Files Modified

### 1. `src/main.py`
- **Change Type:** Modified
- **Status:** 📝 Modified

**Code Changes:**
```diff
- old code
+ new code
```

### 2. `tests/test_main.py`
- **Change Type:** Added
- **Status:** ➕ Added

---

## 🔍 Code Review Analysis

### AI Analysis Summary
[AI analysis would appear here...]

### Issues Identified (2)

#### 1. 🔴 High Severity Issue
**Details:**
- **File:** `src/main.py`
- **Line:** 42
- **Severity:** High
- **Category:** Security

**Description:**
Issue description here...

**Suggested Fix:**
Suggested solution here...

---

## 🚀 Development Recommendations

### Immediate Actions Required
- [ ] Address Critical Issues
- [ ] Code Review
- [ ] Testing
- [ ] Documentation

### Best Practices Checklist
- [ ] Code Style
- [ ] Documentation
- [ ] Testing
- [ ] Performance
- [ ] Security
- [ ] Error Handling

### Next Steps
1. Code Review
2. Implementation
3. Testing
4. Deployment
5. Monitoring

---

**Generated by:** GitLab Gemini Reviewer (Simulation Mode)
```

### Use Cases

- **Team Collaboration:** Share the plan with team members for feedback
- **Documentation:** Keep track of code review decisions
- **LLM Context:** Provide comprehensive context to AI assistants
- **Audit Trail:** Maintain records of code review analyses
- **Planning:** Guide development priorities and next steps

### Integration Tips

- **Version Control:** Commit the generated plans alongside code changes
- **CI/CD:** Generate plans automatically in CI pipelines
- **Documentation Sites:** Use the plans in wiki pages or documentation
- **Team Workflows:** Integrate into code review and planning processes

## 🐛 Debugging and Development

### VS Code Launch Configurations

The project includes pre-configured launch configurations for easy debugging and testing of simulation features:

#### Available Launch Configurations:

1. **🎭 Simulação Simples**
   - Runs simulation mode to analyze local uncommitted changes
   - Shows preview of what would happen in real mode
   - Perfect for testing code changes before committing

2. **📋 Simulação com Plano de Desenvolvimento**
   - Runs simulation and generates a comprehensive development plan
   - Saves plan as `development-plan.md` in project root
   - Ideal for documentation and team collaboration

3. **📝 Simulação com Plano Personalizado**
   - Prompts for custom filename for the development plan
   - Allows flexible naming conventions for different scenarios
   - Great for organizing multiple development plans

#### How to Use Launch Configurations:

1. **Open VS Code** in the project directory
2. **Go to Run and Debug** (Ctrl+Shift+D or Cmd+Shift+D)
3. **Select a launch configuration** from the dropdown:
   - `🎭 Simulação Simples`
   - `📋 Simulação com Plano de Desenvolvimento`
   - `📝 Simulação com Plano Personalizado`
4. **Click the green play button** or press F5 to start debugging

#### Prerequisites for Launch Configurations:

- **Environment Variables**: Ensure `.env.local` exists with `GEMINI_API_KEY`
- **Python Interpreter**: VS Code should detect the correct Python interpreter
- **Git Repository**: Must be in a git repository with changes to analyze

#### Example Workflow:

```bash
# 1. Make some code changes
echo "# New feature" >> src/main.py

# 2. Use VS Code launch configuration
# Select "🎭 Simulação Simples" and press F5

# 3. Review the analysis output in terminal

# 4. If satisfied, generate development plan
# Select "📋 Simulação com Plano de Desenvolvimento" and press F5

# 5. Check the generated development-plan.md file
```

### Custom Launch Configuration

You can also create custom launch configurations by modifying `.vscode/launch.json`:

```json
{
    "name": "My Custom Simulation",
    "type": "debugpy",
    "request": "launch",
    "module": "gitlab_gemini_reviewer.gemini_mr_review",
    "args": [
        "--simulate",
        "--generate-plan",
        "my-custom-plan.md",
        "--ignore-severity",
        "low,medium"
    ],
    "console": "integratedTerminal",
    "envFile": "${workspaceFolder}/.env.local"
}
```

## 📄 License