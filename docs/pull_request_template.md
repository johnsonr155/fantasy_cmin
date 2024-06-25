# Pull request template

More information on the QA process can be found in the [10DS docs repo](https://github.com/PMO-Data-Science/10ds-core-documentation/blob/main/qa/qa.md)
- Brief description of the changes, including [closing any GitHub issues in this repo that are fixed through this PR](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue): 
- Dashboard is live in: (Dev, Preprod) 
- Anything you are particularly concerned about/needs extra focus in the review: 
- If there is an urgent deadline, please specify it here: 

### PR creator checklist
- [ ] I have provided the information above
- [ ] The code is linted using black
- [ ] I think anyone in the team could pick this code up easily e.g. sensible variable names and comments
- [ ] I have followed [10DS style guidelines](https://github.com/PMO-Data-Science/10ds-core-documentation/blob/main/qa/10ds_style_guidelines.md) to the best of my knowledge
- [ ] I have added the appropriate reviewer onto this PR

### PR reviewer checklist
- [ ] I understand the purpose and customer of this product and what their needs are
- [ ] The code has been checked for readability, reliability and matches the [10DS style guidelines](https://github.com/PMO-Data-Science/10ds-core-documentation/blob/main/qa/pr_guidelines.md)
- [ ] The UI & UX of the dashboard has been checked
- [ ] I have tested for bugs on the dashboard by e.g. playing with different input values
- [ ] Overall, if all the comments I have made on the PR are addressed, I would be happy to see this work on production
